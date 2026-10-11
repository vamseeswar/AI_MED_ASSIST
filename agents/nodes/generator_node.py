from typing import Dict, Any
from agents.state.agent_state import AgentState
from agents.prompts.agent_prompts import (
    CORE_MEDICAL_DISCLAIMER,
    SYSTEM_PROMPT_RAG_AGENT,
    SYSTEM_PROMPT_KNOWLEDGE_AGENT,
    SYSTEM_PROMPT_ANALYSIS_AGENT,
    SYSTEM_PROMPT_REPORT_AGENT
)
from rag.citations.citation_engine import format_citations_markdown
from ai.llm_provider import get_llm_client
from backend.app.core.logging import app_logger


def response_generator_node(state: AgentState) -> Dict[str, Any]:
    """Generates source-grounded response using LLM client and appends verifiable citations and disclaimer."""
    # If already answered by a guardrail refusal, preserve it
    if state.get("final_answer") and state.get("safety_status") != "SAFE":
        return {}

    provenance = state.get("agent_provenance", "Document Agent")
    context = state.get("retrieved_context", "")
    query = state.get("user_query", "")

    # Select system prompt
    if provenance == "Knowledge Agent":
        system_prompt = SYSTEM_PROMPT_KNOWLEDGE_AGENT
    elif provenance == "Analysis Agent":
        system_prompt = SYSTEM_PROMPT_ANALYSIS_AGENT
    elif provenance == "Report Agent":
        system_prompt = SYSTEM_PROMPT_REPORT_AGENT
    else:
        system_prompt = SYSTEM_PROMPT_RAG_AGENT

    user_prompt = f"Reference Context:\n{context}\n\nUser Question:\n{query}"

    llm = get_llm_client()
    raw_answer = llm.generate(system_prompt=system_prompt, user_prompt=user_prompt)

    # Format citations
    citations = state.get("citations", [])
    citations_md = format_citations_markdown(citations)

    # Assemble complete final answer
    complete_answer = raw_answer + citations_md + CORE_MEDICAL_DISCLAIMER

    return {
        "final_answer": complete_answer
    }
