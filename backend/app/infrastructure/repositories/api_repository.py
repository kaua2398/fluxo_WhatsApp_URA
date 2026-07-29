from app.infrastructure.models import ApiModel
from app.infrastructure.repositories.base import BaseRepository


class ApiRepository(BaseRepository[ApiModel]):
    def get_by_id(self, api_id: str) -> ApiModel | None:
        return self.db.query(ApiModel).filter(ApiModel.id == api_id).first()

    def get_by_flow(self, flow_id: str) -> list[ApiModel]:
        return self.db.query(ApiModel).filter(ApiModel.flow_id == flow_id).all()

    def create(self, entity: ApiModel) -> ApiModel:
        self.db.add(entity)
        return entity

    def create_bulk(self, entities: list[ApiModel]) -> list[ApiModel]:
        self.db.add_all(entities)
        self.db.commit()
        for entity in entities:
            self.db.refresh(entity)
        return entities

    def delete(self, api_id: str) -> bool:
        entity = self.get_by_id(api_id)
        if not entity:
            return False
        self.db.delete(entity)
        self.db.commit()
        return True
