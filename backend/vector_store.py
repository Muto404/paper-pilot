import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter

papers_storage = {}

class VectorStore:
    def __init__(self, paper_id: str, text: str):
        self.paper_id = paper_id
        self.text = text
        self.model = SentenceTransformer('moka-ai/m3e-base')
        self.vector_db = self._create_vector_db()

    def _create_vector_db(self):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        sentences = text_splitter.split_text(self.text)
        embeddings = self.model.encode(sentences)
        vector_db = faiss.IndexFlatL2(embeddings.shape[1])
        vector_db.add(np.array(embeddings, dtype=np.float32))
        papers_storage[self.paper_id] = {
            "vector_db": vector_db,
            "sentences": sentences,
            "model": self.model
        }
        return vector_db

    @staticmethod
    def get_retriever(paper_id: str):
        if paper_id in papers_storage:
            return papers_storage[paper_id]
        return None