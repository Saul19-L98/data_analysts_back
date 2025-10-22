"""Data analyzer service for extracting schema and statistics."""
import io
from typing import Any

import numpy as np
import pandas as pd


class DataAnalyzerService:
    """Service for analyzing pandas DataFrames and extracting metadata."""

    @staticmethod
    def extract_columns(df: pd.DataFrame) -> list[str]:
        """Extract column names from DataFrame."""
        return df.columns.tolist()

    @staticmethod
    def extract_dtypes(df: pd.DataFrame) -> dict[str, str]:
        """
        Extract data types for each column.

        Returns:
            Dictionary mapping column names to string representations of dtypes
        """
        return {col: str(dtype) for col, dtype in df.dtypes.items()}

    @staticmethod
    def extract_numeric_summary(df: pd.DataFrame) -> dict[str, Any] | None:
        """
        Extract summary statistics for numeric columns.

        Returns:
            Dictionary representation of df.describe() for numeric columns,
            or None if no numeric columns exist
        """
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return None

        return numeric_df.describe().to_dict()

    @staticmethod
    def extract_non_numeric_summary(df: pd.DataFrame) -> dict[str, Any] | None:
        """
        Extract summary statistics for non-numeric columns.

        Returns:
            Dictionary representation of df.describe() for object columns,
            or None if no object columns exist
        """
        object_df = df.select_dtypes(include=["object"])
        if object_df.empty:
            return None

        return object_df.describe().to_dict()

    @staticmethod
    def extract_info_text(df: pd.DataFrame) -> str:
        """
        Capture df.info() output as a string.

        Returns:
            String representation of DataFrame info
        """
        buffer = io.StringIO()
        df.info(buf=buffer)
        return buffer.getvalue()

    @classmethod
    def analyze(cls, df: pd.DataFrame) -> dict[str, Any]:
        """
        Perform complete analysis of DataFrame.

        Args:
            df: pandas DataFrame to analyze

        Returns:
            Dictionary containing columns, dtypes, and summary statistics
        """
        return {
            "columns": cls.extract_columns(df),
            "dtypes": cls.extract_dtypes(df),
            "describe_numeric": cls.extract_numeric_summary(df),
            "describe_non_numeric": cls.extract_non_numeric_summary(df),
            "info_text": cls.extract_info_text(df),
        }
