"""Test case for simple calculator spec-to-code generation.

This test demonstrates how to use lilagent to generate a package from a specification.
For actual execution, you need valid API keys configured in .env file.
"""

import os
import tempfile
from pathlib import Path
import pytest

# Mark all tests in this file as integration tests
pytestmark = pytest.mark.integration


def test_calculator_spec_exists():
    """Verify the calculator test specification exists."""
    spec_file = Path(__file__).parent / "fixtures" / "calculator_spec.md"
    assert spec_file.exists(), "Calculator spec file should exist"

    content = spec_file.read_text()
    assert "calculator" in content.lower()
    assert "add" in content.lower() or "addition" in content.lower()


@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires API key configured in environment"
)
def test_calculator_generation():
    """Test full spec-to-code pipeline with calculator example.

    This test requires:
    1. Valid API keys in .env or environment
    2. Network access to LLM proxy
    3. Several minutes to complete

    Run with: poetry run pytest tests/test_simple_calculator.py -v -s
    """
    from lilagent import run_spec_to_code

    spec_file = str(Path(__file__).parent / "fixtures" / "calculator_spec.md")

    with tempfile.TemporaryDirectory() as work_dir:
        # Run spec-to-code pipeline
        result = run_spec_to_code(spec_file, work_dir)

        # Verify results
        assert result["success"], "Pipeline should complete successfully"
        assert result["implementation"]["uat_passed"], "UAT should pass"

        # Verify output directory has expected structure
        work_path = Path(work_dir)
        assert (work_path / "SPECIFICATION.md").exists(), "Enhanced spec should be saved"
        assert (work_path / "README.md").exists(), "README should be generated"

        # Verify package can be described (detailed verification would require installation)
        files = list(work_path.rglob("*.py"))
        assert len(files) > 0, "Should generate Python files"


if __name__ == "__main__":
    # Run test directly
    import sys

    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not configured")
        print("Copy .env.example to .env and configure your API keys")
        sys.exit(1)

    test_calculator_generation()
    print("\n✅ Test passed!")
