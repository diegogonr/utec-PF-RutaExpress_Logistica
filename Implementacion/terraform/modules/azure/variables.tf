variable "resource_group_name" { type = string }
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
  default = "Standard_D2s_v5"
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
