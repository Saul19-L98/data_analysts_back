"""Service for transforming agent chart suggestions to shadcn format."""
from typing import Any

from app.models.schemas.chart import (
    ShadcnChartConfig,
    SuggestedChart,
    TransformedChart,
)


class ChartTransformService:
    """
    Service to transform Bedrock Agent chart suggestions into shadcn-compatible format.

    Handles conversion of agent's chart parameters into the structure
    required by shadcn/recharts components.
    """

    # Color palette for chart series (shadcn chart colors)
    CHART_COLORS = [
        "hsl(var(--chart-1))",
        "hsl(var(--chart-2))",
        "hsl(var(--chart-3))",
        "hsl(var(--chart-4))",
        "hsl(var(--chart-5))",
    ]

    def transform_charts(
        self, suggested_charts: list[SuggestedChart], session_data: dict[str, Any] | None = None
    ) -> list[TransformedChart]:
        """
        Transform multiple chart suggestions into shadcn format.

        Args:
            suggested_charts: List of chart suggestions from agent
            session_data: Optional session data containing the analyzed dataset

        Returns:
            List of transformed charts ready for shadcn visualization
        """
        transformed = []

        for idx, chart in enumerate(suggested_charts):
            try:
                transformed_chart = self._transform_single_chart(chart, idx)
                transformed.append(transformed_chart)
            except Exception as e:
                # Log error but continue processing other charts
                print(f"Error transforming chart '{chart.title}': {e}")
                continue

        return transformed

    def _transform_single_chart(self, chart: SuggestedChart, color_index: int) -> TransformedChart:
        """
        Transform a single chart suggestion.

        Args:
            chart: Chart suggestion from agent
            color_index: Index for color selection

        Returns:
            Transformed chart in shadcn format
        """
        # Extract parameters
        params = chart.parameters
        x_axis_key = params.x_axis
        y_axis_key = params.y_axis

        # Build chart config (colors and labels)
        chart_config = self._build_chart_config(params, color_index)

        # Extract y-axis keys for the chart
        y_axis_keys = self._extract_y_axis_keys(params)

        # Generate sample/placeholder data structure
        # In a real scenario, this would query actual data based on parameters
        chart_data = self._generate_data_structure(params)

        return TransformedChart(
            title=chart.title,
            description=chart.insight,
            chart_type=chart.chart_type,
            chart_config=chart_config,
            chart_data=chart_data,
            x_axis_key=x_axis_key,
            y_axis_keys=y_axis_keys,
            trend_percentage=None,  # Could be calculated from actual data
        )

    def _build_chart_config(
        self, params: Any, color_index: int
    ) -> dict[str, ShadcnChartConfig]:
        """
        Build shadcn chartConfig object.

        Args:
            params: Chart parameters
            color_index: Index for color selection

        Returns:
            Dictionary mapping data keys to their config
        """
        chart_config = {}

        # Add configuration for y-axis
        if params.y_axis:
            chart_config[params.y_axis] = ShadcnChartConfig(
                label=self._format_label(params.y_axis),
                color=self.CHART_COLORS[color_index % len(self.CHART_COLORS)],
            )

        # Add configuration for aggregations
        if params.aggregations:
            for idx, agg in enumerate(params.aggregations):
                column = agg.get("column", "value")
                func = agg.get("func", "sum")
                key = f"{column}_{func}" if func != "sum" else column

                chart_config[key] = ShadcnChartConfig(
                    label=self._format_label(column),
                    color=self.CHART_COLORS[(color_index + idx) % len(self.CHART_COLORS)],
                )

        # Add configuration for group_by fields
        if params.group_by:
            for idx, group_field in enumerate(params.group_by):
                if group_field not in chart_config:
                    chart_config[group_field] = ShadcnChartConfig(
                        label=self._format_label(group_field),
                        color=self.CHART_COLORS[(color_index + idx + 1) % len(self.CHART_COLORS)],
                    )

        return chart_config

    def _extract_y_axis_keys(self, params: Any) -> list[str]:
        """
        Extract the data keys that will be plotted on Y axis.

        Args:
            params: Chart parameters

        Returns:
            List of data keys for Y axis
        """
        keys = []

        if params.y_axis:
            keys.append(params.y_axis)

        if params.aggregations:
            for agg in params.aggregations:
                column = agg.get("column", "value")
                func = agg.get("func", "sum")
                key = f"{column}_{func}" if func != "sum" else column
                if key not in keys:
                    keys.append(key)

        return keys if keys else ["value"]

    def _generate_data_structure(self, params: Any) -> list[dict[str, Any]]:
        """
        Generate placeholder data structure showing expected format.

        In production, this would query actual data from storage.

        Args:
            params: Chart parameters

        Returns:
            List of data points in shadcn format
        """
        # This is a placeholder showing the expected structure
        # Real implementation would fetch data from database/session storage
        data_structure = {
            "note": "Data structure placeholder",
            "description": "Use the chart parameters to query your actual dataset",
            "x_axis": params.x_axis or "category",
            "y_axis_keys": self._extract_y_axis_keys(params),
            "aggregations": params.aggregations or [],
            "filters": params.filters or [],
            "sort": params.sort or {},
        }

        # Return empty list with a note - frontend should handle data fetching
        return [data_structure]

    @staticmethod
    def _format_label(field_name: str) -> str:
        """
        Format a field name into a human-readable label.

        Args:
            field_name: Raw field name

        Returns:
            Formatted label
        """
        # Replace underscores with spaces and title case
        return field_name.replace("_", " ").title()
