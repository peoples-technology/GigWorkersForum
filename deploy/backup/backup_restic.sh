#!/usr/bin/env bash
# CITU Kerala Gig Workers Union Platform
# Automated Database & Document Backup Script (NFR4.1)
# Uses pg_dump + Restic encrypted off-site backup (India region S3/MinIO/B2)
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/backups/citu}"
UPLOADS_DIR="${UPLOADS_DIR:-/var/data/citu/uploads}"
PGDATABASE="${PGDATABASE:-citu_gigworkers}"
PGUSER="${PGUSER:-citu_user}"
PGHOST="${PGHOST:-localhost}"
PGPORT="${PGPORT:-5432}"

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
DUMP_FILE="${BACKUP_DIR}/citu_db_${TIMESTAMP}.sql.gz"

mkdir -p "${BACKUP_DIR}"

echo "[INFO] [$(date)] Starting CITU Kerala union platform backup..."

# 1. Dump PostgreSQL database with compression
echo "[INFO] Exporting PostgreSQL schema and data..."
pg_dump -h "${PGHOST}" -p "${PGPORT}" -U "${PGUSER}" "${PGDATABASE}" | gzip -9 > "${DUMP_FILE}"
echo "[INFO] Database dump completed: ${DUMP_FILE} ($(du -h "${DUMP_FILE}" | cut -f1))"

# 2. Check restic repository configuration
if [ -n "${RESTIC_REPOSITORY:-}" ]; then
    echo "[INFO] Running off-site restic backup to ${RESTIC_REPOSITORY}..."
    restic backup \
        --tag "citu-production" \
        --tag "kerala" \
        "${DUMP_FILE}" \
        "${UPLOADS_DIR}"

    echo "[INFO] Applying backup retention policy..."
    restic forget \
        --keep-daily 30 \
        --keep-weekly 8 \
        --keep-monthly 12 \
        --keep-yearly 7 \
        --prune
    echo "[INFO] Off-site restic backup completed successfully."
else
    echo "[WARN] RESTIC_REPOSITORY not set. Database backup kept locally at ${DUMP_FILE}."
fi

# 3. Clean up local dumps older than 14 days
find "${BACKUP_DIR}" -name "citu_db_*.sql.gz" -mtime +14 -delete

echo "[INFO] [$(date)] Backup workflow finished."
