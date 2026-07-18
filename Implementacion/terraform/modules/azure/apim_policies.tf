# Mock WMS: cabecera X-Mock-Wms-Status: 503 simula degradación (E4)
resource "azurerm_api_management_api_operation_policy" "mock_wms_confirm" {
  api_name            = azurerm_api_management_api.mock_wms.name
  api_management_name = azurerm_api_management.main.name
  resource_group_name = local.rg_name
  operation_id        = "confirmReservation"

  xml_content = <<-XML
    <policies>
      <inbound>
        <base />
        <choose>
          <when condition="@(context.Request.Headers.GetValueOrDefault("X-Mock-Wms-Status","") == "503")">
            <return-response>
              <set-status code="503" reason="Service Unavailable" />
              <set-body>{"error":"WMS degradado","scenario":"E4"}</set-body>
            </return-response>
          </when>
        </choose>
        <return-response>
          <set-status code="200" reason="OK" />
          <set-header name="Content-Type" exists-action="override">
            <value>application/json</value>
          </set-header>
          <set-body>{"status":"CONFIRMED","source":"mock-wms"}</set-body>
        </return-response>
      </inbound>
      <backend><base /></backend>
      <outbound><base /></outbound>
      <on-error><base /></on-error>
    </policies>
  XML
}

# Mock portal tracking (E8 — contrato lectura CQRS; respuesta mock APIM, infra BQ en GCP)
resource "azurerm_api_management_api_operation_policy" "mock_portal_tracking" {
  api_name            = azurerm_api_management_api.mock_portal.name
  api_management_name = azurerm_api_management.main.name
  resource_group_name = local.rg_name
  operation_id        = "getTracking"

  xml_content = <<-XML
    <policies>
      <inbound>
        <base />
        <return-response>
          <set-status code="200" reason="OK" />
          <set-header name="Content-Type" exists-action="override">
            <value>application/json</value>
          </set-header>
          <set-body>@{
            var id = context.Request.MatchedParameters["id"];
            return new JObject(
              new JProperty("orderId", id),
              new JProperty("status", "IN_TRANSIT"),
              new JProperty("scenario", "E8"),
              new JProperty("source", "mock-portal-mvp")
            ).ToString();
          }</set-body>
        </return-response>
      </inbound>
      <backend><base /></backend>
      <outbound><base /></outbound>
      <on-error><base /></on-error>
    </policies>
  XML
}
