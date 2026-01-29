"""
Serviço para gerenciar treinamento de modelos ML.
"""
from __future__ import annotations

import os
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from ..ml import TransactionClassifierTrainer
from ..models import (
    TrainingJob,
    TrainingJobStatus,
    TrainingJobSource,
    PendingTransaction,
    ReviewStatus,
)


class TrainingService:
    """
    Gerencia treinamento de modelos ML de categorização.
    """

    def __init__(
        self,
        session_factory: Callable[[], Session],
        models_folder: str,
        upload_folder: str,
    ):
        """
        Inicializa o serviço de treinamento.

        Args:
            session_factory: Factory para criar sessões do banco
            models_folder: Pasta onde modelos treinados são salvos
            upload_folder: Pasta para CSVs uploadados
        """
        self.session_factory = session_factory
        self.models_folder = Path(models_folder)
        self.upload_folder = Path(upload_folder)

        # Criar pastas se não existirem
        self.models_folder.mkdir(parents=True, exist_ok=True)
        self.upload_folder.mkdir(parents=True, exist_ok=True)

    def _detect_csv_format(self, df: pd.DataFrame) -> str:
        """
        Detecta se CSV está em formato brasileiro (PT) ou padrão (EN).

        Args:
            df: DataFrame com dados do CSV

        Returns:
            'pt-BR' se formato brasileiro, 'en' se padrão, 'unknown' se não reconhecido
        """
        pt_columns = {'Data de Efetivação', 'Descrição', 'Valor', 'Categoria'}
        en_columns = {'date', 'description', 'value', 'category'}

        df_columns = set(df.columns)

        if pt_columns.issubset(df_columns):
            return 'pt-BR'
        elif en_columns.issubset(df_columns):
            return 'en'
        else:
            return 'unknown'

    def _parse_brazilian_value(self, value_str: str) -> float:
        """
        Converte valor monetário brasileiro para float.
        Suporta múltiplos formatos:
        - "R$ 1.234,56" (formato BR padrão: ponto=milhar, vírgula=decimal)
        - "R$ 1234.56" (formato americano com prefixo R$)
        - "R$  0.39"

        Args:
            value_str: String com valor monetário

        Returns:
            Valor como float

        Examples:
            "R$ 1.234,56" -> 1234.56
            "R$ 1234.56" -> 1234.56
            "R$  0.39" -> 0.39
        """
        if pd.isna(value_str):
            return None

        # Remover "R$" e espaços
        clean = str(value_str).replace('R$', '').strip()

        # Remover aspas se houver
        clean = clean.replace('"', '')

        # Detectar formato: se tem vírgula, é formato brasileiro (ponto=milhar, vírgula=decimal)
        # Se não tem vírgula, é formato americano (ponto=decimal)
        if ',' in clean:
            # Formato brasileiro: R$ 1.234,56
            # Remover pontos de milhar e trocar vírgula por ponto
            clean = clean.replace('.', '').replace(',', '.')
        # else: formato americano ou sem decimal, manter como está

        return pd.to_numeric(clean, errors='coerce')

    def validate_csv(self, file_path: str) -> Tuple[bool, List[str]]:
        """
        Valida se o CSV tem o formato correto para treinamento.
        Suporta formato brasileiro (PT) e padrão (EN).

        Args:
            file_path: Caminho do arquivo CSV

        Returns:
            Tupla (válido, lista_de_erros)
        """
        errors = []

        try:
            # Ler com UTF-8-sig para suportar BOM
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        except Exception as e:
            errors.append(f"Erro ao ler CSV: {str(e)}")
            return False, errors

        # Limpar nomes das colunas
        df.columns = df.columns.str.strip()

        # Detectar formato
        csv_format = self._detect_csv_format(df)

        if csv_format == 'pt-BR':
            required_columns = ['Data de Efetivação', 'Descrição', 'Valor', 'Categoria']
            format_name = "brasileiro"
        elif csv_format == 'en':
            required_columns = ['date', 'description', 'value', 'type', 'category']
            format_name = "padrão"
        else:
            errors.append(
                "Formato de CSV não reconhecido. "
                "Colunas esperadas (PT): Data de Efetivação, Descrição, Valor, Categoria. "
                "OU Colunas esperadas (EN): date, description, value, type, category"
            )
            return False, errors

        # Verificar colunas obrigatórias
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            errors.append(
                f"Colunas faltando para formato {format_name}: {', '.join(missing_columns)}"
            )

        # Verificar se há dados
        if len(df) == 0:
            errors.append("CSV está vazio (sem linhas)")

        # Verificar se há categorias
        category_col = 'Categoria' if csv_format == 'pt-BR' else 'category'
        if category_col in df.columns and df[category_col].notna().sum() == 0:
            errors.append("Nenhuma transação possui categoria definida")

        is_valid = len(errors) == 0
        return is_valid, errors

    def preview_csv(self, file_path: str, limit: int = 10) -> Dict:
        """
        Retorna preview das primeiras linhas do CSV.
        Suporta formato brasileiro (PT) e padrão (EN).

        Args:
            file_path: Caminho do arquivo
            limit: Número de linhas para preview

        Returns:
            Dict com info do CSV
        """
        # Ler com UTF-8-sig para suportar BOM
        df = pd.read_csv(file_path, encoding='utf-8-sig')

        # Limpar nomes das colunas
        df.columns = df.columns.str.strip()

        # Detectar formato
        csv_format = self._detect_csv_format(df)
        category_col = 'Categoria' if csv_format == 'pt-BR' else 'category'

        # Substituir NaN por None para JSON válido
        df_preview = df.head(limit).where(pd.notna(df.head(limit)), None)

        return {
            "total_rows": len(df),
            "columns": list(df.columns),
            "format": csv_format,
            "preview": df_preview.to_dict(orient='records'),
            "categories_count": df[category_col].nunique() if category_col in df.columns else 0,
            "sample_categories": [cat for cat in df[category_col].unique().tolist()[:10] if pd.notna(cat)]
        }

    def prepare_training_data(self, csv_path: str) -> pd.DataFrame:
        """
        Prepara dados do CSV para treinamento.
        Suporta formato brasileiro (PT) e padrão (EN).

        Args:
            csv_path: Caminho do CSV

        Returns:
            DataFrame pronto para treinar
        """
        # Ler com UTF-8-sig para suportar BOM
        df = pd.read_csv(csv_path, encoding='utf-8-sig')

        # Limpar nomes das colunas
        df.columns = df.columns.str.strip()

        # Detectar formato
        csv_format = self._detect_csv_format(df)

        # Converter formato brasileiro para padrão
        if csv_format == 'pt-BR':
            # Mapear colunas
            df_mapped = pd.DataFrame()
            df_mapped['date'] = df['Data de Efetivação']
            df_mapped['description'] = df['Descrição']

            # Parsear valores brasileiros
            df_mapped['value'] = df['Valor'].apply(self._parse_brazilian_value)

            df_mapped['category'] = df['Categoria']

            # Inferir tipo da transação baseado no valor
            df_mapped['type'] = df_mapped['value'].apply(
                lambda x: 'credito' if x > 0 else 'debito'
            )

            df = df_mapped

            # Converter datas do formato brasileiro DD/MM/YYYY
            df['date'] = pd.to_datetime(df['date'], format='%d/%m/%Y', errors='coerce')
        else:
            # Formato padrão (inglês)
            required_columns = ['date', 'description', 'value', 'type', 'category']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Coluna '{col}' não encontrada no CSV")

            # Converter datas (formato padrão)
            df['date'] = pd.to_datetime(df['date'], errors='coerce')

            # Converter valores para float
            df['value'] = pd.to_numeric(df['value'], errors='coerce')

        # Limpeza comum para ambos os formatos

        # Remover linhas sem categoria
        df = df.dropna(subset=['category'])

        # Remover linhas sem data
        df = df.dropna(subset=['date'])

        # Remover linhas sem valor
        df = df.dropna(subset=['value'])

        # Normalizar tipo de transação
        df['type'] = df['type'].str.lower().str.strip()

        # Garantir que temos as colunas necessárias
        final_columns = ['date', 'description', 'value', 'type', 'category']
        return df[final_columns]

    def train_model(
        self,
        data: pd.DataFrame,
        user_id: int,
        source: TrainingJobSource = TrainingJobSource.CSV_UPLOAD,
        csv_path: Optional[str] = None
    ) -> Dict:
        """
        Treina um novo modelo ML.

        Args:
            data: DataFrame com dados de treinamento
            user_id: ID do usuário que iniciou treinamento
            source: Origem dos dados
            csv_path: Caminho do CSV (se aplicável)

        Returns:
            Dict com métricas e info do job
        """
        session = self.session_factory()

        try:
            # Criar job de treinamento
            model_version = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

            job = TrainingJob(
                user_id=user_id,
                status=TrainingJobStatus.RUNNING,
                source=source,
                csv_path=csv_path,
                model_version=model_version
            )
            session.add(job)
            session.commit()

            # Treinar modelo
            trainer = TransactionClassifierTrainer(max_features=100, random_state=42)

            # Filtrar categorias com poucas amostras (mínimo 2 para cross-validation)
            category_counts = data['category'].value_counts()
            min_samples = 2  # Mínimo para stratified split funcionar
            valid_categories = category_counts[category_counts >= min_samples].index.tolist()

            if len(valid_categories) < len(category_counts):
                removed_categories = category_counts[category_counts < min_samples]
                print(f"⚠️  Removendo {len(removed_categories)} categoria(s) com < {min_samples} amostras:")
                for cat, count in removed_categories.items():
                    print(f"   - {cat}: {count} amostra(s)")

                # Filtrar dataset
                data = data[data['category'].isin(valid_categories)].copy()
                print(f"✅ Dataset filtrado: {len(data)} transações, {len(valid_categories)} categorias")

            try:
                metrics = trainer.train(data, test_size=0.2)

                # Salvar modelo
                model_path = str(self.models_folder / f"model_{model_version}.pkl")
                trainer.save_model(model_path)

                # Atualizar job com sucesso
                job.status = TrainingJobStatus.COMPLETED
                job.metrics = metrics
                job.completed_at = datetime.utcnow()
                session.commit()

                return {
                    "job_id": job.id,
                    "status": "completed",
                    "model_version": model_version,
                    "model_path": model_path,
                    "metrics": metrics
                }

            except Exception as train_error:
                # Atualizar job com falha
                job.status = TrainingJobStatus.FAILED
                job.error_message = str(train_error)
                job.completed_at = datetime.utcnow()
                session.commit()
                raise

        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def auto_retrain_from_approved(
        self,
        user_id: int,
        min_transactions: int = 100
    ) -> Optional[Dict]:
        """
        Re-treina modelo usando transações aprovadas.

        Args:
            user_id: ID do usuário
            min_transactions: Mínimo de transações necessárias

        Returns:
            Dict com resultado ou None se não houver dados suficientes
        """
        session = self.session_factory()

        try:
            # Buscar transações aprovadas/modificadas com categoria
            # Nota: final_category é uma property, então filtramos pelas colunas reais
            from sqlalchemy import or_
            query = session.query(PendingTransaction).filter(
                PendingTransaction.review_status.in_([
                    ReviewStatus.APPROVED,
                    ReviewStatus.MODIFIED
                ])
            ).filter(
                or_(
                    PendingTransaction.user_category.isnot(None),
                    PendingTransaction.predicted_category.isnot(None)
                )
            )

            transactions = query.all()

            if len(transactions) < min_transactions:
                return None  # Dados insuficientes

            # Converter para DataFrame
            data = []
            for tx in transactions:
                data.append({
                    'date': tx.date,
                    'description': tx.description,
                    'value': tx.amount,
                    'type': tx.transaction_type if tx.transaction_type else 'debito',
                    'category': tx.final_category
                })

            df = pd.DataFrame(data)

            # Treinar modelo
            result = self.train_model(
                data=df,
                user_id=user_id,
                source=TrainingJobSource.AUTO_RETRAIN
            )

            return result

        finally:
            session.close()

    def get_job_status(self, job_id: int) -> Optional[Dict]:
        """
        Retorna status de um job de treinamento.

        Args:
            job_id: ID do job

        Returns:
            Dict com info do job ou None
        """
        session = self.session_factory()
        try:
            job = session.query(TrainingJob).filter(TrainingJob.id == job_id).first()
            return job.to_dict() if job else None
        finally:
            session.close()

    def list_training_history(self, user_id: Optional[int] = None, limit: int = 20) -> List[Dict]:
        """
        Lista histórico de treinamentos.

        Args:
            user_id: Filtrar por usuário (opcional)
            limit: Máximo de resultados

        Returns:
            Lista de jobs
        """
        session = self.session_factory()
        try:
            query = session.query(TrainingJob).order_by(TrainingJob.created_at.desc())

            if user_id:
                query = query.filter(TrainingJob.user_id == user_id)

            jobs = query.limit(limit).all()
            return [job.to_dict() for job in jobs]
        finally:
            session.close()

    def activate_model(self, model_version: str) -> bool:
        """
        Ativa um modelo treinado (substitui o modelo atual).

        Args:
            model_version: Versão do modelo a ativar

        Returns:
            True se sucesso
        """
        source_path = self.models_folder / f"model_{model_version}.pkl"
        target_path = self.models_folder / "category_classifier.pkl"

        if not source_path.exists():
            raise FileNotFoundError(f"Modelo {model_version} não encontrado")

        # Criar backup do modelo atual
        if target_path.exists():
            backup_path = target_path.parent / f"category_classifier_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pkl"
            import shutil
            shutil.copy(str(target_path), str(backup_path))

        # Copiar novo modelo
        import shutil
        shutil.copy(str(source_path), str(target_path))

        return True
