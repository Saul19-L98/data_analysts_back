"""Ingest API endpoint controller."""
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.core.config import Settings, get_settings
from app.core.exceptions import (
    AppException,
    FileSizeExceededError,
    UnsupportedFileTypeError,
    ValidationError,
)
from app.models.schemas.ingest import ErrorResponse, IngestResponse
from app.services.ingest_service import IngestService

router = APIRouter(prefix="/ingest", tags=["ingest"])


def get_ingest_service(settings: Settings = Depends(get_settings)) -> IngestService:
    """Dependency to get IngestService instance."""
    return IngestService(settings)


@router.post(
    "",
    response_model=IngestResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request - parsing error"},
        413: {"model": ErrorResponse, "description": "Payload too large"},
        415: {"model": ErrorResponse, "description": "Unsupported media type"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        429: {"model": ErrorResponse, "description": "Too many requests - throttled"},
        502: {"model": ErrorResponse, "description": "Bad gateway - Bedrock error"},
    },
)
async def ingest_file(
    file: UploadFile = File(..., description="CSV or XLSX file to analyze"),
    message: str = Form(default="", description="Optional context message"),
    agent_id: str = Form(..., description="Bedrock Agent ID"),
    agent_alias_id: str = Form(..., description="Bedrock Agent Alias ID"),
    service: IngestService = Depends(get_ingest_service),
    settings: Settings = Depends(get_settings),
) -> IngestResponse:
    """
    Upload and analyze a spreadsheet file using AWS Bedrock Agent.

    Accepts CSV or XLSX files, extracts schema and statistics,
    then sends the data profile along with the user message to a Bedrock Agent.

    Args:
        file: The spreadsheet file to upload
        message: Optional context message from the user
        agent_id: AWS Bedrock Agent ID to use
        agent_alias_id: AWS Bedrock Agent Alias ID to use
        service: Injected IngestService
        settings: Injected application settings

    Returns:
        Analysis results including agent response

    Raises:
        HTTPException: Various status codes for different error conditions
    """
    # Validate required fields
    if not agent_id or not agent_id.strip():
        raise ValidationError("agent_id is required and cannot be empty")

    if not agent_alias_id or not agent_alias_id.strip():
        raise ValidationError("agent_alias_id is required and cannot be empty")

    # Read file content
    file_content = await file.read()

    # Check file size
    file_size_mb = len(file_content) / (1024 * 1024)
    if file_size_mb > settings.max_file_size_mb:
        raise FileSizeExceededError(int(file_size_mb), settings.max_file_size_mb)

    # Validate content type
    content_type = file.content_type or "application/octet-stream"

    try:
        # Process the upload
        result = await service.handle_upload(
            file_content=file_content,
            content_type=content_type,
            filename=file.filename or "unknown",
            message=message.strip(),
            agent_id=agent_id.strip(),
            agent_alias_id=agent_alias_id.strip(),
        )

        return result

    except AppException:
        # Re-raise our custom exceptions
        raise

    except Exception as e:
        # Catch any unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )
