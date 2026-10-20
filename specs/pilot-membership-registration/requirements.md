# Requirements · Pilot — Membership Registration Module

**Kerala State Gig & Platform Workers Union (CITU)**
**Spec feature:** `pilot-membership-registration`
**Pilot scope:** the membership registration module, including bulk import of existing paper/Google-Forms members. Every other module (grievance filing/tracking, UPI Autopay, automated lapse, forum, WhatsApp notifications, PVC print) ships switched off or is deferred.

Source proposals: `Membership_Web_Application_Proposal-2.md` (functional) and `Membership_App_Technical_Proposal.md` (technical). Reconciliation notes in §6.

---

## 1. Overview

A worker joins the union online from a phone in a few minutes: verifies their phone by SMS OTP, fills the membership form, takes a selfie, consents, pays, and immediately receives a membership number and a downloadable card. They are connected to their district via a WhatsApp group link and shown grievance contacts. State office-bearers and 14 district offices administer members, fees, and master data with an unalterable audit log.

The platform is built so another organisation can reuse it by changing configuration, not code.

## 2. Users

| User | Scope |
| --- | --- |
| Member | Registers, pays, views own details, downloads card, views payment history, sees district WhatsApp link + grievance contacts. |
| State office-bearer (3 logins: President, General Secretary, Treasurer) | All districts/sectors; search, export, reports, reconcile, master data, audit log. |
| District login (14, one per district) | Own district only; view, search, export; cannot change fees/master data; cannot see other districts. |
| Technical administrator | Configures system + accounts; no member data, no membership work. |
| Public verifier | Scans a card QR; sees name, membership number, district, status only. |

Access rules are enforced on the **server**. Hiding a button in the UI is not sufficient.

## 3. User stories

- **US1 — As a worker**, I want to register from my phone in a few minutes so that I can join without visiting an office.
- **US2 — As a worker**, I want the form to save as I go so that I can resume if interrupted.
- **US3 — As a worker**, I want to pay online and get active immediately so that there is no waiting for approval.
- **US4 — As a worker**, I want my card with a QR so that anyone can verify my membership.
- **US5 — As a worker**, I want to use Malayalam or English so that I understand every step.
- **US6 — As a State office-bearer**, I want to see current membership across all districts without asking each district.
- **US7 — As a district officer**, I want to see and export only my district's members so that data stays scoped.
- **US8 — As a State office-bearer**, I want to edit fees and master data without a developer.
- **US9 — As an auditor**, I want an unalterable log of every change so that accountability is guaranteed.
- **US10 — As a public verifier**, I want to scan a QR and see only minimal status so that member privacy is protected.
- **US11 — As a State office-bearer**, I want to import existing paper/Google-Forms members in bulk so that they enter the system without re-registering online.
- **US12 — As a district officer**, I want to import only my district's paper members so that existing members are migrated accurately and without duplicates.

## 4. Functional requirements

Functional requirements use EARS phrasing ("The system shall..."). Each has an ID referenced by tasks in `tasks.md`.

### 4.1 Registration journey

- **FR1.1** The system shall verify a member's mobile number with a one-time SMS code before registration proceeds.
- **FR1.2** The system shall reject a mobile number that is already registered.
- **FR1.3** The system shall rate-limit OTP requests per phone and per IP to prevent SMS flooding.
- **FR1.4** The system shall autosave form answers and allow an interrupted worker to resume.
- **FR1.5** The system shall require a live selfie captured in-app as the membership photograph.
- **FR1.6** The system shall require the worker to read and tick the willingness statement and consent notice (in Malayalam and English) before registration can proceed.
- **FR1.7** The system shall activate the membership automatically upon confirmed payment, with no approval step.
- **FR1.8** The system shall show a welcome screen with the membership number, card download, and the district WhatsApp group link, and send the link by message.
- **FR1.9** The system shall not claim that a member has joined the WhatsApp group.

### 4.2 Form & data

- **FR2.1** The system shall collect the 15 confirmed fields (name, address, permanent address if different, working district/city, email optional, mobile, WhatsApp number, DOB, gender, mother tongue, companies/platforms, vehicle details, working mode, Aadhaar masked, photograph).
- **FR2.2** The system shall store identity proof as document type + last four digits only and shall never store a full Aadhaar number. *(Decided: masked approach confirmed by the union.)*
- **FR2.3** The system shall encrypt identity-proof uploads and store them outside the web root, accessible only to admins, with every access audit-logged.
- **FR2.4** The system shall let admins edit, reorder, add, or archive form fields without code; archiving a field shall preserve existing answers, which remain visible and exportable.
- **FR2.5** The system shall validate a member's answers against the form version they filled in.
- **FR2.6** The system shall support a sector-grouped platform picker with an "Others (specify)" option per group, and one primary platform per member.
- **FR2.7** The system shall calculate and display age from date of birth and shall block registration for anyone under 18.

### 4.3 Fees & payments

- **FR3.1** The system shall charge Rs 160 at sign-up (Rs 100 registration + Rs 60 covering six monthly subscriptions of Rs 10).
- **FR3.2** The system shall allow paying ahead 1 to N months.
- **FR3.3** The system shall let the State office edit fees with an effective-from date; current members shall not be affected mid-period; past rates shall be retained.
- **FR3.4** The system shall process online payments via a gateway accepting UPI, cards, and net banking, and shall not store card details.
- **FR3.5** The system shall treat payments as an append-only ledger; no payment shall be edited or deleted; mistakes shall be corrected with reversal entries.
- **FR3.6** The system shall process provider webhooks idempotently, keyed on the provider's payment ID.
- **FR3.7** The system shall allow admins to record offline (cash/direct-UPI) payments with a numbered receipt, recording who logged it, method, and reference; such entries shall never be deleted.
- **FR3.8** The system shall issue a numbered digital receipt downloadable by the member for each payment.
- **FR3.9** The system shall compute "paid up to" from payment allocations.

### 4.4 Membership number & card

- **FR4.1** The system shall assign the membership number as district code + six-digit serial (e.g. `KLTVC000009`) only after payment is confirmed; a failed payment shall consume no number; numbers shall never be reused.
- **FR4.2** The system shall generate a membership card as PDF and image showing name, membership number, district, sector, status, validity, photograph, and union logo, in the member's chosen language.
- **FR4.3** The system shall put a QR code on the card that encodes an opaque random token (not the member ID), opening a public verification page showing only name, membership number, district, and status.
- **FR4.4** The system shall allow card tokens to be revoked and reissued.

### 4.5 Validity & lapse

- **FR5.1** The system shall keep a membership valid for the period paid.
- **FR5.2** The system shall allow active status to continue up to six months after expiry for renewal, as a setting that is off by default. *(Reconciliation R5.)*

### 4.6 Member self-service

- **FR6.1** The system shall provide a member dashboard showing own details (read-only), card download, payment history with receipts, the district WhatsApp link, and grievance contacts (contacts only, no filing).
- **FR6.2** The system shall let the State office replace a district WhatsApp invite link.

### 4.7 Administration

- **FR7.1** The system shall enforce admin role scoping on the server: state office-bearers see all districts; a district login sees only its own district and cannot edit fees or master data.
- **FR7.2** The system shall let admins search and filter members by district, sector, platform, status, working mode, age, and registration date.
- **FR7.3** The system shall let admins export to Excel/CSV and shall record each export with the user and time.
- **FR7.4** The system shall show summary counts by district and sector.
- **FR7.5** The system shall let admins suspend or reactivate a member with a recorded reason, audit-logged.
- **FR7.6** The system shall provide payment reports by district and by month, reconcilable against gateway settlements, and shall record refunds.
- **FR7.7** The system shall let the State office manage master data (districts, platforms, sectors, fees, grievance contacts, WhatsApp links) without a developer.
- **FR7.8** The system shall maintain an append-only audit log of every admin viewing of an ID document, every edit, export, payment entry, and role change; the audit log shall be unalterable.
- **FR7.9** The system shall require two-factor authentication (TOTP) for all office-bearer and district admin accounts.

### 4.8 Authentication & account

- **FR8.1** The system shall hash member passwords with argon2id and shall rate-limit login attempts.
- **FR8.2** The system shall store sessions server-side with HttpOnly, Secure, SameSite cookies.
- **FR8.3** The system shall reset passwords via email link for members with email, and via a single-use, short-lived reset code issued by the district admin (after identity check) for members without email.

### 4.9 Bilingual support

- **FR9.1** The system shall allow switching between Malayalam and English on every screen; the choice shall persist.
- **FR9.2** The system shall display Malayalam text correctly and shall support typing Malayalam in the form.
- **FR9.3** The system shall show validation messages in both languages.
- **FR9.4** The system shall render the card in the member's chosen language.

### 4.10 Bulk paper import

- **FR10.1** The system shall allow an authorised admin to upload a file (CSV or Excel) of existing paper- or Google-Forms-registered members and create their records in bulk.
- **FR10.2** The system shall provide a downloadable CSV template generated from the current form version, including optional columns for paid-up-to month and original paper receipt number.
- **FR10.3** The system shall validate each row against the current form version, accept valid rows, and reject invalid rows, reporting a per-row reason for every rejection.
- **FR10.4** The system shall skip (and not create) any row whose mobile number already exists in the system, reporting it as a skipped duplicate, so re-running an import or importing a member who later self-registers online does not create a second record.
- **FR10.5** The system shall assign each accepted imported member a membership number via the per-district sequence and shall set their status to active when a paid-up-to month is provided.
- **FR10.6** For each imported member with a paid-up-to month, the system shall create an offline payment entry in the append-only ledger, logged by the importing admin, so the member's paid-up-to reflects their paper payment.
- **FR10.7** The system shall store Aadhaar from imported rows in masked form (document type + last four digits) only and shall never persist a full Aadhaar number from an import file.
- **FR10.8** The system shall allow imported members to be created without a photograph, flagged as "photo pending" for later capture by the member or an admin.
- **FR10.9** A district admin shall be able to import rows only for their own district, and the system shall reject rows whose working district is not theirs; a state office-bearer shall be able to import rows for any district.
- **FR10.10** The system shall produce a downloadable import report (CSV) listing total rows, accepted, rejected (with per-row reasons), and skipped duplicates.
- **FR10.11** The system shall audit-log every import job (who, when, file name, counts) and every member record created by an import.
- **FR10.12** The system shall process large imports asynchronously and shall expose import status (queued, processing, completed) and the report for download when complete.

## 5. Non-functional requirements

### 5.1 Capacity
- **NFR1.1** The system shall handle up to 200 registrations per day, including short peaks on drive days.
- **NFR1.2** The target deployment (2 vCPU / 4 GB RAM) shall comfortably support 45,000 members.
- **NFR1.3** The system shall accept a single bulk-import file of at least 5,000 rows and process it asynchronously without blocking other requests.

### 5.2 Performance (phone-first)
- **NFR2.1** The app shall load quickly on a slow mobile-data connection and shall avoid requiring a large download to register.
- **NFR2.2** The frontend shall ship as a small static bundle (SvelteKit static build).

### 5.3 Security & privacy
- **NFR3.1** The system shall comply with India's DPDP Act 2023 / DPDP Rules 2025 for sensitive personal data.
- **NFR3.2** The system shall enforce CSRF protection and a strict Content Security Policy.
- **NFR3.3** Data shall stay in India.
- **NFR3.4** A breach-response plan shall be written before launch.
- **NFR3.5** Login and OTP send shall be rate-limited.

### 5.4 Reliability & operations
- **NFR4.1** The system shall back up nightly (encrypted `pg_dump` + uploaded files) to an off-site location in India, and a full restore shall be rehearsed before go-live.
- **NFR4.2** Deployment shall be from a git tag (sync → migrate → restart); nothing shall be hand-edited on the server.
- **NFR4.3** The system shall run on one Linux VPS without Docker, with systemd-managed services.

### 5.5 Accessibility & language
- **NFR5.1** The UI shall be usable on small screens with sufficient contrast and readable type sizes.
- **NFR5.2** Labels shall be short; help text shall appear where a field is likely to confuse.

### 5.6 Ownership
- **NFR6.1** The union shall own its data, domain, hosting account, and source code, and shall hold the credentials for these.

### 5.7 Extensibility
- **NFR7.1** The system shall be re-purposable to another organisation by configuration (organisation name, logo, registration number, sectors, platforms, fees, form fields, hierarchy, languages) without code changes.
- **NFR7.2** Every module except registration and the admin console shall ship behind an on/off switch so an unready module goes live switched off instead of delaying launch.

## 6. Open decisions pending (with safe defaults)

| ID | Decision | Default until decided |
| --- | --- | --- |
| Q1 | Payment gateway (Razorpay / Cashfree) | Build to a provider interface; integrate whichever KYC clears first. |
| Q2 | Membership number prefix format | District code + 6-digit serial (union's choice). |
| Q3 | Lapse grace period | 6-month grace as a setting, off by default. |
| Q4 | VPS / SMS / email providers | Indian-region VPS + DLT-registered SMS + SMTP; start onboarding now. |
| Q5 | Data retention period per data type | Define before launch; ID images deletable on request. |
| R1 | Aadhaar storage approach (full vs masked) | **Decided:** masked (type + last-4 + encrypted upload). |
| C1 | District codes for all 14 districts | Thiruvananthapuram = `KLTVC`; rest to be confirmed. |
| C2 | District login holders | To be confirmed by union. |
| C4 | Card design artwork | Union to propose; team to implement. |

## 7. Out of scope (pilot)

Online grievance filing/tracking (contacts display only); WhatsApp outbound notifications; UPI Autopay mandates; automated lapse processing; PVC print sheets; community forum; surveys/polls; meeting records; multi-union hosting.
