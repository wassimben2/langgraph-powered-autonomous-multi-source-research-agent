from collections import defaultdict
from rank_bm25 import BM25Okapi
from memory.vector_store import get_all_memories , vector_store

def RRF_function(    
    ranked_results: list[list],
    k: int = 60,
    ):
    scores = defaultdict(float) 
    documents_map = {}
    for ranking in ranked_results: ## we are iterating through each ranking we get and then from each documents we get its rank and then for each doc we do score = score +1/(k+rank)
 ## so for example if we have 3 ranking made by 2 different types of search methods and we have 3 documents in each ranking we will do the following:
        for rank , document in enumerate(ranking , start=1):
            doc_id = document.metadata.get("id")
            scores[doc_id] += 1 / (k+rank) 
            documents_map[doc_id] = document

    sorted_ids = sorted(
    scores,
    key=lambda doc_id: scores[doc_id],
    reverse=True
)
    return [
        documents_map[doc_id]
        for doc_id in sorted_ids
    ]

def semantic_search(user_question:str ):
    results = vector_store.similarity_search(query=user_question  , k=5
    )
    for doc in results:
        if "id" not in doc.metadata:
            # On devra garantir cet ID au moment du stockage.
            print("Warning: document has no ID in metadata")
    return results

def BM25_function(user_question:str ):
    memories = get_all_memories()
    if not memories:
        return []
    tokenized_memories = [
        doc.page_content.lower().split() for doc in memories
    ]
    bm25 = BM25Okapi(tokenized_memories)
    tokenized_query = user_question.lower().split()
    scores = bm25.get_scores(tokenized_query)
    ranked_results = sorted(
        zip(memories, scores),
        key=lambda x: x[1],
        reverse=True
    )

    return [memory for memory, score in ranked_results[:10]]
def hybrid_search(user_question:str ):
    semantic_results = semantic_search(user_question)
    bm25_results = BM25_function(user_question)
    combined_results = RRF_function([semantic_results , bm25_results])
    return combined_results[:5]