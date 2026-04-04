import os
import json
import sys

# 确保可以从项目根目录导入 collector 模块
sys.path.append(os.path.abspath("."))

from collector.generate_path import generate_learning_path

KNOWLEDGE_MAP_PATH = "knowledge_map.json"
DATA_DIR = "data"


def load_knowledge_map():
    if not os.path.exists(KNOWLEDGE_MAP_PATH):
        return {}

    with open(KNOWLEDGE_MAP_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_knowledge_map(knowledge_map):
    with open(KNOWLEDGE_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(knowledge_map, f, ensure_ascii=False, indent=2)


def parse_metadata_and_content(raw_text: str):
    """
    解析你当前 markdown 文件头部的元信息：
    # 标题

    URL: ...
    TOPIC: ...
    CATEGORY: ...
    AI_REASON: ...

    正文...
    """
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
            if seen_metadata:
                content_start = i + 1
                break
            else:
                continue
        else:
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


def load_resource_file(resource_name: str):
    path = os.path.join(DATA_DIR, resource_name)
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    return parse_metadata_and_content(raw_text)


def fill_missing_paths():
    knowledge_map = load_knowledge_map()
    if not knowledge_map:
        print("knowledge_map.json 不存在或为空。")
        return

    updated_count = 0
    skipped_count = 0

    for topic, info in knowledge_map.items():
        prerequisites = info.get("prerequisites", [])
        steps = info.get("steps", [])
        resources = info.get("resources", [])

        # 已经完整的不处理
        if prerequisites and steps:
            skipped_count += 1
            continue

        if not resources:
            print(f"[跳过] {topic} 没有资源文件可用于补全。")
            skipped_count += 1
            continue

        # 默认拿第一篇资源来生成学习路径
        resource_name = resources[0]
        resource_data = load_resource_file(resource_name)

        if resource_data is None:
            print(f"[跳过] {topic} 的资源文件不存在：{resource_name}")
            skipped_count += 1
            continue

        content = resource_data["content"]
        category = resource_data["category"] or "其他"

        if not content.strip():
            print(f"[跳过] {topic} 的资源内容为空：{resource_name}")
            skipped_count += 1
            continue

        print(f"[补全中] {topic} <- {resource_name}")

        try:
            generated = generate_learning_path(topic, category, content)
        except Exception as e:
            print(f"[失败] {topic} 生成学习路径失败：{e}")
            skipped_count += 1
            continue

        knowledge_map[topic]["prerequisites"] = generated.get("prerequisites", [])
        knowledge_map[topic]["steps"] = generated.get("steps", [])

        updated_count += 1
        print(f"[完成] {topic}")

    save_knowledge_map(knowledge_map)

    print()
    print("补全结束。")
    print(f"成功补全：{updated_count}")
    print(f"跳过/未处理：{skipped_count}")


if __name__ == "__main__":
    fill_missing_paths()