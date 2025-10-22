"""AWS Bedrock Agent service for invoking agents."""
import json
from typing import Any

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from app.core.config import Settings
from app.core.exceptions import BedrockInvocationError, BedrockThrottlingError


class BedrockService:
    """Service for interacting with AWS Bedrock Agents."""

    def __init__(self, settings: Settings):
        """
        Initialize Bedrock client.

        Args:
            settings: Application settings containing AWS credentials
        """
        self.settings = settings
        self._client = None

    @property
    def client(self) -> Any:
        """Lazy-load boto3 client for bedrock-agent-runtime."""
        if self._client is None:
            session_kwargs = {
                "region_name": self.settings.aws_region,
                "aws_access_key_id": self.settings.aws_access_key_id,
                "aws_secret_access_key": self.settings.aws_secret_access_key,
            }

            if self.settings.aws_session_token:
                session_kwargs["aws_session_token"] = self.settings.aws_session_token

            session = boto3.Session(**session_kwargs)
            self._client = session.client("bedrock-agent-runtime")

        return self._client

    def invoke_agent(
        self,
        agent_id: str,
        agent_alias_id: str,
        session_id: str,
        input_text: str,
        enable_trace: bool = False,
    ) -> dict[str, Any] | str:
        """
        Invoke Bedrock Agent and return the response.

        Args:
            agent_id: Bedrock Agent ID
            agent_alias_id: Bedrock Agent Alias ID
            session_id: Session ID for conversation continuity
            input_text: Prompt text to send to the agent
            enable_trace: Whether to enable tracing

        Returns:
            Parsed JSON response as dict, or raw string if JSON parsing fails

        Raises:
            BedrockThrottlingError: If request is throttled
            BedrockInvocationError: If invocation fails
        """
        try:
            response = self.client.invoke_agent(
                agentId=agent_id,
                agentAliasId=agent_alias_id,
                sessionId=session_id,
                inputText=input_text,
                enableTrace=enable_trace,
            )

            # Extract completion from event stream
            completion_text = self._extract_completion(response)

            # Try to parse as JSON
            return self._parse_json_response(completion_text)

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")

            if error_code == "ThrottlingException":
                raise BedrockThrottlingError()
            elif error_code == "ValidationException":
                raise BedrockInvocationError(
                    f"Validation error: {e.response['Error']['Message']}", e
                )
            else:
                raise BedrockInvocationError(f"Client error: {str(e)}", e)

        except BotoCoreError as e:
            raise BedrockInvocationError(f"AWS SDK error: {str(e)}", e)

        except Exception as e:
            raise BedrockInvocationError(f"Unexpected error: {str(e)}", e)

    @staticmethod
    def _extract_completion(response: dict[str, Any]) -> str:
        """
        Extract completion text from Bedrock Agent response stream.

        Args:
            response: Response from invoke_agent call

        Returns:
            Concatenated completion text
        """
        completion_parts = []

        # The response contains an EventStream
        event_stream = response.get("completion", [])

        for event in event_stream:
            # Each event can contain a 'chunk' with completion text
            if "chunk" in event:
                chunk = event["chunk"]
                if "bytes" in chunk:
                    # Decode bytes to string
                    text = chunk["bytes"].decode("utf-8")
                    completion_parts.append(text)

        # If no completion found, return a default message
        if not completion_parts:
            return "Agent response received but no text content was extracted."

        return "".join(completion_parts)

    @staticmethod
    def _parse_json_response(response_text: str) -> dict[str, Any] | str:
        """
        Attempt to parse the agent response as JSON.

        Args:
            response_text: Raw response text from agent

        Returns:
            Parsed JSON as dict if successful, otherwise returns raw string
        """
        # Strip whitespace and newlines from start/end
        cleaned_text = response_text.strip()
        
        try:
            # Try to parse the entire response as JSON
            return json.loads(cleaned_text)
        except json.JSONDecodeError:
            # If that fails, try to find JSON within the text
            # Sometimes responses may have extra text before/after JSON
            try:
                # Look for JSON object boundaries
                start_idx = cleaned_text.find('{')
                end_idx = cleaned_text.rfind('}')
                
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = cleaned_text[start_idx:end_idx + 1]
                    return json.loads(json_str)
            except json.JSONDecodeError:
                pass
            
            # If all parsing attempts fail, return the raw string
            # This ensures we never lose data even if format is unexpected
            return cleaned_text
