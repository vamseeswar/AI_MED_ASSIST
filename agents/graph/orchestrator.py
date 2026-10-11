from typing import Dict, Any, Optional
from langgraph.graph import StateGraph, START, END

from agents.state.agent_state import AgentState
from agents.nodes.query_analyzer import query_analyzer_node
from agents.nodes.rag_agent_node import rag_agent_node
from agents.nodes.knowledge_agent_node import knowledge_agent_node
from agents.nodes.analysis_agent_node import analysis_agent_node
from agents.nodes.report_agent_node import report_agent_node
from agents.nodes.validators import evidence_validator_node, safety_validator_node
from agents.nodes.generator_node import response_generator_node
from backend.app.core.logging import app_logger


def route_intent(state: AgentState) -> str:
    """Conditional edge router based on intent analysis."""
    intent = state.get("intent", "rag_document")
    if intent == "safety_refusal":
        return "safety_exit"
    elif intent == "medical_knowledge":
        return "knowledge_agent"
    elif intent == "document_analysis":
        return "analysis_agent"
    elif intent == "report_generation":
        return "report_agent"
    else:
        return "rag_agent"


def build_medassist_graph():
    """Builds and compiles the full LangGraph multi-agent state graph."""
    workflow = StateGraph(AgentState)

    # 1. Add Nodes
    workflow.add_node("query_analyzer", query_analyzer_node)
    workflow.add_node("rag_agent", rag_agent_node)
    workflow.add_node("knowledge_agent", knowledge_agent_node)
    workflow.add_node("analysis_agent", analysis_agent_node)
    workflow.add_node("report_agent", report_agent_node)
    workflow.add_node("evidence_validator", evidence_validator_node)
    workflow.add_node("response_generator", response_generator_node)
    workflow.add_node("safety_validator", safety_validator_node)

    # 2. Add Edges
    workflow.add_edge(START, "query_analyzer")

    # Conditional branching from query analyzer
    workflow.add_conditional_edges(
        "query_analyzer",
        route_intent,
        {
            "safety_exit": END,
            "rag_agent": "rag_agent",
            "knowledge_agent": "knowledge_agent",
            "analysis_agent": "analysis_agent",
            "report_agent": "report_agent"
        }
    )

    # Connect agents to evidence validator
    workflow.add_edge("rag_agent", "evidence_validator")
    workflow.add_edge("knowledge_agent", "evidence_validator")
    workflow.add_edge("analysis_agent", "evidence_validator")
    workflow.add_edge("report_agent", "evidence_validator")

    # Evidence validator to response generator
    workflow.add_edge("evidence_validator", "response_generator")

    # Response generator to safety validator
    workflow.add_edge("response_generator", "safety_validator")

    # Safety validator to END
    workflow.add_edge("safety_validator", END)

    app_logger.info("Compiled LangGraph state graph for MedAssist AI.")
    return workflow.compile()


# Global compiled app
_COMPILED_GRAPH = None


def get_agent_graph():
    global _COMPILED_GRAPH
    if _COMPILED_GRAPH is None:
        _COMPILED_GRAPH = build_medassist_graph()
    return _COMPILED_GRAPH


def run_agent_workflow(
    query: str,
    document_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    history: Optional[list] = None
) -> Dict[str, Any]:
    """Entrypoint function to execute the LangGraph multi-agent workflow."""
    app = get_agent_graph()

    initial_state: AgentState = {
        "user_query": query,
        "conversation_id": conversation_id,
        "document_id": document_id,
        "history": history or [],
        "intent": "",
        "retrieved_context": "",
        "tool_results": [],
        "evidence_valid": False,
        "safety_status": "PENDING",
        "safety_message": None,
        "agent_provenance": "General Assistant",
        "final_answer": "",
        "citations": [],
        "errors": []
    }

    result = app.invoke(initial_state)
    return result
