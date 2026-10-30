from fastapi import FastAPI

app = FastAPI(
    title="KPMC AI Command Centre",
    version="0.1.0",
    description="Single-user AI development command centre API.",
)


@app.get("/api/health", tags=["system"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "kpmc-ai-command-centre"}
