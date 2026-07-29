from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.services.comparison_service import ComparisonService
from app.application.services.documentation_service import DocumentationService
from app.application.services.export_service import ExportService
from app.application.services.flow_service import FlowService
from app.application.services.module_service import ModuleService
from app.application.services.parse_service import ParseService
from app.application.services.project_service import ProjectService
from app.application.services.upload_service import UploadService
from app.core.database import get_db
from app.infrastructure.repositories.api_repository import ApiRepository
from app.infrastructure.repositories.document_repository import DocumentRepository
from app.infrastructure.repositories.edge_repository import EdgeRepository
from app.infrastructure.repositories.export_repository import ExportRepository
from app.infrastructure.repositories.flow_repository import FlowRepository
from app.infrastructure.repositories.node_repository import NodeRepository
from app.infrastructure.repositories.project_repository import ProjectRepository
from app.infrastructure.repositories.variable_repository import VariableRepository
from app.infrastructure.repositories.version_repository import VersionRepository


def get_project_repository(db: Session = Depends(get_db)) -> ProjectRepository:
    return ProjectRepository(db)


def get_flow_repository(db: Session = Depends(get_db)) -> FlowRepository:
    return FlowRepository(db)


def get_node_repository(db: Session = Depends(get_db)) -> NodeRepository:
    return NodeRepository(db)


def get_edge_repository(db: Session = Depends(get_db)) -> EdgeRepository:
    return EdgeRepository(db)


def get_api_repository(db: Session = Depends(get_db)) -> ApiRepository:
    return ApiRepository(db)


def get_variable_repository(db: Session = Depends(get_db)) -> VariableRepository:
    return VariableRepository(db)


def get_version_repository(db: Session = Depends(get_db)) -> VersionRepository:
    return VersionRepository(db)


def get_document_repository(db: Session = Depends(get_db)) -> DocumentRepository:
    return DocumentRepository(db)


def get_export_repository(db: Session = Depends(get_db)) -> ExportRepository:
    return ExportRepository(db)


def get_project_service(
    repo: ProjectRepository = Depends(get_project_repository),
) -> ProjectService:
    return ProjectService(repo)


def get_flow_service(
    flow_repo: FlowRepository = Depends(get_flow_repository),
    node_repo: NodeRepository = Depends(get_node_repository),
    edge_repo: EdgeRepository = Depends(get_edge_repository),
    api_repo: ApiRepository = Depends(get_api_repository),
    variable_repo: VariableRepository = Depends(get_variable_repository),
    version_repo: VersionRepository = Depends(get_version_repository),
) -> FlowService:
    return FlowService(flow_repo, node_repo, edge_repo, api_repo, variable_repo, version_repo)


def get_parse_service(
    flow_service: FlowService = Depends(get_flow_service),
) -> ParseService:
    return ParseService(flow_service)


def get_upload_service(
    parse_service: ParseService = Depends(get_parse_service),
) -> UploadService:
    return UploadService(parse_service)


def get_module_service(
    flow_repo: FlowRepository = Depends(get_flow_repository),
    node_repo: NodeRepository = Depends(get_node_repository),
) -> ModuleService:
    return ModuleService(flow_repo, node_repo)


def get_documentation_service(
    flow_repo: FlowRepository = Depends(get_flow_repository),
    node_repo: NodeRepository = Depends(get_node_repository),
    api_repo: ApiRepository = Depends(get_api_repository),
    variable_repo: VariableRepository = Depends(get_variable_repository),
    document_repo: DocumentRepository = Depends(get_document_repository),
) -> DocumentationService:
    return DocumentationService(flow_repo, node_repo, api_repo, variable_repo, document_repo)


def get_export_service(
    flow_repo: FlowRepository = Depends(get_flow_repository),
    node_repo: NodeRepository = Depends(get_node_repository),
    edge_repo: EdgeRepository = Depends(get_edge_repository),
    export_repo: ExportRepository = Depends(get_export_repository),
    doc_service: DocumentationService = Depends(get_documentation_service),
) -> ExportService:
    return ExportService(flow_repo, node_repo, edge_repo, export_repo, doc_service)


def get_comparison_service(
    flow_repo: FlowRepository = Depends(get_flow_repository),
    node_repo: NodeRepository = Depends(get_node_repository),
    edge_repo: EdgeRepository = Depends(get_edge_repository),
    version_repo: VersionRepository = Depends(get_version_repository),
) -> ComparisonService:
    return ComparisonService(flow_repo, node_repo, edge_repo, version_repo)
