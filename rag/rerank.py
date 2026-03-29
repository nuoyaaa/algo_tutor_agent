def rerank(query, candidates):
    query_words = set(query.split())
    intent_words = {"例子", "定义", "原理", "解释", "区别"}

    query_intent_words = query_words & intent_words
    scored_candidates = []

    for candidate in candidates:
        score = 0
        text = candidate["text"]

        matched_intent = False

        for word in query_words:
            if word in text:
                if word in intent_words:
                    score += 4
                    matched_intent = True
                else:
                    score += 1

        if query_intent_words and not matched_intent:
            score -= 2

        candidate["rerank_score"] = score
        scored_candidates.append(candidate)

    scored_candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
    return scored_candidates