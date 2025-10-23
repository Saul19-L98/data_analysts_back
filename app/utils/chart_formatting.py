"""
Utility functions for formatting and validating agent responses.
Used in services to ensure chart suggestions are properly formatted.
"""

import json
from typing import Any


def parse_agent_reply(agent_reply: str | dict) -> dict:
    """
    Parse agent_reply field from string to dict if needed.
    
    Args:
        agent_reply: Raw agent reply (string or dict)
        
    Returns:
        Parsed agent reply as dictionary
        
    Raises:
        ValueError: If agent_reply cannot be parsed
    """
    if isinstance(agent_reply, str):
        try:
            return json.loads(agent_reply)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in agent_reply: {e}") from e
    
    return agent_reply


def filter_supported_charts(
    charts: list[dict[str, Any]], 
    supported_types: set[str] | None = None
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """
    Filter charts by supported chart types.
    
    Args:
        charts: List of chart suggestions from agent
        supported_types: Set of supported chart type strings (if None, uses default)
        
    Returns:
        Tuple of (valid_charts, skipped_charts)
    """
    if supported_types is None:
        # Default supported types (shadcn/recharts compatible)
        supported_types = {"line", "bar", "area", "pie", "donut", "scatter", "radar", "radial"}
    
    valid_charts = []
    skipped_charts = []
    
    for chart in charts:
        chart_type = chart.get("chart_type")
        if chart_type in supported_types:
            valid_charts.append(chart)
        else:
            skipped_charts.append({
                "title": chart.get("title"),
                "chart_type": chart_type,
                "reason": f"Unsupported chart type: {chart_type}"
            })
    
    return valid_charts, skipped_charts


def extract_chart_suggestions(agent_reply: str | dict) -> list[dict[str, Any]]:
    """
    Extract and validate chart suggestions from agent reply.
    
    Args:
        agent_reply: Agent reply string or dict
        
    Returns:
        List of valid chart suggestions
        
    Raises:
        ValueError: If agent_reply is invalid or missing required fields
    """
    # Parse if string
    parsed_reply = parse_agent_reply(agent_reply)
    
    # Extract suggested_charts
    suggested_charts = parsed_reply.get("suggested_charts")
    if not suggested_charts:
        raise ValueError("No 'suggested_charts' found in agent_reply")
    
    if not isinstance(suggested_charts, list):
        raise ValueError("'suggested_charts' must be a list")
    
    return suggested_charts


def format_chart_transform_request(
    session_id: str,
    agent_reply: str | dict,
    dataset: list[dict[str, Any]],
    filter_unsupported: bool = True
) -> dict[str, Any]:
    """
    Format a complete chart transform request from ingest response data.
    
    Args:
        session_id: Session ID from ingest response
        agent_reply: Agent reply (string or dict)
        dataset: Dataset records from ingest response
        filter_unsupported: Whether to filter out unsupported chart types
        
    Returns:
        Formatted request for chart transform endpoint
        
    Raises:
        ValueError: If data is invalid
    """
    # Extract charts from agent reply
    suggested_charts = extract_chart_suggestions(agent_reply)
    
    # Optionally filter unsupported types
    if filter_unsupported:
        suggested_charts, skipped = filter_supported_charts(suggested_charts)
        if skipped:
            # Log skipped charts (in production, use proper logging)
            print(f"Warning: Skipped {len(skipped)} unsupported chart(s)")
    
    # Build request
    return {
        "session_id": session_id,
        "suggested_charts": suggested_charts,
        "dataset": dataset
    }


def validate_chart_suggestion(chart: dict[str, Any]) -> tuple[bool, str | None]:
    """
    Validate a single chart suggestion structure.
    
    Args:
        chart: Chart suggestion dictionary
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = ["title", "chart_type", "parameters"]
    
    # Check required fields
    for field in required_fields:
        if field not in chart:
            return False, f"Missing required field: {field}"
    
    # Validate chart_type
    supported_types = {"line", "bar", "area", "pie", "donut", "scatter", "radar", "radial"}
    if chart["chart_type"] not in supported_types:
        return False, f"Unsupported chart type: {chart['chart_type']}"
    
    # Validate parameters is a dict
    if not isinstance(chart.get("parameters"), dict):
        return False, "Field 'parameters' must be a dictionary"
    
    return True, None


def validate_all_chart_suggestions(charts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Validate all chart suggestions and return errors.
    
    Args:
        charts: List of chart suggestions
        
    Returns:
        List of validation errors (empty if all valid)
    """
    errors = []
    
    for i, chart in enumerate(charts):
        is_valid, error_msg = validate_chart_suggestion(chart)
        if not is_valid:
            errors.append({
                "chart_index": i,
                "chart_title": chart.get("title", "Unknown"),
                "error": error_msg
            })
    
    return errors
