from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.application.dto.schemas import FlowCreate, FlowResponse, ProjectCreate, ProjectResponse, ProjectUpdate, UploadResponse
from app.application.services.flow_service import FlowService
from app.application.services.parse_service import ParseService, UploadService
from app.application.services.project_service import ProjectService
from app.core.dependencies import get_flow_repository, get_flow_service, get_parse_service, get_project_service, get_upload_service
from app.infrastructure.models import FlowModel
from app.infrastructure.repositories.flow_repository import FlowRepository

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectResponse])
def list_projects(service: ProjectService = Depends(get_project_service)):
    return service.get_all()


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, service: ProjectService = Depends(get_project_service)):
    project = service.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(data: ProjectCreate, service: ProjectService = Depends(get_project_service)):
    return service.create(data)


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: str, data: ProjectUpdate, service: ProjectService = Depends(get_project_service)
):
    project = service.update(project_id, data)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: str, service: ProjectService = Depends(get_project_service)):
    if not service.delete(project_id):
        raise HTTPException(status_code=404, detail="Project not found")


flows_router = APIRouter(prefix="/flows", tags=["flows"])


@flows_router.get("", response_model=list[FlowResponse])
def list_flows(
    project_id: str | None = None,
    flow_repo: FlowRepository = Depends(get_flow_repository),
    flow_service: FlowService = Depends(get_flow_service),
):
    if project_id:
        flows = flow_repo.get_by_project(project_id)
    else:
        flows = []
    return [flow_service.to_flow_response(f) for f in flows]


@flows_router.get("/{flow_id}", response_model=FlowResponse)
def get_flow(flow_id: str, flow_service: FlowService = Depends(get_flow_service)):
    flow = flow_service.get_flow_detail(flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    return flow_service.to_flow_response(flow)


@flows_router.post("", response_model=FlowResponse, status_code=201)
def create_flow(
    data: FlowCreate,
    flow_repo: FlowRepository = Depends(get_flow_repository),
    flow_service: FlowService = Depends(get_flow_service),
):
    flow = FlowModel(
        project_id=data.project_id,
        name=data.name,
        flow_type=data.flow_type,
        description=data.description,
    )
    created = flow_repo.create(flow)
    return flow_service.to_flow_response(created)


@flows_router.delete("/{flow_id}", status_code=204)
def delete_flow(flow_id: str, flow_repo: FlowRepository = Depends(get_flow_repository)):
    if not flow_repo.delete(flow_id):
        raise HTTPException(status_code=404, detail="Flow not found")


upload_router = APIRouter(tags=["upload"])


@upload_router.post("/upload", response_model=UploadResponse)
async def upload_file(
    project_id: str = Form(...),
    flow_type: str = Form("whatsapp"),
    flow_name: str | None = Form(None),
    file: UploadFile = File(...),
    upload_service: UploadService = Depends(get_upload_service),
    flow_repo: FlowRepository = Depends(get_flow_repository),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    try:
        return await upload_service.upload_file(
            flow_repo, project_id, file.filename or "unknown.json", content, flow_type, flow_name
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@upload_router.post("/parse", response_model=UploadResponse)
async def parse_flow(
    flow_id: str = Form(...),
    file: UploadFile = File(...),
    flow_type: str | None = Form(None),
    parse_service: ParseService = Depends(get_parse_service),
):
    content = await file.read()
    try:
        return parse_service.parse_content(flow_id, content, file.filename or "unknown.json", flow_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
