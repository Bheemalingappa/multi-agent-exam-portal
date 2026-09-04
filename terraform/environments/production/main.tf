module "network" {
  source             = "../../modules/network"
  project_name       = var.project_name
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
}

module "security" {
  source       = "../../modules/security"
  project_name = var.project_name
  environment  = var.environment
  vpc_id       = module.network.vpc_id
}

module "iam" {
  source       = "../../modules/iam"
  project_name = var.project_name
  environment  = var.environment
}

module "eks" {
  source           = "../../modules/eks"
  project_name     = var.project_name
  environment      = var.environment
  subnet_ids       = module.network.private_subnet_ids
  cluster_role_arn = module.iam.eks_cluster_role_arn
  node_role_arn    = module.iam.eks_node_role_arn
}

module "rds" {
  source            = "../../modules/rds"
  project_name      = var.project_name
  environment       = var.environment
  subnet_ids        = module.network.database_subnet_ids
  security_group_id = module.security.rds_sg_id
  db_password       = var.db_password
}

module "redis" {
  source            = "../../modules/redis"
  project_name      = var.project_name
  environment       = var.environment
  subnet_ids        = module.network.private_subnet_ids
  security_group_id = module.security.redis_sg_id
}

module "ecr" {
  source       = "../../modules/ecr"
  project_name = var.project_name
  environment  = var.environment
}
