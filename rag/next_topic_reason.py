import json
from openai import OpenAI

client = OpenAI()
MODEL_NAME = "gpt-4.1-mini"
KNOWLEDGE_MAP_PATH = "knowledge_map.json"


def load_knowledge_map():
    with open(KNOWLEDGE_MAP_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_next_topic_reasons(current_topic: str, candidate_topics: list[str]):
    knowledge_map = load_knowledge_map()

    candidate_info = []
    for topic in candidate_topics:
        info = knowledge_map.get(topic, {})
        candidate_info.append({
            "topic": topic,
            "prerequisites": info.get("prerequisites", []),
            "steps": info.get("steps", []),
            "resource_count": len(info.get("resources", []))
        })

    prompt = f"""
你是一个算法学习助手中的学习建议生成模块。

当前用户正在学习的知识点：
{current_topic}

系统推荐的下一步候选知识点如下：
{candidate_info}

请为每个候选知识点生成一句简洁的推荐理由，要求：
1. 理由要贴合该知识点的学习价值
2. 理由要简洁自然，适合直接展示给用户
3. 不要重复空话，不要泛泛而谈
4. 每个 topic 对应一句 reason

请严格输出 JSON，字段如下：
- reasons: 数组，每个元素包含：
  - topic: 字符串
  - reason: 字符串
"""

    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "next_topic_reasons",
                "schema": {
                    "type": "object",
                    "properties": {
                        "reasons": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "topic": {"type": "string"},
                                    "reason": {"type": "string"}
                                },
                                "required": ["topic", "reason"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["reasons"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    )

    return json.loads(response.output_text)


if __name__ == "__main__":
    current_topic = "动态规划"
    candidate_topics = [
        "动态规划-双串线性DP",
        "动态规划-完全背包问题",
        "动态规划-记忆化搜索"
    ]
    result = generate_next_topic_reasons(current_topic, candidate_topics)
    print(result)