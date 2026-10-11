import io
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.main import app
from backend.app.core.database import Base, get_db
from rag.pipelines.rag_pipeline import get_rag_pipeline
from rag.chunking.splitter import MedicalTextSplitter
from rag.citations.citation_engine import format_citations_markdown, build_citations_from_retrieved_chunks

client = TestClient(app)


@pytest.fixture
def auth_headers():
    client.post("/api/auth/register", json={
        "email": "rag_tester@medassist.ai",
        "password": "Password123!"
    })
    token = client.post("/api/auth/login", json={
        "email": "rag_tester@medassist.ai",
        "password": "Password123!"
    }).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_text_splitter_chunking():
    splitter = MedicalTextSplitter(chunk_size=100, chunk_overlap=20)
    sections = [
        {
            "page_number": 1,
            "section_heading": "Pharmacology",
            "content": "Metformin hydrochloride is an oral antihyperglycemic medication used in the management of type 2 diabetes mellitus. It decreases hepatic glucose production, decreases intestinal absorption of glucose, and improves insulin sensitivity."
        }
    ]
    chunks = splitter.chunk_document_sections(sections, document_id="doc-test-1")
    assert len(chunks) >= 2
    assert chunks[0]["page_number"] == 1
    assert chunks[0]["section_heading"] == "Pharmacology"
    assert "document_id" in chunks[0]


def test_rag_indexing_and_hybrid_retrieval():
    pipeline = get_rag_pipeline()

    sample_sections = [
        {
            "page_number": 2,
            "section_heading": "Asthma Therapeutics",
            "content": "Inhaled corticosteroids such as fluticasone propionate are the primary controller medications for persistent asthma in pediatric and adult patients."
        },
        {
            "page_number": 4,
            "section_heading": "Adverse Reactions",
            "content": "Common adverse events observed in clinical trials included dysphonia and oral candidiasis, preventable by rinsing the mouth after inhalation."
        }
    ]

    indexed_chunks = pipeline.index_document_sections(
        document_id="doc-asthma-101",
        document_name="asthma_guidelines.pdf",
        sections=sample_sections
    )
    assert len(indexed_chunks) >= 2

    # Query for corticosteroid
    retrieval = pipeline.retrieve("inhaled corticosteroids controller medications", top_k=2, document_id="doc-asthma-101")
    assert retrieval["chunks_retrieved_count"] > 0
    top_chunk = retrieval["chunks"][0]
    assert "asthma" in top_chunk["content"].lower() or "corticosteroids" in top_chunk["content"].lower()

    # Verify citation generated
    citations = retrieval["citations"]
    assert len(citations) > 0
    assert citations[0]["document_name"] == "asthma_guidelines.pdf"
    assert citations[0]["page_number"] in [2, 4]


def test_citation_markdown_formatting():
    citations = [
        {
            "document_name": "diabetes_care_2024.pdf",
            "page_number": 14,
            "section_heading": "Glycemic Targets",
            "snippet": "An HbA1c target below 7.0 percent is recommended for nonpregnant adults.",
            "relevance_score": 0.89
        }
    ]
    md = format_citations_markdown(citations)
    assert "diabetes_care_2024.pdf" in md
    assert "Page 14" in md
    assert "HbA1c target" in md

    # Test empty citations
    empty_md = format_citations_markdown([])
    assert "No reliable uploaded document sources" in empty_md


def test_search_api_endpoint(auth_headers):
    # Upload doc first
    content = (
        "ONCOLOGY STUDY ON IMMUNOTHERAPY\n\n"
        "Checkpoint inhibitors targeting PD-1 and PD-L1 have transformed the treatment paradigm for metastatic melanoma.\n\n"
        "Immune-related adverse events commonly affect gastrointestinal, hepatic, and endocrine systems."
    )
    files = {"file": ("oncology_study.txt", io.BytesIO(content.encode("utf-8")), "text/plain")}
    client.post("/api/documents/upload", headers=auth_headers, files=files)

    # Search with hybrid mode
    res = client.post("/api/search", headers=auth_headers, json={
        "query": "checkpoint inhibitors PD-1 melanoma",
        "search_type": "hybrid",
        "top_k": 3
    })
    assert res.status_code == 200
    search_data = res.json()
    assert search_data["total_results"] > 0
    assert any("melanoma" in r["snippet"].lower() for r in search_data["results"])
