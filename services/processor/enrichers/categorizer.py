from typing import Dict, Tuple

from core.utils.normalize import normalize_text

CATEGORIES: Dict[str, list[str]] = {
    "finance": ["market", "stock", "investment", "economy", "inflation", "trading"],
    "technology": ["ai", "software", "github", "tech", "startup", "cloud"],
    "politics": ["government", "election", "policy", "senate", "minister"],
}

CATEGORY_WEIGHTS = {
    "title": 2.0,
    "content": 1.0,
}


def _score_text(text: str, keywords: list[str]) -> int:
    text_norm = normalize_text(text)
    return sum(1 for kw in keywords if kw in text_norm)


def categorize(title: str, content: str) -> Tuple[str, float]:
    """
    Returns (category, confidence_score)
    """
    scores: Dict[str, float] = {}

    for category, keywords in CATEGORIES.items():
        score = (
                _score_text(title, keywords) * CATEGORY_WEIGHTS["title"]
                + _score_text(content, keywords) * CATEGORY_WEIGHTS["content"]
        )
        scores[category] = score

    best_category = max(scores, key=scores.get)
    best_score = scores[best_category]

    if best_score == 0:
        return "general", 0.0

    # simple confidence normalization
    total = sum(scores.values()) or 1
    confidence = best_score / total

    return best_category, round(confidence, 3)
