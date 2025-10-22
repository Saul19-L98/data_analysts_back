"""Utility functions for the application."""
from datetime import datetime, timezone
import uuid


def generate_session_id() -> str:
    """
    Generate a unique session ID for Bedrock Agent conversations.
    
    Format: sess_YYYY_MM_DDTHH_MM_SSZ_uuid
    """
    timestamp = datetime.now(timezone.utc).strftime("%Y_%m_%dT%H_%M_%SZ")
    unique_id = uuid.uuid4().hex[:8]
    return f"sess_{timestamp}_{unique_id}"


def format_bedrock_prompt(
    message: str,
    columns: list[str],
    dtypes: dict[str, str],
    describe_numeric: dict | None,
    describe_non_numeric: dict | None,
    info_text: str,
) -> str:
    """
    Format the prompt to send to Bedrock Agent.
    
    Args:
        message: User's message/context
        columns: List of column names
        dtypes: Dictionary of column names to data types
        describe_numeric: Numeric summary from df.describe()
        describe_non_numeric: Non-numeric summary from df.describe()
        info_text: Output from df.info()
    
    Returns:
        Formatted prompt string
    """
    prompt_parts = [
        "User message:",
        message or "(No message provided)",
        "",
        "Dataset profile:",
        f"- Columns: {', '.join(columns)}",
        f"- Data types: {dtypes}",
        "",
    ]

    if describe_numeric:
        prompt_parts.extend(
            [
                "Numeric statistics (df.describe()):",
                str(describe_numeric),
                "",
            ]
        )

    if describe_non_numeric:
        prompt_parts.extend(
            [
                "Non-numeric statistics (df.describe()):",
                str(describe_non_numeric),
                "",
            ]
        )

    prompt_parts.extend(
        [
            "DataFrame info:",
            info_text,
            "",
            "Task:",
            "1) Summarize relevant insights from this dataset.",
            "2) Identify potential data quality issues.",
            "3) Ask at most 3 precise follow-up questions to clarify analysis goals.",
        ]
    )

    return "\n".join(prompt_parts)
