# AWS Deployment Toolchain Setup & Installation Guide (Windows)

## 1. Toolchain Verification Status

| Tool | Required Version | Status | Windows Installation Command |
|---|---|---|---|
| **Git** | >= 2.x | **INSTALLED** (`v2.53.0`) | Pre-installed |
| **AWS CLI v2** | >= 2.x | **MISSING** | `winget install -e --id Amazon.AWSCLI` |
| **Terraform** | >= 1.5 | **MISSING** | `winget install -e --id HashiCorp.Terraform` |
| **kubectl** | >= 1.28 | **MISSING** | `winget install -e --id Kubernetes.kubectl` |
| **Helm** | >= 3.x | **MISSING** | `winget install -e --id Helm.Helm` |
| **Docker Desktop**| >= 24.x | **MISSING** | `winget install -e --id Docker.DockerDesktop` |

---

## 2. Windows Automated Installation Script (PowerShell Administrator)

Run the following command in PowerShell as Administrator to install all required cloud deployment tools via Windows Package Manager (`winget`):

```powershell
# Install complete AWS deployment toolchain on Windows
winget install -e --id Amazon.AWSCLI
winget install -e --id HashiCorp.Terraform
winget install -e --id Kubernetes.kubectl
winget install -e --id Helm.Helm
winget install -e --id Docker.DockerDesktop

# Restart PowerShell terminal to reload System PATH, then verify:
aws --version
terraform --version
kubectl version --client
helm version
docker --version
```

---

## 3. AWS Deployment Gate Evaluation

```text
[CHECK 01] AWS CLI Installed               : FAIL (aws CLI not found in PATH)
[CHECK 02] AWS Identity Verified           : BLOCKED (aws sts get-caller-identity)
[CHECK 03] Terraform Installed             : FAIL (terraform binary not found)
[CHECK 04] kubectl Installed               : FAIL (kubectl binary not found)
[CHECK 05] Helm Installed                  : FAIL (helm binary not found)
[CHECK 06] Docker Installed                : FAIL (docker binary not found)
[CHECK 07] Git Installed                   : PASS (git version 2.53.0)
[CHECK 08] AWS Region Configured           : TARGET: us-east-1
[CHECK 09] Codebase & Unit Tests           : PASS (60 modules, 31 tests OK)
```

### **GATE DECISION: STATUS: DEPLOYMENT BLOCKED**
