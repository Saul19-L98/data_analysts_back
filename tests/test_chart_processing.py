"""
Test the chart transformation with actual dataset using TestClient.
"""
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

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

# Chart suggestion from agent
suggested_charts = [
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

# Request payload
payload = {
    "session_id": "sess_test_with_data",
    "suggested_charts": suggested_charts,
    "dataset": dataset
}

print("=" * 70)
print("Testing Chart Transformation with Real Dataset")
print("=" * 70)
print(f"\nDataset size: {len(dataset)} records")
print(f"Date range: {dataset[-1]['date']} to {dataset[0]['date']}")
print(f"Chart suggestions: {len(suggested_charts)}")
print("\nFiltering for September 2024 data...")
print("=" * 70)

response = client.post("/api/v1/charts/transform", json=payload)

print(f"\n[STATUS] {response.status_code}")

if response.status_code == 200:
    result = response.json()
    
    print("\n[SUCCESS] Charts transformed successfully!")
    print(f"\nSession ID: {result['session_id']}")
    print(f"Total charts: {result['total_charts']}")
    
    for idx, chart in enumerate(result['charts'], 1):
        print(f"\n{'=' * 70}")
        print(f"Chart {idx}: {chart['title']}")
        print(f"{'=' * 70}")
        print(f"Type: {chart['chart_type']}")
        print(f"Description: {chart['description']}")
        print(f"X-axis: {chart['x_axis_key']}")
        print(f"Y-axes: {', '.join(chart['y_axis_keys'])}")
        
        print(f"\nChart Config:")
        for key, config in chart['chart_config'].items():
            print(f"  - {key}: {config['label']} ({config['color']})")
        
        print(f"\nChart Data ({len(chart['chart_data'])} points):")
        print(json.dumps(chart['chart_data'], indent=2))
        
        # Verify the data is properly filtered and aggregated
        if chart['chart_data'] and len(chart['chart_data']) > 0:
            print(f"\n[VALIDATION]")
            print(f"  - Received {len(chart['chart_data'])} data points")
            print(f"  - Expected: Aggregated by paper_type for September")
            
            # Check if aggregation worked
            has_paper_type = 'paper_type' in chart['chart_data'][0]
            has_total_sales = 'total_sales' in chart['chart_data'][0]
            
            if has_paper_type and has_total_sales:
                print(f"  - [OK] Data contains paper_type and total_sales")
                total = sum(point['total_sales'] for point in chart['chart_data'])
                print(f"  - Total sales in September: ${total:,.2f}")
            else:
                print(f"  - [WARNING] Unexpected data structure")
    
    print("\n" + "=" * 70)
    print("SUCCESS! Chart data is ready for frontend")
    print("=" * 70)
else:
    print(f"\n[ERROR] Request failed")
    print(response.text)
