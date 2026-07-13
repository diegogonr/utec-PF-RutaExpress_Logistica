locals {
  prefix = "${var.project}-${var.environment}"

  tags = merge(
    {
      project     = var.project
      environment = var.environment
      cost-center = var.cost_center
      managed-by  = "terraform"
      package     = "rutaexpress-mvp"
    },
    var.extra_tags
  )

  resource_group_name = "rg-${local.prefix}"
  aks_name            = "aks-${local.prefix}"
  apim_name           = "apim-${local.prefix}"
  key_vault_name      = substr(replace("kv-${local.prefix}", "-", ""), 0, 24)
  sql_server_name     = "sql-${local.prefix}"
  eventhub_ns_name    = "eh-${local.prefix}"
  servicebus_ns_name  = "sb-${local.prefix}"
  redis_name          = "redis-${local.prefix}"
  log_analytics_name  = "log-${local.prefix}"
  app_insights_name   = "appi-${local.prefix}"
  acr_name            = substr(replace("acr${local.prefix}", "-", ""), 0, 50)

  ecs_cluster_name    = "ecs-${local.prefix}"
  dynamodb_table_name = "${local.prefix}-mobile-outbox"
  s3_evidence_bucket  = "${local.prefix}-evidence-${var.aws_account_suffix}"
  sqs_mobile_queue    = "${local.prefix}-mobile-bridge"
  sqs_dlq_name        = "${local.prefix}-mobile-dlq"

  bq_dataset_id       = replace("${local.prefix}_tracking", "-", "_")
  cloud_run_service   = "cr-${local.prefix}-projector"
}
