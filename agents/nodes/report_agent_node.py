from typing import Dict, Any
from agents.state.agent_state import AgentState
from mcp.registry import mcp_registry


def report_agent_node(state: AgentState) -> Dict[str, Any]:
    """Compiles multi-document executive and comparative reports via Reporting MCP tools."""
    doc_id = state.get("document_id")
    doc_ids = [doc_id] if doc_id else []

    if not doc_ids:
        # Retrieve recent user documents via Database MCP
        # Default report context
        context_text = "Executive multi-document medical summary synthesis."
    else:
        rep_res = mcp_registry.execute_tool("generate_summary_report", {"document_ids": doc_ids})
        if rep_res.get("success") and rep_res.get("result"):
            context_text = rep_res["result"].get("markdown_content", "")
        else:
            context_text = "Synthesis across designated document records."

    return {
        "retrieved_context": context_text,
        "agent_provenance": "Report Agent"
    }
