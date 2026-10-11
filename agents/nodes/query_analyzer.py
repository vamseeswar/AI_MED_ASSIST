import re
from typing import Dict, Any
from agents.state.agent_state import AgentState
from backend.app.security.prompt_guard import (
    assess_medical_safety,
    detect_prompt_injection
)
from backend.app.core.logging import app_logger


def query_analyzer_node(state: AgentState) -> Dict[str, Any]:
    """Analyzes query for security, medical safety violations, and intent classification."""
    query = state.get("user_query", "").strip()

    # 1. Prompt Injection Defense
    is_injection, injection_msg = detect_prompt_injection(query)
    if is_injection:
        app_logger.warning(f"Prompt injection attempt blocked: {injection_msg}")
        return {
            "intent": "safety_refusal",
            "safety_status": "INJECTION_BLOCKED",
            "safety_message": "Request contains unauthorized system override patterns and was blocked.",
            "final_answer": "Security Policy Warning: Your query contains unauthorized instruction override patterns. Operation halted.",
            "agent_provenance": "Security Guard"
        }

    # 2. Medical Safety Evaluation (Diagnosis / Prescription check)
    is_violation, category, refusal_msg = assess_medical_safety(query)
    if is_violation:
        app_logger.info(f"Medical safety boundary triggered: {category}")
        return {
            "intent": "safety_refusal",
            "safety_status": category,
            "safety_message": refusal_msg,
            "final_answer": refusal_msg,
            "agent_provenance": "Medical Safety Guard"
        }

    # 3. Intent Classification
    q_lower = query.lower()
    if any(k in q_lower for k in ["report", "synthesize", "generate summary report"]):
        intent = "report_generation"
    elif any(k in q_lower for k in ["structure", "extract table", "columns", "statistics", "word count"]):
        intent = "document_analysis"
    elif any(k in q_lower for k in ["what is", "define", "meaning of", "terminology", "explain term", "guideline"]):
        intent = "medical_knowledge"
    else:
        # Default to RAG document search
        intent = "rag_document"

    return {
        "intent": intent,
        "safety_status": "SAFE",
        "safety_message": None
    }
