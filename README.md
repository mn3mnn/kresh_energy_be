# Kresh Energy — Backend API

REST API behind [**ecosolaris.kresh-ng.de**](https://ecosolaris.kresh-ng.de), a solar-energy
company website for the German market. It serves admin-editable marketing content,
captures leads (quote requests and on-site inspection bookings), runs a customer account
and referral-reward system, and exposes an AI sales/support assistant.

The frontend lives in a separate repository; the two are deployed side by side on one VPS.

[![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white)](.github/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)
[![Python 3.14](https://img.shields.io/badge/python-3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django 6](https://img.shields.io/badge/django-6.0-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Built with Cookiecutter Django](https://img.shields.io/badge/built%20with-Cookiecutter%20Django-ff69b4.svg?logo=cookiecutter)](https://github.com/cookiecutter/cookiecutter-django/)

---

## Features

- **Content API.** Services, reference projects, FAQs, testimonials, service areas and
  savings-calculator settings, all edited in the Django admin with DE/EN fields and an
  `is_active` toggle.
- **Lead capture.** Quote requests with file uploads (electricity bill, meter photo, roof
  photos) and inspection bookings. Customers get a branded confirmation email in their
  own language.
- **"Send quote" admin workflow.** Staff enter a price, preview and edit the email in the
  admin, and send it as a branded HTML email with a plain-text fallback. The send time is
  recorded on the quote.
- **Customer accounts.** Email-only signup with mandatory verification (django-allauth),
  exposed as JSON endpoints through dj-rest-auth with token auth.
- **Referral programme.** Every user gets a referral code. When a referred user submits
  their first quote or booking, both sides receive a discount voucher. Reward amounts are
  set in a singleton settings model, and both sides are notified by email.
- **AI assistant.** A chat endpoint that builds its system prompt from live catalog data,
  calls any OpenAI-compatible provider (OpenRouter in development) and hands off to a
  human when it can't answer. It has three throttles: burst, hourly, and a global daily cap.
- **Multilingual.** German (default), English and Arabic (RTL), for the API, the emails
  and the admin dashboard.
- **Split media storage.** Public marketing images and private lead uploads live in
  separate Cloudflare R2 buckets. Private files are only served through signed URLs
  that expire.

## Tech stack

| Area           | Tools                                                                       |
| -------------- | --------------------------------------------------------------------------- |
| Language       | Python 3.14                                                                 |
| Framework      | Django 6, Django REST Framework                                             |
| Auth           | django-allauth (email login, MFA-ready), dj-rest-auth, DRF token auth       |
| API docs       | drf-spectacular (OpenAPI 3 + Swagger UI)                                    |
| Database       | PostgreSQL (psycopg 3)                                                      |
| Cache          | Redis (django-redis, hiredis) in production; in-memory locally              |
| Storage        | Cloudflare R2 (S3-compatible) via django-storages; WhiteNoise for static    |
| Email          | SMTP (Hostinger) in production; console backend locally                     |
| AI             | `openai` SDK against any OpenAI-compatible Chat Completions API             |
| Server         | Gunicorn + Uvicorn worker (ASGI)                                            |
| Infrastructure | Docker Compose, Traefik + Let's Encrypt, GHCR, single VPS                   |
| CI/CD          | GitHub Actions (lint, migrations check, tests, build → deploy over SSH)     |
| Tooling        | uv, Ruff, mypy (django-stubs), pytest + factory-boy, djLint, pre-commit, just |

## Project structure

```
.
├── config/                    # Django project config
│   ├── settings/              #   base / local / production / test
│   ├── api_router.py          #   all /api/ routes
│   └── urls.py                #   admin, auth, schema & docs URLs
├── kresh_energy_be/           # Application code
│   ├── catalog/               #   Services, projects, FAQs, testimonials, areas, calculator config
│   ├── leads/                 #   Quote requests, roof photos, inspection bookings, emails, "send quote" admin
│   ├── referrals/             #   Referral codes, rewards settings, discount vouchers, reward service
│   ├── assistant/             #   AI chat: catalog context builder, prompt, OpenAI-compatible client
│   ├── users/                 #   Custom User model, allauth adapters, users API
│   ├── common/                #   Shared serializers, private/public storage backends
│   ├── templates/             #   Admin overrides + localized HTML/text email templates
│   └── fixtures/seed.json     #   Initial catalog content
├── locale/                    # de / ar translations (gettext)
├── compose/                   # Dockerfiles & scripts (local, production: django, postgres, traefik, aws)
├── docker-compose.local.yml   # Local stack
├── docker-compose.production.yml
├── scripts/setup_server.sh    # First-time VPS bootstrap
├── .github/workflows/         # ci.yml, deploy.yml
├── docs/                      # Sphinx docs
└── justfile                   # Shortcuts for common Docker commands
```

## API overview

All routes are under `/api/`. Content reads are public. Lead, referral-check and assistant
writes are public but rate-limited. Account endpoints need a token.

| Endpoint                                 | Method      | Auth   | Purpose                               |
| ---------------------------------------- | ----------- | ------ | ------------------------------------- |
| `/api/services/`                         | GET         | —      | Active services                       |
| `/api/projects/`                         | GET         | —      | Reference projects                    |
| `/api/faqs/`                             | GET         | —      | FAQs                                  |
| `/api/testimonials/`                     | GET         | —      | Testimonials                          |
| `/api/service-areas/`                    | GET         | —      | Coverage areas                        |
| `/api/calculator-config/`                | GET         | —      | Savings-calculator parameters         |
| `/api/quotes/`                           | POST        | opt.   | Submit a quote request (+ photos)     |
| `/api/bookings/`                         | POST        | opt.   | Book an on-site inspection            |
| `/api/assistant/chat/`                   | POST        | —      | One AI assistant chat turn            |
| `/api/referrals/check-code/`             | POST        | —      | Check that a referral code is valid   |
| `/api/referrals/me/`                     | GET         | token  | The signed-in user's referral dashboard |
| `/api/auth/registration/`                | POST        | —      | Sign up (email verification follows)  |
| `/api/auth/login/` · `logout/` · `password/…` | POST   | —/token | Login, logout, password flows        |
| `/api/users/me/`                         | GET         | token  | Current user                          |
| `/api/schema/` · `/api/docs/`            | GET         | —      | OpenAPI schema · Swagger UI           |

Leads submitted while signed in are linked to the user, and those are the submissions
that trigger referral rewards.

## Getting started

Prerequisites: Docker and Docker Compose. [`just`](https://github.com/casey/just) is optional.

```bash
git clone <this-repo> && cd kresh_energy_be
cp .envs/.local/.django.example .envs/.local/.django

# Build and start Django + Postgres
docker compose -f docker-compose.local.yml up --build

# In another shell: create an admin user and load the starter content
docker compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser
docker compose -f docker-compose.local.yml run --rm django python manage.py loaddata seed
```

| URL                              | What                         |
| -------------------------------- | ---------------------------- |
| <http://localhost:8000/api/>     | API root                     |
| <http://localhost:8000/api/docs/>| Swagger UI                   |
| <http://localhost:8000/admin/>   | Django admin                 |

In development, outgoing emails are printed to the Django container logs.

Local environment variables live in `.envs/.local/`. To try the assistant, set
`OPENAI_API_KEY`, `OPENAI_BASE_URL` and `OPENAI_MODEL` in `.envs/.local/.django`. Git
ignores that file, so your key stays local.

With `just`: `just up`, `just manage <cmd>`, `just pytest`, `just logs`, `just down`.

### Tests and quality checks

```bash
docker compose -f docker-compose.local.yml run --rm django pytest
docker compose -f docker-compose.local.yml run --rm django mypy kresh_energy_be
docker compose -f docker-compose.local.yml run --rm django python manage.py makemigrations --check
pre-commit run --all-files   # Ruff, djLint and file hygiene hooks
```

CI runs pre-commit, then the migration check and the full test suite in Docker, on every
push and pull request to `main`.

### Translations

```bash
docker compose -f docker-compose.local.yml run --rm django python manage.py makemessages -l de -l ar
docker compose -f docker-compose.local.yml run --rm django python manage.py compilemessages
```

## Configuration

Settings are driven by environment variables (`config/settings/{base,local,production}.py`,
using django-environ). The main production variables are:

| Variable                                         | Purpose                                         |
| ------------------------------------------------ | ----------------------------------------------- |
| `DJANGO_SECRET_KEY`, `DJANGO_ADMIN_URL`          | Secret key, admin path (not the default one)    |
| `DJANGO_ALLOWED_HOSTS`                           | e.g. `.kresh-ng.de`                             |
| `DATABASE_URL`, `REDIS_URL`                      | Postgres / Redis                                |
| `DJANGO_AWS_ACCESS_KEY_ID` / `…_SECRET_ACCESS_KEY` | Cloudflare R2 credentials                     |
| `DJANGO_AWS_STORAGE_BUCKET_NAME`                 | Public media bucket                             |
| `DJANGO_AWS_PRIVATE_STORAGE_BUCKET_NAME`         | Private lead-upload bucket (signed URLs)        |
| `DJANGO_AWS_S3_ENDPOINT_URL`, `DJANGO_AWS_S3_CUSTOM_DOMAIN` | R2 endpoint, public media domain     |
| `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP (port 465, SSL)                      |
| `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL`, `OPENAI_MAX_TOKENS` | AI assistant provider   |
| `ASSISTANT_THROTTLE_BURST` / `_HOUR` / `_GLOBAL` | Assistant rate limits                          |
| `DJANGO_NUM_PROXIES`                             | `1` behind Traefik, so per-IP throttling sees real client IPs |

If no private bucket is configured, private uploads fall back to the local filesystem,
so local development and CI don't need R2 credentials.

## Deployment

The app runs on a single VPS:

1. **Bootstrap (once):** `scripts/setup_server.sh` installs Docker, creates the shared
   `kresh_web` network, configures UFW, generates a deploy key and prints the GitHub
   secrets you need to add.
2. **Deploy:** run the **Deploy** workflow (`workflow_dispatch`). It builds the
   production image, pushes it to GHCR, then connects to the VPS over SSH to pull,
   migrate and restart. Deploy the backend first, then the frontend.
3. **Edge:** this stack owns Traefik (ports 80/443, Let's Encrypt). It routes
   `ecosolaris-api.kresh-ng.de` to Django and `ecosolaris.kresh-ng.de` to the frontend
   container on the shared network. The `.com` and `.org` domains redirect to `.de`.
4. **Seed once** after the first deploy with `loaddata seed`. Don't automate this step:
   the fixtures use fixed primary keys and would overwrite edits made in the admin.

Postgres backups and restores use the scripts in `compose/production/postgres/maintenance/`.
See [`DOCKER.md`](DOCKER.md) for container details.

## License

Released under the [MIT License](LICENSE). You're free to use, modify and distribute the code.

## Author

Built by **Monem**: [abdoeladawy4@gmail.com](mailto:abdoeladawy4@gmail.com)
