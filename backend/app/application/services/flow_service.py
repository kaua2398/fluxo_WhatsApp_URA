import math
from typing import Any

from app.application.dto.schemas import FlowResponse, ProjectResponse
from app.domain.entities.graph import ParsedGraph
from app.domain.enums.flow_enums import NodeType
from app.infrastructure.models import (
    ApiModel,
    EdgeModel,
    FlowModel,
    NodeModel,
    ProjectModel,
    VariableModel,
    VersionModel,
)
from app.infrastructure.repositories.api_repository import ApiRepository
from app.infrastructure.repositories.edge_repository import EdgeRepository
from app.infrastructure.repositories.flow_repository import FlowRepository
from app.infrastructure.repositories.node_repository import NodeRepository
from app.infrastructure.repositories.variable_repository import VariableRepository
from app.infrastructure.repositories.version_repository import VersionRepository


class FlowService:
    def __init__(
        self,
        flow_repo: FlowRepository,
        node_repo: NodeRepository,
        edge_repo: EdgeRepository,
        api_repo: ApiRepository,
        variable_repo: VariableRepository,
        version_repo: VersionRepository,
    ):
        self.flow_repo = flow_repo
        self.node_repo = node_repo
        self.edge_repo = edge_repo
        self.api_repo = api_repo
        self.variable_repo = variable_repo
        self.version_repo = version_repo

    def save_parsed_graph(self, flow_id: str, graph: ParsedGraph) -> FlowModel:
        flow = self.flow_repo.get_by_id(flow_id)
        if not flow:
            raise ValueError(f"Flow {flow_id} not found")

        self.flow_repo.clear_graph(flow_id)

        external_to_internal: dict[str, str] = {}
        nodes_by_module: dict[str, list[NodeModel]] = {}

        for i, graph_node in enumerate(graph.nodes):
            module = graph_node.module or "Geral"
            if module not in nodes_by_module:
                nodes_by_module[module] = []

            col = len(nodes_by_module[module])
            row = len(nodes_by_module)
            x = graph_node.position_x or (col * 280 + 100)
            y = graph_node.position_y or (row * 180 + 100)

            node = NodeModel(
                flow_id=flow_id,
                external_id=graph_node.external_id,
                label=graph_node.label,
                node_type=graph_node.node_type,
                description=graph_node.description,
                module=module,
                position_x=x,
                position_y=y,
                metadata_json=graph_node.metadata,
            )
            nodes_by_module[module].append(node)

        all_nodes: list[NodeModel] = []
        for module_nodes in nodes_by_module.values():
            all_nodes.extend(module_nodes)

        created_nodes = self.node_repo.create_bulk(all_nodes)
        for node in created_nodes:
            external_to_internal[node.external_id] = node.id

        edges: list[EdgeModel] = []
        for graph_edge in graph.edges:
            source_id = external_to_internal.get(graph_edge.source_id)
            target_id = external_to_internal.get(graph_edge.target_id)
            if source_id and target_id:
                edges.append(
                    EdgeModel(
                        flow_id=flow_id,
                        source_id=source_id,
                        target_id=target_id,
                        label=graph_edge.label,
                        edge_type=graph_edge.edge_type,
                        metadata_json=graph_edge.metadata,
                    )
                )

        if edges:
            self.edge_repo.create_bulk(edges)

        api_entities = [
            ApiModel(
                flow_id=flow_id,
                external_id=api.external_id,
                name=api.name,
                method=api.method,
                url=api.url,
                description=api.description,
                node_ids=[external_to_internal.get(nid, nid) for nid in api.node_ids],
                metadata_json=api.metadata,
            )
            for api in graph.apis
        ]
        if api_entities:
            self.api_repo.create_bulk(api_entities)

        var_entities = [
            VariableModel(
                flow_id=flow_id,
                external_id=var.external_id,
                name=var.name,
                description=var.description,
                default_value=var.default_value,
                node_ids=[external_to_internal.get(nid, nid) for nid in var.node_ids],
                metadata_json=var.metadata,
            )
            for var in graph.variables
        ]
        if var_entities:
            self.variable_repo.create_bulk(var_entities)

        self._create_version_snapshot(flow_id, graph)
        return self.flow_repo.get_by_id(flow_id)  # type: ignore

    def _create_version_snapshot(self, flow_id: str, graph: ParsedGraph) -> VersionModel:
        version_number = self.version_repo.get_latest_version_number(flow_id) + 1
        snapshot = {
            "nodes": [
                {
                    "external_id": n.external_id,
                    "label": n.label,
                    "node_type": n.node_type,
                    "module": n.module,
                    "metadata": n.metadata,
                }
                for n in graph.nodes
            ],
            "edges": [
                {
                    "source_id": e.source_id,
                    "target_id": e.target_id,
                    "label": e.label,
                    "edge_type": e.edge_type,
                }
                for e in graph.edges
            ],
        }
        return self.version_repo.create(
            VersionModel(
                flow_id=flow_id,
                version_number=version_number,
                label=f"v{version_number}",
                snapshot_json=snapshot,
            )
        )

    def to_flow_response(self, flow: FlowModel) -> FlowResponse:
        nodes = flow.nodes or []
        return FlowResponse(
            id=flow.id,
            project_id=flow.project_id,
            name=flow.name,
            flow_type=flow.flow_type,
            description=flow.description,
            source_type=flow.source_type,
            source_file=flow.source_file,
            is_active=flow.is_active,
            node_count=len(nodes),
            api_count=len(flow.apis or []),
            decision_count=sum(1 for n in nodes if n.node_type == NodeType.CONDITION.value),
            version_count=len(flow.versions or []),
            created_at=flow.created_at,
            updated_at=flow.updated_at,
        )

    def get_flow_detail(self, flow_id: str) -> FlowModel | None:
        return self.flow_repo.get_by_id(flow_id)
