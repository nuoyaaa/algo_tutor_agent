import json
from openai import OpenAI
from rag.embed import get_embedding

client = OpenAI()
MODEL_NAME = "gpt-4.1-mini"
KNOWLEDGE_MAP_PATH = "knowledge_map.json"


def load_topics():
    with open(KNOWLEDGE_MAP_PATH, "r", encoding="utf-8") as f:
        knowledge_map = json.load(f)
    return list(knowledge_map.keys())


def api_match_topic(user_topic: str, topics: list[str]):
    prompt = f"""
你是一个算法学习助手中的知识点对齐模块。

用户输入了一个知识点名称，需要从系统已有的标准 topic 列表中，
选择最匹配的一个 topic。

要求：
1. 只能从给定 topic 列表中选择
2. 如果没有合适匹配，返回 null
3. 优先选择语义最接近、粒度最合适的 topic
4. 如果用户输入本身已经是一个标准 topic，就直接返回它
5. 不要把宽泛概念错误匹配到更具体的子主题，除非用户明确在问那个子主题

用户输入的知识点：
{user_topic}

系统已有 topic 列表：
{topics}

请严格输出 JSON，字段如下：
- matched_topic: 字符串或 null
"""

    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "topic_match",
                "schema": {
                    "type": "object",
                    "properties": {
                        "matched_topic": {
                            "type": ["string", "null"]
                        }
                    },
                    "required": ["matched_topic"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    )

    return json.loads(response.output_text)["matched_topic"]


def match_topic(user_topic: str, threshold: float = 0.5):
    topics = load_topics()
    if not topics:
        return None

    # 1. 完全相等优先
    if user_topic in topics:
        return user_topic

    # 2. 包含匹配：如果只有一个候选，直接返回；如果有多个，交给 API 选
    contains_matches = [topic for topic in topics if user_topic in topic]
    if len(contains_matches) == 1:
        return contains_matches[0]
    elif len(contains_matches) > 1:
        return api_match_topic(user_topic, contains_matches)

    # 3. embedding 粗筛
    user_emb = get_embedding([user_topic])[0]
    topic_embs = get_embedding(topics)

    scored = []
    for topic, emb in zip(topics, topic_embs):
        score = float(user_emb @ emb)
        scored.append((score, topic))

    scored.sort(reverse=True, key=lambda x: x[0])

    if scored[0][0] < threshold:
        return None

    candidate_topics = [topic for _, topic in scored[:5]]
    matched_topic = api_match_topic(user_topic, candidate_topics)
    return matched_topic

