import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from ..config import get_settings
from ..ingestion.chunker import Chunk

class RepoIndex:
    def __init__(self, repo_id: str):
        self.settings = get_settings()
        self.repo_id = repo_id
        self.dir = self.settings.data_dir / repo_id
        self.index_path = self.dir / "index.faiss"
        self.meta_path = self.dir / "metadata.json"
        self.model = SentenceTransformer(self.settings.embedding_model)
        self.index = None
        self.metadata = []
        self._load()

    def _load(self):
        if self.index_path.exists() and self.meta_path.exists():
            self.index = faiss.read_index(str(self.index_path))
            self.metadata = json.loads(self.meta_path.read_text(encoding="utf-8"))

    def build(self, chunks: list[Chunk]):
        self.dir.mkdir(parents=True, exist_ok=True)
        texts = [f"FILE: {c.path}\nLINES: {c.start_line}-{c.end_line}\n{c.content}" for c in chunks]
        vectors = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        vectors = np.asarray(vectors, dtype="float32")
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        self.index = index
        self.metadata = [c.__dict__ for c in chunks]
        faiss.write_index(index, str(self.index_path))
        self.meta_path.write_text(json.dumps(self.metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        return len(chunks)

    def search(self, query: str, top_k: int = 6):
        if self.index is None or not self.metadata:
            raise ValueError("Repository has not been indexed")
        vector = self.model.encode([query], normalize_embeddings=True)
        scores, ids = self.index.search(np.asarray(vector, dtype="float32"), top_k)
        out = []
        for score, idx in zip(scores[0], ids[0]):
            if idx < 0:
                continue
            item = dict(self.metadata[int(idx)])
            item["score"] = float(score)
            out.append(item)
        return out
