from sqlalchemy.orm import Session, joinedload

from app.infrastructure.models import FlowModel, ProjectModel
from app.infrastructure.repositories.base import BaseRepository


class ProjectRepository(BaseRepository[ProjectModel]):
    def get_by_id(self, project_id: str) -> ProjectModel | None:
        return (
            self.db.query(ProjectModel)
            .options(joinedload(ProjectModel.flows))
            .filter(ProjectModel.id == project_id)
            .first()
        )

    def get_all(self) -> list[ProjectModel]:
        return (
            self.db.query(ProjectModel)
            .options(joinedload(ProjectModel.flows))
            .order_by(ProjectModel.name)
            .all()
        )

    def create(self, entity: ProjectModel) -> ProjectModel:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def update(self, entity: ProjectModel) -> ProjectModel:
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, project_id: str) -> bool:
        entity = self.get_by_id(project_id)
        if not entity:
            return False
        self.db.delete(entity)
        self.db.commit()
        return True
