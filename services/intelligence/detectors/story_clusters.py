import uuid
from typing import Dict, Set


class StoryClusterStore:
    """
    Groups related articles into evolving stories.
    """

    def __init__(self, overlap_threshold: int = 2):
        self.overlap_threshold = overlap_threshold
        self.clusters: Dict[str, Set[str]] = {}

    def assign_story(self, keywords: list[str]) -> str:
        kw_set = set(keywords)

        for story_id, existing_keywords in self.clusters.items():
            overlap = len(kw_set & existing_keywords)

            if overlap >= self.overlap_threshold:
                existing_keywords.update(kw_set)
                return story_id

        story_id = str(uuid.uuid4())
        self.clusters[story_id] = set(keywords)
        return story_id
