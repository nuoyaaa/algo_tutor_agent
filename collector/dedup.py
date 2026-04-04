import pickle
from rag.embed import get_embedding


def split_text_to_chunks(text: str):
    parts = text.split("\n\n")
    chunks = []
    i = 0

    while i < len(parts):
        part = parts[i].strip()
        if not part:
            i += 1
            continue

        if part.startswith("#") and i + 1 < len(parts):
            next_part = parts[i + 1].strip()
            if next_part and not next_part.startswith("#"):
                chunks.append(part + "\n" + next_part)
                i += 2
                continue

        chunks.append(part)
        i += 1

    return chunks


def is_similar_to_existing(new_text: str, threshold=0.92):
    with open("vector_store/docs.pkl", "rb") as f:
        existing_docs = pickle.load(f)

    existing_texts = [item["text"] for item in existing_docs]
    existing_sources = [item["source"] for item in existing_docs]

    new_chunks = split_text_to_chunks(new_text)
    if not new_chunks or not existing_texts:
        return False, None

    new_embs = get_embedding(new_chunks)
    existing_embs = get_embedding(existing_texts)

    max_sim = -1
    max_source = None

    for i, new_emb in enumerate(new_embs):
        for j, old_emb in enumerate(existing_embs):
            sim = new_emb @ old_emb
            if sim > max_sim:
                max_sim = sim
                max_source = existing_sources[j]

    if max_sim >= threshold:
        return True, max_source

    return False, None

if __name__ == "__main__":
    text = """
    # 动态规划定义

    动态规划是一种通过将原问题分解为子问题，并保存子问题答案来避免重复计算的方法。
    """
    result = is_similar_to_existing(text)
    print(result)