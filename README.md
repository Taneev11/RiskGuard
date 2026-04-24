# RiskGuard

RiskGuard is a lightweight portfolio compliance and risk assessment tool.
It includes:

- A FastAPI backend for file upload, risk calculations, and violation persistence
- A Streamlit frontend for interactive portfolio uploads and audit visibility
- A PostgreSQL schema for trades and compliance violations

## Learning Scope and AI Assistance

This project is a learning-focused prototype built to practice the Python backend stack
(FastAPI, Polars, asyncpg, Streamlit, and PostgreSQL) end to end.

The finance/risk domain is used as sample context for building and integrating APIs,
data processing, and persistence workflows. Some implementation ideas were AI-assisted,
while the final integration, structure, and validation were completed as part of the
learning process.

## What It Does

Given a portfolio file (`.csv` or `.json`) with holdings, RiskGuard:

1. Enriches holdings with market data (`current_price`, `sector`)
2. Computes market value and portfolio/sector weights
3. Runs rule checks:
   - Sector concentration (`> 25%`)
   - Per-position liquidity cap (`market_value > 1,000,000`)
   - Wash-sale signal based on recent BUY/SELL history in DB
4. Computes annualized volatility by ticker from historical prices
5. Returns a risk report and stores violations for audit trail

## Tech Stack

- Python 3.12+
- FastAPI
- Streamlit
- Polars
- asyncpg
- PostgreSQL
- uv (dependency/runtime management)

## Project Structure

- `src/backend/main.py` - API endpoints (`/upload-portfolio`, `/violations`)
- `src/backend/risk_engine.py` - enrichment, volatility, and risk checks
- `src/backend/db.py` - PostgreSQL access and persistence helpers
- `src/frontend/app.py` - Streamlit UI
- `src/backend/data/` - sample market and price-history datasets
- `src/sql/schema.sql` - DB schema

## Prerequisites

1. Python 3.12 or newer
2. PostgreSQL running locally (or reachable remotely)
3. `uv` installed

Install `uv` (if needed):

```bash
pip install uv
```

## Setup

From the project root:

```bash
uv sync
```

Create the database and apply schema:

```bash
# Example with local postgres
createdb riskguard
psql -d riskguard -f src/sql/schema.sql
```

Set environment variable (optional if using the default in code):

```bash
export DATABASE_URL="postgresql://rguser:riskguard@localhost/riskguard"
```

## Run the Application

Start backend API:

```bash
uv run fastapi dev src/backend/main.py
```

Start frontend in a separate terminal:

```bash
uv run streamlit run src/frontend/app.py
```

Frontend default URL: `http://localhost:8501`  
Backend default URL: `http://localhost:8000`

## Portfolio Input Format

Required columns/fields:

- `ticker` (string)
- `quantity` (integer)
- `avg_purchase_price` (number)

Optional:

- `trade_type` (`BUY` or `SELL`, defaults to `BUY`)

## API Endpoints

### `POST /upload-portfolio`

Accepts a multipart file (`csv` or `json`) and returns:

- `total_value`
- `volatility_by_ticker`
- `sector_weights`
- `violations`

### `GET /violations`

Returns the most recent stored violations (default limit: 50).

## Current Constraints and Known Gaps

- No automated tests are present yet (`pytest` currently reports no tests).
- Error handling around DB connectivity is minimal.
- File validation checks required columns but does not fully validate datatypes/values.
- The risk engine currently depends on static CSV data in `src/backend/data`.
- `tool.uv.dev-dependencies` is deprecated; move to dependency groups in `pyproject.toml`.

## Suggested Next Improvements

1. Add backend tests for upload parsing, risk checks, and DB interactions
2. Add startup health checks and clearer DB error responses
3. Introduce input schema validation (type/range checks)
4. Add containerized local stack (`docker-compose`) for app + Postgres
5. Add CI to run linting and tests
