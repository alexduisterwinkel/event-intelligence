import random
from datetime import datetime
from typing import List, Dict

from .base import BaseSource


class MockNewsSource(BaseSource):
    """
    Synthetic news generator for local testing.
    Produces semi-realistic category bursts.
    """

    CATEGORIES = [
        "finance",
        "tech",
        "politics",
        "energy",
        "crypto",
    ]

    async def fetch(self) -> List[Dict]:
        burst = random.random() < 0.25  # occasional burst

        num_items = random.randint(1, 5 if burst else 2)

        items: List[Dict] = []

        for _ in range(num_items):
            category = random.choice(self.CATEGORIES)

            items.append(
                {
                    "title": f"{category.title()} market shifts {random.randint(1,100)}%",
                    "content": f"Synthetic {category} news event for testing.",
                    "category_hint": category,
                    "published_at": datetime.utcnow().isoformat(),
                    "source": "mocknews",
                }
            )

        return items
