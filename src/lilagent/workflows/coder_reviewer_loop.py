"""Inner feedback loop: Coder ↔ Reviewer."""

from typing import Dict, Any, List
from crewai import Task, Crew, Process

from ..config import Config
from ..agents import create_coder_agent, create_reviewer_agent


def run_coder_reviewer_loop(
    work_dir: str,
    task_description: str,
    context: str = "",
    max_iterations: int = None
) -> Dict[str, Any]:
    """Run the Coder-Reviewer feedback loop.

    Args:
        work_dir: Working directory for file operations
        task_description: Description of the coding task
        context: Additional context from previous tasks
        max_iterations: Max iterations (defaults to config value)

    Returns:
        Dict with:
            - success: bool
            - iterations: int
            - final_result: str
            - review_approved: bool
    """
    if max_iterations is None:
        max_iterations = Config.MAX_CODER_REVIEWER_ITERATIONS

    coder = create_coder_agent(work_dir)
    reviewer = create_reviewer_agent(work_dir)

    iteration = 0
    feedback = ""
    approved = False

    print(f"\n{'='*70}")
    print(f"🔄 CODER-REVIEWER LOOP: {task_description[:50]}...")
    print(f"{'='*70}\n")

    while iteration < max_iterations and not approved:
        iteration += 1
        print(f"\n--- Iteration {iteration}/{max_iterations} ---\n")

        # Coding task
        coding_task_desc = task_description
        if feedback:
            coding_task_desc += f"\n\nREVIEWER FEEDBACK (address these issues):\n{feedback}"
        if context:
            coding_task_desc += f"\n\nCONTEXT:\n{context}"

        coding_task = Task(
            description=coding_task_desc,
            expected_output="Implementation complete with files created/modified and self-test results",
            agent=coder,
        )

        coding_crew = Crew(
            agents=[coder],
            tasks=[coding_task],
            process=Process.sequential,
            verbose=Config.ENABLE_VERBOSE_LOGGING,
        )

        print("👨‍💻 Coder working...")
        coder_result = coding_crew.kickoff()

        # Review task
        review_task = Task(
            description=f"""Review the code changes made by the Coder agent.

TASK THAT WAS IMPLEMENTED:
{task_description}

CODER'S WORK:
{coder_result}

Perform a thorough code review according to your criteria.
Output either:
- "APPROVED" if code meets standards
- "CHANGES_REQUESTED" with specific, actionable feedback

Be specific about file names, line numbers, and issues.
Distinguish CRITICAL issues from MINOR suggestions.
""",
            expected_output="Review decision: APPROVED or CHANGES_REQUESTED with detailed feedback",
            agent=reviewer,
        )

        review_crew = Crew(
            agents=[reviewer],
            tasks=[review_task],
            process=Process.sequential,
            verbose=Config.ENABLE_VERBOSE_LOGGING,
        )

        print("🔍 Reviewer evaluating...")
        review_result = str(review_crew.kickoff())

        # Check if approved
        if "APPROVED" in review_result and "CHANGES_REQUESTED" not in review_result:
            approved = True
            print("\n✅ Code review APPROVED!\n")
        else:
            feedback = review_result
            print(f"\n⚠️  Changes requested (iteration {iteration}/{max_iterations})\n")

    return {
        "success": approved,
        "iterations": iteration,
        "final_result": str(coder_result),
        "review_approved": approved,
        "final_review": review_result if iteration > 0 else "",
    }
