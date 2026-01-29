# Claude Configuration — Flow Forecaster

This document primes Claude Code when collaborating on the Flow Forecaster codebase. Treat it as the source of truth for architectural intent, coding standards, and workflow expectations. Always read this file before generating code or plans.

---

## 1. Mission & Scope
- Build and maintain a Flask-based forecasting platform that ingests project/portfolio metrics, computes forecasts (Monte Carlo, Weibull, ML models), and exposes them via REST APIs, background jobs, and UI templates.
- Python 3.11 is the target runtime (`runtime.txt`). Keep the project deployable to Fly.io/Heroku-style environments (`Procfile`, `fly.toml`, `Dockerfile`).
- Claude must preserve backwards compatibility with existing endpoints, Celery tasks, CLI scripts, and analytical notebooks unless explicitly told otherwise.

## 2. Operating Principles
1. **TDD First** – Write or update tests *before* changing implementation. Use `pytest` with the existing suite (`tests/*.py`). Aim for focused unit tests plus integration coverage for public APIs, database flows, and Celery orchestration. **This is non-negotiable for production code.**
2. **Small, Verifiable Steps** – Prefer incremental changes that can ship independently. Document multi-step efforts in `PLAN.md` (create/update as needed) and cross-link from PRs. Review `PLAN.md` before starting new work.
3. **Readable, Observable Code** – Comply with PEP 8, `black`/`ruff` conventions, and include docstrings plus type hints on all new functions. Use the centralized logger utilities (`logger.py`) rather than ad‑hoc prints.
4. **Safety First** – Treat forecasting algorithms and statistical routines as critical paths. Guard against regressions with property-based or fixture-heavy tests when modifying stochastic code.
5. **Infrastructure Awareness** – Respect configuration boundaries defined in `config.py`, `.env` files, and deployment guides (`DEPLOY_*.md`). Never hardcode credentials or environment-specific paths.

## 3. Architectural Guardrails
### 3.1 Application Layers
- **Entry Points:** `app.py` (sync Flask), `app_async_endpoints.py` (async blueprint), `wsgi.py` (deployment). Keep these thin: wire dependencies, register blueprints, set up error handlers.
- **API Layer:** Routes live inside `api/` or `templates/` for UI. Use Blueprints, request validation, and JSON-only responses for APIs. Follow REST semantics; long-running work should hand off to Celery.
- **Domain / Services:** Forecasting logic resides in modules such as `monte_carlo.py`, `ml_forecaster.py`, `portfolio_*`, `dependency_analyzer.py`. Keep them framework-agnostic; prefer pure functions or small service classes with explicit inputs/outputs.
- **Persistence:** `database.py`, `models.py`, and migration scripts manage SQLAlchemy/Postgres/SQLite concerns. Encapsulate DB access inside repositories/helpers; avoid direct SQL in handlers unless absolutely necessary.
- **Background Tasks:** `celery_app.py` plus `tasks/` orchestrate async jobs. Tasks must be idempotent, retry-safe, and log progress for monitoring (`monitoring/`, `LOAD_TESTING_GUIDE.md`).

### 3.2 Cross-Cutting Concerns
- **Validation:** Reuse shared schemas/validators. For new payloads, add Marshmallow/Pydantic-style validators or explicit helper functions and cover them with tests.
- **Error Handling:** Leverage `error_handlers.py`. Raise domain-specific exceptions and translate them to HTTP errors centrally.
- **Performance:** Profiling and load guides (`PERFORMANCE_*.md`, `LOAD_TESTING_GUIDE.md`) exist—follow their recommendations before altering algorithmic complexity.
- **Observability:** Emit structured logs via `logger.py`. When touching Celery or async flows, add tracing hooks if missing.

## 4. Coding Standards
- Follow `requirements.txt` for allowed libraries. Ask before introducing heavy dependencies; prioritize stdlib, NumPy, Pandas, SciPy, and Flask ecosystem packages already in use.
- Prefer dataclasses or TypedDicts for structured data passed between layers.
- Keep modules focused (<500 lines when practical). Split out helpers to `app_package/` or `scripts/` rather than overloading entry-point files.
- Document non-trivial algorithms inline (short comments) and in the relevant guide files (e.g., `ASYNC_ARCHITECTURE_GUIDE.md`, `KFOLD_CV_IMPLEMENTATION.md`).
- Enforce deterministic behavior: seed RNGs (`numpy.random.default_rng`) within funcs/tests.

## 5. Testing Expectations
- Run `pytest -m "not slow"` for quick iterations; execute the full suite (including slow tests) before shipping significant work.
- Mirror new functionality with:
  - **Unit tests** near the target module (`test_*.py` already co-located).
  - **API tests** exercising Flask endpoints (`test_api_*.py`).
  - **Algorithm validation** comparing statistical expectations (`test_forecast_vs_actual.py`, `test_ml_validation.py`).
- Use fixtures/factories from `conftest.py`. Prefer deterministic sample datasets stored in `data/` or generated fixtures over inline random numbers.

## 6. Workflow for Agentic Collaboration
- **Claude <-> PLAN.md**: When executing multi-step efforts, outline tasks in `PLAN.md` (or create it if absent) before coding. Update status as work progresses.
- **Memory Bank Integration**: Sync with docs inside `docs/` or other `*_GUIDE.md` files for domain knowledge; surface deviations explicitly.
- **Handoffs**: Summaries in PR/commit messages must cite affected modules, new tests, and any migrations/runbooks touched.
- **Tooling**: Use `poetry` or `pip` consistent with `requirements*.txt`. Prefer built-in scripts over ad-hoc shell commands.

## 7. Common Scenarios & Rules
- **Adding Endpoints**: Create/extend a Blueprint, validate payloads, delegate heavy work to service layer, return JSON with ISO-8601 timestamps, and add tests + documentation (README or relevant guide).
- **Extending Forecast Algorithms**: Keep computational code independent of Flask. Parameterize new knobs, expose them via config, and document assumptions.
- **Database Migrations**: Scripts live under repo root (`migrate_*.py`, SQL files). Provide both forward and idempotent fixes; document manual steps in `MIGRATION_GUIDE.md`.
- **Background/Async Enhancements**: Modify `celery_app.py` responsibly, update retry/backoff policies, and ensure monitoring hooks are created/updated.
- **Monetization System**: Changes to `quotas.py`, `stripe_integration.py`, or trial logic MUST include tests. Never modify plan limits without updating tests. Stripe webhooks require mock testing. Document promotional periods in code comments with expiration dates.

## 8. Quality Gates Before Shipping
1. All new/changed behavior documented (README variants or targeted guide).
2. Tests updated and green locally.
3. Lint/type-check (ruff/mypy if configured) or at minimum `python -m compileall` for touched modules.
4. Deployment artifacts (`Procfile`, `fly.toml`, Dockerfiles) validated when relevant.

## 9. Asking for Clarification
If requirements conflict with this document, defer to the latest stakeholder instructions but note the deviation inside commits/PR descriptions and update CLAUDE.md when rules change.

---

Following these guardrails keeps Claude effective, ensures architectural consistency, and protects the reliability of the Flow Forecaster platform. Keep this file synchronized with evolving practices.
