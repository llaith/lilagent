"""Execution and notification tools for agent use."""

import subprocess
import json
import requests
from pathlib import Path
from typing import Optional
from crewai_tools import BaseTool
from pydantic import BaseModel, Field


class ExecuteCommandInput(BaseModel):
    """Input schema for ExecuteCommandTool."""

    command: str = Field(..., description="Shell command to execute")
    timeout: int = Field(default=60, description="Timeout in seconds")


class ExecuteCommandTool(BaseTool):
    """Tool for executing shell commands in work directory."""

    name: str = "execute_command"
    description: str = (
        "Execute a shell command in the work directory. "
        "Use this to run builds, tests, installations, or utility scripts. "
        "Returns stdout, stderr, and exit code. "
        "Timeout default is 60 seconds."
    )
    args_schema: type[BaseModel] = ExecuteCommandInput
    work_dir: str = Field(..., description="Base work directory")

    def _run(self, command: str, timeout: int = 60) -> str:
        """Execute shell command."""
        try:
            # Run command in work directory
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.work_dir,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            output = []
            output.append(f"Command: {command}")
            output.append(f"Exit Code: {result.returncode}")

            if result.stdout:
                output.append(f"\n=== STDOUT ===\n{result.stdout}")

            if result.stderr:
                output.append(f"\n=== STDERR ===\n{result.stderr}")

            if result.returncode == 0:
                output.append("\n✓ Command executed successfully")
            else:
                output.append(f"\n✗ Command failed with exit code {result.returncode}")

            return "\n".join(output)

        except subprocess.TimeoutExpired:
            return f"Error: Command timed out after {timeout} seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"


class SendWebhookInput(BaseModel):
    """Input schema for SendWebhookTool."""

    issue_type: str = Field(..., description="Type of issue (e.g., 'blocked', 'clarification_needed')")
    message: str = Field(..., description="Detailed message about the issue")
    context: str = Field(..., description="Additional context about current state")


class SendWebhookTool(BaseTool):
    """Tool for sending webhook notifications when agent is blocked."""

    name: str = "send_webhook"
    description: str = (
        "Send a webhook notification when you cannot proceed without user input. "
        "Use this when the task is too complex, ambiguous, or requires clarification. "
        "Provide issue type, detailed message, and context."
    )
    args_schema: type[BaseModel] = SendWebhookInput
    webhook_url: str = Field(..., description="Webhook URL to POST to")

    def _run(self, issue_type: str, message: str, context: str) -> str:
        """Send webhook notification."""
        if not self.webhook_url:
            return "Warning: No webhook URL configured - notification not sent"

        try:
            payload = {
                "status": "blocked",
                "issue_type": issue_type,
                "message": message,
                "context": context,
                "requires_user_input": True
            }

            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )

            if response.status_code in [200, 201, 202]:
                return (
                    f"✓ Webhook notification sent successfully\n"
                    f"Status: {response.status_code}\n"
                    f"Issue: {issue_type}\n"
                    f"Message: {message}"
                )
            else:
                return (
                    f"✗ Webhook notification failed\n"
                    f"Status: {response.status_code}\n"
                    f"Response: {response.text}"
                )

        except requests.exceptions.RequestException as e:
            return f"Error sending webhook: {str(e)}"


def create_execution_tools(work_dir: str, webhook_url: Optional[str] = None) -> list[BaseTool]:
    """Create execution and notification tools.

    Args:
        work_dir: Base directory for command execution
        webhook_url: Optional webhook URL for notifications

    Returns:
        List of configured execution tools
    """
    tools = [ExecuteCommandTool(work_dir=work_dir)]

    if webhook_url:
        tools.append(SendWebhookTool(webhook_url=webhook_url))

    return tools
