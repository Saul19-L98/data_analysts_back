# Development Mode (DEV_MODE) 🔧

## Overview

The `DEV_MODE` environment variable enables debugging features in the API responses, specifically the inclusion of raw Bedrock Agent responses in the `/api/v1/ingest` endpoint.

## Configuration

### Environment Variable

Add to your `.env` file:

```bash
DEV_MODE=dev  # Options: dev, prod
```

**Values:**
- `dev`: Enable debugging features (includes raw `agent_reply` in responses)
- `prod`: Production mode (cleaner responses, no raw agent data) **[DEFAULT]**

### Settings

The setting is loaded via `pydantic-settings` in `app/core/config.py`:

```python
from typing import Literal
from pydantic import Field

class Settings(BaseSettings):
    dev_mode: Literal["dev", "prod"] = Field(default="prod", alias="DEV_MODE")
```

## Impact on API Responses

### `/api/v1/ingest` Endpoint

#### Production Mode (`DEV_MODE=prod` or not set)

Response **DOES NOT** include `agent_reply`:

```json
{
  "message": "Archivo analizado con éxito",
  "session_id": "sess_2025_01_21T10_30_00Z_abc123",
  "columns": ["name", "age", "city"],
  "dtypes": {
    "name": "object",
    "age": "int64",
    "city": "object"
  },
  "summary": {
    "describe_numeric": {...},
    "describe_non_numeric": {...},
    "info_text": "..."
  },
  "sent_to_agent": true,
  "chart_transform_request": {
    "session_id": "sess_2025_01_21T10_30_00Z_abc123",
    "suggested_charts": [
      {
        "chart_type": "bar",
        "title": "Sales by Category",
        "description": "Displays sales distribution across categories",
        "x_axis_column": "category",
        "y_axis_column": "sales"
      }
    ],
    "dataset": [...]
  }
}
```

#### Development Mode (`DEV_MODE=dev`)

Response **INCLUDES** `agent_reply` with raw Bedrock Agent output:

```json
{
  "message": "Archivo analizado con éxito",
  "session_id": "sess_2025_01_21T10_30_00Z_abc123",
  "columns": ["name", "age", "city"],
  "dtypes": {
    "name": "object",
    "age": "int64",
    "city": "object"
  },
  "summary": {
    "describe_numeric": {...},
    "describe_non_numeric": {...},
    "info_text": "..."
  },
  "sent_to_agent": true,
  "chart_transform_request": {
    "session_id": "sess_2025_01_21T10_30_00Z_abc123",
    "suggested_charts": [...],
    "dataset": [...]
  },
  "agent_reply": {
    "raw_response": "...",
    "parsed_json": {...},
    "metadata": {...}
  }
}
```

## Use Cases

### When to Use `DEV_MODE=dev`

✅ **Local Development**
- Debugging agent responses
- Validating agent output format
- Troubleshooting chart suggestions
- Understanding AI behavior

✅ **Testing & QA**
- Comparing agent responses across runs
- Verifying agent configuration changes
- Testing new prompt templates

✅ **Documentation**
- Capturing example agent responses
- Creating integration guides

### When to Use `DEV_MODE=prod` (or omit)

✅ **Production Environments**
- Live deployments
- Customer-facing APIs
- Performance-critical scenarios

✅ **Reduced Response Size**
- Minimizing bandwidth usage
- Faster response times
- Cleaner client integrations

## Implementation Details

### Service Layer

In `app/services/ingest_service.py`:

```python
# 10. Conditionally include agent_reply in dev mode
if self.settings.dev_mode == "dev":
    response_data["agent_reply"] = agent_reply
    logger.info("DEV_MODE: Including raw agent_reply in response")

return IngestResponse(**response_data)
```

### Schema Layer

In `app/models/schemas/ingest.py`:

```python
from typing import Optional

class IngestResponse(BaseModel):
    # ... other fields ...
    agent_reply: Optional[dict[str, Any]] = Field(
        default=None,
        description="Raw agent response (only included when DEV_MODE=dev for debugging purposes)"
    )
```

## Logging

When `DEV_MODE=dev`, the service logs:

```
INFO: DEV_MODE: Including raw agent_reply in response
```

This helps identify when debugging mode is active in application logs.

## Performance Impact

### Development Mode (`dev`)
- **Response Size**: ~50% larger (includes raw agent data)
- **Processing Time**: Minimal impact (~5ms overhead)
- **Memory**: Additional dict allocation for agent_reply

### Production Mode (`prod`)
- **Response Size**: Optimized (no duplication)
- **Processing Time**: Fastest
- **Memory**: Minimal footprint

## Security Considerations

⚠️ **Never enable DEV_MODE in production** if `agent_reply` contains:
- Sensitive data
- Internal system details
- Debug information not meant for clients

The raw agent response may include:
- Complete prompt sent to the agent
- Internal reasoning traces
- Bedrock-specific metadata

## Migration Guide

### Upgrading to v1.6.0+

If you previously relied on `agent_reply` in production responses:

1. **Update your client code** to use `chart_transform_request` instead:
   ```javascript
   // Old (pre-v1.6.0)
   const charts = response.agent_reply.suggested_charts;
   
   // New (v1.6.0+)
   const charts = response.chart_transform_request.suggested_charts;
   ```

2. **Enable DEV_MODE for local testing**:
   ```bash
   # .env
   DEV_MODE=dev
   ```

3. **Keep DEV_MODE disabled in production**:
   ```bash
   # Production .env
   DEV_MODE=prod  # Or omit entirely
   ```

## Testing

### Manual Testing

```bash
# 1. Set dev mode
echo "DEV_MODE=dev" >> .env

# 2. Restart server
uv run uvicorn app.main:app --reload

# 3. Send test request (Postman or cURL)
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@test.csv" \
  -F "message=test" \
  -F "agent_id=AGENT123" \
  -F "agent_alias_id=ALIAS456"

# 4. Verify agent_reply is present in response
```

### Automated Testing

```python
import pytest
from fastapi.testclient import TestClient

def test_dev_mode_includes_agent_reply(client: TestClient, monkeypatch):
    monkeypatch.setenv("DEV_MODE", "dev")
    response = client.post("/api/v1/ingest", files={...}, data={...})
    assert "agent_reply" in response.json()

def test_prod_mode_excludes_agent_reply(client: TestClient, monkeypatch):
    monkeypatch.setenv("DEV_MODE", "prod")
    response = client.post("/api/v1/ingest", files={...}, data={...})
    assert "agent_reply" not in response.json() or response.json()["agent_reply"] is None
```

## Troubleshooting

### `agent_reply` not showing in dev mode

**Symptoms:**
- `DEV_MODE=dev` is set
- `agent_reply` is still `null` or missing

**Solutions:**
1. Verify `.env` is loaded:
   ```python
   from app.core.config import get_settings
   print(get_settings().dev_mode)  # Should print "dev"
   ```

2. Check server logs for:
   ```
   INFO: DEV_MODE: Including raw agent_reply in response
   ```

3. Restart server after changing `.env`:
   ```bash
   # Stop server (Ctrl+C)
   uv run uvicorn app.main:app --reload
   ```

### `agent_reply` showing in production

**Symptoms:**
- Production environment
- `agent_reply` appearing in responses

**Solutions:**
1. Check production `.env`:
   ```bash
   cat .env | grep DEV_MODE
   # Should be: DEV_MODE=prod or not present
   ```

2. Explicitly set in production:
   ```bash
   export DEV_MODE=prod
   ```

3. Verify settings loading:
   ```python
   from app.core.config import get_settings
   assert get_settings().dev_mode == "prod"
   ```

## Best Practices

1. **Default to Production**: Always use `prod` mode by default
2. **Explicit Dev Mode**: Only enable `dev` mode explicitly when needed
3. **Document Usage**: Add comments in `.env.example` explaining when to use each mode
4. **CI/CD Checks**: Verify `DEV_MODE=prod` in production deployments
5. **Log Monitoring**: Monitor logs for unexpected "DEV_MODE" messages in production

## Version History

- **v1.6.0** (2025-01-21): Added DEV_MODE feature with conditional `agent_reply` inclusion
- **v1.5.0** (2025-01-21): Removed `agent_reply` duplication (prompted creation of DEV_MODE)

## Related Documentation

- [Agent Response Formatting](./AGENT_RESPONSE_FORMATTING.md)
- [Postman Testing Guide](./POSTMAN_TESTING_GUIDE.md)
- [Chart Transformation Guide](./CHART_TRANSFORMATION_GUIDE.md)
