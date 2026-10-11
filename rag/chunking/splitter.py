import re
from typing import List, Dict, Any
from backend.app.core.config import settings


class MedicalTextSplitter:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP
        self.separators = ["\n\n", "\n", ". ", "; ", ", ", " "]

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Recursively splits text using hierarchical separators."""
        final_chunks = []
        separator = separators[-1]
        new_separators = []

        for i, sep in enumerate(separators):
            if sep == "":
                separator = ""
                break
            if sep in text:
                separator = sep
                new_separators = separators[i + 1:]
                break

        splits = text.split(separator) if separator else list(text)

        good_splits = []
        for s in splits:
            if separator and s:
                s = s + separator if separator.strip() else s
            if len(s) < self.chunk_size:
                good_splits.append(s)
            else:
                if new_separators:
                    sub_chunks = self._split_text(s, new_separators)
                    good_splits.extend(sub_chunks)
                else:
                    # Hard split
                    for idx in range(0, len(s), self.chunk_size - self.chunk_overlap):
                        good_splits.append(s[idx:idx + self.chunk_size])

        # Merge splits up to chunk_size with overlap
        current_chunk = []
        current_len = 0

        for piece in good_splits:
            piece_len = len(piece)
            if current_len + piece_len > self.chunk_size and current_chunk:
                merged = "".join(current_chunk).strip()
                if merged:
                    final_chunks.append(merged)
                # Overlap calculation
                while current_chunk and current_len > self.chunk_overlap:
                    popped = current_chunk.pop(0)
                    current_len -= len(popped)

            current_chunk.append(piece)
            current_len += piece_len

        if current_chunk:
            merged = "".join(current_chunk).strip()
            if merged:
                final_chunks.append(merged)

        return final_chunks

    def chunk_document_sections(self, sections: List[Dict[str, Any]], document_id: str) -> List[Dict[str, Any]]:
        """Takes extracted sections and produces indexed chunks with page and section metadata."""
        chunks = []
        chunk_idx = 0

        for section in sections:
            page_num = section.get("page_number", 1)
            heading = section.get("section_heading", "General")
            raw_content = section.get("content", "")

            if not raw_content.strip():
                continue

            text_chunks = self._split_text(raw_content, self.separators)

            for tc in text_chunks:
                if len(tc.strip()) < 15:
                    continue  # Ignore tiny artifact fragments

                token_estimate = len(tc.split())

                chunks.append({
                    "document_id": document_id,
                    "chunk_index": chunk_idx,
                    "content": tc,
                    "cleaned_content": tc.lower().strip(),
                    "page_number": page_num,
                    "section_heading": heading,
                    "token_count": token_estimate,
                    "metadata": {
                        "page_number": page_num,
                        "section_heading": heading,
                        "token_count": token_estimate
                    }
                })
                chunk_idx += 1

        return chunks
