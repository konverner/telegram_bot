import chromadb
from chromadb import EmbeddingFunction
from sentence_transformers import SentenceTransformer

class SentenceTransformerEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name="./models/rubert-base-cased-sentence"):
      self.model = SentenceTransformer(model_name, local_files_only=True)
    def __call__(self, input_document):
        batch_embeddings = self.model.encode(input_document)
        return batch_embeddings.tolist()


class VectorStore:
    def __init__(self):
        self.client = chromadb.Client()
        self.embedding_func = SentenceTransformerEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="user_data", embedding_function=self.embedding_func
        )
    def upsert_document(self, document_text: str, idx: int):
        embedding = self.embedding_func.model.encode([document_text])
        self.collection.upsert(
            ids=[str(idx)],
            documents=document_text,
            embeddings=embedding,
        )

    def query(self, question: str, n_results: int):
        return self.collection.query(query_texts=question, n_results=n_results)

