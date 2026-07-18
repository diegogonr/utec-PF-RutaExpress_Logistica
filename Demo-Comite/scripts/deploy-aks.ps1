# Despliega Demo-Comite en AKS (MVP) — ACR + LoadBalancer
$ErrorActionPreference = "Stop"

$Acr = "acrrutaexpressmvp.azurecr.io"
$Image = "$Acr/demo-comite:latest"
$Rg = "rg_Diego_Gonzales"
$Aks = "aks-rutaexpress-mvp"
$Root = Split-Path -Parent $PSScriptRoot

Write-Host "==> Docker build $Image"
Set-Location $Root
docker build -t $Image .

Write-Host "==> ACR login + push"
az acr login --name acrrutaexpressmvp
docker push $Image

Write-Host "==> kubectl context"
az aks get-credentials --resource-group $Rg --name $Aks --overwrite-existing

Write-Host "==> Service Bus connection (E5 en nube)"
$SbConn = az servicebus namespace authorization-rule keys list `
  --resource-group $Rg `
  --namespace-name sb-rutaexpress-mvp `
  --name RootManageSharedAccessKey `
  --query primaryConnectionString -o tsv

$manifest = Get-Content "$Root\k8s\deployment.yaml" -Raw
if ($SbConn) {
  $manifest = $manifest.Replace("__SERVICE_BUS_CONNECTION_STRING__", $SbConn)
} else {
  $manifest = $manifest.Replace("__SERVICE_BUS_CONNECTION_STRING__", "")
}

$tmp = Join-Path $env:TEMP "demo-comite-k8s.yaml"
Set-Content -Path $tmp -Value $manifest -Encoding UTF8

Write-Host "==> kubectl apply"
kubectl apply -f $tmp

Write-Host "==> Esperando IP publica..."
$dns = "rutaexpress-demo-comite.eastus.cloudapp.azure.com"
for ($i = 0; $i -lt 30; $i++) {
  $ip = kubectl get svc demo-comite -o jsonpath="{.status.loadBalancer.ingress[0].ip}" 2>$null
  if ($ip) {
    Write-Host ""
    Write-Host "Demo publicada (celular):"
    Write-Host "  https://$dns"
    Write-Host "  http://$dns"
    Write-Host "  http://$ip"
    Write-Host ""
    Write-Host "En el celular, si sale advertencia de certificado: Avanzado -> Continuar (MVP)."
    exit 0
  }
  Start-Sleep -Seconds 10
}

Write-Host "Servicio creado; IP aun pendiente. Ejecuta:"
Write-Host "  kubectl get svc demo-comite"
