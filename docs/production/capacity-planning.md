# Capacity Planning & Resource Modeling

## 1. Concurrency Models

| Concurrent Candidates | FastAPI Replicas | Celery Workers | Max DB Connections | Memory Footprint |
|---|---|---|---|---|
| **10 Candidates** | 2 Replicas | 2 Workers | 20 Connections | ~ 1.5 GB Total |
| **100 Candidates** | 3 Replicas | 4 Workers | 40 Connections | ~ 4.0 GB Total |
| **500 Candidates** | 6 Replicas | 8 Workers | 90 Connections | ~ 12.0 GB Total |
| **1000 Candidates** | 10 Replicas | 16 Workers | 180 Connections | ~ 24.0 GB Total |
