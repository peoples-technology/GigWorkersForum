# Kerala State Gig & Platform Workers Union Platform
### CITU Kerala (Affiliated to Centre of Indian Trade Unions / CPI(M))

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Litestar 2.x](https://img.shields.io/badge/backend-Litestar%202.x-red.svg)](https://litestar.dev/)
[![SvelteKit 5](https://img.shields.io/badge/frontend-SvelteKit%205-orange.svg)](https://svelte.dev/)
[![PostgreSQL 16](https://img.shields.io/badge/database-PostgreSQL%2016-blue.svg)](https://www.postgresql.org/)
[![License](https://img.shields.io/badge/license-Proprietary%20Union%20Owned-red.svg)]()

Production-grade pilot membership registration, digital verification card issuance, append-only dues ledger, and administrative console for the **Kerala State Gig & Platform Workers Union (CITU)**.

Designed specifically for gig workers (Swiggy, Zomato, Uber, Ola, Porter, Zepto, Blinkit, Urban Company) with high-legibility bilingual UI in Malayalam (മലയാളം) and English, 48px+ touch targets for delivery motorcycle workers on mobile, and strict Indian DPDP Act 2023 compliance.

---

## 🏛️ Project Architecture

```
GigWorkersForum/
├── backend/                     # Litestar 2.x async REST API & background processing
│   ├── app/
│   │   ├── api/                 # Controllers (auth, register, payments, cards, admin, portal, import)
│   │   ├── core/                # Security, DPDP storage, card renderer, QR generator, rate limits
│   │   ├── db/                  # SQLAlchemy 2.0 async models, seeds, sessions
│   │   └── main.py              # Litestar app, CORS, OpenAPI configuration
│   ├── scripts/                 # Peak load benchmark, OpenAPI schema exporter
│   ├── tests/                   # Complete pytest suite (49 unit, integration, and E2E tests)
│   └── pyproject.toml           # uv / hatchling package definition
├── frontend/                    # SvelteKit 5 + Tailwind CSS PWA
│   ├── src/
│   │   ├── lib/                 # Reusable bilingual components, icons, stores
│   │   └── routes/              # Client-side onboarding wizard & member card viewer
│   └── build/                   # Static Single Page App distribution
├── deploy/                      # Production deployment assets
│   ├── nginx/                   # Reverse proxy config with strict CSP & rate limiting
│   ├── systemd/                 # Systemd service units for API server & workers
│   └── backup/                  # Restic encrypted off-site backup script (India region)
├── design/                      # UI tokens & Google Stitch MCP design assets
│   ├── tokens.json              # Union-red palette, typography, and spacing tokens
│   └── stitch_screens.md        # Stitch project screens and design system metadata
├── specs/                       # Pilot membership registration specifications
│   └── pilot-membership-registration/
│       ├── requirements.md      # Functional (FR) & Non-Functional (NFR) requirements
│       ├── design.md            # Technical design, schemas, security models
│       └── tasks.md             # Execution task tracker (Phases P0 – P9)
├── openapi.json                 # Synchronized OpenAPI 3.1 schema specification
└── README.md                    # Root documentation
```

---

## ✨ Key Capabilities

1. **Bilingual Phone-First Onboarding (മലയാളം & English)**
   - Instant phone OTP authentication with rate-limiting protection against SMS bombing.
   - Autosave-on-blur client drafts to prevent lost registrations when workers take deliveries mid-form.
   - 15 confirmed bilingual fields with real-time age verification (workers under 18 blocked).

2. **Digital Personal Data Protection (DPDP Act 2023) Compliance**
   - **Zero Full-Aadhaar Storage:** Only document type (`Aadhaar`, `Driving Licence`) and last 4 digits are retained. Full 12-digit numbers are rejected or stripped in memory.
   - **AES-256-GCM Storage:** Uploaded identity documents and photos are encrypted at rest outside the web root.

3. **Immutable Financial Ledger & Auto-Activation**
   - Database-level trigger blocks `UPDATE` and `DELETE` on the `payments` table.
   - Sign-up dues allocation: ₹160 (₹100 admission fee + 6 months advance dues at ₹10/month).
   - Automatic member activation upon verified payment receipt.
   - Offline manual payment logging (cash/direct-UPI) for district organizers with digital receipts.

4. **Sequential District Membership Numbering & Digital ID Card**
   - Row-level locked (`SELECT ... FOR UPDATE`) district sequence (`KLKKD000042`, `KLEKM000042`).
   - High-resolution digital union ID card rendering in PNG and PDF using CITU red banners, emblems, and Malayalam typography.
   - Segno QR code embedding an opaque random URL-safe 32-character token.

5. **Public QR Code Verification (`/verify/{token}`)**
   - Instant mobile verification for employers, traffic authorities, and fellow union organizers.
   - Zero-authentication required.
   - **Strict Privacy Barrier:** Returns only public safe fields (`name`, `membership_number`, `district`, `status`, `union`). Never leaks phone numbers, Aadhaar digits, addresses, or payment amounts.

6. **Server-Side Role Scoping for District Administration**
   - **State Office-Bearers:** Statewide search, reconciliation, summary analytics, and master data management.
   - **14 District Logins:** Cryptographically scoped to their assigned district unit (`unit_id`). Blocked from querying, editing, or exporting other districts with `403 Forbidden`.
   - Audit logging for all identity document viewing, CSV exports, status changes, and unit transfers.

7. **Bulk Paper Records Migration Engine**
   - Bulk ingestion of existing paper and Google Forms registrations (supports batches of 5,000+ workers).
   - E.164 phone deduplication (skips existing records to avoid duplicates).
   - Offline payment ledger backfill and `photo_pending` flag for future capture.
   - Downloadable CSV audit reports with per-row outcomes and rejection reasons.

8. **Member Self-Service Dashboard**
   - Read-only worker profile, digital card downloads, and past payment receipts.
   - District WhatsApp group invite links dynamically managed by the state office.
   - Read-only district grievance secretary contacts (filing disabled behind switch as per NFR7.2).

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend API** | [Litestar 2.x](https://litestar.dev/) + [Granian](https://github.com/emmett-framework/granian) | High-throughput async Python ASGI server |
| **Language Runtime** | Python 3.12 + [`uv`](https://github.com/astral-sh/uv) | Modern typing, fast package resolution |
| **Database & ORM** | PostgreSQL 16 + [SQLAlchemy 2.0](https://www.sqlalchemy.org/) | Async ORM, `ltree` unit hierarchies, JSONB dynamic forms |
| **Frontend Framework**| [SvelteKit 5](https://svelte.dev/) (Runes) | Ultra-lightweight reactive client for low-bandwidth mobile |
| **Styling & Tokens** | Tailwind CSS 3.4 + Stitch Tokens | Union Red (`#C62828`), Star Gold (`#F59E0B`), Slate (`#1E293B`) |
| **Security & Crypto** | `argon2-cffi`, `cryptography` | Argon2id password hashing, AES-256-GCM, RFC 6238 TOTP 2FA |
| **ID Card Engine** | Pillow (`PIL`) + `segno` | EXIF stripping, Segno QR generation, CR80 ID card generation |
| **Reverse Proxy** | Nginx | HTTP/2, TLS 1.3, strict Content Security Policy, rate limits |
| **Disaster Recovery** | `restic` + `pg_dump` | Automated off-site encrypted backups in Indian cloud region |

---

## 🚀 Quick Start & Local Development

### Prerequisites
- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) package manager
- Node.js 20+ and `npm`

### 1. Clone & Set Up Backend

```bash
cd backend

# Install dependencies using uv
uv sync

# Run database migrations and seed data
uv run python -m app.db.seeds

# Start local API dev server (defaults to http://127.0.0.1:8000)
uv run python -m granian --interface asgi app.main:app --port 8000 --reload
```

The interactive OpenAPI documentation is available at:
- **Swagger UI:** `http://127.0.0.1:8000/schema/swagger`
- **Health Check:** `http://127.0.0.1:8000/health`

### 2. Set Up & Run Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev

# Or build static production bundle
npm run build
```

---

## 🧪 Testing & Verification

The test suite covers unit logic, role-scoping permissions, financial ledger immutability, DPDP masking, and end-to-end user lifecycles.

```bash
cd backend

# Run all 49 automated tests
uv run pytest

# Run linter and code formatter
uv run ruff check .
uv run ruff format .

# Run peak registration load benchmark (NFR1.1)
uv run python scripts/load_test_peak.py

# Re-export synchronized OpenAPI specification
uv run python scripts/export_openapi.py
```

---

## 🛡️ Security & Privacy Summary

- **Authentication:** `argon2id` hashed passwords for administrative logins with mandatory RFC 6238 TOTP two-factor authentication (2FA).
- **Rate Limiting:** Sliding-window rate limiters across OTP endpoints to protect against SMS bombing and brute-force attacks.
- **DPDP Act Compliance:** Zero full 12-digit Aadhaar storage; AES-256-GCM encrypted document uploads; opaque random tokens for QR verification.
- **Auditing:** Immutable append-only audit trail recording every ID document view, CSV export, role change, and member status adjustment.

---

## 📜 Union Ownership & License

This platform is proprietary software developed for and owned by the **Kerala State Gig & Platform Workers Union (CITU)**. All union marks, data, domain assets, and membership records remain the exclusive property of the union state committee.
