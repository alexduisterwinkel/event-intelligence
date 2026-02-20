from collections import defaultdict, deque
from datetime import datetime, timedelta
import math


class AnomalyDetector:
    """
    Streaming z-score anomaly detector per category.

    Detects sudden spikes in event frequency.
    """

    def __init__(
            self,
            window_seconds: int = 120,
            anomaly_threshold: float = 2.5,
            min_samples: int = 5,
    ):
        self.window = timedelta(seconds=window_seconds)
        self.threshold = anomaly_threshold
        self.min_samples = min_samples

        # category -> deque[timestamps]
        self.events = defaultdict(deque)

    # ------------------------------

    def _prune_old(self, category: str, now: datetime):
        cutoff = now - self.window
        dq = self.events[category]

        while dq and dq[0] < cutoff:
            dq.popleft()

    # ------------------------------

    def _compute_rate_series(self, dq: deque, now: datetime):
        """
        Convert timestamps into per-second event counts.
        """
        bucket = defaultdict(int)

        for ts in dq:
            second = int(ts.timestamp())
            bucket[second] += 1

        values = list(bucket.values())
        if not values:
            return []

        return values

    # ------------------------------

    def _zscore(self, values: list[int]) -> float:
        if len(values) < self.min_samples:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        std = math.sqrt(variance)

        if std == 0:
            return 0.0

        latest = values[-1]
        return (latest - mean) / std

    # ------------------------------

    def add_event(self, category: str, timestamp: datetime) -> tuple[bool, float]:
        """
        Returns:
            (is_anomaly, z_score)
        """
        now = timestamp

        self.events[category].append(now)
        self._prune_old(category, now)

        series = self._compute_rate_series(self.events[category], now)
        z = self._zscore(series)

        return z >= self.threshold, z
