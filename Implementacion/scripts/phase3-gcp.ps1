#Requires -Version 5.1
<#
.SYNOPSIS
  Fase 3: Habilita GCP (Cloud Run + BigQuery) — escenario E8 CQRS
#>
$ErrorActionPreference = "Stop"
$TfDir = Join-Path (Split-Path -Parent $PSScriptRoot) "terraform\environments\mvp"

Push-Location $TfDir
$tfvars = Get-Content "terraform.tfvars" -Raw
if ($tfvars -notmatch 'enable_gcp\s*=\s*true') {
  (Get-Content "terraform.tfvars") -replace 'enable_gcp\s*=\s*false', 'enable_gcp = true' | Set-Content "terraform.tfvars"
  Write-Host "enable_gcp = true en terraform.tfvars"
}
if ($tfvars -match 'gcp_project_id\s*=\s*"disabled"') {
  throw "Configura gcp_project_id real en terraform.tfvars (gcloud projects list). No uses 'disabled'."
}
terraform init
terraform plan -out phase3.tfplan
terraform apply phase3.tfplan
if ($LASTEXITCODE -ne 0) {
  Pop-Location
  throw "terraform apply fase 3 fallo. Si fue Secret Manager 403, git pull y reintenta (README 8.2)."
}
Pop-Location

Write-Host "=== FASE 3 completada ===" -ForegroundColor Green
Write-Host "Outputs en mvp\: gcp_cloud_run_uri, gcp_bq_dataset, deploy_phase"
Write-Host "Siguiente: probar E8 desde mvp\ (README 8.3) o Postman E8"
