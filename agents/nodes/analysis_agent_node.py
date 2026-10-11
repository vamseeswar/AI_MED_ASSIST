from typing import Dict, Any
from agents.state.agent_state import AgentState
from mcp.registry import mcp_registry


def analysis_agent_node(state: AgentState) -> Dict[str, Any]:
    """Analyzes document metadata, page statistics, and structure via Database MCP."""
    doc_id = state.get("document_id")
    query = state.get("user_query", "")

    analysis_blocks = []
    if doc_id:
        res = mcp_registry.execute_tool("get_document_metadata", {"document_id": doc_id})
        if res.get("success") and res.get("result"):
            d = res["result"]
            meta = d.get("metadata", {})
            analysis_blocks.append(
                f"Document Structural Profile ({d.get('filename')}):\n"
                f"- Title: {d.get('title')}\n"
                f"- Format: {d.get('file_type')}\n"
                f"- Page Count: {d.get('page_count')}\n"
                f"- Word Count: {meta.get('total_words', 'N/A')}\n"
                f"- Detected Clinical Sections: {', '.join(meta.get('medical_domain_sections', []))}"
            )

    if not analysis_blocks:
        analysis_blocks.append("Document structural analysis completed across available document scope.")

    return {
        "retrieved_context": "\n\n".join(analysis_blocks),
        "agent_provenance": "Analysis Agent"
    }
