resource "azurerm_api_management_api" "mock_wms" {
  name                = "mock-wms"
  resource_group_name = azurerm_resource_group.main.name
  api_management_name = azurerm_api_management.main.name
  revision            = "1"
  display_name        = "Mock WMS Principal (APP-06)"
  path                = "mock/wms"
  protocols           = ["https"]
  service_url         = "https://placeholder.invalid"

  import {
    content_format = "openapi"
    content_value  = file("${var.mock_openapi_base_path}/mock-wms.openapi.yaml")
  }
}

resource "azurerm_api_management_api" "mock_erp" {
  name                = "mock-erp"
  resource_group_name = azurerm_resource_group.main.name
  api_management_name = azurerm_api_management.main.name
  revision            = "1"
  display_name        = "Mock ERP Financiero (APP-25)"
  path                = "mock/erp"
  protocols           = ["https"]
  service_url         = "https://placeholder.invalid"

  import {
    content_format = "openapi"
    content_value  = file("${var.mock_openapi_base_path}/mock-erp.openapi.yaml")
  }
}

resource "azurerm_api_management_api" "mock_portal" {
  name                = "mock-portal"
  resource_group_name = azurerm_resource_group.main.name
  api_management_name = azurerm_api_management.main.name
  revision            = "1"
  display_name        = "Mock Portal B2B tracking (APP-18)"
  path                = "mock/portal"
  protocols           = ["https"]
  service_url         = "https://placeholder.invalid"

  import {
    content_format = "openapi"
    content_value  = file("${var.mock_openapi_base_path}/mock-portal.openapi.yaml")
  }
}

resource "azurerm_api_management_api" "mock_tms" {
  name                = "mock-tms"
  resource_group_name = azurerm_resource_group.main.name
  api_management_name = azurerm_api_management.main.name
  revision            = "1"
  display_name        = "Mock TMS (APP-11)"
  path                = "mock/tms"
  protocols           = ["https"]
  service_url         = "https://placeholder.invalid"

  import {
    content_format = "openapi"
    content_value  = file("${var.mock_openapi_base_path}/mock-tms.openapi.yaml")
  }
}

resource "azurerm_api_management_api" "orders" {
  name                = "orders-api"
  resource_group_name = azurerm_resource_group.main.name
  api_management_name = azurerm_api_management.main.name
  revision            = "1"
  display_name        = "Orders API (APP-02)"
  path                = "api"
  protocols           = ["https"]
  service_url         = "http://order-service.rutaexpress.svc.cluster.local:8080"

  import {
    content_format = "openapi"
    content_value  = file("${var.mock_openapi_base_path}/orders.openapi.yaml")
  }
}
