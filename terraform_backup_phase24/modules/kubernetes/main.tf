# Infrastructure as Code (IaC) - Kubernetes Cluster Module

variable "environment" {
  type    = string
  default = "production"
}

variable "node_count" {
  type    = number
  default = 3
}

output "cluster_name" {
  value = "multi-agent-exam-cluster-${var.environment}"
}
