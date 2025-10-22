# 🧪 Testing Documentation Summary

Quick reference for all testing documentation in this project.

---

## 📚 Documentation Files

### 1. [POSTMAN_TESTING_GUIDE.md](POSTMAN_TESTING_GUIDE.md)
**Purpose**: Testing the `/api/v1/ingest` endpoint

**What it covers**:
- File upload (CSV/XLSX) with Postman
- Configuring form-data requests
- AWS Bedrock agent configuration
- Response validation
- Basic chart transformation (placeholder mode)
- Troubleshooting common issues

**When to use**: When you want to upload a file and get chart suggestions from the Bedrock Agent.

---

### 2. [CHART_TRANSFORM_DATASET_TESTING.md](CHART_TRANSFORM_DATASET_TESTING.md) ✨ NEW
**Purpose**: Testing the `/api/v1/charts/transform` endpoint with data processing

**What it covers**:
- **v1.4.0 Feature**: Including dataset for actual data processing
- Complete workflow: Upload → Parse → Transform → Render
- CSV to JSON conversion techniques
- Testing filters, aggregations, grouping, and sorting
- Multiple chart scenarios (monthly comparison, top products, time series)
- Postman test scripts for validation
- Troubleshooting data processing issues

**When to use**: When you want to get fully processed, chart-ready data instead of just placeholders.

---

### 3. [JSON_PARSING_IMPROVEMENTS.md](JSON_PARSING_IMPROVEMENTS.md)
**Purpose**: Technical documentation of JSON parsing enhancements

**What it covers**:
- 4-strategy JSON parsing system
- Handling truncated Bedrock responses
- Debug logging and testing
- Production readiness checklist

**When to use**: When debugging JSON parsing issues or understanding how truncated responses are handled.

---

### 4. [CHART_DATA_PROCESSING.md](CHART_DATA_PROCESSING.md)
**Purpose**: Technical documentation of chart data processing feature

**What it covers**:
- Before/after comparison (placeholder vs processed data)
- Processing pipeline explanation (filter → aggregate → sort)
- Supported operations and examples
- Frontend integration code (TypeScript/React)
- Use cases and scenarios

**When to use**: When implementing frontend chart rendering or understanding the data processing pipeline.

---

## 🎯 Quick Navigation by Task

### I want to upload a file and get chart suggestions
→ **[POSTMAN_TESTING_GUIDE.md](POSTMAN_TESTING_GUIDE.md)**

### I want to test chart transformation with actual data processing
→ **[CHART_TRANSFORM_DATASET_TESTING.md](CHART_TRANSFORM_DATASET_TESTING.md)**

### I'm getting JSON parsing errors
→ **[JSON_PARSING_IMPROVEMENTS.md](JSON_PARSING_IMPROVEMENTS.md)**

### I want to understand how data processing works
→ **[CHART_DATA_PROCESSING.md](CHART_DATA_PROCESSING.md)**

### I want to integrate charts in my frontend
→ **[CHART_DATA_PROCESSING.md](CHART_DATA_PROCESSING.md)** (see Frontend Integration section)

---

## 🚀 Recommended Testing Workflow

### For Backend Development/Testing

1. **Start Server**
   ```bash
   uv run uvicorn app.main:app --reload
   ```

2. **Test File Upload** (use Postman)
   - Follow **[POSTMAN_TESTING_GUIDE.md](POSTMAN_TESTING_GUIDE.md)**
   - Verify agent_reply returns as object (not string)
   - Save session_id and suggested_charts

3. **Test Chart Transformation with Data** (use Postman)
   - Follow **[CHART_TRANSFORM_DATASET_TESTING.md](CHART_TRANSFORM_DATASET_TESTING.md)**
   - Include dataset in request body
   - Verify chart_data contains processed records
   - Validate filters, aggregations work correctly

4. **Run Unit Tests**
   ```bash
   uv run pytest
   ```

### For Frontend Development

1. **Understand the Data Flow**
   - Read **[CHART_DATA_PROCESSING.md](CHART_DATA_PROCESSING.md)**
   - Review "Frontend Integration" section

2. **Test API Endpoints**
   - Use **[CHART_TRANSFORM_DATASET_TESTING.md](CHART_TRANSFORM_DATASET_TESTING.md)**
   - Test CSV to JSON conversion
   - Verify chart_data format matches your component expectations

3. **Implement Chart Components**
   - Use code examples from **[CHART_DATA_PROCESSING.md](CHART_DATA_PROCESSING.md)**
   - Pass chart_data directly to shadcn/recharts
   - Test with different chart types (line, bar, area, pie)

---

## 📊 Feature Comparison

| Feature | Placeholder Mode | Data Processing Mode (v1.4.0+) |
|---------|------------------|--------------------------------|
| **Endpoint** | `/api/v1/charts/transform` | `/api/v1/charts/transform` |
| **Include Dataset?** | No | ✅ Yes |
| **Returns** | Chart structure + parameters | Actual filtered/aggregated data |
| **Frontend Work** | Must query and process data | Pass directly to chart component |
| **Use Case** | Structure preview | Production rendering |
| **Documentation** | POSTMAN_TESTING_GUIDE.md | CHART_TRANSFORM_DATASET_TESTING.md |

---

## 🔧 Environment Setup

All testing requires:

1. **Python Environment** (managed by UV)
   ```bash
   uv sync
   ```

2. **AWS Credentials** in `.env`
   ```
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   AWS_DEFAULT_REGION=us-east-1
   BEDROCK_AGENT_ID=your_agent_id
   BEDROCK_AGENT_ALIAS_ID=your_alias_id
   ```

3. **Running Server**
   ```bash
   uv run uvicorn app.main:app --reload
   ```

---

## 📝 Test Data

### Sample CSV (paper_sales.csv)
```csv
date,paper_type,quantity,price,total_sales
2024-09-28,A4,160,5.50,880.00
2024-09-29,Letter,140,6.00,840.00
2024-09-30,Legal,110,6.25,687.50
2024-10-01,A4,150,5.50,825.00
2024-10-02,Letter,120,6.00,720.00
2024-10-03,Legal,100,6.25,625.00
2024-10-04,A4,180,5.50,990.00
2024-10-05,Cardstock,75,8.00,600.00
```

**Available in**: `test_chart_processing.py`

---

## ✅ Testing Checklist

### Before Testing
- [ ] Server is running on localhost:8000
- [ ] AWS credentials are configured
- [ ] Postman is installed
- [ ] Sample data file is ready (CSV or XLSX)

### /ingest Endpoint
- [ ] File upload works (200 status)
- [ ] agent_reply is an object (not string)
- [ ] suggested_charts array is present
- [ ] session_id is returned
- [ ] columns array matches CSV headers

### /charts/transform Endpoint (without dataset)
- [ ] Returns 200 status
- [ ] chart_config has proper structure
- [ ] chart_data contains placeholder with parameters
- [ ] x_axis_key and y_axis_keys are correct

### /charts/transform Endpoint (with dataset) ✨
- [ ] Returns 200 status
- [ ] chart_data contains actual records (not placeholders)
- [ ] Filters were applied (verify record count)
- [ ] Aggregations are correct (manually verify sums/means)
- [ ] Sorting is in expected order
- [ ] Multiple charts process independently
- [ ] Frontend can render chart_data directly

---

## 🐛 Troubleshooting

### Issue: "agent_reply is a string, not an object"
→ **Solution**: Fixed in v1.3.0. See [JSON_PARSING_IMPROVEMENTS.md](JSON_PARSING_IMPROVEMENTS.md)

### Issue: "chart_data still shows placeholder"
→ **Solution**: Include `dataset` field. See [CHART_TRANSFORM_DATASET_TESTING.md](CHART_TRANSFORM_DATASET_TESTING.md)

### Issue: "Filters not working / wrong data count"
→ **Solution**: Check filter operators and date formats. See troubleshooting in [CHART_TRANSFORM_DATASET_TESTING.md](CHART_TRANSFORM_DATASET_TESTING.md)

### Issue: "502 Bad Gateway from Bedrock"
→ **Solution**: Check AWS credentials. See [POSTMAN_TESTING_GUIDE.md](POSTMAN_TESTING_GUIDE.md) troubleshooting section

---

## 📚 Related Files

### Test Scripts
- `test_json_parsing.py` - Tests 4-strategy JSON parsing
- `test_chart_processing.py` - Tests data processing with real dataset

### Service Files
- `app/services/bedrock_service.py` - Bedrock integration + JSON parsing
- `app/services/chart_transform_service.py` - Chart transformation + data processing

### Schema Files
- `app/models/schemas/chart.py` - Chart request/response models (includes dataset field)

---

**Last Updated**: v1.4.0 (Chart data processing feature)

**For Questions**: Refer to the specific guide for your task above, or check the inline code documentation.
