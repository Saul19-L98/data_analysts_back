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

        result = "".join(completion_parts)
        
        # Log the result for debugging (first 500 chars)
        print(f"[DEBUG] Extracted completion length: {len(result)} chars")
        print(f"[DEBUG] First 200 chars: {result[:200]}")
        print(f"[DEBUG] Last 200 chars: {result[-200:]}")
        
        return result

    @staticmethod
    def _parse_json_response(response_text: str) -> dict[str, Any] | str:
        """
        Attempt to parse the agent response as JSON with multiple strategies.

        Args:
            response_text: Raw response text from agent

        Returns:
            Parsed JSON as dict if successful, otherwise returns raw string
        """
        import re
        
        # Strip whitespace and newlines from start/end
        cleaned_text = response_text.strip()
        
        # Strategy 1: Direct JSON parsing
        try:
            parsed = json.loads(cleaned_text)
            print(f"[DEBUG] Strategy 1 succeeded - Direct JSON parsing")
            return parsed
        except json.JSONDecodeError as e:
            print(f"[DEBUG] Strategy 1 failed: {str(e)}")
        
        # Strategy 2: Find JSON boundaries and extract
        try:
            start_idx = cleaned_text.find('{')
            end_idx = cleaned_text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = cleaned_text[start_idx:end_idx + 1]
                parsed = json.loads(json_str)
                print(f"[DEBUG] Strategy 2 succeeded - Boundary extraction")
                return parsed
        except json.JSONDecodeError as e:
            print(f"[DEBUG] Strategy 2 failed: {str(e)}")
        
        # Strategy 3: Find last comma before truncation and cut there
        try:
            start_idx = cleaned_text.find('{')
            if start_idx != -1:
                json_str = cleaned_text[start_idx:]
                
                # Find the last comma in the string
                last_comma = json_str.rfind(',')
                
                if last_comma > 0:
                    # Truncate at the last comma
                    json_str = json_str[:last_comma]
                    print(f"[DEBUG] Strategy 3 - Truncated at last comma (position {last_comma})")
                
                # Clean up
                json_str = json_str.rstrip()
                
                # Count brackets and braces
                open_braces = json_str.count('{')
                close_braces = json_str.count('}')
                open_brackets = json_str.count('[')
                close_brackets = json_str.count(']')
                
                missing_brackets = open_brackets - close_brackets
                missing_braces = open_braces - close_braces
                
                print(f"[DEBUG] Strategy 3 - Braces: {open_braces} open, {close_braces} close")
                print(f"[DEBUG] Strategy 3 - Brackets: {open_brackets} open, {close_brackets} close")
                
                if missing_brackets >= 0 and missing_braces >= 0:
                    # Close the JSON
                    json_str += ']' * missing_brackets
                    json_str += '}' * missing_braces
                    print(f"[DEBUG] Strategy 3 - Added {missing_brackets} brackets, {missing_braces} braces")
                    
                    parsed = json.loads(json_str)
                    print(f"[DEBUG] Strategy 3 succeeded - Completed incomplete JSON")
                    return parsed
        except json.JSONDecodeError as e:
            print(f"[DEBUG] Strategy 3 failed: {str(e)}")
        except Exception as e:
            print(f"[DEBUG] Strategy 3 error: {str(e)}")
        
        # Strategy 4: Look for ]\s*} patterns (array closing before object close)
        try:
            start_idx = cleaned_text.find('{')
            if start_idx != -1:
                json_str = cleaned_text[start_idx:]
                
                # Find all occurrences of ], or ]\s*}
                matches = list(re.finditer(r'\]\s*[},]', json_str))
                
                if matches:
                    # Use the SECOND-to-last match (to avoid cutting inside incomplete structure)
                    # Or if only one, use it
                    match_idx = -2 if len(matches) > 1 else -1
                    match = matches[match_idx]
                    truncate_pos = match.start() + 1  # Include the ]
                    
                    json_str = json_str[:truncate_pos]
                    print(f"[DEBUG] Strategy 4 - Truncated at array close pattern (position {truncate_pos}, match {match_idx})")
                    
                    # Clean and close
                    json_str = json_str.rstrip()
                    
                    # Count and close
                    open_braces = json_str.count('{')
                    close_braces = json_str.count('}')
                    open_brackets = json_str.count('[')
                    close_brackets = json_str.count(']')
                    
                    missing_brackets = open_brackets - close_brackets
                    missing_braces = open_braces - close_braces
                    
                    print(f"[DEBUG] Strategy 4 - Braces: {open_braces} open, {close_braces} close")
                    print(f"[DEBUG] Strategy 4 - Brackets: {open_brackets} open, {close_brackets} close")
                    
                    if missing_brackets >= 0 and missing_braces >= 0:
                        json_str += ']' * missing_brackets
                        json_str += '}' * missing_braces
                        print(f"[DEBUG] Strategy 4 - Added {missing_brackets} brackets, {missing_braces} braces")
                        
                        parsed = json.loads(json_str)
                        print(f"[DEBUG] Strategy 4 succeeded - Completed incomplete JSON")
                        return parsed
        except json.JSONDecodeError as e:
            print(f"[DEBUG] Strategy 4 failed: {str(e)}")
        except Exception as e:
            print(f"[DEBUG] Strategy 4 error: {str(e)}")
        
        # If all parsing attempts fail, return the raw string
        # This ensures we never lose data even if format is unexpected
        print(f"[DEBUG] All parsing strategies failed, returning raw string")
        return cleaned_text
