from pathlib import Path

from app.application.dto.schemas import FlowCreate, FlowResponse, UploadResponse
from app.application.services.flow_service import FlowService
from app.core.config import get_settings
from app.infrastructure.models import FlowModel
from app.infrastructure.repositories.flow_repository import FlowRepository
from app.parsers.registry import parser_registry


class ParseService:
    def __init__(self, flow_service: FlowService):
        self.flow_service = flow_service

    def parse_content(
        self, flow_id: str, content: bytes | str, filename: str, flow_type: str | None = None
    ) -> UploadResponse:
        parser = parser_registry.get_parser(filename, flow_type=flow_type)
        graph = parser.parse(content, metadata={"filename": filename, "flow_type": flow_type})

        flow = self.flow_service.save_parsed_graph(flow_id, graph)
        source_type = parser_registry.detect_source_type(filename, flow_type)

        flow.source_type = source_type
        flow.source_file = filename

        return UploadResponse(
            flow_id=flow_id,
            filename=filename,
            source_type=source_type,
            node_count=len(graph.nodes),
            edge_count=len(graph.edges),
            module_count=len(graph.modules),
            version_number=len(flow.versions or []),
        )


class UploadService:
    def __init__(self, parse_service: ParseService):
        self.parse_service = parse_service
        self.settings = get_settings()

    async def upload_file(
        self,
        flow_repo: FlowRepository,
        project_id: str,
        filename: str,
        content: bytes,
        flow_type: str = "whatsapp",
        flow_name: str | None = None,
    ) -> UploadResponse:
        self.settings.ensure_directories()

        flow = FlowModel(
            project_id=project_id,
            name=flow_name or Path(filename).stem,
            flow_type=flow_type,
            source_file=filename,
        )
        created_flow = flow_repo.create(flow)

        file_path = self.settings.upload_dir / f"{created_flow.id}_{filename}"
        file_path.write_bytes(content)

        return self.parse_service.parse_content(created_flow.id, content, filename, flow_type)

