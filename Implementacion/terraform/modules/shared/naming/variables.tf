variable "project" {
  type        = string
  description = "Nombre del proyecto (rutaexpress)"
}

variable "environment" {
  type        = string
  description = "Ambiente (mvp, dev, prod)"
}

variable "cost_center" {
  type        = string
  default     = "logistics"
  description = "Tag FinOps cost-center"
}

variable "aws_account_suffix" {
  type        = string
  default     = "mvp"
  description = "Sufijo único para nombres S3 globalmente únicos"
}

variable "extra_tags" {
  type        = map(string)
  default     = {}
  description = "Tags adicionales"
}
