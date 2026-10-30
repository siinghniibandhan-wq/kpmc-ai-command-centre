# KPMC AI Command Centre

A lightweight, single-user workspace for AI-assisted software development and automation across approved projects.

## Product principles
- Simple, responsive interface with minimal visual clutter.
- Human approval before repository writes, pull requests, deployments, or external actions.
- Isolated project workspaces; no direct production database access.
- Provider-independent model adapter, starting with Gemini.
- Keep core application footprint small; temporary build workspaces are managed separately.

## Initial architecture
- Frontend: lightweight HTML/CSS/JavaScript prototype (no frontend framework or runtime dependency yet).
- Backend: FastAPI service.
- Agent orchestration: Google ADK behind a coordinator interface (planned).
- Model access: Gemini API through a server-side provider adapter (planned).
- Persistence: PostgreSQL for projects, tasks, runs, and audit events (planned).
- Repository access: GitHub integration with least-privilege permissions (planned).
- Execution: isolated worker/container per approved task (planned).

## Safety boundaries
- Never store API keys in frontend code or commit secrets.
- Do not connect to Super Bajaar production infrastructure or databases.
- No writes to a repository's default branch; work on feature branches and propose PRs.
- No deployment or production mutation without explicit human approval.
- Record task inputs, tool actions, outputs, and verification evidence.

## Current status
Initial UI and FastAPI health endpoint scaffold only. The task form is a placeholder; it does not yet create or execute tasks. No agents, model calls, repository automation, database integration, or deployment workflows are enabled.
