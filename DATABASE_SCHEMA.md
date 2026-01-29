# MODELO DE BANCO DE DADOS - PLANNER FINANCEIRO

**Projeto:** Sistema de Gestão Financeira Pessoal Web
**Banco de Dados:** PostgreSQL 14+
**ORM:** SQLAlchemy 2.0
**Migrations:** Alembic
**Versão:** 1.0
**Data:** 18 de Dezembro de 2025

---

## ÍNDICE

1. [Convenções e Padrões](#convenções-e-padrões)
2. [Diagrama ER Completo](#diagrama-er-completo)
3. [Tabelas Detalhadas](#tabelas-detalhadas)
4. [Índices e Performance](#índices-e-performance)
5. [Triggers e Functions](#triggers-e-functions)
6. [Views Materializadas](#views-materializadas)
7. [Scripts SQL](#scripts-sql)
8. [Migrations Alembic](#migrations-alembic)

---

## CONVENÇÕES E PADRÕES

### Nomenclatura

**Tabelas:**
- Sempre no plural: `users`, `transactions`, `categories`
- Snake_case: `financial_plans`, `credit_cards`

**Colunas:**
- Snake_case: `user_id`, `created_at`, `event_date`
- Timestamps: `created_at`, `updated_at`
- Foreign keys: `<tabela>_id` (ex: `user_id`, `category_id`)

**Índices:**
- Formato: `idx_<tabela>_<colunas>` (ex: `idx_transactions_user_date`)
- Compostos: `idx_transactions_user_category_status`

**Constraints:**
- Primary Key: `pk_<tabela>` (padrão PostgreSQL)
- Foreign Key: `fk_<tabela>_<coluna>_<tabela_ref>`
- Unique: `uq_<tabela>_<coluna(s)>`
- Check: `ck_<tabela>_<regra>`

### Tipos de Dados Padrão

```sql
-- IDs
id SERIAL PRIMARY KEY  -- ou BIGSERIAL para tabelas grandes

-- Strings
email VARCHAR(120)
name VARCHAR(100)
description TEXT

-- Numéricos
value NUMERIC(12, 2)  -- Valores monetários
percentage NUMERIC(5, 2)  -- Percentuais

-- Datas
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
event_date DATE
is_active BOOLEAN DEFAULT TRUE

-- Enums (usar CHECK constraints ou ENUMs nativos)
status VARCHAR(20) CHECK (status IN ('pending', 'completed'))
```

---

## DIAGRAMA ER COMPLETO

```sql
┌────────────────────────────┐
│          users             │
├────────────────────────────┤
│ • id (PK)                  │
│   email                    │
│   password_hash            │
│   full_name                │
│   role                     │
│   is_active                │
│   created_at               │
│   updated_at               │
└────────────────────────────┘
         │
         │ 1:N
         ├──────────────────────────────────┐
         │                                  │
         ▼                                  ▼
┌────────────────────────┐      ┌────────────────────────┐
│      categories        │      │     institutions       │
├────────────────────────┤      ├────────────────────────┤
│ • id (PK)              │      │ • id (PK)              │
│ ○ user_id (FK)         │      │ ○ user_id (FK)         │
│   name                 │      │   name                 │
│   type                 │      │   type                 │
│ ○ parent_id (FK)       │      │   partition            │
│   color                │      │   initial_balance      │
│   icon                 │      │   current_balance      │
│   created_at           │      │   is_active            │
└────────────────────────┘      │   created_at           │
         │                      │   updated_at           │
         │ 1:1 (self)           └────────────────────────┘
         │                               │
         ├───────────────────────────────┼──────────┐
         │                               │          │
         │                               │ 1:N      │ 1:N
         │                               │          │
         ▼                               ▼          ▼
┌────────────────────────┐      ┌────────────────────────┐
│    transactions        │      │    credit_cards        │
├────────────────────────┤      ├────────────────────────┤
│ • id (PK)              │      │ • id (PK)              │
│ ○ user_id (FK)         │      │ ○ user_id (FK)         │
│ ○ category_id (FK)     │      │ ○ institution_id (FK)  │
│ ○ institution_id (FK)  │      │   name                 │
│ ○ credit_card_id (FK)  │◄────┐│   brand                │
│   event_date           │     ││   last_four_digits     │
│   effective_date       │     ││   closing_day          │
│   description          │     ││   due_day              │
│   value                │     ││   limit_amount         │
│   status               │     ││   is_active            │
│   notes                │     ││   created_at           │
│   created_at           │     ││   updated_at           │
│   updated_at           │     │└────────────────────────┘
└────────────────────────┘     │
                               │
┌────────────────────────┐     │
│     investments        │     │
├────────────────────────┤     │
│ • id (PK)              │     │
│ ○ user_id (FK)         │     │
│ ○ institution_id (FK)  │─────┘
│   product_type         │
│   classification       │
│   ticker               │
│   quantity             │
│   invested_value       │
│   current_value        │
│   investment_date      │
│   maturity_date        │
│   rate                 │
│   is_active            │
│   notes                │
│   created_at           │
│   updated_at           │
└────────────────────────┘
         │
         │ 1:N
         ▼
┌────────────────────────┐
│   investment_earnings  │
├────────────────────────┤
│ • id (PK)              │
│ ○ investment_id (FK)   │
│   type                 │
│   payment_date         │
│   value                │
│   description          │
│   created_at           │
└────────────────────────┘

┌────────────────────────┐
│   financial_plans      │
├────────────────────────┤
│ • id (PK)              │
│ ○ user_id (FK)         │
│ ○ institution_id (FK)  │
│   name                 │
│   description          │
│   target_value         │
│   monthly_contribution │
│   current_value        │
│   start_date           │
│   target_date          │
│   partition            │
│   priority             │
│   is_completed         │
│   completed_at         │
│   created_at           │
│   updated_at           │
└────────────────────────┘
         │
         │ 1:N
         ▼
┌────────────────────────┐
│  plan_contributions    │
├────────────────────────┤
│ • id (PK)              │
│ ○ plan_id (FK)         │
│   contribution_date    │
│   value                │
│   notes                │
│   created_at           │
└────────────────────────┘

┌────────────────────────┐
│   revenue_planning     │
├────────────────────────┤
│ • id (PK)              │
│ ○ user_id (FK)         │
│   year                 │
│   month                │
│   fixed_income         │
│   extra_income         │
│   thirteenth_salary    │
│   notes                │
│   created_at           │
│   updated_at           │
└────────────────────────┘

┌────────────────────────┐
│      audit_logs        │
├────────────────────────┤
│ • id (PK)              │
│ ○ user_id (FK)         │
│   action               │
│   entity_type          │
│   entity_id            │
│   changes              │
│   ip_address           │
│   user_agent           │
│   created_at           │
└────────────────────────┘

┌────────────────────────┐
│    user_sessions       │
├────────────────────────┤
│ • id (PK)              │
│ ○ user_id (FK)         │
│   token_jti            │
│   expires_at           │
│   revoked              │
│   created_at           │
└────────────────────────┘

Legenda:
• = Primary Key
○ = Foreign Key
```

---

## TABELAS DETALHADAS

### 1. users

**Descrição:** Usuários do sistema (família)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'user',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT ck_users_role CHECK (role IN ('admin', 'user'))
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_is_active ON users(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE users IS 'Usuários do sistema';
COMMENT ON COLUMN users.role IS 'admin: acesso total, user: acesso limitado';
```

**SQLAlchemy Model:**
```python
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint("role IN ('admin', 'user')", name='ck_users_role'),
    )
```

---

### 2. categories

**Descrição:** Categorias e subcategorias de transações

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL,
    parent_id INTEGER,
    color VARCHAR(7),
    icon VARCHAR(50),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_categories_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_categories_parent FOREIGN KEY (parent_id)
        REFERENCES categories(id) ON DELETE SET NULL,
    CONSTRAINT ck_categories_type CHECK (type IN ('income', 'expense')),
    CONSTRAINT uq_categories_user_name_parent UNIQUE (user_id, name, parent_id)
);

CREATE INDEX idx_categories_user ON categories(user_id);
CREATE INDEX idx_categories_parent ON categories(parent_id);
CREATE INDEX idx_categories_type ON categories(type);

COMMENT ON TABLE categories IS 'Categorias hierárquicas de receitas e despesas';
COMMENT ON COLUMN categories.parent_id IS 'NULL = categoria principal, NOT NULL = subcategoria';
COMMENT ON COLUMN categories.color IS 'Código hexadecimal da cor (ex: #FF5733)';
```

**SQLAlchemy Model:**
```python
class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'))
    color = db.Column(db.String(7))
    icon = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relacionamentos
    user = db.relationship('User', backref='categories')
    parent = db.relationship('Category', remote_side=[id], backref='subcategories')

    __table_args__ = (
        db.CheckConstraint("type IN ('income', 'expense')", name='ck_categories_type'),
        db.UniqueConstraint('user_id', 'name', 'parent_id', name='uq_categories_user_name_parent'),
    )
```

---

### 3. institutions

**Descrição:** Instituições financeiras (bancos, corretoras)

```sql
CREATE TABLE institutions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL,
    partition VARCHAR(50) NOT NULL DEFAULT 'Principal',
    initial_balance NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    current_balance NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_institutions_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT ck_institutions_type CHECK (type IN ('bank', 'brokerage', 'wallet')),
    CONSTRAINT uq_institutions_user_name_partition UNIQUE (user_id, name, partition)
);

CREATE INDEX idx_institutions_user ON institutions(user_id);
CREATE INDEX idx_institutions_is_active ON institutions(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE institutions IS 'Instituições financeiras onde o dinheiro está depositado';
COMMENT ON COLUMN institutions.partition IS 'Subdivisão lógica (ex: Principal, Reserva, Emergência)';
COMMENT ON COLUMN institutions.current_balance IS 'Saldo atual calculado automaticamente';
```

**SQLAlchemy Model:**
```python
class Institution(db.Model):
    __tablename__ = 'institutions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(20), nullable=False)
    partition = db.Column(db.String(50), nullable=False, default='Principal')
    initial_balance = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    current_balance = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='institutions')

    __table_args__ = (
        db.CheckConstraint("type IN ('bank', 'brokerage', 'wallet')", name='ck_institutions_type'),
        db.UniqueConstraint('user_id', 'name', 'partition', name='uq_institutions_user_name_partition'),
    )
```

---

### 4. credit_cards

**Descrição:** Cartões de crédito

```sql
CREATE TABLE credit_cards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    institution_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    brand VARCHAR(50),
    last_four_digits VARCHAR(4),
    closing_day INTEGER NOT NULL,
    due_day INTEGER NOT NULL,
    limit_amount NUMERIC(12, 2),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_credit_cards_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_credit_cards_institution FOREIGN KEY (institution_id)
        REFERENCES institutions(id) ON DELETE CASCADE,
    CONSTRAINT ck_credit_cards_closing_day CHECK (closing_day BETWEEN 1 AND 31),
    CONSTRAINT ck_credit_cards_due_day CHECK (due_day BETWEEN 1 AND 31),
    CONSTRAINT uq_credit_cards_user_name UNIQUE (user_id, name)
);

CREATE INDEX idx_credit_cards_user ON credit_cards(user_id);
CREATE INDEX idx_credit_cards_institution ON credit_cards(institution_id);
CREATE INDEX idx_credit_cards_is_active ON credit_cards(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE credit_cards IS 'Cartões de crédito vinculados a instituições';
COMMENT ON COLUMN credit_cards.closing_day IS 'Dia de fechamento da fatura (1-31)';
COMMENT ON COLUMN credit_cards.due_day IS 'Dia de vencimento da fatura (1-31)';
```

**SQLAlchemy Model:**
```python
class CreditCard(db.Model):
    __tablename__ = 'credit_cards'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(50))
    last_four_digits = db.Column(db.String(4))
    closing_day = db.Column(db.Integer, nullable=False)
    due_day = db.Column(db.Integer, nullable=False)
    limit_amount = db.Column(db.Numeric(12, 2))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='credit_cards')
    institution = db.relationship('Institution', backref='credit_cards')

    __table_args__ = (
        db.CheckConstraint('closing_day BETWEEN 1 AND 31', name='ck_credit_cards_closing_day'),
        db.CheckConstraint('due_day BETWEEN 1 AND 31', name='ck_credit_cards_due_day'),
        db.UniqueConstraint('user_id', 'name', name='uq_credit_cards_user_name'),
    )
```

---

### 5. transactions

**Descrição:** Transações financeiras (receitas e despesas)

```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    institution_id INTEGER NOT NULL,
    credit_card_id INTEGER,
    event_date DATE NOT NULL,
    effective_date DATE NOT NULL,
    description VARCHAR(255) NOT NULL,
    value NUMERIC(12, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_transactions_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_transactions_category FOREIGN KEY (category_id)
        REFERENCES categories(id) ON DELETE RESTRICT,
    CONSTRAINT fk_transactions_institution FOREIGN KEY (institution_id)
        REFERENCES institutions(id) ON DELETE RESTRICT,
    CONSTRAINT fk_transactions_credit_card FOREIGN KEY (credit_card_id)
        REFERENCES credit_cards(id) ON DELETE SET NULL,
    CONSTRAINT ck_transactions_value CHECK (value <> 0),
    CONSTRAINT ck_transactions_status CHECK (status IN ('pending', 'completed', 'cancelled'))
);

CREATE INDEX idx_transactions_user ON transactions(user_id);
CREATE INDEX idx_transactions_category ON transactions(category_id);
CREATE INDEX idx_transactions_institution ON transactions(institution_id);
CREATE INDEX idx_transactions_credit_card ON transactions(credit_card_id);
CREATE INDEX idx_transactions_event_date ON transactions(event_date);
CREATE INDEX idx_transactions_effective_date ON transactions(effective_date);
CREATE INDEX idx_transactions_status ON transactions(status);

-- Índices compostos para queries comuns
CREATE INDEX idx_transactions_user_date ON transactions(user_id, event_date DESC);
CREATE INDEX idx_transactions_user_category ON transactions(user_id, category_id);
CREATE INDEX idx_transactions_user_status ON transactions(user_id, status) WHERE status = 'pending';

COMMENT ON TABLE transactions IS 'Todas as transações financeiras (receitas e despesas)';
COMMENT ON COLUMN transactions.event_date IS 'Data em que a transação ocorreu';
COMMENT ON COLUMN transactions.effective_date IS 'Data em que a transação impacta o saldo';
COMMENT ON COLUMN transactions.value IS 'Positivo = receita, Negativo = despesa';
```

**SQLAlchemy Model:**
```python
class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='RESTRICT'), nullable=False)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id', ondelete='RESTRICT'), nullable=False)
    credit_card_id = db.Column(db.Integer, db.ForeignKey('credit_cards.id', ondelete='SET NULL'))
    event_date = db.Column(db.Date, nullable=False, index=True)
    effective_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Numeric(12, 2), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    user = db.relationship('User', backref='transactions')
    category = db.relationship('Category', backref='transactions')
    institution = db.relationship('Institution', backref='transactions')
    credit_card = db.relationship('CreditCard', backref='transactions')

    __table_args__ = (
        db.CheckConstraint('value <> 0', name='ck_transactions_value'),
        db.CheckConstraint("status IN ('pending', 'completed', 'cancelled')", name='ck_transactions_status'),
        db.Index('idx_transactions_user_date', 'user_id', 'event_date'),
        db.Index('idx_transactions_user_category', 'user_id', 'category_id'),
    )
```

---

### 6. investments

**Descrição:** Investimentos (renda fixa e variável)

```sql
CREATE TABLE investments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    institution_id INTEGER NOT NULL,
    product_type VARCHAR(50) NOT NULL,
    classification VARCHAR(20) NOT NULL,
    ticker VARCHAR(20),
    quantity NUMERIC(12, 6),
    invested_value NUMERIC(12, 2) NOT NULL,
    current_value NUMERIC(12, 2) NOT NULL,
    investment_date DATE NOT NULL,
    maturity_date DATE,
    rate NUMERIC(5, 2),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_investments_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_investments_institution FOREIGN KEY (institution_id)
        REFERENCES institutions(id) ON DELETE RESTRICT,
    CONSTRAINT ck_investments_classification CHECK (classification IN ('fixed_income', 'variable_income')),
    CONSTRAINT ck_investments_values CHECK (invested_value > 0 AND current_value >= 0)
);

CREATE INDEX idx_investments_user ON investments(user_id);
CREATE INDEX idx_investments_institution ON investments(institution_id);
CREATE INDEX idx_investments_classification ON investments(classification);
CREATE INDEX idx_investments_ticker ON investments(ticker);
CREATE INDEX idx_investments_is_active ON investments(is_active) WHERE is_active = TRUE;

COMMENT ON TABLE investments IS 'Portfólio de investimentos';
COMMENT ON COLUMN investments.product_type IS 'CDB, CRA, CRI, Tesouro, Ações, FIIs, ETF, etc.';
COMMENT ON COLUMN investments.classification IS 'fixed_income ou variable_income';
COMMENT ON COLUMN investments.ticker IS 'Código de negociação (ações, FIIs)';
COMMENT ON COLUMN investments.quantity IS 'Quantidade de ativos (ações, cotas)';
COMMENT ON COLUMN investments.rate IS 'Taxa de rentabilidade (% a.a.)';
```

**SQLAlchemy Model:**
```python
class Investment(db.Model):
    __tablename__ = 'investments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id', ondelete='RESTRICT'), nullable=False)
    product_type = db.Column(db.String(50), nullable=False)
    classification = db.Column(db.String(20), nullable=False)
    ticker = db.Column(db.String(20), index=True)
    quantity = db.Column(db.Numeric(12, 6))
    invested_value = db.Column(db.Numeric(12, 2), nullable=False)
    current_value = db.Column(db.Numeric(12, 2), nullable=False)
    investment_date = db.Column(db.Date, nullable=False)
    maturity_date = db.Column(db.Date)
    rate = db.Column(db.Numeric(5, 2))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='investments')
    institution = db.relationship('Institution', backref='investments')

    __table_args__ = (
        db.CheckConstraint("classification IN ('fixed_income', 'variable_income')", name='ck_investments_classification'),
        db.CheckConstraint('invested_value > 0 AND current_value >= 0', name='ck_investments_values'),
    )
```

---

### 7. investment_earnings

**Descrição:** Proventos e dividendos de investimentos

```sql
CREATE TABLE investment_earnings (
    id SERIAL PRIMARY KEY,
    investment_id INTEGER NOT NULL,
    type VARCHAR(20) NOT NULL,
    payment_date DATE NOT NULL,
    value NUMERIC(12, 2) NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_investment_earnings_investment FOREIGN KEY (investment_id)
        REFERENCES investments(id) ON DELETE CASCADE,
    CONSTRAINT ck_investment_earnings_type CHECK (type IN ('dividend', 'interest', 'rent', 'bonus')),
    CONSTRAINT ck_investment_earnings_value CHECK (value > 0)
);

CREATE INDEX idx_investment_earnings_investment ON investment_earnings(investment_id);
CREATE INDEX idx_investment_earnings_payment_date ON investment_earnings(payment_date);

COMMENT ON TABLE investment_earnings IS 'Proventos, dividendos e rendimentos de investimentos';
COMMENT ON COLUMN investment_earnings.type IS 'dividend, interest, rent, bonus';
```

**SQLAlchemy Model:**
```python
class InvestmentEarning(db.Model):
    __tablename__ = 'investment_earnings'

    id = db.Column(db.Integer, primary_key=True)
    investment_id = db.Column(db.Integer, db.ForeignKey('investments.id', ondelete='CASCADE'), nullable=False, index=True)
    type = db.Column(db.String(20), nullable=False)
    payment_date = db.Column(db.Date, nullable=False, index=True)
    value = db.Column(db.Numeric(12, 2), nullable=False)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    investment = db.relationship('Investment', backref='earnings')

    __table_args__ = (
        db.CheckConstraint("type IN ('dividend', 'interest', 'rent', 'bonus')", name='ck_investment_earnings_type'),
        db.CheckConstraint('value > 0', name='ck_investment_earnings_value'),
    )
```

---

### 8. financial_plans

**Descrição:** Planos financeiros de longo prazo

```sql
CREATE TABLE financial_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    institution_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    target_value NUMERIC(12, 2) NOT NULL,
    monthly_contribution NUMERIC(12, 2) NOT NULL,
    current_value NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    start_date DATE NOT NULL,
    target_date DATE,
    partition VARCHAR(50) NOT NULL DEFAULT 'Principal',
    priority INTEGER NOT NULL DEFAULT 5,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_financial_plans_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_financial_plans_institution FOREIGN KEY (institution_id)
        REFERENCES institutions(id) ON DELETE RESTRICT,
    CONSTRAINT ck_financial_plans_values CHECK (target_value > 0 AND monthly_contribution >= 0),
    CONSTRAINT ck_financial_plans_priority CHECK (priority BETWEEN 1 AND 10),
    CONSTRAINT ck_financial_plans_dates CHECK (target_date IS NULL OR target_date >= start_date)
);

CREATE INDEX idx_financial_plans_user ON financial_plans(user_id);
CREATE INDEX idx_financial_plans_institution ON financial_plans(institution_id);
CREATE INDEX idx_financial_plans_is_completed ON financial_plans(is_completed) WHERE is_completed = FALSE;

COMMENT ON TABLE financial_plans IS 'Metas financeiras de longo prazo';
COMMENT ON COLUMN financial_plans.priority IS 'Prioridade do plano (1=máxima, 10=mínima)';
COMMENT ON COLUMN financial_plans.partition IS 'Subdivisão da instituição financeira';
```

**SQLAlchemy Model:**
```python
class FinancialPlan(db.Model):
    __tablename__ = 'financial_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    institution_id = db.Column(db.Integer, db.ForeignKey('institutions.id', ondelete='RESTRICT'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    target_value = db.Column(db.Numeric(12, 2), nullable=False)
    monthly_contribution = db.Column(db.Numeric(12, 2), nullable=False)
    current_value = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    start_date = db.Column(db.Date, nullable=False)
    target_date = db.Column(db.Date)
    partition = db.Column(db.String(50), nullable=False, default='Principal')
    priority = db.Column(db.Integer, nullable=False, default=5)
    is_completed = db.Column(db.Boolean, nullable=False, default=False)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='financial_plans')
    institution = db.relationship('Institution', backref='financial_plans')

    __table_args__ = (
        db.CheckConstraint('target_value > 0 AND monthly_contribution >= 0', name='ck_financial_plans_values'),
        db.CheckConstraint('priority BETWEEN 1 AND 10', name='ck_financial_plans_priority'),
        db.CheckConstraint('target_date IS NULL OR target_date >= start_date', name='ck_financial_plans_dates'),
    )
```

---

### 9. plan_contributions

**Descrição:** Aportes mensais em planos financeiros

```sql
CREATE TABLE plan_contributions (
    id SERIAL PRIMARY KEY,
    plan_id INTEGER NOT NULL,
    contribution_date DATE NOT NULL,
    value NUMERIC(12, 2) NOT NULL,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_plan_contributions_plan FOREIGN KEY (plan_id)
        REFERENCES financial_plans(id) ON DELETE CASCADE,
    CONSTRAINT ck_plan_contributions_value CHECK (value > 0)
);

CREATE INDEX idx_plan_contributions_plan ON plan_contributions(plan_id);
CREATE INDEX idx_plan_contributions_date ON plan_contributions(contribution_date);

COMMENT ON TABLE plan_contributions IS 'Histórico de aportes em planos financeiros';
```

**SQLAlchemy Model:**
```python
class PlanContribution(db.Model):
    __tablename__ = 'plan_contributions'

    id = db.Column(db.Integer, primary_key=True)
    plan_id = db.Column(db.Integer, db.ForeignKey('financial_plans.id', ondelete='CASCADE'), nullable=False, index=True)
    contribution_date = db.Column(db.Date, nullable=False, index=True)
    value = db.Column(db.Numeric(12, 2), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    plan = db.relationship('FinancialPlan', backref='contributions')

    __table_args__ = (
        db.CheckConstraint('value > 0', name='ck_plan_contributions_value'),
    )
```

---

### 10. revenue_planning

**Descrição:** Planejamento de receitas futuras

```sql
CREATE TABLE revenue_planning (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    fixed_income NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    extra_income NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    thirteenth_salary NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    notes TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_revenue_planning_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT ck_revenue_planning_year CHECK (year BETWEEN 2000 AND 2100),
    CONSTRAINT ck_revenue_planning_month CHECK (month BETWEEN 1 AND 12),
    CONSTRAINT uq_revenue_planning_user_year_month UNIQUE (user_id, year, month)
);

CREATE INDEX idx_revenue_planning_user ON revenue_planning(user_id);
CREATE INDEX idx_revenue_planning_year_month ON revenue_planning(year, month);

COMMENT ON TABLE revenue_planning IS 'Projeção mensal de receitas';
COMMENT ON COLUMN revenue_planning.fixed_income IS 'Receita fixa mensal (salário)';
COMMENT ON COLUMN revenue_planning.extra_income IS 'Receitas extras (bônus, freelance)';
COMMENT ON COLUMN revenue_planning.thirteenth_salary IS '13º salário';
```

**SQLAlchemy Model:**
```python
class RevenuePlanning(db.Model):
    __tablename__ = 'revenue_planning'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    fixed_income = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    extra_income = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    thirteenth_salary = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', backref='revenue_planning')

    __table_args__ = (
        db.CheckConstraint('year BETWEEN 2000 AND 2100', name='ck_revenue_planning_year'),
        db.CheckConstraint('month BETWEEN 1 AND 12', name='ck_revenue_planning_month'),
        db.UniqueConstraint('user_id', 'year', 'month', name='uq_revenue_planning_user_year_month'),
    )
```

---

### 11. audit_logs

**Descrição:** Logs de auditoria

```sql
CREATE TABLE audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER,
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_audit_logs_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

COMMENT ON TABLE audit_logs IS 'Registro de todas as ações importantes do sistema';
COMMENT ON COLUMN audit_logs.action IS 'CREATE, UPDATE, DELETE, LOGIN, etc.';
COMMENT ON COLUMN audit_logs.changes IS 'JSON com valores antes/depois';
```

**SQLAlchemy Model:**
```python
from sqlalchemy.dialects.postgresql import JSONB, INET

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), index=True)
    action = db.Column(db.String(50), nullable=False, index=True)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer)
    changes = db.Column(JSONB)
    ip_address = db.Column(INET)
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    user = db.relationship('User', backref='audit_logs')

    __table_args__ = (
        db.Index('idx_audit_logs_entity', 'entity_type', 'entity_id'),
    )
```

---

### 12. user_sessions

**Descrição:** Sessões de usuários (JWT)

```sql
CREATE TABLE user_sessions (
    id BIGSERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token_jti VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_user_sessions_user FOREIGN KEY (user_id)
        REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX idx_user_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token_jti ON user_sessions(token_jti);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX idx_user_sessions_revoked ON user_sessions(revoked) WHERE revoked = FALSE;

COMMENT ON TABLE user_sessions IS 'Controle de sessões JWT ativas';
COMMENT ON COLUMN user_sessions.token_jti IS 'JWT ID único (para blacklist)';
```

**SQLAlchemy Model:**
```python
class UserSession(db.Model):
    __tablename__ = 'user_sessions'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    token_jti = db.Column(db.String(255), unique=True, nullable=False, index=True)
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    revoked = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref='sessions')
```

---

## ÍNDICES E PERFORMANCE

### Estratégia de Indexação

```sql
-- 1. Sempre indexar Foreign Keys
-- Já implementado em todas as tabelas acima

-- 2. Indexar colunas de filtro comuns
CREATE INDEX idx_transactions_user_status_date
    ON transactions(user_id, status, event_date DESC);

-- 3. Índices parciais para queries específicas
CREATE INDEX idx_transactions_pending
    ON transactions(user_id, event_date)
    WHERE status = 'pending';

CREATE INDEX idx_investments_active
    ON investments(user_id, classification)
    WHERE is_active = TRUE;

-- 4. Índices para ordenação
CREATE INDEX idx_transactions_date_desc
    ON transactions(event_date DESC);

-- 5. Índices GIN para busca em JSONB
CREATE INDEX idx_audit_logs_changes_gin
    ON audit_logs USING GIN (changes);
```

### Análise de Queries

```sql
-- Verificar uso de índices
EXPLAIN ANALYZE
SELECT * FROM transactions
WHERE user_id = 1
  AND event_date >= '2024-01-01'
  AND status = 'completed'
ORDER BY event_date DESC
LIMIT 20;

-- Identificar índices não utilizados
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND schemaname = 'public'
ORDER BY tablename, indexname;
```

---

## TRIGGERS E FUNCTIONS

### 1. Atualizar current_balance em institutions

```sql
CREATE OR REPLACE FUNCTION update_institution_balance()
RETURNS TRIGGER AS $$
BEGIN
    -- Atualizar saldo quando transação for concluída
    IF NEW.status = 'completed' AND (TG_OP = 'INSERT' OR OLD.status <> 'completed') THEN
        UPDATE institutions
        SET current_balance = current_balance + NEW.value,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = NEW.institution_id;
    END IF;

    -- Reverter saldo se transação foi cancelada
    IF TG_OP = 'UPDATE' AND OLD.status = 'completed' AND NEW.status = 'cancelled' THEN
        UPDATE institutions
        SET current_balance = current_balance - OLD.value,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = NEW.institution_id;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_institution_balance
AFTER INSERT OR UPDATE ON transactions
FOR EACH ROW
EXECUTE FUNCTION update_institution_balance();
```

### 2. Auto-atualizar updated_at

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Aplicar em todas as tabelas com updated_at
CREATE TRIGGER trigger_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_transactions_updated_at
BEFORE UPDATE ON transactions
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Repetir para outras tabelas...
```

### 3. Audit Log automático

```sql
CREATE OR REPLACE FUNCTION log_audit_trail()
RETURNS TRIGGER AS $$
DECLARE
    changes JSONB;
BEGIN
    IF TG_OP = 'INSERT' THEN
        changes := jsonb_build_object('new', row_to_json(NEW));
    ELSIF TG_OP = 'UPDATE' THEN
        changes := jsonb_build_object('old', row_to_json(OLD), 'new', row_to_json(NEW));
    ELSIF TG_OP = 'DELETE' THEN
        changes := jsonb_build_object('old', row_to_json(OLD));
    END IF;

    INSERT INTO audit_logs (user_id, action, entity_type, entity_id, changes)
    VALUES (
        COALESCE(NEW.user_id, OLD.user_id),
        TG_OP,
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        changes
    );

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

-- Aplicar em tabelas críticas
CREATE TRIGGER trigger_transactions_audit
AFTER INSERT OR UPDATE OR DELETE ON transactions
FOR EACH ROW
EXECUTE FUNCTION log_audit_trail();

CREATE TRIGGER trigger_financial_plans_audit
AFTER INSERT OR UPDATE OR DELETE ON financial_plans
FOR EACH ROW
EXECUTE FUNCTION log_audit_trail();
```

---

## VIEWS MATERIALIZADAS

### 1. Dashboard Summary

```sql
CREATE MATERIALIZED VIEW mv_user_dashboard_summary AS
SELECT
    u.id AS user_id,
    u.email,
    u.full_name,

    -- Saldo em contas
    COALESCE(SUM(i.current_balance), 0) AS total_balance_institutions,

    -- Saldo em investimentos
    COALESCE((
        SELECT SUM(current_value)
        FROM investments
        WHERE user_id = u.id AND is_active = TRUE
    ), 0) AS total_balance_investments,

    -- Total geral
    COALESCE(SUM(i.current_balance), 0) + COALESCE((
        SELECT SUM(current_value)
        FROM investments
        WHERE user_id = u.id AND is_active = TRUE
    ), 0) AS total_net_worth,

    -- Transações do mês atual
    COALESCE((
        SELECT COUNT(*)
        FROM transactions
        WHERE user_id = u.id
          AND EXTRACT(YEAR FROM event_date) = EXTRACT(YEAR FROM CURRENT_DATE)
          AND EXTRACT(MONTH FROM event_date) = EXTRACT(MONTH FROM CURRENT_DATE)
    ), 0) AS current_month_transactions,

    -- Receitas do mês
    COALESCE((
        SELECT SUM(value)
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = u.id
          AND c.type = 'income'
          AND EXTRACT(YEAR FROM t.event_date) = EXTRACT(YEAR FROM CURRENT_DATE)
          AND EXTRACT(MONTH FROM t.event_date) = EXTRACT(MONTH FROM CURRENT_DATE)
          AND t.status = 'completed'
    ), 0) AS current_month_income,

    -- Despesas do mês
    COALESCE((
        SELECT ABS(SUM(value))
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = u.id
          AND c.type = 'expense'
          AND EXTRACT(YEAR FROM t.event_date) = EXTRACT(YEAR FROM CURRENT_DATE)
          AND EXTRACT(MONTH FROM t.event_date) = EXTRACT(MONTH FROM CURRENT_DATE)
          AND t.status = 'completed'
    ), 0) AS current_month_expenses,

    -- Última atualização
    CURRENT_TIMESTAMP AS last_updated

FROM users u
LEFT JOIN institutions i ON i.user_id = u.id AND i.is_active = TRUE
WHERE u.is_active = TRUE
GROUP BY u.id, u.email, u.full_name;

-- Índice para acesso rápido
CREATE UNIQUE INDEX idx_mv_dashboard_user ON mv_user_dashboard_summary(user_id);

-- Refresh automático (via cron ou celery)
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_user_dashboard_summary;
```

### 2. Category Spending Summary

```sql
CREATE MATERIALIZED VIEW mv_category_spending_summary AS
SELECT
    c.user_id,
    c.id AS category_id,
    c.name AS category_name,
    c.type AS category_type,
    EXTRACT(YEAR FROM t.event_date) AS year,
    EXTRACT(MONTH FROM t.event_date) AS month,
    COUNT(t.id) AS transaction_count,
    COALESCE(SUM(ABS(t.value)), 0) AS total_amount,
    COALESCE(AVG(ABS(t.value)), 0) AS avg_amount,
    MIN(t.event_date) AS first_transaction_date,
    MAX(t.event_date) AS last_transaction_date
FROM categories c
LEFT JOIN transactions t ON t.category_id = c.id AND t.status = 'completed'
WHERE c.parent_id IS NULL  -- Apenas categorias principais
GROUP BY c.user_id, c.id, c.name, c.type, EXTRACT(YEAR FROM t.event_date), EXTRACT(MONTH FROM t.event_date);

CREATE INDEX idx_mv_category_spending_user_year_month
    ON mv_category_spending_summary(user_id, year, month);
```

---

## SCRIPTS SQL

### Script de Seed (Dados Iniciais)

```sql
-- Script: seed_initial_data.sql
-- Descrição: Popula banco com dados iniciais

BEGIN;

-- Usuário admin padrão
INSERT INTO users (email, password_hash, full_name, role) VALUES
('admin@planner.local', '$2b$12$...', 'Administrador', 'admin');

-- Categorias padrão para o admin (user_id = 1)
INSERT INTO categories (user_id, name, type, color, icon) VALUES
-- Receitas
(1, 'Salário', 'income', '#4CAF50', 'attach_money'),
(1, 'Investimentos', 'income', '#2196F3', 'trending_up'),
(1, 'Renda Extra', 'income', '#00BCD4', 'work'),
(1, 'Venda de Ações', 'income', '#009688', 'show_chart'),

-- Despesas
(1, 'Alimentação', 'expense', '#FF5722', 'restaurant'),
(1, 'Transporte', 'expense', '#FF9800', 'directions_car'),
(1, 'Moradia', 'expense', '#795548', 'home'),
(1, 'Saúde', 'expense', '#E91E63', 'local_hospital'),
(1, 'Educação', 'expense', '#9C27B0', 'school'),
(1, 'Lazer', 'expense', '#673AB7', 'sports_esports'),
(1, 'Gastos Extras', 'expense', '#607D8B', 'shopping_cart');

-- Subcategorias de Alimentação
INSERT INTO categories (user_id, name, type, parent_id) VALUES
(1, 'Supermercado', 'expense', (SELECT id FROM categories WHERE name = 'Alimentação' AND user_id = 1)),
(1, 'Restaurante', 'expense', (SELECT id FROM categories WHERE name = 'Alimentação' AND user_id = 1)),
(1, 'Padaria', 'expense', (SELECT id FROM categories WHERE name = 'Alimentação' AND user_id = 1));

-- Subcategorias de Transporte
INSERT INTO categories (user_id, name, type, parent_id) VALUES
(1, 'Combustível', 'expense', (SELECT id FROM categories WHERE name = 'Transporte' AND user_id = 1)),
(1, 'Manutenção', 'expense', (SELECT id FROM categories WHERE name = 'Transporte' AND user_id = 1)),
(1, 'Transporte Público', 'expense', (SELECT id FROM categories WHERE name = 'Transporte' AND user_id = 1));

-- Instituição padrão
INSERT INTO institutions (user_id, name, type, partition, initial_balance) VALUES
(1, 'Banco do Brasil', 'bank', 'Principal', 0.00);

COMMIT;
```

### Script de Backup

```bash
#!/bin/bash
# backup.sh - Script de backup PostgreSQL

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="planner_financeiro"
DB_USER="planner_user"
FILENAME="$BACKUP_DIR/planner_backup_$DATE.sql"

# Criar backup
pg_dump -U $DB_USER -h localhost $DB_NAME > $FILENAME

# Comprimir
gzip $FILENAME

# Remover backups antigos (manter últimos 30 dias)
find $BACKUP_DIR -name "planner_backup_*.sql.gz" -mtime +30 -delete

echo "Backup concluído: $FILENAME.gz"
```

---

## MIGRATIONS ALEMBIC

### Estrutura de Migrations

```
backend/migrations/
├── versions/
│   ├── 001_initial_schema.py
│   ├── 002_add_audit_logs.py
│   ├── 003_add_user_sessions.py
│   └── ...
├── env.py
├── script.py.mako
└── README
```

### Migration 001: Initial Schema

```python
"""Initial schema - Create all tables

Revision ID: 001
Revises:
Create Date: 2025-12-18 16:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, INET

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(120), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(100), nullable=False),
        sa.Column('role', sa.String(20), nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_users_email'),
        sa.CheckConstraint("role IN ('admin', 'user')", name='ck_users_role')
    )
    op.create_index('idx_users_email', 'users', ['email'])

    # categories
    op.create_table(
        'categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('icon', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='fk_categories_user'),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ondelete='SET NULL', name='fk_categories_parent'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("type IN ('income', 'expense')", name='ck_categories_type'),
        sa.UniqueConstraint('user_id', 'name', 'parent_id', name='uq_categories_user_name_parent')
    )
    op.create_index('idx_categories_user', 'categories', ['user_id'])
    op.create_index('idx_categories_parent', 'categories', ['parent_id'])
    op.create_index('idx_categories_type', 'categories', ['type'])

    # institutions
    op.create_table(
        'institutions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('type', sa.String(20), nullable=False),
        sa.Column('partition', sa.String(50), nullable=False, server_default='Principal'),
        sa.Column('initial_balance', sa.Numeric(12, 2), nullable=False, server_default='0.00'),
        sa.Column('current_balance', sa.Numeric(12, 2), nullable=False, server_default='0.00'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE', name='fk_institutions_user'),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("type IN ('bank', 'brokerage', 'wallet')", name='ck_institutions_type'),
        sa.UniqueConstraint('user_id', 'name', 'partition', name='uq_institutions_user_name_partition')
    )
    op.create_index('idx_institutions_user', 'institutions', ['user_id'])

    # ... continuar com outras tabelas ...

def downgrade():
    # Reverter na ordem inversa
    op.drop_table('institutions')
    op.drop_table('categories')
    op.drop_table('users')
```

### Comandos Úteis

```bash
# Criar nova migration
flask db migrate -m "Add new table"

# Aplicar migrations
flask db upgrade

# Reverter última migration
flask db downgrade

# Ver histórico
flask db history

# Ver SQL sem executar
flask db upgrade --sql

# Criar migration vazia (para dados)
flask db revision -m "Seed initial data"
```

---

## COMANDOS PSQL ÚTEIS

```sql
-- Conectar ao banco
psql -U planner_user -d planner_financeiro

-- Listar tabelas
\dt

-- Descrever tabela
\d transactions

-- Ver tamanho das tabelas
SELECT
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Ver queries lentas (ativar pg_stat_statements antes)
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Vacuum e Analyze
VACUUM ANALYZE transactions;

-- Reindex
REINDEX TABLE transactions;
```

---

**Documento criado em:** 18/12/2025
**Versão:** 1.0
**Status:** Pronto para implementação
