#Requires -Version 5.1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$TfDir = Join-Path $Root "terraform\environments\mvp"
$HelmDir = Join-Path $Root "helm"

Push-Location $TfDir
$rg = terraform output -raw azure_resource_group
$aks = terraform output -raw aks_name
$sqlFqdn = terraform output -raw sql_server_fqdn
$apimUrl = terraform output -raw apim_gateway_url
$acr = terraform output -raw acr_login_server
$redisHost = terraform output -raw redis_hostname
Pop-Location

az aks get-credentials --resource-group $rg --name $aks --overwrite-existing

# Leer password SQL de terraform.tfvars (simple parse)
$tfvars = Get-Content (Join-Path $TfDir "terraform.tfvars") -Raw
if ($tfvars -match 'sql_admin_password\s*=\s*"([^"]+)"') {
  $sqlPass = $Matches[1]
} else {
  throw "No se encontró sql_admin_password en terraform.tfvars"
}

# Redis key via az cli
$redisName = ($redisHost -replace '\.redis\.cache\.windows\.net$','')
$redisKey = az redis list-keys --name $redisName --resource-group $rg --query primaryKey -o tsv

# Event Hub connection string
Push-Location $TfDir
$ehConnStr = terraform output -raw eventhub_connection_string
Pop-Location

$mockWms = "$apimUrl/mock/wms/v1/reservations/confirm"

$apimSubKey = ""
try {
  $apimSubKey = az rest --method post `
    --url "https://management.azure.com/subscriptions/$(az account show --query id -o tsv)/resourceGroups/$rg/providers/Microsoft.ApiManagement/service/apim-rutaexpress-mvp/subscriptions/master/listSecrets?api-version=2022-08-01" `
    --query primaryKey -o tsv 2>$null
} catch {
  Write-Warning "No se pudo leer APIM subscription key; E4 puede fallar hasta configurar APIM_SUBSCRIPTION_KEY en order-service"
}
if (-not $apimSubKey) {
  Write-Warning "Pega la primary key manualmente: --set env.apimSubscriptionKey=TU_KEY"
}

function Deploy-Chart($name, $extraSet) {
  $sets = @(
    "--set", "image.repository=$acr/$name",
    "--set", "env.sqlServer=$sqlFqdn",
    "--set", "env.sqlPassword=$sqlPass"
  ) + $extraSet
  helm upgrade --install $name (Join-Path $HelmDir $name) -n rutaexpress --create-namespace @sets
}

Deploy-Chart "inventory-service" @()
Deploy-Chart "order-service" @(
  "--set", "env.redisHost=$redisHost",
  "--set", "env.redisPassword=$redisKey",
  "--set", "env.mockWmsUrl=$mockWms",
  "--set", "env.apimSubscriptionKey=$apimSubKey"
)
Deploy-Chart "bus-workers" @(
  "--set", "env.eventhubConnectionString=$ehConnStr"
)
helm upgrade --install otel (Join-Path $HelmDir "otel") -n rutaexpress

Write-Host "Helm desplegado. Esperando LoadBalancer..." -ForegroundColor Green
kubectl get svc -n rutaexpress order-service
