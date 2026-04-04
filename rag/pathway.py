import json

KNOWLEDGE_MAP_PATH = "knowledge_map.json"


def load_knowledge_map():
    with open(KNOWLEDGE_MAP_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def recommend_path(topic):
    knowledge_map = load_knowledge_map()

    if topic not in knowledge_map:
        return None

    return {
        "topic": topic,
        "parent": knowledge_map[topic].get("parent"),
        "prerequisites": knowledge_map[topic]["prerequisites"],
        "steps": knowledge_map[topic]["steps"],
        "resources": knowledge_map[topic]["resources"]
    }


def get_children(topic):
    knowledge_map = load_knowledge_map()
    children = []

    for name, info in knowledge_map.items():
        if info.get("parent") == topic:
            children.append(name)

    return children


if __name__ == "__main__":
    result = recommend_path("动态规划")
    print(result)
    print("children:", get_children("动态规划"))