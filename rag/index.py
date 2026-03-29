import os
import faiss
import pickle
from rag.embed import get_embedding

def load_docs(data_path="data"):
    docs = []
    for file_name in os.listdir(data_path):
        file_path = os.path.join(data_path, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            docs.append({
                "text": f.read(),
                "source": file_name
            })
    return docs

def split_docs(docs):
    chunks = []

    for doc in docs:
        parts = doc["text"].split("\n\n")
        i = 0

        while i < len(parts):
            part = parts[i].strip()
            if not part:
                i += 1
                continue

            # 如果当前段是标题，并且下一段存在且不是标题，就合并
            if part.startswith("#") and i + 1 < len(parts):
                next_part = parts[i + 1].strip()
                if next_part and not next_part.startswith("#"):
                    merged_text = part + "\n" + next_part
                    chunks.append({
                        "text": merged_text,
                        "source": doc["source"]
                    })
                    i += 2
                    continue

            # 其他情况单独作为一个 chunk
            chunks.append({
                "text": part,
                "source": doc["source"]
            })
            i += 1

    return chunks

def build_index():
    docs = load_docs()
    chunks = split_docs(docs)

    texts = [item["text"] for item in chunks]
    embeddings = get_embedding(texts)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    os.makedirs("vector_store", exist_ok=True)

    faiss.write_index(index, "vector_store/index.faiss")
    with open("vector_store/docs.pkl", "wb") as f:
        pickle.dump(chunks, f)

    print("Index built!")

if __name__ == "__main__":
    build_index()