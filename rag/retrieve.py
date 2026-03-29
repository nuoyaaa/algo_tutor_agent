import faiss
import pickle
from rag.embed import get_embedding
from rag.rerank import rerank

index = faiss.read_index("vector_store/index.faiss")
with open("vector_store/docs.pkl", "rb") as f:
    docs = pickle.load(f)

def retrieve(query, top_k=3, dedup_threshold=0.9):
    q_emb = get_embedding([query])
    scores, indices = index.search(q_emb, top_k * 3)

    candidates = [
    {
        "text": docs[i]["text"],
        "source": docs[i]["source"],
        "retrieval_score": float(score)
    }
    for i, score in zip(indices[0], scores[0])
    if 0 <= i < len(docs)
    ]
    if not candidates:
        return []

    texts = [candidate["text"] for candidate in candidates]
    candidate_embs = get_embedding(texts)

    selected_idx = []
    selected_embs = []

    for i, (text, emb) in enumerate(zip(texts, candidate_embs)):
        is_duplicate = False

        for kept_emb in selected_embs:
            sim = emb @ kept_emb
            if sim > dedup_threshold:
                is_duplicate = True
                break

        if not is_duplicate:
            selected_idx.append(i)
            selected_embs.append(emb)

    if not selected_idx:
        return []

    selected_candidates = [candidates[i] for i in selected_idx]
    reranked = rerank(query, selected_candidates)

    final_results = []
    used_sources = set()

    for candidate in reranked:
        source = candidate["source"]
        if source in used_sources:
            continue

        final_results.append(candidate)
        used_sources.add(source)

        if len(final_results) == top_k:
            break

    return final_results