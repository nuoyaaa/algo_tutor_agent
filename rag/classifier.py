import json
from openai import OpenAI

client = OpenAI()
MODEL_NAME = "gpt-4.1-mini"


def classify_query(query: str):
    prompt = f"""
你是一个算法学习助手的意图分类器。

请判断下面这条用户输入属于哪一类：

1. qa
表示用户在询问某个知识点、概念、定义、例子、区别、原理、题解等普通问答请求

2. path
表示用户想获取某个知识点的学习路径、学习顺序、学习建议、怎么学、先学什么后学什么等

如果属于 path，请尽量提取出用户想学习的 topic。
如果属于 qa，则 topic 可以为 null。

用户输入：
{query}

请严格输出 JSON，字段如下：
- intent: 只能是 "qa" 或 "path"
- topic: 字符串或 null
"""

    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "intent_classification",
                "schema": {
                    "type": "object",
                    "properties": {
                        "intent": {
                            "type": "string",
                            "enum": ["qa", "path"]
                        },
                        "topic": {
                            "type": ["string", "null"]
                        }
                    },
                    "required": ["intent", "topic"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    )

    return json.loads(response.output_text)


if __name__ == "__main__":
    test_queries = [
        "动态规划 例子",
        "我想系统学动态规划",
        "给我一个动态规划学习路线",
        "动态规划和贪心有什么区别",
        "完全背包问题怎么学"
    ]

    for q in test_queries:
        print(q, "->", classify_query(q))