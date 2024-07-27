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
    def upsert_document(self, document_text: str, document_name: str, collection_name: str):
        collection = self.client.get_or_create_collection(
            name=collection_name, embedding_function=self.embedding_func
        )
        embedding = self.embedding_func.model.encode([document_text])
        collection.upsert(
            ids=[document_name],
            documents=document_text,
            embeddings=embedding,
        )

    def query(self, question: str, n_results: int, collection_name: str):
        collection = self.client.get_collection(collection_name, embedding_function=self.embedding_func)
        return collection.query(query_texts=question, n_results=n_results)

    def get_collection_content(self, collection_name: str):
        collection = self.client.get_collection(collection_name)
        return collection.get()["ids"]
