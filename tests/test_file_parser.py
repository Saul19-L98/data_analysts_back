"""Tests for file parser service."""
import pandas as pd
import pytest

from app.core.exceptions import FileParsingError, UnsupportedFileTypeError
from app.services.file_parser import FileParserService


class TestFileParserService:
    """Test suite for FileParserService."""

    def test_parse_csv_success(self):
        """Test successful CSV parsing."""
        csv_content = b"name,age,city\nAlice,30,NYC\nBob,25,LA"
        df = FileParserService.parse_file(csv_content, "text/csv", "test.csv")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2
        assert list(df.columns) == ["name", "age", "city"]
        assert df.iloc[0]["name"] == "Alice"

    def test_parse_csv_with_whitespace_columns(self):
        """Test CSV parsing with whitespace in column names."""
        csv_content = b" name , age , city \nAlice,30,NYC"
        df = FileParserService.parse_file(csv_content, "text/csv", "test.csv")

        # Columns should be stripped
        assert list(df.columns) == ["name", "age", "city"]

    def test_parse_unsupported_file_type(self):
        """Test parsing unsupported file type raises error."""
        with pytest.raises(UnsupportedFileTypeError) as exc_info:
            FileParserService.parse_file(b"content", "application/pdf", "test.pdf")

        assert "application/pdf" in str(exc_info.value.message)

    def test_csv_detection_by_extension(self):
        """Test CSV detection by file extension."""
        csv_content = b"col1,col2\nval1,val2"
        # Even with wrong content type, extension should work
        df = FileParserService.parse_file(csv_content, "application/octet-stream", "data.csv")

        assert len(df) == 1
        assert list(df.columns) == ["col1", "col2"]
