terraform {
  required_version = ">= 1.6.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.110"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.60"
    }
    google = {
      source  = "hashicorp/google"
      version = "~> 5.40"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }

  # Tras bootstrap, descomentar y completar con outputs del bootstrap:
  # backend "azurerm" {
  #   resource_group_name  = "rg-rutaexpress-tfstate"
  #   storage_account_name   = "strutaexpresstf"
  #   container_name       = "tfstate"
  #   key                  = "mvp.terraform.tfstate"
  # }
}

provider "azurerm" {
  features {
    key_vault {
      purge_soft_delete_on_destroy = true
    }
    resource_group {
      prevent_deletion_if_contains_resources = false
    }
  }
  subscription_id = var.azure_subscription_id
  tenant_id       = var.azure_tenant_id
}

provider "aws" {
  region = var.aws_region
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

module "naming" {
  source = "../../modules/shared/naming"

  project              = var.project
  environment          = var.environment
  cost_center          = var.cost_center
  aws_account_suffix   = var.aws_account_suffix
}

module "azure" {
  source = "../../modules/azure"

  resource_group_name = module.naming.resource_group_name
  location            = var.azure_region
  tags                = module.naming.tags
  tenant_id           = var.azure_tenant_id

  key_vault_name      = module.naming.key_vault_name
  sql_server_name     = module.naming.sql_server_name
  sql_admin_login     = var.sql_admin_login
  sql_admin_password  = var.sql_admin_password

  aks_name            = module.naming.aks_name
  aks_node_count      = var.aks_node_count
  aks_vm_size         = var.aks_vm_size

  eventhub_ns_name    = module.naming.eventhub_ns_name
  eventhub_capacity   = var.eventhub_throughput_units

  servicebus_ns_name  = module.naming.servicebus_ns_name
  redis_name          = module.naming.redis_name
  log_analytics_name  = module.naming.log_analytics_name
  app_insights_name   = module.naming.app_insights_name

  apim_name           = module.naming.apim_name
  apim_sku            = var.apim_sku
  apim_publisher_email = var.apim_publisher_email

  mock_openapi_base_path = "${path.module}/../../../apis/mock"
}

module "aws" {
  source = "../../modules/aws"

  prefix               = module.naming.prefix
  tags                 = module.naming.tags
  ecs_cluster_name     = module.naming.ecs_cluster_name
  dynamodb_table_name  = module.naming.dynamodb_table_name
  s3_evidence_bucket   = module.naming.s3_evidence_bucket
  sqs_mobile_queue     = module.naming.sqs_mobile_queue
  sqs_dlq_name         = module.naming.sqs_dlq_name
  mobile_api_image     = var.mobile_api_image

  depends_on = [module.azure]
}

module "gcp" {
  source = "../../modules/gcp"

  project_id                   = var.gcp_project_id
  region                       = var.gcp_region
  prefix                       = module.naming.prefix
  bq_dataset_id                = module.naming.bq_dataset_id
  cloud_run_service            = module.naming.cloud_run_service
  labels                       = module.naming.tags
  projector_image              = var.projector_image
  eventhub_connection_string   = module.azure.eventhub_connection_string

  depends_on = [module.azure]
}
