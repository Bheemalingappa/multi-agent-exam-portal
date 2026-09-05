# Production AWS & Kubernetes Deployment Architecture

## 1. Overview

The **Multi-Agent Exam & Evaluation Portal** is deployed in a multi-tier AWS production environment utilizing **Amazon EKS (Elastic Kubernetes Service)** in the `us-east-1` region. The application runs within an isolated Kubernetes namespace (`multi-agent-exam`).

```mermaid
graph TD
    subgraph Developer Workstation / CI
        Dev[Developer]
        Docker[Docker CLI / WSL2]
        ECR[Amazon ECR Repository]
    end

    subgraph AWS Cloud (Region: us-east-1)
        NLB[AWS Network Load Balancer]

        subgraph Amazon EKS Cluster (Cluster: multi-agent-exam-production-cluster)
            subgraph Kubernetes Namespace: multi-agent-exam
                Ingress[Nginx Reverse Proxy Service]
                FrontendPod["Frontend Pod (React + Nginx)"]
                BackendPod["Backend Pod (FastAPI + Uvicorn)"]
            end
        end

        subgraph Managed Data Layer
            RDS[("Amazon RDS PostgreSQL")]
            Redis[("Amazon ElastiCache Redis")]
        end
    end

    Dev --> Docker
    Docker -->|Docker Push v46| ECR
    ECR -->|Image Pull| BackendPod
    ECR -->|Image Pull| FrontendPod

    NLB --> Ingress
    Ingress --> FrontendPod
    Ingress --> BackendPod

    BackendPod --> RDS
    BackendPod --> Redis
```

---

## 2. Infrastructure Specifications

| Component | AWS / Cloud Service | Configuration Details |
| :--- | :--- | :--- |
| **AWS Region** | `us-east-1` | N. Virginia |
| **EKS Cluster** | Amazon EKS | `multi-agent-exam-production-cluster` |
| **Kubernetes Namespace** | EKS Namespace | `multi-agent-exam` |
| **Container Registry** | Amazon ECR | `053578819971.dkr.ecr.us-east-1.amazonaws.com/multi-agent-exam-backend:v46`<br>`053578819971.dkr.ecr.us-east-1.amazonaws.com/multi-agent-exam-frontend:v46` |
| **Database** | Amazon RDS PostgreSQL | PostgreSQL 15, Multi-AZ managed instance |
| **Cache & Session** | Amazon ElastiCache | Redis cluster mode enabled |
| **Ingress / Load Balancer** | AWS Network Load Balancer | Endpoint: `http://ae7437d5531624dbd8d018588b30e79f-1203586077.us-east-1.elb.amazonaws.com` |

---

## 3. Kubernetes Deployment Manifests Overview

The application deployment in EKS uses standard Kubernetes manifests located in `k8s/`:

### A. Backend Deployment (`exam-portal-backend`)
- **Replicas**: Scaled to 1 replica (resource-tuned for EKS node limits).
- **Probes**:
  - `livenessProbe`: `GET /health` on port 8000 (initialDelaySeconds: 10, periodSeconds: 10).
  - `readinessProbe`: `GET /ready` on port 8000 (initialDelaySeconds: 5, periodSeconds: 5).
  - `startupProbe`: `GET /health` on port 8000 (failureThreshold: 10).
- **Security Context**: Non-root container (`runAsUser: 10001`, `runAsGroup: 10001`, `seccompProfile: RuntimeDefault`).

### B. Frontend Deployment (`exam-portal-frontend`)
- **Replicas**: 1 replica serving compiled React static assets via Nginx.
- **Port**: 80.

---

## 4. Build & Deployment Lifecycle

To deploy a new version (e.g., version `:v46`):

1. **Build Container Images**:
   ```bash
   docker build -t 053578819971.dkr.ecr.us-east-1.amazonaws.com/multi-agent-exam-backend:v46 -f backend/Dockerfile.backend backend
   docker build -t 053578819971.dkr.ecr.us-east-1.amazonaws.com/multi-agent-exam-frontend:v46 -f frontend/Dockerfile.frontend frontend
   ```

2. **Push to Amazon ECR**:
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 053578819971.dkr.ecr.us-east-1.amazonaws.com
   docker push 053578819971.dkr.ecr.us-east-1.amazonaws.com/multi-agent-exam-backend:v46
   docker push 053578819971.dkr.ecr.us-east-1.amazonaws.com/multi-agent-exam-frontend:v46
   ```

3. **Deploy to EKS**:
   ```bash
   kubectl set image deployment/exam-portal-backend backend=053578819971.dkr.ecr.us-east-1.amazonaws.com/multi-agent-exam-backend:v46 -n multi-agent-exam
   kubectl set image deployment/exam-portal-frontend frontend=053578819971.dkr.ecr.us-east-1.amazonaws.com/multi-agent-exam-frontend:v46 -n multi-agent-exam
   kubectl rollout restart deployment/exam-portal-backend -n multi-agent-exam
   ```

4. **Verify Pod Status & Health**:
   ```bash
   kubectl get pods -n multi-agent-exam
   curl http://ae7437d5531624dbd8d018588b30e79f-1203586077.us-east-1.elb.amazonaws.com/api/v1/health
   curl http://ae7437d5531624dbd8d018588b30e79f-1203586077.us-east-1.elb.amazonaws.com/api/v1/ready
   ```
