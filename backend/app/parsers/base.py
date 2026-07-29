from abc import ABC, abstractmethod
from typing import Any

from app.domain.entities.graph import ParsedGraph


class BaseParser(ABC):
    @abstractmethod
    def parse(self, content: bytes | str, metadata: dict[str, Any] | None = None) -> ParsedGraph:
        pass

    @abstractmethod
    def can_parse(self, filename: str, content_type: str | None = None) -> bool:
        pass
