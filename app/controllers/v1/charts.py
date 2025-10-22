"""Chart transformation API endpoint controller."""
from fastapi import APIRouter, status

from app.models.schemas.chart import TransformChartRequest, TransformChartResponse
from app.services.chart_transform_service import ChartTransformService

router = APIRouter(prefix="/charts", tags=["charts"])


@router.post(
    "/transform",
    response_model=TransformChartResponse,
    status_code=status.HTTP_200_OK,
    summary="Transform agent chart suggestions to shadcn format",
    description="Converts Bedrock Agent chart suggestions into shadcn/recharts compatible format",
)
async def transform_charts(request: TransformChartRequest) -> TransformChartResponse:
    """
    Transform agent's suggested charts into shadcn-compatible format.

    Takes the `suggested_charts` array from the agent's response and transforms
    each chart into the structure required by shadcn chart components.

    Args:
        request: Contains session_id and suggested_charts from agent

    Returns:
        Transformed charts ready for shadcn visualization

    Example Request:
        ```json
        {
          "session_id": "sess_2025_10_22T12_00_00Z_abc123",
          "suggested_charts": [
            {
              "title": "Q3 2024 Sales Trend",
              "chart_type": "line",
              "parameters": {
                "x_axis": "date",
                "y_axis": "total_sales",
                "aggregations": [{"column": "total_sales", "func": "sum"}],
                "sort": {"by": "date", "order": "asc"}
              },
              "insight": "Shows sales patterns",
              "priority": "high"
            }
          ]
        }
        ```

    Example Response:
        ```json
        {
          "message": "Gráficos transformados exitosamente",
          "session_id": "sess_2025_10_22T12_00_00Z_abc123",
          "charts": [
            {
              "title": "Q3 2024 Sales Trend",
              "description": "Shows sales patterns",
              "chart_type": "line",
              "chart_config": {
                "total_sales": {
                  "label": "Total Sales",
                  "color": "hsl(var(--chart-1))"
                }
              },
              "chart_data": [...],
              "x_axis_key": "date",
              "y_axis_keys": ["total_sales"]
            }
          ],
          "total_charts": 1
        }
        ```
    """
    service = ChartTransformService()

    # Transform the charts with optional dataset
    transformed_charts = service.transform_charts(
        request.suggested_charts,
        dataset=request.dataset
    )

    return TransformChartResponse(
        message="Gráficos transformados exitosamente",
        session_id=request.session_id,
        charts=transformed_charts,
        total_charts=len(transformed_charts),
    )
