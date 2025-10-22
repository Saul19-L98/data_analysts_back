"""
Test the chart transformation endpoint with actual dataset.
This demonstrates how to use the endpoint with real data.
"""
import requests
import json

# Sample dataset (paper_sales.csv as JSON)
dataset = [
    {"date": "2024-10-01", "paper_type": "A4", "quantity": 150, "price": 5.50, "total_sales": 825.00},
    {"date": "2024-10-02", "paper_type": "Letter", "quantity": 120, "price": 6.00, "total_sales": 720.00},
    {"date": "2024-10-03", "paper_type": "Legal", "quantity": 100, "price": 6.25, "total_sales": 625.00},
    {"date": "2024-10-04", "paper_type": "A4", "quantity": 180, "price": 5.50, "total_sales": 990.00},
    {"date": "2024-10-05", "paper_type": "Cardstock", "quantity": 75, "price": 8.00, "total_sales": 600.00},
    {"date": "2024-09-28", "paper_type": "A4", "quantity": 160, "price": 5.50, "total_sales": 880.00},
    {"date": "2024-09-29", "paper_type": "Letter", "quantity": 140, "price": 6.00, "total_sales": 840.00},
    {"date": "2024-09-30", "paper_type": "Legal", "quantity": 110, "price": 6.25, "total_sales": 687.50},
]

# Chart suggestion from agent (like from /ingest endpoint)
suggested_charts = [
    {
        "title": "Q3 2024 Daily Sales Trend",
        "chart_type": "line",
        "parameters": {
            "x_axis": "date",
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
                    "value": "2024-07-01"
                },
                {
                    "column": "date",
                    "op": "<=",
                    "value": "2024-09-30"
                }
            ],
            "sort": {
                "column": "date",
                "order": "asc"
            }
        },
        "insight": "Will show sales patterns and verify September data presence",
        "priority": "high"
    }
]

# Request payload
payload = {
    "session_id": "sess_test_123",
    "suggested_charts": suggested_charts,
    "dataset": dataset  # <-- This is the key addition!
}

print("=" * 70)
print("Testing Chart Transformation with Real Dataset")
print("=" * 70)
print(f"\nDataset size: {len(dataset)} records")
print(f"Chart suggestions: {len(suggested_charts)}")
print("\nSending request to http://localhost:8000/api/v1/charts/transform")
print("=" * 70)

try:
    response = requests.post(
        "http://localhost:8000/api/v1/charts/transform",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"\n[STATUS] {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        
        print("\n[SUCCESS] Charts transformed successfully!")
        print(f"\nSession ID: {result['session_id']}")
        print(f"Total charts: {result['total_charts']}")
        
        for idx, chart in enumerate(result['charts'], 1):
            print(f"\n--- Chart {idx}: {chart['title']} ---")
            print(f"Type: {chart['chart_type']}")
            print(f"Description: {chart['description']}")
            print(f"X-axis: {chart['x_axis_key']}")
            print(f"Y-axes: {', '.join(chart['y_axis_keys'])}")
            print(f"\nChart Config:")
            for key, config in chart['chart_config'].items():
                print(f"  - {key}: {config['label']} ({config['color']})")
            
            print(f"\nChart Data ({len(chart['chart_data'])} points):")
            for i, point in enumerate(chart['chart_data'][:3], 1):
                print(f"  {i}. {point}")
            if len(chart['chart_data']) > 3:
                print(f"  ... and {len(chart['chart_data']) - 3} more points")
        
        print("\n" + "=" * 70)
        print("FULL RESPONSE:")
        print("=" * 70)
        print(json.dumps(result, indent=2))
        
    else:
        print(f"\n[ERROR] Request failed")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n[ERROR] Could not connect to server")
    print("Make sure the server is running: uv run uvicorn app.main:app --reload")
except Exception as e:
    print(f"\n[ERROR] {str(e)}")
