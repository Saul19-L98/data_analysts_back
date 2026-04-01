# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

FastAPI backend for data analysis with AWS Bedrock Agent integration. Users upload spreadsheets (CSV/XLSX), the service extracts data profiles (schema, dtypes, statistics via pandas), sends them to a Bedrock Agent, and returns AI-powered chart suggestions formatted for shadcn/recharts components.

## Common Commands

```bash
# Install dependencies
uv sync

# Run dev server (port 8000, auto-reload)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/test_file_parser.py

# Run a specific test
uv run pytest tests/test_file_parser.py::test_name -v

# Formatting and linting
uv run black app/ tests/
uv run isort app/ tests/
uv run flake8 app/ tests/
uv run mypy app/

# Docker
docker compose up -d              # Production (port 8080)
docker compose --profile dev up -d api-dev  # Dev with hot reload (port 8001)
```

## Architecture

MVC-style layered architecture. Controllers never contain business logic or DB access; services orchestrate business logic; no database — data comes from uploaded files and AWS Bedrock.

**Request flow for `/api/v1/ingest` (POST, multipart/form-data):**
1. `controllers/v1/ingest.py` — validates input, checks file size/type, calls service
2. `services/ingest_service.py` — orchestrates the full pipeline:
   - `FileParserService` parses CSV/XLSX into a pandas DataFrame
   - `DataAnalyzerService` extracts schema, dtypes, describe() stats
   - `BedrockService` sends formatted prompt to AWS Bedrock Agent and parses JSON response (4-strategy fallback parser for truncated responses)
   - `chart_formatting.py` utility extracts/validates/filters chart suggestions from agent reply
3. Response includes data profile + pre-formatted `chart_transform_request` ready for the charts endpoint

**Request flow for `/api/v1/charts/transform` (POST, JSON):**
1. `controllers/v1/charts.py` — receives chart suggestions + optional dataset
2. `services/chart_transform_service.py` — transforms agent chart specs into shadcn format:
   - Applies filters, aggregations (with pandas), sorting on the dataset
   - Builds `chartConfig` with shadcn CSS variable colors (`hsl(var(--chart-N))`)
   - Returns data ready for recharts components

**Key design decisions:**
- `BedrockService` uses lazy-loaded boto3 client via `@property`
- Settings use pydantic-settings with `@lru_cache` singleton (`get_settings()`)
- Custom exception hierarchy rooted in `AppException` with HTTP status codes (see `core/exceptions.py`)
- `DEV_MODE=dev` env var includes raw agent reply in responses for debugging
- Chart types are restricted to shadcn/recharts compatible: line, bar, area, pie, donut, scatter, radar, radial
- Aggregation function names are mapped from common aliases to pandas names (avg->mean, stdev->std)

## Configuration

Environment variables loaded from `.env` via pydantic-settings. See `.env.example` for all options. Required: `AWS_REGION`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`. The `BEDROCK_AGENT_ID` and `BEDROCK_AGENT_ALIAS_ID` are passed per-request in the API call.

## Testing

Tests use `pytest` with `pytest-asyncio` (mode: auto). The `conftest.py` sets dummy AWS env vars for the test session. Bedrock is mocked via `mock_bedrock_client` fixture. Use `httpx.AsyncClient` or `fastapi.testclient.TestClient` for API tests.

## Code Style

- Black (line-length 100, target py311) + isort (profile: black) + flake8 + mypy (disallow_untyped_defs)
- Python 3.11+ type hints throughout (use `str | None` not `Optional[str]`)
- Spanish user-facing messages in API responses (e.g., "Archivo analizado con exito", "Graficos transformados exitosamente")

## Docker

Multi-stage Dockerfile: builder stage installs deps with uv, runtime stage uses slim Python 3.13. Production runs on port 8080 (AWS App Runner compatible) as non-root `appuser`.
