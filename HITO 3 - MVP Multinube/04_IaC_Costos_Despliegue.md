# IaC, Despliegue y Costos — MVP Multinube
## RutaExpress Fulfillment & Transporte

> **Estado:** Código IaC en [`../Implementacion/`](../Implementacion/) — listo para `terraform plan/apply` con credenciales cloud. Sin `apply` ejecutado en este entorno de documentación.  
> **Principio:** 100% del despliegue MVP vía **Terraform** (herramienta IaC — infraestructura como código) (**Plataforma IaC (PLT-04)**). Sin consola manual salvo bootstrap de estado remoto.

> **Términos técnicos:** glosario del paquete en [`00_INDICE_COMITE.md`](00_INDICE_COMITE.md) §8.  
> **FinOps:** nube en USD (§4) + personal Lima (§5) + operación (§6) + TCO/ROI (§7). Tipo cambio referencial **S/ 3.75 / USD**.

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
| **Helm** | Despliegue AKS | Charts **OMS (APP-02)**, **Inventario (MS-INI01-02)**, **`bus-workers`** (PLT-03) |
| **OpenTelemetry Collector** | Helm chart transversal | Trazas unificadas (estándar OTel) |

### 1.2 Estructura de carpetas (repo actual)

Código en [`../Implementacion/`](../Implementacion/):

```text
Implementacion/
  terraform/
    environments/mvp/        # Orquesta módulos Azure / AWS / GCP
    modules/
      azure/                 # AKS, APIM, Event Hubs, Service Bus, SQL, Redis, KV, Monitor
      aws/                   # ECS Fargate, DynamoDB, S3, SQS, EventBridge, IAM
      gcp/                   # Cloud Run, BigQuery (sin Pub/Sub en v1)
      shared/                # naming, OTel
    bootstrap/               # Estado remoto (apply una vez)
  helm/                      # Charts AKS: OMS, Inventario, bus-workers, OTel
  apps/                      # order-service, inventory-service, bus-workers, mobile-api…
  apis/mock/                 # OpenAPI mocks APIM
```

### 1.3 Orden de despliegue (dependencias)

```text
1. Bootstrap backends (Azure Storage, S3+DynamoDB, GCS)
2. Azure: RG → Key Vault → SQL → AKS → Event Hubs → Service Bus → Azure API Management (APP-01) → Redis → Monitor
3. AWS: IAM → DynamoDB → S3 → SQS → EventBridge → ECS Fargate
4. GCP: BigQuery → Cloud Run (suscripción push desde Event Hubs vía puente)
5. Puente objetivo: EventBridge → Adaptador AWS→Azure → Event Hubs (secrets en Key Vault)
6. Helm: OMS (APP-02), Inventario (MS-INI01-02), `bus-workers` (PLT-03), OTel
7. APIM (APP-01): import OpenAPI mocks + políticas
8. Smoke tests E1–E8
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
| `aws_ecs_cluster` + `service` | ECS Fargate | 0.25 vCPU / 512 MB — API + `retry-worker` en el mismo task |
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
| `deploy-workloads` | Helm: OMS, Inventario, `bus-workers` en AKS + imágenes en registry |
| `smoke` | Escenarios E1–E8 automatizados |

---

## 4. Costos de nube (MVP mensual)

> **Supuestos:** ambiente `mvp` único (dev/demo), tráfico bajo (~500 órdenes/día prueba), 730 h/mes, región **US-East** (precios públicos hyperscaler; habitual contratar desde Perú en USD). Precios orientativos **USD/mes** (julio 2026).  
> Personal y TCO en contexto **Lima, Perú**: §5–§7.

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
- Escala campaña 180k/día requeriría ~3–5× Event Hubs TU y más nodos AKS → estimado **$1,200–1,800/mes** solo nube.
- **FinOps:** tags `project=rutaexpress`, `environment=mvp`, `cost-center=logistics`.

---

## 5. Costos de personal (equipo del MVP · Lima, Perú)

> Cifras en **USD** (práctica habitual en cloud y contratos tech). Referencia de mercado: **Lima**, tarifas de **consultoría / freelancers mid-senior** (no sueldos planilla con CTS/AFP).  
> Tipo de cambio referencial usado en este documento: **S/ 3.75 por USD** (orientativo; actualizar al día de la defensa).  
> No es nómina real de RutaExpress: sirve para TCO y ROI del MVP académico-industrial.

### 5.0 Equivalencia rápida sueldo/tarifa Lima

| Perfil (Lima) | Rango mensual full-time aprox. | Tarifa semanal usada (full) |
|---|---|---:|
| Arquitecto de soluciones | USD 2,800–3,500 (≈ S/ 10.5k–13k) | **USD 800** |
| Backend / cloud mid-senior | USD 2,200–2,800 (≈ S/ 8.3k–10.5k) | **USD 600** |
| DevOps / IaC | USD 2,400–3,000 (≈ S/ 9k–11k) | **USD 650** |
| QA | USD 1,500–2,000 (≈ S/ 5.6k–7.5k) | **USD 450** |
| Frontend / producto técnico | USD 1,800–2,300 (≈ S/ 6.8k–8.6k) | **USD 500** |

### 5.1 Construcción del MVP (one-shot · ~10 semanas)

| Rol | Dedicación | Semanas | Tarifa USD/sem | Subtotal USD | ≈ S/ |
|---|---|---:|---:|---:|---:|
| Arquitecto de soluciones | 50 % | 10 | 800 | **4,000** | 15,000 |
| Backend Azure (OMS, Inventario, `bus-workers`) | 100 % | 10 | 600 | **6,000** | 22,500 |
| Backend AWS (`mobile-api`, `retry-worker`) | 50 % | 10 | 600 | **3,000** | 11,250 |
| DevOps / IaC (Terraform, Helm, CI/CD) | 75 % | 10 | 650 | **4,875** | 18,281 |
| QA / escenarios E1–E8 | 50 % | 8 | 450 | **1,800** | 6,750 |
| Producto / demo (BFF, frontend) | 40 % | 8 | 500 | **1,600** | 6,000 |
| **Total personal construcción** | | | | **~21,275** | **~S/ 80k** |

### 5.2 Personal operativo (sostener el ambiente demo en Lima)

| Rol | Dedicación | USD/mes | ≈ S/ mes | Qué hace |
|---|---|---:|---:|---|
| DevOps part-time | ~20 % | **500** | 1,875 | `plan/apply`, secretos, smoke, FinOps |
| Soporte demo / guardia liviana | ~10 % | **200** | 750 | Arranque para comité, fallos E1–E5 |
| **Subtotal personal operativo** | | **~700** | **~2,625** | MVP demo, no producción 24×7 |

---

## 6. Costos operativos (no nube, no sueldos de build)

Gastos recurrentes locales + cloud extras para mantener el MVP usable como demo en Lima.

| Concepto | USD/mes | ≈ S/ | Notas |
|---|---:|---:|---|
| Observabilidad / alertas extras | **40** | 150 | Sobre el mínimo ya incluido en §4 |
| Backup / retención demo | **25** | 94 | SQL + evidencias S3 de prueba |
| Dominio / TLS / DNS (si aplica) | **10** | 38 | Proveedor local o global |
| Contingencia incidentes menores | **50** | 188 | ~10 % sobre nube |
| Herramientas (GitHub, boards) prorrateo | **30** | 113 | Parte atribuible al MVP |
| **Subtotal operativo** | **~155** | **~580** | |

**Operación mensual recurrente (sin personal de build):**

| Rubro | USD/mes | ≈ S/ mes |
|---|---:|---:|
| Nube (§4) — facturada en USD por hyperscalers | ~449 | ~1,684 |
| Personal operativo Lima (§5.2) | ~700 | ~2,625 |
| Operativo no-nube (§6) | ~155 | ~580 |
| **Total mensual de sostén MVP** | **~1,304** | **~S/ 4,900** |

> La nube se paga en **dólares** (Azure/AWS/GCP). El personal y gran parte del operativo se contratan en **Perú** (facturación en S/ o USD según contrato).

---

## 7. TCO y retorno de inversión (ROI)

### 7.1 Inversión del primer año (MVP + 12 meses demo · Lima)

| Rubro | Cálculo | USD | ≈ S/ |
|---|---|---:|---:|
| Personal construcción | §5.1 | **21,275** | 79,781 |
| Nube × 12 meses | 449 × 12 | **5,388** | 20,205 |
| Personal operativo × 12 | 700 × 12 | **8,400** | 31,500 |
| Operativo no-nube × 12 | 155 × 12 | **1,860** | 6,975 |
| **TCO año 1 (MVP demo)** | | **~36,920** | **~S/ 138k** |

> ~USD **37k** (~S/ **138 mil**) sostiene la **maqueta** un año en contexto Lima. No es el costo de producción a escala Cyber Days.

### 7.2 Beneficio de negocio (caso AS IS → proyección conservadora Perú)

Dolores del caso en [`01_Resumen_Empresa_RutaExpress.md`](01_Resumen_Empresa_RutaExpress.md). El MVP **no** captura el 100 %. Se usa captura **baja** y costos de fricción **ajustados a operación logística en Perú** (mano de obra y soporte más baratos que un benchmark USA).

| Dolor / oportunidad | Magnitud del caso | Captura año 1 prod (conservadora) | Beneficio anual USD |
|---|---|---|---:|
| Pedidos duplicados / reproceso | 32.000 duplicados en campaña | 15 % de ~USD 400k/año en reproceso local | **60,000** |
| Firmas / evidencias perdidas | 1.200 firmas; reclamos y reentregas | 20 % de ~USD 80k/año en fricción | **16,000** |
| Capital retenido / liquidación | USD 2.4M retenidos; 23 días | 5 % del costo de oportunidad (~8 %) | **9,600** |
| Soporte integraciones P2P / bus | Integraciones frágiles sin PLT-03 | 10 % de ~USD 120k/año en soporte Lima | **12,000** |
| **Beneficio anual conservador** | | | **~97,600** |

Supuesto: el **MVP** demuestra la arquitectura; el **beneficio** aparece al llevar el núcleo a producción operativa, no solo con el demo de ~USD 449/mes.

### 7.3 ROI y payback

| Métrica | Fórmula | Resultado |
|---|---|---|
| Inversión año 1 (TCO MVP Lima) | §7.1 | **~USD 36,920** (≈ S/ 138k) |
| Beneficio anual conservador | §7.2 | **~USD 97,600** (≈ S/ 366k) |
| **ROI año 1** | (Beneficio − Inversión) / Inversión | **~(97.6 − 36.9) / 36.9 ≈ 164 %** |
| **Payback** | Inversión / (Beneficio / 12) | **~4.5 meses** tras beneficios en producción |

**Lectura para el comité (Lima):**

1. La **nube (~449 USD/mes ≈ S/ 1,700)** es el ítem más barato; el peso real del MVP es **personal local**.
2. El **TCO año 1 ~USD 37k** es más creíble que un presupuesto “Silicon Valley”; sirve para comparar contra seguir en AS IS.
3. El **ROI ~164 %** asume captura conservadora al pasar a producción temprana; el demo solo no genera esos USD 97k.
4. Sensibilidad: si el beneficio cae a la mitad (~USD 49k), ROI año 1 ≈ **32 %** y payback ≈ **9 meses** — aún razonable para un piloto.

### 7.4 Resumen FinOps para diapositiva

| Vista | USD | ≈ Soles (S/ 3.75) |
|---|---|---|
| Nube MVP / mes | **~449** | **~1,700** |
| Sostén MVP / mes (nube + ops + personal) | **~1,300** | **~4,900** |
| Construcción (one-shot) | **~21,300** | **~80,000** |
| TCO año 1 | **~37,000** | **~138,000** |
| ROI año 1 (conservador) | **~164 %** | — |
| Payback | **~4.5 meses** | — |

---

## 8. APIs mock — despliegue en Azure API Management (APP-01)

| Mock API | Ruta | Política |
|---|---|---|
| WMS Principal (On Premises) (APP-06) | `/mock/wms/v1/*` | Circuit breaker (corte ante fallos) si latency > 2s |
| ERP Financiero (On Premises) (APP-25) | `/mock/erp/v1/*` | Async 202 + callback opcional |
| Portal | `/mock/portal/v1/tracking/{id}` | Lee BigQuery vía función |
| TMS (Transportation Management) (APP-11) | `/mock/tms/v1/manifests` | Valida schema despacho |

Implementación: OpenAPI en repo `apis/mock/`; Terraform `azurerm_api_management_api` + `policy_xml`.

---

## 9. Checklist pre-implementación (comité)

- [ ] Arquitectura hub central Azure confirmada como base del MVP
- [ ] Alcance INI-01/02/03 aceptado; INI-04/05/06 fuera de v1
- [ ] Presupuesto nube ~USD 449/mes y TCO año 1 ~USD 37k (Lima) aceptados
- [ ] Supuestos de ROI (captura conservadora, tarifas Lima) revisados — no confundir demo con beneficio de producción
- [ ] Cuentas cloud con permisos para SP/terraform
- [ ] Backend estado remoto bootstrap autorizado
- [ ] Diagramas C4 N1–N3 generados y revisados
- [ ] Nombres canónicos alineados al índice §3 (`bus-workers`, `retry-worker`, BFF del MVP)

---

*Índice del paquete: [`00_INDICE_COMITE.md`](00_INDICE_COMITE.md)*
