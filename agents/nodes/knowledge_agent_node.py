from typing import Dict, Any
from agents.state.agent_state import AgentState
from mcp.registry import mcp_registry
from backend.app.core.logging import app_logger


def knowledge_agent_node(state: AgentState) -> Dict[str, Any]:
    """Queries medical terminology and curated knowledge articles via MCP tools."""
    query = state.get("user_query", "")

    # Execute Terminology MCP tool
    term_res = mcp_registry.execute_tool("lookup_medical_term", {"term": query})

    # Execute Knowledge MCP tool
    kb_res = mcp_registry.execute_tool("search_knowledge", {"topic": query})

    knowledge_blocks = []
    if term_res.get("success") and term_res.get("result"):
        t_data = term_res["result"]
        knowledge_blocks.append(
            f"Medical Terminology Definition: {t_data.get('term')}\n"
            f"- Clinical Definition: {t_data.get('definition')}\n"
            f"- Layperson Translation: {t_data.get('layperson_explanation')}\n"
            f"- Reference Context: {t_data.get('normal_reference')}"
        )

    if kb_res.get("success") and kb_res.get("result", {}).get("articles"):
        for art in kb_res["result"]["articles"]:
            knowledge_blocks.append(
                f"Clinical Guideline / Educational Article: {art.get('title')}\n"
                f"- Category: {art.get('category')}\n"
                f"- Summary: {art.get('summary')}\n"
                f"- Primary Source: {art.get('source')}"
            )

    combined_knowledge = "\n\n".join(knowledge_blocks)

    tool_entry = {
        "tool": "knowledge_and_terminology_lookup",
        "query": query,
        "results_count": len(knowledge_blocks)
    }

    return {
        "retrieved_context": combined_knowledge,
        "tool_results": state.get("tool_results", []) + [tool_entry],
        "agent_provenance": "Knowledge Agent"
    }
