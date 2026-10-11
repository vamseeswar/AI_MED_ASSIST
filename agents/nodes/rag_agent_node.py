from typing import Dict, Any
from agents.state.agent_state import AgentState
from rag.pipelines.rag_pipeline import get_rag_pipeline
from mcp.registry import mcp_registry
from backend.app.security.prompt_guard import wrap_untrusted_context
from backend.app.core.logging import app_logger


def rag_agent_node(state: AgentState) -> Dict[str, Any]:
    """Retrieves document evidence using hybrid search and MCP tools."""
    query = state.get("user_query", "")
    doc_id = state.get("document_id")

    pipeline = get_rag_pipeline()
    retrieval = pipeline.retrieve(query=query, top_k=5, document_id=doc_id)

    raw_context = retrieval.get("formatted_context", "")
    citations = retrieval.get("citations", [])
    chunks_count = retrieval.get("chunks_retrieved_count", 0)

    # Wrap untrusted retrieved context with security delimiters
    safe_context = wrap_untrusted_context(raw_context) if raw_context else ""

    # Record MCP tool execution
    tool_entry = {
        "tool": "search_documents",
        "query": query,
        "document_id": doc_id,
        "chunks_found": chunks_count
    }

    return {
        "retrieved_context": safe_context,
        "citations": citations,
        "tool_results": state.get("tool_results", []) + [tool_entry],
        "agent_provenance": "Document Agent"
    }
