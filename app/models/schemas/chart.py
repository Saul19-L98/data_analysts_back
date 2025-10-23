"""Pydantic schemas for chart transformation endpoint."""
from typing import Any, Literal

from pydantic import BaseModel, Field


class ChartParameters(BaseModel):
    """Parameters for chart generation from agent."""

    x_axis: str | None = Field(None, description="X-axis column name")
    y_axis: str | None = Field(None, description="Y-axis column name")
    aggregations: list[dict[str, Any]] | None = Field(None, description="Aggregation functions")
    group_by: list[str] | None = Field(None, description="Columns to group by")
    filters: list[dict[str, Any]] | None = Field(None, description="Filter conditions")
    sort: dict[str, str] | None = Field(None, description="Sort configuration")


class SuggestedChart(BaseModel):
    """Chart suggestion from Bedrock Agent."""

    title: str = Field(..., description="Chart title")
    chart_type: Literal["line", "bar", "area", "pie", "donut", "scatter", "radar", "radial"] = Field(
        ..., description="Type of chart (shadcn/recharts compatible)"
    )
    parameters: ChartParameters = Field(..., description="Chart parameters")
    insight: str | None = Field(None, description="Insight about the chart")
    priority: str | None = Field(None, description="Priority level")
    data_request_required: bool | None = Field(None, description="Whether data request is needed")


class TransformChartRequest(BaseModel):
    """Request to transform agent chart suggestions."""

    session_id: str = Field(..., description="Session ID from ingest response")
    suggested_charts: list[SuggestedChart] = Field(..., description="Charts suggested by agent")
    dataset: list[dict[str, Any]] | None = Field(
        None, description="Optional dataset as array of records for immediate chart data generation"
    )


class ShadcnChartConfig(BaseModel):
    """Shadcn chart configuration for a data key."""

    label: str = Field(..., description="Human-readable label")
    color: str = Field(..., description="Color value (CSS variable or hex)")


class ShadcnChartData(BaseModel):
    """Individual data point for shadcn chart."""

    # Dynamic fields will be added based on the data
    # This is a base model, actual data will have additional fields


class TransformedChart(BaseModel):
    """Transformed chart ready for shadcn visualization."""

    title: str = Field(..., description="Chart title")
    description: str | None = Field(None, description="Chart description/insight")
    chart_type: Literal["line", "bar", "area", "pie", "donut", "scatter", "radar", "radial"] = Field(
        ..., description="Chart type (shadcn/recharts compatible)"
    )
    chart_config: dict[str, ShadcnChartConfig] = Field(..., description="Chart configuration for colors/labels")
    chart_data: list[dict[str, Any]] = Field(..., description="Data formatted for shadcn charts")
    x_axis_key: str | None = Field(None, description="Key for X axis")
    y_axis_keys: list[str] = Field(default_factory=list, description="Keys for Y axis data")
    trend_percentage: float | None = Field(None, description="Trend percentage if applicable")


class TransformChartResponse(BaseModel):
    """Response with transformed charts."""

    message: str = Field(..., description="Success message")
    session_id: str = Field(..., description="Session ID")
    charts: list[TransformedChart] = Field(..., description="Transformed charts ready for visualization")
    total_charts: int = Field(..., description="Total number of charts transformed")
