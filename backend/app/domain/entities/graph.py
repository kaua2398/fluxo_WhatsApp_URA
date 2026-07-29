from dataclasses import dataclass, field
from typing import Any


@dataclass
class GraphNode:
    external_id: str
    label: str
    node_type: str
    description: str = ""
    module: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    position_x: float = 0.0
    position_y: float = 0.0


@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    label: str = ""
    edge_type: str = "default"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphApi:
    external_id: str
    name: str
    method: str = "GET"
    url: str = ""
    description: str = ""
    node_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphVariable:
    external_id: str
    name: str
    description: str = ""
    default_value: str = ""
    node_ids: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class GraphModule:
    external_id: str
    name: str
    description: str = ""
    node_ids: list[str] = field(default_factory=list)
    parent_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedGraph:
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)
    apis: list[GraphApi] = field(default_factory=list)
    variables: list[GraphVariable] = field(default_factory=list)
    modules: list[GraphModule] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
