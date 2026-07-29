import re
from typing import Any

from app.domain.entities.graph import GraphApi, GraphEdge, GraphModule, GraphNode, GraphVariable, ParsedGraph
from app.domain.enums.flow_enums import NodeType


class NodeClassifier:
    MENU_KEYWORDS = {"menu", "opção", "opcao", "option", "choices", "list", "lista"}
    MESSAGE_KEYWORDS = {"message", "mensagem", "text", "texto", "reply", "resposta", "send"}
    CONDITION_KEYWORDS = {"condition", "condição", "condicao", "if", "switch", "decision", "decisão"}
    API_KEYWORDS = {"api", "http", "request", "webhook", "rest", "endpoint", "integration", "integração"}
    HUMAN_KEYWORDS = {"human", "humano", "attendant", "atendente", "handoff", "transfer", "transferência"}
    ERROR_KEYWORDS = {"error", "erro", "exception", "fail", "falha", "timeout"}
    END_KEYWORDS = {"end", "fim", "finish", "finalizar", "close", "encerrar", "terminate"}
    START_KEYWORDS = {"start", "início", "inicio", "begin", "root", "entry", "entrada"}
    FLOW_KEYWORDS = {"flow", "fluxo", "subflow", "subfluxo", "redirect", "goto"}
    VARIABLE_KEYWORDS = {"variable", "variável", "variavel", "set", "store", "save", "input", "capture"}

    @classmethod
    def classify(cls, label: str, metadata: dict[str, Any] | None = None) -> str:
        text = label.lower()
        meta_text = " ".join(str(v).lower() for v in (metadata or {}).values())
        combined = f"{text} {meta_text}"

        checks = [
            (cls.START_KEYWORDS, NodeType.START),
            (cls.END_KEYWORDS, NodeType.END),
            (cls.MENU_KEYWORDS, NodeType.MENU),
            (cls.CONDITION_KEYWORDS, NodeType.CONDITION),
            (cls.API_KEYWORDS, NodeType.API),
            (cls.HUMAN_KEYWORDS, NodeType.HUMAN_HANDOFF),
            (cls.ERROR_KEYWORDS, NodeType.ERROR),
            (cls.VARIABLE_KEYWORDS, NodeType.VARIABLE),
            (cls.FLOW_KEYWORDS, NodeType.FLOW),
            (cls.MESSAGE_KEYWORDS, NodeType.MESSAGE),
        ]

        for keywords, node_type in checks:
            if any(kw in combined for kw in keywords):
                return node_type.value

        if metadata:
            meta_type = str(metadata.get("type", metadata.get("$type", ""))).lower()
            if meta_type:
                for keywords, node_type in checks:
                    if any(kw in meta_type for kw in keywords):
                        return node_type.value

        return NodeType.UNKNOWN.value


class ModuleOrganizer:
    @staticmethod
    def organize(nodes: list[GraphNode]) -> tuple[list[GraphNode], list[GraphModule]]:
        modules: dict[str, GraphModule] = {}
        updated_nodes: list[GraphNode] = []

        for node in nodes:
            module_name = ModuleOrganizer._detect_module(node)
            node.module = module_name

            if module_name not in modules:
                modules[module_name] = GraphModule(
                    external_id=f"module_{module_name.lower().replace(' ', '_')}",
                    name=module_name,
                    description=f"Módulo {module_name}",
                    node_ids=[],
                )
            modules[module_name].node_ids.append(node.external_id)
            updated_nodes.append(node)

        return updated_nodes, list(modules.values())

    @staticmethod
    def _detect_module(node: GraphNode) -> str:
        label = node.label.strip()
        if node.metadata.get("module"):
            return str(node.metadata["module"])

        parts = re.split(r"[>/\\|→\-–]", label)
        if len(parts) > 1:
            return parts[0].strip() or "Geral"

        if node.node_type in (NodeType.MENU.value, NodeType.SUBMENU.value):
            return label or "Menus"

        if node.node_type == NodeType.API.value:
            return "APIs"

        if node.node_type == NodeType.CONDITION.value:
            return "Decisões"

        if node.node_type == NodeType.HUMAN_HANDOFF.value:
            return "Atendimento Humano"

        if node.node_type == NodeType.ERROR.value:
            return "Erros"

        if node.node_type == NodeType.END.value:
            return "Finalizações"

        return "Geral"
