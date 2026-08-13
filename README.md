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
- `Instrument` (master / static data)
- `Position` and `Portfolio` (transactional data)
- Margin calculation based on instrument margin rate
- Stress scenario application (price shocks)

### Architecture
- Clear separation of layers:
  - `domain/` – pure business logic
  - `repositories/` – persistence (protocols + SQLite implementations)
  - `services/` – application use cases
  - `api/` – FastAPI routes, schemas, dependencies
- Repository pattern + Dependency Inversion
- FastAPI dependency injection (`Depends`)
- Schema creation separated from repositories

### Persistence
- SQLite
- Two main tables: `instruments` and `positions`
- Foreign key relationship + JOIN when loading a portfolio
- Central `create_schema()` function

### API
- `POST /instruments`
- `GET /instruments`
- `GET /instruments/{symbol}`
- `GET /portfolio`
- `POST /positions`
- `POST /stress`

### Testing
- Domain tests
- Repository tests (including JOIN behaviour)
- API tests with `TestClient` + dependency overrides
- Factory-style fixtures for explicit test setup

---

## Mid-term plan (features + concepts)

The project will continue to grow in controlled steps. Each step should teach something concrete.

### Near-term features
- Better error handling and domain exceptions
- Portfolio snapshots / history
- Multiple portfolios or accounts
- Richer instrument model (currency, multiplier, etc.)
- More realistic stress testing (scenarios as first-class entities)

### Engineering concepts to practice next
- More advanced SQL (joins, subqueries, aggregations, indexes)
- Richer test data management and reproducibility
- Configuration management (settings, environments)

### Production-oriented topics (later increments)
These will be introduced gradually when the core application is stable enough:

- **Docker** – containerising the application and database
- **CI/CD** – running tests and checks automatically (GitHub Actions / similar)
- **Real databases** – moving from SQLite to PostgreSQL
- **Data injection & seeding** – realistic market / instrument data
- **Data analysis** – simple reporting, analytics endpoints or notebooks
- **Async** – async repositories / endpoints where it makes sense
- **Real-time aspects** – market data updates, streaming, or simple event-driven flows
- **Observability basics** - logging, structured logs, health checks

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
├── domain/                 # Business logic
├── repositories/           # Persistence (protocols + SQLite)
├── services/               # Use cases
├── api/                    # FastAPI (routes, schemas, dependencies)
├── main.py
tests/
├── domain/
├── repositories/
└── api/
```

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