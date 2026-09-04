# Database & Operations Backup Strategy

## 1. PostgreSQL Star Schema Backup Procedure
The primary database (`exam_portal_db`) tracks dimension tables and submission facts.

### Automated Daily Dump Strategy
```bash
# Periodic pg_dump execution
pg_dump -U postgres -h localhost -d exam_portal_db -F c -b -v -f "/backups/exam_portal_$(date +%Y%m%d_%H%M%S).dump"
```

## 2. Redis State Backup Strategy
- **Celery Broker & Pub/Sub**: State is transient. Persistence uses Redis RDB snapshots saved to `/data/dump.rdb` every 900 seconds.
