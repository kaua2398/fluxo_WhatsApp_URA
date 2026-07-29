from app.application.dto.schemas import ModuleResponse, NodeResponse
from app.domain.enums.flow_enums import NodeType
from app.infrastructure.repositories.flow_repository import FlowRepository
from app.infrastructure.repositories.node_repository import NodeRepository


class ModuleService:
    def __init__(self, flow_repo: FlowRepository, node_repo: NodeRepository):
        self.flow_repo = flow_repo
        self.node_repo = node_repo

    def get_modules(self, flow_id: str) -> list[ModuleResponse]:
        flow = self.flow_repo.get_by_id(flow_id)
        if not flow:
            return []

        modules_map: dict[str, list] = {}
        for node in flow.nodes or []:
            module_name = node.module or "Geral"
            if module_name not in modules_map:
                modules_map[module_name] = []
            modules_map[module_name].append(node)

        modules: list[ModuleResponse] = []
        for name, nodes in sorted(modules_map.items()):
            api_count = sum(1 for n in nodes if n.node_type == NodeType.API.value)
            decision_count = sum(1 for n in nodes if n.node_type == NodeType.CONDITION.value)
            modules.append(
                ModuleResponse(
                    id=f"module_{name.lower().replace(' ', '_')}",
                    name=name,
                    description=f"Módulo {name} com {len(nodes)} estados",
                    node_count=len(nodes),
                    api_count=api_count,
                    decision_count=decision_count,
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
                        for n in nodes
                    ],
                )
            )
        return modules

    def get_module_nodes(self, flow_id: str, module_name: str) -> list[NodeResponse]:
        nodes = self.node_repo.get_by_module(flow_id, module_name)
        return [
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
            for n in nodes
        ]
