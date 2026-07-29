import json
from datetime import datetime
from pathlib import Path

from app.application.dto.schemas import ComparisonResponse, ExportResponse
from app.application.services.documentation_service import DocumentationService
from app.core.config import get_settings
from app.infrastructure.models import ExportModel
from app.infrastructure.repositories.edge_repository import EdgeRepository
from app.infrastructure.repositories.export_repository import ExportRepository
from app.infrastructure.repositories.flow_repository import FlowRepository
from app.infrastructure.repositories.node_repository import NodeRepository
from app.infrastructure.repositories.version_repository import VersionRepository


class ExportService:
    def __init__(
        self,
        flow_repo: FlowRepository,
        node_repo: NodeRepository,
        edge_repo: EdgeRepository,
        export_repo: ExportRepository,
        doc_service: DocumentationService,
    ):
        self.flow_repo = flow_repo
        self.node_repo = node_repo
        self.edge_repo = edge_repo
        self.export_repo = export_repo
        self.doc_service = doc_service
        self.settings = get_settings()

    def export(self, flow_id: str, format: str, module: str | None = None) -> ExportResponse:
        flow = self.flow_repo.get_by_id(flow_id)
        if not flow:
            raise ValueError(f"Flow {flow_id} not found")

        self.settings.ensure_directories()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{flow.name}_{timestamp}.{format}"
        file_path = self.settings.export_dir / filename

        if format == "json":
            self._export_json(flow_id, file_path, module)
        elif format == "markdown":
            self._export_markdown(flow_id, file_path)
        elif format == "html":
            self._export_html(flow_id, file_path)
        elif format == "svg":
            self._export_svg(flow_id, file_path, module)
        elif format == "png":
            self._export_png_placeholder(flow_id, file_path)
        elif format == "pdf":
            self._export_pdf(flow_id, file_path)
        else:
            raise ValueError(f"Unsupported format: {format}")

        export_record = self.export_repo.create(
            ExportModel(flow_id=flow_id, format=format, file_path=str(file_path))
        )

        return ExportResponse(
            id=export_record.id,
            flow_id=flow_id,
            format=format,
            file_path=str(file_path),
            download_url=f"/api/v1/export/download/{export_record.id}",
            created_at=export_record.created_at,
        )

    def get_export_file(self, export_id: str) -> Path | None:
        record = self.export_repo.get_by_id(export_id)
        if not record:
            return None
        path = Path(record.file_path)
        return path if path.exists() else None

    def _export_json(self, flow_id: str, file_path: Path, module: str | None) -> None:
        flow = self.flow_repo.get_by_id(flow_id)
        nodes = flow.nodes or []
        if module:
            nodes = [n for n in nodes if (n.module or "Geral") == module]

        data = {
            "flow": {"id": flow.id, "name": flow.name, "type": flow.flow_type},
            "nodes": [
                {
                    "id": n.id,
                    "external_id": n.external_id,
                    "label": n.label,
                    "type": n.node_type,
                    "module": n.module,
                    "metadata": n.metadata_json,
                }
                for n in nodes
            ],
            "edges": [
                {
                    "source": e.source_id,
                    "target": e.target_id,
                    "label": e.label,
                    "type": e.edge_type,
                }
                for e in (flow.edges or [])
            ],
        }
        file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def _export_markdown(self, flow_id: str, file_path: Path) -> None:
        doc = self.doc_service.generate_documentation(flow_id)
        content = "\n\n---\n\n".join(
            [
                doc.summary,
                doc.objective,
                doc.inputs,
                doc.outputs,
                doc.apis,
                doc.variables,
                doc.flow_description,
                doc.rules,
                doc.exceptions,
            ]
        )
        file_path.write_text(content, encoding="utf-8")

    def _export_html(self, flow_id: str, file_path: Path) -> None:
        doc = self.doc_service.generate_documentation(flow_id)
        flow = self.flow_repo.get_by_id(flow_id)
        html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>{flow.name} - Documentação</title>
  <style>
    body {{ font-family: system-ui, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; line-height: 1.6; }}
    h1, h2, h3 {{ color: #1a1a2e; }}
    code {{ background: #f4f4f4; padding: 2px 6px; border-radius: 4px; }}
    hr {{ border: none; border-top: 1px solid #e0e0e0; margin: 2rem 0; }}
  </style>
</head>
<body>
  <h1>{flow.name}</h1>
  <p>Tipo: {flow.flow_type} | Estados: {len(flow.nodes or [])}</p>
  <hr>
  <pre>{doc.summary}</pre>
  <pre>{doc.objective}</pre>
  <pre>{doc.inputs}</pre>
  <pre>{doc.outputs}</pre>
  <pre>{doc.apis}</pre>
  <pre>{doc.variables}</pre>
  <pre>{doc.flow_description}</pre>
  <pre>{doc.rules}</pre>
  <pre>{doc.exceptions}</pre>
</body>
</html>"""
        file_path.write_text(html, encoding="utf-8")

    def _export_svg(self, flow_id: str, file_path: Path, module: str | None) -> None:
        flow = self.flow_repo.get_by_id(flow_id)
        nodes = flow.nodes or []
        if module:
            nodes = [n for n in nodes if (n.module or "Geral") == module]

        width, height = 1200, max(800, len(nodes) * 80 + 200)
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
            '<style>.node {{ fill: #6366f1; stroke: #4338ca; rx: 8; }} .label {{ fill: white; font: 12px sans-serif; }}</style>',
        ]

        for i, node in enumerate(nodes):
            x = 100 + (i % 4) * 250
            y = 100 + (i // 4) * 100
            label = node.label[:30].replace("&", "&amp;").replace("<", "&lt;")
            svg_parts.append(f'<rect class="node" x="{x}" y="{y}" width="200" height="50"/>')
            svg_parts.append(f'<text class="label" x="{x + 10}" y="{y + 30}">{label}</text>')

        svg_parts.append("</svg>")
        file_path.write_text("\n".join(svg_parts), encoding="utf-8")

    def _export_png_placeholder(self, flow_id: str, file_path: Path) -> None:
        try:
            import cairosvg

            svg_path = file_path.with_suffix(".svg")
            self._export_svg(flow_id, svg_path, None)
            cairosvg.svg2png(url=str(svg_path), write_to=str(file_path))
            svg_path.unlink(missing_ok=True)
        except Exception:
            file_path.write_bytes(b"PNG placeholder - install cairosvg for full export")

    def _export_pdf(self, flow_id: str, file_path: Path) -> None:
        html_path = file_path.with_suffix(".html")
        self._export_html(flow_id, html_path)
        try:
            from weasyprint import HTML

            HTML(filename=str(html_path)).write_pdf(str(file_path))
            html_path.unlink(missing_ok=True)
        except Exception:
            file_path.write_text(html_path.read_text(encoding="utf-8"), encoding="utf-8")
            html_path.unlink(missing_ok=True)


class ComparisonService:
    def __init__(
        self,
        flow_repo: FlowRepository,
        node_repo: NodeRepository,
        edge_repo: EdgeRepository,
        version_repo: VersionRepository,
    ):
        self.flow_repo = flow_repo
        self.node_repo = node_repo
        self.edge_repo = edge_repo
        self.version_repo = version_repo

    def compare_versions(self, flow_id: str, version_a: int, version_b: int) -> ComparisonResponse:
        versions = self.version_repo.get_by_flow(flow_id)
        snap_a = next((v.snapshot_json for v in versions if v.version_number == version_a), None)
        snap_b = next((v.snapshot_json for v in versions if v.version_number == version_b), None)

        if not snap_a or not snap_b:
            raise ValueError("One or both versions not found")

        nodes_a = {n["external_id"]: n for n in snap_a.get("nodes", [])}
        nodes_b = {n["external_id"]: n for n in snap_b.get("nodes", [])}

        added = [nodes_b[k] for k in nodes_b if k not in nodes_a]
        removed = [nodes_a[k] for k in nodes_a if k not in nodes_b]
        changed = [
            {"before": nodes_a[k], "after": nodes_b[k]}
            for k in nodes_a
            if k in nodes_b and nodes_a[k] != nodes_b[k]
        ]

        edges_a = {(e["source_id"], e["target_id"]): e for e in snap_a.get("edges", [])}
        edges_b = {(e["source_id"], e["target_id"]): e for e in snap_b.get("edges", [])}

        added_edges = [edges_b[k] for k in edges_b if k not in edges_a]
        removed_edges = [edges_a[k] for k in edges_a if k not in edges_b]

        return ComparisonResponse(
            flow_id=flow_id,
            version_a=version_a,
            version_b=version_b,
            added_nodes=added,
            removed_nodes=removed,
            changed_nodes=changed,
            added_edges=added_edges,
            removed_edges=removed_edges,
        )
