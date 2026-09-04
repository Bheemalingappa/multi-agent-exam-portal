module "kubernetes_production" {
  source      = "../../modules/kubernetes"
  environment = "production"
  node_count  = 5
}

output "production_cluster_name" {
  value = module.kubernetes_production.cluster_name
}
