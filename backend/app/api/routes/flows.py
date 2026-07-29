from fastapi import APIRouter, Depends, HTTPException, Query

from app.application.dto.schemas import (
    ApiResponse,
    ComparisonResponse,
    DocumentationResponse,
    DocumentResponse,
    EdgeResponse,
    ExportResponse,
    FlowDetailResponse,
    ModuleResponse,
    NodeResponse,
    SearchResult,
    VariableResponse,
    VersionResponse,
)
from app.application.services.comparison_service import ComparisonService
from app.application.services.documentation_service import DocumentationService
from app.application.services.export_service import ExportService
from app.application.services.flow_service import FlowService
from app.application.services.module_service import ModuleService
from app.core.dependencies import (
    get_comparison_service,
    get_documentation_service,
    get_export_service,
    get_flow_service,
    get_module_service,
    get_node_repository,
)
from app.infrastructure.repositories.node_repository import NodeRepository

router = APIRouter(tags=["flow-detail"])


@router.get("/flow/{flow_id}", response_model=FlowDetailResponse)
def get_flow_detail(flow_id: str, flow_service: FlowService = Depends(get_flow_service)):
    flow = flow_service.get_flow_detail(flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")

    base = flow_service.to_flow_response(flow)
    return FlowDetailResponse(
        **base.model_dump(),
        nodes=[
            NodeResponse(
                id=n.id,
                external_id=n.external_id,
                label=n.label,
                node_type=n.node_type,
                description=n.description,
                module=n.module,
                position_x=n.position_x,
                position_y=n.position_y,
                metadata=n.metadata_json,
                is_collapsed=n.is_collapsed,
            )
            for n in (flow.nodes or [])
        ],
        edges=[
            EdgeResponse(
                id=e.id,
                source_id=e.source_id,
                target_id=e.target_id,
                label=e.label,
                edge_type=e.edge_type,
                metadata=e.metadata_json,
            )
            for e in (flow.edges or [])
        ],
        apis=[
            ApiResponse(
                id=a.id,
                external_id=a.external_id,
                name=a.name,
                method=a.method,
                url=a.url,
                description=a.description,
                node_ids=a.node_ids,
                metadata=a.metadata_json,
            )
            for a in (flow.apis or [])
        ],
        variables=[
            VariableResponse(
                id=v.id,
                external_id=v.external_id,
                name=v.name,
                description=v.description,
                default_value=v.default_value,
                node_ids=v.node_ids,
                metadata=v.metadata_json,
            )
            for v in (flow.variables or [])
        ],
    )


@router.get("/modules", response_model=list[ModuleResponse])
def get_modules(
    flow_id: str = Query(...),
    module_service: ModuleService = Depends(get_module_service),
):
    return module_service.get_modules(flow_id)


@router.get("/modules/{module_name}/nodes", response_model=list[NodeResponse])
def get_module_nodes(
    module_name: str,
    flow_id: str = Query(...),
    module_service: ModuleService = Depends(get_module_service),
):
    return module_service.get_module_nodes(flow_id, module_name)


@router.get("/flow/{flow_id}/documentation", response_model=DocumentationResponse)
def get_documentation(
    flow_id: str,
    regenerate: bool = Query(False),
    doc_service: DocumentationService = Depends(get_documentation_service),
):
    if regenerate:
        return doc_service.generate_documentation(flow_id)
    docs = doc_service.get_documents(flow_id)
    if not docs:
        return doc_service.generate_documentation(flow_id)
    sections = {d.section: d.content for d in docs}
    return DocumentationResponse(
        flow_id=flow_id,
        summary=sections.get("summary", ""),
        objective=sections.get("objective", ""),
        inputs=sections.get("inputs", ""),
        outputs=sections.get("outputs", ""),
        apis=sections.get("apis", ""),
        variables=sections.get("variables", ""),
        flow_description=sections.get("flow", ""),
        rules=sections.get("rules", ""),
        exceptions=sections.get("exceptions", ""),
    )


@router.get("/flow/{flow_id}/documents", response_model=list[DocumentResponse])
def list_documents(flow_id: str, doc_service: DocumentationService = Depends(get_documentation_service)):
    return doc_service.get_documents(flow_id)


@router.get("/flow/{flow_id}/versions", response_model=list[VersionResponse])
def list_versions(flow_id: str, flow_service: FlowService = Depends(get_flow_service)):
    flow = flow_service.get_flow_detail(flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    return [
        VersionResponse(
            id=v.id,
            flow_id=v.flow_id,
            version_number=v.version_number,
            label=v.label,
            created_at=v.created_at,
        )
        for v in (flow.versions or [])
    ]


@router.get("/flow/{flow_id}/compare", response_model=ComparisonResponse)
def compare_versions(
    flow_id: str,
    version_a: int = Query(...),
    version_b: int = Query(...),
    comparison_service: ComparisonService = Depends(get_comparison_service),
):
    try:
        return comparison_service.compare_versions(flow_id, version_a, version_b)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/export/{format}", response_model=ExportResponse)
def export_flow(
    format: str,
    flow_id: str = Query(...),
    module: str | None = Query(None),
    export_service: ExportService = Depends(get_export_service),
):
    try:
        return export_service.export(flow_id, format, module)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/export/download/{export_id}")
def download_export(export_id: str, export_service: ExportService = Depends(get_export_service)):
    from fastapi.responses import FileResponse

    file_path = export_service.get_export_file(export_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Export not found")
    return FileResponse(path=str(file_path), filename=file_path.name)


@router.get("/search", response_model=list[SearchResult])
def search_flow(
    q: str = Query(..., min_length=1),
    flow_id: str = Query(...),
    flow_service: FlowService = Depends(get_flow_service),
):
    flow = flow_service.get_flow_detail(flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")

    query = q.lower()
    results: list[SearchResult] = []

    for node in flow.nodes or []:
        if query in node.label.lower() or query in node.external_id.lower():
            results.append(
                SearchResult(type="node", id=node.id, label=node.label, module=node.module, flow_id=flow_id)
            )

    for api in flow.apis or []:
        if query in api.name.lower() or (api.url and query in api.url.lower()):
            results.append(SearchResult(type="api", id=api.id, label=api.name, flow_id=flow_id))

    for var in flow.variables or []:
        if query in var.name.lower():
            results.append(SearchResult(type="variable", id=var.id, label=var.name, flow_id=flow_id))

    return results


@router.patch("/nodes/{node_id}/position", response_model=NodeResponse)
def update_node_position(
    node_id: str,
    position_x: float = Query(...),
    position_y: float = Query(...),
    node_repo: NodeRepository = Depends(get_node_repository),
):
    node = node_repo.update_position(node_id, position_x, position_y)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    return NodeResponse(
        id=node.id,
        external_id=node.external_id,
        label=node.label,
        node_type=node.node_type,
        description=node.description,
        module=node.module,
        position_x=node.position_x,
        position_y=node.position_y,
        metadata=node.metadata_json,
        is_collapsed=node.is_collapsed,
    )
