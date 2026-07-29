from app.application.dto.schemas import DocumentationResponse, DocumentResponse
from app.domain.enums.flow_enums import NodeType
from app.infrastructure.repositories.api_repository import ApiRepository
from app.infrastructure.repositories.document_repository import DocumentRepository
from app.infrastructure.repositories.flow_repository import FlowRepository
from app.infrastructure.repositories.node_repository import NodeRepository
from app.infrastructure.repositories.variable_repository import VariableRepository


class DocumentationService:
    SECTIONS = ["summary", "objective", "inputs", "outputs", "apis", "variables", "flow", "rules", "exceptions"]

    def __init__(
        self,
        flow_repo: FlowRepository,
        node_repo: NodeRepository,
        api_repo: ApiRepository,
        variable_repo: VariableRepository,
        document_repo: DocumentRepository,
    ):
        self.flow_repo = flow_repo
        self.node_repo = node_repo
        self.api_repo = api_repo
        self.variable_repo = variable_repo
        self.document_repo = document_repo

    def generate_documentation(self, flow_id: str) -> DocumentationResponse:
        flow = self.flow_repo.get_by_id(flow_id)
        if not flow:
            raise ValueError(f"Flow {flow_id} not found")

        nodes = flow.nodes or []
        apis = flow.apis or []
        variables = flow.variables or []

        modules = sorted({n.module or "Geral" for n in nodes})
        start_nodes = [n for n in nodes if n.node_type == NodeType.START.value]
        end_nodes = [n for n in nodes if n.node_type == NodeType.END.value]
        conditions = [n for n in nodes if n.node_type == NodeType.CONDITION.value]
        errors = [n for n in nodes if n.node_type == NodeType.ERROR.value]

        doc = DocumentationResponse(
            flow_id=flow_id,
            summary=self._build_summary(flow.name, flow.flow_type, len(nodes), len(modules)),
            objective=self._build_objective(flow.name, flow.description, flow.flow_type),
            inputs=self._build_inputs(start_nodes, variables),
            outputs=self._build_outputs(end_nodes),
            apis=self._build_apis_section(apis),
            variables=self._build_variables_section(variables),
            flow_description=self._build_flow_description(modules, nodes),
            rules=self._build_rules(conditions),
            exceptions=self._build_exceptions(errors),
        )

        for section, content in [
            ("summary", doc.summary),
            ("objective", doc.objective),
            ("inputs", doc.inputs),
            ("outputs", doc.outputs),
            ("apis", doc.apis),
            ("variables", doc.variables),
            ("flow", doc.flow_description),
            ("rules", doc.rules),
            ("exceptions", doc.exceptions),
        ]:
            self.document_repo.upsert(flow_id, section, content)

        return doc

    def get_documents(self, flow_id: str) -> list[DocumentResponse]:
        docs = self.document_repo.get_by_flow(flow_id)
        if not docs:
            return []
        return [
            DocumentResponse(
                id=d.id,
                flow_id=d.flow_id,
                section=d.section,
                content=d.content,
                updated_at=d.updated_at,
            )
            for d in docs
        ]

    def _build_summary(self, name: str, flow_type: str, node_count: int, module_count: int) -> str:
        return (
            f"# {name}\n\n"
            f"Fluxo do tipo **{flow_type}** com **{node_count}** estados organizados em "
            f"**{module_count}** módulos.\n\n"
            f"Este documento foi gerado automaticamente pelo Flow Navigator."
        )

    def _build_objective(self, name: str, description: str | None, flow_type: str) -> str:
        base = description or f"Automatizar o atendimento via {flow_type} para {name}."
        return f"## Objetivo\n\n{base}"

    def _build_inputs(self, start_nodes, variables) -> str:
        lines = ["## Entradas\n"]
        if start_nodes:
            lines.append("### Pontos de Entrada\n")
            for n in start_nodes:
                lines.append(f"- **{n.label}** ({n.external_id})")
        if variables:
            lines.append("\n### Variáveis de Entrada\n")
            for v in variables:
                default = f" (padrão: {v.default_value})" if v.default_value else ""
                lines.append(f"- `{v.name}`{default}")
        return "\n".join(lines)

    def _build_outputs(self, end_nodes) -> str:
        lines = ["## Saídas\n"]
        if end_nodes:
            for n in end_nodes:
                lines.append(f"- **{n.label}** — Finalização ({n.external_id})")
        else:
            lines.append("- Fluxo sem estados de finalização explícitos detectados.")
        return "\n".join(lines)

    def _build_apis_section(self, apis) -> str:
        lines = ["## APIs\n"]
        if not apis:
            lines.append("Nenhuma API detectada neste fluxo.")
            return "\n".join(lines)
        for api in apis:
            lines.append(f"### {api.name}\n")
            lines.append(f"- **Método:** {api.method}")
            if api.url:
                lines.append(f"- **URL:** `{api.url}`")
            if api.description:
                lines.append(f"- **Descrição:** {api.description}")
            lines.append("")
        return "\n".join(lines)

    def _build_variables_section(self, variables) -> str:
        lines = ["## Variáveis\n"]
        if not variables:
            lines.append("Nenhuma variável detectada neste fluxo.")
            return "\n".join(lines)
        for var in variables:
            usage = len(var.node_ids or [])
            lines.append(f"- `{var.name}` — utilizada em {usage} estado(s)")
        return "\n".join(lines)

    def _build_flow_description(self, modules, nodes) -> str:
        lines = ["## Fluxo\n"]
        for module in modules:
            module_nodes = [n for n in nodes if (n.module or "Geral") == module]
            lines.append(f"### 📦 {module}\n")
            for n in module_nodes[:20]:
                icon = self._node_icon(n.node_type)
                lines.append(f"- {icon} {n.label}")
            if len(module_nodes) > 20:
                lines.append(f"- ... e mais {len(module_nodes) - 20} estados")
            lines.append("")
        return "\n".join(lines)

    def _build_rules(self, conditions) -> str:
        lines = ["## Regras\n"]
        if not conditions:
            lines.append("Nenhuma regra de decisão detectada.")
            return "\n".join(lines)
        for c in conditions:
            lines.append(f"- **{c.label}** — condição em `{c.external_id}`")
        return "\n".join(lines)

    def _build_exceptions(self, errors) -> str:
        lines = ["## Exceções\n"]
        if not errors:
            lines.append("Nenhum tratamento de erro explícito detectado.")
            return "\n".join(lines)
        for e in errors:
            lines.append(f"- ⚠️ **{e.label}** — `{e.external_id}`")
        return "\n".join(lines)

    @staticmethod
    def _node_icon(node_type: str) -> str:
        icons = {
            "start": "▶️",
            "end": "⏹️",
            "menu": "📋",
            "submenu": "📑",
            "message": "💬",
            "condition": "🔀",
            "api": "🔗",
            "variable": "📊",
            "human_handoff": "👤",
            "error": "⚠️",
            "flow": "🔄",
        }
        return icons.get(node_type, "•")
