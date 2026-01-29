# Codex Configuration — Flow Forecaster

This document primes OpenAI Codex agents (CLI, IDE integrations, MCP tools) for work on the Flow Forecaster Python/Flask project. Keep it synchronized with architectural decisions and follow it whenever Codex is invoked.

---

## 1. Setup & Authentication
1. **Prerequisites**  
   - Node.js ≥ 22, npm, Git ≥ 2.23, Python ≥ 3.10, pip.  
   - Valid OpenAI (or Azure OpenAI) credentials.  
   - Access to this Git repository (preferred via GitHub).
2. **Install Codex CLI**  
   ```bash
   npm install -g @openai/codex
   ```
3. **Authenticate**  
   Set `OPENAI_API_KEY` (or run `codex` once and follow the browser login). Never commit API keys.  
   ```bash
   export OPENAI_API_KEY="***"
   ```
4. **Repository Preparation**  
   ```bash
   cd flow-forecaster
   git init   # if needed
   codex      # launches interactive loop
   ```
5. **Optional Advanced Config**  
   - `~/.codex/config.toml` for Azure endpoints, default orgs, rate limits.  
   - Repository-level `AGENTS.md` / `CLAUDE.md` / `CODEX.md` for higher-order instructions (this file).  
   - Configure MCP resources (databases, memory bank docs) as needed for automation.

## 2. Operating Model
- Codex runs inside the repo to gather context (git history, docs, tests). Ensure `CODEX.md`, `CLAUDE.md`, and `PLAN.md` stay current so Codex understands constraints.
- Use Codex for scoped tasks: refactors, test authoring, bug fixes, API additions. Engineers remain responsible for architecture, review, and deployment decisions.
- Default workflow:
  1. **Plan** – Describe the feature/fix in natural language (CLI prompt, AGENTS.md, or PLAN.md).
  2. **Delegate** – Let Codex execute inside an isolated container. It will run installers (`pip install -r requirements.txt`, etc.) and local scripts as needed.
  3. **Review** – Codex outputs diffs or PRs. Human owners review, run tests, and merge once satisfied.

## 3. Tooling Expectations
- **Version Control**: Every Codex session assumes a clean git tree. Commit early, branch often, and tie Codex tasks to branches/PRs.
- **Testing**: Codex must run `pytest` (respecting markers like `not slow`) before delivering substantive changes. For Flask endpoints or services, request Codex to add/modify tests in `tests/`.
- **Linters/Formatters**: Follow `black` style, `ruff` linting, and type hints when touching new modules. Codex should auto-format where possible.
- **Dependency Management**: Use `pip` with `requirements*.txt`. Introduce new packages only when justified; update docs and lockfiles accordingly.

## 4. Python/Flask Architectural Guardrails
1. **App Structure**  
   - Entry points: `app.py`, `app_async_endpoints.py`, `wsgi.py`. Keep them thin; register blueprints, config, and error handlers.  
   - APIs: Use Flask Blueprints under `api/`. Validate requests, return JSON, handle errors via `error_handlers.py`.  
   - Services/Domain: Forecasting logic (e.g., `monte_carlo.py`, `ml_forecaster.py`, `portfolio_*`) stays framework-agnostic with pure functions or lightweight service classes.  
   - Persistence: Encapsulate DB access via SQLAlchemy helpers (`database.py`, `models.py`). Avoid raw SQL in route handlers.  
   - Background Work: Celery tasks in `celery_app.py` and `tasks/` must be idempotent, logged, and covered by tests.
2. **Coding Standards**  
   - PEP 8, docstrings, type annotations on public APIs.  
   - Deterministic randomness (seeded RNG) for statistical routines.  
   - Structured logging via `logger.py`; no stray prints.  
   - Keep modules cohesive (<500 LOC where practical); split helpers into dedicated files.
3. **Performance & Reliability**  
   - Follow guidance from `PERFORMANCE_*.md`, `ASYNC_ARCHITECTURE_GUIDE.md`, `LOAD_TESTING_GUIDE.md`.  
   - When changing algorithms, update relevant documentation and ensure regression coverage in `test_*` modules.  
   - Validate migrations/scripts via `MIGRATION_GUIDE.md`.

## 5. Integration with Agentic Assets
- **AGENTS.md / CLAUDE.md / CODEX.md**: Keep instructions in sync; reference this file inside Codex prompts to inherit constraints.  
- **PLAN.md**: For multi-step tasks, Codex should create/update plans, mark progress, and cite them in PR summaries.  
- **Memory Bank (`docs/`, `*_GUIDE.md`)**: Codex must consult domain docs when implementing forecasts, portfolio analytics, or deployment scripts. Link any deviations in commits/PRs.

## 6. Typical Codex Tasks
- **API Enhancements**: Generate or update Flask routes, add schema validation, extend Swagger-like docs (if present), and supply tests in `test_api_*.py`.  
- **Algorithm Updates**: Modify statistical models in isolated modules, add configuration knobs, document in README/guide, and extend `test_forecast_vs_actual.py` or similar.  
- **Data Pipelining**: Adjust Celery workflows, add new tasks, and ensure monitoring/logging is intact.  
- **Refactoring & Cleanup**: Apply best practices (dependency inversion, modularization) while preserving behavior; Codex should run targeted tests before finalizing diffs.

## 7. Quality Gate Checklist
1. Tests written/updated and executed (`pytest`, targeted scripts).  
2. Linters/formatters applied (black, ruff).  
3. Docs updated (README variants, guide files, this document if rules changed).  
4. Deployment artifacts validated when touched (`Dockerfile`, `Procfile`, `fly.toml`).  
5. Git status clean; commits reference associated tasks/issues.

## 8. Security & Compliance
- Never echo secrets to logs or repository. Use environment variables and `.env` patterns already established.  
- Respect sandbox boundaries; destructive commands (e.g., database resets) require explicit human approval.  
- Follow data governance rules for any attached MCP resources.

## 9. Escalation & Clarification
- When instructions conflict, prioritize latest stakeholder guidance but document the deviation and update `CODEX.md`.  
- If Codex cannot fulfill a request due to missing context or permissions, it should pause and prompt the human operator.

---

Adhering to these guidelines keeps Codex aligned with our Python/Flask architecture, enabling safe, test-driven, and reviewable contributions across the Flow Forecaster platform.
