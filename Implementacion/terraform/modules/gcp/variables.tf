variable "project_id" { type = string }
variable "region" { type = string }
variable "prefix" { type = string }
variable "bq_dataset_id" { type = string }
variable "cloud_run_service" { type = string }
variable "labels" { type = map(string) }

variable "projector_image" {
  type    = string
  default = "gcr.io/cloudrun/hello"
}

variable "eventhub_connection_string" {
  type        = string
  default     = ""
  sensitive   = true
  description = "Opcional en primer apply; completar tras crear Event Hubs en Azure"
}

variable "eventhub_secret_id" {
  type    = string
  default = "eventhub-connection"
}
