__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import chromadb
import chromadb.utils.embedding_functions as embedding_functions


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chromadb")
        huggingface_ef = embedding_functions.HuggingFaceEmbeddingFunction(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name="user_data", embedding_function=huggingface_ef
        )
    def upsert_document(self, document_text: str, idx: int):
        embedding = self.collection.embedding_function([document_text])
        self.collection.upsert(
            ids=[str(idx)],
            documents=document_text,
            embeddings=embedding,
        )

    def query(self, question: str, n_results: int):
        return self.collection.query(query_texts=question, n_results=n_results)

