# Chart Transformation Endpoint Guide

## Overview

The `/api/v1/charts/transform` endpoint transforms Bedrock Agent's chart suggestions into shadcn/recharts compatible format.

---

## Endpoint

**POST** `/api/v1/charts/transform`

---

## Request Format

```json
{
  "session_id": "sess_2025_10_22T12_00_00Z_abc123",
  "suggested_charts": [
    {
      "title": "Q3 2024 Sales Trend Analysis",
      "chart_type": "line",
      "parameters": {
        "x_axis": "date",
        "y_axis": "total_sales",
        "aggregations": [
          {
            "column": "total_sales",
            "func": "sum"
          }
        ],
        "sort": {
          "by": "date",
          "order": "asc"
        }
      },
      "insight": "Will reveal if Q3 data exists and show sales patterns/anomalies",
      "priority": "high",
      "data_request_required": true
    }
  ]
}
```

---

## Response Format

**Status**: `200 OK`

```json
{
  "message": "Gráficos transformados exitosamente",
  "session_id": "sess_2025_10_22T12_00_00Z_abc123",
  "charts": [
    {
      "title": "Q3 2024 Sales Trend Analysis",
      "description": "Will reveal if Q3 data exists and show sales patterns/anomalies",
      "chart_type": "line",
      "chart_config": {
        "total_sales": {
          "label": "Total Sales",
          "color": "hsl(var(--chart-1))"
        }
      },
      "chart_data": [
        {
          "note": "Data structure placeholder",
          "description": "Use the chart parameters to query your actual dataset",
          "x_axis": "date",
          "y_axis_keys": ["total_sales"],
          "aggregations": [
            {
              "column": "total_sales",
              "func": "sum"
            }
          ],
          "filters": [],
          "sort": {
            "by": "date",
            "order": "asc"
          }
        }
      ],
      "x_axis_key": "date",
      "y_axis_keys": ["total_sales"],
      "trend_percentage": null
    }
  ],
  "total_charts": 1
}
```

---

## Using with Shadcn Charts

### 1. Extract from Ingest Response

After calling `/api/v1/ingest`, extract the `suggested_charts` from `agent_reply`:

```javascript
// From ingest response
const { session_id, agent_reply } = ingestResponse;
const suggested_charts = agent_reply.suggested_charts;
```

### 2. Transform Charts

```javascript
const transformResponse = await fetch('/api/v1/charts/transform', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id: session_id,
    suggested_charts: suggested_charts
  })
});

const { charts } = await transformResponse.json();
```

### 3. Render with Shadcn

```tsx
import { LineChart, Line, XAxis, CartesianGrid } from "recharts"
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart"

function Chart({ transformedChart }) {
  return (
    <ChartContainer config={transformedChart.chart_config} className="min-h-[200px] w-full">
      <LineChart data={transformedChart.chart_data}>
        <CartesianGrid vertical={false} />
        <XAxis dataKey={transformedChart.x_axis_key} />
        <ChartTooltip content={<ChartTooltipContent />} />
        {transformedChart.y_axis_keys.map((key) => (
          <Line 
            key={key}
            dataKey={key}
            fill={`var(--color-${key})`}
            stroke={`var(--color-${key})`}
          />
        ))}
      </LineChart>
    </ChartContainer>
  )
}
```

---

## Supported Chart Types

| Chart Type | Description | Best For |
|------------|-------------|----------|
| `line` | Line chart | Trends over time |
| `bar` | Bar chart | Comparing categories |
| `area` | Area chart | Cumulative data |
| `pie` | Pie chart | Proportions |

---

## Chart Config Structure

The `chart_config` follows shadcn's format:

```typescript
{
  [dataKey: string]: {
    label: string;      // Human-readable label
    color: string;      // CSS variable or hex color
  }
}
```

Colors use shadcn's chart color variables:
- `hsl(var(--chart-1))` - Primary
- `hsl(var(--chart-2))` - Secondary
- `hsl(var(--chart-3))` - Tertiary
- `hsl(var(--chart-4))` - Quaternary
- `hsl(var(--chart-5))` - Quinary

---

## Example: Full Workflow

```typescript
// 1. Upload file and get analysis
const ingestResponse = await fetch('/api/v1/ingest', {
  method: 'POST',
  body: formData
});

const { session_id, agent_reply } = await ingestResponse.json();

// 2. Transform suggested charts
const transformResponse = await fetch('/api/v1/charts/transform', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    session_id,
    suggested_charts: agent_reply.suggested_charts
  })
});

const { charts } = await transformResponse.json();

// 3. Render each chart
charts.forEach(chart => {
  renderChart(chart);
});
```

---

## Notes

- The `chart_data` in the response is a placeholder structure
- You should fetch actual data based on the chart parameters
- The `x_axis_key` and `y_axis_keys` tell you which fields to plot
- `chart_config` provides colors and labels for each data series
- Multiple charts can be transformed in a single request

---

## Testing in Postman

### Example Request

```json
POST http://localhost:8000/api/v1/charts/transform

{
  "session_id": "sess_2025_10_22T05_49_19Z_caf83587",
  "suggested_charts": [
    {
      "title": "Paper Sales by Type",
      "chart_type": "bar",
      "parameters": {
        "x_axis": "paper_type",
        "y_axis": "quantity",
        "aggregations": [{"column": "quantity", "func": "sum"}]
      },
      "insight": "Shows which paper types sell the most"
    }
  ]
}
```

### Expected Response

Status: `200 OK`

```json
{
  "message": "Gráficos transformados exitosamente",
  "session_id": "sess_2025_10_22T05_49_19Z_caf83587",
  "charts": [...],
  "total_charts": 1
}
```
