from typing import List, Dict, Any
from backend.app.core.logging import app_logger


def extract_txt(file_path: str) -> List[Dict[str, Any]]:
    """Extracts text from plain text files, handling encodings safely."""
    sections_data = []

    content = ""
    for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                content = f.read()
            break
        except UnicodeDecodeError:
            continue

    if not content:
        raise ValueError("Could not decode plain text file with supported encodings.")

    # Split into logical sections by double line breaks or chunk paragraphs
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [content.strip()]

    # Group into sections of ~3-5 paragraphs to represent logical pages
    batch_size = 4
    for i in range(0, len(paragraphs), batch_size):
        page_num = (i // batch_size) + 1
        page_text = "\n\n".join(paragraphs[i:i + batch_size])
        first_line = paragraphs[i].split("\n")[0][:60]
        sections_data.append({
            "page_number": page_num,
            "section_heading": f"Section {page_num}: {first_line}" if first_line else f"Section {page_num}",
            "content": page_text,
            "metadata": {"source_type": "txt", "page_number": page_num}
        })

    return sections_data
