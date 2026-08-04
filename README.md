# Kresh Energy — Backend (API)

REST API for the [Kresh Energy](https://ecosolaris.kresh-ng.de) solar-energy website
(German market). Built on **Django 6 + Django REST Framework**, it powers the public
marketing site, captures leads (quote requests & on-site inspection bookings), serves
admin-editable catalog content, and exposes an **AI assistant** endpoint.

[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Stack

| Layer        | Choice                                                             |
| ------------ | ----------------------------------------------------------------- |
| Language     | Python 3.14                                                        |
| Framework    | Django 6, Django REST Framework                                    |
| API docs     | drf-spectacular (OpenAPI 3, Swagger/Redoc)                         |
| Database     | PostgreSQL                                                         |
| Cache/queue  | Redis                                                              |
| Media        | Cloudflare R2 (S3-compatible) via django-storages — split buckets |
| Email        | Hostinger SMTP (SSL)                                               |
| AI assistant | OpenAI-compatible Chat Completions                                 |
| Edge         | Traefik + Let's Encrypt (production)                               |
| Runtime      | gunicorn + uvicorn worker                                          |
| Tooling      | uv, Ruff, mypy, pytest                                             |

## Domain model

- **`catalog`** — admin-editable marketing content, all with an `is_active` flag and
  DE/EN fields:
  - `Service`, `Project` (references/case studies), `FAQ`, `Testimonial`,
    `ServiceArea` (coverage), `CalculatorConfig` (drives the frontend savings
    calculator).
- **`leads`** — customer submissions:
  - `QuoteRequest` (+ `QuoteRoofPhoto`) with sensitive uploads (electricity bill,
    meter photo, roof photos); `InspectionBooking` (on-site visit scheduling).
- **`assistant`** — RAG-style sales/support chat: builds a system prompt from live
  catalog context and proxies to an OpenAI-compatible model, with a human-handoff
  message when it can't answer.

## API surface

All routes are under `/api/`. Reads are public; writes are public but rate-limited.

| Endpoint                     | Method   | Purpose                              |
| ---------------------------- | -------- | ------------------------------------ |
| `/api/services/`             | GET      | Active services                      |
| `/api/projects/`             | GET      | Reference projects                   |
| `/api/faqs/`                 | GET      | FAQs                                 |
| `/api/testimonials/`         | GET      | Testimonials                         |
| `/api/service-areas/`        | GET      | Coverage areas                       |
| `/api/calculator-config/`    | GET      | Savings-calculator parameters        |
| `/api/quotes/`               | POST     | Submit a quote request (+ photos)    |
| `/api/bookings/`             | POST     | Book an on-site inspection           |
| `/api/assistant/chat/`       | POST     | AI assistant chat turn               |
| `/api/schema/` `…/docs/`     | GET      | OpenAPI schema + Swagger UI          |

## Local development

Requires Docker + Docker Compose.

```bash
# Build & start the local stack (Django, Postgres, Redis, mailpit, docs)
docker compose -f docker-compose.local.yml up --build

# Create an admin user
docker compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser

# Seed catalog content (services, FAQs, projects, testimonials, service areas)
docker compose -f docker-compose.local.yml run --rm django python manage.py loaddata seed
```

- API: <http://localhost:8000/api/>
- Admin: <http://localhost:8000/AdminZ22Dj/>
- API docs: <http://localhost:8000/api/docs/>

Emails in development are captured by mailpit instead of being sent.

### Quality checks

```bash
docker compose -f docker-compose.local.yml run --rm django python manage.py check
docker compose -f docker-compose.local.yml run --rm django python manage.py makemigrations --check
docker compose -f docker-compose.local.yml run --rm django pytest
docker compose -f docker-compose.local.yml run --rm django mypy kresh_energy_be
```

## Configuration

Settings are environment-driven (`config/settings/{base,local,production}.py`). Key
production variables (see `.envs/.production/`):

| Variable                                | Purpose                                            |
| --------------------------------------- | -------------------------------------------------- |
| `DJANGO_SECRET_KEY`                     | Django secret                                      |
| `DJANGO_ALLOWED_HOSTS`                  | e.g. `.kresh-ng.de`                                |
| `DATABASE_URL`                          | Postgres DSN                                        |
| `DJANGO_AWS_ACCESS_KEY_ID` / `…_SECRET` | Cloudflare R2 credentials                          |
| `DJANGO_AWS_STORAGE_BUCKET_NAME`        | Public media bucket                                |
| `DJANGO_AWS_PRIVATE_STORAGE_BUCKET_NAME`| Private lead-upload bucket (signed URLs)           |
| `DJANGO_AWS_S3_ENDPOINT_URL`            | `https://<account>.r2.cloudflarestorage.com`       |
| `DJANGO_AWS_S3_CUSTOM_DOMAIN`           | `ecosolaris-media.kresh-ng.de` (public bucket)         |
| `EMAIL_HOST` / `EMAIL_HOST_USER` / `…_PASSWORD` | Hostinger SMTP (port 465, SSL)             |
| `OPENAI_API_KEY` / `OPENAI_MODEL` / `OPENAI_BASE_URL` | AI assistant provider                 |
| `DJANGO_NUM_PROXIES`                    | `1` (behind Traefik) for correct per-IP throttling |

### Media storage (split R2)

- **Public bucket** — marketing images (`Project.image`, `Testimonial.avatar`), served
  from `ecosolaris-media.kresh-ng.de` with no query-string auth.
- **Private bucket** — sensitive lead uploads (electricity bills, meter/roof photos),
  served via **signed, expiring URLs** and not publicly listable. Selected per-field via
  `kresh_energy_be/common/storages.py` (`PrivateMediaStorage`), which falls back to the
  local filesystem when no private bucket is configured — so local/CI need no R2
  credentials.

## Deployment

Runs on a single dedicated VPS. GitHub Actions builds the image, pushes it to a private
GHCR registry, and the VPS pulls + migrates + restarts over SSH.

- **Edge:** this project owns Traefik (binds 80/443, Let's Encrypt), plus `django`,
  `postgres`, `redis`, and an `awscli` helper. Routing is via the Traefik file provider
  (`compose/production/traefik/traefik.yml`): `ecosolaris-api.kresh-ng.de → django:5000`,
  `ecosolaris.kresh-ng.de → frontend:3000` (the frontend runs from a separate repo on the
  shared external `kresh_web` Docker network). `ecosolaris.kresh-ng.com` / `.org` 301-redirect
  to `ecosolaris.kresh-ng.de`.
- **First-time VPS bootstrap:** `scripts/setup_server.sh` (installs Docker, creates the
  `kresh_web` network, configures UFW, generates a deploy key, prints the required GitHub
  secrets).
- **Deploy:** trigger the **Deploy** workflow (`workflow_dispatch`) — **backend first**,
  then the frontend. After the first deploy, seed catalog content once with
  `loaddata seed` (do not automate this; fixed PKs would overwrite admin edits).

See `DOCKER.md` for container details.
