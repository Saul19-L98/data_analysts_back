"""Pydantic schemas for API requests and responses."""
from typing import Any

from pydantic import BaseModel, Field


class IngestResponse(BaseModel):
    """Response model for the ingest endpoint."""

    message: str = Field(..., description="Success message")
    session_id: str = Field(..., description="Unique session ID for the Bedrock conversation")
    columns: list[str] = Field(..., description="List of column names from the dataset")
    dtypes: dict[str, str] = Field(..., description="Data types for each column")
    summary: "DataSummary" = Field(..., description="Statistical summary of the dataset")
    agent_reply: dict[str, Any] | str = Field(..., description="Parsed JSON response from the Bedrock Agent (or raw string if parsing fails)")
    sent_to_agent: bool = Field(default=True, description="Whether data was sent to agent")


class DataSummary(BaseModel):
    """Summary statistics from pandas DataFrame."""

    describe_numeric: dict[str, Any] | None = Field(
        default=None, description="Numeric column statistics from df.describe()"
    )
    describe_non_numeric: dict[str, Any] | None = Field(
        default=None, description="Non-numeric column statistics from df.describe()"
    )
    info_text: str = Field(..., description="Output from df.info()")


class ErrorResponse(BaseModel):
    """Standard error response."""

    detail: str = Field(..., description="Error message")
    error_type: str | None = Field(default=None, description="Type of error")
