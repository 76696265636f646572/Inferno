# Inferno — Implementation TODO

**Product:** Inferno — your local AI control plane  
**North star:** Search Hugging Face → download GGUF → register → start llama.cpp → call OpenAI-compatible API → observe metrics.

This file is the working plan. Complete items in order unless a later step is a hard dependency of an earlier one. Prefer a working golden-path over extra polish.

Design principles while implementing:

1. Prefer simple solutions.
2. Avoid unnecessary dependencies.
3. Keep modules loosely coupled.
4. Prefer production-safe defaults.
5. Make local development easy.
6. Make Docker deployment straightforward.
7. Keep the MVP achievable.
8. Do not introduce Redis/Kafka/distributed infra unless actually needed.
9. Do not put business logic in FastAPI route handlers.
10. Do not make the whole app llama.cpp-specific; use runtime and source abstractions.

---

## Phase 0 — Repository and project foundation

### 0.1 Create monorepo layout

**Description:** Initialize the repository structure so frontend and backend are independently testable and deployable.

```text
inferno/
├── frontend/
├── backend/
├── docker/
├── docker-compose.yml
├── .env.example
├── README.md
└── LICENSE
```

Include `frontend/` Nuxt directories (`pages`, `components`, `composables`, `stores`, `layouts`, `middleware`, `assets`) and `backend/app/` modules (`api/v1`, `core`, `db`, `models`, `schemas`, `services`, `sources`, `runtimes`, `workers`, `websocket`). Add `backend/migrations/` and `backend/tests/`.

### 0.2 Add license, gitignore, and editor defaults

**Description:** Add MIT (or chosen OSS) `LICENSE`, root `.gitignore` covering Python/Node/Docker/models, and basic editor/CI ignore rules. Do not ignore `.env.example`.

### 0.3 Define typed backend configuration

**Description:** Create Pydantic Settings in `backend/app/core/config.py` loaded from environment variables. Cover `APP_NAME`, `ENVIRONMENT`, `DATABASE_URL`, `MODEL_STORAGE_PATH`, `LLAMA_CPP_BINARY`, `HF_TOKEN`, `AUTH_ENABLED`, OIDC fields, CORS, bind host/port, and log level. Provide `.env.example` with safe local defaults (`AUTH_ENABLED=false`, SQLite-capable URL, `/models`).

### 0.4 Database layer (SQLAlchemy 2 + Alembic)

**Description:** Set up async SQLAlchemy 2 engine/session, Alembic migrations, and dual-database support: PostgreSQL (`asyncpg`) for production and SQLite for local/dev tests. Use UUID primary keys. Keep session/lifecycle helpers out of route handlers.

### 0.5 FastAPI application skeleton

**Description:** Create `backend/app/main.py` with lifespan, CORS, structured logging, request-id middleware, and a versioned `/api/v1` router. Do not put business logic in handlers. Add health/readiness endpoints. Ensure OpenAPI tags exist from day one: Models, Downloads, Runtimes, Inference, Analytics, Authentication, API Keys, System.

### 0.6 Structured errors and logging

**Description:** Define a consistent error envelope (`error.code`, `error.message`) and exception handlers. Add structured JSON logging with request/runtime/model/download IDs and duration. Never log API secrets, OIDC client secrets, full API keys, or prompt/completion content by default.

### 0.7 Nuxt 4 application shell

**Description:** Scaffold Nuxt 4 + Vue 3 + TypeScript + Nuxt UI. Implement dark-first theme with restrained orange accent, light theme support, persistent sidebar, collapsible nav, and top header for system health. Navigation:

- Overview
- Models
- Downloads
- Runtimes
- Analytics → Requests / Tokens / Performance
- API
- Settings → General / Storage / Authentication / API Keys

### 0.8 Shared frontend primitives

**Description:** Build reusable Nuxt UI-based components used across pages: `AppSidebar`, `AppHeader`, `StatusBadge`, `MetricCard`, `MetricGrid`, `ChartCard`, `EmptyState`, `ConfirmDialog`. Add toast, skeleton, empty, and error patterns. Do not duplicate page-level UI logic.

### 0.9 Docker and local run path

**Description:** Add `docker-compose.yml` for `frontend`, `backend`, and `postgres`. Mount a persistent models volume (never bake GGUF files into images). GPU support must be optional, not required. Document `make`/`pnpm`/`uv` (or equivalent) commands so the stack runs locally without Docker as well.

---

## Phase 1 — Working foundation (must run locally)

Goal: registry + runtime manager + start/stop + `/api/v1/models`. The app must already run.

### 1.1 Domain models and migrations

**Description:** Create SQLAlchemy models and Alembic migrations for the core entities:

- `User` (even if unused until auth)
- `Model`
- `ModelFile`
- `ModelSource`
- `DownloadJob`
- `RuntimeInstance`
- `RuntimeConfig`
- `ApiKey`
- `RequestMetric`
- `SystemMetric`
- `AuditLog`

Models and model files are separate. A model can own multiple GGUF quantizations. Add indexes for common lookups (model name, file status, runtime status, metric timestamps).

Suggested `Model` fields: `id`, `name`, `display_name`, `description`, `architecture`, `parameter_count`, `context_length`, `source_type`, `source_url`, `repository`, `author`, `tags`, `created_at`, `updated_at`.

Suggested `ModelFile` fields: `id`, `model_id`, `filename`, `local_path`, `size_bytes`, `sha256`, `quantization`, `download_status`, `created_at`.

### 1.2 Model registry service

**Description:** Implement `ModelManager` / registry service that creates, updates, lists, and deletes models and files. Canonical paths live in the database. Do **not** scan the filesystem on every request. Restrict all paths to `MODEL_STORAGE_PATH`. Prevent path traversal, arbitrary output paths, and overwriting unrelated files. A model is not usable until a verified file exists.

### 1.3 Runtime abstraction

**Description:** Define a `Runtime` protocol (`start`, `stop`, `restart`, `status`, `logs`) under `backend/app/runtimes/`. Implement only `LlamaCppRuntime`. Keep room for future `VLLMRuntime`, `OllamaRuntime`, `MLXRuntime` without implementing them. Do not leak llama.cpp-specific types into the rest of the API surface.

### 1.4 Llama.cpp runtime manager

**Description:** Implement process management for `llama-server`:

- Start / stop / restart
- Health checks against the local HTTP endpoint
- Port allocation
- PID / process tracking
- Crash detection and state sync
- Resource-aware validation before start

Never use `shell=True`. Always construct argv arrays. Persist `RuntimeConfig` in the database (`model`, `context_size`, `gpu_layers`, `batch_size`, `threads`, `parallel`, `flash_attention`, `host`, `port`).

Runtime states: `stopped`, `starting`, `running`, `stopping`, `unhealthy`, `crashed`, `error`.

Startup flow: validate model → validate config → validate resources → allocate port → start process → wait for health → mark healthy → notify UI.

### 1.5 Runtime API and Models API

**Description:** Expose REST endpoints to list/register models, list files, start/stop/restart runtimes, and fetch runtime status. Group under OpenAPI tags `Models` and `Runtimes`. Return typed Pydantic response models, not raw dicts.

### 1.6 OpenAI models listing (minimum)

**Description:** Implement `/api/v1/models` so registered, runnable models appear in an OpenAI-compatible catalog. Full chat/completions come in Phase 3; this listing is required for the foundation to feel API-first.

### 1.7 Frontend: Models list, model detail, runtimes

**Description:** Build:

- Models list/table with status
- Model detail page (overview, metadata, runtime, actions)
- Runtimes page with cards (health, port, PID, uptime, GPU layers, context, actions)

Dangerous actions (`Stop`, `Delete`, `Restart`) use confirmation dialogs. Empty state for no models: “Find a model on Hugging Face…” with a browse CTA (can link to a placeholder until Phase 2).

### 1.8 WebSocket skeleton

**Description:** Add `/ws` with a typed event model. At this phase, emit `runtime.status` events. Keep the protocol generic so downloads, logs, system status, and request activity can reuse the same channel later.

### 1.9 Phase 1 tests

**Description:** Backend tests for model creation/lookup, runtime command construction, runtime lifecycle (mocked process), and `/api/v1/models`. Frontend tests for model list, model detail, runtime state, and dashboard shell loading. No superficial coverage padding.

**Phase 1 exit criteria:** A developer can run Inferno locally, register a local GGUF (even if via API/fixture), start/stop llama-server, and see the runtime turn healthy in the UI.

---

## Phase 2 — Model discovery and downloads

Goal: Hugging Face search, inspect GGUF files, background download with live progress, verify, register.

### 2.1 Model source abstraction

**Description:** Define `ModelSource` protocol: `search`, `inspect`, `list_files`, `download`. Implement `HuggingFaceSource` and `DirectURLSource`. Leave room for GitHub/S3/Local/CustomRegistry later. Isolate network I/O behind the interface so tests can mock it.

### 2.2 Hugging Face search and inspect API

**Description:** Backend endpoints to search HF, inspect a repo, list GGUF files, and extract quantization/size/SHA metadata. Honor `HF_TOKEN` for private/gated repos. Validate filenames, URLs, file types, and sizes before queueing a download.

### 2.3 Hugging Face browser UX

**Description:** Dedicated discovery page: search box, repo cards (architecture, params, author), GGUF table (quant, size, download). Show useful metadata. Warn when disk space is insufficient. Support gated/private repos when a token is configured.

### 2.4 Download job system

**Description:** Background download worker (asyncio tasks; no Redis). States: `queued`, `downloading`, `verifying`, `registering`, `completed`, `cancelled`, `failed`.

Support:

- Resumable downloads
- Cancel / retry
- Concurrent downloads + queue
- Speed, ETA, progress
- Disk-space checks
- SHA256 verification
- Atomic install: write `filename.gguf.part`, rename to `filename.gguf` only after validation

Do not block the FastAPI event loop with filesystem/network I/O. The registry must not mark a file usable until the final verified GGUF exists.

### 2.5 Download dashboard

**Description:** Downloads page with Active / Queued / Completed / Failed / Cancelled. Active cards show progress bar, bytes, speed, ETA, pause/cancel. Failed jobs can retry.

### 2.6 Live download events

**Description:** Push typed WebSocket events, e.g. `download.progress` with `job_id`, `bytes_downloaded`, `bytes_total`, `speed`, `percentage`. UI updates without polling as the primary path.

### 2.7 Model storage layout

**Description:** Default `MODEL_STORAGE_PATH=/models` with a predictable layout (e.g. `/models/{author}/{repo}/{quant}.gguf`). Database stores canonical paths; do not require a scan to know what is installed.

### 2.8 Phase 2 tests

**Description:** Tests for HF provider (mocked HTTP), download lifecycle, cancellation, SHA256 verification, disk-space rejection, path-traversal rejection, and frontend download state. Use fixtures, not live multi-GB downloads, in CI.

**Phase 2 exit criteria:** User can search “Qwen GGUF”, open a repo, download Q4_K_M, watch live progress, see SHA256 verification, and find the model registered and ready to start.

---

## Phase 3 — Inference gateway

Goal: OpenAI-compatible chat/completions with streaming, API keys, routing, and runtime health.

### 3.1 API key service

**Description:** Keys have `id`, `name`, `prefix`, `hash`, `created_at`, `last_used_at`, `revoked_at`. Never store the full secret. Create / revoke / delete. Show the secret once after creation. Hash with a strong one-way function.

### 3.2 API key UI

**Description:** Settings → API Keys table, create dialog, one-time secret reveal, revoke/delete with confirmation.

### 3.3 Model routing

**Description:** Resolve `model` name → registered model → verified model file → healthy runtime instance → llama-server. Do not expose raw llama.cpp ports to external clients unless explicitly configured.

### 3.4 OpenAI-compatible inference API

**Description:** Implement:

- `POST /api/v1/chat/completions`
- `POST /api/v1/completions`
- existing `GET /api/v1/models`

Behave like OpenAI enough for Open WebUI, Continue, Python OpenAI SDK, and similar clients. Support streaming. Validate requests, enforce size limits and timeouts.

### 3.5 Gateway cross-cutting concerns

**Description:** API key auth (when keys exist / when auth policy requires them), rate limiting, request logging (metadata only), error mapping to the structured error envelope, and runtime health gating (fail clearly if no healthy runtime).

### 3.6 API page in the dashboard

**Description:** Document base URL, example curl/SDK snippets, available models, and how to use a key. This is product UX, not just FastAPI docs.

### 3.7 Phase 3 tests

**Description:** Tests for API key hashing/auth, model routing, OpenAI request/response shape, streaming, missing/unhealthy runtime, and revoked keys. Mock llama-server HTTP rather than requiring a GPU.

**Phase 3 exit criteria:** With a running runtime, a client can send a streaming chat completion using an Inferno API key and receive a valid OpenAI-compatible response.

---

## Phase 4 — Observability

Goal: request/token/runtime metrics, dashboard, charts, live logs.

### 4.1 Request metrics capture

**Description:** Record every inference request: `request_id`, `timestamp`, `model`, `runtime_id`, `user_id`, `api_key_id`, `endpoint`, `status`, `duration_ms`, `ttft_ms`, `input_tokens`, `output_tokens`, `total_tokens`, `tokens_per_second`, `error`. For streaming, capture TTFT and token timing. Do **not** store prompt/completion content by default. If optional request logging is added later, make privacy implications explicit in Settings.

### 4.2 System monitoring abstraction

**Description:** Collect CPU, RAM, disk, and optional GPU (utilization, memory, temperature). NVIDIA support where available; never require NVIDIA. Keep a pluggable monitor interface so other GPU backends can be added later. Persist sampled `SystemMetric` rows for dashboard ranges.

### 4.3 Overview dashboard

**Description:** Answer immediately: what is installed, what is running, hardware use, inference performance.

Metric cards: Requests, Tokens, Tokens/sec, Avg latency, TTFT, Active models, Running runtimes, Errors.

Hardware: GPU util, GPU memory, CPU, RAM, Disk.

Graphs with ranges `1h / 6h / 24h / 7d / 30d`: requests, tokens, requests by model, I/O token ratio, latency, TTFT, tokens/sec, errors, GPU util, GPU memory.

Header shows live health: system status, GPU, CPU, RAM.

### 4.4 Analytics pages

**Description:**

- **Requests:** totals, success/fail, by model, by endpoint, over time
- **Tokens:** input/output/total, by model, over time
- **Performance:** avg latency, P50/P95/P99, TTFT, tokens/sec

Filters: model, runtime, API key, time range, status. Use a modern charting library already compatible with Vue/Nuxt; do not add extra frontend frameworks.

### 4.5 Live runtime logs

**Description:** Stream llama-server logs over WebSocket to a terminal-style `RuntimeLogs` component on runtime and model detail pages.

### 4.6 Model detail performance section

**Description:** Per-model requests, tokens, tokens/sec, TTFT, latency, errors — sourced from `RequestMetric`, not ad-hoc counters.

### 4.7 Live activity events

**Description:** Extend `/ws` with system status and request activity events so the header and overview stay fresh without heavy polling.

### 4.8 Phase 4 tests

**Description:** Tests that a mocked inference request records metrics (including streaming TTFT), analytics aggregations, and dashboard loading. Frontend tests for dashboard and metric empty/error states.

**Phase 4 exit criteria:** After a chat completion, Analytics and Overview show the request, tokens/sec, latency, and TTFT. Runtime logs are visible live.

---

## Phase 5 — Authentication, roles, and audit

Goal: optional OIDC, sessions, users, roles, audit log. Local-first when auth is off.

### 5.1 Optional auth switch

**Description:** `AUTH_ENABLED=false` keeps local use frictionless (no login wall). When enabled, protect dashboard and mutating APIs. Inference API keys remain the client credential for OpenAI endpoints.

### 5.2 Generic OIDC

**Description:** `OIDC_ENABLED` + issuer/client id/secret. Use discovery; Authorization Code flow; PKCE where appropriate. No Keycloak-specific hard-coding. Sessions, logout, and basic user identity persistence.

### 5.3 Roles and authorization

**Description:** Basic roles (e.g. admin/operator/viewer) for start/stop, downloads, settings, and API key management. Enforce on the backend; UI only hides what the API already rejects.

### 5.4 Settings pages

**Description:** General, Storage, Authentication, API Keys. Storage must explain `MODEL_STORAGE_PATH` and disk usage. Authentication must clearly explain what happens when OIDC is on vs off.

### 5.5 Audit log

**Description:** Record `login`, `logout`, `model_download`, `model_delete`, `runtime_start`, `runtime_stop`, `runtime_restart`, `api_key_create`, `api_key_revoke`, `settings_change`. Do not log secrets. Provide a simple Settings or System view of recent audit events.

### 5.6 Phase 5 tests

**Description:** Tests for auth-disabled vs enabled paths, OIDC callback handling (mocked IdP), session/logout, role checks, and audit events on sensitive actions.

**Phase 5 exit criteria:** Inferno still runs with auth off. With OIDC on, a user can log in, manage models/runtimes, and sensitive actions appear in the audit log.

---

## Cross-cutting work (apply in every phase)

### C.1 Security defaults

**Description:** Argument-array process spawning, storage-path jail, download URL/filename/type/size/checksum validation, API authz, rate limits, request size limits, timeouts. Treat this as a control plane that downloads arbitrary files and starts local processes.

### C.2 UX quality bar

**Description:** Skeleton loading, safe optimistic UI, toasts, empty/error/retry states, confirmation dialogs, tooltips on technical llama.cpp parameters, keyboard-friendly controls, responsive collapse of the sidebar. Dark mode must be excellent.

### C.3 OpenAPI cleanliness

**Description:** Keep tags, response models, and examples accurate as endpoints land. No untyped dict dumps.

### C.4 Performance under load

**Description:** UI and API stay responsive while a 50+ GB download, llama-server, inference traffic, and dashboard updates run together. Background workers for blocking I/O.

### C.5 Documentation

**Description:** README: what Inferno is, architecture diagram, local dev, Docker, GPU-optional notes, env vars, golden-path walkthrough, and security warnings about binding to public interfaces.

---

## Golden-path acceptance checklist

Use this as the final integration gate. Every box must work for real, not as a stub.

- [ ] Open Inferno dashboard
- [ ] Browse Hugging Face
- [ ] Search “Qwen GGUF”
- [ ] Open repository
- [ ] Choose a Q4_K_M (or similar) GGUF
- [ ] Click Download
- [ ] See real-time progress (bytes, speed, ETA)
- [ ] Download completes
- [ ] SHA256 verified
- [ ] Model registered and marked usable
- [ ] Open model detail
- [ ] Configure llama.cpp
- [ ] Click Start
- [ ] llama-server launches (no `shell=True`)
- [ ] Health check succeeds
- [ ] Runtime shows Healthy
- [ ] Create API key (secret shown once)
- [ ] Call `/api/v1/chat/completions` (streaming)
- [ ] Receive streamed response
- [ ] Request appears in Analytics
- [ ] Tokens/sec, latency, and TTFT are visible

---

## Explicit non-goals (do not do yet)

- vLLM, Ollama, or MLX runtimes
- GitHub / S3 / custom registry sources (interfaces only)
- Redis, Kafka, or other distributed queues
- Storing prompts/completions by default
- Hard-coded Keycloak behavior
- Shipping GGUF files inside Docker images
- A generic CRUD admin aesthetic
- Visual “fire/gaming” theming beyond a restrained orange accent
