from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict):
    user_query: str
    conversation_id: Optional[str]
    document_id: Optional[str]
    history: List[Dict[str, str]]
    intent: str  # rag_document, medical_knowledge, document_analysis, report_generation, safety_refusal
    retrieved_context: str
    tool_results: List[Dict[str, Any]]
    evidence_valid: bool
    safety_status: str  # SAFE, DIAGNOSIS_BLOCKED, TREATMENT_BLOCKED, INJECTION_BLOCKED
    safety_message: Optional[str]
    agent_provenance: str
    final_answer: str
    citations: List[Dict[str, Any]]
    errors: List[str]
