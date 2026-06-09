from app.rag.embedder import Embedder
from app.rag.vector_store import VectorStore

embedder = Embedder()
vector_store = VectorStore(dim=1024)