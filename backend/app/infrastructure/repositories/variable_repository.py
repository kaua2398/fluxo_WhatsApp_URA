from app.infrastructure.models import VariableModel
from app.infrastructure.repositories.base import BaseRepository


class VariableRepository(BaseRepository[VariableModel]):
    def get_by_id(self, variable_id: str) -> VariableModel | None:
        return self.db.query(VariableModel).filter(VariableModel.id == variable_id).first()

    def get_by_flow(self, flow_id: str) -> list[VariableModel]:
        return self.db.query(VariableModel).filter(VariableModel.flow_id == flow_id).all()

    def get_by_name(self, flow_id: str, name: str) -> VariableModel | None:
        return (
            self.db.query(VariableModel)
            .filter(VariableModel.flow_id == flow_id, VariableModel.name == name)
            .first()
        )

    def create(self, entity: VariableModel) -> VariableModel:
        self.db.add(entity)
        return entity

    def create_bulk(self, entities: list[VariableModel]) -> list[VariableModel]:
        self.db.add_all(entities)
        self.db.commit()
        for entity in entities:
            self.db.refresh(entity)
        return entities

    def delete(self, variable_id: str) -> bool:
        entity = self.get_by_id(variable_id)
        if not entity:
            return False
        self.db.delete(entity)
        self.db.commit()
        return True
