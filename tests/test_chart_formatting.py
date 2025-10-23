"""
Test script demonstrating agent response formatting utilities.
Shows how to parse, validate, and format agent responses for chart transformation.
"""

import json
from pathlib import Path
from app.utils.chart_formatting import (
    parse_agent_reply,
    filter_supported_charts,
    extract_chart_suggestions,
    format_chart_transform_request,
    validate_all_chart_suggestions
)


def test_parse_agent_reply():
    """Test parsing agent reply from string."""
    print("=" * 60)
    print("TEST 1: Parse Agent Reply")
    print("=" * 60)
    
    # Simulate agent reply as JSON string (as returned by Bedrock)
    agent_reply_str = json.dumps({
        "version": "1.0",
        "suggested_charts": [
            {"title": "Sales Trend", "chart_type": "line", "parameters": {}},
            {"title": "Distribution", "chart_type": "bar", "parameters": {}}
        ]
    })
    
    parsed = parse_agent_reply(agent_reply_str)
    print(f"✅ Parsed from string: {len(parsed['suggested_charts'])} charts")
    
    # Test with dict (already parsed)
    parsed2 = parse_agent_reply(parsed)
    print(f"✅ Parsed from dict: {len(parsed2['suggested_charts'])} charts")
    print()


def test_filter_supported_charts():
    """Test filtering unsupported chart types."""
    print("=" * 60)
    print("TEST 2: Filter Supported Charts")
    print("=" * 60)
    
    charts = [
        {"title": "Valid Line", "chart_type": "line", "parameters": {}},
        {"title": "Valid Bar", "chart_type": "bar", "parameters": {}},
        {"title": "Invalid Histogram", "chart_type": "histogram", "parameters": {}},
        {"title": "Valid Scatter", "chart_type": "scatter", "parameters": {}},
        {"title": "Invalid Treemap", "chart_type": "treemap", "parameters": {}}
    ]
    
    valid, skipped = filter_supported_charts(charts)
    
    print(f"📊 Total charts: {len(charts)}")
    print(f"✅ Valid charts: {len(valid)}")
    for chart in valid:
        print(f"   - {chart['title']} ({chart['chart_type']})")
    
    print(f"❌ Skipped charts: {len(skipped)}")
    for chart in skipped:
        print(f"   - {chart['title']} ({chart['chart_type']}): {chart['reason']}")
    print()


def test_extract_chart_suggestions():
    """Test extracting chart suggestions from agent reply."""
    print("=" * 60)
    print("TEST 3: Extract Chart Suggestions")
    print("=" * 60)
    
    agent_reply = {
        "version": "1.0",
        "context": {"dataset_name": "test"},
        "suggested_charts": [
            {"title": "Chart 1", "chart_type": "line", "parameters": {"x_axis": "date"}},
            {"title": "Chart 2", "chart_type": "bar", "parameters": {"x_axis": "category"}}
        ]
    }
    
    charts = extract_chart_suggestions(agent_reply)
    print(f"✅ Extracted {len(charts)} charts from agent reply")
    for i, chart in enumerate(charts, 1):
        print(f"   {i}. {chart['title']} ({chart['chart_type']})")
    print()


def test_format_chart_transform_request():
    """Test formatting complete chart transform request."""
    print("=" * 60)
    print("TEST 4: Format Chart Transform Request")
    print("=" * 60)
    
    session_id = "sess_test_123"
    agent_reply = {
        "suggested_charts": [
            {
                "title": "Monthly Trend",
                "chart_type": "line",
                "parameters": {"x_axis": "date", "y_axis": "sales"}
            },
            {
                "title": "Category Breakdown",
                "chart_type": "bar",
                "parameters": {"x_axis": "category", "y_axis": "total"}
            },
            {
                "title": "Unsupported",
                "chart_type": "histogram",
                "parameters": {"x_axis": "value"}
            }
        ]
    }
    dataset = [
        {"date": "2024-01", "category": "A", "sales": 100, "total": 500},
        {"date": "2024-02", "category": "B", "sales": 150, "total": 600}
    ]
    
    # Format request (with filtering)
    request = format_chart_transform_request(
        session_id=session_id,
        agent_reply=agent_reply,
        dataset=dataset,
        filter_unsupported=True
    )
    
    print(f"✅ Formatted chart transform request:")
    print(f"   Session ID: {request['session_id']}")
    print(f"   Charts: {len(request['suggested_charts'])} (filtered from 3)")
    print(f"   Dataset records: {len(request['dataset'])}")
    print(f"\n📋 Request structure:")
    print(json.dumps(request, indent=2)[:500] + "...")
    print()


def test_validate_chart_suggestions():
    """Test validation of chart suggestions."""
    print("=" * 60)
    print("TEST 5: Validate Chart Suggestions")
    print("=" * 60)
    
    charts = [
        # Valid chart
        {
            "title": "Valid Chart",
            "chart_type": "line",
            "parameters": {"x_axis": "date"}
        },
        # Missing title
        {
            "chart_type": "bar",
            "parameters": {"x_axis": "category"}
        },
        # Invalid chart type
        {
            "title": "Invalid Type",
            "chart_type": "invalid_type",
            "parameters": {}
        },
        # Missing parameters
        {
            "title": "Missing Params",
            "chart_type": "area"
        }
    ]
    
    errors = validate_all_chart_suggestions(charts)
    
    if errors:
        print(f"❌ Found {len(errors)} validation error(s):")
        for error in errors:
            print(f"   Chart #{error['chart_index']} ({error['chart_title']}): {error['error']}")
    else:
        print("✅ All charts are valid")
    print()


def test_real_world_scenario():
    """Test with real-world agent response structure."""
    print("=" * 60)
    print("TEST 6: Real-World Scenario")
    print("=" * 60)
    
    # Simulate /api/v1/ingest response
    ingest_response = {
        "message": "Archivo analizado con éxito",
        "session_id": "sess_2025_10_22T22_58_57Z_098bc5ca",
        "columns": ["date", "paper_type", "quantity", "price", "total_sales"],
        "agent_reply": json.dumps({  # Agent reply is JSON string
            "version": "1.0",
            "suggested_charts": [
                {
                    "title": "Monthly Sales Trend",
                    "chart_type": "line",
                    "parameters": {"x_axis": "date", "y_axis": "total_sales"},
                    "insight": "Shows monthly sales evolution",
                    "priority": "high"
                },
                {
                    "title": "Sales by Paper Type",
                    "chart_type": "bar",
                    "parameters": {"x_axis": "paper_type", "y_axis": "total_sales"},
                    "insight": "Compares sales across types",
                    "priority": "medium"
                },
                {
                    "title": "Scatter Analysis",
                    "chart_type": "scatter",
                    "parameters": {"x_axis": "quantity", "y_axis": "total_sales"},
                    "insight": "Correlation analysis",
                    "priority": "low"
                }
            ]
        }),
        "dataset": [
            {"date": "2024-10-01", "paper_type": "A4", "quantity": 150, "price": 5.5, "total_sales": 825.0},
            {"date": "2024-10-02", "paper_type": "Letter", "quantity": 200, "price": 4.75, "total_sales": 950.0}
        ]
    }
    
    # Format the request
    transform_request = format_chart_transform_request(
        session_id=ingest_response["session_id"],
        agent_reply=ingest_response["agent_reply"],
        dataset=ingest_response["dataset"],
        filter_unsupported=True
    )
    
    print("✅ Successfully formatted real-world agent response!")
    print(f"\n📊 Summary:")
    print(f"   Session: {transform_request['session_id']}")
    print(f"   Charts: {len(transform_request['suggested_charts'])}")
    print(f"   Dataset: {len(transform_request['dataset'])} records")
    
    print(f"\n📈 Chart Details:")
    for i, chart in enumerate(transform_request['suggested_charts'], 1):
        print(f"   {i}. {chart['title']}")
        print(f"      Type: {chart['chart_type']}")
        print(f"      Priority: {chart.get('priority', 'N/A')}")
    
    # Validate
    errors = validate_all_chart_suggestions(transform_request['suggested_charts'])
    if errors:
        print(f"\n❌ Validation errors: {len(errors)}")
    else:
        print(f"\n✅ All charts validated successfully!")
    
    # Save to file
    output_file = Path("test_formatted_request.json")
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(transform_request, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Saved formatted request to: {output_file}")
    print()


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("AGENT RESPONSE FORMATTING UTILITY TESTS")
    print("=" * 60 + "\n")
    
    test_parse_agent_reply()
    test_filter_supported_charts()
    test_extract_chart_suggestions()
    test_format_chart_transform_request()
    test_validate_chart_suggestions()
    test_real_world_scenario()
    
    print("=" * 60)
    print("✅ ALL TESTS COMPLETED")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
