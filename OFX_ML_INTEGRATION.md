# IMPORTAÇÃO OFX + MACHINE LEARNING - CLASSIFICAÇÃO AUTOMÁTICA

**Projeto:** Planner Financeiro Web
**Prioridade:** MÁXIMA - Feature Principal
**Versão:** 1.0
**Data:** 18 de Dezembro de 2025

---

## ÍNDICE

1. [Visão Geral](#visão-geral)
2. [Formato OFX](#formato-ofx)
3. [Arquitetura do Sistema](#arquitetura-do-sistema)
4. [Pipeline de Importação](#pipeline-de-importação)
5. [Machine Learning - Classificação](#machine-learning---classificação)
6. [Dataset de Treino](#dataset-de-treino)
7. [API Endpoints](#api-endpoints)
8. [Interface do Usuário](#interface-do-usuário)
9. [Implementação Passo a Passo](#implementação-passo-a-passo)

---

## VISÃO GERAL

### Objetivo Principal

**Automatizar a classificação de transações bancárias** importadas de arquivos OFX usando Machine Learning treinado no histórico de transações já categorizadas na planilha Excel existente.

### Fluxo Completo

```
┌─────────────────────────────────────────────────────────────────┐
│                    FLUXO DE IMPORTAÇÃO OFX                      │
└─────────────────────────────────────────────────────────────────┘

1. Upload OFX
   ↓
2. Parse do arquivo (ofxparse)
   ↓
3. Extrair transações
   ↓
4. ┌─────────────────────────────────────┐
   │   ML: Classificação Automática      │
   │   - Feature extraction              │
   │   - Predict categoria               │
   │   - Confidence score                │
   └─────────────────────────────────────┘
   ↓
5. Salvar transações com sugestões
   ↓
6. Interface de Revisão
   ├─ Aceitar classificação sugerida
   ├─ Corrigir e ensinar modelo
   └─ Rejeitar transação
   ↓
7. Confirmar e persistir
   ↓
8. ┌─────────────────────────────────────┐
   │   Retreinar modelo (background)     │
   │   - Incluir novas transações        │
   │   - Melhorar accuracy                │
   └─────────────────────────────────────┘
```

---

## FORMATO OFX

### O que é OFX?

**OFX (Open Financial Exchange)** é um formato padrão usado por bancos brasileiros para exportar extratos bancários e de cartão de crédito.

### Exemplo de Arquivo OFX

```xml
<?xml version="1.0" encoding="UTF-8"?>
<OFX>
  <SIGNONMSGSRSV1>
    <SONRS>
      <STATUS>
        <CODE>0</CODE>
        <SEVERITY>INFO</SEVERITY>
      </STATUS>
      <DTSERVER>20241218120000</DTSERVER>
      <LANGUAGE>POR</LANGUAGE>
    </SONRS>
  </SIGNONMSGSRSV1>

  <BANKMSGSRSV1>
    <STMTTRNRS>
      <TRNUID>1</TRNUID>
      <STATUS>
        <CODE>0</CODE>
        <SEVERITY>INFO</SEVERITY>
      </STATUS>
      <STMTRS>
        <CURDEF>BRL</CURDEF>
        <BANKACCTFROM>
          <BANKID>001</BANKID>
          <ACCTID>12345-6</ACCTID>
          <ACCTTYPE>CHECKING</ACCTTYPE>
        </BANKACCTFROM>

        <BANKTRANLIST>
          <DTSTART>20241101000000</DTSTART>
          <DTEND>20241130235959</DTEND>

          <STMTTRN>
            <TRNTYPE>DEBIT</TRNTYPE>
            <DTPOSTED>20241115000000</DTPOSTED>
            <TRNAMT>-250.50</TRNAMT>
            <FITID>202411150001</FITID>
            <MEMO>SUPERMERCADO CARREFOUR SAO PAULO BR</MEMO>
          </STMTTRN>

          <STMTTRN>
            <TRNTYPE>CREDIT</TRNTYPE>
            <DTPOSTED>20241105000000</DTPOSTED>
            <TRNAMT>3500.00</TRNAMT>
            <FITID>202411050001</FITID>
            <MEMO>SALARIO EMPRESA XYZ LTDA</MEMO>
          </STMTTRN>

          <STMTTRN>
            <TRNTYPE>DEBIT</TRNTYPE>
            <DTPOSTED>20241120000000</DTPOSTED>
            <TRNAMT>-89.90</TRNAMT>
            <FITID>202411200001</FITID>
            <MEMO>POSTO SHELL BR 356 COMBUSTIVEL</MEMO>
          </STMTTRN>

        </BANKTRANLIST>

        <LEDGERBAL>
          <BALAMT>5432.10</BALAMT>
          <DTASOF>20241130235959</DTASOF>
        </LEDGERBAL>

      </STMTRS>
    </STMTTRNRS>
  </BANKMSGSRSV1>
</OFX>
```

### Campos Importantes

| Campo | Descrição | Uso |
|-------|-----------|-----|
| `TRNTYPE` | Tipo (DEBIT/CREDIT) | Determinar se é receita/despesa |
| `DTPOSTED` | Data da transação | `event_date` |
| `TRNAMT` | Valor | `value` |
| `FITID` | ID único da transação | Evitar duplicatas |
| `MEMO` | Descrição | **Feature principal para ML** |
| `BANKID` | Código do banco | Identificar instituição |
| `ACCTID` | Número da conta | Vincular à instituição |

---

## ARQUITETURA DO SISTEMA

### Novos Componentes

```
backend/app/
├── ml/                              # 🆕 Módulo de Machine Learning
│   ├── __init__.py
│   ├── classifier.py                # Classificador principal
│   ├── feature_extractor.py         # Extração de features
│   ├── model_trainer.py             # Treinamento do modelo
│   ├── predictor.py                 # Predições
│   └── models/                      # Modelos salvos
│       ├── category_classifier.pkl
│       └── vectorizer.pkl
│
├── importers/                       # 🆕 Importadores
│   ├── __init__.py
│   ├── ofx_importer.py             # Importador OFX
│   ├── csv_importer.py             # Importador CSV (futuro)
│   └── base_importer.py            # Classe base
│
├── services/
│   ├── import_service.py           # 🆕 Orquestração de importação
│   ├── classification_service.py   # 🆕 Classificação ML
│   └── ...
│
├── api/
│   ├── imports.py                  # 🆕 Endpoints de importação
│   └── ...
│
└── models/
    ├── import_batch.py             # 🆕 Model de batch de importação
    ├── pending_transaction.py      # 🆕 Transações pendentes de revisão
    └── ...
```

### Novas Tabelas no Banco

#### 1. import_batches

```sql
CREATE TABLE import_batches (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    institution_id INTEGER NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(10) NOT NULL,  -- 'OFX', 'CSV'
    imported_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_transactions INTEGER NOT NULL,
    processed_transactions INTEGER NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- 'pending', 'reviewing', 'completed', 'failed'
    metadata JSONB,  -- Informações do arquivo (banco, conta, período, etc.)

    CONSTRAINT fk_import_batches_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_import_batches_institution FOREIGN KEY (institution_id)
        REFERENCES institutions(id) ON DELETE RESTRICT,
    CONSTRAINT ck_import_batches_status CHECK (status IN ('pending', 'reviewing', 'completed', 'failed'))
);

CREATE INDEX idx_import_batches_user ON import_batches(user_id);
CREATE INDEX idx_import_batches_status ON import_batches(status);
```

#### 2. pending_transactions

```sql
CREATE TABLE pending_transactions (
    id SERIAL PRIMARY KEY,
    import_batch_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,

    -- Dados da transação original (OFX)
    fitid VARCHAR(100) NOT NULL,  -- ID único do banco
    event_date DATE NOT NULL,
    description VARCHAR(255) NOT NULL,
    value NUMERIC(12, 2) NOT NULL,

    -- Classificação sugerida pelo ML
    suggested_category_id INTEGER,
    confidence_score NUMERIC(5, 4),  -- 0.0000 a 1.0000

    -- Classificação final (após revisão do usuário)
    final_category_id INTEGER,
    final_institution_id INTEGER,
    final_credit_card_id INTEGER,

    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'pending',  -- 'pending', 'accepted', 'corrected', 'rejected'
    reviewed_at TIMESTAMP,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_pending_transactions_batch FOREIGN KEY (import_batch_id)
        REFERENCES import_batches(id) ON DELETE CASCADE,
    CONSTRAINT fk_pending_transactions_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_pending_transactions_suggested_category FOREIGN KEY (suggested_category_id)
        REFERENCES categories(id) ON DELETE SET NULL,
    CONSTRAINT fk_pending_transactions_final_category FOREIGN KEY (final_category_id)
        REFERENCES categories(id) ON DELETE RESTRICT,
    CONSTRAINT ck_pending_transactions_status CHECK (status IN ('pending', 'accepted', 'corrected', 'rejected')),
    CONSTRAINT uq_pending_transactions_fitid UNIQUE (import_batch_id, fitid)
);

CREATE INDEX idx_pending_transactions_batch ON pending_transactions(import_batch_id);
CREATE INDEX idx_pending_transactions_user ON pending_transactions(user_id);
CREATE INDEX idx_pending_transactions_status ON pending_transactions(status);
```

---

## PIPELINE DE IMPORTAÇÃO

### 1. Parser OFX

```python
# app/importers/ofx_importer.py
from typing import List, Dict
from ofxparse import OfxParser
from datetime import datetime
from decimal import Decimal

class OFXImporter:
    """Importador de arquivos OFX"""

    def __init__(self):
        self.supported_encodings = ['UTF-8', 'ISO-8859-1', 'Windows-1252']

    def parse_file(self, file_path: str) -> Dict:
        """
        Parse arquivo OFX e extrai informações

        Returns:
            {
                'bank_id': '001',
                'account_id': '12345-6',
                'account_type': 'CHECKING',
                'start_date': datetime,
                'end_date': datetime,
                'balance': Decimal,
                'transactions': [...]
            }
        """
        # Tentar diferentes encodings
        ofx_data = None
        for encoding in self.supported_encodings:
            try:
                with open(file_path, encoding=encoding) as f:
                    ofx_data = OfxParser.parse(f)
                break
            except UnicodeDecodeError:
                continue

        if not ofx_data:
            raise ValueError("Não foi possível decodificar o arquivo OFX")

        # Extrair conta bancária
        account = ofx_data.account

        # Extrair transações
        transactions = []
        for txn in account.statement.transactions:
            transactions.append({
                'fitid': txn.id,
                'date': txn.date,
                'amount': Decimal(str(txn.amount)),
                'type': txn.type,
                'memo': txn.memo or txn.payee or '',
                'checknum': txn.checknum
            })

        return {
            'bank_id': account.institution.organization if account.institution else None,
            'account_id': account.number,
            'account_type': account.type,
            'start_date': account.statement.start_date,
            'end_date': account.statement.end_date,
            'balance': Decimal(str(account.statement.balance)),
            'transactions': transactions
        }

    def detect_duplicates(self, transactions: List[Dict], user_id: int) -> List[str]:
        """
        Detectar transações duplicadas pelo FITID

        Returns:
            Lista de FITIDs já existentes no banco
        """
        from app.models.transaction import Transaction

        fitids = [t['fitid'] for t in transactions]

        # Query no banco para verificar duplicatas
        existing = Transaction.query.filter(
            Transaction.user_id == user_id,
            Transaction.fitid.in_(fitids)
        ).all()

        return [t.fitid for t in existing]
```

### 2. Service de Importação

```python
# app/services/import_service.py
from typing import Dict, List
from datetime import datetime
from app.importers.ofx_importer import OFXImporter
from app.services.classification_service import ClassificationService
from app.models.import_batch import ImportBatch
from app.models.pending_transaction import PendingTransaction
from app.repositories.institution_repository import InstitutionRepository
from app.extensions import db

class ImportService:
    """Orquestra o processo de importação"""

    def __init__(self):
        self.ofx_importer = OFXImporter()
        self.classification_service = ClassificationService()
        self.institution_repo = InstitutionRepository()

    def import_ofx(self, user_id: int, file_path: str, file_name: str) -> ImportBatch:
        """
        Importar arquivo OFX completo

        1. Parse do arquivo
        2. Identificar/criar instituição
        3. Criar batch de importação
        4. Classificar transações com ML
        5. Salvar como pendentes

        Returns:
            ImportBatch criado
        """
        # 1. Parse OFX
        ofx_data = self.ofx_importer.parse_file(file_path)

        # 2. Identificar instituição
        institution = self._find_or_create_institution(
            user_id=user_id,
            bank_id=ofx_data['bank_id'],
            account_id=ofx_data['account_id'],
            account_type=ofx_data['account_type']
        )

        # 3. Detectar duplicatas
        duplicates = self.ofx_importer.detect_duplicates(
            ofx_data['transactions'],
            user_id
        )

        # Filtrar transações já existentes
        new_transactions = [
            t for t in ofx_data['transactions']
            if t['fitid'] not in duplicates
        ]

        if not new_transactions:
            raise ValueError("Todas as transações já foram importadas anteriormente")

        # 4. Criar batch de importação
        batch = ImportBatch(
            user_id=user_id,
            institution_id=institution.id,
            file_name=file_name,
            file_type='OFX',
            total_transactions=len(new_transactions),
            status='pending',
            metadata={
                'bank_id': ofx_data['bank_id'],
                'account_id': ofx_data['account_id'],
                'start_date': ofx_data['start_date'].isoformat(),
                'end_date': ofx_data['end_date'].isoformat(),
                'balance': str(ofx_data['balance']),
                'duplicates_skipped': len(duplicates)
            }
        )
        db.session.add(batch)
        db.session.flush()  # Para obter batch.id

        # 5. Classificar e salvar transações
        for txn in new_transactions:
            # Classificação automática com ML
            prediction = self.classification_service.predict_category(
                user_id=user_id,
                description=txn['memo'],
                amount=txn['amount']
            )

            # Criar transação pendente
            pending = PendingTransaction(
                import_batch_id=batch.id,
                user_id=user_id,
                fitid=txn['fitid'],
                event_date=txn['date'],
                description=txn['memo'],
                value=txn['amount'],
                suggested_category_id=prediction['category_id'],
                confidence_score=prediction['confidence'],
                status='pending'
            )
            db.session.add(pending)

        batch.status = 'reviewing'
        db.session.commit()

        return batch

    def _find_or_create_institution(self, user_id: int, bank_id: str,
                                     account_id: str, account_type: str):
        """Encontrar ou criar instituição financeira"""
        # Mapear código do banco para nome
        BANK_NAMES = {
            '001': 'Banco do Brasil',
            '033': 'Santander',
            '104': 'Caixa Econômica',
            '237': 'Bradesco',
            '341': 'Itaú',
            '260': 'Nubank',
            # ... adicionar mais bancos
        }

        bank_name = BANK_NAMES.get(bank_id, f'Banco {bank_id}')

        # Buscar instituição existente
        institution = self.institution_repo.find_by_name_and_type(
            user_id=user_id,
            name=bank_name,
            type='bank'
        )

        if not institution:
            # Criar nova instituição
            institution = self.institution_repo.create({
                'user_id': user_id,
                'name': bank_name,
                'type': 'bank',
                'partition': f'Conta {account_id[-4:]}'  # Últimos 4 dígitos
            })

        return institution

    def confirm_batch(self, batch_id: int, user_id: int) -> int:
        """
        Confirmar batch de importação e criar transações definitivas

        Returns:
            Número de transações criadas
        """
        batch = ImportBatch.query.get(batch_id)

        if not batch or batch.user_id != user_id:
            raise ValueError("Batch não encontrado")

        if batch.status != 'reviewing':
            raise ValueError(f"Batch não pode ser confirmado (status: {batch.status})")

        # Buscar transações pendentes aceitas ou corrigidas
        pending_txns = PendingTransaction.query.filter(
            PendingTransaction.import_batch_id == batch_id,
            PendingTransaction.status.in_(['accepted', 'corrected'])
        ).all()

        from app.models.transaction import Transaction

        created_count = 0
        for pending in pending_txns:
            # Criar transação definitiva
            transaction = Transaction(
                user_id=user_id,
                category_id=pending.final_category_id,
                institution_id=pending.final_institution_id or batch.institution_id,
                credit_card_id=pending.final_credit_card_id,
                event_date=pending.event_date,
                effective_date=pending.event_date,  # Assumir mesma data
                description=pending.description,
                value=pending.value,
                status='completed',
                fitid=pending.fitid
            )
            db.session.add(transaction)
            created_count += 1

            # Se foi corrigida, treinar modelo com nova informação
            if pending.status == 'corrected':
                self.classification_service.add_training_example(
                    description=pending.description,
                    amount=pending.value,
                    category_id=pending.final_category_id
                )

        batch.status = 'completed'
        batch.processed_transactions = created_count
        db.session.commit()

        # Retreinar modelo em background (Celery ou similar)
        # self.classification_service.retrain_model_async(user_id)

        return created_count
```

---

## MACHINE LEARNING - CLASSIFICAÇÃO

### Estratégia de ML

**Algoritmo:** Naive Bayes Multinomial ou Random Forest
**Features:** TF-IDF da descrição + valor normalizado + dia do mês
**Labels:** category_id

### 1. Feature Extractor

```python
# app/ml/feature_extractor.py
import re
import unicodedata
from typing import Dict, List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

class FeatureExtractor:
    """Extrai features de transações para ML"""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),  # Unigrams e bigrams
            min_df=2,
            stop_words=self._get_stopwords()
        )

    def _get_stopwords(self) -> List[str]:
        """Stopwords para português"""
        return [
            'de', 'da', 'do', 'dos', 'das', 'em', 'na', 'no', 'nas', 'nos',
            'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas',
            'para', 'por', 'com', 'sem', 'sob', 'sobre',
            'ltda', 'sa', 'me', 'epp', 'eireli',
            'parc', 'parcela', 'brasil', 'br'
        ]

    def clean_description(self, text: str) -> str:
        """
        Limpar e normalizar descrição

        - Remove acentos
        - Lowercase
        - Remove números de parcelas
        - Remove pontuação excessiva
        """
        if not text:
            return ""

        # Remover acentos
        text = unicodedata.normalize('NFKD', text)
        text = text.encode('ASCII', 'ignore').decode('ASCII')

        # Lowercase
        text = text.lower()

        # Remover padrões comuns
        text = re.sub(r'parc\s*\d+/\d+', '', text)  # parcela 1/12
        text = re.sub(r'\d{2}/\d{2}/\d{4}', '', text)  # datas
        text = re.sub(r'\d{2}/\d{2}', '', text)  # datas curtas
        text = re.sub(r'[*]{2,}', '', text)  # asteriscos

        # Remover pontuação excessiva, manter espaços
        text = re.sub(r'[^\w\s]', ' ', text)

        # Remover múltiplos espaços
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def extract_features(self, description: str, amount: float,
                         date: str = None) -> np.ndarray:
        """
        Extrair features de uma transação

        Returns:
            Array numpy com features
        """
        # 1. Text features (TF-IDF)
        clean_desc = self.clean_description(description)
        text_features = self.vectorizer.transform([clean_desc]).toarray()[0]

        # 2. Numeric features
        numeric_features = []

        # Valor normalizado (log scale para lidar com diferentes magnitudes)
        amount_normalized = np.log1p(abs(amount))
        numeric_features.append(amount_normalized)

        # Tipo (receita ou despesa)
        is_income = 1 if amount > 0 else 0
        numeric_features.append(is_income)

        # Dia do mês (se fornecido)
        if date:
            from datetime import datetime
            if isinstance(date, str):
                date = datetime.fromisoformat(date)
            day_of_month = date.day
            numeric_features.append(day_of_month / 31.0)  # Normalizado 0-1
        else:
            numeric_features.append(0.0)

        # Concatenar text + numeric features
        all_features = np.concatenate([text_features, numeric_features])

        return all_features

    def fit_vectorizer(self, descriptions: List[str]):
        """Treinar o vetorizador TF-IDF com corpus de descrições"""
        clean_descriptions = [self.clean_description(d) for d in descriptions]
        self.vectorizer.fit(clean_descriptions)
```

### 2. Model Trainer

```python
# app/ml/model_trainer.py
from typing import List, Tuple
import numpy as np
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import pandas as pd
from app.ml.feature_extractor import FeatureExtractor

class ModelTrainer:
    """Treina modelo de classificação de transações"""

    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.model = None
        self.label_encoder = {}
        self.reverse_label_encoder = {}

    def prepare_dataset_from_excel(self, excel_path: str) -> Tuple[np.ndarray, np.ndarray]:
        """
        Preparar dataset a partir da planilha Excel existente

        Returns:
            X (features), y (labels)
        """
        # Ler planilha
        df = pd.read_excel(excel_path, sheet_name='FLUXODECAIXA', header=5)

        # Filtrar apenas transações categorizadas
        df = df.dropna(subset=['Categoria', 'Descrição', 'Valor'])

        # Pegar colunas relevantes
        descriptions = df['Descrição'].tolist()
        categories = df['Categoria'].tolist()
        values = df['Valor'].tolist()
        dates = df['Data do Evento'].tolist()

        print(f"Dataset: {len(descriptions)} transações encontradas")

        # Criar mapeamento de categorias para IDs numéricos
        unique_categories = list(set(categories))
        self.label_encoder = {cat: idx for idx, cat in enumerate(unique_categories)}
        self.reverse_label_encoder = {idx: cat for cat, idx in self.label_encoder.items()}

        print(f"Categorias únicas: {len(unique_categories)}")

        # Treinar vetorizador com todas as descrições
        self.feature_extractor.fit_vectorizer(descriptions)

        # Extrair features
        X = []
        y = []

        for desc, cat, val, date in zip(descriptions, categories, values, dates):
            try:
                features = self.feature_extractor.extract_features(desc, val, date)
                label = self.label_encoder[cat]

                X.append(features)
                y.append(label)
            except Exception as e:
                print(f"Erro ao processar transação: {e}")
                continue

        return np.array(X), np.array(y)

    def train(self, X: np.ndarray, y: np.ndarray, model_type: str = 'random_forest'):
        """
        Treinar modelo

        Args:
            X: Features
            y: Labels
            model_type: 'naive_bayes' ou 'random_forest'
        """
        # Split train/test
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        print(f"\nTreinamento: {len(X_train)} samples")
        print(f"Teste: {len(X_test)} samples")

        # Escolher modelo
        if model_type == 'naive_bayes':
            # Naive Bayes requer features não-negativas
            # Ajustar features (TF-IDF já são positivas, mas numeric podem ser negativas)
            X_train = np.abs(X_train)
            X_test = np.abs(X_test)
            self.model = MultinomialNB(alpha=0.1)
        else:
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=20,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )

        # Treinar
        print(f"\nTreinando {model_type}...")
        self.model.fit(X_train, y_train)

        # Avaliar
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)

        print(f"\nAccuracy - Train: {train_score:.4f}")
        print(f"Accuracy - Test: {test_score:.4f}")

        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train, y_train, cv=5)
        print(f"Cross-validation (5-fold): {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

        # Predições no conjunto de teste
        y_pred = self.model.predict(X_test)

        # Relatório de classificação
        print("\n" + "="*80)
        print("RELATÓRIO DE CLASSIFICAÇÃO")
        print("="*80)

        target_names = [self.reverse_label_encoder[i] for i in sorted(self.reverse_label_encoder.keys())]
        print(classification_report(y_test, y_pred, target_names=target_names, zero_division=0))

        return {
            'train_score': train_score,
            'test_score': test_score,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std()
        }

    def save_model(self, model_path: str = 'app/ml/models/category_classifier.pkl'):
        """Salvar modelo treinado"""
        if not self.model:
            raise ValueError("Modelo não foi treinado ainda")

        model_data = {
            'model': self.model,
            'feature_extractor': self.feature_extractor,
            'label_encoder': self.label_encoder,
            'reverse_label_encoder': self.reverse_label_encoder
        }

        joblib.dump(model_data, model_path)
        print(f"\nModelo salvo em: {model_path}")

    @classmethod
    def load_model(cls, model_path: str = 'app/ml/models/category_classifier.pkl'):
        """Carregar modelo treinado"""
        model_data = joblib.load(model_path)

        trainer = cls()
        trainer.model = model_data['model']
        trainer.feature_extractor = model_data['feature_extractor']
        trainer.label_encoder = model_data['label_encoder']
        trainer.reverse_label_encoder = model_data['reverse_label_encoder']

        return trainer
```

### 3. Predictor

```python
# app/ml/predictor.py
import numpy as np
from typing import Dict, List
from app.ml.model_trainer import ModelTrainer

class CategoryPredictor:
    """Realiza predições de categoria para transações"""

    def __init__(self, model_path: str = 'app/ml/models/category_classifier.pkl'):
        self.trainer = ModelTrainer.load_model(model_path)

    def predict(self, description: str, amount: float, date: str = None) -> Dict:
        """
        Prever categoria de uma transação

        Returns:
            {
                'category': 'Alimentação',
                'category_id': 5,  # Será mapeado para ID do banco
                'confidence': 0.85,
                'top_3': [
                    {'category': 'Alimentação', 'confidence': 0.85},
                    {'category': 'Supermercado', 'confidence': 0.10},
                    {'category': 'Restaurante', 'confidence': 0.03}
                ]
            }
        """
        # Extrair features
        features = self.trainer.feature_extractor.extract_features(
            description, amount, date
        )
        features = features.reshape(1, -1)

        # Predição com probabilidades
        probabilities = self.trainer.model.predict_proba(features)[0]
        predicted_class = np.argmax(probabilities)
        confidence = probabilities[predicted_class]

        # Top 3 categorias
        top_3_indices = np.argsort(probabilities)[-3:][::-1]
        top_3 = [
            {
                'category': self.trainer.reverse_label_encoder[idx],
                'confidence': float(probabilities[idx])
            }
            for idx in top_3_indices
        ]

        return {
            'category': self.trainer.reverse_label_encoder[predicted_class],
            'category_id': int(predicted_class),  # Será mapeado para ID real
            'confidence': float(confidence),
            'top_3': top_3
        }

    def predict_batch(self, transactions: List[Dict]) -> List[Dict]:
        """Prever categorias para múltiplas transações"""
        results = []

        for txn in transactions:
            prediction = self.predict(
                description=txn.get('description', ''),
                amount=txn.get('amount', 0),
                date=txn.get('date')
            )
            results.append(prediction)

        return results
```

---

## DATASET DE TREINO

### Script de Extração da Planilha

```python
# scripts/extract_training_data.py
"""
Extrair dados da planilha Excel para treinar o modelo de ML

Uso:
    python scripts/extract_training_data.py
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app.ml.model_trainer import ModelTrainer

def main():
    print("="*80)
    print("EXTRAÇÃO DE DADOS PARA TREINAMENTO")
    print("="*80)

    # Path da planilha
    excel_path = 'Planilha/Meu_Planner_Financeiro_MacOs_V3-2.xlsm'

    # Criar trainer
    trainer = ModelTrainer()

    # Preparar dataset
    print("\nExtraindo dados da planilha...")
    X, y = trainer.prepare_dataset_from_excel(excel_path)

    print(f"\nDataset preparado:")
    print(f"  - Features shape: {X.shape}")
    print(f"  - Labels shape: {y.shape}")
    print(f"  - Categorias únicas: {len(set(y))}")

    # Treinar modelo
    print("\n" + "="*80)
    print("TREINAMENTO DO MODELO")
    print("="*80)

    metrics = trainer.train(X, y, model_type='random_forest')

    # Salvar modelo
    print("\n" + "="*80)
    trainer.save_model()

    print("\n✅ Processo concluído!")
    print(f"\nMétricas finais:")
    print(f"  - Train accuracy: {metrics['train_score']:.4f}")
    print(f"  - Test accuracy: {metrics['test_score']:.4f}")
    print(f"  - CV mean: {metrics['cv_mean']:.4f}")

    if metrics['test_score'] > 0.8:
        print("\n🎉 Modelo com boa performance! (> 80%)")
    elif metrics['test_score'] > 0.6:
        print("\n⚠️  Modelo com performance razoável (60-80%)")
    else:
        print("\n❌ Modelo com baixa performance (< 60%). Considere:")
        print("   - Aumentar dataset de treino")
        print("   - Melhorar feature engineering")
        print("   - Ajustar hiperparâmetros")

if __name__ == '__main__':
    main()
```

---

## API ENDPOINTS

### Endpoints de Importação

```python
# app/api/imports.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
import os
from app.services.import_service import ImportService
from app.schemas.import_schema import ImportBatchSchema
from app.utils.responses import success_response, error_response

imports_bp = Blueprint('imports', __name__, url_prefix='/api/v1/imports')
import_service = ImportService()
batch_schema = ImportBatchSchema()

ALLOWED_EXTENSIONS = {'ofx'}
UPLOAD_FOLDER = '/tmp/uploads'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@imports_bp.route('/ofx', methods=['POST'])
@jwt_required()
def upload_ofx():
    """
    Upload e importação de arquivo OFX
    ---
    POST /api/v1/imports/ofx
    Content-Type: multipart/form-data

    Form Data:
        file: arquivo OFX

    Response:
        {
            "success": true,
            "data": {
                "batch_id": 123,
                "total_transactions": 45,
                "duplicates_skipped": 5,
                "status": "reviewing"
            }
        }
    """
    user_id = get_jwt_identity()

    # Verificar se arquivo foi enviado
    if 'file' not in request.files:
        return error_response('NO_FILE', 'Nenhum arquivo enviado', status_code=400)

    file = request.files['file']

    if file.filename == '':
        return error_response('EMPTY_FILENAME', 'Nome de arquivo vazio', status_code=400)

    if not allowed_file(file.filename):
        return error_response('INVALID_FILE_TYPE', 'Apenas arquivos OFX são permitidos', status_code=400)

    try:
        # Salvar arquivo temporariamente
        filename = secure_filename(file.filename)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, f"{user_id}_{filename}")
        file.save(file_path)

        # Importar OFX
        batch = import_service.import_ofx(user_id, file_path, filename)

        # Remover arquivo temporário
        os.remove(file_path)

        # Retornar sucesso
        return success_response(
            data={
                'batch_id': batch.id,
                'total_transactions': batch.total_transactions,
                'duplicates_skipped': batch.metadata.get('duplicates_skipped', 0),
                'status': batch.status,
                'institution': batch.institution.name,
                'period': {
                    'start': batch.metadata.get('start_date'),
                    'end': batch.metadata.get('end_date')
                }
            },
            message="Arquivo OFX importado com sucesso",
            status_code=201
        )

    except ValueError as e:
        return error_response('IMPORT_ERROR', str(e), status_code=400)
    except Exception as e:
        # Log error
        return error_response('INTERNAL_ERROR', 'Erro ao importar arquivo', status_code=500)

@imports_bp.route('/batches/<int:batch_id>/transactions', methods=['GET'])
@jwt_required()
def get_batch_transactions(batch_id):
    """
    Listar transações pendentes de um batch
    ---
    GET /api/v1/imports/batches/123/transactions

    Response:
        {
            "success": true,
            "data": [
                {
                    "id": 1,
                    "description": "SUPERMERCADO CARREFOUR",
                    "value": -250.50,
                    "date": "2024-11-15",
                    "suggested_category": {
                        "id": 5,
                        "name": "Alimentação"
                    },
                    "confidence": 0.92,
                    "status": "pending"
                },
                ...
            ]
        }
    """
    user_id = get_jwt_identity()

    from app.models.pending_transaction import PendingTransaction
    from app.models.import_batch import ImportBatch

    # Verificar se batch pertence ao usuário
    batch = ImportBatch.query.filter_by(id=batch_id, user_id=user_id).first()
    if not batch:
        return error_response('NOT_FOUND', 'Batch não encontrado', status_code=404)

    # Buscar transações
    transactions = PendingTransaction.query.filter_by(import_batch_id=batch_id).all()

    # Serializar
    result = []
    for txn in transactions:
        result.append({
            'id': txn.id,
            'description': txn.description,
            'value': float(txn.value),
            'date': txn.event_date.isoformat(),
            'suggested_category': {
                'id': txn.suggested_category_id,
                'name': txn.suggested_category.name if txn.suggested_category else None
            } if txn.suggested_category_id else None,
            'confidence': float(txn.confidence_score) if txn.confidence_score else None,
            'final_category': {
                'id': txn.final_category_id,
                'name': txn.final_category.name if txn.final_category else None
            } if txn.final_category_id else None,
            'status': txn.status
        })

    return success_response(data=result)

@imports_bp.route('/transactions/<int:txn_id>/accept', methods=['POST'])
@jwt_required()
def accept_transaction(txn_id):
    """
    Aceitar sugestão de categoria do ML
    ---
    POST /api/v1/imports/transactions/123/accept
    """
    user_id = get_jwt_identity()

    from app.models.pending_transaction import PendingTransaction
    from app.extensions import db

    txn = PendingTransaction.query.filter_by(id=txn_id, user_id=user_id).first()
    if not txn:
        return error_response('NOT_FOUND', 'Transação não encontrada', status_code=404)

    txn.final_category_id = txn.suggested_category_id
    txn.status = 'accepted'
    txn.reviewed_at = datetime.utcnow()
    db.session.commit()

    return success_response(message="Classificação aceita")

@imports_bp.route('/transactions/<int:txn_id>/correct', methods=['PUT'])
@jwt_required()
def correct_transaction(txn_id):
    """
    Corrigir categoria sugerida pelo ML
    ---
    PUT /api/v1/imports/transactions/123/correct
    Body:
        {
            "category_id": 10,
            "institution_id": 2,
            "credit_card_id": 3
        }
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    from app.models.pending_transaction import PendingTransaction
    from app.extensions import db

    txn = PendingTransaction.query.filter_by(id=txn_id, user_id=user_id).first()
    if not txn:
        return error_response('NOT_FOUND', 'Transação não encontrada', status_code=404)

    txn.final_category_id = data.get('category_id')
    txn.final_institution_id = data.get('institution_id')
    txn.final_credit_card_id = data.get('credit_card_id')
    txn.status = 'corrected'
    txn.reviewed_at = datetime.utcnow()
    db.session.commit()

    return success_response(message="Classificação corrigida")

@imports_bp.route('/batches/<int:batch_id>/confirm', methods=['POST'])
@jwt_required()
def confirm_batch(batch_id):
    """
    Confirmar batch e criar transações definitivas
    ---
    POST /api/v1/imports/batches/123/confirm

    Response:
        {
            "success": true,
            "data": {
                "transactions_created": 40,
                "batch_status": "completed"
            }
        }
    """
    user_id = get_jwt_identity()

    try:
        count = import_service.confirm_batch(batch_id, user_id)

        return success_response(
            data={
                'transactions_created': count,
                'batch_status': 'completed'
            },
            message=f"{count} transações importadas com sucesso"
        )

    except ValueError as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)
```

---

## INTERFACE DO USUÁRIO

### Tela de Importação OFX

```jsx
// frontend/src/pages/Imports/ImportOFX.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { importApi } from '../../api/importApi';
import { toast } from 'react-toastify';

const ImportOFX = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.toLowerCase().endsWith('.ofx')) {
      setFile(selectedFile);
    } else {
      toast.error('Apenas arquivos OFX são permitidos');
    }
  };

  const handleUpload = async () => {
    if (!file) {
      toast.error('Selecione um arquivo OFX');
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await importApi.uploadOFX(formData);

      toast.success(response.message);

      // Redirecionar para revisão das transações
      navigate(`/imports/review/${response.data.batch_id}`);
    } catch (error) {
      toast.error(error.message || 'Erro ao importar arquivo');
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Importar Extrato OFX</h1>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Arquivo OFX
          </label>
          <input
            type="file"
            accept=".ofx"
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-500
              file:mr-4 file:py-2 file:px-4
              file:rounded-full file:border-0
              file:text-sm file:font-semibold
              file:bg-blue-50 file:text-blue-700
              hover:file:bg-blue-100"
          />
          {file && (
            <p className="mt-2 text-sm text-gray-500">
              Arquivo selecionado: {file.name}
            </p>
          )}
        </div>

        <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800">
                Como obter arquivo OFX?
              </h3>
              <div className="mt-2 text-sm text-blue-700">
                <ol className="list-decimal list-inside space-y-1">
                  <li>Acesse o internet banking do seu banco</li>
                  <li>Vá em "Extratos" ou "Exportar dados"</li>
                  <li>Selecione o período desejado</li>
                  <li>Escolha o formato OFX/Money</li>
                  <li>Faça o download do arquivo</li>
                </ol>
              </div>
            </div>
          </div>
        </div>

        <button
          onClick={handleUpload}
          disabled={!file || uploading}
          className={`w-full py-3 px-4 rounded-lg font-semibold text-white
            ${!file || uploading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-600 hover:bg-blue-700'
            }
          `}
        >
          {uploading ? 'Importando...' : 'Importar Transações'}
        </button>
      </div>
    </div>
  );
};

export default ImportOFX;
```

### Tela de Revisão de Transações

```jsx
// frontend/src/pages/Imports/ReviewTransactions.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { importApi } from '../../api/importApi';
import { toast } from 'react-toastify';

const ReviewTransactions = () => {
  const { batchId } = useParams();
  const navigate = useNavigate();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    loadTransactions();
    loadCategories();
  }, [batchId]);

  const loadTransactions = async () => {
    try {
      const data = await importApi.getBatchTransactions(batchId);
      setTransactions(data);
    } catch (error) {
      toast.error('Erro ao carregar transações');
    } finally {
      setLoading(false);
    }
  };

  const loadCategories = async () => {
    // Carregar categorias da API
    // const data = await categoryApi.list();
    // setCategories(data);
  };

  const handleAccept = async (txnId) => {
    try {
      await importApi.acceptTransaction(txnId);
      toast.success('Classificação aceita');
      loadTransactions();
    } catch (error) {
      toast.error('Erro ao aceitar classificação');
    }
  };

  const handleCorrect = async (txnId, categoryId) => {
    try {
      await importApi.correctTransaction(txnId, { category_id: categoryId });
      toast.success('Classificação corrigida');
      loadTransactions();
    } catch (error) {
      toast.error('Erro ao corrigir classificação');
    }
  };

  const handleConfirmBatch = async () => {
    if (!window.confirm('Confirmar importação de todas as transações revisadas?')) {
      return;
    }

    try {
      const result = await importApi.confirmBatch(batchId);
      toast.success(result.message);
      navigate('/transactions');
    } catch (error) {
      toast.error('Erro ao confirmar importação');
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceLabel = (confidence) => {
    if (confidence >= 0.8) return 'Alta';
    if (confidence >= 0.6) return 'Média';
    return 'Baixa';
  };

  if (loading) {
    return <div>Carregando...</div>;
  }

  const pendingCount = transactions.filter(t => t.status === 'pending').length;
  const reviewedCount = transactions.length - pendingCount;

  return (
    <div className="container mx-auto p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Revisar Transações</h1>
        <div className="text-sm text-gray-600">
          {reviewedCount} de {transactions.length} revisadas
        </div>
      </div>

      {/* Progress Bar */}
      <div className="bg-gray-200 rounded-full h-2 mb-6">
        <div
          className="bg-blue-600 h-2 rounded-full transition-all"
          style={{ width: `${(reviewedCount / transactions.length) * 100}%` }}
        />
      </div>

      {/* Transaction List */}
      <div className="space-y-4">
        {transactions.map(txn => (
          <div
            key={txn.id}
            className={`bg-white rounded-lg shadow p-4 ${
              txn.status !== 'pending' ? 'opacity-60' : ''
            }`}
          >
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <h3 className="font-semibold text-lg">{txn.description}</h3>
                <p className="text-sm text-gray-500">{txn.date}</p>
              </div>
              <div className={`text-xl font-bold ${
                txn.value > 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                R$ {Math.abs(txn.value).toFixed(2)}
              </div>
            </div>

            {txn.suggested_category && (
              <div className="mt-4 p-3 bg-gray-50 rounded">
                <div className="flex justify-between items-center">
                  <div>
                    <span className="text-sm text-gray-600">Sugestão do ML:</span>
                    <span className="ml-2 font-semibold">
                      {txn.suggested_category.name}
                    </span>
                    {txn.confidence && (
                      <span className={`ml-2 text-sm ${getConfidenceColor(txn.confidence)}`}>
                        ({getConfidenceLabel(txn.confidence)}: {(txn.confidence * 100).toFixed(0)}%)
                      </span>
                    )}
                  </div>

                  {txn.status === 'pending' && (
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleAccept(txn.id)}
                        className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                      >
                        ✓ Aceitar
                      </button>
                      <button
                        className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700"
                      >
                        ✎ Corrigir
                      </button>
                    </div>
                  )}

                  {txn.status === 'accepted' && (
                    <span className="text-green-600 font-semibold">✓ Aceita</span>
                  )}

                  {txn.status === 'corrected' && (
                    <span className="text-blue-600 font-semibold">
                      ✎ Corrigida → {txn.final_category.name}
                    </span>
                  )}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Confirm Button */}
      {reviewedCount === transactions.length && (
        <div className="mt-8 flex justify-end">
          <button
            onClick={handleConfirmBatch}
            className="px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700"
          >
            Confirmar Importação ({transactions.length} transações)
          </button>
        </div>
      )}
    </div>
  );
};

export default ReviewTransactions;
```

---

## IMPLEMENTAÇÃO PASSO A PASSO

### Fase 1: Setup Básico (1-2 dias)

#### 1.1 Dependências Python

```bash
pip install ofxparse==0.21
pip install scikit-learn==1.3.2
pip install joblib==1.3.2
pip install openpyxl==3.1.2  # Para ler Excel
```

#### 1.2 Criar estrutura de pastas

```bash
mkdir -p backend/app/ml/models
mkdir -p backend/app/importers
mkdir -p backend/scripts
```

#### 1.3 Criar tabelas no banco

```bash
flask db migrate -m "Add import_batches and pending_transactions tables"
flask db upgrade
```

### Fase 2: Extração e Treinamento do Modelo (2-3 dias)

```bash
# 1. Extrair dados da planilha e treinar modelo
python scripts/extract_training_data.py

# Output esperado:
# Dataset: 1884 transações encontradas
# Categorias únicas: 18
# Accuracy - Test: 0.8542
# Modelo salvo em: app/ml/models/category_classifier.pkl
```

### Fase 3: Importador OFX (2-3 dias)

1. Implementar `OFXImporter`
2. Implementar `ImportService`
3. Criar endpoints de importação
4. Testes com arquivos OFX reais

### Fase 4: Interface de Revisão (2-3 dias)

1. Tela de upload OFX
2. Tela de revisão com sugestões do ML
3. Aceitar/Corrigir classificações
4. Confirmar batch

### Fase 5: Melhoria Contínua (ongoing)

1. Retreinamento automático com novas transações
2. Análise de performance do modelo
3. Fine-tuning de hiperparâmetros
4. Feedback loop: transações corrigidas melhoram o modelo

---

## MÉTRICAS DE SUCESSO

### Performance do ML

| Métrica | Target | Atual |
|---------|--------|-------|
| Accuracy geral | > 80% | A medir |
| Precision (top categoria) | > 85% | A medir |
| Recall (principais categorias) | > 75% | A medir |
| Tempo de predição | < 100ms | A medir |

### Usabilidade

| Métrica | Target |
|---------|--------|
| Taxa de aceitação das sugestões | > 70% |
| Tempo médio de revisão por transação | < 5s |
| Transações importadas por minuto | > 50 |

---

## PRÓXIMOS PASSOS

**Prioridade MÁXIMA - Fazer agora:**

1. ✅ Criar tabelas `import_batches` e `pending_transactions`
2. ✅ Instalar dependências (`ofxparse`, `scikit-learn`)
3. ✅ Executar script de extração e treinamento
4. ✅ Testar modelo com transações de exemplo
5. ✅ Implementar endpoint de upload OFX
6. ✅ Criar interface de revisão

**Prioridade Média - Logo depois:**

7. Retreinamento automático
8. Análise de confidence scores
9. Sugestão de múltiplas categorias (top-3)
10. Histórico de importações

**Prioridade Baixa - Futuro:**

11. Integração com Open Banking (API de bancos)
12. Importação automática agendada
13. Notificações de novas transações

---

**Documento criado em:** 18/12/2025
**Versão:** 1.0
**Status:** Pronto para implementação
