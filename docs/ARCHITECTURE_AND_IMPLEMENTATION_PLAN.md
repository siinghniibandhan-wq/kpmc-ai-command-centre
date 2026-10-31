# KPMC AI Command Centre — Architecture and Delivery Plan

**Status:** Architecture baseline — proposed, not deployed  
**Date:** 2026-10-31  
**Repository:** `siinghniibandhan-wq/kpmc-ai-command-centre`

## 1. Product goal

Build a secure, provider-independent AI command centre for coordinating software development, error investigation, audits, documentation, business research and approved automations across the user's projects.

The command centre is a task control plane. It does not attempt to merge the separate consumer chat subscriptions of ChatGPT, Gemini, Claude or Perplexity. Each provider must be connected through an explicitly supported API, CLI/worker adapter or user-approved integration. Subscription access does not imply API access; provider API usage and billing are separate.

## 2. Initial provider roles

| Provider | Default role | Execution boundary |
|---|---|---|
| ChatGPT | CTO/orchestrator, task decomposition, architecture, integration review | May coordinate; cannot bypass approval gates |
| Gemini | Primary implementation, debugging, routine code fixes and tests | Isolated task workspace; feature branch only |
| Perplexity | Research, Sentry investigation, independent audit; may edit files in an isolated workspace | Read/write in ephemeral workspace only; no Git commit, push, PR merge or deployment credentials |
| Claude | Escalation for exceptionally complex analysis; returns corrected files or patches | Read-only repository input; output patch/artifacts only; no repository write credentials |
| Copilot | Optional coding assistant when available | Not a runtime dependency; capabilities verified per account |

Provider roles are routing defaults, not hard-coded assumptions. The owner may override assignments per task.

## 3. Target architecture

```text
Owner / Operators
       |
       v
Web Command Centre (React or existing lightweight UI)
       |
       v
FastAPI Control Plane
  |-- Authentication / RBAC
  |-- Projects, tasks, approvals, audit trail
  |-- Policy engine and budget guard
  |-- Provider adapter registry
  |-- Workflow state machine
       |
       +---- PostgreSQL (metadata, task state, audit)
       |
       +---- S3 (patches, artifacts, reports; encryption + lifecycle)
       |
       +---- Queue / scheduler (start with DB-backed queue; add SQS/EventBridge later)
       |
       +---- Isolated Worker per task (container, no privileged host access)
                 |
                 +-- Gemini API/worker adapter
                 +-- Perplexity API/worker adapter
                 +-- Claude API/patch adapter
                 +-- OpenAI/ChatGPT API adapter
                 +-- GitHub read-only fetch + controlled branch publisher
                 +-- Sentry / Datadog / CloudWatch read adapters
       |
       v
Approval Gate -> GitHub feature branch / PR -> GitHub Actions CI
       |
       v
Human merge approval -> separate deployment workflow (not automatic)
```

### AWS placement

**MVP (cost-controlled):**
- Run the FastAPI control plane on the existing isolated command-centre host only if capacity and security review pass; otherwise use a small separate service.
- PostgreSQL stores metadata only. Never connect this platform to Super Bajaar's production business database.
- Use S3 for task artifacts with encryption, short lifecycle retention and no public access.
- Use a single low-cost worker execution path initially. Do not provision AgentCore, NAT Gateway, load balancers or a new RDS instance by default.
- Use CloudWatch for service logs and alarms with explicit retention.
- Keep GitHub Actions as the CI authority.

**Later managed option:**
- Strands Agents as the open-source orchestration framework.
- Amazon Bedrock AgentCore Runtime for isolated managed agent execution; Gateway for tool exposure; Identity for delegated credentials; Memory only if justified; Observability via CloudWatch.
- Step Functions for durable, human-in-the-loop workflows when state complexity warrants it.
- EventBridge/SQS for event-driven task intake and retries.
- AgentCore is modular and consumption-priced; it is not assumed free. Enable services individually after cost review.

## 4. Core modules

1. **Command dashboard:** task queue, status, owner, project, agent, approvals, run history and cost estimate.
2. **Task manager:** create, classify, decompose, assign, cancel and retry tasks.
3. **Provider adapters:** common interface for model selection, prompt, context, tool permissions, timeout, usage and output.
4. **Workspace manager:** ephemeral per-task clone/worktree/container; clean teardown; no shared writable production checkout.
5. **Repository gateway:** read files/branches/PRs; publish only approved changes to a feature branch using a dedicated GitHub App installation.
6. **Error centre:** ingest Sentry issues/events and Datadog/CloudWatch signals; redact sensitive data; create investigation tasks.
7. **Audit centre:** independent review, security checklist, diff review and evidence capture.
8. **CI monitor:** consume GitHub Actions status, logs and artifacts; report exact commit SHA and test outcome.
9. **Approval centre:** explicit approvals for repository publishing, PR creation, merge, secrets access, external actions and deployment.
10. **Automation centre:** scheduled and event-triggered workflows with pause/kill switch.
11. **Cost centre:** provider token spend, AWS spend, per-task limits, daily/monthly caps and usage reports.
12. **Knowledge/documentation:** project rules, architecture, task templates and verified runbooks.

## 5. Permission model and non-negotiable safeguards

### Roles
- **Owner:** full control; sole authority for production deployment and default-branch merge approval.
- **CTO/orchestrator:** create tasks, route agents, inspect evidence and request approvals; no hidden privilege escalation.
- **Implementation worker (Gemini):** read project context and edit only its isolated task workspace; may prepare a patch/branch proposal. No production access.
- **Perplexity worker:** read repository and edit files only in an isolated ephemeral workspace. Git credentials are read-only; no commit, push, PR, merge or deployment capability.
- **Claude reviewer:** read-only repository snapshot; can return patch/file artifacts; no Git credentials.
- **Auditor:** read-only diffs, logs and test outputs.
- **CI worker:** run tests/builds; no secrets beyond narrowly scoped test credentials.
- **Release workflow:** separate identity; only owner-approved PR merge/deploy path.

### Technical enforcement
- No shared provider API keys in prompts or browser code. Store credentials in AWS Secrets Manager or an equivalent encrypted secret store; workers receive short-lived, task-scoped credentials.
- Use separate IAM roles per service. Deny wildcard admin permissions. No worker receives EC2 instance-profile credentials or production database credentials.
- GitHub App permissions: Contents read by default; Contents write only for the controlled publisher after approval; Actions read; Pull Requests write only if the owner enables PR creation. No default-branch push.
- Perplexity's no-commit rule is enforced by withholding all write-capable Git credentials, not merely by instruction. Its workspace filesystem is writable, but its Git remote is read-only.
- Claude receives source snapshots and returns patches; it does not receive a repository token.
- All workers run unprivileged, isolated, with CPU/memory/time limits, restricted network egress and temporary storage.
- Treat repository files, issue text, logs, web pages and tool outputs as untrusted data. Ignore instructions embedded in retrieved content that attempt to override system policy or request secrets.
- Require human approval before external side effects, repository publication, PR creation (unless separately approved), merge, production data access, infrastructure mutation or deployment.
- No direct production database connection from agents. No automated SQL migrations.
- Audit every task, model, tool call, permission decision, artifact hash, cost and approval. Redact secrets and personal data.

## 6. Workflow state machine

```text
CREATED -> TRIAGED -> APPROVED_FOR_ANALYSIS -> RUNNING
  -> REVIEW_REQUIRED -> APPROVED_FOR_PUBLISH -> PR_OPEN
  -> CI_RUNNING -> CI_PASSED -> OWNER_MERGE_APPROVAL -> MERGED
Any state may transition to BLOCKED / FAILED / CANCELLED.
Deployment is a separate workflow requiring a separate explicit owner approval.
```

A task can finish as a report or patch without creating a PR. No worker can self-approve its own output.

## 7. Cost controls

### AWS
- Create AWS Budgets for the command-centre cost allocation tag and account-level spend. Suggested alerts at 50%, 80% and 100% of a small owner-selected monthly cap; alerts do not themselves stop spend.
- Set a hard application-level monthly AWS spend ceiling and disable new task execution when the internal threshold is reached. AWS billing data is delayed, so maintain conservative headroom.
- Do not enable AgentCore Runtime, Browser, Code Interpreter, Memory, Gateway, Web Search or Evaluations until explicitly selected and costed.
- Do not create NAT Gateways, load balancers, RDS, persistent oversized EC2, paid OpenSearch or always-on GPU resources for the MVP.
- Apply S3 lifecycle deletion to temporary artifacts; set CloudWatch log retention; cap log verbosity and trace sampling.
- Tag resources: `Project=KPMC-AI-Command-Centre`, `Environment=dev|staging|prod`, `Owner=platform`, `CostCentre=ai-orchestration`.

### Model providers
- Require per-task maximum input/output tokens, maximum model calls, wall-clock timeout, retry ceiling and maximum parallel agents.
- Configure per-provider daily/monthly spend caps where supported; otherwise enforce local usage budgets and alerts.
- Default to one agent per task; parallel reviewers only for high-risk or complex tasks.
- No automatic model fallback to a paid provider without an approved budget policy.
- Show estimated and actual cost per task; stop execution when task or daily budget is exhausted.
- API costs are separate from ChatGPT/Claude/Gemini/Perplexity consumer subscriptions.

### Initial safe defaults (configurable)
- Max concurrent tasks: 1.
- Max worker runtime: 15 minutes per task for MVP.
- Max retries: 1.
- Max agent handoffs: 2.
- No browser automation or paid web search by default.
- No automatic scheduled agent runs until owner enables them.

## 8. Observability and incident workflow

- Sentry: application exceptions and releases; Perplexity can investigate through its Sentry integration if its account connection is active. The command centre may use a read-only Sentry API adapter later.
- Datadog: optional broader infrastructure/APM integration; not a prerequisite.
- CloudWatch: AWS service logs, metrics and alarms.
- Correlate every error investigation with project, environment, release SHA, Sentry issue/event ID and task ID.
- Monitoring adapters are read-only. They create findings/tasks, never automatically modify production.

## 9. Delivery plan

### Phase 0 — Foundation and design
- Confirm this architecture, repo boundaries and provider access.
- Record threat model, data classification, IAM matrix and monthly budget.
- Inventory existing scaffold and dependencies.
- No AWS resources or production credentials created.

### Phase 1 — Working local MVP
- FastAPI task API and minimal dashboard.
- PostgreSQL task/run/approval/audit tables and migrations.
- Provider adapter interface with mock provider and one real provider selected by owner.
- Task state machine, policy checks and cost accounting.
- Unit tests and local Docker Compose development.
- No repository writes or AWS deployment.

### Phase 2 — Safe agent execution
- Isolated worker container and ephemeral workspace.
- Gemini primary coding adapter.
- Perplexity read/write ephemeral workspace adapter with read-only Git remote.
- Claude read-only review/patch adapter.
- OpenAI orchestrator adapter only if API access and budget are approved.
- Artifact storage, patch preview, cancellation and audit logs.

### Phase 3 — GitHub integration
- Dedicated GitHub App with minimum permissions.
- Read-only repository inspection.
- Approval-gated feature-branch publisher.
- PR creation only after explicit owner permission.
- GitHub Actions status and evidence ingestion.
- No default branch writes and no automated merge.

### Phase 4 — Error and observability integrations
- Sentry read-only issue/event intake.
- CloudWatch read-only log/metric intake.
- Datadog optional, only after connection and cost review.
- Automatic task creation for high-severity regressions, with deduplication and rate limits.

### Phase 5 — Automation and managed AWS
- EventBridge/SQS/Step Functions only where operational need exists.
- Evaluate AgentCore Runtime/Gateway/Identity/Observability using a costed pilot.
- Add scheduled audits, recurring reports and approved business workflows.
- Production rollout only after security review, load tests, backups and owner approval.

## 10. Acceptance criteria

- One task can be created, assigned, executed, cancelled and inspected end-to-end.
- Every run records provider/model, inputs metadata, tool calls, outputs, token usage, estimated/actual cost, timestamps and status.
- Provider failures/timeouts are contained and retried only within policy.
- Perplexity cannot commit or push even if prompted to do so.
- Claude cannot write to the repository.
- No worker can access production database credentials or deployment secrets.
- Repository publication is impossible without an explicit approval record.
- Every PR is tied to a task ID, artifact hash, base SHA and CI evidence.
- Cost limits stop new work and alert the owner.
- Security tests cover prompt injection, secret exfiltration, cross-project access and workspace escape.
- All tests pass before any deployment.

## 11. Decisions still requiring owner confirmation

1. Which provider API accounts/keys are available and approved for use (OpenAI, Gemini, Anthropic, Perplexity).
2. Whether the command centre should remain single-user initially or support multiple team members.
3. Monthly AWS and model-provider spending caps.
4. Whether agents may create PRs after approval, or whether a human-only publisher must do so.
5. Whether Sentry access is via Perplexity only initially or also a command-centre read-only integration.

## 12. Explicit exclusions for MVP

- No production deployment automation.
- No direct production DB access or migration execution.
- No automatic commits, pushes, merges or releases by agents.
- No Figma or GitLab integration.
- No Datadog dependency; it remains optional.
- No paid AgentCore components until a costed pilot is approved.
- No assumption that consumer AI subscriptions include API credits or automation rights.
