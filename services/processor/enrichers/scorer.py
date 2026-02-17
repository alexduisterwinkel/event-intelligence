def score_article(text: str) -> float:
    length_score = min(len(text) / 500, 1.0)
    keyword_bonus = 0.2 if "market" in text.lower() else 0.0
    return round(min(length_score + keyword_bonus, 1.0), 2)
