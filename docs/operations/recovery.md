# Disaster Recovery Procedures

## 1. PostgreSQL Database Restoration
To restore the star schema from a compressed binary backup dump:

```bash
# 1. Terminate active database connections
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'exam_portal_db';

# 2. Re-create clean database
DROP DATABASE IF EXISTS exam_portal_db;
CREATE DATABASE exam_portal_db;

# 3. Restore schema & data tables
pg_restore -U postgres -h localhost -d exam_portal_db -v "/backups/exam_portal_backup.dump"
```

## 2. Docker Ephemeral Sandbox Recovery
If Docker socket or container engine becomes unresponsive:

```bash
# Force cleanup orphaned sandbox containers
docker rm -f $(docker ps -a -q --filter ancestor=multi-agent-exam-portal-sandbox:latest)
```
