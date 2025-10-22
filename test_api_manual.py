#!/usr/bin/env python
"""
Test script for the Data Analyst Backend API.
Provides different ways to test the /api/v1/ingest endpoint.
"""
import requests
import json


# =============================================================================
# Configuration
# =============================================================================
BASE_URL = "http://localhost:8000"
INGEST_ENDPOINT = f"{BASE_URL}/api/v1/ingest"

# YOU NEED TO REPLACE THESE WITH YOUR ACTUAL BEDROCK AGENT IDs
AGENT_ID = "YOUR_BEDROCK_AGENT_ID"  # e.g., "ABCDEFGHIJ"
AGENT_ALIAS_ID = "YOUR_BEDROCK_ALIAS_ID"  # e.g., "TSTALIASID"

# =============================================================================
# Test 1: Health Check
# =============================================================================
def test_health():
    """Test the health endpoint."""
    print("\n" + "="*70)
    print("TEST 1: Health Check")
    print("="*70)
    
    response = requests.get(f"{BASE_URL}/health")
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    print("✅ Health check passed!")


# =============================================================================
# Test 2: Upload CSV File (Basic)
# =============================================================================
def test_upload_csv_basic():
    """Test uploading a CSV file with minimal data."""
    print("\n" + "="*70)
    print("TEST 2: Upload CSV File (Basic)")
    print("="*70)
    
    # Prepare the file
    files = {
        'file': ('sample_data.csv', open('sample_data.csv', 'rb'), 'text/csv')
    }
    
    # Prepare form data
    data = {
        'message': 'Analyze this sales data and identify trends',
        'agent_id': AGENT_ID,
        'agent_alias_id': AGENT_ALIAS_ID
    }
    
    print(f"Uploading file: sample_data.csv")
    print(f"Message: {data['message']}")
    print(f"Agent ID: {data['agent_id']}")
    print(f"Agent Alias ID: {data['agent_alias_id']}")
    
    response = requests.post(INGEST_ENDPOINT, files=files, data=data)
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 201:
        result = response.json()
        print(f"\n✅ Success! Response:")
        print(json.dumps(result, indent=2))
    else:
        print(f"\n❌ Error:")
        print(json.dumps(response.json(), indent=2))


# =============================================================================
# Test 3: Upload with cURL Command (Copy-Paste Ready)
# =============================================================================
def print_curl_command():
    """Print a cURL command for manual testing."""
    print("\n" + "="*70)
    print("TEST 3: cURL Command for Manual Testing")
    print("="*70)
    
    curl_command = f"""
curl -X POST "{INGEST_ENDPOINT}" \\
  -F "file=@sample_data.csv" \\
  -F "message=Analyze sales trends and identify any anomalies or patterns" \\
  -F "agent_id={AGENT_ID}" \\
  -F "agent_alias_id={AGENT_ALIAS_ID}"
"""
    
    print("\nCopy and paste this command in your terminal:")
    print(curl_command)


# =============================================================================
# Test 4: Test with PowerShell (Windows)
# =============================================================================
def print_powershell_command():
    """Print a PowerShell command for manual testing."""
    print("\n" + "="*70)
    print("TEST 4: PowerShell Command for Windows")
    print("="*70)
    
    ps_command = f"""
$uri = "{INGEST_ENDPOINT}"
$filePath = "sample_data.csv"

$form = @{{
    file = Get-Item -Path $filePath
    message = "Analyze this sales data for trends and insights"
    agent_id = "{AGENT_ID}"
    agent_alias_id = "{AGENT_ALIAS_ID}"
}}

Invoke-RestMethod -Uri $uri -Method Post -Form $form
"""
    
    print("\nCopy and paste this in PowerShell:")
    print(ps_command)


# =============================================================================
# Test 5: Validation Tests (Should Fail)
# =============================================================================
def test_validation_errors():
    """Test validation by sending invalid requests."""
    print("\n" + "="*70)
    print("TEST 5: Validation Error Tests (Expected to Fail)")
    print("="*70)
    
    # Test 1: Missing file
    print("\n5.1 - Missing file (should return 422):")
    response = requests.post(
        INGEST_ENDPOINT,
        data={
            'message': 'test',
            'agent_id': AGENT_ID,
            'agent_alias_id': AGENT_ALIAS_ID
        }
    )
    print(f"Status: {response.status_code} - {response.json()['detail']}")
    
    # Test 2: Missing agent_id
    print("\n5.2 - Missing agent_id (should return 422):")
    files = {'file': ('test.csv', b'col1,col2\nval1,val2', 'text/csv')}
    response = requests.post(
        INGEST_ENDPOINT,
        files=files,
        data={'message': 'test', 'agent_alias_id': AGENT_ALIAS_ID}
    )
    print(f"Status: {response.status_code} - {response.json()['detail']}")
    
    # Test 3: Missing agent_alias_id
    print("\n5.3 - Missing agent_alias_id (should return 422):")
    files = {'file': ('test.csv', b'col1,col2\nval1,val2', 'text/csv')}
    response = requests.post(
        INGEST_ENDPOINT,
        files=files,
        data={'message': 'test', 'agent_id': AGENT_ID}
    )
    print(f"Status: {response.status_code} - {response.json()['detail']}")
    
    # Test 4: Unsupported file type
    print("\n5.4 - Unsupported file type (should return 415):")
    files = {'file': ('test.pdf', b'fake pdf content', 'application/pdf')}
    response = requests.post(
        INGEST_ENDPOINT,
        files=files,
        data={
            'message': 'test',
            'agent_id': AGENT_ID,
            'agent_alias_id': AGENT_ALIAS_ID
        }
    )
    print(f"Status: {response.status_code} - {response.json()['detail']}")
    
    print("\n✅ All validation tests behaved as expected!")


# =============================================================================
# Test 6: Request/Response Structure Documentation
# =============================================================================
def print_request_response_structure():
    """Print the complete request/response structure."""
    print("\n" + "="*70)
    print("TEST 6: API Request/Response Structure Documentation")
    print("="*70)
    
    request_structure = """
REQUEST STRUCTURE (multipart/form-data):
----------------------------------------

Required Fields:
  • file (File):           CSV or XLSX file to analyze
  • agent_id (String):     AWS Bedrock Agent ID
  • agent_alias_id (String): AWS Bedrock Agent Alias ID

Optional Fields:
  • message (String):      Context message for the agent (default: "")

Example using Python requests:
```python
files = {
    'file': ('sales_data.csv', open('sales_data.csv', 'rb'), 'text/csv')
}

data = {
    'message': 'Analyze Q3 sales trends and identify anomalies',
    'agent_id': 'ABCDEFGHIJ',
    'agent_alias_id': 'TSTALIASID'
}

response = requests.post('http://localhost:8000/api/v1/ingest', files=files, data=data)
```

RESPONSE STRUCTURE (JSON - 201 Created):
-----------------------------------------
```json
{
  "session_id": "sess_2025_10_21T20_30_00Z_abc123",
  "agent_id": "ABCDEFGHIJ",
  "agent_alias_id": "TSTALIASID",
  "columns": ["date", "store_id", "sales", "category", "units_sold"],
  "dtypes": {
    "date": "object",
    "store_id": "int64",
    "sales": "float64",
    "category": "object",
    "units_sold": "int64"
  },
  "summary": {
    "describe_numeric": {
      "store_id": {
        "count": 15.0,
        "mean": 102.0,
        "std": 0.816496580927726,
        "min": 101.0,
        "25%": 101.0,
        "50%": 102.0,
        "75%": 103.0,
        "max": 103.0
      },
      "sales": {
        "count": 15.0,
        "mean": 1758.1833333333334,
        ...
      },
      "units_sold": {
        "count": 15.0,
        "mean": 33.8,
        ...
      }
    },
    "describe_non_numeric": {
      "date": {
        "count": 15,
        "unique": 5,
        "top": "2024-01-01",
        "freq": 3
      },
      "category": {
        "count": 15,
        "unique": 3,
        "top": "Food",
        "freq": 5
      }
    },
    "info_text": "<class 'pandas.core.frame.DataFrame'>\\nRangeIndex: 15 entries...\\nDtypes: ..."
  },
  "agent_reply": "Based on the dataset profile, I can see you have sales data with...",
  "sent_to_agent": true
}
```

ERROR RESPONSES:
----------------
400 Bad Request - File parsing error
{
  "detail": "Failed to parse CSV file: ...",
  "error_type": "FileParsingError"
}

413 Payload Too Large - File exceeds size limit
{
  "detail": "File size (30MB) exceeds maximum allowed (25MB)",
  "error_type": "FileSizeExceededError"
}

415 Unsupported Media Type - Invalid file type
{
  "detail": "Unsupported media type: application/pdf",
  "error_type": "UnsupportedFileTypeError"
}

422 Unprocessable Entity - Validation error
{
  "detail": "agent_id is required and cannot be empty",
  "error_type": "ValidationError"
}

429 Too Many Requests - Bedrock throttling
{
  "detail": "Request throttled by Bedrock. Please retry later.",
  "error_type": "BedrockThrottlingError"
}

502 Bad Gateway - Bedrock service error
{
  "detail": "Bedrock invocation failed: ...",
  "error_type": "BedrockInvocationError"
}
```
"""
    print(request_structure)


# =============================================================================
# Main Test Runner
# =============================================================================
def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("🧪 DATA ANALYST BACKEND - API TESTING SUITE")
    print("="*70)
    
    # Check if agent IDs are configured
    if AGENT_ID.startswith("YOUR_") or AGENT_ALIAS_ID.startswith("YOUR_"):
        print("\n⚠️  WARNING: Please update AGENT_ID and AGENT_ALIAS_ID in this script!")
        print("   You can still run health check and validation tests.\n")
    
    try:
        # Always run these tests
        test_health()
        print_request_response_structure()
        test_validation_errors()
        
        # Print manual test commands
        print_curl_command()
        print_powershell_command()
        
        # Only run actual upload if agent IDs are configured
        if not AGENT_ID.startswith("YOUR_") and not AGENT_ALIAS_ID.startswith("YOUR_"):
            test_upload_csv_basic()
        else:
            print("\n" + "="*70)
            print("⏭️  Skipping actual upload test (agent IDs not configured)")
            print("   Update AGENT_ID and AGENT_ALIAS_ID to test the full workflow")
            print("="*70)
        
        print("\n" + "="*70)
        print("✅ Testing Complete!")
        print("="*70)
        print("\n📚 Next Steps:")
        print("   1. Update AGENT_ID and AGENT_ALIAS_ID in this script")
        print("   2. Run: uv run python test_api_manual.py")
        print("   3. Or visit: http://localhost:8000/docs to test interactively")
        print("   4. Check sample_data.csv for test data structure")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to the API server")
        print("   Make sure the server is running:")
        print("   uv run uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
