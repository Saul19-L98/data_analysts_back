# Data Analyst Backend 🚀

FastAPI backend for data analysis with AWS Bedrock Agent integration. Upload spreadsheets (CSV/XLSX), extract comprehensive data profiles, and get AI-powered insights.

## Features ✨

- 📊 **File Upload**: Support for CSV and Excel files
- 🔍 **Data Analysis**: Automatic extraction of schema, dtypes, and statistics
- 🤖 **AI Integration**: AWS Bedrock Agent for intelligent data insights
- ⚡ **High Performance**: Built with FastAPI and async/await patterns
- 🏗️ **Clean Architecture**: MVC pattern with clear separation of concerns
- 🧪 **Well Tested**: Comprehensive test coverage
- 📝 **Auto Documentation**: Swagger UI and ReDoc

## Architecture 🏛️

```
app/
├── core/              # Configuration, exceptions, utilities
├── models/schemas/    # Pydantic request/response models
├── services/          # Business logic layer
│   ├── file_parser.py       # CSV/XLSX parsing
│   ├── data_analyzer.py     # Schema & stats extraction
│   ├── bedrock_service.py   # AWS Bedrock integration
│   └── ingest_service.py    # Orchestration
└── controllers/v1/    # API endpoints (routers)
```

## Prerequisites 📋

- Python 3.11+
- UV package manager
- AWS Account with Bedrock Agent access
- AWS credentials (Access Key ID & Secret Access Key)

## Quick Start 🚀

### 1. Clone and Setup

```bash
# Clone the repository
cd data_analyst_back

# Install dependencies with UV
uv sync
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# Required:
# - AWS_REGION
# - AWS_ACCESS_KEY_ID
# - AWS_SECRET_ACCESS_KEY
```

### 3. Run the Application

```bash
# Development server with auto-reload
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server with multiple workers
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## API Usage 📡

### Upload and Analyze Endpoint

**POST** `/api/v1/ingest`

Upload a spreadsheet file and get AI-powered analysis.

**Request** (multipart/form-data):
```
file: (CSV or XLSX file) [REQUIRED]
message: "Analyze Q3 sales trends" [OPTIONAL]
agent_id: "your-bedrock-agent-id" [REQUIRED]
agent_alias_id: "your-agent-alias-id" [REQUIRED]
```

**Response** (201 Created):
```json
{
  "session_id": "sess_2025_10_21T15_45_00Z_abc123",
  "agent_id": "AGENT123",
  "agent_alias_id": "ALIAS456",
  "columns": ["date", "store_id", "sales", "category"],
  "dtypes": {
    "date": "datetime64[ns]",
    "store_id": "int64",
    "sales": "float64",
    "category": "object"
  },
  "summary": {
    "describe_numeric": { ... },
    "describe_non_numeric": { ... },
    "info_text": "class DataFrame..."
  },
  "agent_reply": "Based on the data profile...",
  "sent_to_agent": true
}
```

**Error Responses**:
- `400` - File parsing error
- `413` - File too large (>25MB)
- `415` - Unsupported file type
- `422` - Missing required fields
- `429` - Bedrock throttling
- `502` - Bedrock service error

### cURL Example

```bash
curl -X POST "http://localhost:8000/api/v1/ingest" \
  -F "file=@sales_data.csv" \
  -F "message=Analyze sales trends and identify anomalies" \
  -F "agent_id=YOUR_AGENT_ID" \
  -F "agent_alias_id=YOUR_ALIAS_ID"
```

## Testing 🧪

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_file_parser.py

# Run with verbose output
uv run pytest -v
```

## Development 🛠️

### Code Quality

```bash
# Format code with Black
uv run black app/ tests/

# Sort imports with isort
uv run isort app/ tests/

# Lint with flake8
uv run flake8 app/ tests/

# Type checking with mypy
uv run mypy app/
```

### Project Structure Principles

- ✅ **Single Responsibility**: Each service has one clear purpose
- ✅ **Dependency Injection**: Services receive dependencies via constructor
- ✅ **DRY**: No code duplication, shared logic in utilities
- ✅ **Separation of Concerns**: Controllers, services, and models are independent
- ✅ **Type Safety**: Full type hints for better IDE support and fewer bugs

## Configuration ⚙️

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AWS_REGION` | Yes | - | AWS region for Bedrock |
| `AWS_ACCESS_KEY_ID` | Yes | - | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | Yes | - | AWS secret key |
| `AWS_SESSION_TOKEN` | No | - | AWS session token (for temporary credentials) |
| `APP_NAME` | No | "Data Analyst Backend" | Application name |
| `DEBUG` | No | false | Debug mode |
| `MAX_FILE_SIZE_MB` | No | 25 | Maximum upload size in MB |
| `ALLOWED_ORIGINS` | No | localhost:3000,localhost:5173 | CORS allowed origins |
| `API_V1_PREFIX` | No | /api/v1 | API version prefix |

### Security Best Practices

- 🔐 Never commit `.env` file
- 🔑 Use IAM roles instead of access keys in production
- 🔄 Rotate credentials regularly
- 🚫 Use least-privilege permissions for AWS credentials
- 📝 Enable AWS CloudTrail for audit logging

## Troubleshooting 🔧

### Common Issues

**Import errors when running**:
```bash
# Make sure dependencies are installed
uv sync
```

**AWS credential errors**:
```bash
# Verify .env file exists and has correct values
cat .env

# Test AWS credentials
aws sts get-caller-identity --region us-east-1
```

**File size errors**:
```bash
# Increase MAX_FILE_SIZE_MB in .env
MAX_FILE_SIZE_MB=50
```

## Resources 📚

### Documentation
- **[Testing Summary](docs/TESTING_SUMMARY.md)** - Quick reference for all testing docs
- **[Postman Testing Guide](docs/POSTMAN_TESTING_GUIDE.md)** - Test /ingest endpoint with file uploads
- **[Chart Transform with Dataset](docs/CHART_TRANSFORM_DATASET_TESTING.md)** - **NEW v1.4.0**: Test chart data processing
- **[Agent Response Formatting](docs/AGENT_RESPONSE_FORMATTING.md)** - **NEW v1.5.0**: Format agent responses for chart transform
- **[Quick Reference: Formatting](docs/QUICK_REFERENCE_FORMATTING.md)** - **NEW v1.5.0**: One-liner commands and snippets
- **[JSON Parsing Improvements](docs/JSON_PARSING_IMPROVEMENTS.md)** - Technical: JSON parsing system
- **[Chart Data Processing](docs/CHART_DATA_PROCESSING.md)** - Technical: Data processing pipeline

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [AWS Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [UV Package Manager](https://github.com/astral-sh/uv)

## Testing 🧪

### Run Unit Tests
```bash
uv run pytest
```

### Test with Postman
See [POSTMAN_TESTING_GUIDE.md](docs/POSTMAN_TESTING_GUIDE.md) for complete testing instructions.

### Quick Test Scripts
```bash
# Test JSON parsing with truncated responses
uv run python test_json_parsing.py

# Test chart data processing
uv run python test_chart_processing.py

# Test agent response formatting (NEW v1.5.0)
uv run python test_chart_formatting.py

# Format agent response (CLI)
uv run python format_agent_response.py response.json
```

## Recent Updates 🆕

### v1.5.0 (Current)
- 🎨 **Auto-Formatted Chart Requests**: `/ingest` now returns `chart_transform_request` ready for immediate use
- 🗑️ **Removed `agent_reply` Duplication**: Cleaner response structure without redundant data
- 📊 **Extended Chart Types**: Added support for scatter, donut, radar, radial charts (shadcn/recharts compatible)
- 🛠️ **CLI Tool**: Command-line utility for formatting agent responses
- ✅ **Auto-Validation**: Automatic filtering of unsupported chart types (histogram, box, etc.)
- 📚 **Comprehensive Docs**: Complete guide with examples and best practices

### v1.4.0
- ✨ **Chart data processing**: Include dataset in transform request for fully processed chart data
- 🔧 **Pandas integration**: Automatic filtering, aggregation, grouping, and sorting
- 📊 **Ready-to-render data**: Chart data can be passed directly to shadcn/recharts
- 📝 **Complete documentation**: New testing guide for data processing feature

### v1.3.0
- 🐛 **Fixed JSON parsing**: 4-strategy system handles truncated Bedrock responses
- 📈 **Improved reliability**: Progressive fallback for incomplete JSON
- 🔍 **Debug logging**: Track which parsing strategy succeeds

