import math
import re
from typing import List, Dict, Any, Optional
from collections import Counter


class BM25KeywordIndex:
    """Okapi BM25 implementation for lexical and keyword document retrieval."""
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunks: List[Dict[str, Any]] = []
        self.doc_lengths: List[int] = []
        self.avg_doc_len: float = 0.0
        self.doc_freqs: Dict[str, int] = Counter()
        self.term_freqs: List[Dict[str, int]] = []

    def _tokenize(self, text: str) -> List[str]:
        # Lowercase and extract alphanumeric words
        return re.findall(r'\b[a-zA-Z0-9_\-]{2,}\b', text.lower())

    def add_chunks(self, chunks: List[Dict[str, Any]]):
        for chunk in chunks:
            self.chunks.append(chunk)
            tokens = self._tokenize(chunk.get("content", ""))
            self.doc_lengths.append(len(tokens))
            t_counts = Counter(tokens)
            self.term_freqs.append(t_counts)
            for term in t_counts.keys():
                self.doc_freqs[term] += 1

        total_words = sum(self.doc_lengths)
        self.avg_doc_len = (total_words / len(self.chunks)) if self.chunks else 0.0

    def search(self, query: str, top_k: int = 5, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        query_tokens = self._tokenize(query)
        if not query_tokens or not self.chunks:
            return []

        N = len(self.chunks)
        scores = []

        for idx, chunk in enumerate(self.chunks):
            if document_id and chunk.get("document_id") != document_id:
                continue

            doc_len = self.doc_lengths[idx]
            t_freqs = self.term_freqs[idx]
            score = 0.0

            for q_term in query_tokens:
                if q_term not in t_freqs:
                    continue

                freq = t_freqs[q_term]
                df = self.doc_freqs.get(q_term, 0)
                # Standard IDF
                idf = math.log((N - df + 0.5) / (df + 0.5) + 1.0)
                # BM25 term weight
                numerator = freq * (self.k1 + 1.0)
                denominator = freq + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avg_doc_len or 1.0)))
                score += idf * (numerator / denominator)

            if score > 0:
                scores.append((score, chunk))

        scores.sort(key=lambda x: x[0], reverse=True)
        results = []
        for s, chunk in scores[:top_k]:
            res = chunk.copy()
            res["bm25_score"] = round(float(s), 4)
            results.append(res)

        return results

    def delete_document(self, document_id: str):
        keep_indices = [i for i, c in enumerate(self.chunks) if c.get("document_id") != document_id]
        self.chunks = [self.chunks[i] for i in keep_indices]
        self.doc_lengths = [self.doc_lengths[i] for i in keep_indices]
        self.term_freqs = [self.term_freqs[i] for i in keep_indices]
        self.doc_freqs = Counter()
        for t_counts in self.term_freqs:
            for term in t_counts.keys():
                self.doc_freqs[term] += 1
        total_words = sum(self.doc_lengths)
        self.avg_doc_len = (total_words / len(self.chunks)) if self.chunks else 0.0


_GLOBAL_BM25_INDEX = None


def get_keyword_index() -> BM25KeywordIndex:
    global _GLOBAL_BM25_INDEX
    if _GLOBAL_BM25_INDEX is None:
        _GLOBAL_BM25_INDEX = BM25KeywordIndex()
    return _GLOBAL_BM25_INDEX
