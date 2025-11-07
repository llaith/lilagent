"""File operation tools for agent use."""

import os
from pathlib import Path
from typing import Optional
from crewai_tools import BaseTool
from pydantic import BaseModel, Field


class ReadFileInput(BaseModel):
    """Input schema for ReadFileTool."""

    file_path: str = Field(..., description="Relative path to file within work directory")


class ReadFileTool(BaseTool):
    """Tool for reading file contents."""

    name: str = "read_file"
    description: str = (
        "Read the contents of a file. "
        "Provide the relative path from the work directory. "
        "Returns the file contents as a string."
    )
    args_schema: type[BaseModel] = ReadFileInput
    work_dir: str = Field(..., description="Base work directory")

    def _run(self, file_path: str) -> str:
        """Read file contents."""
        try:
            full_path = Path(self.work_dir) / file_path

            if not full_path.exists():
                return f"Error: File '{file_path}' does not exist"

            if not full_path.is_file():
                return f"Error: '{file_path}' is not a file"

            # Ensure path is within work_dir (security)
            if not str(full_path.resolve()).startswith(str(Path(self.work_dir).resolve())):
                return f"Error: Access denied - path outside work directory"

            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return f"Contents of {file_path}:\n\n{content}"

        except Exception as e:
            return f"Error reading file: {str(e)}"


class WriteFileInput(BaseModel):
    """Input schema for WriteFileTool."""

    file_path: str = Field(..., description="Relative path to file within work directory")
    content: str = Field(..., description="Content to write to file")


class WriteFileTool(BaseTool):
    """Tool for writing file contents."""

    name: str = "write_file"
    description: str = (
        "Write content to a file. Creates parent directories if needed. "
        "Overwrites existing files. Provide relative path from work directory."
    )
    args_schema: type[BaseModel] = WriteFileInput
    work_dir: str = Field(..., description="Base work directory")

    def _run(self, file_path: str, content: str) -> str:
        """Write content to file."""
        try:
            full_path = Path(self.work_dir) / file_path

            # Ensure path is within work_dir (security)
            if not str(full_path.resolve()).startswith(str(Path(self.work_dir).resolve())):
                return f"Error: Access denied - path outside work directory"

            # Create parent directories
            full_path.parent.mkdir(parents=True, exist_ok=True)

            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"Successfully wrote {len(content)} characters to {file_path}"

        except Exception as e:
            return f"Error writing file: {str(e)}"


class ListDirectoryInput(BaseModel):
    """Input schema for ListDirectoryTool."""

    directory_path: str = Field(
        default=".",
        description="Relative path to directory (default: current/root)"
    )


class ListDirectoryTool(BaseTool):
    """Tool for listing directory contents."""

    name: str = "list_directory"
    description: str = (
        "List contents of a directory. Shows files and subdirectories. "
        "Provide relative path from work directory, or '.' for root."
    )
    args_schema: type[BaseModel] = ListDirectoryInput
    work_dir: str = Field(..., description="Base work directory")

    def _run(self, directory_path: str = ".") -> str:
        """List directory contents."""
        try:
            full_path = Path(self.work_dir) / directory_path

            if not full_path.exists():
                return f"Error: Directory '{directory_path}' does not exist"

            if not full_path.is_dir():
                return f"Error: '{directory_path}' is not a directory"

            # Ensure path is within work_dir (security)
            if not str(full_path.resolve()).startswith(str(Path(self.work_dir).resolve())):
                return f"Error: Access denied - path outside work directory"

            items = []
            for item in sorted(full_path.iterdir()):
                rel_path = item.relative_to(self.work_dir)
                item_type = "DIR " if item.is_dir() else "FILE"
                size = f"{item.stat().st_size:>10} bytes" if item.is_file() else ""
                items.append(f"{item_type} {rel_path} {size}")

            if not items:
                return f"Directory '{directory_path}' is empty"

            return f"Contents of {directory_path}:\n\n" + "\n".join(items)

        except Exception as e:
            return f"Error listing directory: {str(e)}"


def create_file_tools(work_dir: str) -> list[BaseTool]:
    """Create file operation tools for a specific work directory.

    Args:
        work_dir: Base directory for file operations

    Returns:
        List of configured file tools
    """
    return [
        ReadFileTool(work_dir=work_dir),
        WriteFileTool(work_dir=work_dir),
        ListDirectoryTool(work_dir=work_dir),
    ]
