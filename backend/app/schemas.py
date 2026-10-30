from typing import Literal

from pydantic import BaseModel, Field, field_validator


AgentRole = Literal[
    "coordinator",
    "backend",
    "frontend",
    "database",
    "security",
    "qa",
    "devops",
    "research",
    "github",
]


class PlanRequest(BaseModel):
    task: str = Field(min_length=10, max_length=12000)
    project_context: str | None = Field(default=None, max_length=6000)


class PlannedTask(BaseModel):
    id: str = Field(min_length=1, max_length=20)
    title: str = Field(min_length=3, max_length=140)
    role: AgentRole
    description: str = Field(min_length=10, max_length=2000)
    depends_on: list[str] = Field(default_factory=list)
    priority: Literal["critical", "high", "medium", "low"] = "medium"
    expected_output: str = Field(min_length=3, max_length=500)
    requires_approval: bool = True


class TaskPlan(BaseModel):
    summary: str = Field(min_length=10, max_length=1200)
    assumptions: list[str] = Field(default_factory=list, max_length=12)
    tasks: list[PlannedTask] = Field(min_length=10, max_length=20)

    @field_validator("tasks")
    @classmethod
    def validate_task_graph(cls, tasks: list[PlannedTask]) -> list[PlannedTask]:
        ids = [task.id for task in tasks]
        if len(ids) != len(set(ids)):
            raise ValueError("Task IDs must be unique.")
        known = set(ids)
        for task in tasks:
            unknown = set(task.depends_on) - known
            if task.id in task.depends_on or unknown:
                raise ValueError(f"Invalid dependencies for task {task.id}.")
        return tasks
