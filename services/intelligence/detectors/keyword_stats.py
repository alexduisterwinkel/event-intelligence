from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, Deque, Tuple


class KeywordStatsStore:
    """
    Tracks keyword frequency over rolling windows.

    Provides:
    - short window count
    - long window count
    - burst score
    """

    def __init__(
            self,
            short_window_seconds: int = 60,
            long_window_seconds: int = 300,
    ):
        self.short_window = timedelta(seconds=short_window_seconds)
        self.long_window = timedelta(seconds=long_window_seconds)

        self.events: Dict[str, Deque[datetime]] = defaultdict(deque)

    def add_keywords(
            self,
            keywords: list[str],
            timestamp: datetime,
    ) -> Dict[str, Tuple[int, int, float]]:
        """
        Returns per-keyword stats:
        {
            keyword: (short_count, long_count, burst_score)
        }
        """
        results = {}

        for kw in keywords:
            dq = self.events[kw]
            dq.append(timestamp)

            self._evict_old(dq, timestamp)

            short_count = self._count_since(dq, timestamp - self.short_window)
            long_count = self._count_since(dq, timestamp - self.long_window)

            baseline = max(1, long_count)
            burst = short_count / baseline

            results[kw] = (short_count, long_count, burst)

        return results

    def _evict_old(self, dq: Deque[datetime], now: datetime):
        cutoff = now - self.long_window
        while dq and dq[0] < cutoff:
            dq.popleft()

    @staticmethod
    def _count_since(dq: Deque[datetime], cutoff: datetime) -> int:
        return sum(1 for ts in dq if ts >= cutoff)
