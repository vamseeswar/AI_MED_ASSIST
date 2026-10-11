import re
import unicodedata
from typing import List


def normalize_text_for_ml(text: str) -> str:
    """Normalizes text for ML feature extraction."""
    if not text:
        return ""

    text = unicodedata.normalize("NFKC", text).lower()
    # Replace punctuation with spaces
    text = re.sub(r'[^a-z0-9\s\-]', ' ', text)
    # Condense whitespace
    tokens = text.split()
    return " ".join(tokens)
