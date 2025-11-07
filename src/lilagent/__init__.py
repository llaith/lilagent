"""lilagent - Multi-agent spec-to-code system."""

__version__ = "0.1.0"

from .orchestrator import run_spec_to_code, SpecToCodeOrchestrator

__all__ = ["run_spec_to_code", "SpecToCodeOrchestrator", "__version__"]
