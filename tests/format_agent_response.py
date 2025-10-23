"""
Utility script to format agent response into valid JSON for chart transform endpoint.
Extracts suggested_charts and dataset from the raw /api/v1/ingest response.

Usage:
    uv run python format_agent_response.py <input_file> [output_file]
    
Example:
    uv run python format_agent_response.py agent_response.json chart_transform_request.json
"""

import json
import sys
from pathlib import Path


def extract_chart_transform_request(ingest_response: dict) -> dict:
    """
    Extract and format chart transform request from /api/v1/ingest response.
    
    Args:
        ingest_response: Full response from /api/v1/ingest endpoint
        
    Returns:
        Formatted request for /api/v1/charts/transform endpoint
    """
    # Parse agent_reply if it's a string (JSON embedded in JSON)
    agent_reply = ingest_response.get("agent_reply")
    if isinstance(agent_reply, str):
        try:
            agent_reply = json.loads(agent_reply)
        except json.JSONDecodeError as e:
            print(f"Warning: Could not parse agent_reply as JSON: {e}", file=sys.stderr)
            agent_reply = {}
    
    # Extract suggested charts
    suggested_charts = agent_reply.get("suggested_charts", [])
    
    # Filter out unsupported chart types (optional)
    supported_types = {"line", "bar", "area", "pie", "donut", "scatter", "radar", "radial"}
    valid_charts = []
    skipped_charts = []
    
    for chart in suggested_charts:
        chart_type = chart.get("chart_type")
        if chart_type in supported_types:
            valid_charts.append(chart)
        else:
            skipped_charts.append({
                "title": chart.get("title"),
                "chart_type": chart_type,
                "reason": "Unsupported chart type"
            })
    
    if skipped_charts:
        print(f"\nSkipped {len(skipped_charts)} unsupported chart(s):", file=sys.stderr)
        for skipped in skipped_charts:
            print(f"  - {skipped['title']} ({skipped['chart_type']}): {skipped['reason']}", file=sys.stderr)
    
    # Build chart transform request
    transform_request = {
        "session_id": ingest_response.get("session_id"),
        "suggested_charts": valid_charts,
        "dataset": ingest_response.get("dataset", [])
    }
    
    return transform_request


def format_agent_response(input_path: str, output_path: str = None) -> None:
    """
    Format agent response from file and save to output file.
    
    Args:
        input_path: Path to file containing /api/v1/ingest response
        output_path: Path to save formatted request (optional)
    """
    input_file = Path(input_path)
    
    if not input_file.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    
    # Read input file
    try:
        with input_file.open("r", encoding="utf-8") as f:
            ingest_response = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Format the request
    try:
        transform_request = extract_chart_transform_request(ingest_response)
    except Exception as e:
        print(f"Error formatting response: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Determine output path
    if output_path is None:
        output_path = input_file.parent / f"{input_file.stem}_transform{input_file.suffix}"
    
    output_file = Path(output_path)
    
    # Write output file
    try:
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(transform_request, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Successfully formatted agent response!")
        print(f"📄 Input:  {input_file}")
        print(f"📄 Output: {output_file}")
        print(f"\n📊 Summary:")
        print(f"   - Session ID: {transform_request['session_id']}")
        print(f"   - Valid charts: {len(transform_request['suggested_charts'])}")
        print(f"   - Dataset records: {len(transform_request['dataset'])}")
        
        # Show chart details
        if transform_request['suggested_charts']:
            print(f"\n📈 Charts included:")
            for i, chart in enumerate(transform_request['suggested_charts'], 1):
                print(f"   {i}. {chart['title']} ({chart['chart_type']})")
        
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python format_agent_response.py <input_file> [output_file]")
        print("\nExample:")
        print("  python format_agent_response.py agent_response.json")
        print("  python format_agent_response.py agent_response.json chart_request.json")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    format_agent_response(input_path, output_path)


if __name__ == "__main__":
    main()
