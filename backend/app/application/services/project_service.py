from app.application.dto.schemas import ProjectCreate, ProjectResponse, ProjectUpdate
from app.infrastructure.models import ProjectModel
from app.infrastructure.repositories.project_repository import ProjectRepository


class ProjectService:
    def __init__(self, project_repo: ProjectRepository):
        self.project_repo = project_repo

    def get_all(self) -> list[ProjectResponse]:
        projects = self.project_repo.get_all()
        return [self._to_response(p) for p in projects]

    def get_by_id(self, project_id: str) -> ProjectResponse | None:
        project = self.project_repo.get_by_id(project_id)
        return self._to_response(project) if project else None

    def create(self, data: ProjectCreate) -> ProjectResponse:
        project = ProjectModel(name=data.name, description=data.description)
        created = self.project_repo.create(project)
        return self._to_response(created)

    def update(self, project_id: str, data: ProjectUpdate) -> ProjectResponse | None:
        project = self.project_repo.get_by_id(project_id)
        if not project:
            return None
        if data.name is not None:
            project.name = data.name
        if data.description is not None:
            project.description = data.description
        updated = self.project_repo.update(project)
        return self._to_response(updated)

    def delete(self, project_id: str) -> bool:
        return self.project_repo.delete(project_id)

    def _to_response(self, project: ProjectModel) -> ProjectResponse:
        return ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            flow_count=len(project.flows or []),
            created_at=project.created_at,
            updated_at=project.updated_at,
        )
