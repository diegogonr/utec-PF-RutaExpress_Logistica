# Backend hacia order-service en AKS.
# Tras helm install, actualizar order_api_backend_url con la IP del LoadBalancer:
#   kubectl get svc -n rutaexpress order-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
resource "azurerm_api_management_backend" "orders" {
  name                = "orders-aks-backend"
  resource_group_name = local.rg_name
  api_management_name = azurerm_api_management.main.name
  protocol            = "http"
  url                 = var.order_api_backend_url
  description         = "Orquestador de Pedidos (APP-02) en AKS"
}

resource "azurerm_api_management_api_policy" "orders_routing" {
  api_name            = azurerm_api_management_api.orders.name
  api_management_name = azurerm_api_management.main.name
  resource_group_name = local.rg_name

  xml_content = <<-XML
    <policies>
      <inbound>
        <base />
        <set-header name="X-Mock-Wms-Status" exists-action="skip">
          <value>@(context.Request.Headers.GetValueOrDefault("X-Mock-Wms-Status",""))</value>
        </set-header>
        <set-backend-service backend-id="${azurerm_api_management_backend.orders.name}" />
      </inbound>
      <backend><base /></backend>
      <outbound><base /></outbound>
      <on-error><base /></on-error>
    </policies>
  XML
}
