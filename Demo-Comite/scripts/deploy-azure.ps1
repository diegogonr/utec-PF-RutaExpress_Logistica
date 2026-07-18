# Despliega Demo-Comite en Azure App Service (MVP)
# Requiere: az login

$ErrorActionPreference = "Stop"

$AppName = "rutaexpress-demo-comite"
$Rg = "rg_Diego_Gonzales"
$Location = "eastus"
$PlanName = "asp-rutaexpress-demo"
$Runtime = "NODE:22-lts"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "==> npm install --production"
npm install --omit=dev

$planExists = $null
try {
  $planExists = az appservice plan show --name $PlanName --resource-group $Rg --query name -o tsv 2>$null
} catch { $planExists = $null }

if (-not $planExists) {
  Write-Host "==> Crear App Service Plan $PlanName"
  az appservice plan create `
    --name $PlanName `
    --resource-group $Rg `
    --location $Location `
    --sku B1 `
    --is-linux `
    --output none
}

$appExists = $null
try {
  $appExists = az webapp show --name $AppName --resource-group $Rg --query name -o tsv 2>$null
} catch { $appExists = $null }

if (-not $appExists) {
  Write-Host "==> Crear Web App $AppName"
  az webapp create `
    --name $AppName `
    --resource-group $Rg `
    --plan $PlanName `
    --runtime $Runtime `
    --output none
} else {
  Write-Host "==> Web App $AppName ya existe"
  az webapp config set --name $AppName --resource-group $Rg --linux-fx-version $Runtime --output none
}

Write-Host "==> Configurar arranque"
az webapp config set `
  --name $AppName `
  --resource-group $Rg `
  --startup-file "npm start" `
  --output none

Write-Host "==> Service Bus (E5)"
$SbConn = az servicebus namespace authorization-rule keys list `
  --resource-group $Rg `
  --namespace-name sb-rutaexpress-mvp `
  --name RootManageSharedAccessKey `
  --query primaryConnectionString -o tsv

$settings = @(
  "SCM_DO_BUILD_DURING_DEPLOYMENT=true",
  "WEBSITE_NODE_DEFAULT_VERSION=~22"
)
if ($SbConn) {
  $settings += "SERVICE_BUS_CONNECTION_STRING=$SbConn"
}

az webapp config appsettings set `
  --name $AppName `
  --resource-group $Rg `
  --settings $settings `
  --output none

Write-Host "==> Publicar codigo (zip deploy)"
$stage = Join-Path $env:TEMP "rutaexpress-demo-stage"
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Path $stage | Out-Null
Copy-Item "$Root\package.json", "$Root\package-lock.json", "$Root\server.js", "$Root\.deployment" $stage
Copy-Item "$Root\lib", "$Root\public" $stage -Recurse

$zip = Join-Path $env:TEMP "rutaexpress-demo-comite.zip"
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path "$stage\*" -DestinationPath $zip -Force

az webapp deploy `
  --resource-group $Rg `
  --name $AppName `
  --src-path $zip `
  --type zip `
  --async false

$hostName = az webapp show --name $AppName --resource-group $Rg --query defaultHostName -o tsv
Write-Host ""
Write-Host "Demo publicada: https://$hostName"
