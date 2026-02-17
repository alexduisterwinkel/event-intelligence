from collections import defaultdict, deque
from datetime import datetime, timedelta


class TrendDetector:

    def __init__(self, window_seconds: int = 60, threshold: int = 3):
        self.window = timedelta(seconds=window_seconds)
        self.threshold = threshold
        self.events = defaultdict(deque)

    def add_event(self, category: str, timestamp: datetime):
        now = timestamp

        queue = self.events[category]
        queue.append(now)

        # Remove old events
        while queue and (now - queue[0]) > self.window:
            queue.popleft()

        return len(queue) >= self.threshold
