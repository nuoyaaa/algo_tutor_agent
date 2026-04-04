import os
import faiss
import pickle
from rag.embed import get_embedding


def parse_metadata_and_text(raw_text: str):
    lines = raw_text.splitlines()

    url = None
    topic = None
    category = None
    ai_reason = None

    content_start = 0
    seen_metadata = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # 第一行标题跳过
        if i == 0 and stripped.startswith("#"):
            continue

        if stripped.startswith("URL:"):
            url = stripped.replace("URL:", "", 1).strip()
            seen_metadata = True
        elif stripped.startswith("TOPIC:"):
            topic = stripped.replace("TOPIC:", "", 1).strip()
            seen_metadata = True
        elif stripped.startswith("CATEGORY:"):
            category = stripped.replace("CATEGORY:", "", 1).strip()
            seen_metadata = True
        elif stripped.startswith("AI_REASON:"):
            ai_reason = stripped.replace("AI_REASON:", "", 1).strip()
            seen_metadata = True
        elif stripped == "":
            # 只有在已经看到过元信息后，空行才表示正文开始
            if seen_metadata:
                content_start = i + 1
                break
            else:
                continue
        else:
            # 如果既不是元信息也不是空行，说明正文直接开始
            content_start = i
            break

    content = "\n".join(lines[content_start:]).strip()

    return {
        "url": url,
        "topic": topic,
        "category": category,
        "ai_reason": ai_reason,
        "content": content
    }


def load_docs(data_path="data"):
    docs = []
    for file_name in os.listdir(data_path):
        file_path = os.path.join(data_path, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()

        parsed = parse_metadata_and_text(raw_text)

        docs.append({
            "text": parsed["content"],
            "source": file_name,
            "url": parsed["url"],
            "topic": parsed["topic"],
            "category": parsed["category"],
            "ai_reason": parsed["ai_reason"]
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
                        "source": doc["source"],
                        "url": doc["url"],
                        "topic": doc["topic"],
                        "category": doc["category"],
                        "ai_reason": doc["ai_reason"]
                    })
                    i += 2
                    continue

            # 其他情况单独作为一个 chunk
            chunks.append({
                "text": part,
                "source": doc["source"],
                "url": doc["url"],
                "topic": doc["topic"],
                "category": doc["category"],
                "ai_reason": doc["ai_reason"]
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