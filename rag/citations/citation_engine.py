from typing import List, Dict, Any, Optional


class CitationItem:
    def __init__(
        self,
        document_id: Optional[str],
        document_name: str,
        page_number: Optional[int],
        section_heading: Optional[str],
        snippet: str,
        relevance_score: Optional[float] = None
    ):
        self.document_id = document_id
        self.document_name = document_name
        self.page_number = page_number
        self.section_heading = section_heading
        self.snippet = snippet
        self.relevance_score = relevance_score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "document_id": self.document_id,
            "document_name": self.document_name,
            "page_number": self.page_number,
            "section_heading": self.section_heading,
            "snippet": self.snippet,
            "relevance_score": self.relevance_score
        }


def format_citations_markdown(citations: List[Dict[str, Any]]) -> str:
    """Formats structured citations into clear markdown reference cards."""
    if not citations:
        return "\n\n*Sources: No reliable uploaded document sources matched this query.*"

    lines = ["\n\n### Verified Sources & Citations:"]
    for idx, c in enumerate(citations, start=1):
        doc = c.get("document_name", "Document")
        page = f"Page {c.get('page_number')}" if c.get("page_number") else "Section General"
        section = f" — {c.get('section_heading')}" if c.get("section_heading") else ""
        score = f" (Score: {c.get('relevance_score')})" if c.get("relevance_score") is not None else ""
        snippet = c.get("snippet", "").strip().replace("\n", " ")
        if len(snippet) > 200:
            snippet = snippet[:197] + "..."

        lines.append(f"**[{idx}] {doc}** — {page}{section}{score}")
        lines.append(f"> \"{snippet}\"\n")

    return "\n".join(lines)


def build_citations_from_retrieved_chunks(chunks: List[Dict[str, Any]], doc_name_lookup: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
    """Builds verifiable citations from the top retrieved context chunks."""
    doc_name_lookup = doc_name_lookup or {}
    citations = []
    seen = set()

    for c in chunks:
        doc_id = c.get("document_id")
        page = c.get("page_number", 1)
        heading = c.get("section_heading", "General")
        key = (doc_id, page, heading)

        if key in seen:
            continue
        seen.add(key)

        snippet = c.get("content", "")
        # Compact snippet
        clean_snippet = " ".join(snippet.split())[:250]
        score = c.get("rerank_score") or c.get("relevance_score") or c.get("vector_score") or 0.0

        citations.append({
            "document_id": doc_id,
            "document_name": doc_name_lookup.get(doc_id, c.get("document_name", "Uploaded Medical Document")),
            "page_number": page,
            "section_heading": heading,
            "snippet": clean_snippet,
            "relevance_score": round(float(score), 3) if score else None
        })

    return citations
