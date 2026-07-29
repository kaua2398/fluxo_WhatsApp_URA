from app.infrastructure.models import NodeModel
from app.infrastructure.repositories.base import BaseRepository


class NodeRepository(BaseRepository[NodeModel]):
    def get_by_id(self, node_id: str) -> NodeModel | None:
        return self.db.query(NodeModel).filter(NodeModel.id == node_id).first()

    def get_by_flow(self, flow_id: str) -> list[NodeModel]:
        return self.db.query(NodeModel).filter(NodeModel.flow_id == flow_id).all()

    def get_by_module(self, flow_id: str, module: str) -> list[NodeModel]:
        return (
            self.db.query(NodeModel)
            .filter(NodeModel.flow_id == flow_id, NodeModel.module == module)
            .all()
        )

    def get_by_external_id(self, flow_id: str, external_id: str) -> NodeModel | None:
        return (
            self.db.query(NodeModel)
            .filter(NodeModel.flow_id == flow_id, NodeModel.external_id == external_id)
            .first()
        )

    def create(self, entity: NodeModel) -> NodeModel:
        self.db.add(entity)
        return entity

    def create_bulk(self, entities: list[NodeModel]) -> list[NodeModel]:
        self.db.add_all(entities)
        self.db.commit()
        for entity in entities:
            self.db.refresh(entity)
        return entities

    def delete(self, node_id: str) -> bool:
        entity = self.get_by_id(node_id)
        if not entity:
            return False
        self.db.delete(entity)
        self.db.commit()
        return True

    def update_position(self, node_id: str, x: float, y: float) -> NodeModel | None:
        entity = self.get_by_id(node_id)
        if not entity:
            return None
        entity.position_x = x
        entity.position_y = y
        self.db.commit()
        self.db.refresh(entity)
        return entity
