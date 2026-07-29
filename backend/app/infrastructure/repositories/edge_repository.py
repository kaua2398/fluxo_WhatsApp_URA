from app.infrastructure.models import EdgeModel
from app.infrastructure.repositories.base import BaseRepository


class EdgeRepository(BaseRepository[EdgeModel]):
    def get_by_id(self, edge_id: str) -> EdgeModel | None:
        return self.db.query(EdgeModel).filter(EdgeModel.id == edge_id).first()

    def get_by_flow(self, flow_id: str) -> list[EdgeModel]:
        return self.db.query(EdgeModel).filter(EdgeModel.flow_id == flow_id).all()

    def create(self, entity: EdgeModel) -> EdgeModel:
        self.db.add(entity)
        return entity

    def create_bulk(self, entities: list[EdgeModel]) -> list[EdgeModel]:
        self.db.add_all(entities)
        self.db.commit()
        for entity in entities:
            self.db.refresh(entity)
        return entities

    def delete(self, edge_id: str) -> bool:
        entity = self.get_by_id(edge_id)
        if not entity:
            return False
        self.db.delete(entity)
        self.db.commit()
        return True
