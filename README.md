# Lotto API

A FastAPI application that tracks Powerball and Megamillion lottery draws and generates frequency-weighted number predictions.

> **Disclaimer:** This is a fun/educational project. The predictions generated are based on historical frequency analysis and have absolutely no connection to the actual lottery random number generators (RNGs). Lottery draws are independent random events — past results do not influence future outcomes. Please play responsibly.

## Prerequisites

- Python 3.11
- PostgreSQL
- Pipenv
- Docker (optional, for PostgreSQL)

## Setup

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

Using Docker:

```bash
docker-compose up -d
```

Or use an existing PostgreSQL instance and update `POSTGRES_DB_URI` accordingly.

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
| `skip` | int | 0 | Number of records to skip |
| `limit` | int | 100 | Max records to return (1-1000) |

### Prediction

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/prediction/{lotto_type}` | Generate a frequency-weighted prediction |

**Path parameter:** `lotto_type` — `powerball` or `megamillion`

**Example response:**

```json
{
  "lotto_type": "Powerball",
  "numbers": [7, 19, 34, 52, 61],
  "bonus_number": 14,
  "next_draw_date": "2026-03-29"
}
```

Predictions are weighted by historical number frequency — numbers that have appeared more often in past draws have a higher chance of being selected.

**Draw schedules:**

| Lottery | Draw Days |
|---------|-----------|
| Powerball | Monday, Wednesday, Saturday |
| Megamillion | Tuesday, Friday |

## Data Source

Historical draw data is sourced from the [NY Open Data](https://data.ny.gov) portal:

- [Powerball](https://data.ny.gov/api/views/d6yy-54nr)
- [Mega Millions](https://data.ny.gov/api/views/5xaw-6ayf)
