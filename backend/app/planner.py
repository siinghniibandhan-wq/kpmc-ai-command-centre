import json

from google import genai
from google.genai import types

from .config import get_settings
from .schemas import PlanRequest, TaskPlan
from .security import get_gemini_api_key


SYSTEM_INSTRUCTIONS = """
You are the planning coordinator for KPMC AI Command Centre.
Convert the user's request into 10 to 20 small, concrete, ordered work items.
Use only these specialist roles: coordinator, backend, frontend, database, security,
qa, devops, research, github. Identify dependencies using task IDs. Tasks without
dependencies may run in parallel. Include discovery and verification work where
appropriate. Do not claim that work has been executed. Every task must require human
approval before repository writes, deployments, production changes, or external actions.
Never request secrets, access production databases, or suggest writing directly to a
default Git branch. Return only data matching the supplied structured schema.
"""


def create_task_plan(request: PlanRequest) -> TaskPlan:
    settings = get_settings()
    client = genai.Client(api_key=get_gemini_api_key())
    prompt = (
        f"{SYSTEM_INSTRUCTIONS}\n\nUSER TASK:\n{request.task}\n\n"
        f"PROJECT CONTEXT:\n{request.project_context or 'Not supplied'}"
    )
    response = client.models.generate_content(
        model=settings.gemini_model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TaskPlan,
            temperature=0.2,
        ),
    )
    raw = response.text
    if not raw:
        raise ValueError("Gemini returned an empty planning response.")
    return TaskPlan.model_validate(json.loads(raw))
