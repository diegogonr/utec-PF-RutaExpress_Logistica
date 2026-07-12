terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.110"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.6"
    }
  }
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = var.tags
}

resource "random_string" "sql_suffix" {
  length  = 4
  special = false
  upper   = false
}

resource "azurerm_key_vault" "main" {
  name                       = var.key_vault_name
  location                   = azurerm_resource_group.main.location
  resource_group_name        = azurerm_resource_group.main.name
  tenant_id                  = var.tenant_id
  sku_name                   = "standard"
  soft_delete_retention_days = 7
  purge_protection_enabled   = false
  tags                       = var.tags
}

data "azurerm_client_config" "current" {}

resource "azurerm_key_vault_access_policy" "deployer" {
  key_vault_id = azurerm_key_vault.main.id
  tenant_id    = data.azurerm_client_config.current.tenant_id
  object_id    = data.azurerm_client_config.current.object_id

  secret_permissions = ["Get", "List", "Set", "Delete", "Purge", "Recover"]
}

resource "azurerm_mssql_server" "main" {
  name                         = "${var.sql_server_name}-${random_string.sql_suffix.result}"
  resource_group_name          = azurerm_resource_group.main.name
  location                     = azurerm_resource_group.main.location
  version                      = "12.0"
  administrator_login          = var.sql_admin_login
  administrator_login_password = var.sql_admin_password
  minimum_tls_version          = "1.2"
  tags                         = var.tags
}

resource "azurerm_mssql_database" "orders" {
  name           = "db-orders"
  server_id      = azurerm_mssql_server.main.id
  sku_name       = "S1"
  max_size_gb    = 2
  zone_redundant = false
  tags           = var.tags
}

resource "azurerm_mssql_database" "inventory" {
  name           = "db-inventory"
  server_id      = azurerm_mssql_server.main.id
  sku_name       = "S1"
  max_size_gb    = 2
  zone_redundant = false
  tags           = var.tags
}

resource "azurerm_log_analytics_workspace" "main" {
  name                = var.log_analytics_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
  tags                = var.tags
}

resource "azurerm_application_insights" "main" {
  name                = var.app_insights_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  workspace_id        = azurerm_log_analytics_workspace.main.id
  application_type    = "web"
  tags                = var.tags
}

resource "azurerm_kubernetes_cluster" "main" {
  name                = var.aks_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = var.aks_name
  tags                = var.tags

  default_node_pool {
    name       = "default"
    node_count = var.aks_node_count
    vm_size    = var.aks_vm_size
  }

  identity {
    type = "SystemAssigned"
  }

  oms_agent {
    log_analytics_workspace_id = azurerm_log_analytics_workspace.main.id
  }

  depends_on = [azurerm_log_analytics_workspace.main]
}

resource "azurerm_eventhub_namespace" "main" {
  name                = var.eventhub_ns_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard"
  capacity            = var.eventhub_capacity
  tags                = var.tags
}

resource "azurerm_eventhub" "canonical" {
  name                = "eh-canonical"
  namespace_name      = azurerm_eventhub_namespace.main.name
  resource_group_name = azurerm_resource_group.main.name
  partition_count     = 2
  message_retention   = 1
}

resource "azurerm_eventhub_authorization_rule" "send_listen" {
  name                = "mvp-send-listen"
  namespace_name      = azurerm_eventhub_namespace.main.name
  resource_group_name = azurerm_resource_group.main.name
  eventhub_name       = azurerm_eventhub.canonical.name
  listen              = true
  send                = true
  manage              = true
}

resource "azurerm_servicebus_namespace" "main" {
  name                = var.servicebus_ns_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  sku                 = "Standard"
  tags                = var.tags
}

resource "azurerm_servicebus_queue" "inventory" {
  name         = "q-inventory"
  namespace_id = azurerm_servicebus_namespace.main.id

  dead_lettering_on_message_expiration = true
  max_delivery_count                   = 10
}

resource "azurerm_servicebus_queue" "mock_tms" {
  name         = "q-mock-tms"
  namespace_id = azurerm_servicebus_namespace.main.id

  dead_lettering_on_message_expiration = true
  max_delivery_count                   = 10
}

resource "azurerm_servicebus_queue" "dlq" {
  name         = "q-dlq"
  namespace_id = azurerm_servicebus_namespace.main.id
}

resource "azurerm_redis_cache" "main" {
  name                = var.redis_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  capacity            = 0
  family              = "C"
  sku_name            = "Basic"
  minimum_tls_version = "1.2"
  tags                = var.tags
}

resource "azurerm_api_management" "main" {
  name                = var.apim_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  publisher_name      = "RutaExpress"
  publisher_email     = var.apim_publisher_email
  sku_name            = var.apim_sku
  tags                = var.tags
}

resource "azurerm_key_vault_secret" "eventhub_connection" {
  name         = "eventhub-connection-string"
  value        = azurerm_eventhub_authorization_rule.send_listen.primary_connection_string
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_key_vault_access_policy.deployer]
}

resource "azurerm_key_vault_secret" "servicebus_connection" {
  name         = "servicebus-connection-string"
  value        = azurerm_servicebus_namespace.main.default_primary_connection_string
  key_vault_id = azurerm_key_vault.main.id

  depends_on = [azurerm_key_vault_access_policy.deployer]
}
