from rag.qa import ask
from rag.pathway import recommend_path, get_children
from rag.classifier import classify_query
from rag.topic_matcher import match_topic
from rag.next_topic import recommend_next_topics
from rag.next_topic_reason import generate_next_topic_reasons


def print_learning_path(topic: str):
    path_result = recommend_path(topic)

    if path_result is None:
        print(f"\n未找到知识点「{topic}」的学习路径。\n")
        return

    children = get_children(topic)

    print(f"\n知识点：{path_result['topic']}")
    print(f"父主题：{path_result['parent'] if path_result['parent'] else '无'}")

    print("前置知识：")
    if path_result["prerequisites"]:
        for item in path_result["prerequisites"]:
            print(f"- {item}")
    else:
        print("- 无")

    print("学习步骤：")
    if path_result["steps"]:
        for i, step in enumerate(path_result["steps"], start=1):
            print(f"{i}. {step}")
    else:
        print("- 无")

    print("推荐资料：")
    if path_result["resources"]:
        for resource in path_result["resources"]:
            print(f"- {resource}")
    else:
        print("- 无")

    print("子主题：")
    if children:
        for child in children:
            print(f"- {child}")
    else:
        print("- 无")

    print()


def print_next_topics(topic: str):
    results = recommend_next_topics(topic)

    if results is None:
        print(f"\n未找到知识点「{topic}」，无法推荐下一个知识点。\n")
        return

    print(f"\n当前知识点：{topic}")
    print("推荐继续学习：")

    if not results:
        print("- 当前没有更细的子主题可推荐。")
        print()
        return

    candidate_topics = [item["topic"] for item in results]
    reason_result = generate_next_topic_reasons(topic, candidate_topics)

    reason_map = {}
    for item in reason_result.get("reasons", []):
        reason_map[item["topic"]] = item["reason"]

    for i, item in enumerate(results, start=1):
        topic_name = item["topic"]
        reason = reason_map.get(topic_name, "适合继续深入学习该方向。")
        print(f"{i}. {topic_name}：{reason}")

    print()


if __name__ == "__main__":
    while True:
        query = input("请输入问题：").strip()

        if query.lower() in {"exit", "quit", "q"}:
            print("已退出。")
            break

        result = classify_query(query)

        if result["intent"] in {"path", "next_topic"}:
            topic = result["topic"]

            if not topic:
                print("\n我识别到你在询问学习相关内容，但没有明确识别出知识点。\n")
                continue

            matched_topic = match_topic(topic)
            if matched_topic is not None:
                topic = matched_topic

            if result["intent"] == "path":
                print_learning_path(topic)
            else:
                print_next_topics(topic)

        else:
            answer = ask(query)
            print("\n回答：", answer)
            print()