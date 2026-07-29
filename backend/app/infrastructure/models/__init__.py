import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


class ProjectModel(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    flows: Mapped[list["FlowModel"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class FlowModel(Base):
    __tablename__ = "flows"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    flow_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    project: Mapped["ProjectModel"] = relationship(back_populates="flows")
    nodes: Mapped[list["NodeModel"]] = relationship(back_populates="flow", cascade="all, delete-orphan")
    edges: Mapped[list["EdgeModel"]] = relationship(back_populates="flow", cascade="all, delete-orphan")
    apis: Mapped[list["ApiModel"]] = relationship(back_populates="flow", cascade="all, delete-orphan")
    variables: Mapped[list["VariableModel"]] = relationship(back_populates="flow", cascade="all, delete-orphan")
    versions: Mapped[list["VersionModel"]] = relationship(back_populates="flow", cascade="all, delete-orphan")
    documents: Mapped[list["DocumentModel"]] = relationship(back_populates="flow", cascade="all, delete-orphan")
    exports: Mapped[list["ExportModel"]] = relationship(back_populates="flow", cascade="all, delete-orphan")


class NodeModel(Base):
    __tablename__ = "nodes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    flow_id: Mapped[str] = mapped_column(String(36), ForeignKey("flows.id", ondelete="CASCADE"))
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    label: Mapped[str] = mapped_column(String(500), nullable=False)
    node_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    module: Mapped[str | None] = mapped_column(String(255), nullable=True)
    position_x: Mapped[float] = mapped_column(Float, default=0.0)
    position_y: Mapped[float] = mapped_column(Float, default=0.0)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    parent_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("nodes.id"), nullable=True)
    is_collapsed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    flow: Mapped["FlowModel"] = relationship(back_populates="nodes")
    children: Mapped[list["NodeModel"]] = relationship(back_populates="parent", remote_side=[id])


class EdgeModel(Base):
    __tablename__ = "edges"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    flow_id: Mapped[str] = mapped_column(String(36), ForeignKey("flows.id", ondelete="CASCADE"))
    source_id: Mapped[str] = mapped_column(String(36), ForeignKey("nodes.id", ondelete="CASCADE"))
    target_id: Mapped[str] = mapped_column(String(36), ForeignKey("nodes.id", ondelete="CASCADE"))
    label: Mapped[str | None] = mapped_column(String(500), nullable=True)
    edge_type: Mapped[str] = mapped_column(String(50), default="default")
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    flow: Mapped["FlowModel"] = relationship(back_populates="edges")


class ApiModel(Base):
    __tablename__ = "apis"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    flow_id: Mapped[str] = mapped_column(String(36), ForeignKey("flows.id", ondelete="CASCADE"))
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    method: Mapped[str] = mapped_column(String(20), default="GET")
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    node_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    flow: Mapped["FlowModel"] = relationship(back_populates="apis")


class VariableModel(Base):
    __tablename__ = "variables"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    flow_id: Mapped[str] = mapped_column(String(36), ForeignKey("flows.id", ondelete="CASCADE"))
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    node_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    flow: Mapped["FlowModel"] = relationship(back_populates="variables")


class VersionModel(Base):
    __tablename__ = "versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    flow_id: Mapped[str] = mapped_column(String(36), ForeignKey("flows.id", ondelete="CASCADE"))
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    snapshot_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    flow: Mapped["FlowModel"] = relationship(back_populates="versions")


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    flow_id: Mapped[str] = mapped_column(String(36), ForeignKey("flows.id", ondelete="CASCADE"))
    section: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    flow: Mapped["FlowModel"] = relationship(back_populates="documents")


class ExportModel(Base):
    __tablename__ = "exports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid)
    flow_id: Mapped[str] = mapped_column(String(36), ForeignKey("flows.id", ondelete="CASCADE"))
    format: Mapped[str] = mapped_column(String(20), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    flow: Mapped["FlowModel"] = relationship(back_populates="exports")
