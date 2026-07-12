output "azure_resource_group" { value = module.azure.resource_group_name }
output "apim_gateway_url" { value = module.azure.apim_gateway_url }
output "aks_name" { value = module.azure.aks_name }
output "sql_server_fqdn" { value = module.azure.sql_server_fqdn }
output "eventhub_namespace" { value = module.azure.eventhub_namespace }
output "servicebus_namespace" { value = module.azure.servicebus_namespace }
output "key_vault_uri" { value = module.azure.key_vault_uri }

output "aws_mobile_alb_dns" { value = module.aws.mobile_alb_dns }
output "aws_dynamodb_table" { value = module.aws.dynamodb_table_name }
output "aws_s3_evidence_bucket" { value = module.aws.s3_evidence_bucket }

output "gcp_bq_dataset" { value = module.gcp.bq_dataset_id }
output "gcp_cloud_run_uri" { value = module.gcp.cloud_run_uri }

output "helm_next_steps" {
  value = <<-EOT
    az aks get-credentials -g ${module.azure.resource_group_name} -n ${module.azure.aks_name}
    helm upgrade --install order-service ../../../helm/order-service -n rutaexpress --create-namespace
    helm upgrade --install inventory-service ../../../helm/inventory-service -n rutaexpress
    helm upgrade --install bus-workers ../../../helm/bus-workers -n rutaexpress
  EOT
}
