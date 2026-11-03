import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
COLLECTION_NAME = "collage_notes_database"

_chroma_client = None
_embedding_fn = None

def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        db_path = str(ROOT_DIR / "vector_db")
        _chroma_client = chromadb.PersistentClient(path=db_path)
    return _chroma_client

def get_embedding_function():
    global _embedding_fn
    if _embedding_fn is None:
        embedding_model = "mixedbread-ai/mxbai-embed-large-v1"
        _embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=embedding_model,
            device="cpu"
        )
    return _embedding_fn

def get_indexed_collection():
    client = get_chroma_client()
    try:
        return client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=get_embedding_function()
        )
    except Exception:
        raise ValueError(
            "No study materials indexed yet. "
            "Please download a subject first via the Download page."
        )

def retrieve(query, n_results=5):
    """Query the vector DB, returning (documents, metadatas)."""
    collection = get_indexed_collection()
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    return documents, metadatas

def get_context(query, n_results=5):
    """Join retrieved documents into a single context string."""
    documents, _ = retrieve(query, n_results)
    context = ""
    for doc in documents:
        context += f"\n{doc}\n\n"
    return context
