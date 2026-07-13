output "azure_resource_group" { value = module.azure.resource_group_name }
output "apim_gateway_url" { value = module.azure.apim_gateway_url }
output "aks_name" { value = module.azure.aks_name }
output "sql_server_fqdn" { value = module.azure.sql_server_fqdn }
output "eventhub_namespace" { value = module.azure.eventhub_namespace }
output "servicebus_namespace" { value = module.azure.servicebus_namespace }
output "key_vault_uri" { value = module.azure.key_vault_uri }
output "acr_login_server" { value = module.azure.acr_login_server }
output "acr_name" { value = replace(module.azure.acr_login_server, ".azurecr.io", "") }
output "redis_hostname" { value = module.azure.redis_hostname }
output "eventhub_connection_string" {
  value     = module.azure.eventhub_connection_string
  sensitive = true
}

output "aws_mobile_alb_dns" {
  value = var.enable_aws ? module.aws[0].mobile_alb_dns : null
}
output "aws_ecr_mobile_api_url" {
  value = var.enable_aws ? module.aws[0].ecr_mobile_api_url : null
}
output "aws_ecs_cluster_name" {
  value = var.enable_aws ? module.aws[0].ecs_cluster_name : null
}
output "aws_ecs_service_name" {
  value = var.enable_aws ? module.aws[0].ecs_service_name : null
}
output "aws_region" {
  value = var.enable_aws ? var.aws_region : null
}
output "aws_dynamodb_table" {
  value = var.enable_aws ? module.aws[0].dynamodb_table_name : null
}
output "aws_s3_evidence_bucket" {
  value = var.enable_aws ? module.aws[0].s3_evidence_bucket : null
}

output "gcp_bq_dataset" {
  value = var.enable_gcp ? module.gcp[0].bq_dataset_id : null
}
output "gcp_cloud_run_uri" {
  value = var.enable_gcp ? module.gcp[0].cloud_run_uri : null
}

output "deploy_phase" {
  value = var.enable_gcp ? "3-azure-aws-gcp" : (var.enable_aws ? "2-azure-aws" : "1-azure-only")
}

output "helm_next_steps" {
  value = <<-EOT
    # Fase 1 — Azure
    az aks get-credentials -g ${module.azure.resource_group_name} -n ${module.azure.aks_name}
    cd Implementacion/scripts
    ./build-push-images.ps1
    ./deploy-helm-azure.ps1
    # Obtener IP LB y actualizar order_api_backend_url en terraform.tfvars, luego:
    terraform apply -var="order_api_backend_url=http://<LB-IP>:8080"
  EOT
}
