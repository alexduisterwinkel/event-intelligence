import random
from datetime import datetime


class MockNewsSource:

    async def fetch(self):
        return [
            {
                "title": f"Market shifts {random.randint(1,100)}%",
                "content": "Synthetic news event for testing.",
                "published_at": datetime.utcnow().isoformat(),
            }
        ]
