"""Tests for data analyzer service."""
import pandas as pd
import pytest

from app.services.data_analyzer import DataAnalyzerService


class TestDataAnalyzerService:
    """Test suite for DataAnalyzerService."""

    @pytest.fixture
    def sample_df(self):
        """Create a sample DataFrame for testing."""
        return pd.DataFrame(
            {
                "id": [1, 2, 3],
                "name": ["Alice", "Bob", "Charlie"],
                "age": [30, 25, 35],
                "score": [85.5, 92.0, 78.5],
            }
        )

    def test_extract_columns(self, sample_df):
        """Test column extraction."""
        columns = DataAnalyzerService.extract_columns(sample_df)
        assert columns == ["id", "name", "age", "score"]

    def test_extract_dtypes(self, sample_df):
        """Test dtype extraction."""
        dtypes = DataAnalyzerService.extract_dtypes(sample_df)

        assert "id" in dtypes
        assert "name" in dtypes
        assert "age" in dtypes
        assert "score" in dtypes
        assert "int" in dtypes["id"]
        assert "object" in dtypes["name"]

    def test_extract_numeric_summary(self, sample_df):
        """Test numeric summary extraction."""
        summary = DataAnalyzerService.extract_numeric_summary(sample_df)

        assert summary is not None
        assert "id" in summary
        assert "age" in summary
        assert "score" in summary
        assert "count" in summary["id"]
        assert "mean" in summary["age"]

    def test_extract_non_numeric_summary(self, sample_df):
        """Test non-numeric summary extraction."""
        summary = DataAnalyzerService.extract_non_numeric_summary(sample_df)

        assert summary is not None
        assert "name" in summary
        assert "count" in summary["name"]
        assert "unique" in summary["name"]

    def test_extract_info_text(self, sample_df):
        """Test info text extraction."""
        info_text = DataAnalyzerService.extract_info_text(sample_df)

        assert "DataFrame" in info_text
        assert "4 entries" in info_text or "4 columns" in info_text
        assert "3 entries" in info_text or "RangeIndex: 3" in info_text

    def test_analyze_complete(self, sample_df):
        """Test complete analysis."""
        result = DataAnalyzerService.analyze(sample_df)

        assert "columns" in result
        assert "dtypes" in result
        assert "describe_numeric" in result
        assert "describe_non_numeric" in result
        assert "info_text" in result

        assert len(result["columns"]) == 4
        assert len(result["dtypes"]) == 4

    def test_empty_dataframe(self):
        """Test analysis of empty DataFrame."""
        empty_df = pd.DataFrame()
        result = DataAnalyzerService.analyze(empty_df)

        assert result["columns"] == []
        assert result["dtypes"] == {}
        assert result["describe_numeric"] is None
        assert result["describe_non_numeric"] is None

    def test_all_numeric_dataframe(self):
        """Test DataFrame with only numeric columns."""
        numeric_df = pd.DataFrame({"a": [1, 2, 3], "b": [4.5, 5.5, 6.5]})
        result = DataAnalyzerService.analyze(numeric_df)

        assert result["describe_numeric"] is not None
        assert result["describe_non_numeric"] is None

    def test_all_non_numeric_dataframe(self):
        """Test DataFrame with only non-numeric columns."""
        text_df = pd.DataFrame({"name": ["Alice", "Bob"], "city": ["NYC", "LA"]})
        result = DataAnalyzerService.analyze(text_df)

        assert result["describe_numeric"] is None
        assert result["describe_non_numeric"] is not None
