"""Tests for chart transformation endpoint."""
from fastapi.testclient import TestClient


def test_transform_charts_success():
    """Test successful chart transformation."""
    from app.main import app

    client = TestClient(app)

    request_data = {
        "session_id": "sess_2025_10_22T12_00_00Z_abc123",
        "suggested_charts": [
            {
                "title": "Q3 2024 Sales Trend",
                "chart_type": "line",
                "parameters": {
                    "x_axis": "date",
                    "y_axis": "total_sales",
                    "aggregations": [{"column": "total_sales", "func": "sum"}],
                    "sort": {"by": "date", "order": "asc"},
                },
                "insight": "Shows sales patterns",
                "priority": "high",
                "data_request_required": True,
            }
        ],
    }

    response = client.post("/api/v1/charts/transform", json=request_data)

    assert response.status_code == 200
    data = response.json()

    assert data["message"] == "Gráficos transformados exitosamente"
    assert data["session_id"] == "sess_2025_10_22T12_00_00Z_abc123"
    assert data["total_charts"] == 1
    assert len(data["charts"]) == 1

    chart = data["charts"][0]
    assert chart["title"] == "Q3 2024 Sales Trend"
    assert chart["chart_type"] == "line"
    assert chart["description"] == "Shows sales patterns"
    assert "chart_config" in chart
    assert "chart_data" in chart
    assert chart["x_axis_key"] == "date"
    assert "total_sales" in chart["y_axis_keys"]


def test_transform_multiple_charts():
    """Test transformation of multiple charts."""
    from app.main import app

    client = TestClient(app)

    request_data = {
        "session_id": "sess_test_multi",
        "suggested_charts": [
            {
                "title": "Sales by Category",
                "chart_type": "bar",
                "parameters": {
                    "x_axis": "category",
                    "y_axis": "sales",
                    "aggregations": [{"column": "sales", "func": "sum"}],
                },
            },
            {
                "title": "Monthly Trend",
                "chart_type": "line",
                "parameters": {
                    "x_axis": "month",
                    "y_axis": "revenue",
                    "aggregations": [{"column": "revenue", "func": "avg"}],
                },
            },
        ],
    }

    response = client.post("/api/v1/charts/transform", json=request_data)

    assert response.status_code == 200
    data = response.json()

    assert data["total_charts"] == 2
    assert len(data["charts"]) == 2
    assert data["charts"][0]["title"] == "Sales by Category"
    assert data["charts"][1]["title"] == "Monthly Trend"


def test_transform_charts_missing_session_id():
    """Test chart transformation without session_id."""
    from app.main import app

    client = TestClient(app)

    request_data = {
        "suggested_charts": [
            {
                "title": "Test Chart",
                "chart_type": "bar",
                "parameters": {"x_axis": "x", "y_axis": "y"},
            }
        ]
    }

    response = client.post("/api/v1/charts/transform", json=request_data)
    assert response.status_code == 422  # Validation error


def test_transform_charts_empty_array():
    """Test chart transformation with empty charts array."""
    from app.main import app

    client = TestClient(app)

    request_data = {"session_id": "sess_empty", "suggested_charts": []}

    response = client.post("/api/v1/charts/transform", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["total_charts"] == 0
    assert len(data["charts"]) == 0


def test_chart_config_colors():
    """Test that chart configs have proper color assignments."""
    from app.main import app

    client = TestClient(app)

    request_data = {
        "session_id": "sess_colors",
        "suggested_charts": [
            {
                "title": "Multi-metric Chart",
                "chart_type": "area",
                "parameters": {
                    "x_axis": "date",
                    "aggregations": [
                        {"column": "revenue", "func": "sum"},
                        {"column": "profit", "func": "sum"},
                        {"column": "cost", "func": "sum"},
                    ],
                },
            }
        ],
    }

    response = client.post("/api/v1/charts/transform", json=request_data)

    assert response.status_code == 200
    data = response.json()

    chart = data["charts"][0]
    chart_config = chart["chart_config"]

    # Check that multiple metrics have different colors
    assert len(chart_config) > 0
    for key, config in chart_config.items():
        assert "label" in config
        assert "color" in config
        assert config["color"].startswith("hsl(var(--chart-")
