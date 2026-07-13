#Requires -Version 5.1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$TfDir = Join-Path $Root "terraform\environments\mvp"
$Apps = Join-Path $Root "apps"

Push-Location $TfDir
$acr = terraform output -raw acr_login_server
if ($LASTEXITCODE -ne 0) {
  Pop-Location
  throw "No se pudo leer acr_login_server. Ejecuta terraform apply primero."
}
Pop-Location

if (-not $acr) { throw "No se obtuvo acr_login_server. ¿Ejecutaste terraform apply?" }

Write-Host "Login ACR: $acr" -ForegroundColor Cyan
az acr login --name ($acr -replace '\.azurecr\.io$','')

$services = @("order-service", "inventory-service", "bus-workers")
foreach ($svc in $services) {
  $ctx = Join-Path $Apps $svc
  $img = "${acr}/${svc}:latest"
  Write-Host "Building $img ..."
  docker build -t $img $ctx
  docker push $img
}

Write-Host "Imágenes publicadas en $acr" -ForegroundColor Green
