from app.infrastructure.models import DocumentModel
from app.infrastructure.repositories.base import BaseRepository


class DocumentRepository(BaseRepository[DocumentModel]):
    def get_by_id(self, document_id: str) -> DocumentModel | None:
        return self.db.query(DocumentModel).filter(DocumentModel.id == document_id).first()

    def get_by_flow(self, flow_id: str) -> list[DocumentModel]:
        return self.db.query(DocumentModel).filter(DocumentModel.flow_id == flow_id).all()

    def get_by_section(self, flow_id: str, section: str) -> DocumentModel | None:
        return (
            self.db.query(DocumentModel)
            .filter(DocumentModel.flow_id == flow_id, DocumentModel.section == section)
            .first()
        )

    def create(self, entity: DocumentModel) -> DocumentModel:
        self.db.add(entity)
        self.db.commit()
        self.db.refresh(entity)
        return entity

    def upsert(self, flow_id: str, section: str, content: str) -> DocumentModel:
        existing = self.get_by_section(flow_id, section)
        if existing:
            existing.content = content
            self.db.commit()
            self.db.refresh(existing)
            return existing
        entity = DocumentModel(flow_id=flow_id, section=section, content=content)
        return self.create(entity)

    def delete(self, document_id: str) -> bool:
        entity = self.get_by_id(document_id)
        if not entity:
            return False
        self.db.delete(entity)
        self.db.commit()
        return True
