output "resource_group_name" { value = local.rg_name }
output "resource_group_location" { value = local.rg_location }
output "key_vault_id" { value = azurerm_key_vault.main.id }
output "key_vault_uri" { value = azurerm_key_vault.main.vault_uri }
output "sql_server_fqdn" { value = azurerm_mssql_server.main.fully_qualified_domain_name }
output "aks_name" { value = azurerm_kubernetes_cluster.main.name }
output "aks_kube_config" {
  value     = azurerm_kubernetes_cluster.main.kube_config_raw
  sensitive = true
}
output "eventhub_namespace" { value = azurerm_eventhub_namespace.main.name }
output "eventhub_connection_string" {
  value     = azurerm_eventhub_authorization_rule.send_listen.primary_connection_string
  sensitive = true
}
output "servicebus_namespace" { value = azurerm_servicebus_namespace.main.name }
output "servicebus_connection_string" {
  value     = azurerm_servicebus_namespace.main.default_primary_connection_string
  sensitive = true
}
output "apim_gateway_url" { value = azurerm_api_management.main.gateway_url }
output "redis_hostname" { value = azurerm_redis_cache.main.hostname }
output "redis_primary_key" {
  value     = azurerm_redis_cache.main.primary_access_key
  sensitive = true
}
output "acr_login_server" { value = azurerm_container_registry.main.login_server }
output "acr_admin_username" { value = azurerm_container_registry.main.admin_username }
output "acr_admin_password" {
  value     = azurerm_container_registry.main.admin_password
  sensitive = true
}
output "sql_orders_database" { value = azurerm_mssql_database.orders.name }
output "sql_inventory_database" { value = azurerm_mssql_database.inventory.name }
output "app_insights_instrumentation_key" {
  value     = azurerm_application_insights.main.instrumentation_key
  sensitive = true
}
