from app.infrastructure.models import ExportModel
from app.infrastructure.repositories.base import BaseRepository


class ExportRepository(BaseRepository[ExportModel]):
    def get_by_id(self, export_id: str) -> ExportModel | None:
        return self.db.query(ExportModel).filter(ExportModel.id == export_id).first()

    def get_by_flow(self, flow_id: str) -> list[ExportModel]:
        return (
            self.db.query(ExportModel)
            .filter(ExportModel.flow_id == flow_id)
            .order_by(ExportModel.created_at.desc())
            .all()
        )

    def create(self, entity: ExportModel) -> ExportModel:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, export_id: str) -> bool:
        entity = self.get_by_id(export_id)
        if not entity:
            return False
        self.db.delete(entity)
        self.db.commit()
        return True
