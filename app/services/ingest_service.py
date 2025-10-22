"""Ingest service orchestrating file parsing, analysis, and Bedrock invocation."""
from typing import Any

from app.core.config import Settings
from app.core.utils import format_bedrock_prompt, generate_session_id
from app.models.schemas.ingest import DataSummary, IngestResponse
from app.services.bedrock_service import BedrockService
from app.services.data_analyzer import DataAnalyzerService
from app.services.file_parser import FileParserService


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

        # 6. Build response
        summary = DataSummary(
            describe_numeric=analysis["describe_numeric"],
            describe_non_numeric=analysis["describe_non_numeric"],
            info_text=analysis["info_text"],
        )

        return IngestResponse(
            session_id=session_id,
            agent_id=agent_id,
            agent_alias_id=agent_alias_id,
            columns=analysis["columns"],
            dtypes=analysis["dtypes"],
            summary=summary,
            agent_reply=agent_reply,
            sent_to_agent=True,
        )
