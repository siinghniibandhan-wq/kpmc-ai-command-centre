from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .planner import create_task_plan
from .schemas import PlanRequest

settings = get_settings()

app = FastAPI(
    title="KPMC AI Command Centre",
    version="0.2.0",
    description="Single-user AI development command centre API.",
)

origins = [item.strip() for item in settings.cors_allowed_origins.split(",") if item.strip()]
if origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )


@app.get("/api/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "kpmc-ai-command-centre"}


@app.post("/api/v1/plans", tags=["planning"])
async def create_plan(request: PlanRequest) -> dict:
    try:
        plan = create_task_plan(request)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="The planning request could not be completed. Check backend Gemini configuration and logs.",
        ) from exc
    return {
        "status": "awaiting_approval",
        "model": settings.gemini_model,
        "plan": plan.model_dump(),
        "execution_started": False,
    }
