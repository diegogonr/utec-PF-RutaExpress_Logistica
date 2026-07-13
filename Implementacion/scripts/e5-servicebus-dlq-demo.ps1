#Requires -Version 5.1
<#
.SYNOPSIS
  E5 — Encola mensaje en q-inventory y agota reintentos (10x abandon) con SDK @azure/service-bus.
.EXAMPLE
  .\e5-servicebus-dlq-demo.ps1
  .\e5-servicebus-dlq-demo.ps1 -OrderId "ORD-E5-MANUAL"
#>
param(
  [string]$ResourceGroup = "rg_Diego_Gonzales",
  [string]$Namespace = "sb-rutaexpress-mvp",
  [string]$Queue = "q-inventory",
  [string]$OrderId = "ORD-E5-PS",
  [int]$AbandonCount = 10
)

$ErrorActionPreference = "Stop"
$ScriptDir = $PSScriptRoot

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  throw "Node.js no encontrado. Instala Node o usa portal Service Bus Explorer."
}

if (-not (Test-Path (Join-Path $ScriptDir "node_modules\@azure\service-bus"))) {
  Write-Host "Instalando @azure/service-bus (una vez)..." -ForegroundColor Cyan
  Push-Location $ScriptDir
  npm install --omit=dev 2>&1 | Out-Null
  Pop-Location
}

Write-Host "Obteniendo connection string de $Namespace..." -ForegroundColor Cyan
$conn = az servicebus namespace authorization-rule keys list `
  --resource-group $ResourceGroup `
  --namespace-name $Namespace `
  --name RootManageSharedAccessKey `
  --query primaryConnectionString -o tsv

$conn = $conn.Trim()
if (-not $conn) {
  throw "No se pudo leer primaryConnectionString. Verifica az login."
}

$env:SB_CONN = $conn
$env:SB_QUEUE = $Queue
$env:ORDER_ID = $OrderId
$env:ABANDON_COUNT = "$AbandonCount"

node (Join-Path $ScriptDir "e5-servicebus-dlq-demo.js")
