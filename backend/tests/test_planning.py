import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import PlannedTask, TaskPlan

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_plan_rejects_duplicate_task_ids():
    task = PlannedTask(
        id="T01",
        title="Inspect repository",
        role="research",
        description="Inspect the repository structure and identify relevant components.",
        expected_output="Repository inspection notes",
    )
    with pytest.raises(ValueError, match="unique"):
        TaskPlan(summary="A valid planning summary.", tasks=[task] * 10)


def test_plan_requires_ten_to_twenty_tasks():
    task = PlannedTask(
        id="T01",
        title="Inspect repository",
        role="research",
        description="Inspect the repository structure and identify relevant components.",
        expected_output="Repository inspection notes",
    )
    with pytest.raises(ValueError):
        TaskPlan(summary="A valid planning summary.", tasks=[task] * 9)


def test_plan_endpoint_rejects_short_input():
    response = client.post("/api/v1/plans", json={"task": "short"})
    assert response.status_code == 422
