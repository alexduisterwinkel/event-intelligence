from abc import ABC, abstractmethod
from typing import List, Dict


class BaseSource(ABC):

    @abstractmethod
    async def fetch(self) -> List[Dict]:
        """
        Fetch raw items from external source.
        """
        pass
