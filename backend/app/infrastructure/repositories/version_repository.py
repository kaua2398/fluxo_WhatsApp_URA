from app.infrastructure.models import VersionModel
from app.infrastructure.repositories.base import BaseRepository


class VersionRepository(BaseRepository[VersionModel]):
    def get_by_id(self, version_id: str) -> VersionModel | None:
        return self.db.query(VersionModel).filter(VersionModel.id == version_id).first()

    def get_by_flow(self, flow_id: str) -> list[VersionModel]:
        return (
            self.db.query(VersionModel)
            .filter(VersionModel.flow_id == flow_id)
            .order_by(VersionModel.version_number.desc())
            .all()
        )

    def get_latest_version_number(self, flow_id: str) -> int:
        latest = (
            self.db.query(VersionModel)
            .filter(VersionModel.flow_id == flow_id)
            .order_by(VersionModel.version_number.desc())
            .first()
        )
        return latest.version_number if latest else 0

    def create(self, entity: VersionModel) -> VersionModel:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def delete(self, version_id: str) -> bool:
        entity = self.get_by_id(version_id)
        if not entity:
            return False
        self.db.delete(entity)
        self.db.commit()
        return True
