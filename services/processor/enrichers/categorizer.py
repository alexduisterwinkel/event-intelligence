CATEGORIES = {
    "finance": ["market", "stock", "investment", "economy"],
    "technology": ["ai", "software", "github", "tech"],
    "politics": ["government", "election", "policy"],
}


def categorize(text: str) -> str:
    text_lower = text.lower()

    for category, keywords in CATEGORIES.items():
        if any(keyword in text_lower for keyword in keywords):
            return category

    return "general"
