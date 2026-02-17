import re
from collections import Counter


def extract_keywords(text: str, limit: int = 5):
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    most_common = Counter(words).most_common(limit)
    return [word for word, _ in most_common]
