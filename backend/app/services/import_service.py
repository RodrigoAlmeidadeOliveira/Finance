"""
Serviço responsável por orquestrar importação OFX e classificação ML.
"""
from __future__ import annotations

import json
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from ..importers import OFXImporter
from ..ml import TransactionPredictor
from ..models import ImportBatch, ImportStatus, PendingTransaction, ReviewStatus


class ImportService:
    """
    Realiza a importação de arquivos OFX, classificando transações e
    persistindo em import_batches e pending_transactions.
    """

    def __init__(
        self,
        session_factory: Callable[[], Session],
        predictor: TransactionPredictor,
        upload_folder: str,
    ):
        self.session_factory = session_factory
        self.predictor = predictor
        self.upload_folder = Path(upload_folder)
        self.upload_folder.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _session_scope(self):
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def import_ofx_file(self, file_path: str, filename: str, user_id: int) -> Dict:
        """
        Processa um arquivo OFX já salvo em disco.

        Args:
            file_path: Caminho do arquivo OFX salvo
            filename: Nome original do arquivo
            user_id: Usuário responsável pelo upload

        Returns:
            Dicionário contendo dados do lote e transações pendentes
        """
        parsed_data = OFXImporter.parse_ofx_file(file_path)
        summary = OFXImporter.get_import_summary(parsed_data)
        transactions = parsed_data["transactions"]

        predictions = self._predict_transactions(transactions)

        with self._session_scope() as session:
            batch = self._create_batch(session, parsed_data, summary, filename, file_path, user_id)
            pending, duplicates = self._create_pending_transactions(
                session, batch, transactions, predictions
            )

            batch.processed_transactions = len(pending)
            batch.total_transactions = summary["transactions"]["total"]
            batch.status = ImportStatus.REVIEW

            session.flush()

            return {
                "batch": batch.to_dict(),
                "summary": summary,
                "pending_transactions": [p.to_dict() for p in pending],
                "duplicates_skipped": duplicates,
            }

    def list_batches(self) -> List[Dict]:
        """
        Retorna lista simplificada de batches.
        """
        session = self.session_factory()
        try:
            batches = session.query(ImportBatch).order_by(ImportBatch.created_at.desc()).all()
            return [b.to_dict() for b in batches]
        finally:
            session.close()

    def get_batch(self, batch_id: int) -> Optional[Dict]:
        """
        Busca um lote específico.
        """
        session = self.session_factory()
        try:
            batch = session.get(ImportBatch, batch_id)
            return batch.to_dict() if batch else None
        finally:
            session.close()

    def list_pending_transactions(self, batch_id: int) -> List[Dict]:
        """
        Lista transações pendentes de um lote.
        """
        session = self.session_factory()
        try:
            transactions = (
                session.query(PendingTransaction)
                .filter(PendingTransaction.import_batch_id == batch_id)
                .order_by(PendingTransaction.date.asc())
                .all()
            )
            return [t.to_dict() for t in transactions]
        finally:
            session.close()

    def review_transaction(
        self,
        batch_id: int,
        transaction_id: int,
        final_category: str,
        status: ReviewStatus = ReviewStatus.APPROVED,
        notes: Optional[str] = None,
    ) -> Optional[Dict]:
        """
        Atualiza a revisão de uma transação pendente.
        """
        with self._session_scope() as session:
            transaction = (
                session.query(PendingTransaction)
                .filter(
                    PendingTransaction.id == transaction_id,
                    PendingTransaction.import_batch_id == batch_id,
                )
                .first()
            )
            if not transaction:
                return None

            transaction.user_category = final_category
            transaction.review_status = status
            transaction.reviewed_at = datetime.utcnow()
            transaction.notes = notes
            self._update_batch_status(session, batch_id)
            session.flush()
            return transaction.to_dict()

    def _update_batch_status(self, session: Session, batch_id: int) -> None:
        """
        Define status do lote como COMPLETED quando todas transações foram revistas.
        """
        pending_count = (
            session.query(PendingTransaction)
            .filter(
                PendingTransaction.import_batch_id == batch_id,
                PendingTransaction.review_status == ReviewStatus.PENDING,
            )
            .count()
        )
        if pending_count == 0:
            batch = session.get(ImportBatch, batch_id)
            if batch:
                batch.status = ImportStatus.COMPLETED

    def _predict_transactions(self, transactions: List[Dict]) -> List[Dict]:
        """
        Executa predição de categorias para lista de transações OFX.
        """
        descriptions = [t["description"] for t in transactions]
        values = [t["amount"] for t in transactions]
        types = [t["type"] for t in transactions]
        dates = [t["date"] for t in transactions]

        return self.predictor.predict_batch(
            descriptions=descriptions,
            values=values,
            transaction_types=types,
            dates=dates,
        )

    def _create_batch(
        self,
        session: Session,
        parsed_data: Dict,
        summary: Dict,
        filename: str,
        file_path: str,
        user_id: int,
    ) -> ImportBatch:
        """
        Cria registro ImportBatch com metadados do arquivo.
        """
        batch = ImportBatch(
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            status=ImportStatus.PROCESSING,
            institution_name=parsed_data["institution"]["name"],
            account_id=parsed_data["account"]["account_id"],
            period_start=parsed_data["period"]["start_date"],
            period_end=parsed_data["period"]["end_date"],
            balance=summary["balance"]["current"],
            total_transactions=summary["transactions"]["total"],
        )
        session.add(batch)
        session.flush()
        return batch

    def _create_pending_transactions(
        self,
        session: Session,
        batch: ImportBatch,
        transactions: List[Dict],
        predictions: List[Dict],
    ) -> Tuple[List[PendingTransaction], List[str]]:
        """
        Persiste PendingTransaction para cada item, ignorando duplicatas por FITID.
        """
        fitids = [t["fitid"] for t in transactions if t.get("fitid")]
        existing_fitids = set()
        pending: List[PendingTransaction] = []

        if fitids:
            existing_fitids = {
                row[0]
                for row in session.query(PendingTransaction.fitid)
                .filter(PendingTransaction.fitid.in_(fitids))
                .all()
            }

        for tx, pred in zip(transactions, predictions):
            if tx["fitid"] in existing_fitids:
                continue

            suggested = json.dumps(pred.get("suggestions", []))

            pending_tx = PendingTransaction(
                import_batch_id=batch.id,
                fitid=tx["fitid"],
                date=tx["date"],
                description=tx["description"],
                amount=tx["amount"],
                transaction_type=tx["type"],
                payee=tx.get("payee"),
                memo=tx.get("memo"),
                check_number=tx.get("check_number"),
                ofx_type=tx.get("ofx_type"),
                predicted_category=pred.get("category"),
                confidence_score=pred.get("confidence"),
                confidence_level=pred.get("confidence_level"),
                suggested_categories=suggested,
            )
            session.add(pending_tx)
            pending.append(pending_tx)

        return pending, list(existing_fitids)

    def delete_batch(self, batch_id: int, user_id: int) -> bool:
        """
        Remove um lote de importação e todas as suas transações.

        Args:
            batch_id: ID do lote a ser removido
            user_id: ID do usuário (para validação de permissão)

        Returns:
            True se removido com sucesso, False se não encontrado
        """
        with self._session_scope() as session:
            batch = session.get(ImportBatch, batch_id)
            if not batch or batch.user_id != user_id:
                return False

            # Remove transações pendentes associadas
            session.query(PendingTransaction).filter(
                PendingTransaction.import_batch_id == batch_id
            ).delete()

            # Remove o lote
            session.delete(batch)
            session.flush()
            return True

    def update_batch(self, batch_id: int, user_id: int, **kwargs) -> Optional[Dict]:
        """
        Atualiza metadados de um lote de importação.

        Args:
            batch_id: ID do lote
            user_id: ID do usuário (para validação de permissão)
            **kwargs: Campos a serem atualizados (status, notes, etc.)

        Returns:
            Dicionário com dados atualizados ou None se não encontrado
        """
        with self._session_scope() as session:
            batch = session.get(ImportBatch, batch_id)
            if not batch or batch.user_id != user_id:
                return None

            # Atualiza apenas campos permitidos
            allowed_fields = ['status', 'institution_name']
            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    setattr(batch, field, value)

            session.flush()
            return batch.to_dict()

    def delete_transaction(self, batch_id: int, transaction_id: int) -> bool:
        """
        Remove uma transação pendente específica.

        Args:
            batch_id: ID do lote
            transaction_id: ID da transação

        Returns:
            True se removido com sucesso, False se não encontrado
        """
        with self._session_scope() as session:
            transaction = (
                session.query(PendingTransaction)
                .filter(
                    PendingTransaction.id == transaction_id,
                    PendingTransaction.import_batch_id == batch_id,
                )
                .first()
            )
            if not transaction:
                return False

            session.delete(transaction)
            session.flush()
            return True

    def find_duplicates(self, threshold_days: int = 3) -> List[Dict]:
        """
        Identifica transações potencialmente duplicadas baseado em:
        - Mesmo valor (amount)
        - Mesma descrição (ou similar)
        - Datas próximas (dentro do threshold)

        Args:
            threshold_days: Número de dias para considerar datas como próximas

        Returns:
            Lista de grupos de duplicatas encontradas
        """
        session = self.session_factory()
        try:
            from sqlalchemy import func, or_
            from datetime import timedelta

            # Busca todas transações pendentes ordenadas por data e valor
            transactions = (
                session.query(PendingTransaction)
                .filter(PendingTransaction.review_status == ReviewStatus.PENDING)
                .order_by(PendingTransaction.date, PendingTransaction.amount)
                .all()
            )

            duplicates = []
            seen_ids = set()

            for i, tx1 in enumerate(transactions):
                if tx1.id in seen_ids:
                    continue

                group = [tx1.to_dict()]
                seen_ids.add(tx1.id)

                # Compara com transações subsequentes
                for tx2 in transactions[i+1:]:
                    if tx2.id in seen_ids:
                        continue

                    # Critérios de duplicata
                    same_amount = abs(tx1.amount - tx2.amount) < 0.01
                    date_diff = abs((tx1.date - tx2.date).days)
                    within_threshold = date_diff <= threshold_days
                    similar_description = self._similar_strings(
                        tx1.description, tx2.description
                    )

                    if same_amount and within_threshold and similar_description:
                        group.append(tx2.to_dict())
                        seen_ids.add(tx2.id)

                # Adiciona grupo apenas se tiver duplicatas
                if len(group) > 1:
                    duplicates.append({
                        'count': len(group),
                        'amount': group[0]['amount'],
                        'description': group[0]['description'],
                        'transactions': group
                    })

            return duplicates
        finally:
            session.close()

    def merge_duplicates(
        self,
        keep_transaction_id: int,
        remove_transaction_ids: List[int]
    ) -> Optional[Dict]:
        """
        Mantém uma transação e remove as duplicatas.

        Args:
            keep_transaction_id: ID da transação a manter
            remove_transaction_ids: Lista de IDs a remover

        Returns:
            Dicionário com a transação mantida ou None se erro
        """
        with self._session_scope() as session:
            keep_tx = session.get(PendingTransaction, keep_transaction_id)
            if not keep_tx:
                return None

            # Remove as duplicatas
            session.query(PendingTransaction).filter(
                PendingTransaction.id.in_(remove_transaction_ids)
            ).delete(synchronize_session=False)

            session.flush()
            return keep_tx.to_dict()

    @staticmethod
    def _similar_strings(str1: str, str2: str, threshold: float = 0.8) -> bool:
        """
        Verifica se duas strings são similares usando Levenshtein distance.

        Args:
            str1: Primeira string
            str2: Segunda string
            threshold: Limiar de similaridade (0.0 a 1.0)

        Returns:
            True se strings são similares
        """
        if not str1 or not str2:
            return False

        # Normaliza strings
        s1 = str1.lower().strip()
        s2 = str2.lower().strip()

        # Se são idênticas
        if s1 == s2:
            return True

        # Calcula distância de Levenshtein simplificada
        if len(s1) < len(s2):
            s1, s2 = s2, s1

        if len(s2) == 0:
            return False

        # Implementação simples de Levenshtein
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        distance = previous_row[-1]
        max_len = max(len(s1), len(s2))
        similarity = 1 - (distance / max_len)

        return similarity >= threshold
