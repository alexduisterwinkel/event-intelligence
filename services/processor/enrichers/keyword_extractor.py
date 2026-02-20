from collections import Counter
from typing import List

from core.utils.normalize import normalize_text

STOPWORDS = {
    "the", "a", "an", "and", "or", "is", "are", "to", "of", "in", "for"
}


def extract_keywords(text: str, top_k: int = 5) -> List[str]:
    text = normalize_text(text)
    tokens = text.split()

    filtered = [
        t for t in tokens
        if len(t) > 3 and t not in STOPWORDS
    ]

    counts = Counter(filtered)
    return [word for word, _ in counts.most_common(top_k)]
