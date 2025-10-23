# Agent Response Formatting Guide

## Overview

This guide explains how to format agent responses from AWS Bedrock into valid JSON for the chart transformation endpoint. The agent returns chart suggestions embedded as JSON strings within the `/api/v1/ingest` response, which need to be parsed and validated before sending to `/api/v1/charts/transform`.

---

## Problem Statement

The `/api/v1/ingest` endpoint returns (v1.5.0):
```json
{
  "chart_transform_request": {
    "session_id": "sess_xxx",
    "suggested_charts": [...],  // Already parsed and filtered!
    "dataset": [...]             // Complete dataset included
  },
  "session_id": "sess_xxx",
  "columns": [...],
  "dtypes": {...}
}
```

The `/api/v1/charts/transform` endpoint expects:
```json
{
  "session_id": "sess_xxx",
  "suggested_charts": [...],
  "dataset": [...]
}
```

**Solution in v1.5.0**: The backend now automatically formats the complete request! Simply use `chart_transform_request` as-is - no parsing, no formatting, no duplication.

---

## Supported Chart Types

Based on **shadcn/Recharts** compatibility:

### ✅ Supported
- `line` - Line charts (temporal trends)
- `bar` - Bar charts (categorical comparisons)
- `area` - Area charts (filled temporal trends)
- `pie` - Pie charts (proportional composition)
- `donut` - Donut charts (pie variant with center hole)
- `scatter` - Scatter plots (correlation analysis)
- `radar` - Radar charts (multivariate comparison)
- `radial` - Radial charts (circular progress/metrics)

### ❌ Not Supported (Require Custom Implementation)
- `histogram` - Statistical distribution
- `box` - Box plots (quartile analysis)
- `heatmap` - 2D color-coded matrix
- `treemap` - Hierarchical rectangles

---

## Solution 1: Command-Line Utility

### Usage

```bash
# Format agent response from file
uv run python format_agent_response.py agent_response.json

# Specify custom output file
uv run python format_agent_response.py agent_response.json output.json
```

### Features
- ✅ Parses nested JSON strings
- ✅ Filters unsupported chart types
- ✅ Validates structure
- ✅ Pretty-prints summary
- ✅ Saves to file

### Example Output
```
✅ Successfully formatted agent response!
📄 Input:  agent_response.json
📄 Output: agent_response_transform.json

📊 Summary:
   - Session ID: sess_2025_10_22T22_58_57Z_098bc5ca
   - Valid charts: 3
   - Dataset records: 30

📈 Charts included:
   1. Monthly Sales Trend (line)
   2. Sales Distribution by Paper Type (bar)
   3. Sales vs Quantity Relationship (scatter)
```

---

## Solution 2: Python Utility Functions

### Import

```python
from app.utils.chart_formatting import (
    parse_agent_reply,
    filter_supported_charts,
    extract_chart_suggestions,
    format_chart_transform_request,
    validate_all_chart_suggestions
)
```

### Parse Agent Reply

```python
# Agent reply can be string or dict
agent_reply_str = response["agent_reply"]  # JSON string from Bedrock
parsed = parse_agent_reply(agent_reply_str)  # Returns dict

# Extract just the charts
charts = extract_chart_suggestions(parsed)
```

### Filter Unsupported Types

```python
charts = [
    {"title": "Valid", "chart_type": "line", "parameters": {}},
    {"title": "Invalid", "chart_type": "histogram", "parameters": {}}
]

valid, skipped = filter_supported_charts(charts)
# valid: [{"title": "Valid", ...}]
# skipped: [{"title": "Invalid", "chart_type": "histogram", "reason": "..."}]
```

### Format Complete Request

```python
# One-step formatting
request = format_chart_transform_request(
    session_id="sess_xxx",
    agent_reply=ingest_response["agent_reply"],  # Can be string or dict
    dataset=ingest_response["dataset"],
    filter_unsupported=True  # Auto-filter invalid types
)

# Ready to POST to /api/v1/charts/transform
```

### Validate Charts

```python
errors = validate_all_chart_suggestions(charts)

if errors:
    for error in errors:
        print(f"Chart #{error['chart_index']}: {error['error']}")
else:
    print("All charts valid!")
```

---

## Solution 3: Integration in Service Layer

### Update IngestService (Recommended)

```python
# app/services/ingest_service.py

from app.utils.chart_formatting import format_chart_transform_request

class IngestService:
    
    async def handle_upload(self, file, session_id):
        # ... existing code ...
        
        # Format chart transform request automatically
        chart_request = format_chart_transform_request(
            session_id=session_id,
            agent_reply=agent_reply,
            dataset=dataset,
            filter_unsupported=True
        )
        
        # Add to response
        return IngestResponse(
            message="Archivo analizado con éxito",
            session_id=session_id,
            agent_reply=agent_reply,
            dataset=dataset,
            chart_transform_request=chart_request  # New field!
        )
```

### Add Field to Schema

```python
# app/models/schemas/ingest.py

class IngestResponse(BaseModel):
    message: str
    session_id: str
    agent_reply: str
    dataset: list[dict[str, Any]]
    chart_transform_request: dict[str, Any] | None = Field(
        None,
        description="Pre-formatted request for /api/v1/charts/transform endpoint"
    )
```

**Benefit**: Frontend receives both raw agent response AND ready-to-use transform request!

---

## Complete Workflow Examples

### Example 1: Manual Formatting (Command Line)

```bash
# Step 1: Call /api/v1/ingest and save response
curl -X POST http://localhost:8000/api/v1/ingest \
  -F "file=@sales.csv" \
  > agent_response.json

# Step 2: Format for chart transform
uv run python format_agent_response.py agent_response.json chart_request.json

# Step 3: Send to chart transform endpoint
curl -X POST http://localhost:8000/api/v1/charts/transform \
  -H "Content-Type: application/json" \
  -d @chart_request.json
```

### Example 2: Programmatic Formatting (Python)

```python
import httpx
from app.utils.chart_formatting import format_chart_transform_request

# Step 1: Upload file to ingest endpoint
with open("sales.csv", "rb") as f:
    response = httpx.post(
        "http://localhost:8000/api/v1/ingest",
        files={"file": f}
    )
ingest_data = response.json()

# Step 2: Format chart transform request
chart_request = format_chart_transform_request(
    session_id=ingest_data["session_id"],
    agent_reply=ingest_data["agent_reply"],
    dataset=ingest_data["dataset"],
    filter_unsupported=True
)

# Step 3: Call chart transform endpoint
transform_response = httpx.post(
    "http://localhost:8000/api/v1/charts/transform",
    json=chart_request
)
charts = transform_response.json()
```

### Example 3: Frontend Integration (TypeScript) - v1.5.0

```typescript
// Step 1: Upload file
const formData = new FormData();
formData.append('file', file);
formData.append('agent_id', AGENT_ID);
formData.append('agent_alias_id', AGENT_ALIAS_ID);

const ingestResponse = await fetch('/api/v1/ingest', {
  method: 'POST',
  body: formData
});
const ingestData = await ingestResponse.json();

// Step 2: Get pre-formatted chart request (NO PARSING NEEDED!)
const chartRequest = ingestData.chart_transform_request;

// Step 3: Send directly to transform endpoint
const chartsResponse = await fetch('/api/v1/charts/transform', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(chartRequest)  // Already formatted!
});
const charts = await chartsResponse.json();
```

**Key Benefit**: No need to parse `agent_reply` or filter chart types - the backend does it all!

---

## Testing

### Run Formatting Tests

```bash
# Test all formatting utilities
uv run python test_chart_formatting.py
```

### Test Output Includes:
1. ✅ Parse agent reply (string → dict)
2. ✅ Filter unsupported chart types
3. ✅ Extract chart suggestions
4. ✅ Format complete transform request
5. ✅ Validate chart structure
6. ✅ Real-world scenario with file output

---

## Validation Rules

### Required Fields (Per Chart)
- `title` (string)
- `chart_type` (must be in supported list)
- `parameters` (object/dict)

### Optional Fields
- `insight` (string)
- `priority` ("high" | "medium" | "low")
- `data_request_required` (boolean)

### Chart Parameters
- `x_axis` (string): Column name for X axis
- `y_axis` (string): Column name for Y axis
- `series` (array): Multiple data series
- `group_by` (array): Grouping columns
- `filters` (array): Filter conditions
- `aggregations` (array): Aggregation functions
- `sort` (object): Sort configuration
- `limit` (number): Row limit

---

## Error Handling

### Common Issues

#### Issue 1: Invalid JSON in agent_reply
```python
try:
    parsed = parse_agent_reply(agent_reply)
except ValueError as e:
    # Handle parsing error
    return {"error": f"Invalid agent response: {e}"}
```

#### Issue 2: Unsupported Chart Types
```python
valid, skipped = filter_supported_charts(charts)
if skipped:
    # Log or notify about skipped charts
    logger.warning(f"Skipped {len(skipped)} unsupported charts")
```

#### Issue 3: Missing Required Fields
```python
errors = validate_all_chart_suggestions(charts)
if errors:
    # Return validation errors to client
    return {"validation_errors": errors}
```

---

## Best Practices

1. **Always validate before transformation**
   ```python
   errors = validate_all_chart_suggestions(charts)
   if errors:
       raise HTTPException(400, detail=errors)
   ```

2. **Filter unsupported types automatically**
   ```python
   format_chart_transform_request(..., filter_unsupported=True)
   ```

3. **Log skipped charts for monitoring**
   ```python
   valid, skipped = filter_supported_charts(charts)
   if skipped:
       logger.info(f"Skipped charts: {[s['title'] for s in skipped]}")
   ```

4. **Handle missing dataset gracefully**
   ```python
   dataset = ingest_response.get("dataset", [])
   if not dataset:
       logger.warning("No dataset provided, charts may be empty")
   ```

5. **Use type hints for clarity**
   ```python
   def format_request(
       session_id: str,
       agent_reply: str | dict,
       dataset: list[dict[str, Any]]
   ) -> dict[str, Any]:
       ...
   ```

---

## Files Reference

- **Utility Functions**: `app/utils/chart_formatting.py`
- **CLI Tool**: `format_agent_response.py`
- **Test Script**: `test_chart_formatting.py`
- **Schema**: `app/models/schemas/chart.py`
- **Example Output**: `test_formatted_request.json`

---

## Summary

| Method | Use Case | Pros | Cons |
|--------|----------|------|------|
| **CLI Tool** | One-off formatting, debugging | Easy to use, no code needed | Manual step |
| **Utility Functions** | Custom logic, integration | Flexible, reusable | Requires coding |
| **Service Integration** | Production API | Automatic, seamless | Requires backend changes |

**Recommendation**: Use **Service Integration** for production, **CLI Tool** for testing/debugging, and **Utility Functions** for custom workflows.
