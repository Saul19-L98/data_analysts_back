# 🎯 Testing Chart Transformation with Dataset (v1.4.0+)

## Overview

The `/api/v1/charts/transform` endpoint now supports **data processing**! Include your dataset to get fully processed, chart-ready data instead of placeholders.

---

## Quick Comparison

### Without Dataset (Old Way)
```json
{
  "session_id": "sess_123",
  "suggested_charts": [...]
}
```
**Returns**: Placeholder data structure with parameters

### With Dataset (New Way) ✨
```json
{
  "session_id": "sess_123",
  "dataset": [...],  // Your actual data
  "suggested_charts": [...]
}
```
**Returns**: Fully processed chart data ready for rendering

---

## Postman Testing Guide

### Step 1: Create New Request

1. Open Postman
2. Click **"New"** → **"HTTP Request"**
3. Name it: `Transform Charts with Dataset`

### Step 2: Configure Request

- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/charts/transform`
- **Headers**:
  - `Content-Type`: `application/json`

### Step 3: Prepare Request Body

Click **"Body"** → Select **"raw"** → Choose **"JSON"**

### Step 4: Example Request (September Sales Analysis)

```json
{
  "session_id": "sess_2025_10_22T17_20_02Z_474ab3b8",
  "dataset": [
    {"date": "2024-09-28", "paper_type": "A4", "quantity": 160, "price": 5.50, "total_sales": 880.00},
    {"date": "2024-09-29", "paper_type": "Letter", "quantity": 140, "price": 6.00, "total_sales": 840.00},
    {"date": "2024-09-30", "paper_type": "Legal", "quantity": 110, "price": 6.25, "total_sales": 687.50},
    {"date": "2024-10-01", "paper_type": "A4", "quantity": 150, "price": 5.50, "total_sales": 825.00},
    {"date": "2024-10-02", "paper_type": "Letter", "quantity": 120, "price": 6.00, "total_sales": 720.00},
    {"date": "2024-10-03", "paper_type": "Legal", "quantity": 100, "price": 6.25, "total_sales": 625.00},
    {"date": "2024-10-04", "paper_type": "A4", "quantity": 180, "price": 5.50, "total_sales": 990.00},
    {"date": "2024-10-05", "paper_type": "Cardstock", "quantity": 75, "price": 8.00, "total_sales": 600.00}
  ],
  "suggested_charts": [
    {
      "title": "September Sales by Type",
      "chart_type": "bar",
      "parameters": {
        "x_axis": "paper_type",
        "aggregations": [
          {
            "column": "total_sales",
            "func": "sum"
          }
        ],
        "filters": [
          {
            "column": "date",
            "op": ">=",
            "value": "2024-09-01"
          },
          {
            "column": "date",
            "op": "<=",
            "value": "2024-09-30"
          }
        ]
      },
      "insight": "Shows sales breakdown by paper type for September",
      "priority": "high"
    }
  ]
}
```

### Step 5: Expected Response ✅

```json
{
  "message": "Gráficos transformados exitosamente",
  "session_id": "sess_2025_10_22T17_20_02Z_474ab3b8",
  "charts": [
    {
      "title": "September Sales by Type",
      "description": "Shows sales breakdown by paper type for September",
      "chart_type": "bar",
      "chart_config": {
        "total_sales": {
          "label": "Total Sales",
          "color": "hsl(var(--chart-1))"
        }
      },
      "chart_data": [
        {
          "paper_type": "A4",
          "total_sales": 880.0
        },
        {
          "paper_type": "Legal",
          "total_sales": 687.5
        },
        {
          "paper_type": "Letter",
          "total_sales": 840.0
        }
      ],
      "x_axis_key": "paper_type",
      "y_axis_keys": ["total_sales"],
      "trend_percentage": null
    }
  ],
  "total_charts": 1
}
```

**What Happened**:
- 8 records in dataset → Filtered to 3 September records
- Grouped by `paper_type`
- Summed `total_sales` for each type
- Returned chart-ready JSON

---

## Complete Workflow

### 1. Upload File to /ingest

```
POST http://localhost:8000/api/v1/ingest
Content-Type: multipart/form-data

file: paper_sales.csv
agent_id: YOUR_AGENT_ID
agent_alias_id: YOUR_ALIAS_ID
```

### 2. Convert CSV to JSON

From your CSV file, create a JSON array:

**CSV:**
```csv
date,paper_type,quantity,price,total_sales
2024-09-28,A4,160,5.50,880.00
2024-09-29,Letter,140,6.00,840.00
```

**JSON:**
```json
[
  {"date": "2024-09-28", "paper_type": "A4", "quantity": 160, "price": 5.50, "total_sales": 880.00},
  {"date": "2024-09-29", "paper_type": "Letter", "quantity": 140, "price": 6.00, "total_sales": 840.00}
]
```

### 3. Extract Suggested Charts

From the `/ingest` response:
```json
{
  "agent_reply": {
    "suggested_charts": [
      // Copy these charts
    ]
  }
}
```

### 4. Call /transform with Dataset

```json
POST http://localhost:8000/api/v1/charts/transform

{
  "session_id": "{{from_ingest_response}}",
  "dataset": {{your_json_array}},
  "suggested_charts": {{from_agent_reply}}
}
```

### 5. Use Chart Data in Frontend

```typescript
// React + shadcn/recharts
import { BarChart, Bar, XAxis, YAxis } from 'recharts';

function MyChart({ chart }) {
  return (
    <BarChart data={chart.chart_data}>
      <XAxis dataKey={chart.x_axis_key} />
      <YAxis />
      {chart.y_axis_keys.map(key => (
        <Bar 
          key={key}
          dataKey={key} 
          fill={`var(--color-${key})`} 
        />
      ))}
    </BarChart>
  );
}

// No additional data processing needed! 🎉
```

---

## Supported Data Operations

### Filters

```json
{
  "filters": [
    {"column": "date", "op": ">=", "value": "2024-09-01"},
    {"column": "date", "op": "<=", "value": "2024-09-30"},
    {"column": "price", "op": ">", "value": 5.00},
    {"column": "category", "op": "==", "value": "A4"},
    {"column": "status", "op": "in", "value": ["active", "pending"]}
  ]
}
```

**Operators**: `>=`, `<=`, `==`, `>`, `<`, `!=`, `in`

### Aggregations

```json
{
  "aggregations": [
    {"column": "total_sales", "func": "sum"},
    {"column": "quantity", "func": "mean"},
    {"column": "price", "func": "max"},
    {"column": "id", "func": "count"}
  ]
}
```

**Functions**: `sum`, `mean`, `max`, `min`, `count`

### Grouping

Automatically groups by the `x_axis` field:

```json
{
  "x_axis": "paper_type"  // Will group by this field
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

---

## Testing Scenarios

### Scenario 1: Monthly Sales Comparison

```json
{
  "session_id": "sess_test",
  "dataset": [
    // All your sales data
  ],
  "suggested_charts": [{
    "title": "October vs September Sales",
    "chart_type": "bar",
    "parameters": {
      "x_axis": "paper_type",
      "aggregations": [{"column": "total_sales", "func": "sum"}],
      "filters": [
        {"column": "date", "op": ">=", "value": "2024-09-01"},
        {"column": "date", "op": "<=", "value": "2024-10-31"}
      ]
    },
    "insight": "Compare sales across two months",
    "priority": "high"
  }]
}
```

### Scenario 2: Top Products

```json
{
  "session_id": "sess_test",
  "dataset": [...],
  "suggested_charts": [{
    "title": "Top 5 Products by Revenue",
    "chart_type": "bar",
    "parameters": {
      "x_axis": "product",
      "aggregations": [{"column": "revenue", "func": "sum"}],
      "sort": {"column": "revenue", "order": "desc"}
    },
    "insight": "Best performing products",
    "priority": "high"
  }]
}
```

### Scenario 3: Time Series Analysis

```json
{
  "session_id": "sess_test",
  "dataset": [...],
  "suggested_charts": [{
    "title": "Daily Sales Trend",
    "chart_type": "line",
    "parameters": {
      "x_axis": "date",
      "aggregations": [{"column": "total_sales", "func": "sum"}],
      "sort": {"column": "date", "order": "asc"}
    },
    "insight": "Sales over time",
    "priority": "high"
  }]
}
```

### Scenario 4: Multiple Charts at Once

```json
{
  "session_id": "sess_test",
  "dataset": [...],  // Same dataset for all charts
  "suggested_charts": [
    {
      "title": "Sales by Type",
      "chart_type": "bar",
      "parameters": {
        "x_axis": "paper_type",
        "aggregations": [{"column": "total_sales", "func": "sum"}]
      }
    },
    {
      "title": "Daily Trend",
      "chart_type": "line",
      "parameters": {
        "x_axis": "date",
        "aggregations": [{"column": "total_sales", "func": "sum"}],
        "sort": {"column": "date", "order": "asc"}
      }
    },
    {
      "title": "Quantity Distribution",
      "chart_type": "pie",
      "parameters": {
        "x_axis": "paper_type",
        "aggregations": [{"column": "quantity", "func": "sum"}]
      }
    }
  ]
}
```

Each chart processes the dataset independently!

---

## Postman Test Scripts

Add this to the **Tests** tab for automatic validation:

```javascript
// Validate response structure
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has success message", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData.message).to.equal('Gráficos transformados exitosamente');
});

pm.test("Charts have processed data (not placeholders)", function () {
    var jsonData = pm.response.json();
    var firstChart = jsonData.charts[0];
    
    // Check that chart_data is an array
    pm.expect(firstChart.chart_data).to.be.an('array');
    
    // Check that first item is NOT a placeholder
    var firstDataPoint = firstChart.chart_data[0];
    pm.expect(firstDataPoint).to.not.have.property('note');
    pm.expect(firstDataPoint).to.not.have.property('description');
    
    // Check that it has actual data fields
    pm.expect(firstDataPoint).to.have.property(firstChart.x_axis_key);
});

pm.test("Aggregations were applied", function () {
    var jsonData = pm.response.json();
    var firstChart = jsonData.charts[0];
    
    // Check that chart_data has aggregated values
    firstChart.chart_data.forEach(function(item) {
        firstChart.y_axis_keys.forEach(function(key) {
            pm.expect(item).to.have.property(key);
            pm.expect(item[key]).to.be.a('number');
        });
    });
});

pm.test("Response time is acceptable", function () {
    pm.expect(pm.response.responseTime).to.be.below(5000);
});
```

---

## Validation Checklist

### Before Sending Request
- [ ] Server is running (`uv run uvicorn app.main:app --reload`)
- [ ] Request body is valid JSON
- [ ] `session_id` is included
- [ ] `dataset` is an array of objects
- [ ] `suggested_charts` is an array with at least one chart
- [ ] All chart parameters are valid (x_axis, aggregations, etc.)

### After Receiving Response
- [ ] Status code is 200
- [ ] `chart_data` is NOT a placeholder (no "note" or "description" fields)
- [ ] `chart_data` has the expected number of records
- [ ] Aggregated values match your manual calculations
- [ ] Filters were applied correctly (check record count)
- [ ] Sorting is in the expected order
- [ ] `chart_config` has colors for all y_axis_keys

---

## Tips for CSV to JSON Conversion

### Manual Conversion (Small Files)

Use an online tool like:
- https://csvjson.com/csv2json
- https://www.convertcsv.com/csv-to-json.htm

### In Postman (Pre-request Script)

```javascript
// Parse CSV from environment variable
const csv = pm.environment.get("csv_data");
const lines = csv.split('\n');
const headers = lines[0].split(',');

const dataset = lines.slice(1).map(line => {
    const values = line.split(',');
    const obj = {};
    headers.forEach((header, i) => {
        const value = values[i]?.trim();
        // Try to parse as number
        obj[header.trim()] = isNaN(value) ? value : parseFloat(value);
    });
    return obj;
});

pm.environment.set("dataset_json", JSON.stringify(dataset));
```

Then in your request body:
```json
{
  "session_id": "{{session_id}}",
  "dataset": {{dataset_json}},
  "suggested_charts": [...]
}
```

### In JavaScript/TypeScript (Frontend)

```typescript
function csvToJSON(csv: string): Record<string, any>[] {
  const lines = csv.split('\n');
  const headers = lines[0].split(',').map(h => h.trim());
  
  return lines.slice(1)
    .filter(line => line.trim())
    .map(line => {
      const values = line.split(',');
      return headers.reduce((obj, header, i) => {
        const value = values[i]?.trim();
        obj[header] = isNaN(Number(value)) ? value : parseFloat(value);
        return obj;
      }, {} as Record<string, any>);
    });
}

// Usage
const csvData = `date,paper_type,quantity,price,total_sales
2024-09-28,A4,160,5.50,880.00
2024-09-29,Letter,140,6.00,840.00`;

const dataset = csvToJSON(csvData);
```

---

## Troubleshooting

### Problem: Getting Placeholder Data Instead of Processed Data

**Solution**: Make sure you include the `dataset` field in your request body.

### Problem: "date" Filters Not Working

**Solution**: Ensure dates are in ISO format: `"2024-09-01"` (YYYY-MM-DD)

### Problem: Aggregation Results Don't Match

**Solution**: 
- Check that filters are applied correctly (might be filtering out records)
- Verify that column names match exactly (case-sensitive)
- Confirm aggregation function is correct (sum vs mean vs count)

### Problem: Empty chart_data Array

**Solution**:
- Check that filters aren't too restrictive (no matching records)
- Verify column names in filters exist in dataset
- Check that dataset array is not empty

### Problem: TypeError or NaN in Results

**Solution**:
- Ensure numeric columns contain valid numbers in dataset
- Check for null/undefined values in your dataset
- Verify aggregation functions match column types (don't sum strings!)

---

## Summary

**Key Benefits**:
- ✅ No need to query data separately in frontend
- ✅ Filters, aggregations, and sorting handled automatically
- ✅ Chart-ready data format (direct to shadcn/recharts)
- ✅ Batch process multiple charts at once
- ✅ Consistent data transformations across all charts

**Best Practices**:
1. Always include `dataset` for production use
2. Test filters with known data to validate results
3. Verify aggregations match manual calculations
4. Use Postman tests to automate validation
5. Save successful requests as examples in collection

---

For the full Postman testing guide including the /ingest endpoint, see `POSTMAN_TESTING_GUIDE.md`.
