"""Outer feedback loop: Planner → (Coder/Reviewer)* → UAT → Gap Analysis."""

from typing import Dict, Any, List
from crewai import Task, Crew, Process

from ..config import Config
from ..agents import (
    create_planning_agent,
    create_uat_agent,
    create_gap_analyst_agent,
    create_documentation_agent,
)
from .coder_reviewer_loop import run_coder_reviewer_loop


def run_planning_uat_loop(
    work_dir: str,
    specification: str,
    max_iterations: int = None
) -> Dict[str, Any]:
    """Run the Planning-UAT feedback loop with gap analysis.

    Args:
        work_dir: Working directory for package creation
        specification: Complete enhanced specification
        max_iterations: Max outer loop iterations (defaults to config)

    Returns:
        Dict with:
            - success: bool
            - iterations: int
            - uat_passed: bool
            - final_package_path: str
    """
    if max_iterations is None:
        max_iterations = Config.MAX_PLANNING_UAT_ITERATIONS

    planner = create_planning_agent(work_dir)
    uat = create_uat_agent(work_dir)
    gap_analyst = create_gap_analyst_agent()
    documentation = create_documentation_agent(work_dir)

    iteration = 0
    uat_passed = False
    gap_analysis = ""

    print(f"\n{'='*70}")
    print(f"🚀 PLANNING-UAT LOOP STARTING")
    print(f"{'='*70}\n")

    while iteration < max_iterations and not uat_passed:
        iteration += 1
        print(f"\n{'#'*70}")
        print(f"# OUTER LOOP ITERATION {iteration}/{max_iterations}")
        print(f"{'#'*70}\n")

        # Planning phase
        planning_desc = f"""Analyze the specification and create a task breakdown for implementation.

SPECIFICATION:
{specification}

{gap_analysis if gap_analysis else ''}

Your job is to:
1. Break down the specification into clear, atomic implementation tasks
2. Each task should be specific enough for the Coder agent to implement
3. Order tasks logically (dependencies, foundation first)
4. Create 3-7 focused tasks

Output a numbered list of tasks with clear descriptions.
Each task should be independently implementable in fresh context.
"""

        planning_task = Task(
            description=planning_desc,
            expected_output="Numbered list of implementation tasks with clear descriptions",
            agent=planner,
        )

        planning_crew = Crew(
            agents=[planner],
            tasks=[planning_task],
            process=Process.sequential,
            verbose=Config.ENABLE_VERBOSE_LOGGING,
        )

        print("📋 Planning agent creating task breakdown...")
        plan_result = str(planning_crew.kickoff())
        print(f"\n📝 Plan created:\n{plan_result}\n")

        # Extract tasks from plan (simple approach: look for numbered lines)
        tasks = []
        for line in plan_result.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                # Remove list markers
                clean_line = line.lstrip('0123456789.-*) \t')
                if clean_line:
                    tasks.append(clean_line)

        if not tasks:
            print("⚠️  No clear tasks found in plan, treating entire plan as one task")
            tasks = [plan_result]

        print(f"\n🎯 Executing {len(tasks)} task(s)...\n")

        # Execute each task with Coder-Reviewer loop
        all_results = []
        for idx, task in enumerate(tasks, 1):
            print(f"\n{'='*70}")
            print(f"Task {idx}/{len(tasks)}: {task[:60]}...")
            print(f"{'='*70}")

            # Provide context from previous tasks
            context = ""
            if all_results:
                context = f"Previous tasks completed:\n"
                for i, prev_result in enumerate(all_results, 1):
                    context += f"\nTask {i} result:\n{prev_result['final_result'][:200]}...\n"

            result = run_coder_reviewer_loop(
                work_dir=work_dir,
                task_description=task,
                context=context,
            )

            all_results.append(result)

            if not result['success']:
                print(f"\n❌ Task {idx} failed after max iterations in coder-reviewer loop")
                # Continue anyway - UAT will catch issues

        print(f"\n{'='*70}")
        print("✓ All coding tasks completed, running UAT...")
        print(f"{'='*70}\n")

        # UAT phase
        uat_desc = f"""Perform User Acceptance Testing on the complete implementation.

ORIGINAL SPECIFICATION:
{specification}

The implementation has been completed. Your job is to:
1. Verify the package can be installed
2. Run all tests
3. Check core functionality
4. Validate against acceptance criteria
5. Check for drift from specification

Output either:
- "UAT RESULT: PASS" if all criteria met
- "UAT RESULT: FAIL" with detailed gap analysis

Be thorough and specific about any issues found.
"""

        uat_task = Task(
            description=uat_desc,
            expected_output="UAT result: PASS or FAIL with detailed findings",
            agent=uat,
        )

        uat_crew = Crew(
            agents=[uat],
            tasks=[uat_task],
            process=Process.sequential,
            verbose=Config.ENABLE_VERBOSE_LOGGING,
        )

        print("🧪 UAT agent testing implementation...")
        uat_result = str(uat_crew.kickoff())

        # Check if UAT passed
        if "UAT RESULT: PASS" in uat_result or "PASS" in uat_result.upper():
            uat_passed = True
            print("\n✅ UAT PASSED! Proceeding to documentation...\n")
            break
        else:
            print(f"\n❌ UAT FAILED (iteration {iteration}/{max_iterations})\n")

            # Gap analysis
            if iteration < max_iterations:
                gap_desc = f"""Analyze the UAT failure and create a remediation plan.

ORIGINAL SPECIFICATION:
{specification}

UAT FINDINGS:
{uat_result}

PLAN THAT WAS EXECUTED:
{plan_result}

Provide a detailed gap analysis and remediation plan.
Identify what went wrong and what specific actions are needed to fix it.
"""

                gap_task = Task(
                    description=gap_desc,
                    expected_output="Gap analysis report with remediation plan",
                    agent=gap_analyst,
                )

                gap_crew = Crew(
                    agents=[gap_analyst],
                    tasks=[gap_task],
                    process=Process.sequential,
                    verbose=Config.ENABLE_VERBOSE_LOGGING,
                )

                print("🔍 Gap analyst analyzing failures...")
                gap_result = str(gap_crew.kickoff())
                gap_analysis = f"\n\nGAP ANALYSIS FROM PREVIOUS ITERATION:\n{gap_result}\n"
                print(f"\n📊 Gap analysis complete, replanning...\n")

    # If UAT passed, generate documentation
    if uat_passed:
        print(f"\n{'='*70}")
        print("📚 Generating documentation...")
        print(f"{'='*70}\n")

        doc_task = Task(
            description=f"""Generate comprehensive documentation for the package.

SPECIFICATION:
{specification}

Create a complete README.md and any other necessary documentation.
Ensure examples are accurate and installation instructions are complete.
""",
            expected_output="README.md and other documentation files created",
            agent=documentation,
        )

        doc_crew = Crew(
            agents=[documentation],
            tasks=[doc_task],
            process=Process.sequential,
            verbose=Config.ENABLE_VERBOSE_LOGGING,
        )

        doc_result = str(doc_crew.kickoff())
        print("\n✅ Documentation complete!\n")

    return {
        "success": uat_passed,
        "iterations": iteration,
        "uat_passed": uat_passed,
        "final_package_path": work_dir,
        "uat_result": uat_result if iteration > 0 else "",
    }
