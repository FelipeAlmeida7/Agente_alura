from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class Chunk:
    source: str
    text: str

def chunk_text(text, source, chunk_size=900, overlap=150):
    clean = " ".join(text.split())
    chunks = []
    start = 0
    while start < len(clean):
        end = min(start + chunk_size, len(clean))
        chunks.append(Chunk(source, clean[start:end]))
        if end == len(clean):
            break
        start = end - overlap
    return chunks

class KnowledgeBase:
    def __init__(self, chunks):
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode")
        self.matrix = self.vectorizer.fit_transform([c.text for c in chunks]) if chunks else None

    def search(self, question, top_k=4):
        if self.matrix is None:
            return []
        query = self.vectorizer.transform([question])
        scores = cosine_similarity(query, self.matrix).flatten()
        indexes = scores.argsort()[::-1][:top_k]
        return [(self.chunks[i], float(scores[i])) for i in indexes if scores[i] > 0]

def build_context(results):
    return "\n\n".join(
        f"[Fonte {i}: {chunk.source}]\n{chunk.text}"
        for i, (chunk, _score) in enumerate(results, 1)
    )
