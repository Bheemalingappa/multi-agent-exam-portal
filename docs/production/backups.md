# Production Backup Strategy

## 1. Managed PostgreSQL Backup Strategy
- **Point-In-Time Recovery (PITR)**: 35-day automated retention window.
- **Daily Automated Snapshots**: Stored in encrypted cloud object storage (S3 / GCS).

## 2. Redis State Backup Strategy
- Redis stores transient task queues and Pub/Sub channel states. Persistence uses RDB snapshotting saved to persistent volumes.
