# Tasks · Pilot — Membership Registration Module

**Spec feature:** `pilot-membership-registration`
Implements `requirements.md` per `design.md`. Status key: `[ ]` not started · `[~]` in progress · `[x]` done. Requirement IDs in parentheses reference `requirements.md`.

External approvals (payment KYC, SMS DLT, VPS/domain) run in parallel from week 1 — they are the only things that can block 1 Nov. The on/off switch pattern (NFR7.2) is the fallback for any unready module.

---

## P0 · Foundations

- [x] **T0.1** Initialise monorepo: `backend/`, `frontend/`, `deploy/`, `docs/`. Pin tooling: uv, ruff, ty, pytest (backend); Biome, Vitest, Playwright (frontend). (NFR4.2)
- [x] **T0.2** Litestar app skeleton with Granian entrypoint; health check; structured logging; warnings-as-errors. (§2.1)
- [x] **T0.3** Postgres 18 local setup; Alembic baseline; `organisations`, `units` (ltree + GIST index) migration; seed State + 14 districts. (FR7.7, NFR7.1)
- [x] **T0.4** `settings` table with module on/off switches (Autopay off, lapse off, grievance-filing off) and the lapse setting. (NFR7.2, FR5.2)
- [x] **T0.5** SvelteKit (Svelte 5) PWA skeleton, TypeScript strict, Biome, Paraglide ML/EN scaffolding, service worker for installability. (NFR2.2, FR9.1)
- [x] **T0.6** OpenAPI → openapi-typescript pipeline; CI contract check. (§2.2)
- [x] **T0.7** nginx local config + Let's Encrypt staging; static app + reverse proxy; authorised file-download location header. (NFR3.2, NFR4.3)
- [x] **T0.8** CI: lint, typecheck, test, build on push; tag-triggered deploy (sync → migrate → restart). (NFR4.2)

## P1 · Auth & identity

- [ ] **T1.1** OTP request/verify endpoints with per-phone + per-IP rate limits and resend cooldown; DLT-registered template. (FR1.1, FR1.3, NFR3.5)
- [ ] **T1.2** Reject already-registered phone numbers at OTP stage. (FR1.2)
- [ ] **T1.3** Server-side sessions in Postgres; HttpOnly+Secure+SameSite cookies; expiry. (FR8.2)
- [ ] **T1.4** Member password hashing with argon2id; rate-limited login; account-lock policy. (FR8.1, NFR3.5)
- [ ] **T1.5** Admin login + mandatory TOTP 2FA; recovery codes. (FR7.9)
- [ ] **T1.6** Append-only `audit_log` table + writer helper; every sensitive action audited. (FR7.8)
- [ ] **T1.7** Password reset: email link (members with email); single-use short-lived reset code issued by district admin (members without email). (FR8.3)
- [ ] **T1.8** Tests: OTP rate-limit, session expiry, 2FA flow, audit-log immutability.

## P2 · Registration form

- [ ] **T2.1** `form_versions` schema (ordered fields, bilingual labels, types, required, options, validation); seed the 15 confirmed fields. (FR2.1, FR2.5)
- [ ] **T2.2** JSONB answers storage keyed to `form_version_id`; server-side validation against that version. (FR2.4, FR2.5)
- [ ] **T2.3** Autosave on field blur; resume endpoint returns incomplete submission. (FR1.4)
- [ ] **T2.4** Live selfie capture component (in-app camera), compression + EXIF strip (Pillow), lighting/framing guidance, slow-connection tolerance. (FR1.5, NFR5.2)
- [ ] **T2.5** Masked identity proof: capture doc type + last-4 only; encrypt + store upload outside web root; admins-only access (audited). (FR2.2, FR2.3, NFR3.1)
- [ ] **T2.6** Sector-grouped platform picker with "Others (specify)"; `platform_entries` with exactly one `is_primary`. (FR2.6)
- [ ] **T2.7** DOB with auto age display; block under-18. (FR2.7)
- [ ] **T2.8** Bilingual labels + validation messages via Paraglide; Malayalam input works; language switcher persists. (FR9.1–FR9.3)
- [ ] **T2.9** Archiving a field keeps existing answers; archived fields hidden from new forms but visible/exportable to admins. (FR2.4)
- [ ] **T2.10** Tests: form-version validation, resume, selfie EXIF strip, masked-ID storage, primary-platform uniqueness, under-18 block.

## P3 · Fees & payments

- [ ] **T3.1** `fee_schedules` with `effective_from`; past rows retained; org_admin editor only. (FR3.3)
- [ ] **T3.2** Payment-provider interface: `create_order`, `verify_webhook_signature`, `create/cancel_mandate`, `fetch_status`. Integrate one provider before launch (Razorpay/Cashfree — Q1). (FR3.4)
- [ ] **T3.3** Order creation for registration fee + N months (default 6 at sign-up = Rs 160); allow pay-ahead 1–N. (FR3.1, FR3.2)
- [ ] **T3.4** Idempotent webhook handler keyed on `provider_payment_id`; allocations to fee/month(s); `paid_up_to` computed. (FR3.6, FR3.9)
- [ ] **T3.5** Automatic activation on confirmed payment; audit-log the activation. (FR1.7)
- [ ] **T3.6** Append-only ledger enforcement (DB-level: no UPDATE/DELETE on `payments`); reversal-entry endpoint. (FR3.5)
- [ ] **T3.7** Offline payment entry (cash/direct-UPI) by admin: records `logged_by`, method, reference, numbered receipt; never deletable. (FR3.7)
- [ ] **T3.8** Numbered digital receipt download (PDF) for member. (FR3.8)
- [ ] **T3.9** Tests: webhook idempotency, paid_up_to calc, append-only enforcement, offline entry immutability, activation-on-payment.

## P4 · Membership number & card

- [ ] **T4.1** Per-district number sequence with row-lock counter; format `DISTCODE + 6-digit`; assigned only after payment confirmed; never reused. (FR4.1)
- [ ] **T4.2** Typst card template: union logo, photo, name, number, working district, status, validity, in member's language; Noto Sans Malayalam. (FR4.2)
- [ ] **T4.3** segno QR encoding an opaque random `card_token` (not member id); `card_tokens` with `revoked` flag; reissue endpoint. (FR4.3, FR4.4)
- [ ] **T4.4** Public `GET /verify/:token` returning only {name, number, district, status}; no auth; no enumeration vector. (FR4.3)
- [ ] **T4.5** Card download as PDF and image; correct Malayalam rendering verified in tests. (FR4.2)
- [ ] **T4.6** Tests: number-sequence concurrency (no gaps/dupes under load), token revocation, verify-page field leakage.

## P5 · Admin console

- [ ] **T5.1** Role enforcement on server: state office-bearers (all districts) vs 14 district logins (own district only); server-side scoping. (FR7.1)
- [ ] **T5.2** Members list: filter by unit, sector, platform, status, dues, working mode, age, registration date; paginated. (FR7.2)
- [ ] **T5.3** Member detail view + edit (audit-logged); transfer member between units (audit-logged). (FR7.5)
- [ ] **T5.4** Suspend/reactivate member with recorded reason; audit-logged. (FR7.5)
- [ ] **T5.5** Payment reports by district and by month; reconciliation against provider settlements; record refunds. (FR7.6)
- [ ] **T5.6** Summary counts by district and sector. (FR7.4)
- [ ] **T5.7** CSV/Excel export; each export logged (user, time, filters). (FR7.3)
- [ ] **T5.8** Master-data editors: districts, platforms, sectors, fees, grievance contacts, WhatsApp links — org_admin only; audited. (FR7.7)
- [ ] **T5.9** Audit-log viewer (read-only, unalterable). (FR7.8)
- [ ] **T5.10** 2FA enforced for all admin accounts. (FR7.9)
- [ ] **T5.11** Tests: role-scoped queries (district can't see other districts), export logging, master-data permission.

## P6 · Bulk paper import

- [ ] **T6.1** `imports` + `import_rows` tables migration; Procrastinate job skeleton. (FR10.1, FR10.12)
- [ ] **T6.2** `GET /admin/import/template` — generate CSV from current form version + optional `paid_up_to`, `paper_receipt_no` columns (bilingual headers). (FR10.2)
- [ ] **T6.3** `POST /admin/import` — accept file, create `imports` job (status queued), enqueue async job; enforce admin unit scope server-side (reject out-of-scope rows). (FR10.1, FR10.9)
- [ ] **T6.4** Async parser/validator: normalise phone (E.164), validate required fields/types, district code exists, age ≥ 18; write per-row outcome to `import_rows`. (FR10.3)
- [ ] **T6.5** Dedup by phone: skip rows whose phone exists, outcome `skipped`/`duplicate_phone`. (FR10.4)
- [ ] **T6.6** For accepted rows: create member (masked Aadhaar from row, `photo_pending` flag), assign membership number via per-district sequence; if `paid_up_to` provided, create offline payment entry in append-only ledger logged by admin. (FR10.5, FR10.6, FR10.7, FR10.8)
- [ ] **T6.7** `GET /admin/import/:id` (status + counts) and `GET /admin/import/:id/report` (CSV: total, accepted, rejected w/ reasons, skipped). (FR10.10, FR10.12)
- [ ] **T6.8** Audit-log every import job (admin, time, file, counts) and every member created by an import. (FR10.11)
- [ ] **T6.9** Admin UI: upload, template download, job list, status, report download; scoped by role. (FR10.9)
- [ ] **T6.10** Tests: duplicate-phone skip, out-of-scope rejection, masked-Aadhaar (no full number stored), offline-payment backfill, report accuracy, async job completion, re-run idempotency.

## P7 · Member self-service

- [ ] **T7.1** Member dashboard: own details (read-only), card download, payment history + receipts. (FR6.1)
- [ ] **T7.2** District WhatsApp group link (replaceable by state office). (FR6.1, FR6.2)
- [ ] **T7.3** Grievance contacts display only (per district: name, role, number); filing disabled by switch. (FR6.1, NFR7.2)
- [ ] **T7.4** Language switch re-renders card/dashboard in chosen language. (FR9.4)
- [ ] **T7.5** Welcome screen post-payment: number, card download, WhatsApp link; link sent by message; no false "joined" claim. (FR1.8, FR1.9)

## P8 · UI design with Google Stitch (runs in parallel with P0–P6)

- [x] **T8.1** Generate design system + tokens in Stitch (union-red palette, Noto Sans/Noto Sans Malayalam, type scale, spacing, 44px targets); export tokens. (NFR5.1, §7)
- [~] **T8.2** Generate registration-flow screens (steps 1–7) in ML and EN; clickable prototype. (§7)
- [~] **T8.3** Generate admin screens: members list + filters, member detail, payment reports, summary, master-data editors, audit log, bulk-import upload + report. (§7)
- [~] **T8.4** Generate card layout (PDF + image) and public QR verify page. (FR4.2, FR4.3)
- [ ] **T8.5** Share prototype with a few workers; collect feedback; iterate. (§7)
- [x] **T8.6** Port Stitch tokens + screens to SvelteKit components; verify Malayalam rendering; tree-shake CSS; accessibility pass (contrast, semantic HTML, keyboard flow). (NFR5.1, §7)

## P9 · Hardening & launch

- [ ] **T9.1** Security review: CSRF, CSP, upload path traversal, ID-mask verification, rate limits. (NFR3.2, NFR3.5)
- [ ] **T9.2** Load test to 200 registrations/day + drive-day peak; verify VPS sizing. (NFR1.1, NFR1.2)
- [ ] **T9.3** Backup + rehearsed full restore; restic off-site (India). (NFR4.1)
- [ ] **T9.4** End-to-end Playwright suite (register → pay [test provider] → card → verify; and bulk-import → accepted member appears) in ML and EN. (NFR1.1)
- [ ] **T9.5** Privacy/consent notice content in ML/EN reviewed; consent tick gating enforced. (FR1.6)
- [ ] **T9.6** Go-live checklist; module switches set (Autopay off, lapse off, grievance-filing off). (NFR7.2)
- [ ] **T9.7** Pilot in 1–2 districts; fix surfaced issues; then statewide go-live + Malayalam training. (§10)

## External / blocking approvals (start week 1)

- [ ] **E1** Payment-provider KYC: union PAN, bank current account, registration certificate. (FR3.4, Q1)
- [ ] **E2** DLT-registered SMS sender ID + OTP message template. (FR1.1, Q4)
- [ ] **E3** Domain + VPS (Indian region) + SMTP provider. (NFR4.3, Q4)
- [ ] **E4** Union content: district codes (C1), district login holders (C2), ML translations, logo + card artwork (C4), sector/platform lists, admin roster, grievance contacts, and paper/Google-Forms member records for the pilot districts (for bulk import).

## Open decisions to close

- [x] **D1** Aadhaar approach decided: masked (type + last-4 + encrypted upload). (FR2.2)
- [ ] **D2** Payment gateway choice (Q1).
- [ ] **D3** Membership number prefix format (Q2).
- [ ] **D4** Lapse grace period (Q3).
- [ ] **D5** Data retention per data type (Q5).
