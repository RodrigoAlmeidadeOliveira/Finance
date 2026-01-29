"""
Módulo para importação de arquivos OFX (Open Financial Exchange).
"""
from typing import Dict, List, Optional
from datetime import datetime
from io import BytesIO
import hashlib

import ofxparse
from ofxparse import OfxParser
from ofxparse.ofxparse import Account, Transaction as OfxTransaction


class OFXImporter:
    """
    Importa e parseia arquivos OFX de bancos brasileiros.
    """

    @staticmethod
    def parse_ofx_file(file_path: str) -> Dict:
        """
        Parseia um arquivo OFX e extrai informações.

        Args:
            file_path: Caminho do arquivo OFX

        Returns:
            Dicionário com dados extraídos
        """
        with open(file_path, 'rb') as ofx_file:
            ofx = OfxParser.parse(ofx_file)

        return OFXImporter._extract_data_from_ofx(ofx)

    @staticmethod
    def parse_ofx_content(file_content: bytes) -> Dict:
        """
        Parseia conteúdo de arquivo OFX.

        Args:
            file_content: Conteúdo do arquivo OFX em bytes

        Returns:
            Dicionário com dados extraídos
        """
        # Converter bytes para file-like object
        file_like = BytesIO(file_content)
        ofx = OfxParser.parse(file_like)
        return OFXImporter._extract_data_from_ofx(ofx)

    @staticmethod
    def _extract_data_from_ofx(ofx) -> Dict:
        """
        Extrai dados estruturados de um objeto OFX parseado.

        Args:
            ofx: Objeto OFX parseado

        Returns:
            Dicionário com dados estruturados
        """
        # Informações da conta
        account = ofx.account if hasattr(ofx, 'account') else None

        if not account:
            raise ValueError("Arquivo OFX não contém informações de conta")

        # Informações da instituição
        institution = {
            'name': account.institution.organization if hasattr(account.institution, 'organization') else 'Desconhecido',
            'id': account.institution.fid if hasattr(account.institution, 'fid') else None
        }

        # Informações da conta
        account_info = {
            'account_id': account.account_id,
            'routing_number': account.routing_number if hasattr(account, 'routing_number') else None,
            'account_type': account.account_type if hasattr(account, 'account_type') else 'checking',
            'branch_id': account.branch_id if hasattr(account, 'branch_id') else None,
        }

        # Saldo
        statement = account.statement
        balance_info = {
            'balance': float(statement.balance) if statement.balance else 0.0,
            'balance_date': statement.balance_date if hasattr(statement, 'balance_date') else None,
            'available_balance': float(statement.available_balance) if hasattr(statement, 'available_balance') and statement.available_balance else None,
        }

        # Período do extrato
        period = {
            'start_date': statement.start_date if hasattr(statement, 'start_date') else None,
            'end_date': statement.end_date if hasattr(statement, 'end_date') else None,
        }

        # Transações
        transactions = []
        for ofx_trans in statement.transactions:
            transaction = OFXImporter._parse_transaction(ofx_trans, account.account_id)
            transactions.append(transaction)

        return {
            'institution': institution,
            'account': account_info,
            'balance': balance_info,
            'period': period,
            'transactions': transactions,
            'total_transactions': len(transactions)
        }

    @staticmethod
    def _parse_transaction(ofx_trans: OfxTransaction, account_id: str) -> Dict:
        """
        Parseia uma transação OFX individual.

        Args:
            ofx_trans: Objeto de transação OFX
            account_id: ID da conta

        Returns:
            Dicionário com dados da transação
        """
        # Tipo de transação
        trans_type = str(ofx_trans.type).lower() if ofx_trans.type else 'other'

        # Determinar se é débito ou crédito baseado no valor
        amount = float(ofx_trans.amount)
        transaction_type = 'credito' if amount > 0 else 'debito'

        # Limpar descrição (remover espaços extras)
        description = ' '.join(ofx_trans.memo.split()) if ofx_trans.memo else ''
        if ofx_trans.payee and ofx_trans.payee != description:
            # Combinar payee e memo se diferentes
            description = f"{ofx_trans.payee} {description}".strip()

        # FITID (Financial Transaction ID) - usado para detectar duplicatas
        fitid = ofx_trans.id if ofx_trans.id else None

        # Se não tem FITID, gerar hash baseado nos dados
        if not fitid:
            fitid = OFXImporter._generate_transaction_hash(
                date=ofx_trans.date,
                amount=amount,
                description=description,
                account_id=account_id
            )

        return {
            'fitid': fitid,
            'date': ofx_trans.date,
            'description': description,
            'amount': amount,
            'type': transaction_type,
            'ofx_type': trans_type,
            'payee': ofx_trans.payee if ofx_trans.payee else None,
            'memo': ofx_trans.memo if ofx_trans.memo else None,
            'check_number': ofx_trans.checknum if hasattr(ofx_trans, 'checknum') and ofx_trans.checknum else None,
        }

    @staticmethod
    def _generate_transaction_hash(date, amount: float, description: str, account_id: str) -> str:
        """
        Gera um hash único para uma transação (usado quando FITID não está disponível).

        Args:
            date: Data da transação
            amount: Valor da transação
            description: Descrição
            account_id: ID da conta

        Returns:
            Hash hexadecimal
        """
        # Criar string única
        date_str = date.strftime('%Y%m%d') if isinstance(date, datetime) else str(date)
        unique_str = f"{account_id}_{date_str}_{amount}_{description}"

        # Gerar hash MD5
        hash_object = hashlib.md5(unique_str.encode())
        return hash_object.hexdigest()

    @staticmethod
    def validate_ofx_file(file_path: str) -> Dict:
        """
        Valida um arquivo OFX sem fazer parse completo.

        Args:
            file_path: Caminho do arquivo

        Returns:
            Dicionário com resultado da validação
        """
        try:
            with open(file_path, 'rb') as f:
                content = f.read()

            # Verificar se parece um arquivo OFX
            content_str = content.decode('latin-1', errors='ignore')

            if 'OFX' not in content_str.upper():
                return {
                    'valid': False,
                    'error': 'Arquivo não parece ser formato OFX'
                }

            # Tentar parse
            OFXImporter.parse_ofx_content(content)

            return {
                'valid': True,
                'error': None
            }

        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }

    @staticmethod
    def get_import_summary(parsed_data: Dict) -> Dict:
        """
        Gera um resumo dos dados importados.

        Args:
            parsed_data: Dados parseados do OFX

        Returns:
            Dicionário com resumo
        """
        transactions = parsed_data['transactions']

        # Contar débitos e créditos
        debits = [t for t in transactions if t['type'] == 'debito']
        credits = [t for t in transactions if t['type'] == 'credito']

        total_debit = sum(abs(t['amount']) for t in debits)
        total_credit = sum(t['amount'] for t in credits)

        return {
            'institution': parsed_data['institution']['name'],
            'account_id': parsed_data['account']['account_id'],
            'period': {
                'start': parsed_data['period']['start_date'],
                'end': parsed_data['period']['end_date']
            },
            'balance': {
                'current': parsed_data['balance']['balance'],
                'available': parsed_data['balance']['available_balance']
            },
            'transactions': {
                'total': parsed_data['total_transactions'],
                'debits': {
                    'count': len(debits),
                    'total': total_debit
                },
                'credits': {
                    'count': len(credits),
                    'total': total_credit
                }
            }
        }
