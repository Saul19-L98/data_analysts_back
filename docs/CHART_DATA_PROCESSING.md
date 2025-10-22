# Chart Transformation with Dataset Processing

## Overview

The `/api/v1/charts/transform` endpoint now **processes actual data** and returns **ready-to-render chart data** for shadcn/recharts components.

**✨ NEW in v1.4.0**: The `/api/v1/ingest` endpoint now returns the `dataset` field for **both CSV and XLSX files**! This means:
- ✅ No frontend CSV parsing needed
- ✅ No Excel library (SheetJS/xlsx) needed in frontend
- ✅ Backend handles all file format conversions
- ✅ Consistent JSON format for both file types
- ✅ Dates, numbers, and NaN values properly handled

## What Changed

### Before (v1.3.0)
```json
{
  "chart_data": [
    {
      "note": "Data structure placeholder",
      "description": "Use the chart parameters to query your actual dataset"
    }
  ]
}
```
❌ Frontend had to fetch and process data separately

### After (v1.4.0)
```json
{
  "chart_data": [
    {"paper_type": "A4", "total_sales": 880.0},
    {"paper_type": "Legal", "total_sales": 687.5},
    {"paper_type": "Letter", "total_sales": 840.0}
  ]
}
```
✅ Data is **filtered, aggregated, sorted, and ready** to pass directly to recharts

## How It Works

### 1. Send Dataset with Chart Request

```json
POST /api/v1/charts/transform
{
  "session_id": "sess_xxx",
  "suggested_charts": [...],  // From /ingest endpoint
  "dataset": [                 // NEW: Raw data from CSV/Excel
    {"date": "2024-09-28", "paper_type": "A4", "quantity": 160, "total_sales": 880.0},
    {"date": "2024-09-29", "paper_type": "Letter", "quantity": 140, "total_sales": 840.0},
    ...
  ]
}
```

### 2. Backend Processes Data

The service automatically:

1. **Converts to DataFrame**: `pd.DataFrame(dataset)`
2. **Applies Filters**: Based on `parameters.filters`
   ```python
   # Example: Filter for September 2024
   df = df[(df['date'] >= '2024-09-01') & (df['date'] <= '2024-09-30')]
   ```
3. **Performs Aggregations**: Based on `parameters.aggregations`
   ```python
   # Example: Sum total_sales by paper_type
   df = df.groupby('paper_type')['total_sales'].sum()
   ```
4. **Applies Sorting**: Based on `parameters.sort`
5. **Converts Dates**: To JSON-safe strings (`YYYY-MM-DD`)
6. **Returns Records**: As list of dictionaries

## How Excel (.xlsx) and CSV Files Are Handled

Both file types are processed identically by the backend:

### CSV Files
1. Parsed with pandas: `pd.read_csv()`
2. Converted to DataFrame
3. Converted to JSON records
4. Returned in `/ingest` response

### Excel Files (.xlsx)
1. Parsed with pandas + openpyxl: `pd.read_excel()`
2. Converted to DataFrame
3. Converted to JSON records  (same as CSV)
4. Returned in `/ingest` response

### Data Type Handling

The backend automatically handles:
- **Dates**: Converted to ISO format strings (`YYYY-MM-DD`)
- **Numbers**: Preserved as integers or floats
- **NaN/Empty**: Converted to `null` (JSON compatible)
- **Text**: Preserved as strings

**Frontend receives the same JSON structure regardless of file type!**

### 3. Frontend Receives Ready Data

```typescript
// No processing needed - just pass to recharts!
<BarChart data={chart.chart_data}>
  <XAxis dataKey={chart.x_axis_key} />  // "paper_type"
  <Bar dataKey={chart.y_axis_keys[0]} /> // "total_sales"
</BarChart>
```

## Complete Workflow Example

### Step 1: Upload File to /ingest

```bash
POST /api/v1/ingest
Content-Type: multipart/form-data

file: paper_sales.csv  # or paper_sales.xlsx
agent_id: your_agent_id
agent_alias_id: your_alias_id
```

**Response:**
```json
{
  "message": "Archivo analizado con éxito",
  "session_id": "sess_2025_10_22T17_20_02Z_474ab3b8",
  "columns": ["date", "paper_type", "quantity", "price", "total_sales"],
  "dtypes": {"date": "object", "paper_type": "object", "quantity": "int64"},
  "summary": {...},
  "agent_reply": {
    "suggested_charts": [
      {
        "title": "September Sales by Type",
        "chart_type": "bar",
        "parameters": {
          "x_axis": "paper_type",
          "aggregations": [{"column": "total_sales", "func": "sum"}],
          "filters": [
            {"column": "date", "op": ">=", "value": "2024-09-01"},
            {"column": "date", "op": "<=", "value": "2024-09-30"}
          ]
        }
      }
    ]
  },
  "sent_to_agent": true,
  "dataset": [
    {"date": "2024-10-01", "paper_type": "A4", "quantity": 150, "price": 5.5, "total_sales": 825.0},
    {"date": "2024-10-02", "paper_type": "Letter", "quantity": 120, "price": 6.0, "total_sales": 720.0},
    {"date": "2024-10-03", "paper_type": "Legal", "quantity": 90, "price": 6.5, "total_sales": 585.0}
  ]
}
```

**✨ NEW**: The `dataset` field is now included for **both CSV and XLSX** files! No need for frontend parsing.

### Step 2: Use Dataset from /ingest Response (No Frontend Parsing Needed!)

```javascript
// Upload file
const formData = new FormData();
formData.append('file', file);  // Can be .csv or .xlsx
formData.append('message', 'Analiza las ventas');
formData.append('agent_id', agentId);
formData.append('agent_alias_id', agentAliasId);

const ingestResponse = await fetch('/api/v1/ingest', {
  method: 'POST',
  body: formData
});

const ingestData = await ingestResponse.json();

// ✅ Dataset is already formatted as JSON - no parsing needed!
const dataset = ingestData.dataset;
const suggestedCharts = ingestData.agent_reply.suggested_charts;
```

### Step 3: Transform Charts with Data from Ingest

### Step 3: Transform Charts with Data from Ingest

```javascript
const response = await fetch('/api/v1/charts/transform', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    session_id: ingestData.session_id,
    suggested_charts: suggestedCharts,
    dataset: dataset  // ← From ingest response - works for CSV and XLSX!
  })
});

const { charts } = await response.json();
```

### Step 4: Render Charts Immediately

```tsx
{charts.map(chart => (
  <Card key={chart.title}>
    <CardHeader>
      <CardTitle>{chart.title}</CardTitle>
      <CardDescription>{chart.description}</CardDescription>
    </CardHeader>
    <CardContent>
      <ChartContainer config={chart.chart_config}>
        {chart.chart_type === 'bar' ? (
          <BarChart data={chart.chart_data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={chart.x_axis_key} />
            <YAxis />
            <Tooltip />
            <Bar dataKey={chart.y_axis_keys[0]} fill="var(--color-total_sales)" />
          </BarChart>
        ) : chart.chart_type === 'line' ? (
          <LineChart data={chart.chart_data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey={chart.x_axis_key} />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey={chart.y_axis_keys[0]} stroke="var(--color-total_sales)" />
          </LineChart>
        ) : null}
      </ChartContainer>
    </CardContent>
  </Card>
))}
```

## Supported Operations

### Filters

```json
{
  "filters": [
    {"column": "date", "op": ">=", "value": "2024-09-01"},
    {"column": "price", "op": "<", "value": 100},
    {"column": "status", "op": "==", "value": "active"},
    {"column": "category", "op": "in", "value": ["A", "B"]}
  ]
}
```

Operators: `>=`, `<=`, `==`, `>`, `<`, `!=`, `in`

### Aggregations

```json
{
  "aggregations": [
    {"column": "total_sales", "func": "sum"},
    {"column": "quantity", "func": "mean"},
    {"column": "price", "func": "max"}
  ]
}
```

Functions: `sum`, `mean`, `max`, `min`, `count`

### Grouping

```json
{
  "x_axis": "date",           // Primary group
  "group_by": ["category"]    // Secondary groups
}
```

### Sorting

```json
{
  "sort": {
    "column": "date",
    "order": "asc"  // or "desc"
  }
}
```

## Example Test Results

### Input Dataset (8 records)
```json
[
  {"date": "2024-09-28", "paper_type": "A4", "total_sales": 880.0},
  {"date": "2024-09-29", "paper_type": "Letter", "total_sales": 840.0},
  {"date": "2024-09-30", "paper_type": "Legal", "total_sales": 687.5},
  {"date": "2024-10-01", "paper_type": "A4", "total_sales": 825.0},
  ...
]
```

### Chart Parameters
```json
{
  "x_axis": "paper_type",
  "aggregations": [{"column": "total_sales", "func": "sum"}],
  "filters": [
    {"column": "date", "op": ">=", "value": "2024-09-01"},
    {"column": "date", "op": "<=", "value": "2024-09-30"}
  ]
}
```

### Output (3 aggregated records)
```json
[
  {"paper_type": "A4", "total_sales": 880.0},
  {"paper_type": "Legal", "total_sales": 687.5},
  {"paper_type": "Letter", "total_sales": 840.0}
]
```

✅ Filtered to September only (3 records out of 8)  
✅ Aggregated by paper_type  
✅ Ready for bar chart  

## Performance Considerations

- **In-Memory Processing**: Uses pandas for fast operations
- **Small Datasets**: Optimized for typical CSV uploads (< 100MB)
- **Recommended**: For large datasets (> 1M rows), consider server-side caching

## Backward Compatibility

### Without Dataset
```json
{
  "session_id": "sess_xxx",
  "suggested_charts": [...],
  "dataset": null  // or omit entirely
}
```

**Response:** Placeholder data structure (same as before)

### With Dataset
```json
{
  "session_id": "sess_xxx",
  "suggested_charts": [...],
  "dataset": [...]  // Actual records
}
```

**Response:** Fully processed chart data

## Testing

Run the included test:

```bash
uv run python test_chart_processing.py
```

Expected output:
```
[SUCCESS] Charts transformed successfully!
Chart Data (3 points):
[
  {"paper_type": "A4", "total_sales": 880.0},
  {"paper_type": "Legal", "total_sales": 687.5},
  {"paper_type": "Letter", "total_sales": 840.0}
]
[VALIDATION]
  - [OK] Data contains paper_type and total_sales
  - Total sales in September: $2,407.50
```

## Files Modified

- ✅ `app/models/schemas/chart.py` - Added `dataset` field to request
- ✅ `app/services/chart_transform_service.py` - Added `_process_data()` method
- ✅ `app/controllers/v1/charts.py` - Pass dataset to service
- ✅ `test_chart_processing.py` - Comprehensive test with real data

## Next Steps for Frontend

### Simplified Workflow (No File Parsing Needed!)

1. **Upload File** (CSV or XLSX) via `/api/v1/ingest`
2. **Extract from Response**:
   - `session_id`
   - `suggested_charts` (from `agent_reply`)
   - `dataset` (✨ already formatted as JSON!)
3. **Send to Transform** with all three fields
4. **Render charts** directly without additional processing

### Example Implementation

```typescript
// No need for CSV parsers or Excel libraries!
async function processFile(file: File) {
  // 1. Upload file (works for .csv and .xlsx)
  const formData = new FormData();
  formData.append('file', file);
  formData.append('message', 'Analyze sales data');
  formData.append('agent_id', AGENT_ID);
  formData.append('agent_alias_id', AGENT_ALIAS_ID);
  
  const ingestRes = await fetch('/api/v1/ingest', {
    method: 'POST',
    body: formData
  });
  
  const { session_id, agent_reply, dataset } = await ingestRes.json();
  
  // 2. Transform with dataset from backend
  const transformRes = await fetch('/api/v1/charts/transform', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id,
      suggested_charts: agent_reply.suggested_charts,
      dataset  // ← Backend already converted CSV/XLSX to JSON!
    })
  });
  
  const { charts } = await transformRes.json();
  
  // 3. Render charts immediately
  return charts;
}
```

### Benefits

✅ **No CSV Parsing Libraries**: No need for papaparse, csv-parse, etc.  
✅ **No Excel Libraries**: No need for SheetJS/xlsx (saves ~500KB bundle size)  
✅ **Consistent Format**: Same JSON structure for CSV and XLSX  
✅ **Type Safety**: Numbers, dates, nulls properly typed  
✅ **Error Handling**: File parsing errors handled by backend  
✅ **Performance**: Parsing happens on server (faster CPU)  

No more manual data queries or transformations needed! 🎉

---

**Version**: 1.4.0  
**Status**: ✅ Production Ready  
**Breaking Changes**: None (backward compatible)
