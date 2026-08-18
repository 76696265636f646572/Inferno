# Inferno

**Your local AI control plane.**

Inferno is a self-hosted control plane for downloading, managing, running, and observing local AI models. The first inference runtime is [llama.cpp](https://github.com/ggml-org/llama.cpp) (`llama-server`).

> Manage. Run. Observe.

This repository is a monorepo. Phase 0 is the runnable foundation: FastAPI, the database layer, the Nuxt dashboard shell, and Docker. Model registry, downloads, inference, and metrics land in later phases — see [TODO.md](./TODO.md).

```text
                         ┌───────────────────────┐
                         │      Inferno UI       │
                         │      Nuxt + Nuxt UI   │
                         └───────────┬───────────┘
                                     │ REST / WebSocket
                                     ▼
                         ┌───────────────────────┐
                         │    Inferno API        │
                         │    FastAPI            │
                         └──────┬────────┬───────┘
                                │        │
                   ┌────────────┘        └───────────────┐
                   ▼                                     ▼
          ┌─────────────────┐                    ┌───────────────┐
          │ Model Manager   │                    │ Runtime       │
          └───────┬─────────┘                    └───────┬───────┘
                  ▼                                      ▼
          ┌─────────────────┐                    ┌───────────────┐
          │ Model Storage   │                    │ llama-server  │
          └─────────────────┘                    └───────────────┘
```

## Requirements

- Python 3.12+
- Node.js 22+
- [uv](https://docs.astral.sh/uv/) (backend)
- [pnpm](https://pnpm.io/) (frontend)
- Docker (optional, for Compose)
- PostgreSQL 16 (Compose) or SQLite (local default)

GPU is **optional**. The default Compose stack is CPU-only.

## Local development

```bash
cp .env.example .env
make install
```

In two terminals:

```bash
make backend    # http://localhost:8000  (OpenAPI at /docs)
make frontend   # http://localhost:3000
```

SQLite is the default database (`DATABASE_URL=sqlite+aiosqlite:///./inferno.db`). Models are stored under `MODEL_STORAGE_PATH` (default `./models`). Alembic migrations run automatically in development when `DATABASE_AUTO_MIGRATE=true`.

```bash
make test
make lint
make migrate
```

## Docker

```bash
cp .env.example .env
docker compose up --build
```

Services:

| Service    | URL                    | Notes                                      |
| ---------- | ---------------------- | ------------------------------------------ |
| Frontend   | http://localhost:3000  | Nuxt dashboard                             |
| Backend    | http://localhost:8000  | FastAPI, OpenAPI at `/docs`                |
| PostgreSQL | localhost:5432         | Internal to Compose; not published by default |

GGUF weights live in the `model_storage` volume. They are never baked into images.

Optional NVIDIA GPU reservation (does not change the CPU-only default):

```bash
docker compose -f docker-compose.yml -f docker/docker-compose.gpu.yml up --build
```

## Configuration

All infrastructure settings are environment variables. See [`.env.example`](./.env.example).

| Variable              | Default                                      | Purpose                          |
| --------------------- | -------------------------------------------- | -------------------------------- |
| `APP_NAME`            | `Inferno`                                    | Product name                     |
| `ENVIRONMENT`         | `development`                                | `development` / `production` / `test` |
| `DATABASE_URL`        | SQLite                                       | SQLAlchemy async URL             |
| `MODEL_STORAGE_PATH`  | `./models` (Compose: `/models`)              | GGUF storage jail                |
| `LLAMA_CPP_BINARY`    | `/usr/local/bin/llama-server`                | Runtime binary (Phase 1)         |
| `HF_TOKEN`            | empty                                        | Hugging Face (Phase 2)           |
| `AUTH_ENABLED`        | `false`                                      | Leave off for local use          |
| `OIDC_*`              | empty                                        | Generic OIDC (Phase 5)           |
| `NUXT_PUBLIC_API_BASE`| `http://localhost:8000`                      | Browser API origin               |

Secrets (`HF_TOKEN`, `OIDC_CLIENT_SECRET`, database passwords) are never written to logs.

## Security

Inferno downloads files and will start local processes. Treat a public bind as a production deployment:

- Do not expose the dashboard or API to the internet without authentication.
- Model storage is restricted to `MODEL_STORAGE_PATH`.
- Processes are started with argument arrays, never `shell=True`.
- Authentication is optional and off by default so local use stays frictionless.

## License

[MIT](./LICENSE)
