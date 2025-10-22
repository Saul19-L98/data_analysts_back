"""Tests for utility functions."""
from app.core.utils import format_bedrock_prompt, generate_session_id


class TestUtils:
    """Test suite for utility functions."""

    def test_generate_session_id_format(self):
        """Test session ID generation format."""
        session_id = generate_session_id()

        assert session_id.startswith("sess_")
        assert len(session_id) > 20  # Should have timestamp and UUID
        assert "_" in session_id

    def test_generate_session_id_unique(self):
        """Test that session IDs are unique."""
        id1 = generate_session_id()
        id2 = generate_session_id()

        assert id1 != id2

    def test_format_bedrock_prompt_with_message(self):
        """Test prompt formatting with user message."""
        prompt = format_bedrock_prompt(
            message="Analyze sales data",
            columns=["date", "sales", "region"],
            dtypes={"date": "datetime64", "sales": "float64", "region": "object"},
            describe_numeric={"sales": {"mean": 1000.0}},
            describe_non_numeric={"region": {"count": 100}},
            info_text="<class 'pandas.core.frame.DataFrame'>",
        )

        assert "Analyze sales data" in prompt
        assert "date, sales, region" in prompt
        assert "DataFrame" in prompt
        assert "Task:" in prompt

    def test_format_bedrock_prompt_without_message(self):
        """Test prompt formatting without user message."""
        prompt = format_bedrock_prompt(
            message="",
            columns=["col1"],
            dtypes={"col1": "int64"},
            describe_numeric={"col1": {"mean": 5.0}},
            describe_non_numeric=None,
            info_text="info",
        )

        assert "(No message provided)" in prompt
        assert "col1" in prompt

    def test_format_bedrock_prompt_with_none_summaries(self):
        """Test prompt formatting with None summaries."""
        prompt = format_bedrock_prompt(
            message="Test",
            columns=["col1"],
            dtypes={"col1": "object"},
            describe_numeric=None,
            describe_non_numeric={"col1": {"count": 10}},
            info_text="info",
        )

        assert "Test" in prompt
        assert "col1" in prompt
        # Should not include numeric section
        assert "Non-numeric statistics" in prompt
