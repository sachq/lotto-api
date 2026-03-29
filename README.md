# Lotto API

A FastAPI application that tracks Powerball and Megamillion lottery draws and generates frequency-weighted number predictions.

> **Disclaimer:** This is a fun/educational project. The predictions generated are based on historical frequency analysis and have absolutely no connection to the actual lottery random number generators (RNGs). Lottery draws are independent random events — past results do not influence future outcomes. Please play responsibly.

## Quick Start (Docker)

```bash
cp .env.template .env
# Edit .env with your credentials
docker compose up --build
```

This starts PostgreSQL, runs migrations, populates lottery data, and serves the API at `http://localhost`.

## Manual Setup

### Prerequisites

- Python 3.11
- PostgreSQL
- Pipenv

### 1. Install dependencies

```bash
pipenv install
```

### 2. Configure environment

Create a `.env` file in the project root:

```env
POSTGRES_DB=lotto
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB_URI=postgresql://your_user:your_password@localhost:5432/lotto
DEBUG=True
PYTHONPATH=/path/to/lotto-api
```

### 3. Start PostgreSQL

Use an existing PostgreSQL instance and update `POSTGRES_DB_URI` accordingly.

### 4. Run database migrations

```bash
cd app
alembic upgrade head
```

### 5. Populate lottery data

```bash
pipenv run python -m app.scripts.lotto_data
```

This fetches historical Powerball and Megamillion draw data from the NY Open Data API.

### 6. Start the application

```bash
pipenv run uvicorn app:app --reload
```

The API will be available at `http://localhost:8000`.

## API Endpoints

Base URL: `/api/v1`

### Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/summary/draws` | Get all draws with pagination |
| `GET` | `/api/v1/summary/draws/{draw_date}` | Get draws for a specific date |

**Query parameters for `/draws`:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `per_page` | int | 50 | Items per page (1-500) |

**Example response:**

```json
{
  "items": [{ "id": 1, "draw_date": "2026-03-25", "A": 7, ... }],
  "page": 1,
  "per_page": 50,
  "total_items": 5407,
  "total_pages": 109
}
```

### Prediction

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/prediction/{lotto_type}` | Generate a frequency-weighted prediction |

**Path parameter:** `lotto_type` — `powerball` or `megamillion`

**Query parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `draw_date` | date | next draw day | Specific draw date (must be a valid draw day) |
| `count` | int | 1 | Number of combinations to generate (1-10) |

**Example response:**

```json
{
  "lotto_type": "Powerball",
  "draw_date": "2026-03-28",
  "combinations": [
    {
      "numbers": [7, 19, 34, 52, 61],
      "bonus_number": 14
    },
    {
      "numbers": [3, 22, 38, 45, 67],
      "bonus_number": 9
    }
  ]
}
```

Predictions are deterministic per draw date — the same date always returns the same combinations. Numbers are weighted by historical frequency from past draws. Passing an invalid draw day (e.g. a Thursday for Powerball) returns a 400 error.

**Draw schedules:**

| Lottery | Draw Days |
|---------|-----------|
| Powerball | Monday, Wednesday, Saturday |
| Megamillion | Tuesday, Friday |

## MCP Server

The project includes an MCP (Model Context Protocol) server that exposes lottery tools for AI assistants like Claude.

### Available Tools

| Tool | Description |
|------|-------------|
| `get_draws` | Get paginated historical draws |
| `get_draws_by_date` | Get draws for a specific date |
| `get_draws_by_type` | Get draws filtered by lottery type |
| `get_draws_in_range` | Get draws within a date range |
| `generate_prediction` | Generate frequency-weighted predictions |
| `get_next_draw_date` | Get the next upcoming draw date |
| `fetch_latest_data` | Ingest latest data from NY Open Data |
| `get_number_frequencies` | Get frequency counts for all numbers |
| `get_hot_cold_numbers` | Get most/least frequently drawn numbers |
| `get_draw_stats` | Get summary statistics about stored draws |

### Connecting to the MCP Server

The MCP server is mounted inside the FastAPI app at `/lotto-mcp` using Streamable HTTP transport. It starts automatically with the API -- no separate service needed.

**Remote (Streamable HTTP):**

```json
{
  "mcpServers": {
    "lotto": {
      "type": "streamable-http",
      "url": "http://localhost/lotto-mcp"
    }
  }
}
```

**Local (stdio):**

```bash
PYTHONPATH=. pipenv run python -m app.mcp.server
```

```json
{
  "mcpServers": {
    "lotto": {
      "command": "pipenv",
      "args": ["run", "python", "-m", "app.mcp.server"],
      "cwd": "/path/to/lotto-api"
    }
  }
}
```

## Data Source

Historical draw data is sourced from the [NY Open Data](https://data.ny.gov) portal:

- [Powerball](https://data.ny.gov/api/views/d6yy-54nr)
- [Mega Millions](https://data.ny.gov/api/views/5xaw-6ayf)
