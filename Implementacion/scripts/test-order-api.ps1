#Requires -Version 5.1
<#
.SYNOPSIS
  POST a APIM /api/v1/orders; muestra el body JSON en respuestas 409/503 (E2–E4).
.EXAMPLE
  & .\test-order-api.ps1 -ApimBaseUrl $apim -Headers $headers -Body $body
#>
[CmdletBinding()]
param(
  [Parameter(Mandatory)]
  [string] $ApimBaseUrl,
  [Parameter(Mandatory)]
  [hashtable] $Headers,
  [Parameter(Mandatory)]
  [string] $Body
)

$uri = "$ApimBaseUrl/api/v1/orders"
try {
  Invoke-RestMethod -Method POST -Uri $uri -Headers $Headers -Body $Body -ContentType "application/json"
} catch {
  if ($_.ErrorDetails.Message) { $_.ErrorDetails.Message } else { $_.Exception.Message }
}
