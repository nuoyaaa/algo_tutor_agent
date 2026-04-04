import os
import re
import json
import subprocess
from collector.fetch import fetch_article
from collector.filter import evaluate_article
from collector.dedup import is_similar_to_existing
from collector.resolve_conflict import resolve_conflict
from collector.generate_path import generate_learning_path
from collector.generate_parent import generate_parent

KNOWLEDGE_MAP_PATH = "knowledge_map.json"


def slugify(text: str) -> str:
    text = re.sub(r"[^\w\u4e00-\u9fff-]+", "_", text)
    return text[:50].strip("_")


def save_article(topic: str, category: str, content: str):
    os.makedirs("data", exist_ok=True)
    filename = f"{slugify(topic)}_{slugify(category)}.md"
    path = os.path.join("data", filename)

    base, ext = os.path.splitext(path)
    count = 1
    while os.path.exists(path):
        path = f"{base}_{count}{ext}"
        count += 1

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

    return path


def load_existing_article(source_name: str):
    path = os.path.join("data", source_name)
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_knowledge_map():
    if not os.path.exists(KNOWLEDGE_MAP_PATH):
        return {}

    with open(KNOWLEDGE_MAP_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_knowledge_map(knowledge_map):
    with open(KNOWLEDGE_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(knowledge_map, f, ensure_ascii=False, indent=2)


def update_knowledge_map(topic: str, resource_name: str, category: str, content: str):
    knowledge_map = load_knowledge_map()

    is_new_topic = topic not in knowledge_map
    need_generate_path = False

    if is_new_topic:
        knowledge_map[topic] = {
            "parent": None,
            "prerequisites": [],
            "steps": [],
            "resources": []
        }
        need_generate_path = True
    else:
        if not knowledge_map[topic]["prerequisites"] or not knowledge_map[topic]["steps"]:
            need_generate_path = True
        if "parent" not in knowledge_map[topic]:
            knowledge_map[topic]["parent"] = None

    if resource_name not in knowledge_map[topic]["resources"]:
        knowledge_map[topic]["resources"].append(resource_name)

    if need_generate_path:
        generated = generate_learning_path(topic, category, content)
        knowledge_map[topic]["prerequisites"] = generated["prerequisites"]
        knowledge_map[topic]["steps"] = generated["steps"]

    # 只有在新 topic 或 parent 为空时，才尝试生成 parent
    if knowledge_map[topic].get("parent") is None:
        existing_topics = [t for t in knowledge_map.keys() if t != topic]
        if existing_topics:
            parent_result = generate_parent(topic, existing_topics)
            knowledge_map[topic]["parent"] = parent_result["parent"]

    save_knowledge_map(knowledge_map)


def ingest_url(url: str):
    article = fetch_article(url)
    if not article["success"]:
        print("抓取失败：", article["error"])
        return

    title = article.get("title") or url
    content = article["content"]

    result = evaluate_article(title, content)
    print("筛选结果：", result)

    if not result["keep"]:
        print("该资料未被纳入知识库。")
        return

    markdown_text = (
        f"# {result['topic']} {result['category']}\n\n"
        f"URL: {url}\n"
        f"TOPIC: {result['topic']}\n"
        f"CATEGORY: {result['category']}\n"
        f"AI_REASON: {result['reason']}\n\n"
        f"{content}"
    )

    is_dup, dup_source = is_similar_to_existing(markdown_text, threshold=0.92)
    if is_dup:
        old_text = load_existing_article(dup_source)
        if old_text is None:
            print(f"检测到相似资料，但无法读取旧资料：{dup_source}")
            return

        decision = resolve_conflict(
            old_source=dup_source,
            old_text=old_text,
            new_url=url,
            new_text=markdown_text
        )

        print("冲突仲裁结果：", decision)

        if decision["winner"] == "old":
            print(f"保留旧资料：{dup_source}")
            return
        else:
            old_path = os.path.join("data", dup_source)
            if os.path.exists(old_path):
                os.remove(old_path)
                print(f"已删除旧资料：{dup_source}")

    path = save_article(result["topic"], result["category"], markdown_text)
    print(f"已写入知识库：{path}")

    resource_name = os.path.basename(path)
    update_knowledge_map(
        result["topic"],
        resource_name,
        result["category"],
        content
    )
    print(f"已同步更新 learning path：{resource_name}")

    print("正在重建索引...")
    subprocess.run(["python", "-m", "rag.index"], check=True)
    print("索引更新完成。")


if __name__ == "__main__":
    url = input("请输入文章 URL：").strip()
    ingest_url(url)