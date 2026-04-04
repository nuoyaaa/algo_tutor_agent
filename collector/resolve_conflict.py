import json
from openai import OpenAI

client = OpenAI()
MODEL_NAME = "gpt-4.1-mini"


def resolve_conflict(old_source: str, old_text: str, new_url: str, new_text: str):
    prompt = f"""
你是一个数据结构与算法学习资料质量仲裁助手。

现在有两份内容高度相似的资料，需要二选一保留到知识库中。
请从以下角度比较它们：
1. 哪一份知识讲解更清晰
2. 哪一份内容更完整、更系统
3. 哪一份更适合作为学习资料长期保留
4. 哪一份例子或解释更有帮助

旧资料来源：
{old_source}

旧资料内容：
{old_text[:3500]}

新资料来源：
{new_url}

新资料内容：
{new_text[:3500]}

请严格输出 JSON，字段如下：
- winner: 字符串，只能是 ["old", "new"] 之一
- reason: 一句话说明原因
"""

    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "conflict_resolution",
                "schema": {
                    "type": "object",
                    "properties": {
                        "winner": {
                            "type": "string",
                            "enum": ["old", "new"]
                        },
                        "reason": {"type": "string"}
                    },
                    "required": ["winner", "reason"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    )

    return json.loads(response.output_text)


if __name__ == "__main__":
    old_source = "dp_definition.md"
    old_text = """
# 动态规划定义

动态规划是一种通过将原问题分解为子问题，并保存子问题答案来避免重复计算的方法。
"""

    new_url = "https://example.com/dp"
    new_text = """
# 动态规划基础

动态规划是一种求解多阶段最优化问题的方法，其核心在于把问题拆成重叠子问题并保存子问题结果，避免重复计算。
"""

    result = resolve_conflict(old_source, old_text, new_url, new_text)
    print(result)