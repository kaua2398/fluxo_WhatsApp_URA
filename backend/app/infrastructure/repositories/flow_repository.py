from sqlalchemy.orm import Session, joinedload

from app.infrastructure.models import FlowModel
from app.infrastructure.repositories.base import BaseRepository


class FlowRepository(BaseRepository[FlowModel]):
    def get_by_id(self, flow_id: str) -> FlowModel | None:
        return (
            self.db.query(FlowModel)
            .options(
                joinedload(FlowModel.nodes),
                joinedload(FlowModel.edges),
                joinedload(FlowModel.apis),
                joinedload(FlowModel.variables),
                joinedload(FlowModel.versions),
                joinedload(FlowModel.documents),
            )
            .filter(FlowModel.id == flow_id)
            .first()
        )

    def get_by_project(self, project_id: str) -> list[FlowModel]:
        return (
            self.db.query(FlowModel)
            .filter(FlowModel.project_id == project_id)
            .order_by(FlowModel.name)
            .all()
        )

    def create(self, entity: FlowModel) -> FlowModel:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity: FlowModel) -> FlowModel:
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, flow_id: str) -> bool:
        entity = self.get_by_id(flow_id)
        if not entity:
            return False
        self.db.delete(entity)
        self.db.commit()
        return True

    def clear_graph(self, flow_id: str) -> None:
        flow = self.get_by_id(flow_id)
        if not flow:
            return
        for edge in list(flow.edges):
            self.db.delete(edge)
        for node in list(flow.nodes):
            self.db.delete(node)
        for api in list(flow.apis):
            self.db.delete(api)
        for var in list(flow.variables):
            self.db.delete(var)
        self.db.commit()
