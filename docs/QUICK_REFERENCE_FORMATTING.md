# 🚀 Quick Reference: Agent Response Formatting

## 📋 One-Liner Commands

```bash
# Format agent response (CLI)
uv run python format_agent_response.py response.json

# Run all tests
uv run python test_chart_formatting.py

# Test with pytest
uv run pytest tests/ -v
```

---

## 🐍 Code Snippets

### Basic Usage
```python
from app.utils.chart_formatting import format_chart_transform_request

# Format in one line
request = format_chart_transform_request(
    session_id=response["session_id"],
    agent_reply=response["agent_reply"],
    dataset=response["dataset"],
    filter_unsupported=True
)
```

### Validate Charts
```python
from app.utils.chart_formatting import validate_all_chart_suggestions

errors = validate_all_chart_suggestions(charts)
if errors:
    print(f"❌ {len(errors)} validation errors")
```

### Filter Unsupported
```python
from app.utils.chart_formatting import filter_supported_charts

valid, skipped = filter_supported_charts(charts)
print(f"✅ {len(valid)} valid | ❌ {len(skipped)} skipped")
```

---

## ✅ Supported Chart Types

```python
SUPPORTED = {
    "line", "bar", "area", "pie", 
    "donut", "scatter", "radar", "radial"
}
```

---

## 📊 Request Structure

```json
{
  "session_id": "sess_xxx",
  "suggested_charts": [
    {
      "title": "Chart Title",
      "chart_type": "line",
      "parameters": {
        "x_axis": "date",
        "y_axis": "sales"
      }
    }
  ],
  "dataset": [...]
}
```

---

## 🧪 Test Command

```bash
# Quick test
uv run python -c "
from app.utils.chart_formatting import format_chart_transform_request
import json

result = format_chart_transform_request(
    session_id='test',
    agent_reply={'suggested_charts': [
        {'title': 'Test', 'chart_type': 'line', 'parameters': {}}
    ]},
    dataset=[]
)
print(json.dumps(result, indent=2))
"
```

---

## 🔍 Files Created

| File | Purpose |
|------|---------|
| `app/utils/chart_formatting.py` | Core utility functions |
| `format_agent_response.py` | CLI tool for formatting |
| `test_chart_formatting.py` | Test suite |
| `docs/AGENT_RESPONSE_FORMATTING.md` | Full documentation |
| `test_formatted_request.json` | Example output |
| `test_chart_transform_request.json` | Example request |

---

## 🎯 Common Patterns

### Pattern 1: CLI Workflow
```bash
# 1. Get response from ingest
curl -X POST http://localhost:8000/api/v1/ingest -F "file=@data.csv" > response.json

# 2. Format it
uv run python format_agent_response.py response.json request.json

# 3. Send to transform
curl -X POST http://localhost:8000/api/v1/charts/transform -d @request.json
```

### Pattern 2: Python Workflow
```python
# 1. Upload and ingest
ingest_response = requests.post(url, files={"file": file}).json()

# 2. Format
from app.utils.chart_formatting import format_chart_transform_request
request = format_chart_transform_request(
    session_id=ingest_response["session_id"],
    agent_reply=ingest_response["agent_reply"],
    dataset=ingest_response["dataset"]
)

# 3. Transform
charts = requests.post(transform_url, json=request).json()
```

### Pattern 3: Service Integration
```python
# In IngestService
from app.utils.chart_formatting import format_chart_transform_request

class IngestService:
    async def handle_upload(self, file):
        # ... get agent response ...
        
        # Auto-format
        chart_request = format_chart_transform_request(
            session_id=session_id,
            agent_reply=agent_reply,
            dataset=dataset
        )
        
        return {
            "agent_reply": agent_reply,
            "dataset": dataset,
            "chart_request": chart_request  # Pre-formatted!
        }
```

---

## ⚠️ Common Errors

### Error: Invalid chart_type
**Solution**: Use `filter_unsupported=True`
```python
format_chart_transform_request(..., filter_unsupported=True)
```

### Error: Missing parameters
**Solution**: Validate before sending
```python
errors = validate_all_chart_suggestions(charts)
if errors:
    raise ValueError(errors)
```

### Error: agent_reply is string
**Solution**: Auto-parses string or dict
```python
parse_agent_reply(agent_reply)  # Handles both!
```
