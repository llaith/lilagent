"""Main orchestrator for the spec-to-code multi-agent system."""

import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from .config import Config
from .workflows.spec_pipeline import process_specification
from .workflows.planning_uat_loop import run_planning_uat_loop


class SpecToCodeOrchestrator:
    """Orchestrates the entire spec-to-code pipeline."""

    def __init__(self, spec_file: str, work_dir: str, verbose: bool = True):
        """Initialize orchestrator.

        Args:
            spec_file: Path to specification file
            work_dir: Directory where package will be created
            verbose: Enable verbose logging
        """
        self.spec_file = spec_file
        self.work_dir = work_dir
        self.verbose = verbose
        self.start_time = datetime.now()

        # Ensure work directory exists
        os.makedirs(work_dir, exist_ok=True)

    def run(self) -> Dict[str, Any]:
        """Execute the full pipeline.

        Returns:
            Dict with execution results and metadata
        """
        print(f"\n{'='*70}")
        print(f"🤖 LILAGENT - Spec-to-Code Multi-Agent System")
        print(f"{'='*70}")
        print(f"Specification: {self.spec_file}")
        print(f"Output Directory: {self.work_dir}")
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")

        try:
            # Phase 1: Specification Pipeline (Normalize → Enhance)
            print(f"\n{'#'*70}")
            print("# PHASE 1: SPECIFICATION PROCESSING")
            print(f"{'#'*70}\n")

            spec_result = process_specification(self.spec_file)
            enhanced_spec = spec_result["enhanced_spec"]

            # Save enhanced spec to work directory for reference
            spec_output_path = Path(self.work_dir) / "SPECIFICATION.md"
            with open(spec_output_path, 'w') as f:
                f.write(enhanced_spec)

            print(f"\n✅ Specification processed and saved to: {spec_output_path}\n")

            # Phase 2: Multi-Agent Implementation (Planning → Coding → UAT)
            print(f"\n{'#'*70}")
            print("# PHASE 2: MULTI-AGENT IMPLEMENTATION")
            print(f"{'#'*70}\n")

            implementation_result = run_planning_uat_loop(
                work_dir=self.work_dir,
                specification=enhanced_spec,
            )

            # Final summary
            end_time = datetime.now()
            duration = end_time - self.start_time

            print(f"\n{'='*70}")
            print(f"🏁 EXECUTION COMPLETE")
            print(f"{'='*70}")
            print(f"Status: {'✅ SUCCESS' if implementation_result['success'] else '❌ FAILED'}")
            print(f"UAT Passed: {implementation_result['uat_passed']}")
            print(f"Outer Loop Iterations: {implementation_result['iterations']}")
            print(f"Duration: {duration}")
            print(f"Output: {self.work_dir}")
            print(f"{'='*70}\n")

            return {
                "success": implementation_result["success"],
                "spec_processing": spec_result["metadata"],
                "implementation": implementation_result,
                "work_dir": self.work_dir,
                "duration": str(duration),
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
            }

        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}\n")
            raise


def run_spec_to_code(spec_file: str, work_dir: str) -> Dict[str, Any]:
    """Convenience function to run the spec-to-code pipeline.

    Args:
        spec_file: Path to specification file
        work_dir: Directory where package will be created

    Returns:
        Execution results
    """
    orchestrator = SpecToCodeOrchestrator(spec_file, work_dir)
    return orchestrator.run()
