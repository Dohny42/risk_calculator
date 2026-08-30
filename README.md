# Risk Calculator

A learning-oriented backend project that models a simplified risk / portfolio system.

The main goal is **not** to build a production-ready clearing system, but to practice real-world software engineering concepts in a realistic domain (positions, instruments, margin, stress testing).

This project is intentionally evolved **incrementally**. Every new feature is used as an opportunity to introduce or deepen architectural and engineering ideas.

---

## Current Goals

- Practice clean application architecture (domain, services, repositories, API)
- Learn proper testing strategies (domain, repository, API, fixtures, factories)
- Understand dependency injection and testability
- Work with relational data and SQL (joins, constraints, schema management)
- Make deliberate architectural decisions and document them
- Gradually introduce production-related practices

---

## What is already implemented

### Domain
- `Instrument` (master / static data: type, margin rate, name)
- `Position` and `Portfolio` (transactional data; positions reference instruments)
- Margin calculation from instrument margin rate
- Stress scenario **definitions** (`StressScenario`) and application (price shocks)
- Domain exception hierarchy (`DomainError`, unknown instrument/scenario, invalid position, duplicates, …)

### Architecture
- Clear separation of layers:
  - `domain/` – pure business logic + exceptions
  - `repositories/` – persistence (protocols + SQLite implementations)
  - `services/` – application use cases (portfolio, instruments, stress scenarios)
  - `api/` – FastAPI routes, schemas, dependencies, exception handlers
- Repository pattern + Dependency Inversion
- FastAPI dependency injection (`Depends`)
- Schema creation centralized (`create_schema()`), not buried inside each repository
- Domain errors mapped to HTTP status codes (400 / 404 / 409, …)

### Persistence
- SQLite
- Tables: `instruments`, `positions`, `stress_scenarios`
- Foreign key `positions.symbol` → `instruments.symbol`
- JOIN when loading a portfolio (positions + instrument attributes)
- Stress scenario shocks stored as JSON on the scenario row

### API
- Instruments: `POST /instruments`, `GET /instruments`, `GET /instruments/{symbol}`
- Portfolio: `GET /portfolio`, `POST /positions`
- Ad-hoc stress: `POST /stress` (optional raw `price_changes`)
- Stress scenarios (first-class):
  - `POST /stress-scenarios` (create; duplicate → 409)
  - `GET /stress-scenarios`, `GET /stress-scenarios/{name}`
  - `PUT /stress-scenarios/{name}` (update body without name in path-only identity)
  - `POST /stress-scenarios/{name}/apply` (apply stored scenario to current portfolio)
- Request validation (e.g. bounded `price_changes`, separate create vs update schemas)

### Testing
- Domain tests
- Repository tests (including JOIN and scenario persistence)
- API tests with `TestClient` + dependency overrides
- Factory-style fixtures for explicit setup (instruments, positions, scenarios)

### Configuration
- Central `Settings` via pydantic-settings
- Environment variables + optional `.env`
- Cached `get_settings()`; no hard-coded DB paths in wiring

---

## Mid-term plan (features + concepts)

The project will continue to grow in controlled steps. Each step should teach something concrete.

### Near-term features
- [x] Better error handling and domain exceptions
- [x] Configuration management (settings, environments)
- [x] More realistic stress testing (scenarios as first-class entities)
- [ ] Portfolio snapshots / history
- [ ] Multiple portfolios or accounts
- [ ] Richer instrument model (currency, multiplier, etc.)

### Engineering concepts to practice next
- More advanced SQL (subqueries, aggregations, indexes; optional normalized shock table)
- Richer test data management and reproducibility
- Observability basics (structured logging, request IDs, health checks)
- (Later) Database migrations — see note below

### Production-oriented topics (later increments)
These will be introduced gradually when the core application is stable enough:

- **Docker** – containerising the application and database
- **CI/CD** – running tests and checks automatically (GitHub Actions / similar)
- **Real databases** – moving from SQLite to PostgreSQL
- **Data injection & seeding** – realistic market / instrument data
- **Data analysis** – simple reporting, analytics endpoints or notebooks
- **Async** – async repositories / endpoints where it makes sense
- **Real-time aspects** – market data updates, streaming, or simple event-driven flows
- **Observability basics** – logging, structured logs, health checks

### Note on migrations (Alembic)
We skipped formal migrations so far in favour of `create_schema()`. That is fine while the schema is small and local-only. Migrations become important when:
- multiple environments must upgrade safely,
- you cannot wipe the DB,
- schema changes must be ordered, reversible, and reviewable in a team.

Worth adding after snapshots or before PostgreSQL/Docker — not before the domain is stable.

---

## Design principles we follow

1. **Incremental complexity**  
   We only add complexity when it teaches something useful.

2. **Explicit over clever**  
   Especially in tests and architecture.

3. **Domain first**  
   Business rules live in the domain layer, not in routes or SQL.

4. **Testability by design**  
   Dependency injection and clear boundaries are treated as first-class concerns.

5. **Documentation stays in sync**  
   When we add a significant feature or architectural change, this README (and eventually more detailed docs) should be updated.

---

## Project structure

```text
risk_calculator/
├── domain/                 # Business logic + exceptions
├── repositories/           # Persistence (protocols + SQLite)
├── services/               # Use cases
├── api/                    # FastAPI (routes, schemas, dependencies, handlers)
├── config.py               # Settings
├── main.py
tests/
├── domain/
├── repositories/
└── api/

---

## Install and run the project

This project is managed with [uv](https://docs.astral.sh/uv/) so please install it.

```bash
# Clone the project
git clone https://github.com/Dohny42/risk_calculator.git && cd risk_calculator

# Install dependencies
uv sync

# Run the API
uv run uvicorn risk_calculator.api.app:app --reload

# Tests
uv run pytest -v
```

---

## Configuration

Application settings are managed with `pydantic-settings` in `risk_calculator/config.py`.

### How it works

Settings are loaded from:

1. Environment variables
2. Optional `.env` file
3. Defaults in code

The `get_settings()` function is cached so the process uses a single settings object.

### Main settings

| Setting       | Env var       | Default         | Description                  |
|---------------|---------------|-----------------|------------------------------|
| `app_name`    | `APP_NAME`    | Risk Calculator API | API title                 |
| `db_path`     | `DB_PATH`     | `portfolio.db`  | SQLite database path         |

### Local development

Create a `.env` file in the project root (it is git-ignored):

```env
APP_NAME="Custom User Title"
DB_PATH=path/to/usr/db_file.db