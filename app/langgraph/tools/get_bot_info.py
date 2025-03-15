from langchain_core.tools import tool
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore
import os

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


collection_name = "mikrotik-bot-info"

qdrant_api_endpoint = os.getenv("QDRANT_API_ENDPOINT")
qdrant_api_key = os.getenv("QDRANT_API_KEY")

client = QdrantClient(
    url=qdrant_api_endpoint,
    api_key=qdrant_api_key
)
vector_store = QdrantVectorStore(
    client=client,
    collection_name=collection_name,
    embedding=embeddings,
)

@tool
def get_bot_info(query: str) -> str:
    """
    Busca información sobre el bot. Desde una base vectorial. Es importante que la pregunta sea para este fin.

    Args:
        query (str): Consulta a realizar.
    
    Returns:
        str: Información sobre el bot.
    """
    vectors = vector_store.similarity_search(query=query, k=4)

    context_str = "Resultado en Base de datos:\n"
    
    for i, v in enumerate(vectors):
        context_str += f"{i+1}. {v.page_content}\n"
    return {'answer':context_str, 'suggestions':{}}
