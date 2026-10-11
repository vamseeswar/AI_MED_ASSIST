import io
from typing import Optional
from backend.app.core.logging import app_logger

try:
    import pytesseract
    from PIL import Image
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


def perform_ocr_on_image_bytes(image_bytes: bytes) -> str:
    """Attempts OCR on image bytes using pytesseract with fallback."""
    if not TESSERACT_AVAILABLE:
        app_logger.warning("Pytesseract or PIL not available for OCR.")
        return ""

    try:
        image = Image.open(io.BytesIO(image_bytes))
        extracted_text = pytesseract.image_to_string(image)
        return extracted_text.strip()
    except Exception as exc:
        app_logger.warning(f"OCR processing failed or Tesseract binary not configured: {exc}")
        return ""
