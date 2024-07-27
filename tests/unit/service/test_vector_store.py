from telegram_bot.service.vector_store import VectorStore

def test_init():
    vector_store = VectorStore()
    assert vector_store.client is not None
    assert vector_store.collection is not None

def test_upsert_document():
    vector_store = VectorStore()
    document_text = "test document"
    question = "test question"
    idx = 1

    vector_store.upsert_document(document_text, idx)
    results = vector_store.query(question, n_results=1)

    assert len(results["documents"]) != 0, results

