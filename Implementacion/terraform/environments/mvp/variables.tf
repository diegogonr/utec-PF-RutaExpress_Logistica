variable "project" {
  type    = string
  default = "rutaexpress"
}

variable "environment" {
  type    = string
  default = "mvp"
}

variable "cost_center" {
  type    = string
  default = "logistics"
}

variable "azure_create_resource_group" {
  type        = bool
  description = "false = desplegar dentro de un RG existente (cuentas UTEC)"
  default     = false
}

variable "azure_resource_group_name" {
  type        = string
  description = "Nombre del RG. Si create=false, debe existir y tener rol Contributor"
  default     = ""
}

variable "azure_subscription_id" {
  type        = string
  description = "Azure subscription ID"
}

variable "azure_tenant_id" {
  type        = string
  description = "Azure AD tenant ID"
}

variable "azure_region" {
  type    = string
  default = "eastus"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "aws_account_suffix" {
  type    = string
  default = "mvp01"
}

variable "gcp_project_id" {
  type        = string
  description = "GCP project ID (requerido solo si enable_gcp = true)"
  default     = "disabled"
}

variable "enable_aws" {
  type        = bool
  description = "Fase 2: desplegar recursos AWS (última milla)"
  default     = false
}

variable "enable_gcp" {
  type        = bool
  description = "Fase 3: desplegar recursos GCP (CQRS)"
  default     = false
}

variable "order_api_backend_url" {
  type        = string
  description = "URL del LoadBalancer de order-service. Actualizar tras helm (fase 1 paso 4)"
  default     = "http://127.0.0.1:8080"
}

variable "gcp_region" {
  type    = string
  default = "us-east1"
}

variable "sql_admin_login" {
  type    = string
  default = "sqladmin"
}

variable "sql_admin_password" {
  type        = string
  sensitive   = true
  description = "Password SQL — usar TF_VAR_sql_admin_password o Key Vault en prod"
}

variable "aks_node_count" {
  type    = number
  default = 2
}

variable "aks_vm_size" {
  type    = string
  default = "Standard_D2s_v3"
}

variable "eventhub_throughput_units" {
  type    = number
  default = 1
}

variable "apim_sku" {
  type    = string
  default = "Developer_1"
}

variable "apim_publisher_email" {
  type    = string
  default = "arquitectura@rutaexpress.demo"
}

variable "mobile_api_image" {
  type        = string
  description = "Vacío = ECR AWS creado por Terraform (recomendado tras build-push-mobile-aws.ps1)."
  default     = ""
}

variable "projector_image" {
  type    = string
  default = "gcr.io/cloudrun/hello"
}
