import chromadb
from sentence_transformers import SentenceTransformer
from chromadb import EmbeddingFunction, Documents, Embeddings


class MyEmbeddingFunction(EmbeddingFunction):
    def __init__(self, model_name=r'C:\Users\konst\PycharmProjects\telegram-bot\telegram_bot_recsys\models\rubert-base-cased-sentence'):
      self.model = SentenceTransformer(model_name)
    def __call__(self, input: Documents) -> Embeddings:
        batch_embeddings = self.model.encode(input)
        return batch_embeddings.tolist()
        
client = chromadb.PersistentClient(path="./chromadb")

# create collection
collection = client.get_or_create_collection(
    name="user_data",  embedding_function=embedding_func
)
