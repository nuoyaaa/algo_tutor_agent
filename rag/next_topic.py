import json

KNOWLEDGE_MAP_PATH = "knowledge_map.json"


def load_knowledge_map():
    with open(KNOWLEDGE_MAP_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def recommend_next_topics(topic: str, top_k: int = 3):
    knowledge_map = load_knowledge_map()

    if topic not in knowledge_map:
        return None

    # 先找子主题
    children = []
    for name, info in knowledge_map.items():
        if info.get("parent") == topic:
            children.append({
                "topic": name,
                "resource_count": len(info.get("resources", [])),
                "has_path": bool(info.get("prerequisites")) and bool(info.get("steps"))
            })

    # 排序规则：
    # 1. 有完整学习路径的优先
    # 2. 资源数更多的优先
    # 3. 名称字典序兜底
    children.sort(
        key=lambda x: (
            not x["has_path"],
            -x["resource_count"],
            x["topic"]
        )
    )

    return children[:top_k]


if __name__ == "__main__":
    tests = [
        "动态规划",
        "动态规划与背包问题",
        "动态规划-完全背包问题"
    ]

    for t in tests:
        print(t, "->", recommend_next_topics(t))