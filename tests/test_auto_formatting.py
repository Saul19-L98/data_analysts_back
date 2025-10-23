"""
Test the automatic chart formatting integration in IngestService.
Verifies that IngestResponse includes chart_transform_request field.
"""

import json
import httpx
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_ingest_with_chart_formatting():
    """Test that /api/v1/ingest returns formatted chart_transform_request."""
    
    print("\n" + "=" * 70)
    print("TEST: Ingest with Automatic Chart Formatting")
    print("=" * 70)
    
    # Test CSV file
    test_file = Path("paper_sales.csv")
    if not test_file.exists():
        print("❌ Test file not found: paper_sales.csv")
        return
    
    # Get agent credentials from environment
    agent_id = os.getenv("AGENT_ID")
    agent_alias_id = os.getenv("AGENT_ALIAS_ID")
    
    if not agent_id or not agent_alias_id:
        print("❌ Missing AGENT_ID or AGENT_ALIAS_ID in .env file")
        return
    
    # Upload file
    with httpx.Client(timeout=60.0) as client:
        with open(test_file, "rb") as f:
            response = client.post(
                "http://localhost:8000/api/v1/ingest",
                files={"file": (test_file.name, f, "text/csv")},
                data={
                    "agent_id": agent_id,
                    "agent_alias_id": agent_alias_id
                }
            )
    
    if response.status_code != 200:
        print(f"❌ Request failed with status {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    data = response.json()
    
    # Check response structure
    print(f"\n✅ Upload successful!")
    print(f"📊 Response fields:")
    for key in data.keys():
        print(f"   - {key}")
    
    # Check agent_reply
    agent_reply = data.get("agent_reply")
    if isinstance(agent_reply, str):
        print(f"\n⚠️  agent_reply is still a string (not parsed)")
        print(f"   Length: {len(agent_reply)} characters")
        try:
            parsed = json.loads(agent_reply)
            print(f"   ✅ Can be parsed manually")
            print(f"   Contains {len(parsed.get('suggested_charts', []))} charts")
        except json.JSONDecodeError:
            print(f"   ❌ Cannot be parsed as JSON")
    else:
        print(f"\n✅ agent_reply is a dict")
        print(f"   Contains {len(agent_reply.get('suggested_charts', []))} charts")
    
    # Check chart_transform_request (NEW FIELD)
    chart_request = data.get("chart_transform_request")
    if chart_request is None:
        print(f"\n❌ chart_transform_request field is missing or null")
        print(f"   This means formatting failed or was not implemented")
    else:
        print(f"\n✅ chart_transform_request field present!")
        print(f"\n📋 Chart Transform Request:")
        print(f"   Session ID: {chart_request.get('session_id')}")
        print(f"   Suggested Charts: {len(chart_request.get('suggested_charts', []))}")
        print(f"   Dataset Records: {len(chart_request.get('dataset', []))}")
        
        # Show chart details
        charts = chart_request.get("suggested_charts", [])
        if charts:
            print(f"\n📈 Valid Charts (after filtering):")
            for i, chart in enumerate(charts, 1):
                print(f"   {i}. {chart.get('title')} ({chart.get('chart_type')})")
                print(f"      Priority: {chart.get('priority', 'N/A')}")
        
        # Check if this can be sent directly to transform endpoint
        print(f"\n✅ This request can be sent directly to /api/v1/charts/transform")
        print(f"   No parsing or formatting needed on frontend!")
    
    # Save formatted request for inspection
    if chart_request:
        output_file = Path("test_auto_formatted_request.json")
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(chart_request, f, indent=2, ensure_ascii=False)
        print(f"\n💾 Saved formatted request to: {output_file}")
    
    # Compare raw agent_reply vs formatted
    if isinstance(agent_reply, str) and chart_request:
        try:
            parsed_agent = json.loads(agent_reply)
            original_charts = parsed_agent.get("suggested_charts", [])
            formatted_charts = chart_request.get("suggested_charts", [])
            
            print(f"\n📊 Filtering Results:")
            print(f"   Original charts: {len(original_charts)}")
            print(f"   Valid charts: {len(formatted_charts)}")
            print(f"   Filtered out: {len(original_charts) - len(formatted_charts)}")
            
            if len(original_charts) > len(formatted_charts):
                print(f"\n🔍 Unsupported chart types removed:")
                original_types = {c['title']: c['chart_type'] for c in original_charts}
                formatted_types = {c['title']: c['chart_type'] for c in formatted_charts}
                for title, chart_type in original_types.items():
                    if title not in formatted_types:
                        print(f"   ❌ {title} ({chart_type}) - unsupported")
        except:
            pass
    
    print("\n" + "=" * 70)


def test_direct_transform():
    """Test sending the formatted request directly to transform endpoint."""
    
    print("\n" + "=" * 70)
    print("TEST: Direct Chart Transform (Using Formatted Request)")
    print("=" * 70)
    
    # Check if we have the formatted request
    formatted_file = Path("test_auto_formatted_request.json")
    if not formatted_file.exists():
        print("❌ Run test_ingest_with_chart_formatting first")
        return
    
    # Load formatted request
    with formatted_file.open("r", encoding="utf-8") as f:
        request_data = json.load(f)
    
    print(f"\n📤 Sending formatted request to /api/v1/charts/transform...")
    print(f"   Charts: {len(request_data.get('suggested_charts', []))}")
    print(f"   Dataset: {len(request_data.get('dataset', []))} records")
    
    # Send to transform endpoint
    with httpx.Client(timeout=60.0) as client:
        response = client.post(
            "http://localhost:8000/api/v1/charts/transform",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
    
    if response.status_code != 200:
        print(f"\n❌ Transform failed with status {response.status_code}")
        print(f"Response: {response.text[:500]}")
        return
    
    result = response.json()
    
    print(f"\n✅ Transform successful!")
    print(f"\n📊 Transformed Charts:")
    print(f"   Total: {result.get('total_charts', 0)}")
    
    charts = result.get("charts", [])
    for i, chart in enumerate(charts, 1):
        print(f"\n   {i}. {chart.get('title')}")
        print(f"      Type: {chart.get('chart_type')}")
        print(f"      Data points: {len(chart.get('chart_data', []))}")
        print(f"      X-axis: {chart.get('x_axis_key')}")
        print(f"      Y-axes: {', '.join(chart.get('y_axis_keys', []))}")
    
    print("\n✅ Complete workflow successful!")
    print("   1. Upload → /api/v1/ingest")
    print("   2. Auto-format → chart_transform_request field")
    print("   3. Transform → /api/v1/charts/transform")
    print("   4. Ready to render in frontend!")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    # Test 1: Ingest with automatic formatting
    test_ingest_with_chart_formatting()
    
    # Test 2: Use formatted request directly
    test_direct_transform()
