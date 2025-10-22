"""Test script to verify /ingest endpoint returns dataset for both CSV and XLSX files."""
import io
import pandas as pd
import httpx
import time

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
AGENT_ID = "7DTMDVQB1Y"
AGENT_ALIAS_ID = "GCM9JR6C41"

# Sample data
data = {
    "date": ["2024-10-01", "2024-10-02", "2024-10-03", "2024-10-04", "2024-10-05"],
    "paper_type": ["A4", "Letter", "Legal", "Cardstock", "A4"],
    "quantity": [150, 120, 90, 75, 180],
    "price": [5.50, 6.00, 6.50, 8.00, 5.50],
    "total_sales": [825.0, 720.0, 585.0, 600.0, 990.0]
}

df = pd.DataFrame(data)

def test_csv_with_dataset():
    """Test that CSV upload returns dataset in response."""
    print("\n" + "="*60)
    print("TEST 1: CSV File Upload")
    print("="*60)
    
    # Create CSV in memory
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()
    
    # Prepare request
    files = {
        'file': ('paper_sales.csv', csv_content, 'text/csv')
    }
    data_form = {
        'message': 'Analiza las ventas y sugiere gráficos',
        'agent_id': AGENT_ID,
        'agent_alias_id': AGENT_ALIAS_ID
    }
    
    # Send request
    print("\n📤 Sending CSV file...")
    with httpx.Client(timeout=60.0) as client:  # Increased timeout for Bedrock
        response = client.post(f"{BASE_URL}/ingest", files=files, data=data_form)
    
    # Check response
    if response.status_code == 200:
        result = response.json()
        print("✅ Status: 200 OK")
        print(f"✅ Session ID: {result.get('session_id')}")
        print(f"✅ Columns: {result.get('columns')}")
        
        # Check dataset field
        if 'dataset' in result:
            dataset = result['dataset']
            print(f"✅ Dataset field present")
            print(f"✅ Dataset length: {len(dataset)} records")
            print(f"\n📊 First 2 records:")
            for i, record in enumerate(dataset[:2], 1):
                print(f"   Record {i}: {record}")
            
            # Validate structure
            if len(dataset) > 0:
                first_record = dataset[0]
                expected_keys = ['date', 'paper_type', 'quantity', 'price', 'total_sales']
                has_all_keys = all(key in first_record for key in expected_keys)
                print(f"✅ Has all expected keys: {has_all_keys}")
            
            return True
        else:
            print("❌ Dataset field missing!")
            return False
    else:
        print(f"❌ Status: {response.status_code}")
        print(f"❌ Error: {response.text}")
        return False

def test_xlsx_with_dataset():
    """Test that XLSX upload returns dataset in response."""
    print("\n" + "="*60)
    print("TEST 2: XLSX File Upload")
    print("="*60)
    
    # Create XLSX in memory
    xlsx_buffer = io.BytesIO()
    df.to_excel(xlsx_buffer, index=False, engine='openpyxl')
    xlsx_content = xlsx_buffer.getvalue()
    
    # Prepare request
    files = {
        'file': ('paper_sales.xlsx', xlsx_content, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    }
    data_form = {
        'message': 'Analiza las ventas y sugiere gráficos',
        'agent_id': AGENT_ID,
        'agent_alias_id': AGENT_ALIAS_ID
    }
    
    # Send request
    print("\n📤 Sending XLSX file...")
    with httpx.Client(timeout=60.0) as client:  # Increased timeout for Bedrock
        response = client.post(f"{BASE_URL}/ingest", files=files, data=data_form)
    
    # Check response
    if response.status_code == 200:
        result = response.json()
        print("✅ Status: 200 OK")
        print(f"✅ Session ID: {result.get('session_id')}")
        print(f"✅ Columns: {result.get('columns')}")
        
        # Check dataset field
        if 'dataset' in result:
            dataset = result['dataset']
            print(f"✅ Dataset field present")
            print(f"✅ Dataset length: {len(dataset)} records")
            print(f"\n📊 First 2 records:")
            for i, record in enumerate(dataset[:2], 1):
                print(f"   Record {i}: {record}")
            
            # Validate structure
            if len(dataset) > 0:
                first_record = dataset[0]
                expected_keys = ['date', 'paper_type', 'quantity', 'price', 'total_sales']
                has_all_keys = all(key in first_record for key in expected_keys)
                print(f"✅ Has all expected keys: {has_all_keys}")
            
            return True
        else:
            print("❌ Dataset field missing!")
            return False
    else:
        print(f"❌ Status: {response.status_code}")
        print(f"❌ Error: {response.text}")
        return False

def test_chart_transform_with_dataset():
    """Test using the dataset from /ingest in /charts/transform."""
    print("\n" + "="*60)
    print("TEST 3: Chart Transformation with Dataset from Ingest")
    print("="*60)
    
    # First, get data from ingest
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_content = csv_buffer.getvalue()
    
    files = {
        'file': ('paper_sales.csv', csv_content, 'text/csv')
    }
    data_form = {
        'message': 'Analiza las ventas',
        'agent_id': AGENT_ID,
        'agent_alias_id': AGENT_ALIAS_ID
    }
    
    print("\n📤 Step 1: Calling /ingest...")
    with httpx.Client(timeout=60.0) as client:  # Increased timeout for Bedrock
        ingest_response = client.post(f"{BASE_URL}/ingest", files=files, data=data_form)
    
    if ingest_response.status_code != 200:
        print(f"❌ Ingest failed: {ingest_response.status_code}")
        return False
    
    ingest_data = ingest_response.json()
    print("✅ Ingest successful")
    print(f"✅ Got dataset with {len(ingest_data['dataset'])} records")
    
    # Now use the dataset in transform
    transform_payload = {
        "session_id": ingest_data['session_id'],
        "dataset": ingest_data['dataset'],  # Use dataset from ingest!
        "suggested_charts": [
            {
                "title": "Sales by Paper Type",
                "chart_type": "bar",
                "parameters": {
                    "x_axis": "paper_type",
                    "aggregations": [
                        {
                            "column": "total_sales",
                            "func": "sum"
                        }
                    ]
                },
                "insight": "Total sales by product type",
                "priority": "high"
            }
        ]
    }
    
    print("\n📤 Step 2: Calling /charts/transform with dataset...")
    with httpx.Client(timeout=30.0) as client:
        transform_response = client.post(
            f"{BASE_URL}/charts/transform",
            json=transform_payload,
            headers={'Content-Type': 'application/json'}
        )
    
    if transform_response.status_code == 200:
        result = transform_response.json()
        print("✅ Transform successful")
        
        if result.get('charts') and len(result['charts']) > 0:
            chart = result['charts'][0]
            chart_data = chart.get('chart_data', [])
            
            print(f"✅ Got {len(chart_data)} data points")
            print(f"\n📊 Chart Data:")
            for point in chart_data:
                print(f"   {point}")
            
            # Validate it's not placeholder
            if len(chart_data) > 0 and 'note' not in chart_data[0]:
                print("✅ Data is processed (not placeholder)")
                return True
            else:
                print("❌ Data appears to be placeholder")
                return False
        else:
            print("❌ No charts in response")
            return False
    else:
        print(f"❌ Transform failed: {transform_response.status_code}")
        print(f"❌ Error: {transform_response.text}")
        return False

if __name__ == "__main__":
    print("\n" + "🧪 TESTING /INGEST WITH DATASET FEATURE" + "\n")
    print("This tests that both CSV and XLSX files return the dataset field")
    print("so the frontend doesn't need to parse files manually.\n")
    
    results = []
    
    # Test CSV
    try:
        results.append(("CSV Upload", test_csv_with_dataset()))
    except Exception as e:
        print(f"❌ CSV test failed with exception: {e}")
        results.append(("CSV Upload", False))
    
    # Test XLSX
    try:
        results.append(("XLSX Upload", test_xlsx_with_dataset()))
    except Exception as e:
        print(f"❌ XLSX test failed with exception: {e}")
        results.append(("XLSX Upload", False))
    
    # Test full workflow
    try:
        results.append(("Complete Workflow", test_chart_transform_with_dataset()))
    except Exception as e:
        print(f"❌ Workflow test failed with exception: {e}")
        results.append(("Complete Workflow", False))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results)
    print("\n" + ("🎉 All tests passed!" if all_passed else "⚠️ Some tests failed"))
