import json
from openai import OpenAI

client = OpenAI()
MODEL_NAME = "gpt-4.1-mini"


def generate_learning_path(topic: str, category: str, content: str):
    prompt = f"""
你是一个数据结构与算法学习规划助手。

现在有一个新的知识点资料被纳入知识库，请你为这个知识点生成学习路径信息。

知识点主题：
{topic}

资料类别：
{category}

资料内容：
{content[:4000]}

请结合资料内容，生成：
1. 学习这个知识点前建议掌握的前置知识
2. 推荐的学习步骤顺序

要求：
- prerequisites 输出 1~5 条，尽量简洁，是真正需要的前置知识
- steps 输出 3~6 条，体现由浅入深的学习顺序
- 不要输出空泛套话
- 输出必须严格是 JSON

JSON 字段：
- prerequisites: 字符串列表
- steps: 字符串列表
"""

    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "learning_path",
                "schema": {
                    "type": "object",
                    "properties": {
                        "prerequisites": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "steps": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["prerequisites", "steps"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    )

    return json.loads(response.output_text)


if __name__ == "__main__":
    topic = "动态规划与背包问题"
    category = "题解"
    content = """
    0-1 背包问题是动态规划中的经典问题。需要理解状态表示、状态转移方程以及二维到一维优化。
    """
    result = generate_learning_path(topic, category, content)
    print(result)