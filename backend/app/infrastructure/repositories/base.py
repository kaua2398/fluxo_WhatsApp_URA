from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from sqlalchemy.orm import Session

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    def __init__(self, db: Session):
        self.db = db

    @abstractmethod
    def get_by_id(self, entity_id: str) -> T | None:
        pass

    @abstractmethod
    def create(self, entity: T) -> T:
        pass

    @abstractmethod
    def delete(self, entity_id: str) -> bool:
        pass

    def commit(self) -> None:
        self.db.commit()

    def refresh(self, entity: T) -> T:
        self.db.refresh(entity)
        return entity
