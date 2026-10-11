import pytest
from mcp.registry import mcp_registry
import mcp  # Ensure tools are loaded


def test_mcp_tool_listing():
    tools = mcp_registry.list_tools()
    tool_names = [t.name for t in tools]
    assert "search_documents" in tool_names
    assert "get_document" in tool_names
    assert "lookup_medical_term" in tool_names
    assert "search_knowledge" in tool_names
    assert "get_document_metadata" in tool_names
    assert "generate_summary_report" in tool_names


def test_mcp_terminology_lookup():
    res = mcp_registry.execute_tool("lookup_medical_term", {"term": "hypertension"})
    assert res["success"] is True
    data = res["result"]
    assert data["term"] == "Hypertension"
    assert "layperson_explanation" in data
    assert "clinical_significance" in data


def test_mcp_knowledge_search():
    res = mcp_registry.execute_tool("search_knowledge", {"topic": "diabetes"})
    assert res["success"] is True
    data = res["result"]
    assert data["count"] >= 1
    assert any("diabetes" in a["title"].lower() for a in data["articles"])


def test_mcp_invalid_parameters():
    # Calling lookup_medical_term without required parameter 'term'
    res = mcp_registry.execute_tool("lookup_medical_term", {})
    assert res["success"] is False
    assert "Invalid tool arguments" in res["error"]


def test_mcp_database_unauthorized_user():
    # Attempting to access another user's documents as standard USER
    user_context = {"user_id": "user-123", "role": "USER"}
    res = mcp_registry.execute_tool(
        "get_user_documents",
        {"user_id": "other-user-999"},
        user_context=user_context
    )
    assert res["success"] is False
    assert "Unauthorized" in res["error"]


def test_mcp_nonexistent_tool():
    res = mcp_registry.execute_tool("nonexistent_medical_tool", {})
    assert res["success"] is False
    assert "not registered" in res["error"]
