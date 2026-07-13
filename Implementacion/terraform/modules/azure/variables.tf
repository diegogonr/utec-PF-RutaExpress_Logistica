variable "resource_group_name" { type = string }
variable "create_resource_group" {
  type        = bool
  description = "false = usar resource group existente (tipico en cuentas UTEC con Contributor solo en rg_<alumno>)"
  default     = true
}
variable "location" { type = string }
variable "tags" { type = map(string) }
variable "tenant_id" { type = string }

variable "key_vault_name" { type = string }
variable "sql_server_name" { type = string }
variable "sql_admin_login" { type = string }
variable "sql_admin_password" {
  type      = string
  sensitive = true
}

variable "aks_name" { type = string }
variable "aks_node_count" {
  type    = number
  default = 2
}
variable "aks_vm_size" {
  type    = string
  default = "Standard_D2s_v3"
}

variable "eventhub_ns_name" { type = string }
variable "eventhub_capacity" {
  type    = number
  default = 1
}

variable "servicebus_ns_name" { type = string }
variable "redis_name" { type = string }
variable "log_analytics_name" { type = string }
variable "app_insights_name" { type = string }

variable "apim_name" { type = string }
variable "apim_sku" {
  type    = string
  default = "Developer_1"
}
variable "apim_publisher_email" {
  type    = string
  default = "arquitectura@rutaexpress.demo"
}

variable "mock_openapi_base_path" {
  type        = string
  description = "Ruta local a apis/mock (relativa al root del repo Implementacion)"
  default     = "../../../apis/mock"
}

variable "acr_name" { type = string }

variable "order_api_backend_url" {
  type        = string
  description = "URL base del backend APP-02 (AKS LoadBalancer). Ej: http://20.x.x.x:8080"
  default     = "http://127.0.0.1:8080"
}
