import json
import re
from typing import Any

from app.domain.entities.graph import GraphEdge, GraphNode, ParsedGraph
from app.domain.enums.flow_enums import EdgeType, NodeType
from app.parsers.base import BaseParser
from app.parsers.classifier import ModuleOrganizer, NodeClassifier


class UraParser(BaseParser):
    """Generic parser for URA (phone IVR) PDF and JSON files."""

    STEP_PATTERNS = [
        r"(?:passo|step|etapa|state|estado|menu|opção|opcao)\s*[:\-]?\s*(.+)",
        r"(?:se|if|quando|when)\s+(.+?)(?:,\s*(?:então|then|vá|va|ir)\s+(.+))?",
        r"(?:transferir|transfer|encaminhar|redirect)\s+(?:para|to)\s+(.+)",
        r"(?:reproduzir|play|falar|say|mensagem|message)\s*[:\-]?\s*(.+)",
        r"(?:aguardar|wait|input|entrada|capturar|capture)\s*[:\-]?\s*(.+)",
        r"(?:finalizar|end|encerrar|desligar|hangup)",
        r"(?:erro|error|timeout|falha|fail)",
    ]

    ARROW_PATTERN = re.compile(r"(.+?)\s*(?:→|->|-->|=>|vai para|ir para|goto)\s*(.+)", re.IGNORECASE)
    OPTION_PATTERN = re.compile(r"(?:opção|opcao|option|tecla|key|digite|press)\s*[:\-]?\s*(\d+|[*#])\s*[:\-]?\s*(.+)", re.IGNORECASE)

    def can_parse(self, filename: str, content_type: str | None = None) -> bool:
        lower = filename.lower()
        return lower.endswith(".pdf") or lower.endswith(".json")

    def parse(self, content: bytes | str, metadata: dict[str, Any] | None = None) -> ParsedGraph:
        filename = (metadata or {}).get("filename", "")
        if filename.lower().endswith(".json") or (isinstance(content, str) and content.strip().startswith("{")):
            return self._parse_json(content)
        return self._parse_pdf(content)

    def _parse_json(self, content: bytes | str) -> ParsedGraph:
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        data = json.loads(content)

        nodes: dict[str, GraphNode] = {}
        edges: list[GraphEdge] = []

        if isinstance(data, list):
            for i, item in enumerate(data):
                self._parse_json_item(item, nodes, edges, f"step_{i}")
        elif isinstance(data, dict):
            if "nodes" in data or "states" in data or "steps" in data:
                items = data.get("nodes") or data.get("states") or data.get("steps") or []
                for i, item in enumerate(items):
                    self._parse_json_item(item, nodes, edges, f"step_{i}")
            else:
                for i, (key, value) in enumerate(data.items()):
                    if isinstance(value, dict):
                        self._parse_json_item(value, nodes, edges, str(key))
                    else:
                        node_id = f"step_{i}_{key}"
                        nodes[node_id] = GraphNode(
                            external_id=node_id,
                            label=str(value)[:500],
                            node_type=NodeClassifier.classify(str(value)),
                            metadata={"key": key},
                        )

        node_list = list(nodes.values())
        node_list, modules = ModuleOrganizer.organize(node_list)

        return ParsedGraph(
            nodes=node_list,
            edges=edges,
            modules=modules,
            metadata={"source": "ura_json", "node_count": len(node_list)},
        )

    def _parse_json_item(
        self, item: dict[str, Any], nodes: dict[str, GraphNode], edges: list[GraphEdge], default_id: str
    ) -> None:
        node_id = str(item.get("id") or item.get("name") or item.get("state") or default_id)
        label = str(
            item.get("label") or item.get("title") or item.get("description") or item.get("prompt") or node_id
        )
        node_type = NodeClassifier.classify(label, item)

        nodes[node_id] = GraphNode(
            external_id=node_id,
            label=label[:500],
            node_type=node_type,
            description=str(item.get("description", ""))[:1000],
            metadata={k: v for k, v in item.items() if isinstance(v, (str, int, float, bool))},
        )

        for key in ("next", "target", "goto", "success", "failure", "transitions"):
            if key not in item:
                continue
            val = item[key]
            if isinstance(val, str):
                edges.append(GraphEdge(source_id=node_id, target_id=val, label=key, edge_type=EdgeType.DEFAULT.value))
            elif isinstance(val, dict):
                for lbl, tgt in val.items():
                    edges.append(
                        GraphEdge(source_id=node_id, target_id=str(tgt), label=str(lbl), edge_type=EdgeType.DEFAULT.value)
                    )
            elif isinstance(val, list):
                for i, tgt in enumerate(val):
                    target_id = tgt if isinstance(tgt, str) else str(tgt.get("target", tgt.get("id", f"unknown_{i}")))
                    edges.append(
                        GraphEdge(source_id=node_id, target_id=target_id, label=str(i), edge_type=EdgeType.MENU_OPTION.value)
                    )

    def _parse_pdf(self, content: bytes | str) -> ParsedGraph:
        if isinstance(content, str):
            content = content.encode("utf-8")

        text = self._extract_pdf_text(content)
        lines = [line.strip() for line in text.split("\n") if line.strip()]

        nodes: dict[str, GraphNode] = {}
        edges: list[GraphEdge] = []
        current_module = "Geral"

        for i, line in enumerate(lines):
            node_id = f"ura_line_{i}"
            node_type = NodeClassifier.classify(line)
            label = line[:500]

            if self._is_module_header(line):
                current_module = self._extract_module_name(line)
                continue

            nodes[node_id] = GraphNode(
                external_id=node_id,
                label=label,
                node_type=node_type,
                module=current_module,
                metadata={"line_number": i + 1},
            )

            arrow_match = self.ARROW_PATTERN.search(line)
            if arrow_match:
                source_label, target_label = arrow_match.groups()
                target_id = self._find_or_create_target(nodes, target_label.strip(), i)
                source_id = node_id
                edges.append(
                    GraphEdge(source_id=source_id, target_id=target_id, label="→", edge_type=EdgeType.DEFAULT.value)
                )

            option_match = self.OPTION_PATTERN.search(line)
            if option_match:
                option_key, option_label = option_match.groups()
                sub_id = f"ura_option_{i}_{option_key}"
                nodes[sub_id] = GraphNode(
                    external_id=sub_id,
                    label=option_label.strip()[:500],
                    node_type=NodeType.SUBMENU.value,
                    module=current_module,
                    metadata={"option_key": option_key},
                )
                edges.append(
                    GraphEdge(
                        source_id=node_id,
                        target_id=sub_id,
                        label=option_key,
                        edge_type=EdgeType.MENU_OPTION.value,
                    )
                )

            if i > 0 and node_type not in (NodeType.END.value, NodeType.ERROR.value):
                prev_id = f"ura_line_{i - 1}"
                if prev_id in nodes and not any(e.source_id == prev_id and e.target_id == node_id for e in edges):
                    if nodes[prev_id].node_type not in (NodeType.CONDITION.value, NodeType.MENU.value):
                        edges.append(
                            GraphEdge(
                                source_id=prev_id,
                                target_id=node_id,
                                label="next",
                                edge_type=EdgeType.DEFAULT.value,
                            )
                        )

        node_list = list(nodes.values())
        node_list, modules = ModuleOrganizer.organize(node_list)

        return ParsedGraph(
            nodes=node_list,
            edges=edges,
            modules=modules,
            metadata={"source": "ura_pdf", "node_count": len(node_list), "line_count": len(lines)},
        )

    def _extract_pdf_text(self, content: bytes) -> str:
        try:
            import pdfplumber
            import io

            text_parts: list[str] = []
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            return "\n".join(text_parts)
        except Exception:
            try:
                from PyPDF2 import PdfReader
                import io

                reader = PdfReader(io.BytesIO(content))
                return "\n".join(page.extract_text() or "" for page in reader.pages)
            except Exception:
                return content.decode("utf-8", errors="ignore")

    def _is_module_header(self, line: str) -> bool:
        patterns = [
            r"^(?:módulo|modulo|module|seção|secao|section|fluxo|flow)\s*[:\-]",
            r"^[=\-*#]{3,}",
            r"^[A-ZÁÉÍÓÚÂÊÔÃÕÇ\s]{5,}$",
        ]
        return any(re.match(p, line, re.IGNORECASE) for p in patterns)

    def _extract_module_name(self, line: str) -> str:
        cleaned = re.sub(r"^[=\-*#\s]+|[=\-*#\s]+$", "", line)
        cleaned = re.sub(r"^(?:módulo|modulo|module|seção|secao|section|fluxo|flow)\s*[:\-]?\s*", "", cleaned, flags=re.IGNORECASE)
        return cleaned.strip() or "Geral"

    def _find_or_create_target(self, nodes: dict[str, GraphNode], target_label: str, index: int) -> str:
        for node_id, node in nodes.items():
            if node.label.lower() == target_label.lower():
                return node_id
        new_id = f"ura_target_{index}"
        nodes[new_id] = GraphNode(
            external_id=new_id,
            label=target_label[:500],
            node_type=NodeClassifier.classify(target_label),
        )
        return new_id
