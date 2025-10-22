# Changelog

All notable changes to this project will be documented in this file.

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
