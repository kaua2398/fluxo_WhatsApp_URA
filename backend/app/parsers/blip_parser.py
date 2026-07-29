import json
import re
from typing import Any

from app.domain.entities.graph import GraphApi, GraphEdge, GraphNode, GraphVariable, ParsedGraph
from app.domain.enums.flow_enums import EdgeType, NodeType
from app.parsers.base import BaseParser
from app.parsers.classifier import ModuleOrganizer, NodeClassifier


class BlipParser(BaseParser):
    """Generic parser for Blip/WhatsApp bot JSON exports."""

    ID_KEYS = {"id", "$id", "identifier", "name", "key", "nodeId", "blockId", "stateId"}
    LABEL_KEYS = {"title", "label", "name", "text", "description", "content", "message"}
    TYPE_KEYS = {"$type", "type", "kind", "nodeType", "blockType", "stateType"}
    TARGET_KEYS = {"target", "to", "next", "goto", "destination", "success", "failure", "true", "false"}
    TRANSITION_KEYS = {"transitions", "edges", "connections", "links", "outputs", "routes", "nextStates"}
    CONTENT_KEYS = {"content", "body", "payload", "data", "config", "settings", "properties", "metadata"}
    CHILD_KEYS = {"states", "nodes", "blocks", "steps", "items", "children", "elements", "actions"}

    def can_parse(self, filename: str, content_type: str | None = None) -> bool:
        return filename.lower().endswith(".json")

    def parse(self, content: bytes | str, metadata: dict[str, Any] | None = None) -> ParsedGraph:
        if isinstance(content, bytes):
            content = content.decode("utf-8")

        data = json.loads(content)
        nodes: dict[str, GraphNode] = {}
        edges: list[GraphEdge] = []
        apis: list[GraphApi] = []
        variables: dict[str, GraphVariable] = {}
        visited_ids: set[str] = set()

        self._traverse(data, nodes, edges, apis, variables, visited_ids, path="root")

        node_list = list(nodes.values())
        node_list, modules = ModuleOrganizer.organize(node_list)

        return ParsedGraph(
            nodes=node_list,
            edges=edges,
            apis=list(apis),
            variables=list(variables.values()),
            modules=modules,
            metadata={"source": "blip", "node_count": len(node_list)},
        )

    def _traverse(
        self,
        obj: Any,
        nodes: dict[str, GraphNode],
        edges: list[GraphEdge],
        apis: list[GraphApi],
        variables: dict[str, GraphVariable],
        visited_ids: set[str],
        path: str,
        parent_id: str | None = None,
    ) -> None:
        if isinstance(obj, dict):
            node_id = self._extract_id(obj, path)
            label = self._extract_label(obj, node_id)
            node_type = NodeClassifier.classify(label, obj)

            if self._is_node_candidate(obj) and node_id not in visited_ids:
                visited_ids.add(node_id)
                nodes[node_id] = GraphNode(
                    external_id=node_id,
                    label=label,
                    node_type=node_type,
                    description=self._extract_description(obj),
                    metadata={"path": path, "raw_type": self._extract_type(obj), **self._safe_metadata(obj)},
                )

                if node_type == NodeType.API.value:
                    apis.append(self._extract_api(obj, node_id))

                self._extract_variables(obj, node_id, variables)
                self._extract_transitions(obj, node_id, edges)

            for key, value in obj.items():
                child_path = f"{path}.{key}"
                if key in self.CHILD_KEYS and isinstance(value, (list, dict)):
                    if isinstance(value, list):
                        for i, item in enumerate(value):
                            self._traverse(item, nodes, edges, apis, variables, visited_ids, f"{child_path}[{i}]", node_id)
                    else:
                        self._traverse(value, nodes, edges, apis, variables, visited_ids, child_path, node_id)
                elif isinstance(value, (dict, list)) and key not in self.CONTENT_KEYS:
                    if isinstance(value, list):
                        for i, item in enumerate(value):
                            self._traverse(item, nodes, edges, apis, variables, visited_ids, f"{child_path}[{i}]", node_id)
                    else:
                        self._traverse(value, nodes, edges, apis, variables, visited_ids, child_path, node_id)

        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self._traverse(item, nodes, edges, apis, variables, visited_ids, f"{path}[{i}]", parent_id)

    def _is_node_candidate(self, obj: dict[str, Any]) -> bool:
        has_id = any(k in obj for k in self.ID_KEYS)
        has_label = any(k in obj for k in self.LABEL_KEYS)
        has_type = any(k in obj for k in self.TYPE_KEYS)
        has_transitions = any(k in obj for k in self.TRANSITION_KEYS)
        return (has_id and has_label) or (has_type and (has_label or has_transitions))

    def _extract_id(self, obj: dict[str, Any], path: str) -> str:
        for key in self.ID_KEYS:
            if key in obj and obj[key]:
                return str(obj[key])
        return re.sub(r"[^a-zA-Z0-9_]", "_", path)

    def _extract_label(self, obj: dict[str, Any], node_id: str) -> str:
        for key in self.LABEL_KEYS:
            if key in obj and obj[key]:
                val = obj[key]
                if isinstance(val, str) and val.strip():
                    return val.strip()[:500]
                if isinstance(val, dict):
                    for sub_key in ("text", "title", "body", "value"):
                        if sub_key in val and val[sub_key]:
                            return str(val[sub_key]).strip()[:500]
        return node_id

    def _extract_type(self, obj: dict[str, Any]) -> str:
        for key in self.TYPE_KEYS:
            if key in obj:
                return str(obj[key])
        return ""

    def _extract_description(self, obj: dict[str, Any]) -> str:
        for key in ("description", "subtitle", "help", "tooltip"):
            if key in obj and obj[key]:
                return str(obj[key])[:1000]
        return ""

    def _extract_transitions(self, obj: dict[str, Any], source_id: str, edges: list[GraphEdge]) -> None:
        for key in self.TRANSITION_KEYS:
            if key not in obj:
                continue
            transitions = obj[key]
            if isinstance(transitions, dict):
                for label, target in transitions.items():
                    target_id = self._resolve_target(target)
                    if target_id:
                        edge_type = self._resolve_edge_type(label)
                        edges.append(
                            GraphEdge(
                                source_id=source_id,
                                target_id=target_id,
                                label=str(label),
                                edge_type=edge_type,
                            )
                        )
            elif isinstance(transitions, list):
                for i, transition in enumerate(transitions):
                    if isinstance(transition, dict):
                        target_id = self._resolve_target(transition.get("target") or transition.get("to") or transition)
                        label = transition.get("label") or transition.get("condition") or str(i)
                    else:
                        target_id = self._resolve_target(transition)
                        label = str(i)
                    if target_id:
                        edges.append(
                            GraphEdge(
                                source_id=source_id,
                                target_id=target_id,
                                label=str(label),
                                edge_type=EdgeType.DEFAULT.value,
                            )
                        )

        for key in self.TARGET_KEYS:
            if key in obj and obj[key]:
                target_id = self._resolve_target(obj[key])
                if target_id:
                    edges.append(
                        GraphEdge(
                            source_id=source_id,
                            target_id=target_id,
                            label=key,
                            edge_type=self._resolve_edge_type(key),
                        )
                    )

    def _resolve_target(self, target: Any) -> str | None:
        if target is None:
            return None
        if isinstance(target, str):
            return target.strip() or None
        if isinstance(target, dict):
            for key in self.ID_KEYS:
                if key in target:
                    return str(target[key])
        return str(target) if target else None

    def _resolve_edge_type(self, label: str) -> str:
        label_lower = str(label).lower()
        if label_lower in ("true", "yes", "sim", "success"):
            return EdgeType.CONDITION_TRUE.value
        if label_lower in ("false", "no", "não", "nao", "failure", "error"):
            return EdgeType.CONDITION_FALSE.value
        if "error" in label_lower or "fail" in label_lower:
            return EdgeType.ERROR.value
        if "timeout" in label_lower:
            return EdgeType.TIMEOUT.value
        if "option" in label_lower or label_lower.isdigit():
            return EdgeType.MENU_OPTION.value
        return EdgeType.DEFAULT.value

    def _extract_api(self, obj: dict[str, Any], node_id: str) -> GraphApi:
        url = ""
        method = "GET"
        for key in ("url", "uri", "endpoint", "address"):
            if key in obj:
                url = str(obj[key])
                break
        for key in ("method", "httpMethod", "verb"):
            if key in obj:
                method = str(obj[key]).upper()
                break
        return GraphApi(
            external_id=f"api_{node_id}",
            name=self._extract_label(obj, node_id),
            method=method,
            url=url,
            description=self._extract_description(obj),
            node_ids=[node_id],
            metadata=self._safe_metadata(obj),
        )

    def _extract_variables(
        self, obj: dict[str, Any], node_id: str, variables: dict[str, GraphVariable]
    ) -> None:
        var_patterns = ("variable", "variables", "setVariable", "store", "input", "capture", "context")
        for key in var_patterns:
            if key not in obj:
                continue
            val = obj[key]
            if isinstance(val, str):
                self._add_variable(variables, val, node_id)
            elif isinstance(val, dict):
                for var_name in val.keys():
                    self._add_variable(variables, str(var_name), node_id)
            elif isinstance(val, list):
                for item in val:
                    if isinstance(item, str):
                        self._add_variable(variables, item, node_id)
                    elif isinstance(item, dict):
                        name = item.get("name") or item.get("key") or item.get("variable")
                        if name:
                            self._add_variable(variables, str(name), node_id)

    def _add_variable(self, variables: dict[str, GraphVariable], name: str, node_id: str) -> None:
        if name not in variables:
            variables[name] = GraphVariable(external_id=f"var_{name}", name=name, node_ids=[node_id])
        elif node_id not in variables[name].node_ids:
            variables[name].node_ids.append(node_id)

    def _safe_metadata(self, obj: dict[str, Any]) -> dict[str, Any]:
        safe: dict[str, Any] = {}
        for key, value in obj.items():
            if key in self.CHILD_KEYS or key in self.TRANSITION_KEYS:
                continue
            if isinstance(value, (str, int, float, bool)) or value is None:
                safe[key] = value
            elif isinstance(value, dict) and len(json.dumps(value)) < 500:
                safe[key] = value
        return safe
