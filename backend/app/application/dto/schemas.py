from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str | None
    flow_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FlowCreate(BaseModel):
    project_id: str
    name: str = Field(..., min_length=1, max_length=255)
    flow_type: str = "whatsapp"
    description: str | None = None


class FlowResponse(BaseModel):
    id: str
    project_id: str
    name: str
    flow_type: str
    description: str | None
    source_type: str | None
    source_file: str | None
    is_active: bool
    node_count: int = 0
    api_count: int = 0
    decision_count: int = 0
    version_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NodeResponse(BaseModel):
    id: str
    external_id: str
    label: str
    node_type: str
    description: str | None
    module: str | None
    position_x: float
    position_y: float
    metadata: dict[str, Any] | None = None
    is_collapsed: bool = False

    model_config = {"from_attributes": True}


class EdgeResponse(BaseModel):
    id: str
    source_id: str
    target_id: str
    label: str | None
    edge_type: str
    metadata: dict[str, Any] | None = None

    model_config = {"from_attributes": True}


class ApiResponse(BaseModel):
    id: str
    external_id: str
    name: str
    method: str
    url: str | None
    description: str | None
    node_ids: list[str] | None = None
    metadata: dict[str, Any] | None = None

    model_config = {"from_attributes": True}


class VariableResponse(BaseModel):
    id: str
    external_id: str
    name: str
    description: str | None
    default_value: str | None
    node_ids: list[str] | None = None
    metadata: dict[str, Any] | None = None

    model_config = {"from_attributes": True}


class ModuleResponse(BaseModel):
    id: str
    name: str
    description: str
    node_count: int
    api_count: int
    decision_count: int
    nodes: list[NodeResponse] = []


class FlowDetailResponse(FlowResponse):
    nodes: list[NodeResponse] = []
    edges: list[EdgeResponse] = []
    apis: list[ApiResponse] = []
    variables: list[VariableResponse] = []


class VersionResponse(BaseModel):
    id: str
    flow_id: str
    version_number: int
    label: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentResponse(BaseModel):
    id: str
    flow_id: str
    section: str
    content: str
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentationResponse(BaseModel):
    flow_id: str
    summary: str
    objective: str
    inputs: str
    outputs: str
    apis: str
    variables: str
    flow_description: str
    rules: str
    exceptions: str


class UploadResponse(BaseModel):
    flow_id: str
    filename: str
    source_type: str
    node_count: int
    edge_count: int
    module_count: int
    version_number: int


class ParseRequest(BaseModel):
    flow_id: str
    content: str | None = None


class ComparisonResponse(BaseModel):
    flow_id: str
    version_a: int
    version_b: int
    added_nodes: list[dict[str, Any]]
    removed_nodes: list[dict[str, Any]]
    changed_nodes: list[dict[str, Any]]
    added_edges: list[dict[str, Any]]
    removed_edges: list[dict[str, Any]]


class ExportResponse(BaseModel):
    id: str
    flow_id: str
    format: str
    file_path: str
    download_url: str
    created_at: datetime

    model_config = {"from_attributes": True}


class NodePositionUpdate(BaseModel):
    position_x: float
    position_y: float


class SearchResult(BaseModel):
    type: str
    id: str
    label: str
    module: str | None = None
    flow_id: str | None = None
