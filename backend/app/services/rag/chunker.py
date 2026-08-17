import re
from typing import List, Dict, Any

class TextChunk:
    """Represents a chunked slice of an indexed KSHAN entity document."""
    def __init__(self, content: str, chunk_index: int, total_chunks: int, metadata: Dict[str, Any]):
        self.content = content.strip()
        self.chunk_index = chunk_index
        self.total_chunks = total_chunks
        self.metadata = metadata

class DeterministicChunker:
    """
    Deterministic semantic chunker for narrative multiverse documents.
    Splits text along logical sentence/paragraph boundaries while preserving context headers.
    """
    def __init__(self, max_chunk_chars: int = 1200, overlap_chars: int = 150):
        self.max_chunk_chars = max_chunk_chars
        self.overlap_chars = overlap_chars

    def chunk_document(self, text: str, base_metadata: Dict[str, Any]) -> List[TextChunk]:
        clean_text = text.strip()
        if not clean_text:
            return []

        # If document fits within max chunk size, return single chunk
        if len(clean_text) <= self.max_chunk_chars:
            return [TextChunk(content=clean_text, chunk_index=0, total_chunks=1, metadata=dict(base_metadata))]

        # Split along paragraphs or sentences
        paragraphs = clean_text.split("\n\n")
        chunks_text: List[str] = []
        current_chunk = ""

        for p in paragraphs:
            p = p.strip()
            if not p:
                continue

            if len(current_chunk) + len(p) + 2 <= self.max_chunk_chars:
                current_chunk = f"{current_chunk}\n\n{p}".strip()
            else:
                if current_chunk:
                    chunks_text.append(current_chunk)
                # If a single paragraph is longer than max_chunk_chars, split by sentences
                if len(p) > self.max_chunk_chars:
                    sentences = re.split(r'(?<=[.!?])\s+', p)
                    sentence_chunk = ""
                    for s in sentences:
                        if len(sentence_chunk) + len(s) + 1 <= self.max_chunk_chars:
                            sentence_chunk = f"{sentence_chunk} {s}".strip()
                        else:
                            if sentence_chunk:
                                chunks_text.append(sentence_chunk)
                            sentence_chunk = s
                    if sentence_chunk:
                        current_chunk = sentence_chunk
                else:
                    current_chunk = p

        if current_chunk:
            chunks_text.append(current_chunk)

        total = len(chunks_text)
        result: List[TextChunk] = []
        for idx, ct in enumerate(chunks_text):
            meta = dict(base_metadata)
            meta["chunk_index"] = idx
            meta["total_chunks"] = total
            result.append(TextChunk(content=ct, chunk_index=idx, total_chunks=total, metadata=meta))

        return result

chunker = DeterministicChunker()
