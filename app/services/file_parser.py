"""File parser service for handling CSV and Excel files."""
import io
from typing import BinaryIO

import pandas as pd

from app.core.exceptions import FileParsingError, UnsupportedFileTypeError


class FileParserService:
    """Service for parsing uploaded files into pandas DataFrames."""

    SUPPORTED_CSV_TYPES = {"text/csv", "application/csv"}
    SUPPORTED_EXCEL_TYPES = {
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
    }

    @classmethod
    def parse_file(cls, file_content: bytes, content_type: str, filename: str) -> pd.DataFrame:
        """
        Parse uploaded file into a pandas DataFrame.

        Args:
            file_content: Binary file content
            content_type: MIME type of the file
            filename: Original filename

        Returns:
            pandas DataFrame

        Raises:
            UnsupportedFileTypeError: If file type is not supported
            FileParsingError: If parsing fails
        """
        if content_type in cls.SUPPORTED_CSV_TYPES or filename.lower().endswith(".csv"):
            return cls._parse_csv(file_content)
        elif content_type in cls.SUPPORTED_EXCEL_TYPES or filename.lower().endswith(
            (".xlsx", ".xls")
        ):
            return cls._parse_excel(file_content)
        else:
            raise UnsupportedFileTypeError(content_type)

    @staticmethod
    def _parse_csv(file_content: bytes) -> pd.DataFrame:
        """Parse CSV file content."""
        try:
            # Use BytesIO to read from bytes
            buffer = io.BytesIO(file_content)
            # Try UTF-8 first, fallback to latin1
            try:
                df = pd.read_csv(buffer, encoding="utf-8")
            except UnicodeDecodeError:
                buffer.seek(0)
                df = pd.read_csv(buffer, encoding="latin1")

            # Strip whitespace from column names
            df.columns = df.columns.str.strip()

            return df
        except Exception as e:
            raise FileParsingError(f"Failed to parse CSV file: {str(e)}")

    @staticmethod
    def _parse_excel(file_content: bytes) -> pd.DataFrame:
        """Parse Excel file content."""
        try:
            # Use BytesIO to read from bytes
            buffer = io.BytesIO(file_content)
            # Read first sheet by default
            df = pd.read_excel(buffer, sheet_name=0, engine="openpyxl")

            # Strip whitespace from column names
            df.columns = df.columns.str.strip()

            return df
        except Exception as e:
            raise FileParsingError(f"Failed to parse Excel file: {str(e)}")
