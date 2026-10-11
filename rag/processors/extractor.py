import re
from typing import List, Dict, Any, Optional

COMMON_MEDICAL_SECTIONS = [
    "Abstract",
    "Introduction",
    "Clinical History",
    "Chief Complaint",
    "Physical Examination",
    "Laboratory Findings",
    "Diagnostic Results",
    "Methodology",
    "Results",
    "Discussion",
    "Conclusions",
    "Recommendations",
    "References",
    "Dosage and Administration",
    "Contraindications",
    "Adverse Reactions"
]


def extract_metadata_from_sections(sections: List[Dict[str, Any]], filename: str) -> Dict[str, Any]:
    """Extracts overall document metadata, title, detected sections, and metrics."""
    total_words = 0
    total_chars = 0
    all_text = []
    detected_sections = []

    for s in sections:
        content = s.get("content", "")
        all_text.append(content)
        words = len(content.split())
        total_words += words
        total_chars += len(content)

        heading = s.get("section_heading", "")
        if heading and heading not in detected_sections:
            detected_sections.append(heading)

    combined_text = "\n".join(all_text)

    # Detect title
    title = ""
    if sections:
        first_content = sections[0].get("content", "").strip()
        lines = [line.strip() for line in first_content.split("\n") if line.strip()]
        if lines:
            # First significant line under 150 chars
            for line in lines[:3]:
                if 5 < len(line) < 150 and not line.lower().startswith("page"):
                    title = line
                    break

    if not title:
        # Fall back to filename without extension
        title = filename.rsplit(".", 1)[0].replace("_", " ").replace("-", " ").title()

    # Detect medical section markers in full text
    found_medical_sections = []
    for sec_name in COMMON_MEDICAL_SECTIONS:
        if re.search(r'\b' + re.escape(sec_name) + r'\b', combined_text, re.IGNORECASE):
            found_medical_sections.append(sec_name)

    return {
        "title": title,
        "total_words": total_words,
        "total_characters": total_chars,
        "page_count": len(sections),
        "detected_sections": detected_sections[:20],
        "medical_domain_sections": found_medical_sections,
        "estimated_read_time_minutes": max(1, round(total_words / 200))
    }
