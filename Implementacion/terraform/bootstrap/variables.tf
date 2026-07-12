variable "azure_region" {
  type    = string
  default = "eastus"
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "gcp_region" {
  type    = string
  default = "us-east1"
}

variable "gcp_project_id" {
  type = string
}

variable "azure_tfstate_rg" {
  type    = string
  default = "rg-rutaexpress-tfstate"
}

variable "azure_storage_account_name" {
  type        = string
  description = "Nombre globalmente único (solo minúsculas y números, 3-24 chars)"
}

variable "aws_tfstate_bucket" {
  type        = string
  description = "Nombre bucket S3 único global"
}

variable "aws_tfstate_lock_table" {
  type    = string
  default = "rutaexpress-tfstate-lock"
}

variable "gcp_tfstate_bucket" {
  type        = string
  description = "Nombre bucket GCS único global"
}

variable "tags" {
  type = map(string)
  default = {
    project     = "rutaexpress"
    environment = "tfstate"
    managed-by  = "terraform"
  }
}
