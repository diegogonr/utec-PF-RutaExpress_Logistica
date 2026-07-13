variable "prefix" { type = string }
variable "tags" { type = map(string) }
variable "ecs_cluster_name" { type = string }
variable "dynamodb_table_name" { type = string }
variable "s3_evidence_bucket" { type = string }
variable "sqs_mobile_queue" { type = string }
variable "sqs_dlq_name" { type = string }

variable "mobile_api_image" {
  type        = string
  description = "Imagen APP-15. Vacío = ECR del módulo (prefijo-mobile-api:latest)."
  default     = ""
}
