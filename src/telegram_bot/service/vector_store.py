import chromadb
from sentence_transformers import SentenceTransformer
from chromadb import EmbeddingFunction, Documents, Embeddings


class MyEmbeddingFunction(EmbeddingFunction):
    def __init__(self,
                 model_name=r'C:\Users\konst\PycharmProjects\telegram-bot\telegram_bot_recsys\models\rubert-base-cased-sentence'):
        self.model = SentenceTransformer(model_name)

    def __call__(self, input_docs: Documents) -> Embeddings:
        batch_embeddings = self.model.encode(input_docs)
        return batch_embeddings.tolist()


class VectorStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path="./chromadb")
        self.collection = self.client.get_or_create_collection(
            name="user_data", embedding_function=MyEmbeddingFunction()
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

