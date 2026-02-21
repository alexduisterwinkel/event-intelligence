def compute_trend_score(
        importance: float,
        category_confidence: float,
        keyword_burst: float,
) -> float:
    """
    Weighted composite intelligence score.
    """

    w_importance = 0.4
    w_confidence = 0.3
    w_burst = 0.3

    score = (
            importance * w_importance
            + category_confidence * w_confidence
            + min(keyword_burst, 5.0) / 5.0 * w_burst
    )

    return round(score, 4)
