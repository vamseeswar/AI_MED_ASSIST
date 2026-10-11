from typing import List, Dict, Any
from docx import Document as DocxDocument
from backend.app.core.logging import app_logger


def extract_docx(file_path: str) -> List[Dict[str, Any]]:
    """Extracts structured sections, headings, paragraphs, and tables from a DOCX document."""
    sections_data = []

    try:
        doc = DocxDocument(file_path)
        current_heading = "Introduction"
        current_content_lines = []
        section_idx = 1

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            # Check if this paragraph is a Heading
            if para.style.name.startswith("Heading"):
                if current_content_lines:
                    sections_data.append({
                        "page_number": section_idx,
                        "section_heading": current_heading,
                        "content": "\n".join(current_content_lines),
                        "metadata": {"source_type": "docx", "section_index": section_idx}
                    })
                    section_idx += 1
                    current_content_lines = []
                current_heading = text
            else:
                current_content_lines.append(text)

        # Extract tables as structured markdown
        for table in doc.tables:
            table_lines = []
            for row in table.rows:
                row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                table_lines.append(" | ".join(row_cells))
            if table_lines:
                current_content_lines.append("\nTable Data:\n" + "\n".join(table_lines))

        # Append final section
        if current_content_lines:
            sections_data.append({
                "page_number": section_idx,
                "section_heading": current_heading,
                "content": "\n".join(current_content_lines),
                "metadata": {"source_type": "docx", "section_index": section_idx}
            })

    except Exception as exc:
        app_logger.error(f"Error parsing DOCX file {file_path}: {exc}")
        raise ValueError(f"Could not read DOCX file: {exc}")

    return sections_data
