# Changelog

All notable changes to this project will be documented in this file.

## [1.6.0] - 2025-01-21

### ✨ Added
- **Development Mode (DEV_MODE)**: New environment variable for conditional debugging
- Raw `agent_reply` included in `/api/v1/ingest` response when `DEV_MODE=dev`
- Conditional response field inclusion for debugging without production overhead
- Comprehensive DEV_MODE documentation in `docs/DEV_MODE.md`

### 🔧 Configuration
- Added `dev_mode` setting to `app/core/config.py` (`Literal["dev", "prod"]`)
- Default value: `"prod"` (production mode)
- Environment variable: `DEV_MODE` (options: `dev`, `prod`)

### 📋 Schema Changes
- Added optional `agent_reply` field to `IngestResponse`
- Field only populated when `DEV_MODE=dev`
- Maintains backward compatibility (field is optional)

### 🛠️ Service Updates
- `IngestService` now conditionally includes `agent_reply` based on settings
- Logging added: "DEV_MODE: Including raw agent_reply in response"
- Zero performance impact in production mode

### 📚 Documentation
- New guide: `docs/DEV_MODE.md` - Complete DEV_MODE reference
- Updated `README.md` with DEV_MODE configuration note
- Added troubleshooting and best practices sections

### 🎯 Use Cases
- **Development**: Debug raw Bedrock Agent responses
- **Testing**: Validate agent output formats
- **Production**: Clean responses without debugging overhead

---

## [1.3.0] - 2025-10-22

### ✨ Added
- **Chart Transformation Endpoint**: New `/api/v1/charts/transform` endpoint
- Transforms Bedrock Agent chart suggestions into shadcn/recharts compatible format
- Support for line, bar, area, and pie charts
- Automatic color assignment using shadcn chart color palette
- Chart configuration with labels and colors for visualization
- X-axis and Y-axis key extraction
- Aggregation and grouping support

### 📦 New Files
- `app/models/schemas/chart.py` - Chart transformation schemas
- `app/services/chart_transform_service.py` - Chart transformation logic
- `app/controllers/v1/charts.py` - Chart transformation endpoint
- `tests/test_charts.py` - Comprehensive chart transformation tests (5 tests)

### 🎯 API Endpoint
**POST /api/v1/charts/transform**
- Input: Agent's `suggested_charts` array + `session_id`
- Output: Charts formatted for shadcn with `chartConfig` and `chartData`
- Status: `200 OK`
- Message: "Gráficos transformados exitosamente"

### 📊 Shadcn Format
Transforms agent suggestions into:
```json
{
  "chart_config": {
    "total_sales": {
      "label": "Total Sales",
      "color": "hsl(var(--chart-1))"
    }
  },
  "chart_data": [...],
  "x_axis_key": "date",
  "y_axis_keys": ["total_sales"]
}
```

### ✅ Testing
- 31 total tests passing (26 existing + 5 new)
- Tests cover: success cases, multiple charts, validation, empty arrays, color assignments

---

## [1.2.0] - 2025-10-22

### ✨ Added
- **Success Message**: New `message` field in response with "Archivo analizado con éxito"
- User-friendly confirmation message for successful file analysis

### 🔧 Changed
- **Response Status Code**: Changed from `201 Created` to `200 OK` for successful requests
- **Removed Fields**: Removed `agent_id` and `agent_alias_id` from response body (still required in request)
- Simplified response structure focusing on analysis results

### 📝 Updated
- `POSTMAN_TESTING_GUIDE.md` updated with new response format and status codes
- Postman test scripts updated to validate new response structure

### 🎯 Impact
**Before**:
```json
{
  "session_id": "sess_...",
  "agent_id": "7DTMDVQB1Y",
  "agent_alias_id": "GCM9JR6C41",
  "columns": [...],
  ...
}
```
Status: `201 Created`

**After**:
```json
{
  "message": "Archivo analizado con éxito",
  "session_id": "sess_...",
  "columns": [...],
  ...
}
```
Status: `200 OK`

### 📦 Files Modified
- `app/models/schemas/ingest.py` - Added `message` field, removed `agent_id` and `agent_alias_id`
- `app/services/ingest_service.py` - Updated response building with success message
- `app/controllers/v1/ingest.py` - Changed status code to `HTTP_200_OK`
- `POSTMAN_TESTING_GUIDE.md` - Updated examples and test scripts

---

## [1.1.0] - 2025-10-22

### ✨ Added
- **JSON Parsing for Bedrock Responses**: The `agent_reply` field now returns a properly parsed JSON object instead of a raw string
- Intelligent JSON extraction from Bedrock responses with fallback to raw string if parsing fails
- Support for JSON embedded in text responses from Bedrock Agent

### 🔧 Changed
- **Breaking Change**: `agent_reply` type changed from `str` to `dict[str, Any] | str` in `IngestResponse` schema
- `BedrockService.invoke_agent()` now returns parsed JSON objects when possible
- Added `_parse_json_response()` method with smart JSON boundary detection
- Updated test mocks to return valid JSON responses

### 📝 Updated
- `POSTMAN_TESTING_GUIDE.md` now shows correct JSON object format for `agent_reply`
- All 25 tests pass with new JSON parsing functionality

### 🎯 Impact
**Before**:
```json
{
  "agent_reply": "\n{\n  \"version\": \"1.0\",\n  \"insights\": [...]\n}"
}
```

**After**:
```json
{
  "agent_reply": {
    "version": "1.0",
    "insights": [...]
  }
}
```

This makes the API response much easier to consume for frontend applications, as they can directly access nested properties without manual JSON parsing:
- ✅ `response.agent_reply.version` (works now)
- ❌ `JSON.parse(response.agent_reply).version` (no longer needed)

### 📦 Files Modified
- `app/models/schemas/ingest.py` - Updated `IngestResponse.agent_reply` type
- `app/services/bedrock_service.py` - Added JSON parsing logic with fallback
- `tests/conftest.py` - Updated mock to return valid JSON
- `POSTMAN_TESTING_GUIDE.md` - Updated example responses

---

## [1.0.0] - 2025-10-21

### 🎉 Initial Release
- FastAPI backend with AWS Bedrock Agent integration
- CSV/XLSX file upload and parsing
- Pandas-based data analysis (columns, dtypes, statistics)
- Complete MVC architecture
- Comprehensive test suite (25 tests)
- Postman testing guide
- Full documentation
