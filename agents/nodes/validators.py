import re
from typing import Dict, Any
from agents.state.agent_state import AgentState
from backend.app.core.logging import app_logger

UNSAFE_ANSWER_ASSERTIONS = [
    re.compile(r'\b(?:you\s+have|i\s+diagnose\s+you\s+with|you\s+are\s+diagnosed\s+with)\b', re.IGNORECASE),
    re.compile(r'\b(?:you\s+must\s+take|i\s+prescribe|you\s+should\s+take\s+\d+\s*(?:mg|ml))\b', re.IGNORECASE)
]


def evidence_validator_node(state: AgentState) -> Dict[str, Any]:
    """Validates if retrieved evidence has sufficient factual grounding."""
    if state.get("safety_status") != "SAFE":
        return {"evidence_valid": False}

    context = state.get("retrieved_context", "").strip()
    is_valid = len(context) > 20

    return {
        "evidence_valid": is_valid
    }


def safety_validator_node(state: AgentState) -> Dict[str, Any]:
    """Post-generation safety validator ensuring no unauthorized medical claims."""
    answer = state.get("final_answer", "")

    for pattern in UNSAFE_ANSWER_ASSERTIONS:
        if pattern.search(answer):
            app_logger.warning("Unsafe clinical assertion detected in model output. Enforcing educational override.")
            sanitized = (
                "Educational Medical Information:\n\n"
                "According to established clinical documentation, symptoms matching your description "
                "require comprehensive physical evaluation by a healthcare provider. "
                "MedAssist AI cannot confirm diagnostic statuses or prescribe therapeutic courses."
            )
            return {
                "final_answer": sanitized,
                "safety_status": "OUTPUT_SANITIZED"
            }

    return {}
