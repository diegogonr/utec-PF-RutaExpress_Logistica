# IaC, Despliegue y Costos — MVP Multinube
## RutaExpress Fulfillment & Transporte

> **Estado:** Diseño de infraestructura — sin `terraform apply` ejecutado aún.  
> **Principio:** 100% del despliegue MVP vía **Terraform** (herramienta IaC — infraestructura como código) (**Plataforma IaC (PLT-04)**). Sin consola manual salvo bootstrap de estado remoto.

> **Términos técnicos:** glosario del paquete en [`00_INDICE_COMITE.md`](00_INDICE_COMITE.md) §Glosario breve.

---

## 1. Estrategia de Infrastructure as Code

### 1.1 Herramientas seleccionadas

| Herramienta | Rol | Por qué |
|---|---|---|
| **Terraform** ≥ 1.6 | IaC (infraestructura como código) multinube | Un lenguaje, providers Azure/AWS/GCP oficiales, estado remoto |
| **Azure Storage** | Backend estado TF Azure | Blob container con lock |
| **S3 + DynamoDB** | Backend estado TF AWS | Patrón estándar locking |
| **GCS** | Backend estado TF GCP | Bucket versionado |
| **GitHub Actions** (o Azure DevOps) | CI/CD plan/apply | Aprobación manual en `mvp` |
| **Helm** | Despliegue AKS (Kubernetes administrado) | Charts (paquetes de manifiestos) **Orquestador de Pedidos (APP-02)** (aplicación del catálogo) y **Microservicio Inventario y Reservas (MS-INI01-02)** (microservicio INI-01, ID **MS-INI01-02**), más workers del **Bus de Eventos Central (PLT-03)** |
| **OpenTelemetry Collector** | Helm chart transversal | Trazas unificadas (estándar OTel) |

### 1.2 Estructura de carpetas (a crear en implementación)

```text
HITO 3 - MVP Multinube/
  terraform/
    environments/
      mvp/
        main.tf              # Orquesta módulos
        variables.tf
        outputs.tf
        terraform.tfvars.example
    modules/
      azure/
        resource_group/
        aks/
        apim/
        eventhubs/
        servicebus/
        sql/
        redis/
        keyvault/
        monitor/
      aws/
        ecs/
        dynamodb/
        s3/
        sqs_eventbridge/
        iam/
      gcp/
        cloudrun/
        bigquery/
        # pubsub/ — post-MVP; MVP v1 usa Event Hubs → Cloud Run directo
      shared/
        otel/
        naming/
    bootstrap/               # Estado remoto inicial (apply una vez)
```

### 1.3 Orden de despliegue (dependencias)

```text
1. Bootstrap backends (Azure Storage, S3+DynamoDB, GCS)
2. Azure: RG → Key Vault → SQL → AKS → Event Hubs → Service Bus → Azure API Management (APP-01) → Redis → Monitor
3. AWS: IAM → DynamoDB → S3 → SQS → EventBridge → ECS Fargate
4. GCP: BigQuery → Cloud Run (suscripción push desde Event Hubs vía puente)
5. Puente: reglas EventBridge → Event Hubs (connection string en Key Vault)
6. Helm: **Orquestador de Pedidos (APP-02)**, **Microservicio Inventario y Reservas (MS-INI01-02)**, workers **Bus de Eventos Central (PLT-03)**, OTel
7. Azure API Management (APP-01): import OpenAPI mocks + políticas
8. Smoke tests (pruebas mínimas de arranque) E1–E8
```

### 1.4 Variables de entorno MVP

| Variable | Ejemplo | Uso |
|---|---|---|
| `environment` | `mvp` | Tags FinOps (gestión financiera de la nube) |
| `azure_region` | `eastus` | Co-localizar con AWS us-east-1 |
| `aws_region` | `us-east-1` | Última milla |
| `gcp_region` | `us-east1` | Analítica |
| `eventhub_throughput_units` | `1` | Throughput (volumen de mensajes) — costo controlado |
| `aks_node_count` | `2` | MVP sin HA multi-AZ completo |
| `apim_sku` | `Developer` o `Standard_1` | Mocks + rate limit |

### 1.5 Secretos (nunca en Terraform plano)

- Connection strings Event Hubs / Service Bus → **Azure Key Vault**
- Claves AWS IAM → **Secrets Manager**
- Service account GCP → **Secret Manager**
- Azure API Management (APP-01) subscription keys → Key Vault; inyectadas a AKS vía CSI driver

---

## 2. Módulos Terraform — recursos por nube

### 2.1 Azure (~18 recursos principales)

| Recurso Terraform | Servicio | SKU MVP |
|---|---|---|
| `azurerm_resource_group` | Resource Group | `rg-rutaexpress-mvp` |
| `azurerm_kubernetes_cluster` | AKS | 2× Standard_D2s_v5 |
| `azurerm_api_management` | Azure API Management (APP-01) | Developer o Std_1 |
| `azurerm_eventhub_namespace` | Event Hubs | Standard, 1 TU |
| `azurerm_servicebus_namespace` | Service Bus | Standard |
| `azurerm_mssql_server` + `database` | Azure SQL | S1 (20 DTU) |
| `azurerm_redis_cache` | Redis | Basic C0 |
| `azurerm_key_vault` | Key Vault | Standard |
| `azurerm_log_analytics_workspace` | Monitor | PerGB2018 |
| `azurerm_application_insights` | App Insights | Vinculado LA |

### 2.2 AWS (~12 recursos principales)

| Recurso Terraform | Servicio | Config MVP |
|---|---|---|
| `aws_ecs_cluster` + `service` | ECS Fargate | 0.25 vCPU / 512 MB — API + Retry Worker en el mismo task |
| `aws_dynamodb_table` | DynamoDB | On-demand (pago por uso), outbox (cola de salida) GSI (índice secundario) |
| `aws_s3_bucket` + `kms_key` | S3 evidencias | SSE-KMS (cifrado con llaves gestionadas), lifecycle 90d |
| `aws_sqs_queue` + `dlq` | SQS | Puente + DLQ (cola de mensajes fallidos) móvil |
| `aws_cloudwatch_event_bus` | EventBridge | Reglas hacia Azure |
| `aws_iam_role` | IAM | Least privilege por servicio |

### 2.3 GCP (~8 recursos principales)

| Recurso Terraform | Servicio | Config MVP |
|---|---|---|
| `google_bigquery_dataset` + `table` | BigQuery | tracking_projection |
| `google_cloud_run_service` | Cloud Run | 1 vCPU, min 0; trigger desde Event Hubs |
| `google_service_account` | IAM | Solo Cloud Run + BQ |
| `google_secret_manager_secret` | Secretos | Puente credentials |

---

## 3. Pipeline CI/CD (diseño)

```text
PR → terraform fmt/validate → plan (3 nubes en matrix)
     → comentario coste estimado
Merge a main → plan mvp → aprobación manual → apply secuencial:
     Azure → AWS → GCP → Helm → tests
```

| Stage | Gate |
|---|---|
| `validate` | `terraform validate` + tflint |
| `plan` | Sin destroy accidental; policy check tags |
| `apply-azure` | Aprobación arquitecto |
| `apply-aws-gcp` | Tras outputs Azure (Event Hubs connection) |
| `deploy-workloads` | Helm: despliegue de aplicaciones y microservicios en AKS + imágenes en container registry |
| `smoke` | Escenarios E1–E8 automatizados (smoke test — prueba mínima end-to-end) |

---

## 4. Costos estimados por nube (MVP mensual)

> **Supuestos:** ambiente `mvp` único (dev/demo), tráfico bajo (~500 órdenes/día prueba), 730 h/mes, región US-East, sin soporte enterprise. Precios orientativos **USD/mes** (julio 2026, calculadora pública).

### 4.1 Azure

| Componente | SKU / cantidad | USD/mes estimado |
|---|---|---:|
| AKS (2 nodos D2s_v5) | 2 × ~$70 | **140** |
| Azure SQL S1 | 20 DTU | **30** |
| API Management | Developer¹ | **50** |
| Event Hubs Standard | 1 TU + ingress bajo | **25** |
| Service Bus Standard | 1M ops | **10** |
| Redis Basic C0 | 250 MB | **16** |
| Key Vault | ~10k ops | **5** |
| Log Analytics + App Insights | 5 GB ingest | **15** |
| Storage (estado TF + audit) | 50 GB | **5** |
| **Subtotal Azure** | | **~296** |

¹ Developer Azure API Management (APP-01) no tiene SLA producción; para demo académica es adecuado. Producción: Standard ~$700/mes.

### 4.2 AWS

| Componente | SKU / cantidad | USD/mes estimado |
|---|---|---:|
| ECS Fargate | 0.25 vCPU 512MB 24/7 | **38** |
| DynamoDB on-demand | 1M R/W bajo | **15** |
| S3 + KMS | 50 GB, 10k PUT | **8** |
| SQS + EventBridge | 1M requests | **5** |
| CloudWatch + X-Ray | 5 GB logs | **12** |
| Data transfer → Azure | 20 GB egress (tráfico de salida entre nubes) | **18** |
| **Subtotal AWS** | | **~93** |

### 4.3 GCP

| Componente | SKU / cantidad | USD/mes estimado |
|---|---|---:|
| Cloud Run | min 0, ~50k req + push Event Hubs | **25** |
| BigQuery | 100 GB storage + queries | **25** |
| Secret Manager | 5 secretos | **2** |
| Cloud Logging | 5 GB | **8** |
| **Subtotal GCP** | | **~60** |

### 4.4 Resumen FinOps

| Nube | USD/mes MVP | % del total | Rol |
|---|---:|---:|---|
| **Azure** | ~296 | 65% | Hub operativo (mayor peso justificado) |
| **AWS** | ~93 | 21% | Última milla |
| **GCP** | ~60 | 14% | Analítica/CQRS (separar escritura y lectura) |
| **TOTAL** | **~449** | 100% | Ambiente demo único |

**Notas:**
- No incluye licencias SaaS mock externas ni VPN a on premises.
- Escala campaña 180k/día requeriría ~3–5× Event Hubs TU y más nodos AKS → estimado **$1,200–1,800/mes** (alineado parcialmente a INI-02 del Hito 1).
- **FinOps:** tags obligatorios `project=rutaexpress`, `environment=mvp`, `cost-center=logistics` en todos los recursos.

---

## 5. APIs mock — despliegue en Azure API Management (APP-01)

| Mock API | Ruta | Política |
|---|---|---|
| WMS Principal (On Premises) (APP-06) | `/mock/wms/v1/*` | Circuit breaker (corte ante fallos) si latency > 2s |
| ERP Financiero (On Premises) (APP-25) | `/mock/erp/v1/*` | Async 202 + callback opcional |
| Portal | `/mock/portal/v1/tracking/{id}` | Lee BigQuery vía función |
| TMS (Transportation Management) (APP-11) | `/mock/tms/v1/manifests` | Valida schema despacho |

Implementación: OpenAPI en repo `apis/mock/`; Terraform `azurerm_api_management_api` + `policy_xml`.

---

## 6. Checklist pre-implementación (comité aprueba antes de codificar)

- [ ] Arquitectura hub central Azure confirmada como base del MVP
- [ ] Alcance INI-01/02/03 aceptado; INI-04/05/06 fuera de v1
- [ ] Presupuesto ~USD 449/mes ambiente demo aceptado
- [ ] Cuentas cloud con permisos para SP/terraform
- [ ] Backend estado remoto bootstrap autorizado
- [ ] Diagramas C4 N1–N3 generados y revisados

---

*Índice del paquete: [`00_INDICE_COMITE.md`](00_INDICE_COMITE.md)*
