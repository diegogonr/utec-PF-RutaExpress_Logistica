# Implementación MVP — RutaExpress Multinube

Infraestructura como código (IaC) y despliegue del prototipo Hito 3.

> Diseño de referencia: [`HITO 3 - MVP Multinube/04_IaC_Costos_Despliegue.md`](../HITO%203%20-%20MVP%20Multinube/04_IaC_Costos_Despliegue.md)

## Estructura

```text
Implementacion/
├── terraform/
│   ├── bootstrap/          # Estado remoto (apply una vez)
│   ├── environments/mvp/   # Orquestación del ambiente demo
│   └── modules/
│       ├── azure/          # Hub: AKS, APIM, SQL, Event Hubs, Service Bus…
│       ├── aws/            # Última milla: ECS Fargate, S3, DynamoDB, SQS…
│       ├── gcp/            # CQRS: BigQuery, Cloud Run
│       └── shared/naming/  # Convención de nombres y tags
├── helm/                   # Workloads en AKS (APP-02, MS-INI01-02, bus workers)
├── apis/mock/              # OpenAPI de mocks APIM
└── .github/workflows/      # CI/CD plan/apply
```

## Prerrequisitos

| Herramienta | Versión mínima |
|---|---|
| Terraform | ≥ 1.6 |
| Azure CLI + login | `az login` |
| AWS CLI + credenciales | `aws configure` |
| Google Cloud SDK | `gcloud auth application-default login` |
| Helm | ≥ 3.12 |
| kubectl | Para AKS post-apply |

## Orden de despliegue

1. **Bootstrap** (una vez): backends de estado remoto  
2. **Terraform MVP**: Azure → AWS → GCP (módulos con dependencias)  
3. **Helm**: aplicaciones en AKS  
4. **Smoke tests**: escenarios E1–E8  

## 1. Bootstrap del estado remoto

```powershell
cd terraform/bootstrap
copy terraform.tfvars.example terraform.tfvars
# Editar terraform.tfvars con nombres únicos globales

terraform init
terraform plan
terraform apply
```

Anotar los outputs (`azure_storage_account_name`, `aws_s3_bucket`, `gcp_bucket_name`) para configurar el backend en `environments/mvp/backend.tf`.

## 2. Despliegue del ambiente MVP

```powershell
cd terraform/environments/mvp
copy terraform.tfvars.example terraform.tfvars
# Completar: subscription_id, tenant_id, project_id, etc.

terraform init
terraform plan -out=mvp.tfplan
terraform apply mvp.tfplan
```

### Variables obligatorias

Ver `terraform.tfvars.example`. Como mínimo:

- `azure_subscription_id`, `azure_tenant_id`
- `gcp_project_id`
- `sql_admin_password` (o usar Key Vault en producción)

## 3. Helm (workloads AKS)

Tras el apply, obtener credenciales AKS:

```powershell
az aks get-credentials --resource-group rg-rutaexpress-mvp --name aks-rutaexpress-mvp
```

Desplegar charts:

```powershell
cd helm
helm upgrade --install order-service ./order-service -n rutaexpress --create-namespace
helm upgrade --install inventory-service ./inventory-service -n rutaexpress
helm upgrade --install bus-workers ./bus-workers -n rutaexpress
helm upgrade --install otel ./otel -n rutaexpress
```

> Las imágenes por defecto son placeholders (`mcr.microsoft.com/azuredocs/containerapps-helloworld`). Sustituir por imágenes reales de APP-02 y MS-INI01-02 cuando exista el código.

## 4. Mocks APIM

Los OpenAPI en `apis/mock/` se importan vía Terraform (`azurerm_api_management_api`). Rutas:

| Mock | Ruta |
|---|---|
| WMS | `/mock/wms/v1/*` |
| ERP | `/mock/erp/v1/*` |
| Portal tracking | `/mock/portal/v1/tracking/{id}` |
| TMS | `/mock/tms/v1/manifests` |

## Costo estimado

~**USD 449/mes** ambiente demo (ver doc `04` §4).

## Notas importantes

- **Secretos:** nunca en `.tf` plano; usar Key Vault / Secrets Manager / variables de entorno en CI.  
- **APIM Developer:** sin SLA; adecuado para demo académica.  
- **Puente AWS→Azure:** EventBridge publica a Event Hubs; connection string en Key Vault.  
- **Bootstrap:** único paso que puede hacerse manual en consola si el equipo lo prefiere.

## CI/CD

El workflow `.github/workflows/terraform-mvp.yml` ejecuta `fmt`, `validate` y `plan` en PR; `apply` requiere aprobación manual en `main`.
