#Requires -Version 5.1
<#
.SYNOPSIS
  Construye y publica mobile-api en ECR AWS; fuerza redeploy en ECS.
#>
$ErrorActionPreference = "Stop"

function Assert-LastExit($step) {
  if ($LASTEXITCODE -ne 0) { throw $step }
}

function Login-EcrRegistry {
  param(
    [Parameter(Mandatory = $true)][string]$Registry,
    [Parameter(Mandatory = $true)][string]$Region
  )

  # PowerShell altera stdin al pipear a docker login (400 Bad Request en Windows).
  # cmd.exe preserva el pipe binario correcto para --password-stdin.
  $out = cmd /c "aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $Registry" 2>&1
  $out | ForEach-Object { Write-Host $_ }
  if ($LASTEXITCODE -ne 0) {
    throw @"
docker login ECR fallo.
- Renueva credenciales AWS (`$env:AWS_SESSION_TOKEN` si la key es ASIA...).
- Docker Desktop debe estar Running.
- Prueba manual en cmd.exe:
  aws ecr get-login-password --region $Region | docker login --username AWS --password-stdin $Registry
"@
  }
}

$Root = Split-Path -Parent $PSScriptRoot
$TfDir = Join-Path $Root "terraform\environments\mvp"
$AppDir = Join-Path $Root "apps\mobile-api"

Write-Host "Verificando credenciales AWS..." -ForegroundColor Cyan
aws sts get-caller-identity --output text | Out-Null
Assert-LastExit "AWS CLI sin credenciales. Configura `$env:AWS_ACCESS_KEY_ID`, SECRET y SESSION_TOKEN."

Push-Location $TfDir
$ecr = terraform output -raw aws_ecr_mobile_api_url
$cluster = terraform output -raw aws_ecs_cluster_name
$service = terraform output -raw aws_ecs_service_name
$region = terraform output -raw aws_region 2>$null
Pop-Location

if (-not $ecr) { throw "aws_ecr_mobile_api_url vacio. enable_aws=true y terraform apply primero." }
if (-not $region) { $region = "us-east-1" }

$registry = $ecr.Split("/")[0]
$img = "${ecr}:latest"

Write-Host "Login ECR registry: $registry" -ForegroundColor Cyan
Login-EcrRegistry -Registry $registry -Region $region

Write-Host "Building $img ..."
docker build -t $img $AppDir
Assert-LastExit "docker build fallo."

docker push $img
Assert-LastExit "docker push fallo. Revisa login ECR y que el repo exista."

Write-Host "Forzando redeploy ECS: $cluster / $service" -ForegroundColor Cyan
aws ecs update-service --cluster $cluster --service $service --force-new-deployment --region $region | Out-Null
Assert-LastExit "aws ecs update-service fallo."

Write-Host "Imagen publicada. Espera 1-2 min (target healthy) y prueba E6." -ForegroundColor Green
