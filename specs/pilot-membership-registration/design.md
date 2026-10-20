# Design · Pilot — Membership Registration Module

**Spec feature:** `pilot-membership-registration`
Implements the requirements in `requirements.md`. This is the engineering design (the HOW), drawn from `Membership_App_Technical_Proposal.md`.

---

## 1. Goals & context

- Deliver the membership registration module end-to-end on a single cheap Indian VPS, bilingual (Malayalam & English) from day one, fast on low-end Android over mobile data.
- Re-purposable by configuration, not code; one organisation per deployment.
- Every non-registration/admin module ships behind an on/off switch so launch never slips on a single module.
- Sensitive personal data (union membership, blood group, identity documents) treated as DPDP-sensitive from the first line of code.

## 2. Architecture

Single deployable: one Litestar API on Granian, one PostgreSQL 18 database, one Procrastinate worker, a static SvelteKit PWA served by nginx. No Docker, no Redis, no Node process on the server. Sessions, the job queue, and the audit log all live in Postgres.

```
                    ┌───────────────┐
  phone browser ──▶ │  nginx + TLS  │  (Let's Encrypt)
 (PWA, static)       └───┬───────┬───┘
                         │       │ static app + authorised file downloads
                         ▼       ▼
            ┌────────────────┐  files (encrypted, outside web root)
            │ Granian ASGI    │
            │ Litestar API    │
            └────┬───────┬───┘
                 │       │
        ┌────────▼───┐ ┌─▼──────────────┐
        │PostgreSQL 18│ │ Procrastinate  │
        │ sessions,   │ │ worker (jobs) │
        │ queue,      │ └────────────────┘
        │ audit, data  │
        └──────────────┘
                 │
        restic (nightly, encrypted, off-site IN)
```

### 2.1 Technology stack (pilot subset)

| Layer | Choice | Status |
| --- | --- | --- |
| Backend | Litestar + msgspec | Decided |
| App server | Granian (Rust ASGI) | Decided |
| Database | PostgreSQL 18 (JSONB, ltree, row locks) | Proposed |
| DB access | SQLAlchemy 2 async · asyncpg · Alembic | Proposed |
| Jobs | Procrastinate (Postgres-backed) | Proposed |
| Passwords | argon2-cffi (argon2id) | Proposed |
| Encryption | cryptography · AES-GCM | Proposed |
| Images | Pillow (resize, strip EXIF) | Proposed |
| Card PDF | Typst (renders Malayalam correctly) | Proposed |
| QR | segno | Proposed |
| Frontend | SvelteKit (Svelte 5) PWA, TypeScript strict, static build | Decided |
| Translations | Paraglide JS | Proposed |
| API types | OpenAPI → openapi-typescript | Proposed |
| Tooling | uv · ruff · ty · pytest · Biome · Vitest · Playwright | Proposed |
| Proxy / TLS | nginx · Let's Encrypt | Proposed |

### 2.2 Key design decisions

- **No Redis.** Postgres holds sessions, the job queue, and the audit log, so a small VPS has nothing extra to run or back up.
- **API-first, type-safe.** Litestar emits OpenAPI; the frontend's API types are generated from it, so client and server can't drift. CI checks the contract.
- **Append-only money.** Payments are never UPDATEd/DELETEd; corrections are reversal entries. Enforced at the DB level.
- **Masked identity.** Only ID type + last four digits stored as text; uploads encrypted, outside the web root, served only after an API permission check. Full Aadhaar is never stored.
- **Opaque card tokens.** The QR encodes a random token, not the member ID, so the verify page cannot be used to enumerate members.
- **Module switches.** A `settings` table holds on/off flags (UPI Autopay, lapse, grievance filing, etc.); a module not ready at launch is switched off.

## 3. Data model

JSONB and `ltree` are central to keeping the form configurable and the hierarchy queryable.

- **organisations** — one row per deployment (name, logo, reg number, default language). Pilot: one row.
- **units** — `ltree` path per unit, GIST-indexed for "everything under X". Pilot seed: State → 14 districts.
- **members**
  - Fixed columns: `id`, `phone` (unique, E.164), `email`, `password_hash` (argon2id), `working_unit_id`, `membership_number` (unique), `status` (active/suspended), `language`, `photo_path`, `consented_at`, `form_version_id`, `answers` (JSONB), `created_at`.
  - `answers` holds configurable fields plus the `form_version_id` they were validated against.
  - Identity proof: `id_doc_type`, `id_last4`. No full IDs.
- **platform_entries** — many per member: `platform_id`, `sector_id`, `zone`, `is_primary` (exactly one primary). Sector-share stats count only the primary entry.
- **form_versions** — ordered list of fields `{key, type, labels{ml,en}, required, options, validation}`. Removing a field keeps existing answers (archived, still visible/exportable).
- **fee_schedules** — `{fee_type, amount, effective_from}`. Past rows retained.
- **payments** — append-only: `{id, member_id, amount, provider, provider_payment_id (unique → idempotent webhooks), allocations[], status, method, created_at}`. No UPDATE/DELETE; corrections via reversal entries. `paid_up_to` is derived from allocations.
- **offline_payments** — admin-recorded cash/UPI; `logged_by`, method, reference; never deleted.
- **card_tokens** — random opaque token per card (not the member id); `revoked` flag; reissuable.
- **sessions** — server-side in Postgres; HttpOnly, Secure, SameSite cookies.
- **admins** — `unit_id`, `role` (viewer/manager/org_admin), `totp_secret`, `password_hash`.
- **audit_log** — append-only: every ID-document view, edit, export, payment entry, role change.
- **settings** — key/value, including module on/off switches and the lapse setting (off by default).
- **imports** — bulk-import jobs: `{id, admin_id, unit_scope, file_name, total, accepted, rejected, skipped, status (queued/processing/completed/failed), created_at}`. One row per uploaded file.
- **import_rows** — per-row outcome for reporting/durability: `{import_id, row_no, outcome (accepted/rejected/skipped), reason, member_id}`.

### 3.1 Sequences & idempotency

- Membership numbers: `SELECT ... FOR UPDATE` on a per-district counter row; a failed payment consumes no number.
- Webhooks keyed on `provider_payment_id` so a duplicate has no effect.

## 4. Security & compliance

- **Authentication:** admins = password + mandatory TOTP 2FA; members = argon2id passwords, rate-limited login, SMS OTP for phone. Server-side sessions in Postgres; HttpOnly+Secure+SameSite cookies.
- **Accountability:** append-only audit log; payments never deletable; reversal entries only.
- **Protection:** CSRF + strict CSP; uploads encrypted + outside web root, served only after API permission check; full Aadhaar never stored; IDs masked.
- **Rate limiting:** OTP send (per phone + per IP) and login, to prevent SMS flooding.
- **DPDP readiness:** consent notice ML/EN; data used only for stated purpose; members can see/correct own data; breach-response plan written; data stays in India.

## 5. API design (indicative)

Endpoints generated to OpenAPI; frontend types derive via openapi-typescript.

- `POST /auth/otp/request` · `POST /auth/otp/verify` (rate-limited)
- `POST /register/form` (autosave/resume)
- `POST /register/selfie` (upload → resize, strip EXIF)
- `POST /register/consent`
- `POST /payments/create-order` · `POST /payments/webhook` (idempotent) · `GET /payments/history`
- `GET /members/me` · `GET /members/me/card` · `GET /members/me/receipts`
- `GET /verify/:token` (public, no auth — name, number, district, status only)
- Admin: `GET /admin/members` (filter/paginate) · `GET /admin/members/:id` · `POST /admin/members/:id/suspend` · `GET /admin/reports/payments` · `POST /admin/export` (logged) · master-data CRUD · audit log read.
- Bulk import: `GET /admin/import/template` · `POST /admin/import` (async) · `GET /admin/import/:id` (status + counts) · `GET /admin/import/:id/report` (CSV).

## 6. Deployment & backups

- One Linux LTS VPS in an Indian region (~2 vCPU / 4 GB RAM).
- systemd services: Granian API, Procrastinate worker, PostgreSQL.
- CI deploys from a git tag (sync → migrate → restart); nothing hand-edited on the server.
- Backups: nightly encrypted `pg_dump` + uploaded files; `restic` to a second location in India; full restore rehearsed before go-live.

## 7. UI design (Google Stitch)

Google Stitch (Google Labs) turns natural-language prompts, sketches, or screenshots into high-fidelity UI plus exportable design tokens and code (HTML/CSS, React, Tailwind). The production frontend is SvelteKit, so Stitch output is ported, not shipped directly.

**Workflow:**
1. **Tokens:** prompt Stitch for the design system (union-red primary, Noto Sans + Noto Sans Malayalam, type scale, spacing, 44px+ touch targets, mobile 360–414px). Export tokens as JSON/CSS variables.
2. **Screens:** prompt per screen (language picker, phone/OTP, form, selfie, consent, pay, welcome/card, member dashboard, card layout, public verify, admin screens). Refine with follow-ups.
3. **Port to SvelteKit:** convert exported HTML/CSS/Tailwind to Svelte 5 components; substitute the token layer; tree-shake unused CSS; verify Malayalam rendering.
4. **Prototype before build:** share a clickable ML/EN Stitch prototype with a few workers; iterate; then build.

**Guardrails:** Stitch output is a starting point — re-check accessibility, semantic HTML, keyboard flow, and Malayalam typography in the SvelteKit port. Prefer the exported tokens as the source of truth for the component library.

## 8. Trade-offs & alternatives

| Decision | Chosen | Alternative | Rationale |
| --- | --- | --- | --- |
| Backend framework | Litestar + msgspec | FastAPI | Async; serialisation/validation in C; stable since 1.0. |
| State store | Postgres only | Postgres + Redis | One store to run/back up on a small VPS. |
| Frontend | SvelteKit static PWA | Next.js / CSR SPA | Small bundles load fast on low-end Android; installable; no Node on server. |
| Aadhaar storage | Masked (last-4 + encrypted upload) | Full number | DPDP risk; masked is safer and still verifiable. |
| Money model | Append-only ledger | Editable payment rows | Auditability and reconciliation integrity. |
| Card QR | Opaque token | Member ID | Prevents member enumeration via the verify page. |
| Card renderer | Typst | PDF libraries (e.g. WeasyPrint) | Rust; fast; correct Malayalam shaping. |
| Bulk-import dedup | Phone number (E.164) | Name+DOB / national ID | Phone is the login & unique key; matches online self-registration dedup. |

## 9. Bulk paper import

Migrates existing paper/Google-Forms members into the system so they need not re-register online.

- **Actors & scope:** a state office-bearer may import for any district; a district admin may import only their own district (server-enforced). The technical admin has no access to member data and cannot import.
- **Template:** `GET /admin/import/template` returns a CSV generated from the current `form_version` columns, plus optional `paid_up_to` (month) and `paper_receipt_no` columns.
- **Upload & async processing:** `POST /admin/import` accepts the file, creates an `imports` job row (status `queued`), and enqueues a Procrastinate job. The job parses rows in batches, validates each against the form version, and writes per-row outcomes to `import_rows`.
- **Per-row logic:**
  1. Normalise phone to E.164; validate required fields, types, district code exists, age ≥ 18.
  2. If the phone already exists → outcome `skipped`, reason `duplicate_phone`.
  3. If invalid → outcome `rejected` with the specific reason(s).
  4. If valid → create the member (masked Aadhaar from the row; `photo_path` null with a `photo_pending` flag), assign a membership number via the per-district row-locked sequence, and if `paid_up_to` is provided, create an offline payment entry in the append-only ledger logged by the importing admin. Outcome `accepted`.
- **Deduplication** is keyed on the normalised phone, so re-running the same file is safe and a paper member who later self-registers online is not doubled.
- **Aadhaar:** full numbers in a file are truncated to the last four digits and discarded; only `id_doc_type` + `id_last4` are stored.
- **Access control:** the server enforces the admin's unit scope; rows whose working district is outside the admin's scope are rejected with reason `out_of_scope`.
- **Report:** `GET /admin/import/:id/report` returns a CSV of total, accepted, rejected (per-row reasons), and skipped (duplicate). `GET /admin/import/:id` returns status + counts.
- **Audit:** every import job (admin, time, file name, counts) and every created member are written to `audit_log`.
- **Data model:** `imports` (job) and `import_rows` (per-row outcome) tables.

## 10. Build phases (~41 days, two parallel tracks)

External approvals (payment KYC, SMS DLT, VPS/domain) take longer than much of the build and must start in week 1. On/off switches are the fallback for any unready module.

| Phase | Days | Deliverable |
| --- | --- | --- |
| P0 Foundations | 1–5 | Repo, CI, Litestar skeleton, Postgres + Alembic, SvelteKit skeleton, OpenAPI→types, nginx local. |
| P1 Auth + OTP | 6–10 | OTP request/verify (rate-limited), sessions, member passwords, admin login + TOTP 2FA, audit log. |
| P2 Registration form | 11–18 | form_versions, JSONB answers, autosave/resume, bilingual labels, live selfie + EXIF strip, masked ID. |
| P3 Fees + payment | 19–24 | Fee schedules, provider interface, order creation, idempotent webhooks, automatic activation, offline entry, ledger, receipts. |
| P4 Number + card | 25–29 | Per-district number sequence, Typst card, segno QR, opaque tokens, public verify, revoke/reissue. |
| P5 Admin console | 30–34 | Members list/filter/search, detail+edit, payment reports, summary counts, CSV export, master-data, suspend/reactivate. |
| P6 Bulk paper import | 34–37 | CSV template, async upload/parse/validate, dedup by phone, masked Aadhaar, offline-payment backfill, import report, audit logging. (Overlaps P5 tail.) |
| P7 Member self-service | 34–36 | Member dashboard, card download, payment history, WhatsApp link, grievance contacts, language switch. (Overlaps P5/P6.) |
| P8 UI design (Google Stitch) | 1–37 | Parallel: tokens, screen generation, prototype, SvelteKit port. |
| P9 Hardening + verify | 38–41 | Security review, rate-limit tuning, CSP/CSRF audit, backup + rehearsed restore, load test 200/day, E2E (incl. import) Playwright, go-live. |

## 11. Definition of done (pilot)

- A worker registers, pays, activates, and downloads a card on a mid-range Android phone over mobile data, in Malayalam or English.
- A QR scan opens a verify page showing only name, number, district, status.
- State + 14 district admins can view/filter/export their scope, with 2FA and an audit log.
- An authorised admin can bulk-import existing paper/Google-Forms members with per-row accepted/rejected/skipped reporting and no duplicate records.
- Backup restore rehearsed; security review passed; load test at 200/day passed.

## 12. Cross-references

- Requirements: `requirements.md`.
- Tasks: `tasks.md`.
- Source reference docs (workspace root): `Membership_App_Technical_Proposal_Pilot_Spec.md` and `Membership_Web_Application_Proposal_Pilot_Spec.md`.
