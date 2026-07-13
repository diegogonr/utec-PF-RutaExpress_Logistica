#Requires -Version 5.1
<#
.SYNOPSIS
  Fase 2: Habilita AWS (ECS, DynamoDB, S3, puente EventBridge) — escenarios E6–E7
#>
$ErrorActionPreference = "Stop"
$TfDir = Join-Path (Split-Path -Parent $PSScriptRoot) "terraform\environments\mvp"

Push-Location $TfDir
Remove-Item phase2-fix.tfplan -ErrorAction SilentlyContinue
$tfvars = Get-Content "terraform.tfvars" -Raw
if ($tfvars -notmatch 'enable_aws\s*=\s*true') {
  (Get-Content "terraform.tfvars") -replace 'enable_aws\s*=\s*false', 'enable_aws = true' | Set-Content "terraform.tfvars"
  Write-Host "enable_aws = true en terraform.tfvars"
}
terraform init
terraform plan -out phase2.tfplan
terraform apply phase2.tfplan
Pop-Location

Write-Host "=== FASE 2 completada ===" -ForegroundColor Green
Write-Host ""
Write-Host "OBLIGATORIO antes de probar E6 (si no, el ALB devuelve 503):" -ForegroundColor Yellow
Write-Host "  cd Implementacion\scripts"
Write-Host "  .\build-push-mobile-aws.ps1"
Write-Host ""
Write-Host "Luego probar E6 desde Implementacion\terraform\environments\mvp"
