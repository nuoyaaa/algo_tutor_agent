from rag.retrieve import retrieve
from openai import OpenAI

client = OpenAI()

MODEL_NAME = "gpt-4.1-mini"


def ask(query):
    contexts = retrieve(query, top_k=3)

    if not contexts:
        return "没有找到相关资料。"

    context_text = "\n\n".join(
        [
            f"来源：{item['source']}\n"
            f"原始链接：{item.get('url', '无')}\n"
            f"retrieval_score：{item['retrieval_score']:.4f}\n"
            f"rerank_score：{item['rerank_score']}\n"
            f"内容：{item['text']}"
            for item in contexts
        ]
    )

    prompt = f"""你是一个数据结构与算法学习助手。
请严格基于给定资料回答用户问题，不要编造资料中没有的信息。
如果资料不足，就明确说“根据当前资料无法完整回答”。

给定资料：
{context_text}

用户问题：
{query}

请输出：
1. 简洁清晰的回答
2. 不要自行编造或补充资料来源，来源会由系统统一附在回答后面
"""

    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt,
    )

    answer = response.output_text

    sources = []
    used = set()
    for item in contexts:
        key = (item["source"], item.get("url"))
        if key in used:
            continue
        used.add(key)
        sources.append(
            f"- {item['source']} | URL: {item.get('url', '无')}"
        )

    source_text = "\n".join(sources)

    return f"{answer}\n\n参考来源：\n{source_text}"