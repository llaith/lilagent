"""Specification processing pipeline: normalize → enhance."""

from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from ..config import Config
from ..prompts.system_prompts import get_agent_prompt


def get_llm(model_type: str = "agent"):
    """Get LLM instance based on model type.

    Args:
        model_type: Either "normalizer" (cheap) or "agent" (smart)

    Returns:
        LLM instance (ChatAnthropic or ChatOpenAI)
    """
    llm_config = Config.get_llm_config(model_type)
    model = llm_config["model"]

    # Determine which SDK to use based on model prefix
    if "anthropic" in model.lower():
        return ChatAnthropic(
            model=model,
            api_key=llm_config["api_key"],
            base_url=llm_config.get("base_url"),
            temperature=0.3,
        )
    else:
        return ChatOpenAI(
            model=model,
            api_key=llm_config["api_key"],
            base_url=llm_config.get("base_url"),
            temperature=0.3,
        )


def normalize_spec(raw_spec: str) -> str:
    """Normalize specification language using cheap LLM.

    Args:
        raw_spec: Raw user specification text

    Returns:
        Professionally worded specification
    """
    llm = get_llm("normalizer")
    system_prompt = get_agent_prompt("spec_normalizer")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Normalize this specification:\n\n{raw_spec}"}
    ]

    response = llm.invoke(messages)
    return response.content


def enhance_spec(normalized_spec: str) -> str:
    """Enhance normalized spec using template.

    Args:
        normalized_spec: Professionally worded specification

    Returns:
        Complete specification following template structure
    """
    llm = get_llm("agent")
    system_prompt = get_agent_prompt("spec_enhancer")

    # Load template
    template_path = Config.get_spec_template_path()
    with open(template_path, 'r') as f:
        template = f.read()

    user_prompt = f"""Transform the following specification into a complete structured document
using the provided template.

TEMPLATE:
{template}

NORMALIZED SPECIFICATION TO ENHANCE:
{normalized_spec}

Fill out all template sections. Use the specification content to populate relevant fields.
For missing information, infer reasonable defaults based on context, or use "Not specified".
Document your inferences in the metadata section.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    response = llm.invoke(messages)
    return response.content


def process_specification(spec_file_path: str) -> Dict[str, Any]:
    """Run full specification pipeline.

    Args:
        spec_file_path: Path to user's specification file

    Returns:
        Dict containing:
            - raw_spec: Original user input
            - normalized_spec: Cleaned version
            - enhanced_spec: Complete structured specification
            - metadata: Processing metadata
    """
    # Read raw specification
    with open(spec_file_path, 'r') as f:
        raw_spec = f.read()

    print("📝 Step 1/2: Normalizing specification language...")
    normalized_spec = normalize_spec(raw_spec)

    print("📋 Step 2/2: Enhancing specification with template...")
    enhanced_spec = enhance_spec(normalized_spec)

    return {
        "raw_spec": raw_spec,
        "normalized_spec": normalized_spec,
        "enhanced_spec": enhanced_spec,
        "metadata": {
            "source_file": spec_file_path,
            "processed_at": datetime.now().isoformat(),
            "normalizer_model": Config.NORMALIZER_MODEL,
            "enhancer_model": Config.AGENT_MODEL,
        }
    }
