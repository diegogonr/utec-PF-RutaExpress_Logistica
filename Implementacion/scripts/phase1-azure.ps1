#Requires -Version 5.1
<#
.SYNOPSIS
  Fase 1: Terraform Azure-only + build imágenes + Helm en AKS
.PARAMETER SkipTerraform
  Omitir terraform apply (si ya aplicaste infra)
#>
param(
  [switch]$SkipTerraform
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$TfDir = Join-Path $Root "terraform\environments\mvp"

Write-Host "=== FASE 1: Azure (hub) ===" -ForegroundColor Cyan

if (-not $SkipTerraform) {
  Push-Location $TfDir
  if (-not (Test-Path "terraform.tfvars")) {
    Copy-Item "terraform.tfvars.example" "terraform.tfvars"
    Write-Warning "Edita terraform.tfvars con subscription_id, tenant_id, sql_admin_password, apim_publisher_email"
    Pop-Location
    exit 1
  }
  terraform init
  terraform plan -out phase1.tfplan
  terraform apply phase1.tfplan
  Pop-Location
}

& (Join-Path $PSScriptRoot "build-push-images.ps1")
& (Join-Path $PSScriptRoot "deploy-helm-azure.ps1")

Write-Host ""
Write-Host "Siguiente paso manual:" -ForegroundColor Yellow
Write-Host "1. kubectl get svc -n rutaexpress order-service -w"
Write-Host "2. Cuando tengas EXTERNAL-IP, edita terraform.tfvars:"
Write-Host '   order_api_backend_url = "http://<IP>:8080"'
Write-Host "3. cd terraform/environments/mvp && terraform apply"
Write-Host "4. Probar: POST https://<apim>/api/v1/orders con Idempotency-Key"
Write-Host ""
Write-Host "Fase 2: .\phase2-aws.ps1 | Fase 3: .\phase3-gcp.ps1"
