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
    try:
        TaskPlan(summary="A valid planning summary.", tasks=[task, task])
    except ValueError as exc:
        assert "unique" in str(exc)
    else:
        raise AssertionError("Duplicate task IDs must be rejected.")


def test_plan_requires_ten_to_twenty_tasks():
    response = client.post("/api/v1/plans", json={"task": "Fix the frontend task form"})
    assert response.status_code == 422
