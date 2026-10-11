import re
import unicodedata


def clean_text(text: str) -> str:
    """Cleans extracted raw text, removes artifacts, normalizes whitespace and unicode."""
    if not text:
        return ""

    # Normalize unicode (NFKC)
    text = unicodedata.normalize("NFKC", text)

    # Remove non-printable / control characters (preserve \n and \t)
    text = "".join(ch for ch in text if ch in ("\n", "\t") or unicodedata.category(ch)[0] != "C")

    # Replace weird bullet points with standard dashes
    text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219]', '- ', text)

    # Remove repeated page number noise (e.g. "Page 1 of 12" at ends of lines)
    text = re.sub(r'(?i)page\s+\d+\s+(?:of|\/)\s+\d+', '', text)

    # Normalize carriage returns and tabs
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    text = re.sub(r'\t+', ' ', text)

    # Condense 3+ newlines to double newline
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Condense multiple horizontal spaces to single space
    text = re.sub(r'[^\S\r\n]{2,}', ' ', text)

    return text.strip()
