# KPMC AI Command Centre

A lightweight, single-user workspace for AI-assisted software development and automation across approved projects.

## Current milestone: Gemini task planning

- FastAPI endpoint: `POST /api/v1/plans`.
- Gemini generates a structured plan containing 10–20 specialist tasks.
- Roles include coordinator, backend, frontend, database, security, QA, DevOps, research and GitHub.
- The plan is returned with `awaiting_approval`; no code execution or repository mutation occurs.
- The static frontend renders the proposed plan.
- Gemini credentials are read from `GEMINI_API_KEY` for local development or AWS Systems Manager Parameter Store SecureString in hosted environments.
- The default model is `gemini-4-argon`, configurable with `GEMINI_MODEL`. Confirm API access and billing for the Google project before live use.

## Run locally

From `backend/`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
pytest
```

Serve the `frontend/` directory with any static web server. Set `window.KPMC_API_BASE_URL` to the backend URL before loading `app.js` when frontend and backend have different origins. Configure `CORS_ALLOWED_ORIGINS` on the backend to the exact frontend origin.

## AWS credential configuration

Set these backend environment variables:
- `AWS_REGION` (default `us-east-2`)
- `GEMINI_PARAMETER_NAME` (default `/kpmc-ai-command-centre/production/GEMINI_API_KEY`)
- `GEMINI_MODEL` (default `gemini-4-argon`)
- `CORS_ALLOWED_ORIGINS` (comma-separated exact origins)

The backend IAM role needs `ssm:GetParameter` on only the named parameter and the required KMS decrypt permission if a customer-managed key is used. Do not put the Gemini key in frontend code or commit it.

## Safety boundaries

- No Super Bajaar production infrastructure or database access.
- No default-branch repository writes.
- No deployment or production mutation without explicit approval.
- Planning is not execution; the current milestone does not run agents or modify repositories.
- Record task inputs, actions, outputs and verification evidence as persistence is added.

## Not yet implemented

Database persistence, task history, approval actions, GitHub repository operations, isolated execution workers, multi-agent execution, deployment automation and CI verification.
