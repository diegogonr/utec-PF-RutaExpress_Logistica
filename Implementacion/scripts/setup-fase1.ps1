#Requires -Version 5.1
<#
.SYNOPSIS
  Configura terraform.tfvars con tu cuenta Azure UTEC y lanza Fase 1.
.EXAMPLE
  .\setup-fase1.ps1
  .\setup-fase1.ps1 -SkipTerraform
#>
param(
  [switch]$SkipTerraform,
  [string]$SubscriptionId = "088b9168-fdd5-4280-83de-02aaee8b9daf",
  [string]$TenantId = "8a596301-ca34-484d-b823-b330030e539f",
  [string]$PublisherEmail = "Diego.Gonzales@uteclimaperu.onmicrosoft.com",
  [string]$ResourceGroupName = ""
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$TfDir = Join-Path $Root "terraform\environments\mvp"
$TfVars = Join-Path $TfDir "terraform.tfvars"

function Test-SqlPasswordComplexity {
  param([string]$Password)
  if ($Password.Length -lt 12) { return $false }
  $classes = 0
  if ($Password -cmatch '[A-Z]') { $classes++ }
  if ($Password -cmatch '[a-z]') { $classes++ }
  if ($Password -match '\d') { $classes++ }
  if ($Password -match '[^A-Za-z0-9]') { $classes++ }
  return ($classes -ge 3)
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " RutaExpress MVP - Setup Fase 1 Azure" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# --- 1. Azure login ---
Write-Host "[1/6] Verificando sesion Azure..." -ForegroundColor Yellow
$account = az account show 2>$null | ConvertFrom-Json
if (-not $account) {
  Write-Host "No hay sesion. Ejecutando az login..." -ForegroundColor Yellow
  az login
  $account = az account show | ConvertFrom-Json
}
$userName = $account.user.name
$subName = $account.name
Write-Host ("  [OK] {0} | suscripcion: {1}" -f $userName, $subName) -ForegroundColor Green

$contributorRg = $null
if ($ResourceGroupName) {
  $contributorRg = $ResourceGroupName
} else {
  $rgScopes = az role assignment list --all --assignee $userName --query "[?roleDefinitionName=='Contributor' && contains(scope, 'resourcegroups/')].scope" -o json 2>$null | ConvertFrom-Json
  if ($rgScopes) {
    foreach ($scope in $rgScopes) {
      if ($scope -match 'resourcegroups/([^/]+)$') {
        $contributorRg = $Matches[1]
        break
      }
    }
  }
  if (-not $contributorRg -and $userName -match '^([^.]+)\.([^@]+)@') {
    $candidate = "rg_$($Matches[1])_$($Matches[2])"
    $exists = az group exists --name $candidate -o tsv 2>$null
    if ($exists -eq "true") { $contributorRg = $candidate }
  }
}
if ($contributorRg) {
  Write-Host ("  Resource group UTEC detectado: {0}" -f $contributorRg) -ForegroundColor Green
} else {
  Write-Host "  No se detecto RG con rol Contributor. Se intentara crear rg-rutaexpress-mvp (requiere permisos en suscripcion)." -ForegroundColor Yellow
}

if ($account.id -ne $SubscriptionId) {
  Write-Host "  Cambiando a suscripcion UTEC Posgrado..." -ForegroundColor Yellow
  az account set --subscription $SubscriptionId
}

# --- 2. Docker ---
Write-Host "[2/6] Verificando Docker..." -ForegroundColor Yellow
$dockerOk = $false
try {
  docker info 2>&1 | Out-Null
  if ($LASTEXITCODE -eq 0) { $dockerOk = $true }
} catch {
  $dockerOk = $false
}
if (-not $dockerOk) {
  Write-Host "  [ERROR] Docker Desktop no esta corriendo." -ForegroundColor Red
  Write-Host "  Abre Docker Desktop, espera 'Running' y vuelve a ejecutar este script." -ForegroundColor Red
  exit 1
}
Write-Host "  [OK] Docker en ejecucion" -ForegroundColor Green

# --- 3. terraform.tfvars ---
Write-Host "[3/6] Configurando terraform.tfvars..." -ForegroundColor Yellow
if (Test-Path $TfVars) {
  $overwrite = Read-Host "  terraform.tfvars ya existe. Sobrescribir? (s/N)"
  if ($overwrite -eq "s" -or $overwrite -eq "S") {
    Remove-Item $TfVars
  } else {
    Write-Host "  Usando terraform.tfvars existente." -ForegroundColor Gray
  }
}

if (-not (Test-Path $TfVars)) {
  $sqlPass = Read-Host "  Contrasena SQL admin (min 12 caracteres, guardala bien)" -AsSecureString
  $sqlPassPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sqlPass)
  )
  if ($sqlPassPlain.Length -lt 12 -or -not (Test-SqlPasswordComplexity $sqlPassPlain)) {
    throw "La contrasena SQL debe tener min 12 caracteres y mezclar 3 de: mayusculas, minusculas, numeros, simbolos. Ej: RutaExpress2026!Mvp"
  }

  $createRg = "false"
  $rgName = if ($contributorRg) { "`"$contributorRg`"" } else { "`"rg_Diego_Gonzales`"" }
  if (-not $contributorRg) {
    Write-Host "  [AVISO] No se detecto RG UTEC; usando rg_Diego_Gonzales por defecto." -ForegroundColor Yellow
    $contributorRg = "rg_Diego_Gonzales"
  }

  $tfContent = @(
    "enable_aws = false"
    "enable_gcp = false"
    ""
    "azure_create_resource_group = $createRg"
    "azure_resource_group_name   = $rgName"
    ""
    "project               = `"rutaexpress`""
    "environment           = `"mvp`""
    "azure_subscription_id = `"$SubscriptionId`""
    "azure_tenant_id       = `"$TenantId`""
    "azure_region          = `"eastus`""
    "aws_region            = `"us-east-1`""
    "aws_account_suffix    = `"mvp01`""
    "gcp_project_id        = `"disabled`""
    "gcp_region            = `"us-east1`""
    "sql_admin_login       = `"sqladmin`""
    "sql_admin_password    = `"$sqlPassPlain`""
    "aks_node_count        = 2"
    "aks_vm_size           = `"Standard_D2s_v3`""
    "eventhub_throughput_units = 1"
    "apim_sku              = `"Developer_1`""
    "apim_publisher_email  = `"$PublisherEmail`""
    "order_api_backend_url = `"http://127.0.0.1:8080`""
  ) -join [Environment]::NewLine

  Set-Content -Path $TfVars -Value $tfContent -Encoding UTF8
  Write-Host "  [OK] terraform.tfvars creado" -ForegroundColor Green
}

if (-not $contributorRg) {
  $contributorRg = "rg_Diego_Gonzales"
}

if (Test-Path $TfVars) {
  $tfText = Get-Content -Path $TfVars -Raw
  if ($tfText -match 'azure_create_resource_group\s*=') {
    $tfText = $tfText -replace 'azure_create_resource_group\s*=\s*\S+', 'azure_create_resource_group = false'
  } else {
    $tfText = $tfText.TrimEnd() + [Environment]::NewLine + "azure_create_resource_group = false" + [Environment]::NewLine
  }
  if ($tfText -match 'azure_resource_group_name\s*=') {
    $tfText = $tfText -replace 'azure_resource_group_name\s*=\s*.*', "azure_resource_group_name   = `"$contributorRg`""
  } else {
    $tfText = $tfText.TrimEnd() + [Environment]::NewLine + "azure_resource_group_name   = `"$contributorRg`"" + [Environment]::NewLine
  }
  Set-Content -Path $TfVars -Value ($tfText.TrimEnd() + [Environment]::NewLine) -Encoding UTF8 -NoNewline
  Write-Host ("  [OK] RG UTEC forzado: {0} (sin crear RG nuevo)" -f $contributorRg) -ForegroundColor Green
}

if (Test-Path $TfVars) {
  $tfText = Get-Content -Path $TfVars -Raw
  if ($tfText -match 'aks_vm_size\s*=') {
    $tfText = $tfText -replace 'aks_vm_size\s*=\s*.*', 'aks_vm_size           = "Standard_D2s_v3"'
  } else {
    $tfText = $tfText -replace '(aks_node_count\s*=\s*\d+)', "`$1`naks_vm_size           = `"Standard_D2s_v3`""
  }
  if ($tfText -match 'sql_admin_password\s*=\s*"([^"]+)"') {
    $currentSqlPass = $Matches[1]
    if (-not (Test-SqlPasswordComplexity $currentSqlPass)) {
      Write-Host "  [AVISO] sql_admin_password en tfvars no cumple complejidad Azure SQL." -ForegroundColor Yellow
      $newSqlPass = Read-Host "  Ingresa nueva contrasena SQL (12+ chars, 3 tipos: A/a/0/!)" -AsSecureString
      $newSqlPassPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
        [Runtime.InteropServices.Marshal]::SecureStringToBSTR($newSqlPass)
      )
      if (-not (Test-SqlPasswordComplexity $newSqlPassPlain)) {
        throw "Contrasena SQL invalida. Usa mayusculas, minusculas, numeros y simbolos."
      }
      $tfText = $tfText -replace 'sql_admin_password\s*=\s*.*', "sql_admin_password    = `"$newSqlPassPlain`""
      Write-Host "  [OK] Contrasena SQL actualizada en terraform.tfvars" -ForegroundColor Green
    }
  }
  Set-Content -Path $TfVars -Value ($tfText.TrimEnd() + [Environment]::NewLine) -Encoding UTF8 -NoNewline
}

# --- 4. Terraform apply ---
if (-not $SkipTerraform) {
  Write-Host "[4/6] Terraform apply (APIM puede tardar 30-45 min)..." -ForegroundColor Yellow
  Push-Location $TfDir
  terraform init
  if ($LASTEXITCODE -ne 0) {
    Pop-Location
    throw "terraform init fallo"
  }

  if (Test-Path "phase1.tfplan") {
    Remove-Item "phase1.tfplan" -Force
  }

  $tfCheck = Get-Content -Path (Join-Path $TfDir "terraform.tfvars") -Raw
  if ($tfCheck -match 'azure_create_resource_group\s*=\s*true') {
    Pop-Location
    throw "terraform.tfvars tiene azure_create_resource_group=true. Debe ser false para UTEC."
  }

  & terraform plan -out phase1.tfplan
  if ($LASTEXITCODE -ne 0) {
    Pop-Location
    throw "terraform plan fallo. Revisa errores arriba (permisos Azure, providers)."
  }
  if (-not (Test-Path "phase1.tfplan")) {
    Pop-Location
    throw "No se genero phase1.tfplan"
  }

  Write-Host ""
  $confirm = Read-Host "Aplicar infraestructura Azure? (~USD 296/mes) (s/N)"
  if ($confirm -eq "s" -or $confirm -eq "S") {
    & terraform apply phase1.tfplan
    if ($LASTEXITCODE -ne 0) {
      Pop-Location
      throw "terraform apply fallo"
    }
  } else {
    Write-Host "  Apply cancelado. Ejecuta: terraform apply phase1.tfplan" -ForegroundColor Yellow
    Pop-Location
    exit 0
  }
  Pop-Location
} else {
  Write-Host "[4/6] Terraform omitido (-SkipTerraform)" -ForegroundColor Gray
}

# --- 5. Build + push ---
if (-not $SkipTerraform) {
  Write-Host "[5/6] Build y push imagenes a ACR..." -ForegroundColor Yellow
  & (Join-Path $PSScriptRoot "build-push-images.ps1")
  if ($LASTEXITCODE -ne 0) { throw "build-push-images fallo" }

  # --- 6. Helm ---
  Write-Host "[6/6] Desplegando Helm en AKS..." -ForegroundColor Yellow
  & (Join-Path $PSScriptRoot "deploy-helm-azure.ps1")
  if ($LASTEXITCODE -ne 0) { throw "deploy-helm-azure fallo" }
} else {
  Write-Host "[5/6] Build omitido (usa -SkipTerraform solo si infra ya existe)" -ForegroundColor Gray
  Write-Host "[6/6] Helm omitido" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Fase 1 desplegada - pasos finales" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "1. IP del LoadBalancer:"
Write-Host "   kubectl get svc -n rutaexpress order-service -w"
Write-Host ""
Write-Host "2. Editar terraform.tfvars:"
Write-Host '   order_api_backend_url = "http://<EXTERNAL-IP>:8080"'
Write-Host "   cd $TfDir"
Write-Host "   terraform apply"
Write-Host ""
Write-Host "Guia completa: Implementacion\README.md"
