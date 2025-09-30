from abc import ABC, abstractmethod
from typing import List, Dict, Any


class BaseFetcher(ABC):
    """
    Abstract base class for all feed fetchers (RSS, REST, YouTube, Twitter, etc.)
    Each fetcher must return normalized items as dictionaries.
    """

    def __init__(self, source):
        self.source = source
        self.endpoint = source.endpoint
        self.config = source.config or {}

    @abstractmethod
    def fetch(self) -> List[Dict[str, Any]]:
        """
        Fetches items from the source.

        Must return a list of dicts with keys:
        - external_id
        - title
        - summary
        - content
        - url
        - author
        - published_at (datetime or None)
        - raw (original payload for debugging)
        """
        pass
