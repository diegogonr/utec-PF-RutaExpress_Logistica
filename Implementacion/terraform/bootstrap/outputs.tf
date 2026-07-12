output "azure_storage_account_name" { value = azurerm_storage_account.tfstate.name }
output "azure_tfstate_rg" { value = azurerm_resource_group.tfstate.name }
output "aws_s3_bucket" { value = aws_s3_bucket.tfstate.bucket }
output "aws_dynamodb_lock_table" { value = aws_dynamodb_table.tfstate_lock.name }
output "gcp_bucket_name" { value = google_storage_bucket.tfstate.name }

output "mvp_backend_snippet" {
  value = <<-EOT
    # Pegar en environments/mvp/main.tf tras bootstrap:
    backend "azurerm" {
      resource_group_name  = "${azurerm_resource_group.tfstate.name}"
      storage_account_name = "${azurerm_storage_account.tfstate.name}"
      container_name       = "tfstate"
      key                  = "mvp.terraform.tfstate"
    }
  EOT
}
