import pytest
from agents.graph.orchestrator import run_agent_workflow, get_agent_graph
from rag.pipelines.rag_pipeline import get_rag_pipeline


def test_agent_graph_compilation():
    graph = get_agent_graph()
    assert graph is not None


def test_document_agent_rag_query():
    # Pre-index a guideline snippet
    pipeline = get_rag_pipeline()
    pipeline.index_document_sections(
        document_id="doc-langgraph-1",
        document_name="hypertension_protocols.pdf",
        sections=[{
            "page_number": 3,
            "section_heading": "DASH Protocol",
            "content": "The Dietary Approaches to Stop Hypertension (DASH) emphasizes dietary potassium, calcium, magnesium, and dietary fiber."
        }]
    )

    result = run_agent_workflow("What is the DASH protocol according to the guidelines?")
    assert result["safety_status"] == "SAFE"
    assert result["final_answer"] != ""
    assert "Disclaimer" in result["final_answer"]
    assert len(result["tool_results"]) > 0


def test_knowledge_agent_terminology_routing():
    result = run_agent_workflow("What is the meaning of the medical term dyspnea?")
    assert result["intent"] == "medical_knowledge"
    assert result["agent_provenance"] == "Knowledge Agent"
    assert "dyspnea" in result["final_answer"].lower() or "breathing" in result["final_answer"].lower()


def test_report_agent_routing():
    result = run_agent_workflow("Please synthesize and generate summary report for clinical records.")
    assert result["intent"] == "report_generation"
    assert result["agent_provenance"] == "Report Agent"
    assert "Summary" in result["final_answer"] or "Report" in result["final_answer"]
