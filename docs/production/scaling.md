# Horizontal Pod Autoscaling & Worker Scaling Strategy

## 1. FastAPI Gateway HPA
- **Scaling Metric**: CPU Utilization (> 70%) & Memory Utilization (> 80%).
- **Behavior**: Min 2 replicas, Max 10 replicas.

## 2. Celery Task Worker Scaling
- **Current Metric**: CPU-based HPA scaling (Min 2, Max 8 workers).
- **Future Production Recommendation**: KEDA (Kubernetes Event-driven Autoscaling) queue depth scaler triggering on Redis queue depth (`LLEN celery`).
