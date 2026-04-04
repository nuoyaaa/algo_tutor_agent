import json
from openai import OpenAI

client = OpenAI()
MODEL_NAME = "gpt-4.1-mini"


def generate_parent(topic: str, existing_topics: list[str]):
    prompt = f"""
你是一个数据结构与算法知识图谱组织助手。

现在系统中新增了一个知识点 topic，需要判断它是否应该挂到某个已有 topic 下面，作为它的子主题。

新 topic：
{topic}

已有 topic 列表：
{existing_topics}

请根据知识点之间的语义关系做判断，要求：
1. 如果新 topic 明显是某个已有 topic 的更细粒度子主题，就返回那个 topic 作为 parent
2. 如果没有合适的父主题，就返回 null
3. parent 只能从已有 topic 列表中选择，不能编造新值

请严格输出 JSON，字段如下：
- parent: 字符串或 null
"""

    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "parent_generation",
                "schema": {
                    "type": "object",
                    "properties": {
                        "parent": {
                            "type": ["string", "null"]
                        }
                    },
                    "required": ["parent"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    )

    return json.loads(response.output_text)


if __name__ == "__main__":
    topic = "动态规划-完全背包问题"
    existing_topics = [
        "动态规划",
        "动态规划与背包问题",
        "动态规划-记忆化搜索"
    ]
    result = generate_parent(topic, existing_topics)
    print(result)