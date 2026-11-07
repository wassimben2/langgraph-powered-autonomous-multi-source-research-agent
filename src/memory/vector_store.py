from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

embeddings = OllamaEmbeddings(model="nomic-embed-text") ##define the embedding model

vector_store = Chroma( ##define the vector store
    collection_name="research_memory",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
    
)

def get_all_memories():
    data = vector_store.get(include=["metadatas", "documents"])

    memories = []

    for content, metadata, doc_id in zip(
        data["documents"],
        data["metadatas"],
        data["ids"]
    ):
        memories.append(
            Document(
                page_content=content,
                metadata={**metadata, "id": doc_id}
            )
        )

    return memories