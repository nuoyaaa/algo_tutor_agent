import json
from openai import OpenAI

client = OpenAI()
MODEL_NAME = "gpt-4.1-mini"


def evaluate_article(title: str, content: str):
    prompt = f"""
你是一个数据结构与算法学习资料筛选助手。

你的任务是判断下面这篇资料是否适合纳入“算法学习知识库”。

请从以下角度判断：
1. 内容是否适合算法学习
2. 是否具有清晰的知识讲解价值
3. 是否属于某个明确主题
4. 更适合归类为哪种资料类型

其中 topic 的要求如下：
- topic 应尽量具体，不要过于宽泛
- 如果资料主要讲某个算法子主题、变体或经典问题，应输出更细粒度的 topic
- 例如：
  - 不要只输出“动态规划”
  - 如果内容主要围绕背包问题，应输出“动态规划与背包问题”
  - 如果内容主要围绕记忆化搜索，应输出“动态规划-记忆化搜索”
  - 如果内容主要围绕区间 DP，应输出“动态规划-区间DP”

标题：
{title}

正文：
{content[:4000]}

请严格输出 JSON，字段如下：
- keep: 布尔值，是否保留
- category: 字符串，只能是 ["定义", "例子", "区别", "题解", "总结", "其他"] 之一
- topic: 字符串，例如“动态规划”“贪心”“线段树”
- quality_score: 1 到 10 的整数
- reason: 一句话说明原因
"""

    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt,
        text={
            "format": {
                "type": "json_schema",
                "name": "article_eval",
                "schema": {
                    "type": "object",
                    "properties": {
                        "keep": {"type": "boolean"},
                        "category": {
                            "type": "string",
                            "enum": ["定义", "例子", "区别", "题解", "总结", "其他"]
                        },
                        "topic": {"type": "string"},
                        "quality_score": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 10
                        },
                        "reason": {"type": "string"}
                    },
                    "required": ["keep", "category", "topic", "quality_score", "reason"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }
    )

    return json.loads(response.output_text)


if __name__ == "__main__":
    title = "动态规划基础"
    content = """
    动态规划是一种求解多阶段决策过程最优化问题的方法。
    它通过将原问题分解为若干个重叠子问题，并保存子问题的解，避免重复计算。
    斐波那契数列是动态规划的经典例子。
    """
    result = evaluate_article(title, content)
    print(result)