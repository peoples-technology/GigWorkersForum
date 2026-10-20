# CITU Kerala Gig Workers Union Platform — Backend API

Async REST API service powering the membership registration, financial ledger, digital union ID card generation, and scoped administrative console for the **Kerala State Gig & Platform Workers Union (CITU / CPI(M))**.

Built with **Python 3.12**, **Litestar 2.x**, **PostgreSQL 16 (SQLAlchemy 2.0 async)**, and **Granian**.

---

## 🏗️ Architecture & Component Directory

```
backend/
├── app/
│   ├── api/                     # Route controllers
│   │   ├── admin.py             # Role-scoped member directory, exports, reports, audit logs (FR7)
│   │   ├── auth.py              # OTP flows, argon2id admin login, TOTP 2FA, sessions (FR1, FR8)
│   │   ├── bulk_import.py       # Paper form bulk migration, template download, reports (FR10)
│   │   ├── cards.py             # Card preview, PNG/PDF downloads, public /verify/:token (FR4)
│   │   ├── health.py            # Service health probe & system version
│   │   ├── member_portal.py     # Worker self-service dashboard, WhatsApp links, grievance contacts (FR6)
│   │   ├── payments.py          # Append-only dues ledger, webhooks, offline cash entry, receipts (FR3)
│   │   ├── registration.py      # Form schema, autosave drafts, submission, image/selfie uploads (FR2)
│   │   ├── settings.py          # Public fees and module switches (Autopay OFF, lapse OFF)
│   │   └── units.py             # 14 Kerala district units and hierarchical codes
│   ├── core/                    # Core business logic & compliance engines
│   │   ├── audit.py             # Append-only audit logging helper
│   │   ├── card_renderer.py     # Typst/Pillow high-resolution CR80 ID card generator
│   │   ├── form_validator.py    # 15-field dynamic schema validator with age & Aadhaar checks
│   │   ├── image_processor.py   # Pillow EXIF-stripper and avatar thumbnailer
│   │   ├── import_processor.py  # Bulk CSV parser, phone normalizer, deduplication engine
│   │   ├── membership_sequence.py# Concurrency-safe district counter (SELECT ... FOR UPDATE)
│   │   ├── qr_generator.py      # Segno QR generator for opaque URL-safe tokens
│   │   ├── rate_limit.py        # Sliding-window rate limiters for OTP & login endpoints
│   │   ├── security.py          # Argon2id password hasher & RFC 6238 TOTP generator/verifier
│   │   ├── session.py           # Server-side Postgres session storage with SHA-256 token hashes
│   │   └── storage.py           # AES-256-GCM encrypted document storage outside web root
│   ├── db/                      # Database models and migrations
│   │   ├── models/              # SQLAlchemy 2.0 declarative models
│   │   │   ├── admin.py         # Union admin accounts and 2FA credentials
│   │   │   ├── audit.py         # Immutable audit_log records
│   │   │   ├── card_token.py    # Opaque QR verification tokens with revocation flags
│   │   │   ├── form_version.py  # Versioned dynamic registration schemas
│   │   │   ├── import_job.py    # Bulk migration jobs and row-by-row outcomes
│   │   │   ├── member.py        # Worker profiles with DPDP-masked IDs and answers
│   │   │   ├── organisation.py  # Root union details and registration certificates
│   │   │   ├── payment.py       # Append-only payments ledger with mutation block triggers
│   │   │   ├── platform.py      # Gig platforms (Swiggy, Zomato, Uber, etc.)
│   │   │   ├── session.py       # Active HTTP sessions
│   │   │   ├── settings.py      # System settings and fee structure
│   │   │   └── unit.py          # Union units with ltree hierarchy and district counters
│   │   ├── seeds.py             # Initial seed data for districts, platforms, fees, admin users
│   │   └── session.py           # Async engine and session factory
│   ├── config.py                # Pydantic BaseSettings environment configuration
│   └── main.py                  # Litestar application entry point, CORS, and OpenAPI setup
├── scripts/
│   ├── export_openapi.py        # Exports root openapi.json schema
│   └── load_test_peak.py        # Peak drive-day load test simulation (NFR1.1)
├── tests/                       # Pytest test suite (49 passing tests)
│   ├── test_admin_p5.py         # Role scoping, CSV export, audit logging tests
│   ├── test_api.py              # Health, settings, units, and basic OTP tests
│   ├── test_auth_p1.py          # Argon2id, TOTP 2FA, session management, rate limit tests
│   ├── test_cards_p4.py         # Card rendering, QR generation, public verify privacy tests
│   ├── test_e2e_lifecycle_p9.py # End-to-end user onboarding & bulk migration lifecycle tests
│   ├── test_import_p6.py        # Async bulk paper import and phone deduplication tests
│   ├── test_member_portal_p7.py # Member self-service dashboard & WhatsApp link tests
│   ├── test_payments_p3.py      # Append-only ledger, webhook idempotency, receipts tests
│   └── test_registration_p2.py  # 15 confirmed fields, AES-GCM storage, Pillow selfie tests
└── pyproject.toml               # Project metadata and dependencies managed by uv
```

---

## 🔒 Security & Privacy Implementation

1. **Digital Personal Data Protection (DPDP Act 2023)**:
   - **No Full Aadhaar Storage:** Only `id_doc_type` and `id_last4` are saved. 12-digit Aadhaar numbers entered by workers or imported from paper forms are immediately truncated in memory before reaching database storage.
   - **Encrypted Document Vault:** Identity proofs and worker selfies are encrypted using **AES-256-GCM** with unique nonces and stored in `/var/data/citu/uploads/` outside the web root.

2. **Immutable Append-Only Ledger**:
   - The `payments` table has an ORM-level event listener and database-level trigger strictly disallowing `UPDATE` and `DELETE` operations.
   - Dues adjustments and refunds create dedicated negative or reversal records.

3. **Public Verification (`GET /verify/{token}`)**:
   - The QR code on physical and virtual membership cards encodes an opaque random 32-character URL-safe string.
   - Endpoint requires zero authentication and **only returns safe public fields**:
     `{valid: bool, membership_number: str, name: str, district: str, status: str, union: str}`
   - Phone numbers, Aadhaar digits, addresses, and payment amounts are strictly excluded from the verification response.

4. **Server-Side Role Scoping**:
   - `state_admin` / state office-bearers: Full statewide access, master data management, and summary reconciliation.
   - `district_admin`: Hard-scoped on the server to their assigned `unit_id`. Attempting to query, modify, or export records for another district immediately aborts with `403 Forbidden`.

---

## ⚙️ Environment Variables

Configure these settings in `.env` or system environment variables:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+asyncpg://citu_user:citu_pass@localhost:5432/citu_gigworkers` | PostgreSQL async connection string |
| `DATABASE_ECHO` | `False` | Log raw SQL statements |
| `SECRET_KEY` | *(32-char secret)* | Session signing and cryptographic key |
| `STORAGE_ENCRYPTION_KEY`| *(32-byte hex)* | Key for AES-256-GCM document encryption |
| `STORAGE_PATH` | `/var/data/citu/uploads` | Path to store encrypted uploads |
| `ALLOWED_ORIGINS` | `["http://localhost:5173", "https://gigworkers.citu.org.in"]` | CORS allowed origins |
| `DEBUG` | `False` | Enable debug logs and relaxed cookie flags |

---

## 🚀 Development Setup

### 1. Install Dependencies
Ensure Python 3.12+ and `uv` are installed:

```bash
cd backend
uv sync
```

### 2. Run Database Migrations & Seeds
Populates the 14 Kerala district units with sequential counter records, supported gig platforms, standard fee structures, active bilingual form schema, and admin accounts:

```bash
uv run python -m app.db.seeds
```

### 3. Start Granian ASGI Server
Runs the high-performance Granian ASGI server on port 8000:

```bash
uv run python -m granian --interface asgi app.main:app --port 8000 --reload
```

---

## 🧪 Test Suite & Verification

The test suite runs using SQLite in-memory or PostgreSQL, verifying all security, concurrency, and privacy constraints:

```bash
# Run complete test suite (49 tests)
uv run pytest

# Run tests with short traceback
uv run pytest --tb=short

# Run code style and lint checks
uv run ruff check .
uv run ruff format --check .
```

### Run Peak Drive-Day Load Benchmark
Simulates concurrent worker registrations (NFR1.1 capacity validation):

```bash
uv run python scripts/load_test_peak.py
```

### Export OpenAPI 3.1 Spec
Synchronizes the root `openapi.json` from the live Litestar routes:

```bash
uv run python scripts/export_openapi.py
```
