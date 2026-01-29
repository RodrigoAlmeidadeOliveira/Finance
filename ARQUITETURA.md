# ARQUITETURA DO SISTEMA - PLANNER FINANCEIRO WEB

**Projeto:** Sistema de Gestão Financeira Pessoal Web
**Versão:** 1.0
**Data:** 18 de Dezembro de 2025
**Stack:** Python 3.11+ | Flask | React | PostgreSQL

---

## ÍNDICE

1. [Visão Geral da Arquitetura](#visão-geral-da-arquitetura)
2. [Princípios Arquiteturais](#princípios-arquiteturais)
3. [Stack Tecnológica](#stack-tecnológica)
4. [Estrutura do Projeto](#estrutura-do-projeto)
5. [Camadas da Aplicação](#camadas-da-aplicação)
6. [Modelo de Dados](#modelo-de-dados)
7. [API RESTful](#api-restful)
8. [Autenticação e Segurança](#autenticação-e-segurança)
9. [Padrões de Código](#padrões-de-código)
10. [Deploy e Infraestrutura](#deploy-e-infraestrutura)

---

## VISÃO GERAL DA ARQUITETURA

### Diagrama de Alto Nível

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENTE                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │             React SPA (Single Page Application)              │  │
│  │  - React Router (navegação)                                  │  │
│  │  - Redux/Context API (estado global)                         │  │
│  │  - Axios (HTTP client)                                       │  │
│  │  - Chart.js (gráficos)                                       │  │
│  │  - Tailwind CSS (estilização)                                │  │
│  └────────────────────────┬─────────────────────────────────────┘  │
└───────────────────────────┼─────────────────────────────────────────┘
                            │ HTTPS/HTTP
                            │ JSON
                            │
┌───────────────────────────▼─────────────────────────────────────────┐
│                      SERVIDOR BACKEND                               │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                      Flask Application                       │  │
│  │                                                              │  │
│  │  ┌────────────────┐  ┌─────────────────┐  ┌──────────────┐ │  │
│  │  │  API Layer     │  │  Service Layer  │  │ Data Layer   │ │  │
│  │  │  (Routes)      │─▶│  (Business      │─▶│ (Models,     │ │  │
│  │  │  - Blueprints  │  │   Logic)        │  │  Repositories│ │  │
│  │  │  - Validation  │  │  - Domain       │  │  SQLAlchemy) │ │  │
│  │  │  - Serializers │  │    Services     │  │              │ │  │
│  │  └────────────────┘  └─────────────────┘  └──────┬───────┘ │  │
│  │                                                    │         │  │
│  │  ┌────────────────────────────────────────────────┘         │  │
│  │  │                                                          │  │
│  │  │  Cross-Cutting Concerns:                                │  │
│  │  │  - Authentication (JWT)                                 │  │
│  │  │  - Authorization (RBAC)                                 │  │
│  │  │  - Logging (estruturado)                                │  │
│  │  │  - Error Handling                                       │  │
│  │  │  - Validation (Marshmallow)                             │  │
│  │  └─────────────────────────────────────────────────────────┘  │
│  └──────────────────────────┬───────────────────────────────────┘  │
└─────────────────────────────┼───────────────────────────────────────┘
                              │ SQLAlchemy ORM
                              │
┌─────────────────────────────▼───────────────────────────────────────┐
│                      BANCO DE DADOS                                 │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    PostgreSQL 14+                            │  │
│  │  - users                - transactions                       │  │
│  │  - categories           - financial_plans                    │  │
│  │  - institutions         - investments                        │  │
│  │  - credit_cards         - revenue_planning                   │  │
│  │  - audit_logs           - user_sessions                      │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

### Padrão de Arquitetura

**Arquitetura em Camadas (Layered Architecture)**
- Separação clara de responsabilidades
- Cada camada se comunica apenas com a camada imediatamente abaixo
- Facilita testes, manutenção e escalabilidade

---

## PRINCÍPIOS ARQUITETURAIS

### 1. Separação de Responsabilidades (SoC)
- **API Layer**: Gerencia requisições HTTP, validação de entrada, serialização
- **Service Layer**: Contém lógica de negócio, orquestração
- **Data Layer**: Acesso ao banco de dados, persistência

### 2. DRY (Don't Repeat Yourself)
- Reutilização de código via funções helpers e utilitários
- Schemas reutilizáveis (Marshmallow)
- Componentes React modulares

### 3. SOLID
- **S**ingle Responsibility: Uma classe/função, uma responsabilidade
- **O**pen/Closed: Aberto para extensão, fechado para modificação
- **L**iskov Substitution: Subtipos devem ser substituíveis
- **I**nterface Segregation: Interfaces específicas, não genéricas
- **D**ependency Inversion: Dependa de abstrações, não de implementações

### 4. RESTful API Design
- Recursos identificados por URIs
- Verbos HTTP semânticos (GET, POST, PUT, PATCH, DELETE)
- Stateless (sem estado)
- HATEOAS (Hypermedia as the Engine of Application State) - opcional

### 5. Segurança por Design
- Autenticação JWT
- Senhas hasheadas (bcrypt)
- Validação rigorosa de inputs
- SQL Injection prevention (ORM)
- CORS configurado adequadamente
- Rate limiting

### 6. Testabilidade
- Injeção de dependências
- Mocks e fixtures
- Testes unitários, integração e E2E
- Cobertura mínima: 80%

---

## STACK TECNOLÓGICA

### Backend

#### Core
```python
# Python 3.11+
flask==3.0.0              # Framework web
flask-restful==0.3.10     # Extensão REST
flask-sqlalchemy==3.1.1   # ORM
flask-migrate==4.0.5      # Migrations (Alembic)
flask-jwt-extended==4.6.0 # Autenticação JWT
flask-cors==4.0.0         # CORS
flask-limiter==3.5.0      # Rate limiting
```

#### Validação e Serialização
```python
marshmallow==3.20.1       # Serialização/Validação
marshmallow-sqlalchemy==0.29.0
```

#### Banco de Dados
```python
psycopg2-binary==2.9.9    # Driver PostgreSQL
alembic==1.13.1           # Migrations standalone
```

#### Utilitários
```python
python-dotenv==1.0.0      # Variáveis de ambiente
bcrypt==4.1.2             # Hash de senhas
pydantic==2.5.0           # Validação de dados
```

#### Análise e Cálculos
```python
pandas==2.1.4             # Análise de dados
numpy==1.26.2             # Cálculos numéricos
```

#### Testes
```python
pytest==7.4.3             # Framework de testes
pytest-cov==4.1.0         # Cobertura
pytest-flask==1.3.0       # Testes Flask
factory-boy==3.3.0        # Factories para testes
faker==22.0.0             # Dados fake
```

#### Qualidade de Código
```python
black==23.12.1            # Formatação
ruff==0.1.9               # Linting
mypy==1.7.1               # Type checking
```

### Frontend

#### Core
```json
{
  "react": "^18.2.0",
  "react-dom": "^18.2.0",
  "react-router-dom": "^6.21.0"
}
```

#### Estado Global
```json
{
  "redux": "^5.0.0",
  "react-redux": "^9.0.4",
  "@reduxjs/toolkit": "^2.0.1"
}
```

#### HTTP & API
```json
{
  "axios": "^1.6.2",
  "react-query": "^3.39.3"
}
```

#### UI & Estilização
```json
{
  "tailwindcss": "^3.4.0",
  "daisyui": "^4.4.20",
  "react-icons": "^4.12.0"
}
```

#### Gráficos
```json
{
  "chart.js": "^4.4.1",
  "react-chartjs-2": "^5.2.0",
  "recharts": "^2.10.3"
}
```

#### Formulários
```json
{
  "react-hook-form": "^7.49.2",
  "yup": "^1.3.3"
}
```

#### Utilitários
```json
{
  "date-fns": "^3.0.6",
  "numeral": "^2.0.6",
  "react-toastify": "^9.1.3"
}
```

### Banco de Dados

```
PostgreSQL 14+
- Versão estável e madura
- Suporte a JSON (para campos flexíveis)
- Performance excelente
- Transações ACID
```

### Infraestrutura

```
Docker 24+
Docker Compose 2+
Nginx (reverse proxy)
Let's Encrypt (SSL - opcional)
```

---

## ESTRUTURA DO PROJETO

```
planner-financeiro/
│
├── backend/                          # API Flask
│   ├── app/                          # Aplicação principal
│   │   ├── __init__.py              # Factory da aplicação
│   │   │
│   │   ├── api/                      # Camada de API (Routes)
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # Endpoints de autenticação
│   │   │   ├── transactions.py      # Endpoints de transações
│   │   │   ├── categories.py        # Endpoints de categorias
│   │   │   ├── institutions.py      # Endpoints de instituições
│   │   │   ├── investments.py       # Endpoints de investimentos
│   │   │   ├── plans.py             # Endpoints de planos
│   │   │   ├── dashboards.py        # Endpoints de dashboards
│   │   │   └── reports.py           # Endpoints de relatórios
│   │   │
│   │   ├── services/                 # Camada de Serviço (Business Logic)
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py      # Lógica de autenticação
│   │   │   ├── transaction_service.py
│   │   │   ├── investment_service.py
│   │   │   ├── plan_service.py
│   │   │   ├── calculator_service.py # Cálculos financeiros
│   │   │   └── report_service.py    # Geração de relatórios
│   │   │
│   │   ├── models/                   # Camada de Dados (SQLAlchemy Models)
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── transaction.py
│   │   │   ├── category.py
│   │   │   ├── institution.py
│   │   │   ├── credit_card.py
│   │   │   ├── investment.py
│   │   │   ├── financial_plan.py
│   │   │   ├── revenue_planning.py
│   │   │   └── audit_log.py
│   │   │
│   │   ├── repositories/             # Repositórios (Data Access)
│   │   │   ├── __init__.py
│   │   │   ├── base_repository.py   # Repositório base genérico
│   │   │   ├── user_repository.py
│   │   │   ├── transaction_repository.py
│   │   │   └── investment_repository.py
│   │   │
│   │   ├── schemas/                  # Marshmallow Schemas (Serialização)
│   │   │   ├── __init__.py
│   │   │   ├── user_schema.py
│   │   │   ├── transaction_schema.py
│   │   │   ├── investment_schema.py
│   │   │   └── plan_schema.py
│   │   │
│   │   ├── utils/                    # Utilitários e Helpers
│   │   │   ├── __init__.py
│   │   │   ├── validators.py        # Validadores customizados
│   │   │   ├── decorators.py        # Decoradores (auth, logging)
│   │   │   ├── formatters.py        # Formatação de dados
│   │   │   ├── calculators.py       # Cálculos financeiros
│   │   │   └── exceptions.py        # Exceções customizadas
│   │   │
│   │   ├── middleware/               # Middlewares
│   │   │   ├── __init__.py
│   │   │   ├── auth_middleware.py
│   │   │   ├── error_handler.py
│   │   │   └── logging_middleware.py
│   │   │
│   │   └── config.py                 # Configurações da aplicação
│   │
│   ├── migrations/                   # Alembic migrations
│   │   ├── versions/
│   │   └── env.py
│   │
│   ├── tests/                        # Testes
│   │   ├── __init__.py
│   │   ├── conftest.py              # Fixtures pytest
│   │   ├── factories/               # Factories para testes
│   │   │   ├── user_factory.py
│   │   │   └── transaction_factory.py
│   │   ├── unit/                    # Testes unitários
│   │   │   ├── test_services/
│   │   │   └── test_utils/
│   │   └── integration/             # Testes de integração
│   │       ├── test_api/
│   │       └── test_repositories/
│   │
│   ├── scripts/                      # Scripts auxiliares
│   │   ├── seed_db.py               # Popular banco com dados de teste
│   │   ├── migrate_from_excel.py    # Migração da planilha
│   │   └── backup.py                # Script de backup
│   │
│   ├── .env.example                  # Exemplo de variáveis de ambiente
│   ├── .env                          # Variáveis de ambiente (não commitar!)
│   ├── requirements.txt              # Dependências Python
│   ├── requirements-dev.txt          # Dependências de desenvolvimento
│   ├── pytest.ini                    # Configuração pytest
│   ├── pyproject.toml                # Configuração black, ruff, mypy
│   ├── wsgi.py                       # Entry point para produção
│   └── run.py                        # Entry point para desenvolvimento
│
├── frontend/                         # React SPA
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   │
│   ├── src/
│   │   ├── api/                      # Chamadas à API
│   │   │   ├── axiosConfig.js       # Configuração Axios
│   │   │   ├── authApi.js
│   │   │   ├── transactionApi.js
│   │   │   └── investmentApi.js
│   │   │
│   │   ├── components/               # Componentes reutilizáveis
│   │   │   ├── common/              # Componentes comuns
│   │   │   │   ├── Button.jsx
│   │   │   │   ├── Input.jsx
│   │   │   │   ├── Modal.jsx
│   │   │   │   └── Table.jsx
│   │   │   ├── layout/              # Layout
│   │   │   │   ├── Navbar.jsx
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   └── Footer.jsx
│   │   │   └── charts/              # Componentes de gráficos
│   │   │       ├── LineChart.jsx
│   │   │       ├── PieChart.jsx
│   │   │       └── BarChart.jsx
│   │   │
│   │   ├── pages/                    # Páginas (Routes)
│   │   │   ├── Home.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Transactions/
│   │   │   │   ├── TransactionList.jsx
│   │   │   │   ├── TransactionForm.jsx
│   │   │   │   └── TransactionDetail.jsx
│   │   │   ├── Investments/
│   │   │   ├── Plans/
│   │   │   ├── Reports/
│   │   │   └── Settings/
│   │   │
│   │   ├── store/                    # Redux store
│   │   │   ├── index.js             # Store configuration
│   │   │   ├── slices/              # Redux Toolkit slices
│   │   │   │   ├── authSlice.js
│   │   │   │   ├── transactionSlice.js
│   │   │   │   └── uiSlice.js
│   │   │   └── middleware/
│   │   │
│   │   ├── hooks/                    # Custom React hooks
│   │   │   ├── useAuth.js
│   │   │   ├── useTransactions.js
│   │   │   └── useDebounce.js
│   │   │
│   │   ├── utils/                    # Utilitários
│   │   │   ├── formatters.js        # Formatação de valores
│   │   │   ├── validators.js
│   │   │   └── constants.js
│   │   │
│   │   ├── styles/                   # Estilos globais
│   │   │   └── index.css
│   │   │
│   │   ├── App.jsx                   # Componente raiz
│   │   ├── index.jsx                 # Entry point
│   │   └── routes.jsx                # Configuração de rotas
│   │
│   ├── .env.example
│   ├── .env                          # Variáveis de ambiente
│   ├── package.json
│   ├── tailwind.config.js
│   ├── vite.config.js                # Vite bundler config
│   └── .eslintrc.js
│
├── docker/                           # Configurações Docker
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── nginx.conf
│
├── docker-compose.yml                # Orquestração Docker
├── docker-compose.dev.yml            # Ambiente de desenvolvimento
├── .gitignore
├── README.md
├── CASOS_DE_USO.md                   # Documentação de casos de uso
├── ARQUITETURA.md                    # Este arquivo
└── CLAUDE.md                         # Diretrizes para desenvolvimento
```

---

## CAMADAS DA APLICAÇÃO

### 1. API Layer (Camada de Apresentação)

**Responsabilidades:**
- Receber requisições HTTP
- Validar formato de entrada
- Serializar/Deserializar JSON
- Retornar respostas HTTP apropriadas
- Gerenciar códigos de status

**Exemplo (transactions.py):**
```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.transaction_service import TransactionService
from app.schemas.transaction_schema import TransactionSchema
from app.utils.decorators import validate_json

transactions_bp = Blueprint('transactions', __name__, url_prefix='/api/v1/transactions')
transaction_service = TransactionService()
transaction_schema = TransactionSchema()

@transactions_bp.route('', methods=['POST'])
@jwt_required()
@validate_json(transaction_schema)
def create_transaction():
    """
    Criar nova transação
    ---
    POST /api/v1/transactions
    """
    user_id = get_jwt_identity()
    data = request.get_json()

    transaction = transaction_service.create(user_id, data)

    return jsonify(transaction_schema.dump(transaction)), 201

@transactions_bp.route('', methods=['GET'])
@jwt_required()
def list_transactions():
    """
    Listar transações com filtros
    ---
    GET /api/v1/transactions?start_date=2024-01-01&category_id=5
    """
    user_id = get_jwt_identity()
    filters = {
        'start_date': request.args.get('start_date'),
        'end_date': request.args.get('end_date'),
        'category_id': request.args.get('category_id'),
        'status': request.args.get('status')
    }

    transactions = transaction_service.list_with_filters(user_id, filters)

    return jsonify(transaction_schema.dump(transactions, many=True)), 200
```

### 2. Service Layer (Camada de Negócio)

**Responsabilidades:**
- Implementar regras de negócio
- Orquestrar operações entre múltiplos repositórios
- Validar regras de domínio
- Executar cálculos
- Gerenciar transações de banco de dados

**Exemplo (transaction_service.py):**
```python
from typing import List, Dict, Optional
from datetime import datetime
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.category_repository import CategoryRepository
from app.utils.calculators import CalculatorService
from app.utils.exceptions import ValidationError, NotFoundError
from app.models.transaction import Transaction

class TransactionService:
    def __init__(self):
        self.transaction_repo = TransactionRepository()
        self.category_repo = CategoryRepository()
        self.calculator = CalculatorService()

    def create(self, user_id: int, data: Dict) -> Transaction:
        """Criar nova transação com validações de negócio"""

        # Validação 1: Categoria existe e pertence ao usuário
        category = self.category_repo.find_by_id(data['category_id'])
        if not category or category.user_id != user_id:
            raise NotFoundError("Categoria não encontrada")

        # Validação 2: Valor não pode ser zero
        if data['value'] == 0:
            raise ValidationError("Valor não pode ser zero")

        # Regra de Negócio 1: Se data de efetivação não informada, assume data do evento
        if 'effective_date' not in data:
            data['effective_date'] = data['event_date']

        # Regra de Negócio 2: Receitas = valor positivo, Despesas = valor negativo
        if category.type == 'income' and data['value'] < 0:
            data['value'] = abs(data['value'])
        elif category.type == 'expense' and data['value'] > 0:
            data['value'] = -abs(data['value'])

        # Criar transação
        transaction = self.transaction_repo.create({
            **data,
            'user_id': user_id,
            'created_at': datetime.utcnow()
        })

        # Atualizar estatísticas (async ou celery em produção)
        self._update_statistics(user_id)

        return transaction

    def list_with_filters(self, user_id: int, filters: Dict) -> List[Transaction]:
        """Listar transações aplicando filtros"""
        return self.transaction_repo.find_by_filters(user_id, filters)

    def get_monthly_summary(self, user_id: int, year: int, month: int) -> Dict:
        """Calcular resumo mensal"""
        transactions = self.transaction_repo.find_by_month(user_id, year, month)

        return self.calculator.calculate_monthly_summary(transactions)

    def _update_statistics(self, user_id: int):
        """Atualizar estatísticas do usuário (assíncrono)"""
        # TODO: Implementar com Celery ou similar
        pass
```

### 3. Data Layer (Camada de Dados)

**Responsabilidades:**
- Acesso ao banco de dados
- Queries e operações CRUD
- Mapeamento objeto-relacional (ORM)
- Otimização de queries

**Exemplo (transaction_repository.py):**
```python
from typing import List, Dict, Optional
from sqlalchemy import and_, or_, extract
from app.models.transaction import Transaction
from app.repositories.base_repository import BaseRepository

class TransactionRepository(BaseRepository[Transaction]):
    def __init__(self):
        super().__init__(Transaction)

    def find_by_month(self, user_id: int, year: int, month: int) -> List[Transaction]:
        """Buscar transações de um mês específico"""
        return self.session.query(Transaction).filter(
            and_(
                Transaction.user_id == user_id,
                extract('year', Transaction.event_date) == year,
                extract('month', Transaction.event_date) == month
            )
        ).all()

    def find_by_filters(self, user_id: int, filters: Dict) -> List[Transaction]:
        """Buscar com filtros dinâmicos"""
        query = self.session.query(Transaction).filter(Transaction.user_id == user_id)

        if filters.get('start_date'):
            query = query.filter(Transaction.event_date >= filters['start_date'])

        if filters.get('end_date'):
            query = query.filter(Transaction.event_date <= filters['end_date'])

        if filters.get('category_id'):
            query = query.filter(Transaction.category_id == filters['category_id'])

        if filters.get('status'):
            query = query.filter(Transaction.status == filters['status'])

        return query.order_by(Transaction.event_date.desc()).all()

    def get_balance_by_institution(self, user_id: int) -> List[Dict]:
        """Calcular saldo por instituição financeira"""
        # Query otimizada com agregação no banco
        from sqlalchemy import func

        return self.session.query(
            Transaction.institution_id,
            func.sum(Transaction.value).label('balance')
        ).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.status == 'completed'
            )
        ).group_by(Transaction.institution_id).all()
```

**Exemplo (base_repository.py):**
```python
from typing import TypeVar, Generic, List, Optional
from sqlalchemy.orm import Session
from app.extensions import db

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Repositório base genérico com operações CRUD"""

    def __init__(self, model: T):
        self.model = model
        self.session: Session = db.session

    def create(self, data: dict) -> T:
        """Criar novo registro"""
        instance = self.model(**data)
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance

    def find_by_id(self, id: int) -> Optional[T]:
        """Buscar por ID"""
        return self.session.query(self.model).get(id)

    def find_all(self) -> List[T]:
        """Buscar todos"""
        return self.session.query(self.model).all()

    def update(self, id: int, data: dict) -> T:
        """Atualizar registro"""
        instance = self.find_by_id(id)
        if instance:
            for key, value in data.items():
                setattr(instance, key, value)
            self.session.commit()
            self.session.refresh(instance)
        return instance

    def delete(self, id: int) -> bool:
        """Deletar registro"""
        instance = self.find_by_id(id)
        if instance:
            self.session.delete(instance)
            self.session.commit()
            return True
        return False
```

---

## MODELO DE DADOS

### Diagrama Entidade-Relacionamento (ER)

```
┌─────────────────────┐         ┌─────────────────────┐
│      users          │         │    categories       │
├─────────────────────┤         ├─────────────────────┤
│ id (PK)             │         │ id (PK)             │
│ email               │         │ user_id (FK)        │
│ password_hash       │         │ name                │
│ full_name           │         │ type (income/       │
│ role                │◄───┐    │       expense)      │
│ is_active           │    │    │ parent_id (FK)      │
│ created_at          │    │    │ created_at          │
│ updated_at          │    │    └─────────────────────┘
└─────────────────────┘    │              ▲
                           │              │
                           │              │
                           │    ┌─────────────────────┐
                           │    │   transactions      │
                           │    ├─────────────────────┤
                           │    │ id (PK)             │
                           ├────┤ user_id (FK)        │
                           │    │ category_id (FK)    │
                           │    │ institution_id (FK) │
                           │    │ credit_card_id (FK) │
                           │    │ event_date          │
                           │    │ effective_date      │
                           │    │ description         │
                           │    │ value               │
                           │    │ status              │
                           │    │ created_at          │
                           │    │ updated_at          │
                           │    └─────────────────────┘
                           │              │
                           │              │
                           │    ┌─────────▼───────────┐
                           │    │   institutions      │
                           │    ├─────────────────────┤
                           │    │ id (PK)             │
                           ├────┤ user_id (FK)        │
                           │    │ name                │
                           │    │ type (bank/         │
                           │    │       brokerage)    │
                           │    │ partition           │
                           │    │ initial_balance     │
                           │    │ created_at          │
                           │    └─────────────────────┘
                           │              │
                           │              │
                           │    ┌─────────▼───────────┐
                           │    │   credit_cards      │
                           │    ├─────────────────────┤
                           │    │ id (PK)             │
                           ├────┤ user_id (FK)        │
                           │    │ institution_id (FK) │
                           │    │ name                │
                           │    │ closing_day         │
                           │    │ due_day             │
                           │    │ created_at          │
                           │    └─────────────────────┘
                           │
                           │    ┌─────────────────────┐
                           │    │   investments       │
                           │    ├─────────────────────┤
                           │    │ id (PK)             │
                           ├────┤ user_id (FK)        │
                           │    │ institution_id (FK) │
                           │    │ product_type        │
                           │    │ classification      │
                           │    │ invested_value      │
                           │    │ current_value       │
                           │    │ investment_date     │
                           │    │ maturity_date       │
                           │    │ rate                │
                           │    │ notes               │
                           │    │ is_active           │
                           │    │ created_at          │
                           │    │ updated_at          │
                           │    └─────────────────────┘
                           │
                           │    ┌─────────────────────┐
                           │    │  financial_plans    │
                           │    ├─────────────────────┤
                           │    │ id (PK)             │
                           ├────┤ user_id (FK)        │
                           │    │ institution_id (FK) │
                           │    │ name                │
                           │    │ target_value        │
                           │    │ monthly_contribution│
                           │    │ current_value       │
                           │    │ start_date          │
                           │    │ target_date         │
                           │    │ partition           │
                           │    │ is_completed        │
                           │    │ created_at          │
                           │    │ updated_at          │
                           │    └─────────────────────┘
                           │
                           │    ┌─────────────────────┐
                           │    │  revenue_planning   │
                           │    ├─────────────────────┤
                           │    │ id (PK)             │
                           ├────┤ user_id (FK)        │
                           │    │ month               │
                           │    │ year                │
                           │    │ fixed_income        │
                           │    │ extra_income        │
                           │    │ notes               │
                           │    │ created_at          │
                           │    └─────────────────────┘
                           │
                           │    ┌─────────────────────┐
                           │    │    audit_logs       │
                           │    ├─────────────────────┤
                           │    │ id (PK)             │
                           └────┤ user_id (FK)        │
                                │ action              │
                                │ entity_type         │
                                │ entity_id           │
                                │ changes             │
                                │ ip_address          │
                                │ user_agent          │
                                │ created_at          │
                                └─────────────────────┘
```

### Models SQLAlchemy

**Exemplo (user.py):**
```python
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'admin', 'user'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    transactions = db.relationship('Transaction', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    institutions = db.relationship('Institution', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    investments = db.relationship('Investment', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    financial_plans = db.relationship('FinancialPlan', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password: str):
        """Hash da senha"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verificar senha"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'
```

**Exemplo (transaction.py):**
```python
from datetime import datetime
from app.extensions import db

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False, index=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id'), nullable=False)
    credit_card_id = db.Column(db.Integer, db.ForeignKey('credit_cards.id'), nullable=True)

    event_date = db.Column(db.Date, nullable=False, index=True)
    effective_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'completed'

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    category = db.relationship('Category', backref='transactions')
    institution = db.relationship('Institution', backref='transactions')
    credit_card = db.relationship('CreditCard', backref='transactions')

    # Índices compostos para queries comuns
    __table_args__ = (
        db.Index('idx_user_date', 'user_id', 'event_date'),
        db.Index('idx_user_category', 'user_id', 'category_id'),
        db.Index('idx_user_status', 'user_id', 'status'),
    )

    def __repr__(self):
        return f'<Transaction {self.id}: {self.description} - R$ {self.value}>'
```

### Migration Example

```python
"""
Initial migration - Create users and transactions tables

Revision ID: 001_initial
Revises:
Create Date: 2025-12-18 15:00:00
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Criar tabela users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Criar tabela transactions
    op.create_table(
        'transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('institution_id', sa.Integer(), nullable=False),
        sa.Column('credit_card_id', sa.Integer(), nullable=True),
        sa.Column('event_date', sa.Date(), nullable=False),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=False),
        sa.Column('value', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_date', 'transactions', ['user_id', 'event_date'])

def downgrade():
    op.drop_index('idx_user_date', table_name='transactions')
    op.drop_table('transactions')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
```

---

## API RESTFUL

### Convenções de Design

#### 1. Estrutura de URLs
```
Base URL: http://localhost:5000/api/v1

Recursos (Plural):
GET     /api/v1/transactions          # Listar todos
GET     /api/v1/transactions/:id      # Buscar por ID
POST    /api/v1/transactions          # Criar novo
PUT     /api/v1/transactions/:id      # Atualizar completo
PATCH   /api/v1/transactions/:id      # Atualizar parcial
DELETE  /api/v1/transactions/:id      # Deletar

Sub-recursos:
GET     /api/v1/transactions/:id/category     # Categoria da transação
GET     /api/v1/users/:id/transactions        # Transações do usuário

Ações especiais (verbos quando necessário):
POST    /api/v1/transactions/:id/complete     # Marcar como concluída
POST    /api/v1/transactions/:id/duplicate    # Duplicar transação
GET     /api/v1/dashboards/main               # Dashboard principal
POST    /api/v1/simulators/investment         # Simular investimento
```

#### 2. Verbos HTTP

| Verbo  | Ação | Idempotente | Safe |
|--------|------|-------------|------|
| GET    | Ler  | Sim         | Sim  |
| POST   | Criar| Não         | Não  |
| PUT    | Atualizar Total | Sim | Não  |
| PATCH  | Atualizar Parcial | Sim | Não |
| DELETE | Deletar | Sim     | Não  |

#### 3. Códigos de Status HTTP

| Código | Significado | Uso |
|--------|-------------|-----|
| 200 | OK | Sucesso em GET, PUT, PATCH |
| 201 | Created | Sucesso em POST |
| 204 | No Content | Sucesso em DELETE |
| 400 | Bad Request | Erro de validação |
| 401 | Unauthorized | Não autenticado |
| 403 | Forbidden | Sem permissão |
| 404 | Not Found | Recurso não encontrado |
| 409 | Conflict | Conflito (ex: email duplicado) |
| 422 | Unprocessable Entity | Erro de lógica de negócio |
| 500 | Internal Server Error | Erro no servidor |

#### 4. Formato de Resposta

**Sucesso:**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "description": "Supermercado",
    "value": -250.50
  },
  "message": "Transação criada com sucesso"
}
```

**Erro:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Dados inválidos",
    "details": {
      "value": ["Valor não pode ser zero"],
      "category_id": ["Categoria é obrigatória"]
    }
  }
}
```

**Lista com Paginação:**
```json
{
  "success": true,
  "data": [
    { "id": 1, "description": "..." },
    { "id": 2, "description": "..." }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 150,
    "pages": 8
  },
  "links": {
    "first": "/api/v1/transactions?page=1",
    "prev": null,
    "next": "/api/v1/transactions?page=2",
    "last": "/api/v1/transactions?page=8"
  }
}
```

### Endpoints Principais

#### Autenticação
```
POST   /api/v1/auth/register        # Registrar novo usuário
POST   /api/v1/auth/login           # Login (retorna JWT)
POST   /api/v1/auth/refresh         # Refresh token
POST   /api/v1/auth/logout          # Logout
GET    /api/v1/auth/me              # Dados do usuário logado
```

#### Transações
```
GET    /api/v1/transactions                    # Listar com filtros
POST   /api/v1/transactions                    # Criar
GET    /api/v1/transactions/:id                # Buscar
PUT    /api/v1/transactions/:id                # Atualizar
DELETE /api/v1/transactions/:id                # Deletar
POST   /api/v1/transactions/:id/complete       # Marcar concluída
GET    /api/v1/transactions/pending            # Listar pendentes
GET    /api/v1/transactions/summary            # Resumo (receitas, despesas, saldo)
```

#### Categorias
```
GET    /api/v1/categories                      # Listar todas
POST   /api/v1/categories                      # Criar
GET    /api/v1/categories/:id                  # Buscar
PUT    /api/v1/categories/:id                  # Atualizar
DELETE /api/v1/categories/:id                  # Deletar
GET    /api/v1/categories/:id/subcategories    # Listar subcategorias
```

#### Instituições
```
GET    /api/v1/institutions                    # Listar
POST   /api/v1/institutions                    # Criar
GET    /api/v1/institutions/:id                # Buscar
PUT    /api/v1/institutions/:id                # Atualizar
DELETE /api/v1/institutions/:id                # Deletar
GET    /api/v1/institutions/:id/balance        # Saldo da instituição
```

#### Investimentos
```
GET    /api/v1/investments                     # Listar
POST   /api/v1/investments                     # Criar
GET    /api/v1/investments/:id                 # Buscar
PUT    /api/v1/investments/:id                 # Atualizar
DELETE /api/v1/investments/:id                 # Deletar
POST   /api/v1/investments/:id/dividend        # Registrar provento
GET    /api/v1/investments/portfolio           # Visão consolidada
GET    /api/v1/investments/performance         # Análise de performance
```

#### Planos Financeiros
```
GET    /api/v1/plans                           # Listar
POST   /api/v1/plans                           # Criar
GET    /api/v1/plans/:id                       # Buscar
PUT    /api/v1/plans/:id                       # Atualizar
DELETE /api/v1/plans/:id                       # Deletar
POST   /api/v1/plans/:id/contribution          # Registrar aporte
GET    /api/v1/plans/:id/timeline              # Linha do tempo
POST   /api/v1/plans/:id/complete              # Marcar como concluído
```

#### Dashboards
```
GET    /api/v1/dashboards/main                 # Dashboard principal
GET    /api/v1/dashboards/investments          # Dashboard de investimentos
GET    /api/v1/dashboards/plans                # Dashboard de planos
```

#### Relatórios
```
GET    /api/v1/reports/monthly                 # Relatório mensal
GET    /api/v1/reports/annual                  # Relatório anual
GET    /api/v1/reports/by-category             # Por categoria
POST   /api/v1/reports/custom                  # Relatório customizado
GET    /api/v1/reports/:id/export              # Exportar (PDF/Excel)
```

#### Simuladores
```
POST   /api/v1/simulators/investment-goal      # Simular investimento para objetivo
POST   /api/v1/simulators/time-to-goal         # Calcular tempo para objetivo
POST   /api/v1/simulators/future-value         # Calcular valor futuro
```

### Exemplo de Implementação Completa

**Endpoint: POST /api/v1/transactions**

```python
# app/api/transactions.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from app.services.transaction_service import TransactionService
from app.schemas.transaction_schema import TransactionSchema, TransactionCreateSchema
from app.utils.exceptions import NotFoundError, BusinessLogicError
from app.utils.responses import success_response, error_response

transactions_bp = Blueprint('transactions', __name__, url_prefix='/api/v1/transactions')
transaction_service = TransactionService()
transaction_schema = TransactionSchema()
transaction_create_schema = TransactionCreateSchema()

@transactions_bp.route('', methods=['POST'])
@jwt_required()
def create_transaction():
    """
    Criar nova transação
    ---
    tags:
      - Transactions
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - event_date
            - category_id
            - institution_id
            - description
            - value
          properties:
            event_date:
              type: string
              format: date
              example: "2024-12-18"
            effective_date:
              type: string
              format: date
              example: "2024-12-18"
            category_id:
              type: integer
              example: 5
            institution_id:
              type: integer
              example: 1
            credit_card_id:
              type: integer
              example: 2
            description:
              type: string
              example: "Supermercado Carrefour"
            value:
              type: number
              example: -250.50
            status:
              type: string
              enum: [pending, completed]
              example: "completed"
    responses:
      201:
        description: Transação criada com sucesso
        schema:
          type: object
          properties:
            success:
              type: boolean
            data:
              $ref: '#/definitions/Transaction'
            message:
              type: string
      400:
        description: Erro de validação
      401:
        description: Não autenticado
      404:
        description: Categoria ou instituição não encontrada
      422:
        description: Erro de lógica de negócio
    """
    try:
        # 1. Obter usuário logado
        user_id = get_jwt_identity()

        # 2. Validar payload
        data = transaction_create_schema.load(request.get_json())

        # 3. Criar transação via service layer
        transaction = transaction_service.create(user_id, data)

        # 4. Serializar resposta
        result = transaction_schema.dump(transaction)

        # 5. Retornar sucesso
        return success_response(
            data=result,
            message="Transação criada com sucesso",
            status_code=201
        )

    except ValidationError as e:
        return error_response(
            code="VALIDATION_ERROR",
            message="Dados inválidos",
            details=e.messages,
            status_code=400
        )

    except NotFoundError as e:
        return error_response(
            code="NOT_FOUND",
            message=str(e),
            status_code=404
        )

    except BusinessLogicError as e:
        return error_response(
            code="BUSINESS_LOGIC_ERROR",
            message=str(e),
            status_code=422
        )

    except Exception as e:
        # Log error aqui
        return error_response(
            code="INTERNAL_ERROR",
            message="Erro interno do servidor",
            status_code=500
        )
```

**Schema (Marshmallow):**

```python
# app/schemas/transaction_schema.py
from marshmallow import Schema, fields, validates, ValidationError, post_load
from datetime import datetime, date

class TransactionCreateSchema(Schema):
    """Schema para criação de transação"""
    event_date = fields.Date(required=True)
    effective_date = fields.Date(required=False, allow_none=True)
    category_id = fields.Integer(required=True)
    institution_id = fields.Integer(required=True)
    credit_card_id = fields.Integer(required=False, allow_none=True)
    description = fields.String(required=True, validate=lambda x: len(x) >= 3)
    value = fields.Decimal(required=True, places=2)
    status = fields.String(required=False, load_default='pending')

    @validates('value')
    def validate_value(self, value):
        if value == 0:
            raise ValidationError("Valor não pode ser zero")

    @validates('event_date')
    def validate_event_date(self, event_date):
        # Não permitir datas futuras muito distantes
        max_future_date = date.today().replace(year=date.today().year + 1)
        if event_date > max_future_date:
            raise ValidationError("Data do evento não pode ser superior a 1 ano no futuro")

    @post_load
    def set_effective_date(self, data, **kwargs):
        """Se effective_date não informada, assume event_date"""
        if 'effective_date' not in data or data['effective_date'] is None:
            data['effective_date'] = data['event_date']
        return data

class TransactionSchema(Schema):
    """Schema para serialização de transação"""
    id = fields.Integer(dump_only=True)
    user_id = fields.Integer(dump_only=True)
    category_id = fields.Integer()
    institution_id = fields.Integer()
    credit_card_id = fields.Integer(allow_none=True)
    event_date = fields.Date()
    effective_date = fields.Date()
    description = fields.String()
    value = fields.Decimal(places=2)
    status = fields.String()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Nested relationships
    category = fields.Nested('CategorySchema', only=('id', 'name'))
    institution = fields.Nested('InstitutionSchema', only=('id', 'name'))
    credit_card = fields.Nested('CreditCardSchema', only=('id', 'name'), allow_none=True)
```

**Helpers de Resposta:**

```python
# app/utils/responses.py
from flask import jsonify

def success_response(data=None, message=None, status_code=200, **kwargs):
    """Resposta de sucesso padronizada"""
    response = {
        'success': True,
        'data': data,
    }

    if message:
        response['message'] = message

    # Adicionar campos extras (pagination, links, etc)
    response.update(kwargs)

    return jsonify(response), status_code

def error_response(code, message, details=None, status_code=400):
    """Resposta de erro padronizada"""
    response = {
        'success': False,
        'error': {
            'code': code,
            'message': message
        }
    }

    if details:
        response['error']['details'] = details

    return jsonify(response), status_code
```

---

## AUTENTICAÇÃO E SEGURANÇA

### JWT (JSON Web Tokens)

**Fluxo de Autenticação:**

```
1. Login:
   Cliente                        Servidor
     |                               |
     |  POST /api/v1/auth/login      |
     |  {email, password}            |
     |------------------------------>|
     |                               | Valida credenciais
     |                               | Gera JWT tokens
     |  200 OK                       |
     |  {access_token, refresh_token}|
     |<------------------------------|
     |                               |
     | Armazena tokens (localStorage)|
     |                               |

2. Requisições Autenticadas:
   Cliente                        Servidor
     |                               |
     |  GET /api/v1/transactions     |
     |  Header: Authorization:       |
     |          Bearer <access_token>|
     |------------------------------>|
     |                               | Valida JWT
     |                               | Extrai user_id
     |                               | Executa operação
     |  200 OK                       |
     |  {data}                       |
     |<------------------------------|

3. Refresh Token:
   Cliente                        Servidor
     |                               |
     | POST /api/v1/auth/refresh     |
     | {refresh_token}               |
     |------------------------------>|
     |                               | Valida refresh_token
     |                               | Gera novo access_token
     |  200 OK                       |
     |  {access_token}               |
     |<------------------------------|
```

**Implementação:**

```python
# app/api/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from datetime import timedelta
from app.services.auth_service import AuthService
from app.schemas.user_schema import UserLoginSchema, UserRegisterSchema
from app.utils.responses import success_response, error_response

auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')
auth_service = AuthService()
login_schema = UserLoginSchema()
register_schema = UserRegisterSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registrar novo usuário"""
    try:
        data = register_schema.load(request.get_json())
        user = auth_service.register(data)

        return success_response(
            data={'id': user.id, 'email': user.email},
            message="Usuário registrado com sucesso",
            status_code=201
        )
    except Exception as e:
        return error_response("REGISTRATION_ERROR", str(e), status_code=400)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login e geração de tokens"""
    try:
        data = login_schema.load(request.get_json())
        user = auth_service.authenticate(data['email'], data['password'])

        if not user:
            return error_response(
                "INVALID_CREDENTIALS",
                "Email ou senha inválidos",
                status_code=401
            )

        # Gerar tokens
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=1),
            additional_claims={'email': user.email, 'role': user.role}
        )

        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=timedelta(days=30)
        )

        return success_response(
            data={
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'role': user.role
                }
            },
            message="Login realizado com sucesso"
        )

    except Exception as e:
        return error_response("LOGIN_ERROR", str(e), status_code=400)

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Renovar access token usando refresh token"""
    user_id = get_jwt_identity()

    access_token = create_access_token(
        identity=user_id,
        expires_delta=timedelta(hours=1)
    )

    return success_response(
        data={'access_token': access_token},
        message="Token renovado com sucesso"
    )

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Obter dados do usuário logado"""
    user_id = get_jwt_identity()
    user = auth_service.get_user_by_id(user_id)

    return success_response(
        data={
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role
        }
    )
```

### Segurança - Checklist

```python
# config.py - Configurações de Segurança

class Config:
    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')  # Mudar em produção!
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # True apenas em dev

    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')

    # Rate Limiting
    RATELIMIT_STORAGE_URL = 'memory://'  # Usar Redis em produção
    RATELIMIT_DEFAULT = "100 per hour"

    # Bcrypt
    BCRYPT_LOG_ROUNDS = 12  # Custo computacional do hash

    # Security Headers
    SESSION_COOKIE_SECURE = True  # Apenas HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
```

### Proteção Contra Ataques Comuns

**1. SQL Injection**
✅ Protegido pelo SQLAlchemy ORM
✅ Sempre usar queries parametrizadas

**2. XSS (Cross-Site Scripting)**
✅ Validação de inputs com Marshmallow
✅ Sanitização de outputs
✅ Content Security Policy headers

**3. CSRF (Cross-Site Request Forgery)**
✅ API stateless (JWT)
✅ SameSite cookie attribute

**4. Brute Force**
✅ Rate limiting (Flask-Limiter)
✅ Account lockout após N tentativas

**5. Sensitive Data Exposure**
✅ Senhas sempre hasheadas (bcrypt)
✅ HTTPS em produção
✅ Não logar dados sensíveis

---

## PADRÕES DE CÓDIGO

### Python (Backend)

#### 1. PEP 8 + Black
```python
# Formatação automática com Black
black app/ tests/

# Linha máxima: 100 caracteres
# Aspas: Duplas preferencialmente
# Imports: Agrupados e ordenados
```

#### 2. Type Hints
```python
from typing import List, Dict, Optional
from decimal import Decimal

def calculate_balance(transactions: List[Transaction]) -> Decimal:
    """
    Calcular saldo total de transações

    Args:
        transactions: Lista de transações

    Returns:
        Saldo total
    """
    total: Decimal = Decimal('0.00')
    for transaction in transactions:
        total += transaction.value
    return total
```

#### 3. Docstrings
```python
def create_transaction(user_id: int, data: Dict) -> Transaction:
    """
    Criar nova transação com validações de negócio

    Args:
        user_id: ID do usuário
        data: Dados da transação
            - event_date: Data do evento (obrigatório)
            - category_id: ID da categoria (obrigatório)
            - value: Valor da transação (obrigatório)

    Returns:
        Transaction: Transação criada

    Raises:
        ValidationError: Se dados inválidos
        NotFoundError: Se categoria não existe

    Example:
        >>> transaction = create_transaction(1, {
        ...     'event_date': '2024-12-18',
        ...     'category_id': 5,
        ...     'value': -100.50
        ... })
        >>> transaction.id
        123
    """
    pass
```

#### 4. Logging
```python
import logging

logger = logging.getLogger(__name__)

def process_payment(transaction_id: int):
    logger.info(f"Processing payment for transaction {transaction_id}")

    try:
        # Processar pagamento
        result = payment_service.process(transaction_id)
        logger.info(f"Payment processed successfully: {result}")
        return result

    except PaymentError as e:
        logger.error(f"Payment failed for transaction {transaction_id}: {e}", exc_info=True)
        raise

    except Exception as e:
        logger.critical(f"Unexpected error processing payment {transaction_id}: {e}", exc_info=True)
        raise
```

#### 5. Error Handling
```python
# app/utils/exceptions.py

class AppError(Exception):
    """Base exception para erros da aplicação"""
    def __init__(self, message: str, code: str = None):
        self.message = message
        self.code = code or self.__class__.__name__
        super().__init__(self.message)

class ValidationError(AppError):
    """Erro de validação de dados"""
    pass

class NotFoundError(AppError):
    """Recurso não encontrado"""
    pass

class BusinessLogicError(AppError):
    """Erro de lógica de negócio"""
    pass

class UnauthorizedError(AppError):
    """Não autorizado"""
    pass
```

### JavaScript/React (Frontend)

#### 1. Componentes Funcionais
```javascript
// Preferir componentes funcionais + hooks
import React, { useState, useEffect } from 'react';

const TransactionForm = ({ onSubmit, initialData }) => {
  const [formData, setFormData] = useState(initialData || {});
  const [errors, setErrors] = useState({});

  useEffect(() => {
    // Load categories, institutions, etc.
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validate(formData)) {
      onSubmit(formData);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
    </form>
  );
};

export default TransactionForm;
```

#### 2. Hooks Customizados
```javascript
// src/hooks/useTransactions.js
import { useState, useEffect } from 'react';
import { transactionApi } from '../api/transactionApi';

export const useTransactions = (filters) => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTransactions = async () => {
      try {
        setLoading(true);
        const data = await transactionApi.list(filters);
        setTransactions(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, [filters]);

  return { transactions, loading, error };
};
```

#### 3. PropTypes ou TypeScript
```javascript
import PropTypes from 'prop-types';

const TransactionCard = ({ transaction, onClick }) => {
  return (
    <div className="card" onClick={() => onClick(transaction.id)}>
      <h3>{transaction.description}</h3>
      <p>{formatCurrency(transaction.value)}</p>
    </div>
  );
};

TransactionCard.propTypes = {
  transaction: PropTypes.shape({
    id: PropTypes.number.isRequired,
    description: PropTypes.string.isRequired,
    value: PropTypes.number.isRequired,
    category: PropTypes.object,
  }).isRequired,
  onClick: PropTypes.func.isRequired,
};

export default TransactionCard;
```

### Testes

#### Backend (pytest)
```python
# tests/unit/test_transaction_service.py
import pytest
from decimal import Decimal
from app.services.transaction_service import TransactionService
from app.utils.exceptions import ValidationError, NotFoundError
from tests.factories import UserFactory, CategoryFactory

class TestTransactionService:
    @pytest.fixture
    def service(self):
        return TransactionService()

    @pytest.fixture
    def user(self, db_session):
        return UserFactory.create()

    @pytest.fixture
    def category(self, db_session, user):
        return CategoryFactory.create(user=user, type='expense')

    def test_create_transaction_success(self, service, user, category):
        """Deve criar transação com sucesso"""
        data = {
            'event_date': '2024-12-18',
            'category_id': category.id,
            'institution_id': 1,
            'description': 'Test transaction',
            'value': -100.50
        }

        transaction = service.create(user.id, data)

        assert transaction.id is not None
        assert transaction.user_id == user.id
        assert transaction.value == Decimal('-100.50')

    def test_create_transaction_zero_value(self, service, user):
        """Deve rejeitar transação com valor zero"""
        data = {
            'event_date': '2024-12-18',
            'category_id': 1,
            'value': 0
        }

        with pytest.raises(ValidationError, match="Valor não pode ser zero"):
            service.create(user.id, data)

    def test_create_transaction_invalid_category(self, service, user):
        """Deve rejeitar categoria inexistente"""
        data = {
            'event_date': '2024-12-18',
            'category_id': 99999,
            'value': -100
        }

        with pytest.raises(NotFoundError, match="Categoria não encontrada"):
            service.create(user.id, data)
```

#### Frontend (Jest + React Testing Library)
```javascript
// src/components/TransactionForm.test.jsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TransactionForm from './TransactionForm';

describe('TransactionForm', () => {
  const mockOnSubmit = jest.fn();

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  it('should render form fields', () => {
    render(<TransactionForm onSubmit={mockOnSubmit} />);

    expect(screen.getByLabelText(/descrição/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/valor/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/categoria/i)).toBeInTheDocument();
  });

  it('should submit form with valid data', async () => {
    render(<TransactionForm onSubmit={mockOnSubmit} />);

    await userEvent.type(screen.getByLabelText(/descrição/i), 'Supermercado');
    await userEvent.type(screen.getByLabelText(/valor/i), '150.50');
    await userEvent.selectOptions(screen.getByLabelText(/categoria/i), '1');

    fireEvent.click(screen.getByRole('button', { name: /salvar/i }));

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          description: 'Supermercado',
          value: 150.50,
          category_id: 1,
        })
      );
    });
  });

  it('should show error for zero value', async () => {
    render(<TransactionForm onSubmit={mockOnSubmit} />);

    await userEvent.type(screen.getByLabelText(/valor/i), '0');
    fireEvent.click(screen.getByRole('button', { name: /salvar/i }));

    expect(await screen.findByText(/valor não pode ser zero/i)).toBeInTheDocument();
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });
});
```

---

## DEPLOY E INFRAESTRUTURA

### Docker Setup

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14-alpine
    container_name: planner_postgres
    environment:
      POSTGRES_DB: planner_financeiro
      POSTGRES_USER: planner_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - planner_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U planner_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: ../docker/backend.Dockerfile
    container_name: planner_backend
    command: gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
    environment:
      FLASK_APP: app
      FLASK_ENV: production
      DATABASE_URL: postgresql://planner_user:${DB_PASSWORD}@postgres:5432/planner_financeiro
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      CORS_ORIGINS: http://localhost:3000
    volumes:
      - ./backend:/app
    ports:
      - "5000:5000"
    depends_on:
      postgres:
        condition: service_healthy
    networks:
      - planner_network

  frontend:
    build:
      context: ./frontend
      dockerfile: ../docker/frontend.Dockerfile
    container_name: planner_frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    networks:
      - planner_network

networks:
  planner_network:
    driver: bridge

volumes:
  postgres_data:
```

**backend.Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar aplicação
COPY . .

# Criar usuário não-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
```

**frontend.Dockerfile:**
```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Comandos de Deploy

```bash
# Desenvolvimento
docker-compose -f docker-compose.dev.yml up --build

# Produção
docker-compose up -d --build

# Migrations
docker-compose exec backend flask db upgrade

# Seed database
docker-compose exec backend python scripts/seed_db.py

# Backup
docker-compose exec postgres pg_dump -U planner_user planner_financeiro > backup.sql

# Restore
docker-compose exec -T postgres psql -U planner_user planner_financeiro < backup.sql
```

### Acesso via Rede Local

#### Opção 1: IP Local
```
http://192.168.1.X:3000  # Frontend
http://192.168.1.X:5000  # Backend API
```

#### Opção 2: Hostname (.local)
```
http://planner-financeiro.local:3000
```

**Configurar hostname (Linux/Mac):**
```bash
# Adicionar ao /etc/hosts (requer sudo)
echo "192.168.1.X planner-financeiro.local" | sudo tee -a /etc/hosts
```

#### Opção 3: DNS Local (Pi-hole, Router)
Configurar DNS customizado no roteador apontando para IP do servidor

---

## PRÓXIMOS PASSOS

### 1. Setup Inicial
- [ ] Criar estrutura de pastas
- [ ] Configurar ambientes virtuais (venv)
- [ ] Instalar dependências
- [ ] Configurar .gitignore
- [ ] Inicializar Git repository

### 2. Backend Base
- [ ] Setup Flask + extensões
- [ ] Configurar SQLAlchemy + Alembic
- [ ] Criar primeira migration (users table)
- [ ] Implementar autenticação JWT
- [ ] Criar primeiro endpoint (auth/login)
- [ ] Escrever primeiro teste

### 3. Frontend Base
- [ ] Setup React + Vite
- [ ] Configurar Tailwind CSS
- [ ] Criar estrutura de rotas
- [ ] Implementar autenticação (login/logout)
- [ ] Configurar Axios + interceptors
- [ ] Criar componentes base (Button, Input, etc.)

### 4. MVP - Primeira Feature
- [ ] Implementar CRUD de transações (backend)
- [ ] Criar interface de transações (frontend)
- [ ] Testes unitários e integração
- [ ] Documentação da API

---

**Documento criado em:** 18/12/2025
**Versão:** 1.0
**Status:** Pronto para desenvolvimento
