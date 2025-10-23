"""Ingest service orchestrating file parsing, analysis, and Bedrock invocation."""
from typing import Any
import pandas as pd
import logging

from app.core.config import Settings
from app.core.utils import format_bedrock_prompt, generate_session_id
from app.models.schemas.ingest import DataSummary, IngestResponse
from app.services.bedrock_service import BedrockService
from app.services.data_analyzer import DataAnalyzerService
from app.services.file_parser import FileParserService
from app.utils.chart_formatting import format_chart_transform_request

logger = logging.getLogger(__name__)


class IngestService:
    """
    Orchestration service for the complete ingest workflow.

    Coordinates file parsing, data analysis, and Bedrock Agent invocation.
    """

    def __init__(self, settings: Settings):
        """
        Initialize ingest service.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.file_parser = FileParserService()
        self.data_analyzer = DataAnalyzerService()
        self.bedrock_service = BedrockService(settings)

    def _df_to_json_records(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        """
        Convert DataFrame to JSON-serializable list of records.
        
        Handles datetime conversions, NaN values, and type conversions for both CSV and XLSX files.
        
        Args:
            df: DataFrame to convert (from CSV or XLSX parsing)
            
        Returns:
            List of dictionaries (one per row), ready for JSON serialization
        """
        # Make a copy to avoid modifying original
        df_copy = df.copy()
        
        # Convert datetime columns to ISO format strings (YYYY-MM-DD)
        for col in df_copy.select_dtypes(include=['datetime64']).columns:
            df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d')
        
        # Replace NaN/NaT with None (JSON null)
        df_copy = df_copy.where(pd.notnull(df_copy), None)
        
        # Convert to list of dictionaries (records)
        records = df_copy.to_dict(orient='records')
        
        return records

    async def handle_upload(
        self,
        file_content: bytes,
        content_type: str,
        filename: str,
        message: str,
        agent_id: str,
        agent_alias_id: str,
    ) -> IngestResponse:
        """
        Handle complete file upload and analysis workflow.

        Args:
            file_content: Binary file content
            content_type: MIME type of file
            filename: Original filename
            message: User's context message
            agent_id: Bedrock Agent ID
            agent_alias_id: Bedrock Agent Alias ID

        Returns:
            IngestResponse with analysis results and agent reply

        Raises:
            Various exceptions from parsing, analysis, or Bedrock invocation
        """
        # 1. Parse file into DataFrame
        df = self.file_parser.parse_file(file_content, content_type, filename)

        # 2. Analyze DataFrame
        analysis = self.data_analyzer.analyze(df)

        # 3. Generate session ID
        session_id = generate_session_id()

        # 4. Format prompt for Bedrock
        prompt = format_bedrock_prompt(
            message=message,
            columns=analysis["columns"],
            dtypes=analysis["dtypes"],
            describe_numeric=analysis["describe_numeric"],
            describe_non_numeric=analysis["describe_non_numeric"],
            info_text=analysis["info_text"],
        )

        # 5. Invoke Bedrock Agent
        agent_reply = self.bedrock_service.invoke_agent(
            agent_id=agent_id,
            agent_alias_id=agent_alias_id,
            session_id=session_id,
            input_text=prompt,
            enable_trace=False,
        )

        # 6. Convert DataFrame to JSON records
        dataset = self._df_to_json_records(df)

        # 7. Format chart transform request (with validation and filtering)
        chart_transform_request = None
        try:
            chart_transform_request = format_chart_transform_request(
                session_id=session_id,
                agent_reply=agent_reply,
                dataset=dataset,
                filter_unsupported=True  # Auto-filter unsupported chart types
            )
            logger.info(
                f"Formatted chart request with {len(chart_transform_request['suggested_charts'])} valid charts"
            )
        except Exception as e:
            logger.warning(f"Failed to format chart transform request: {e}")
            # Continue without chart_transform_request (optional feature)

        # 8. Build response
        summary = DataSummary(
            describe_numeric=analysis["describe_numeric"],
            describe_non_numeric=analysis["describe_non_numeric"],
            info_text=analysis["info_text"],
        )

        return IngestResponse(
            message="Archivo analizado con éxito",
            session_id=session_id,
            columns=analysis["columns"],
            dtypes=analysis["dtypes"],
            summary=summary,
            sent_to_agent=True,
            dataset=dataset,
            chart_transform_request=chart_transform_request,
        )
