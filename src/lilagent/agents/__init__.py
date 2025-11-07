"""Agent definitions using CrewAI framework."""

from crewai import Agent
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from ..config import Config
from ..prompts.system_prompts import get_agent_prompt
from ..tools import create_file_tools, create_execution_tools


def get_llm(model_type: str = "agent"):
    """Get LLM instance for agents.

    Args:
        model_type: Either "normalizer" (cheap) or "agent" (smart)

    Returns:
        LLM instance
    """
    llm_config = Config.get_llm_config(model_type)
    model = llm_config["model"]

    common_params = {
        "model": model,
        "api_key": llm_config["api_key"],
        "temperature": 0.3,
    }

    if llm_config.get("base_url"):
        common_params["base_url"] = llm_config["base_url"]

    if "anthropic" in model.lower():
        return ChatAnthropic(**common_params)
    else:
        return ChatOpenAI(**common_params)


def create_planning_agent(work_dir: str) -> Agent:
    """Create Planning Agent (Master) - NO coding tools.

    This agent only delegates and evaluates, never codes.
    """
    # Planning agent only gets webhook tool (for blocking notifications)
    tools = []
    if Config.WEBHOOK_URL:
        tools = [create_execution_tools(work_dir, Config.WEBHOOK_URL)[1]]  # Just webhook

    return Agent(
        role="Technical Architect & Orchestration Master",
        goal="Break down specifications, delegate to sub-agents, evaluate results, maintain traceability",
        backstory=get_agent_prompt("planning"),
        llm=get_llm("agent"),
        tools=tools,
        verbose=Config.ENABLE_VERBOSE_LOGGING,
        allow_delegation=True,  # Critical: enables sub-agent delegation
        max_iter=15,
    )


def create_coder_agent(work_dir: str) -> Agent:
    """Create Coder Agent with script-first strategy."""
    # Coder gets all tools: file ops + execution
    file_tools = create_file_tools(work_dir)
    exec_tools = create_execution_tools(work_dir, None)  # No webhook for coder
    tools = file_tools + exec_tools

    return Agent(
        role="Senior Software Engineer",
        goal="Implement tasks efficiently using script-first strategy",
        backstory=get_agent_prompt("coder"),
        llm=get_llm("agent"),
        tools=tools,
        verbose=Config.ENABLE_VERBOSE_LOGGING,
        allow_delegation=False,
        max_iter=20,
    )


def create_reviewer_agent(work_dir: str) -> Agent:
    """Create Reviewer Agent for code quality checks."""
    # Reviewer only needs read access
    tools = [create_file_tools(work_dir)[0]]  # Just read_file

    return Agent(
        role="Senior Code Reviewer",
        goal="Ensure code quality, best practices, and correctness",
        backstory=get_agent_prompt("reviewer"),
        llm=get_llm("agent"),
        tools=tools,
        verbose=Config.ENABLE_VERBOSE_LOGGING,
        allow_delegation=False,
        max_iter=10,
    )


def create_uat_agent(work_dir: str) -> Agent:
    """Create UAT Agent for specification validation."""
    # UAT needs read + execute (to run tests)
    file_tools = create_file_tools(work_dir)
    exec_tools = create_execution_tools(work_dir, None)
    tools = file_tools + exec_tools

    return Agent(
        role="Quality Assurance Engineer",
        goal="Verify implementation matches specification and all acceptance criteria are met",
        backstory=get_agent_prompt("uat"),
        llm=get_llm("agent"),
        tools=tools,
        verbose=Config.ENABLE_VERBOSE_LOGGING,
        allow_delegation=False,
        max_iter=15,
    )


def create_gap_analyst_agent() -> Agent:
    """Create Gap Analyst Agent for failure analysis."""
    # Gap analyst doesn't need tools, just analyzes text
    return Agent(
        role="Gap Analysis Specialist",
        goal="Analyze UAT failures and determine remediation plan",
        backstory=get_agent_prompt("gap_analyst"),
        llm=get_llm("agent"),
        tools=[],
        verbose=Config.ENABLE_VERBOSE_LOGGING,
        allow_delegation=False,
        max_iter=10,
    )


def create_documentation_agent(work_dir: str) -> Agent:
    """Create Documentation Agent for final docs."""
    # Docs agent needs read + write
    tools = create_file_tools(work_dir)

    return Agent(
        role="Technical Documentation Specialist",
        goal="Generate comprehensive user-friendly documentation",
        backstory=get_agent_prompt("documentation"),
        llm=get_llm("agent"),
        tools=tools,
        verbose=Config.ENABLE_VERBOSE_LOGGING,
        allow_delegation=False,
        max_iter=10,
    )


__all__ = [
    "create_planning_agent",
    "create_coder_agent",
    "create_reviewer_agent",
    "create_uat_agent",
    "create_gap_analyst_agent",
    "create_documentation_agent",
]
