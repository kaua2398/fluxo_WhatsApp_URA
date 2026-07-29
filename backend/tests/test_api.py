import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


SAMPLE_BLIP = {
    "id": "root",
    "title": "Início",
    "type": "start",
    "states": [
        {"id": "menu", "title": "Menu", "type": "menu", "transitions": {"1": "msg"}},
        {"id": "msg", "title": "Mensagem", "type": "message"},
    ],
}


class TestProjectsAPI:
    def test_create_project(self, client):
        response = client.post("/api/v1/projects", json={"name": "ValeShop", "description": "Test project"})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "ValeShop"
        assert "id" in data

    def test_list_projects(self, client):
        client.post("/api/v1/projects", json={"name": "Project A"})
        response = client.get("/api/v1/projects")
        assert response.status_code == 200
        assert len(response.json()) >= 1

    def test_get_project_not_found(self, client):
        response = client.get("/api/v1/projects/nonexistent")
        assert response.status_code == 404


class TestFlowsAPI:
    def test_create_flow(self, client):
        project = client.post("/api/v1/projects", json={"name": "Test"}).json()
        response = client.post(
            "/api/v1/flows",
            json={"project_id": project["id"], "name": "WhatsApp", "flow_type": "whatsapp"},
        )
        assert response.status_code == 201
        assert response.json()["name"] == "WhatsApp"

    def test_upload_and_parse(self, client):
        project = client.post("/api/v1/projects", json={"name": "ValeShop"}).json()
        content = json.dumps(SAMPLE_BLIP).encode()
        response = client.post(
            "/api/v1/upload",
            data={"project_id": project["id"], "flow_type": "whatsapp"},
            files={"file": ("flow.json", content, "application/json")},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["node_count"] > 0
        assert data["edge_count"] > 0

    def test_get_flow_detail(self, client):
        project = client.post("/api/v1/projects", json={"name": "Test"}).json()
        content = json.dumps(SAMPLE_BLIP).encode()
        upload = client.post(
            "/api/v1/upload",
            data={"project_id": project["id"], "flow_type": "whatsapp"},
            files={"file": ("flow.json", content, "application/json")},
        ).json()

        response = client.get(f"/api/v1/flow/{upload['flow_id']}")
        assert response.status_code == 200
        data = response.json()
        assert len(data["nodes"]) > 0

    def test_get_modules(self, client):
        project = client.post("/api/v1/projects", json={"name": "Test"}).json()
        content = json.dumps(SAMPLE_BLIP).encode()
        upload = client.post(
            "/api/v1/upload",
            data={"project_id": project["id"], "flow_type": "whatsapp"},
            files={"file": ("flow.json", content, "application/json")},
        ).json()

        response = client.get(f"/api/v1/modules?flow_id={upload['flow_id']}")
        assert response.status_code == 200
        assert len(response.json()) > 0

    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
