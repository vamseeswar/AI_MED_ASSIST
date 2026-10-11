import io
from typing import List, Dict, Any
from pypdf import PdfReader
from backend.app.core.logging import app_logger
from rag.loaders.ocr_loader import perform_ocr_on_image_bytes


def extract_pdf(file_path: str) -> List[Dict[str, Any]]:
    """Extracts text page-by-page from a PDF document, preserving page numbers."""
    pages_data = []

    try:
        reader = PdfReader(file_path)
        total_pages = len(reader.pages)

        for page_idx, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            text = text.strip()

            # If text is empty or very short, check for embedded images for OCR
            if len(text) < 30 and hasattr(page, "images") and len(page.images) > 0:
                app_logger.info(f"Page {page_idx} has little text; attempting OCR on embedded images...")
                ocr_texts = []
                for img in page.images:
                    try:
                        img_text = perform_ocr_on_image_bytes(img.data)
                        if img_text:
                            ocr_texts.append(img_text)
                    except Exception as ocr_err:
                        app_logger.debug(f"Image OCR error on page {page_idx}: {ocr_err}")
                if ocr_texts:
                    text = "\n".join(ocr_texts).strip()

            pages_data.append({
                "page_number": page_idx,
                "section_heading": f"Page {page_idx}",
                "content": text,
                "metadata": {
                    "total_pages": total_pages,
                    "source_type": "pdf"
                }
            })

    except Exception as exc:
        app_logger.error(f"Error parsing PDF file {file_path}: {exc}")
        raise ValueError(f"Could not read PDF file: {exc}")

    return pages_data
