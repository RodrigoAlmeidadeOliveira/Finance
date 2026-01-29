# Backend - Planner Financeiro (OFX + ML)

## Pré-requisitos
- Python 3.11 (recomendado)
- Postgres em execução (ex.: `planner_financeiro` com usuário `planner_user`)
- Ambiente virtual ativo (ex.: `conda activate finance311`)

## Instalação
```bash
pip install -r requirements.txt
```

## Configuração
Defina a URL do banco (ajuste usuário/senha/host conforme seu ambiente):
```bash
export DATABASE_URL=postgresql://planner_user:sua_senha@localhost:5432/planner_financeiro
```

Outras variáveis (opcionais) seguem o `.env.example`.

## Migrações
```bash
cd backend
alembic upgrade head
```
Ou da raiz: `alembic -c backend/alembic.ini upgrade head`.

## Executar API
```bash
cd backend
export FLASK_APP=app:create_app
flask run --debug
```
Endpoints principais:
- `POST /api/imports/ofx` — upload de arquivo OFX (`file`, `user_id`)
- `GET /api/imports` — lista de lotes
- `GET /api/imports/<batch_id>/pending` — transações pendentes
- `POST /api/imports/<batch_id>/pending/<tx_id>/review` — revisa/atualiza categoria

## Testes
```bash
python -m pytest backend/tests
```
Em CI/local, garanta dependências instaladas e `DATABASE_URL` válido (tests de integração usam SQLite in-memory).
