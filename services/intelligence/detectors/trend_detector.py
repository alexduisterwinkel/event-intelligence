from collections import defaultdict, deque
from datetime import datetime, timedelta
import math


class TrendDetector:
    """
    Real-time trend detector using:

    - sliding time window
    - exponential time decay
    - burst detection
    """

    def __init__(
            self,
            window_seconds: int = 60,
            threshold: float = 5.0,
            decay_half_life: float = 30.0,
            burst_weight: float = 1.5,
    ):
        self.window = timedelta(seconds=window_seconds)
        self.threshold = threshold
        self.decay_half_life = decay_half_life
        self.burst_weight = burst_weight

        # category -> deque[timestamps]
        self.events = defaultdict(deque)

        # category -> last computed score (for burst detection)
        self.last_score = defaultdict(float)

    # ------------------------------

    def _decay_weight(self, age_seconds: float) -> float:
        """Exponential time decay."""
        return math.exp(-math.log(2) * age_seconds / self.decay_half_life)

    # ------------------------------

    def _prune_old(self, category: str, now: datetime):
        cutoff = now - self.window
        dq = self.events[category]

        while dq and dq[0] < cutoff:
            dq.popleft()

    # ------------------------------

    def _compute_score(self, category: str, now: datetime) -> float:
        dq = self.events[category]

        weighted_sum = 0.0

        for ts in dq:
            age = (now - ts).total_seconds()
            weighted_sum += self._decay_weight(age)

        # burst detection (rate of change)
        previous = self.last_score[category]
        burst = max(0.0, weighted_sum - previous)

        score = weighted_sum + self.burst_weight * burst

        self.last_score[category] = weighted_sum

        return score

    # ------------------------------

    def add_event(self, category: str, timestamp: datetime) -> tuple[bool, float]:
        """
        Returns:
            (trend_detected, score)
        """
        now = timestamp

        self.events[category].append(now)
        self._prune_old(category, now)

        score = self._compute_score(category, now)

        return score >= self.threshold, score
