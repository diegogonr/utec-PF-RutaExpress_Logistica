# Guía de implementación — RutaExpress MVP Multinube

Despliegue paso a paso en **3 fases**: **Azure** (hub) → **AWS** (última milla) → **GCP** (lectura CQRS).

> Diseño: [`HITO 3 - MVP Multinube/04_IaC_Costos_Despliegue.md`](../HITO%203%20-%20MVP%20Multinube/04_IaC_Costos_Despliegue.md)  
> Catálogo servicios: [`05_Servicios_por_Nube_MVP.md`](../HITO%203%20-%20MVP%20Multinube/05_Servicios_por_Nube_MVP.md)

---

## Índice

1. [Qué hace cada fase](#1-qué-hace-cada-fase)
2. [Recursos por nube (detalle)](#2-recursos-por-nube-detalle)
   - [Leyenda APP / MS / PLT](#leyenda-de-tipos-de-componente)
   - [Azure — mapa recurso → componente](#21-azure--fase-1-296-usdmes--escenarios-e1e5)
   - [AWS](#22-aws--fase-2-93-usdmes--escenarios-e6e7)
   - [GCP](#23-gcp--fase-3-60-usdmes--escenario-e8)
   - [Catálogo de componentes](#25-catálogo-de-componentes-app--ms--plt--mock)
3. [Estructura del repo](#3-estructura-del-repo)
4. [Instalar herramientas (una vez)](#4-instalar-herramientas-una-vez)
5. [Docker — qué es y cómo usarlo aquí](#5-docker--qué-es-y-cómo-usarlo-aquí)
6. [FASE 1 — Azure (E1–E5)](#6-fase-1--azure-e1e5)
7. [FASE 2 — AWS (E6–E7)](#7-fase-2--aws-e6e7)
8. [FASE 3 — GCP (E8)](#8-fase-3--gcp-e8)
9. [Probar todos los escenarios E1–E8](#9-probar-todos-los-escenarios-e1e8)
   - [Mapa rápido por nube (9.1)](#91-mapa-rápido-qué-nube-interviene-en-cada-prueba)
10. [Problemas frecuentes](#10-problemas-frecuentes)
11. [Costos y destruir recursos](#11-costos-y-destruir-recursos)
12. [Scripts](#scripts)

---

## 1. Qué hace cada fase

| Fase | Nube | Qué crea Terraform | Apps | Escenarios demo | Costo aprox./mes |
|:---:|---|---|---|---|---:|
| **1** | **Azure** | AKS, APIM, SQL, Redis, Event Hubs, Service Bus, ACR, Monitor | order-service, inventory-service, bus-workers | E1–E5 | ~296 USD |
| **2** | **AWS** | ECS Fargate, ALB, **ECR**, DynamoDB, S3, SQS, EventBridge | mobile-api (stub) | E6–E7 | +93 USD |
| **3** | **GCP** | Cloud Run, BigQuery, Secret Manager | proyector CQRS | E8 | +60 USD |

**Total multinube (3 fases):** ~**449 USD/mes** mientras todo esté encendido.

> **¿Qué APP, MS o PLT resuelve cada recurso cloud?** Ver [§2 Recursos por nube](#2-recursos-por-nube-detalle) y el [catálogo de componentes](#25-catálogo-de-componentes-app--ms--plt--mock).

Variables en `terraform/environments/mvp/terraform.tfvars`:

```hcl
enable_aws = false   # Fase 1
enable_gcp = false   # Fase 1

enable_aws = true    # Fase 2
enable_gcp = false

enable_aws = true    # Fase 3
enable_gcp = true
```

---

## 2. Recursos por nube (detalle)

Catálogo completo de lo que crea **Terraform** y lo que despliegan **Helm/apps** en cada fase.

> **UTEC (tu caso):** Terraform **no crea** el Resource Group. Usa el que ya tienes asignado (ej. `rg_Diego_Gonzales`) como contenedor. El script `setup-fase1.ps1` configura esto automáticamente en `terraform.tfvars`:
> ```hcl
> azure_create_resource_group = false
> azure_resource_group_name   = "rg_Diego_Gonzales"
> ```

**Leyenda de tipos de componente:**

| Tipo | Significado | Ejemplo en el MVP |
|---|---|---|
| **APP** | Aplicación de negocio (caso de uso completo) | APP-02 Orquestador de Pedidos |
| **MS** | Microservicio de un dominio acotado | MS-INI01-02 Inventario |
| **PLT** | Plataforma transversal (varias apps la usan) | PLT-03 Bus, PLT-01 Observabilidad |
| **mock** | Simulación de sistema legado | mock-wms (sustituye APP-06 WMS real) |
| **infra** | Solo infraestructura cloud (sin lógica de negocio) | ACR, VPC, IAM |

### 2.1 Azure — Fase 1 (~296 USD/mes) · Escenarios E1–E5

**Rol:** Hub operativo (API, OMS, inventario, bus de eventos).

#### Mapa recurso → componente → qué resuelve

| Recurso Azure | Tipo | Componente | Qué resuelve / quién lo usa | Escenario |
|---|---|---|---|:---:|
| **Resource Group** | infra | — | Contenedor UTEC; **no lo crea Terraform** | — |
| **APIM** + API `orders` | APP | **APP-01** Gateway + ruta a APP-02 | Entrada HTTP: `POST /api/v1/orders`, OAuth, rate limit | E1–E4 |
| **APIM** API `mock-wms` | mock | **APP-06** WMS (simulado) | Respuestas WMS sin servidor real; E4 fuerza 503 | E4 |
| **APIM** API `mock-erp` | mock | ERP legado (simulado) | Confirmaciones ERP ficticias en la Saga | — |
| **APIM** API `mock-portal` | mock | **APP-18** Portal tracking | `GET /tracking/{id}` — lectura CQRS vía stub o BQ | E8 |
| **APIM** API `mock-tms` | mock | TMS legado (simulado) | Mensajes transporte hacia cola `q-mock-tms` | — |
| **AKS** | infra | — | Runtime donde corren APP-02, MS y workers | E1–E5 |
| **order-service** (pod Helm) | APP | **APP-02** Orquestador de Pedidos | Saga, idempotencia, outbox, orquestación de órdenes | E1–E5 |
| **inventory-service** (pod Helm) | MS | **MS-INI01-02** Inventario | Reserva/libera stock; valida disponibilidad | E3, E4 |
| **bus-workers** (pod Helm) | PLT | **PLT-03** Bus (lado publicador) | Lee outbox SQL → publica a **Event Hubs** (`eh-canonical`) | E5 (parcial) |
| **otel** (pod Helm, opcional) | PLT | **PLT-01** Observabilidad | Trazas OpenTelemetry desde pods AKS | — |
| **Azure SQL** `db-orders` | infra | APP-02 | Estado transaccional órdenes, Saga, tabla outbox | E1–E5 |
| **Azure SQL** `db-inventory` | infra | MS-INI01-02 | Stock, reservas, outbox inventario | E3, E4 |
| **Redis** | infra | APP-02 + MS | Caché idempotencia y deduplicación (`Idempotency-Key`) | E1, E2 |
| **Event Hubs** `eh-canonical` | PLT | **PLT-03** Bus (stream) | Eventos canónicos fan-out hacia GCP y otros consumidores | E5, E8 |
| **Service Bus** `q-inventory` | PLT | **PLT-03** Bus (cola) | Cola dedicada al microservicio inventario | E3–E5 |
| **Service Bus** `q-mock-tms` | PLT | **PLT-03** + mock TMS | Cola mensajes transporte simulados | — |
| **Service Bus** `q-dlq` | PLT | **PLT-03** DLQ | Mensajes fallidos; replay manual en portal Azure | E5 |
| **Key Vault** | PLT | **PLT-02** IAM (secretos) | Guarda connection strings de Event Hubs y Service Bus | — |
| **Entra ID** | PLT | **PLT-02** IAM | OAuth/JWT en APIM | — |
| **Log Analytics + App Insights** | PLT | **PLT-01** Observabilidad | Logs, métricas y trazas del hub Azure | — |
| **ACR** | infra | PLT-04 IaC (artefactos) | Registro de imágenes Docker de las apps | — |
| **Firewall SQL** | infra | APP-02 + MS | Permite que pods AKS conecten a SQL | — |

> Solo si tienes rol **Contributor en toda la suscripción** (no es el caso UTEC típico) puedes poner `azure_create_resource_group = true` y Terraform crearía `rg-rutaexpress-mvp`. En UTEC deja siempre `false`.

---

### 2.2 AWS — Fase 2 (+93 USD/mes) · Escenarios E6–E7

**Rol:** Última milla, evidencias, puente hacia Azure. Se activa con `enable_aws = true`.

#### Mapa recurso → componente → qué resuelve

| Recurso AWS | Tipo | Componente | Qué resuelve / quién lo usa | Escenario |
|---|---|---|---|:---:|
| **ECS Fargate** + **ALB** | infra | — | Runtime y entrada HTTP del backend móvil | E6, E7 |
| **mobile-api** (contenedor ECS) | APP | **APP-15** App Conductores | API móvil: completar entregas, sync offline, retry worker | E6 |
| **DynamoDB** | infra | APP-15 | Outbox local del móvil cuando no hay red; sync al reconectar | E6 |
| **S3** + **KMS** | infra | **APP-16** Evidencias de entrega | Fotos/firmas cifradas; validación hash SHA-256 | E7 |
| **SQS** + **DLQ** | PLT | Puente **INI-03** → Azure | Buffer de mensajes móvil hacia el hub (Event Hubs) | E6 |
| **EventBridge** | PLT | Puente multinube | Publica eventos de entrega desde AWS hacia Azure | E6 |
| **VPC, subnets, SG, TG** | infra | — | Red y seguridad del ALB/ECS | — |
| **IAM roles** | PLT | **PLT-02** IAM | Permisos ECS sobre S3, DynamoDB, SQS | — |
| **CloudWatch Logs** | PLT | **PLT-01** Observabilidad | Logs del `mobile-api` | — |

> La app móvil en el dispositivo del conductor no se despliega en cloud; habla con **APP-15** vía ALB.

---

### 2.3 GCP — Fase 3 (+60 USD/mes) · Escenario E8

**Rol:** Solo lectura analítica (CQRS). Se activa con `enable_gcp = true`.

#### Mapa recurso → componente → qué resuelve

| Recurso GCP | Tipo | Componente | Qué resuelve / quién lo usa | Escenario |
|---|---|---|---|:---:|
| **Cloud Run** (proyector) | APP | Proyector **CQRS** (lectura) | Consume eventos de Event Hubs → escribe proyección en BigQuery | E8 |
| **BigQuery** dataset + tabla | infra | APP-18 (lectura) | Vista materializada de tracking; no escribe órdenes | E8 |
| **Secret Manager** | PLT | **PLT-02** + puente Azure | Credencial para leer Event Hubs desde GCP | E8 |
| **Service Account + IAM** | PLT | **PLT-02** IAM | Identidad del proyector con permiso en BigQuery | — |
| **mock-portal** (APIM Azure) | mock | **APP-18** Portal tracking | Expone `GET /tracking/{id}` — mock MVP (`scenario: E8`); proyeccion BQ en GCP (fase 3) | E8 |

> **CQRS:** APP-02 escribe en Azure (comando); el proyector GCP solo **lee** y proyecta. No hay escritura transaccional en GCP.

> **Prueba E8 en Postman:** la respuesta HTTP sale de **APIM (Azure)**. GCP se demuestra con la infra desplegada (Cloud Run + BigQuery en consola), no en el clic del GET. Ver **§8.3** y **§9.1**.

---

### 2.4 Transversal (las 3 nubes)

| Recurso / Herramienta | Tipo | Componente | Qué resuelve |
|---|---|---|---|
| **Terraform** | PLT | **PLT-04** IaC | Crea infra en Azure, AWS y GCP de forma reproducible |
| **Estado Terraform** (bootstrap) | infra | PLT-04 | Almacena el state remoto (opcional) |
| **Helm** | PLT | PLT-04 | Despliega pods APP-02, MS-INI01-02 y workers en AKS |
| **OpenAPI mocks** | mock | APP-01 APIM | Contratos YAML importados en APIM |

```text
Cliente B2B ──► APP-01 APIM ──► APP-02 order-service ──► MS-INI01-02 inventory-service
                                      │                        │
                                      └──── PLT-03 Bus ◄───────┘
                                                │
                    APP-15 mobile-api (AWS) ◄───┘ puente EventBridge/SQS
                                                │
                    Proyector CQRS (GCP) ──► BigQuery ◄── APP-18 mock-portal
```

### 2.5 Catálogo de componentes (APP / MS / PLT / mock)

Vista inversa: **desde el componente de negocio** hacia el recurso cloud que lo implementa.

#### Aplicaciones (APP)

| ID | Nombre | Tipo | Nube | Recurso / código que lo implementa | Qué hace | Escenario |
|---|---|:---:|---|---|---|:---:|
| **APP-01** | API Management (Gateway) | APP | Azure | **APIM** `apim-rutaexpress-mvp` | Puerta de entrada HTTP, OAuth, rate limit, enruta a backends | E1–E4 |
| **APP-02** | Orquestador de Pedidos (OMS) | APP | Azure | Pod **order-service** en AKS + SQL `db-orders` + Redis | Saga, idempotencia, outbox, creación de órdenes | E1–E5 |
| **APP-06** | WMS legado | mock | Azure | API APIM **mock-wms** (no hay servidor WMS real) | Simula almacén; E4 devuelve 503 con header | E4 |
| **APP-15** | App de Conductores | APP | AWS | Contenedor **mobile-api** en ECS Fargate + ALB + DynamoDB | API móvil, sync offline, retry worker | E6 |
| **APP-16** | Evidencias de entrega | APP | AWS | **S3** + **KMS** (consumido por mobile-api) | Fotos/firmas cifradas, hash SHA-256 | E7 |
| **APP-18** | Portal tracking B2B | mock | Azure + GCP | API APIM **mock-portal** + lectura **BigQuery** | `GET /tracking/{id}` — vista CQRS de seguimiento | E8 |

#### Microservicios (MS)

| ID | Nombre | Tipo | Nube | Recurso / código que lo implementa | Qué hace | Escenario |
|---|---|:---:|---|---|---|:---:|
| **MS-INI01-02** | Inventario y reservas | MS | Azure | Pod **inventory-service** en AKS + SQL `db-inventory` | Reserva/libera stock; valida disponibilidad | E3, E4 |

> **MS ≠ APP:** el inventario es un dominio acotado llamado por APP-02; no es una aplicación de negocio completa por sí solo.

#### Plataformas (PLT)

| ID | Nombre | Tipo | Nube | Recurso que lo implementa | Qué hace | Escenario |
|---|---|:---:|---|---|---|:---:|
| **PLT-01** | Observabilidad | PLT | Azure | Log Analytics + App Insights + pod **otel** (opcional) | Logs, métricas, trazas OpenTelemetry | — |
| **PLT-01** | Observabilidad | PLT | AWS | CloudWatch Logs | Logs del mobile-api | E6–E7 |
| **PLT-02** | IAM y secretos | PLT | Azure | **Entra ID** + **Key Vault** | OAuth en APIM; secretos del bus | — |
| **PLT-02** | IAM | PLT | AWS | **IAM roles** + **KMS** | Permisos ECS; cifrado S3 | E6–E7 |
| **PLT-02** | Secretos | PLT | GCP | **Secret Manager** + Service Account | Credencial puente Event Hubs | E8 |
| **PLT-03** | Bus de eventos central | PLT | Azure | **Event Hubs** + **Service Bus** (infra) + **bus-workers** (outbox → EH) | Stream, colas, DLQ; publicación outbox en MVP solo a Event Hubs | E5, E8 |
| **PLT-03** | Puente móvil → hub | PLT | AWS | **SQS** + **EventBridge** | Envía eventos de entrega desde AWS hacia Azure | E6 |
| **PLT-04** | IaC | PLT | Las 3 | **Terraform** + **Helm** + **ACR** | Provisiona infra y despliega artefactos | — |

#### Mocks de legado (no son APP reales en MVP)

| Mock APIM | Simula | Recurso | Escenario |
|---|---|---|:---:|
| **mock-erp** | ERP corporativo | Solo APIM (respuestas estáticas) | — |
| **mock-tms** | TMS transporte | APIM + cola Service Bus `q-mock-tms` | — |
| **mock-wms** | APP-06 WMS | APIM (política 503 en E4) | E4 |
| **mock-portal** | APP-18 portal | APIM (+ BigQuery en fase 3) | E8 |

#### Proyector CQRS (GCP — no es APP de escritura)

| Componente | Tipo | Nube | Recurso | Qué hace | Escenario |
|---|---|---|---|---|:---:|
| Proyector CQRS | lectura | GCP | **Cloud Run** + **BigQuery** | Consume Event Hubs → proyecta filas de tracking; **no escribe órdenes** | E8 |

#### Infraestructura pura (sin componente de negocio)

| Recurso | Nube | Nota |
|---|---|---|
| **Resource Group** `rg_Diego_Gonzales` | Azure | **UTEC: no lo crea Terraform** — solo contenedor |
| **AKS** | Azure | Runtime de pods; no es APP ni MS |
| **ACR** | Azure | Registro Docker |
| **Firewall SQL** | Azure | Conectividad AKS → SQL |
| **VPC, subnets, SG, ALB TG** | AWS | Red |
| **Cloud Run IAM invoker** | GCP | Permiso técnico |

> Catálogo ampliado con explicaciones: [`05_Servicios_por_Nube_MVP.md`](../HITO%203%20-%20MVP%20Multinube/05_Servicios_por_Nube_MVP.md)

---

## 3. Estructura del repo

```text
Implementacion/
├── README.md                 ← esta guía
├── apps/
│   ├── order-service/        APP-02 — órdenes, Saga, idempotencia
│   ├── inventory-service/    MS-INI01-02 — reservas stock
│   ├── bus-workers/          PLT-03 — outbox → Event Hubs
│   └── mobile-api/           APP-15 — backend móvil (fase 2)
├── scripts/
│   ├── setup-fase1.ps1       Automatiza fase 1 completa
│   ├── build-push-images.ps1 Docker build + push a ACR
│   ├── deploy-helm-azure.ps1 Helm en AKS
│   ├── phase2-aws.ps1        Terraform fase 2 (phase2.tfplan)
│   ├── build-push-mobile-aws.ps1  Docker push mobile-api a ECR (obligatorio E6)
│   ├── phase3-gcp.ps1
│   └── test-order-api.ps1    POST orders vía script `& ...` (§6.7)
├── terraform/environments/mvp/
├── helm/
├── postman/                  Colección Postman E1-E8 (§6.7, §7.3)
└── apis/mock/                OpenAPI para APIM
```

---

## 4. Instalar herramientas (una vez)

### 4.1 Instalar con winget (Windows)

```powershell
winget install Hashicorp.Terraform
winget install Microsoft.AzureCLI
winget install Amazon.AWSCLI
winget install Google.CloudSDK
winget install Kubernetes.kubectl
winget install Helm.Helm
winget install Docker.DockerDesktop
# Opcional — pruebas HTTP (§6.7):
# winget install Postman.Postman
```

### 4.2 Verificar instalación

```powershell
terraform version
az version
kubectl version --client
helm version
docker version    # debe mostrar Client Y Server (Docker Desktop corriendo)
```

| Herramienta | Fase 1 | Fase 2 | Fase 3 |
|---|:---:|:---:|:---:|
| Terraform | ✅ | ✅ | ✅ |
| Azure CLI | ✅ | ✅ | ✅ |
| Docker Desktop | ✅ | opcional | opcional |
| kubectl + Helm | ✅ | — | — |
| AWS CLI | — | ✅ | ✅ |
| Google Cloud SDK | — | — | ✅ |

---

## 5. Docker — qué es y cómo usarlo aquí

**Docker** empaqueta cada app Node.js en una **imagen** (contenedor portable).

```text
apps/order-service  →  docker build  →  imagen local
                    →  docker push   →  Azure Container Registry (ACR)
                    →  AKS descarga  →  pod corriendo en Kubernetes
```

### Pasos Docker (solo una vez)

1. Instalar **Docker Desktop**
2. Abrirlo y esperar **Docker Desktop is running** (icono verde)
3. Verificar: `docker version` → debe aparecer **Server**

### ¿Tienes que escribir comandos Docker?

**No**, si usas los scripts. `build-push-images.ps1` hace build + push por ti.

Comandos manuales (solo referencia):

```powershell
az acr login --name acrrutaexpressmvp
cd Implementacion\apps\order-service
docker build -t acrrutaexpressmvp.azurecr.io/order-service:latest .
docker push acrrutaexpressmvp.azurecr.io/order-service:latest
```

> El nombre del ACR sale de `terraform output -raw acr_login_server` (sin `.azurecr.io`).

---

## 6. FASE 1 — Azure (E1–E5)

### 6.1 Orden de ejecución

Cuenta **UTEC Posgrado**: recursos en `rg_Diego_Gonzales` (Terraform **no** crea el Resource Group).

```text
terraform init → plan → apply   (~30–45 min, APIM lento)
build-push-images.ps1           (Docker → ACR)
deploy-helm-azure.ps1           (Helm → AKS)
kubectl get svc                 (IP LoadBalancer)
editar tfvars + terraform apply (conectar APIM)
Invoke-RestMethod               (probar E1)
```

| Paso | Acción | Comando |
|:---:|---|---|
| 1 | Login Azure | `az login` |
| 2 | Suscripción UTEC | `az account set --subscription "088b9168-fdd5-4280-83de-02aaee8b9daf"` |
| 3 | Docker Desktop | Abrir → **Running** |
| 4 | Ir a Terraform | `cd Implementacion\terraform\environments\mvp` |
| 5 | `terraform.tfvars` | Plantilla §6.2 |
| 6 | Infra Azure | `terraform init` → `terraform plan -out phase1.tfplan` → `terraform apply phase1.tfplan` |
| 7 | Imágenes → ACR | `cd ..\..\..\scripts` → `.\build-push-images.ps1` |
| 8 | Apps en AKS | `.\deploy-helm-azure.ps1` |
| 9 | IP LoadBalancer | `kubectl get svc -n rutaexpress order-service -w` |
| 10 | APIM → backend | Editar `order_api_backend_url` → `terraform apply` (§6.6) |
| 11 | Demo E1 | `Invoke-RestMethod` (§6.7) |

> Si cambias `terraform.tfvars`, **regenera el plan** (`terraform plan -out phase1.tfplan`).

**Atajo con script** (pasos 5–8):

```powershell
cd Implementacion\scripts
.\setup-fase1.ps1                    # infra + build + helm
.\setup-fase1.ps1 -SkipTerraform     # solo build + helm (infra ya aplicada)
```

---

### 6.2 Login y `terraform.tfvars`

**Qué hace:** autentica tu PC contra Microsoft Azure.

```powershell
az login
```

Se abre el navegador → inicia sesión con tu cuenta (`@uteclimaperu.onmicrosoft.com`).

**Verificar sesión:**

```powershell
az account show --output table
```

**Suscripción UTEC Posgrado (ejemplo):**

```powershell
az account set --subscription "088b9168-fdd5-4280-83de-02aaee8b9daf"
az account show --query "{Name:name, Id:id, Tenant:tenantId}" -o table
```

| Campo | Valor UTEC |
|---|---|
| Subscription ID | `088b9168-fdd5-4280-83de-02aaee8b9daf` |
| Tenant ID | `8a596301-ca34-484d-b823-b330030e539f` |
| Resource Group | `rg_Diego_Gonzales` |
| VM AKS | `Standard_D2s_v3` |

```powershell
cd Implementacion\terraform\environments\mvp
notepad terraform.tfvars
```

```hcl
enable_aws = false
enable_gcp = false

azure_create_resource_group = false
azure_resource_group_name   = "rg_Diego_Gonzales"

project               = "rutaexpress"
environment           = "mvp"
azure_subscription_id = "088b9168-fdd5-4280-83de-02aaee8b9daf"
azure_tenant_id       = "8a596301-ca34-484d-b823-b330030e539f"
azure_region          = "eastus"
sql_admin_login       = "sqladmin"
sql_admin_password    = "TU_PASSWORD_COMPLEJO"   # min 12 chars; 3 de: A/a/0/!
aks_node_count        = 2
aks_vm_size           = "Standard_D2s_v3"
apim_sku              = "Developer_1"
apim_publisher_email  = "tu-email@uteclimaperu.onmicrosoft.com"
order_api_backend_url = "http://127.0.0.1:8080"  # actualizar en §6.6
```

Guardar con **Ctrl+S** antes de continuar.

---

### 6.3 Infraestructura Terraform

```powershell
cd Implementacion\terraform\environments\mvp
terraform init
terraform plan -out phase1.tfplan
terraform apply phase1.tfplan
```

En el plan debe aparecer `data.azurerm_resource_group.existing` (~31 recursos).

Si corriges `terraform.tfvars` tras un error:

```powershell
Remove-Item phase1.tfplan -ErrorAction SilentlyContinue
terraform plan -out phase1.tfplan
terraform apply phase1.tfplan
```

| Recurso Terraform | Servicio Azure | Componente |
|---|---|---|
| `azurerm_kubernetes_cluster` | **AKS** | APP-02, MS, workers |
| `azurerm_api_management` | **APIM** | APP-01 + mocks |
| `azurerm_mssql_server` | **Azure SQL** | APP-02 + MS-INI01-02 |
| `azurerm_redis_cache` | **Redis** | Idempotencia E1/E2 |
| `azurerm_eventhub_namespace` | **Event Hubs** | PLT-03 stream |
| `azurerm_servicebus_namespace` | **Service Bus** | Colas + DLQ E5 |
| `azurerm_container_registry` | **ACR** | Imágenes Docker |

---

### 6.4 Imágenes Docker → ACR

```powershell
cd Implementacion\scripts
.\build-push-images.ps1
```

Publica `order-service`, `inventory-service`, `bus-workers` en `acrrutaexpressmvp.azurecr.io`.

---

### 6.5 Helm en AKS

```powershell
.\deploy-helm-azure.ps1
```

Ejecuta `az aks get-credentials`, crea namespace `rutaexpress` e instala:

| Chart | Componente |
|---|---|
| `order-service` | APP-02 |
| `inventory-service` | MS-INI01-02 |
| `bus-workers` | PLT-03 |
| `otel` | PLT-01 |

Si `kubectl` falla con `localhost:8080`:

```powershell
az aks get-credentials --resource-group rg_Diego_Gonzales --name aks-rutaexpress-mvp --overwrite-existing
kubectl get pods -n rutaexpress
```

---

### 6.6 Conectar APIM al backend

```powershell
kubectl get svc -n rutaexpress order-service -w
```

Cuando `EXTERNAL-IP` tenga valor, editar `terraform.tfvars`:

```hcl
order_api_backend_url = "http://<EXTERNAL-IP>:8080"
```

```powershell
cd Implementacion\terraform\environments\mvp
terraform apply
```

---

### 6.7 Probar escenarios E1–E5

#### Preparación (una vez por sesión)

Carga variables de sesión:

```powershell
cd Implementacion\terraform\environments\mvp
$apim = terraform output -raw apim_gateway_url

$subKey = az rest --method post `
  --url "https://management.azure.com/subscriptions/088b9168-fdd5-4280-83de-02aaee8b9daf/resourceGroups/rg_Diego_Gonzales/providers/Microsoft.ApiManagement/service/apim-rutaexpress-mvp/subscriptions/master/listSecrets?api-version=2022-08-01" `
  --query primaryKey -o tsv
```

O en portal: **APIM** → **Subscriptions** → **Built-in all-access subscription** → **Show/Hide keys**.

> Si `az rest` falla con `ManagementApiRequestFailed`, APIM Developer está en mantenimiento: copia la key desde el portal o espera 10–15 min.

**Enviar petición** (usa `&` al inicio; script en `Implementacion/scripts/test-order-api.ps1`):

```powershell
& ..\..\..\scripts\test-order-api.ps1 -ApimBaseUrl $apim -Headers $headers -Body $body
```

---

#### E1 — Crear orden con idempotencia

**De qué trata:** Un cliente B2B crea un pedido por primera vez. Valida el flujo completo del hub Azure.

**Flujo:** Cliente → **APIM** → **order-service** (APP-02) → reserva en **inventory-service** (MS) → confirmación en **mock WMS** → orden en SQL + evento en outbox.

**Cómo probar:** `Idempotency-Key` **nueva** + body con `quantity: 1`.

```powershell
$key = [guid]::NewGuid().ToString()
$headers = @{
  "Idempotency-Key"           = $key
  "Ocp-Apim-Subscription-Key" = $subKey
}
$body = '{"customerId":"B2B-001","items":[{"sku":"SKU-001","quantity":1}]}'

& ..\..\..\scripts\test-order-api.ps1 -ApimBaseUrl $apim -Headers $headers -Body $body
```

**Respuesta esperada:** HTTP **201** — `orderId`, `status: CONFIRMED`, `scenario: E1`. PowerShell **no** sale en rojo.

**Postman:** request **E1** en `Implementacion/postman/RutaExpress-MVP-Azure.postman_collection.json`.

---

#### E2 — Reintento / deduplicación

**De qué trata:** El cliente reenvía el mismo pedido (timeout de red, doble clic). El sistema no debe crear una orden duplicada ni reservar stock dos veces.

**Flujo:** Misma `Idempotency-Key` y mismo body → Redis o hash en SQL detectan duplicado → devuelve la orden existente.

**Cómo probar:** Repite el comando de E1 **sin cambiar** `$headers` ni `$body`.

```powershell
& ..\..\..\scripts\test-order-api.ps1 -ApimBaseUrl $apim -Headers $headers -Body $body
```

**Respuesta esperada:** HTTP **409** — `{"error":"Orden duplicada (E2)","orderId":"...","status":"CONFIRMED"}` con el **mismo** `orderId` de E1.

**PowerShell:** puede salir en rojo; es **éxito** si el JSON dice `E2` y el `orderId` coincide.

**Postman:** request **E2** (reutiliza `idempotency_key` generada en E1).

---

#### E3 — Sin stock suficiente

**De qué trata:** El cliente pide más unidades de las disponibles (stock inicial ≈ 100 en `SKU-001`). También puedes probar **E3** con `SKU-002`…`SKU-005` (catálogo sin stock en el CD demo).

**Flujo:** order-service pide reserva → **inventory-service** rechaza → la orden **no** se confirma.

**Cómo probar:** Key **nueva** + `quantity: 9999`.

```powershell
$bodyE3 = '{"customerId":"B2B-002","items":[{"sku":"SKU-001","quantity":9999}]}'
$h3 = @{
  "Idempotency-Key"           = [guid]::NewGuid().ToString()
  "Ocp-Apim-Subscription-Key" = $subKey
}
& ..\..\..\scripts\test-order-api.ps1 -ApimBaseUrl $apim -Headers $h3 -Body $bodyE3
```

**Respuesta esperada:** HTTP **409** — `{"error":"Inventario insuficiente (E3)"}`.

**PowerShell:** sale en rojo; es **éxito** si el mensaje contiene `E3`.

**Postman:** request **E3**.

---

#### E4 — WMS degradado (Saga compensa)

**De qué trata:** El almacén (WMS) falla después de reservar stock. La Saga debe **compensar** liberando la reserva.

**Flujo:** Reserva OK → mock WMS devuelve **503** (header `X-Mock-Wms-Status: 503`) → order-service libera stock → orden no confirmada.

**Cómo probar:** Key **nueva** + **`customerId` distinto a E1** (`B2B-E4`) + `quantity: 1`. Si repites el body de E1, obtendrás E2 aunque la key sea nueva.

```powershell
$bodyE4 = '{"customerId":"B2B-E4","items":[{"sku":"SKU-001","quantity":1}]}'
$h4 = @{
  "Idempotency-Key"           = [guid]::NewGuid().ToString()
  "X-Mock-Wms-Status"         = "503"
  "Ocp-Apim-Subscription-Key" = $subKey
}
& ..\..\..\scripts\test-order-api.ps1 -ApimBaseUrl $apim -Headers $h4 -Body $bodyE4
```

**Respuesta esperada:** HTTP **503** — `{"error":"WMS no confirmó (E4)","orderId":"..."}`.

**Si obtienes `CONFIRMED` / `E1`:** el pod `order-service` desplegado es anterior al fix de E4. Vuelve a publicar imagen y Helm:

```powershell
cd Implementacion\scripts
.\build-push-images.ps1
.\deploy-helm-azure.ps1
cd ..\terraform\environments\mvp
terraform apply   # reenvía header X-Mock-Wms-Status en política APIM orders
```

Luego prueba de nuevo con `customerId` nuevo (ej. `B2B-E4-4`).

**PowerShell:** sale en rojo; es **éxito** si el mensaje contiene `E4`.

**Postman:** request **E4** (`B2B-E4` + header `X-Mock-Wms-Status: 503`).

---

#### E5 — DLQ / replay

**De qué trata:** Cuando un **consumidor del bus** no puede procesar un mensaje (schema inválido, error de negocio no recuperable, agotar reintentos), Azure lo mueve a una **dead-letter queue (DLQ)**. Operaciones revisa el payload y puede hacer **replay** (reproceso auditado).

**No confundir con E4:** E4 es fallo **HTTP síncrono** del mock WMS (`503`) — la orden compensa y responde al cliente. E5 es fallo **asíncrono en el bus** — el mensaje queda en cola para revisión.

**¿Si E1–E4 “fallan”, van a DLQ en un flujo normal? → No**

| Escenario | Qué falla | ¿Hay mensaje en el bus? | ¿Va a DLQ? |
|---|---|:---:|:---:|
| **E1** OK | — | Sí (outbox → Event Hubs; en TO-BE también `q-inventory`) | No (si el consumidor procesa bien) |
| **E2** duplicado | HTTP 409 antes de crear orden nueva | No | **No** |
| **E3** sin stock | HTTP 409 en reserva inventario (saga corta) | **No** — nunca llega al outbox | **No** |
| **E4** WMS 503 | HTTP 503; compensa y libera stock | **No** — la orden no se confirma ni escribe outbox | **No** |
| **E5** | Mensaje **ya publicado** y el **consumidor** no puede procesarlo | Sí | **Sí** → `$deadletterqueue` |

En resumen: **DLQ no es para errores HTTP de la Saga (E2–E4)**. Es para mensajes **asíncronos** que ya están en cola y el worker falla o agota reintentos.

**Flujo normal (TO-BE) donde sí aparece E5:**

```text
E1 exitoso → outbox → bus publica en q-inventory
       → worker consumidor lee el mensaje
       → error (schema inválido, dependencia caída, etc.)
       → reintentos → agota max_delivery_count → $deadletterqueue
```

**En el MVP hoy:** E1 escribe outbox y **bus-workers** manda a **Event Hubs**, pero **no** a `q-inventory` y **no hay consumidor**. Por eso la demo E5 en Postman **simula** el tramo que falta: encolar en `q-inventory` + abandon ×10 = mismo efecto que un consumidor que siempre falla.

---

**Cómo funciona en el diseño (TO-BE / dossier)**

```text
APP-02 crea orden → outbox SQL → bus-workers publica evento
       → Service Bus q-inventory (o Event Hubs)
       → worker consumidor valida el mensaje
              ├─ OK → procesa
              └─ FALLO / N reintentos → DLQ ($deadletterqueue o q-dlq central)
       → operador: peek → replay auditado
```

| Cola | Rol |
|---|---|
| `q-inventory` | Cola de trabajo del consumidor de inventario |
| `q-inventory` / **`$deadletterqueue`** | DLQ **nativa de Azure** (mensaje fallido o reintentos agotados) |
| `q-dlq` | DLQ **central** del diseño (operaciones / Replay Controller) — post-MVP mueve aquí mensajes de varias fuentes |

---

**Qué pasa hoy en el MVP (honesto)**

| Paso | ¿Implementado? |
|---|---|
| E1 crea orden y escribe **outbox** en SQL | Sí |
| **bus-workers** publica outbox → **Event Hubs** | Sí |
| Publicar a **Service Bus** `q-inventory` desde la app | **No** (infra creada, cableado pendiente) |
| Consumidor que lee `q-inventory` y valida/falla | **No** (`inventory-service` solo HTTP, no escucha colas) |
| **Replay Controller** en AKS | **Post-MVP** (replay manual en portal en el MVP) |

Por eso **Postman E1–E4 no generan mensajes en DLQ**: esos escenarios usan HTTP (APIM → order-service → inventory HTTP). El bus asíncrono con consumidor que falle **aún no está cableado**.

Tras un **E1 exitoso** puedes ver el evento en **Event Hubs** (`eh-canonical`), no en Service Bus DLQ.

---

**Cómo probar E5 (sin cambiar el MVP)**

El MVP no cablea Service Bus desde las apps, pero la **infra** (`q-inventory`, `max_delivery_count = 10`) sí existe. La demo **simula** publicador + consumidor que falla hasta agotar reintentos.

**Verificar siempre al final:** Portal → `sb-rutaexpress-mvp` → **Queues** → `q-inventory` → pestaña **`$deadletterqueue`** (no la cola principal) → Service Bus Explorer → **Peek**.

> **No confundir:** el body HTTP del **paso 3** en Postman **no** indica el estado del DLQ. Antes apuntaba al mock **E8** de APIM (`IN_TRANSIT`); ahora es un eco auxiliar. El DLQ **solo** se ve en el portal Azure bajo **`$deadletterqueue`**.

**Si Dead-letter = 0 mensajes:** suele haber **mensajes viejos** en Active de pruebas anteriores; el paso 3 abandonaba mensajes distintos y ninguno llegó a 10 reintentos. **Purga** mensajes Active en `q-inventory` (portal → Service Bus Explorer → Receive and delete o eliminar), luego **paso 2 → paso 3** seguidos.

**Cola `q-dlq`:** DLQ central del diseño (post-MVP); en la demo usa **`$deadletterqueue`** de `q-inventory`.

---

**Opción A — PowerShell + Node (recomendada)**

No pegues la Primary Key a mano: el script lee la **connection string** con `az login`.

> `az servicebus queue message send` **no existe** en Azure CLI (solo gestión de colas).

```powershell
cd Implementacion\scripts
.\e5-servicebus-dlq-demo.ps1
```

Requisitos: **Node.js** + `az login` con acceso a `rg_Diego_Gonzales`. La primera vez instala `@azure/service-bus` en `scripts\`.

Opcional con otro `order_id`:

```powershell
.\e5-servicebus-dlq-demo.ps1 -OrderId "ORD-E5-DEMO"
```

Salida esperada:

```text
[OK] Mensaje encolado en q-inventory
  Abandon 1/10 deliveryCount=0
  ...
  Abandon 10/10 deliveryCount=9
Listo. Portal: q-inventory -> $deadletterqueue -> Peek
```

---

**Opción B — Postman (pasos 1→2→3)**

Carpeta: **Azure APIM (fase 1)** → **E5 — DLQ agotar reintentos**.

| Paso | Request | ¿Funciona sin key? | Qué hace |
|---|---|:---:|---|
| **1** | `E5 paso 1 — Crear orden` | Sí | Orden OK vía APIM; guarda `e5_order_id` (contexto; en TO-BE dispararía el evento al bus) |
| **2** | `E5 paso 2 — Encolar evento en q-inventory` | No | REST Service Bus: **simula** el publicador al bus |
| **3** | `E5 paso 3 — Agotar reintentos` | No | REST: recibe + abandona 10 veces → DLQ real de Azure |

**Antes de pasos 2 y 3:** variable `servicebus_sas_key` en **colección o environment** (no en ambos con valores distintos).

1. Portal → `sb-rutaexpress-mvp` → **Shared access policies** → `RootManageSharedAccessKey` → **Primary Key** (copiar sin espacios).
2. Postman → colección o environment → `servicebus_sas_key` = ese valor.
3. Ejecutar en orden: paso 1 → paso 2 → paso 3.

Si paso 2 responde **401**: reimporta la colección Postman (fix SAS en pre-request), verifica `servicebus_sas_key` sin espacios, o usa la **opción A** (script). **No commitees la key.**

Los pasos 2 y 3 generan el token SAS en el pre-request (la Primary Key se usa como texto UTF-8 para el HMAC; no decodificar Base64 en Postman).

---

#### E8 — Tracking portal (CQRS lectura)

**De qué trata:** El portal B2B consulta el estado de un envío (escenario **E8**). En el dossier, la **lectura** es CQRS: escritura en Azure/AWS, **proyección de lectura** en GCP (BigQuery).

**Flujo MVP al hacer clic en Postman:** `GET` → **mock-portal** en APIM (Azure) → JSON con `scenario: "E8"`. **GCP no interviene en esa llamada HTTP.**

**Qué hace GCP entonces (fase 3):** cumple el requisito **multinube + IaC** y deja lista la capa de lectura: **Cloud Run** (proyector) + **BigQuery** `rutaexpress_mvp_tracking` + metadata en **Secret Manager**. En el MVP la imagen de Cloud Run es placeholder y BQ puede estar vacío; el cableado APIM → BigQuery es evolución post-MVP.

**Cómo demostrar E8 multinube al comité:** (1) Postman/ PowerShell → respuesta E8 en APIM; (2) consola GCP → Cloud Run + dataset BigQuery. Narrativa: *entrada Azure (APP-18 mock), proyección GCP (CQRS)*.

```powershell
Invoke-RestMethod -Method GET -Uri "$apim/mock/portal/v1/tracking/ORD-123" -Headers @{ "Ocp-Apim-Subscription-Key" = $subKey }
```

**Respuesta esperada:** HTTP **200** — `orderId`, `status`, `scenario: "E8"`, `source: "mock-portal-mvp"`.

**Postman:** request **E8 — Tracking portal (MVP)**.

---

#### Postman / Insomnia

1. Instala [Postman](https://www.postman.com/downloads/) o [Insomnia](https://insomnia.rest/download).
2. **Import** → `Implementacion/postman/RutaExpress-MVP-Azure.postman_collection.json` (si ya la tenías importada, **reimporta** para aplicar el fix SAS de E5).
3. Variables de colección (en `mvp\` con `terraform output`):

| Variable | Valor |
|---|---|
| `apim_base_url` | `terraform output -raw apim_gateway_url` |
| `apim_subscription_key` | Primary key APIM (§6.7) |
| `servicebus_sas_key` | Solo **E5 pasos 2–3**: Primary Key de `RootManageSharedAccessKey` (§6.7). Alternativa: script `e5-servicebus-dlq-demo.ps1` |
| `aws_alb_base_url` | `http://` + `terraform output -raw aws_mobile_alb_dns` (fase 2) |

4. Orden sugerido: **E1 → E2 → E3 → E4 → E5 (carpeta 3 pasos)** → **E8** (Azure) · **Health → E6 → E7** (AWS).

Carpetas en la colección:

| Carpeta | Escenarios |
|---|---|
| **Azure APIM (fase 1)** | E1, E2, E3, E4, **E5** (subcarpeta 3 pasos), E8 |
| **E5 — DLQ agotar reintentos** | Dentro de **Azure APIM** → pasos 1→2→3 + portal `$deadletterqueue` (§6.7) |
| **AWS ALB (fase 2)** | Health, E6, E7 |

En Postman las respuestas 409/503/400 se ven en el panel de respuesta; revisa el body JSON, no solo el código de color.

---

## 7. FASE 2 — AWS (E6–E7)

**Prerrequisito:** fase 1 funcionando (E1 al menos). **Docker Desktop** en ejecución.

### Flujo completo (orden fijo)

Todos los pasos en la **misma ventana** de PowerShell (credenciales AWS activas en §7.1).

| # | Carpeta | Comando |
|---|---------|---------|
| 0 | cualquiera | Configurar `$env:AWS_*` + `aws sts get-caller-identity` (§7.1) |
| 1 | `Implementacion\scripts` | `.\phase2-aws.ps1` |
| 2 | `Implementacion\scripts` | `.\build-push-mobile-aws.ps1` **obligatorio** |
| 3 | `Implementacion\terraform\environments\mvp` | Probar `/health` y E6 (§7.3) |

> Solo `phase2.tfplan` (no otros nombres). El plan se genera dentro de `mvp\` al ejecutar `phase2-aws.ps1`.

```powershell
# Paso 0 — credenciales (portal AWS, key ASIA...)
$env:AWS_ACCESS_KEY_ID     = "ASIA..."
$env:AWS_SECRET_ACCESS_KEY = "..."
$env:AWS_SESSION_TOKEN     = "..."    # obligatorio con ASIA...
$env:AWS_DEFAULT_REGION    = "us-east-1"
aws sts get-caller-identity

# Paso 1 — infra AWS (crea ECR vacio, ECS, ALB, etc.)
cd Implementacion\scripts
.\phase2-aws.ps1

# Paso 2 — subir imagen mobile-api al ECR (sin esto ECS falla con CannotPullContainerError)
.\build-push-mobile-aws.ps1

# Paso 3 — probar E6
cd ..\terraform\environments\mvp
$alb = terraform output -raw aws_mobile_alb_dns
Invoke-RestMethod "http://$alb/health"
Invoke-RestMethod -Method POST -Uri "http://$alb/deliveries/123/complete" -Body '{}' -ContentType "application/json"
```

**Respuesta E6 esperada:** `ack: true`.

---

### 7.1 Configurar AWS CLI

**Dónde:** cualquier carpeta en PowerShell (credenciales de sesión).

**Credenciales permanentes** (usuario IAM):

```powershell
aws configure
```

| Campo | Ejemplo |
|---|---|
| AWS Access Key ID | `AKIA...` |
| AWS Secret Access Key | `...` |
| Default region | `us-east-1` |
| Default output format | `json` |

**Credenciales temporales del portal AWS** (key `ASIA...` — incluyen session token):

```powershell
$env:AWS_ACCESS_KEY_ID     = "ASIA..."
$env:AWS_SECRET_ACCESS_KEY = "..."
$env:AWS_SESSION_TOKEN     = "..."    # obligatorio con ASIA...
$env:AWS_DEFAULT_REGION    = "us-east-1"
```

```powershell
aws sts get-caller-identity
```

> No uses `export` (eso es Linux). En Windows PowerShell es `$env:NOMBRE = "valor"`.  
> Las credenciales del portal **expiran**; si falla AWS, genera un set nuevo en el portal.

---

### 7.2 Infraestructura AWS

**Dónde editar tfvars:** `Implementacion\terraform\environments\mvp\terraform.tfvars`

```hcl
enable_aws = true
```

**Dónde ejecutar el script** (desde la raíz del repo o con ruta completa):

```powershell
cd Implementacion\scripts
.\phase2-aws.ps1
```

O manualmente (**debes estar en `mvp\`**):

```powershell
cd Implementacion\terraform\environments\mvp
terraform plan -out phase2.tfplan
terraform apply phase2.tfplan
```

**Ver outputs** (solo en `mvp\`):

```powershell
cd Implementacion\terraform\environments\mvp
terraform output
terraform output -raw aws_mobile_alb_dns
terraform output -raw aws_ecr_mobile_api_url
terraform output -raw aws_ecs_cluster_name
terraform output deploy_phase
```

**Recursos que crea:**

| Recurso Terraform | Servicio AWS | Para qué |
|---|---|---|
| `aws_ecr_repository` | **ECR** | Repositorio imagen `mobile-api` (vacío hasta `build-push-mobile-aws.ps1`) |
| `aws_ecs_cluster` + `aws_ecs_service` | **ECS Fargate** | Backend móvil APP-15 |
| `aws_lb` | **ALB** | HTTP puerto 80 hacia ECS |
| `aws_dynamodb_table` | **DynamoDB** | Outbox backend móvil |
| `aws_s3_bucket` | **S3 + KMS** | Evidencias fotos/firmas E7 |
| `aws_sqs_queue` | **SQS + DLQ** | Buffer puente a Azure |
| `aws_cloudwatch_event_rule` | **EventBridge** | Puente hacia Event Hubs Azure |

Tras `phase2-aws.ps1`, ejecuta **siempre** `.\build-push-mobile-aws.ps1` antes de probar E6.

---

### 7.3 App móvil y E6

**De qué trata:** La app del conductor confirma una entrega (sync offline / última milla). Escenario **E6**.

**Flujo:** Cliente móvil → **ALB** (AWS) → **ECS Fargate** (`mobile-api`, APP-15) → ack.

**Código fuente:** `Implementacion/apps/mobile-api/`. Terraform crea el **ECR**; el script sube la imagen.

**Probar E6** (en `Implementacion\terraform\environments\mvp`):

```powershell
$alb = terraform output -raw aws_mobile_alb_dns

# Health primero (debe devolver status: ok)
Invoke-RestMethod "http://$alb/health"

# E6
Invoke-RestMethod -Method POST -Uri "http://$alb/deliveries/123/complete" -Body '{}' -ContentType "application/json"
```

**Respuesta esperada:** `ack: true`, `scenario: "E6"`.

**Postman:** carpeta **AWS ALB (fase 2)** → requests **Health** y **E6 — Completar entrega** (variable `aws_alb_base_url`).

**Cuándo probar:** en consola ECS → servicio `rutaexpress-mvp-mobile-api` → **1/1 Tasks running** y deployment **Completed** (2-5 min tras `build-push-mobile-aws.ps1`).

**No hace falta** editar `mobile_api_image` en `terraform.tfvars` (por defecto usa el ECR de Terraform). Solo si quieres otra imagen externa: `mobile_api_image = "tu-imagen:tag"` + `terraform apply` en `mvp\`.

---

### 7.3.1 E7 — Evidencia de entrega (stub)

**De qué trata:** El conductor sube foto/firma; el backend valida hash SHA-256 antes de guardar en **S3+KMS** (APP-16).

**Flujo:** App móvil → **ALB** → `POST /deliveries/{id}/evidence`.

**Probar** (misma base URL que E6):

```powershell
# Hash valido (200)
Invoke-RestMethod -Method POST -Uri "http://$alb/deliveries/123/evidence" `
  -Body '{"sha256":"a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456"}' `
  -ContentType "application/json"

# Hash invalido (400 E7) — PowerShell en ROJO es normal (como E2/E3/E4)
Invoke-RestMethod -Method POST -Uri "http://$alb/deliveries/123/evidence" `
  -Body '{"sha256":"invalid"}' -ContentType "application/json"
```

**Respuesta valida (200):** `stored: true`, `scenario: "E7"`.

**Respuesta invalida (400):** JSON `{"deliveryId":"123","scenario":"E7","error":"Hash invalido"}`.  
PowerShell lo muestra como error en rojo; **si el JSON dice `scenario: E7` y `Hash invalido`, la prueba es exitosa**.

**Postman:** **E7 — Evidencia hash valido** y **E7 — Evidencia hash invalido** (ahi ves el 400 sin confundirte con el color rojo de PowerShell).

> Tras cambiar `mobile-api`, vuelve a ejecutar `.\build-push-mobile-aws.ps1` para que ECS use la imagen nueva.

---

### 7.4 Ver recursos desplegados en AWS

AWS no tiene un Resource Group automatico como Azure. Opciones:

**A) Resource Group por tag** (recomendado, similar a `rg_Diego_Gonzales`):

1. Consola AWS → **Resource Groups** → Create → Tag based
2. Tag `package` = `rutaexpress-mvp` (o `project` = `rutaexpress` + `environment` = `mvp`)
3. Nombre: `rg-rutaexpress-mvp`
4. Region: **us-east-1**

**B) Inventario Terraform** (en `mvp\`):

```powershell
terraform output
```

**C) Buscar por prefijo** en cualquier servicio: `rutaexpress-mvp` o `ecs-rutaexpress-mvp`.

| Servicio consola | Nombre en tu despliegue |
|---|---|
| ECS → Clusters | `ecs-rutaexpress-mvp` / servicio `rutaexpress-mvp-mobile-api` |
| EC2 → Load Balancers | `rutaexpress-mvp-mobile-alb` |
| ECR | `rutaexpress-mvp-mobile-api` |
| DynamoDB | `rutaexpress-mvp-mobile-outbox` |
| S3 | `rutaexpress-mvp-evidence-mvp01` |
| CloudWatch Logs | `/ecs/rutaexpress-mvp-mobile-api` |

**Errores frecuentes E6:**

| Síntoma | Causa | Solución |
|---|---|---|
| `http:///deliveries/...` | `$alb` vacío; `terraform output` desde `scripts\` | `cd Implementacion\terraform\environments\mvp` y asignar `$alb` de nuevo |
| **503 Service Unavailable** | ECR sin imagen o target unhealthy | `.\build-push-mobile-aws.ps1` + esperar 1/1 Tasks |
| **CannotPullContainerError** en ECS | No ejecutaste paso 2 | `cd Implementacion\scripts` → `.\build-push-mobile-aws.ps1` |
| `push access denied` / login ECR 400 | PowerShell rompe pipe a `docker login` en Windows | `git pull` y `.\build-push-mobile-aws.ps1` (usa cmd.exe). O manual en **cmd.exe**: `aws ecr get-login-password --region us-east-1 ^| docker login --username AWS --password-stdin TU_CUENTA.dkr.ecr.us-east-1.amazonaws.com` |
| ECS 0/1 mas de 5 min | Imagen `latest` no existe en ECR | Verificar en consola ECR que hay tag `latest` |
| `ParserError` en `build-push-mobile-aws.ps1` | Caracteres especiales en script | `git pull` (script usa solo ASCII) |

---

## 8. FASE 3 — GCP (E8)

**Prerrequisito:** fases 1 y 2 aplicadas (`deploy_phase` = `2-azure-aws` o superior).

### Flujo completo (orden fijo)

| # | Carpeta / accion | Comando |
|---|------------------|---------|
| 0 | cualquiera | `gcloud auth login` + `gcloud auth application-default login` |
| 0 | `mvp\terraform.tfvars` | `enable_gcp = true` + `gcp_project_id = "TU-PROYECTO-REAL"` |
| 0 | cualquiera | Habilitar APIs GCP (ver abajo) |
| 1 | `Implementacion\scripts` | `.\phase3-gcp.ps1` |
| 2 | `Implementacion\terraform\environments\mvp` | Probar E8 (§8.3) |

> Solo `phase3.tfplan` (generado en `mvp\` por el script).

```powershell
# Paso 0 — cuenta y proyecto GCP (UTEC)
gcloud auth login
gcloud auth application-default login
gcloud projects list
# Anota PROJECT_ID (no "disabled")

gcloud services enable run.googleapis.com bigquery.googleapis.com secretmanager.googleapis.com `
  --project=utec-posgrado-01

# Editar Implementacion\terraform\environments\mvp\terraform.tfvars:
#   enable_gcp    = true
#   gcp_project_id = "utec-posgrado-01"

# Paso 1 — infra GCP (Cloud Run, BigQuery, Secret Manager)
cd Implementacion\scripts
.\phase3-gcp.ps1

# Paso 2 — E8 (misma URL APIM que fase 1; con GCP el proyector alimenta BigQuery)
cd ..\terraform\environments\mvp
$apim = terraform output -raw apim_gateway_url
$subKey = "TU_APIM_SUBSCRIPTION_KEY"
Invoke-RestMethod -Method GET -Uri "$apim/mock/portal/v1/tracking/ORD-123" `
  -Headers @{ "Ocp-Apim-Subscription-Key" = $subKey }
```

**Respuesta E8 esperada:** HTTP **200** — `scenario: "E8"`, `source: "mock-portal-mvp"` (ver JSON abajo).

---

### 8.1 Configurar Google Cloud

```powershell
gcloud auth login
gcloud auth application-default login
gcloud projects list
```

Edita `terraform.tfvars`:

```hcl
enable_gcp    = true
gcp_project_id = "tu-proyecto-gcp-real"
gcp_region     = "us-east1"
```

**Habilitar APIs (si falla el apply):**

```powershell
gcloud services enable run.googleapis.com bigquery.googleapis.com secretmanager.googleapis.com --project=TU_PROJECT_ID
```

---

### 8.2 Infraestructura GCP

**Dónde editar tfvars:** `Implementacion\terraform\environments\mvp\terraform.tfvars`

```hcl
enable_gcp     = true
gcp_project_id = "tu-proyecto-gcp-real"   # NO dejar "disabled"
gcp_region     = "us-east1"
```

**Dónde ejecutar:**

```powershell
cd Implementacion\scripts
.\phase3-gcp.ps1
```

O manualmente (**en `mvp\`**):

```powershell
cd Implementacion\terraform\environments\mvp
terraform plan -out phase3.tfplan
terraform apply phase3.tfplan
```

**Ver outputs** (en `mvp\`):

```powershell
terraform output gcp_cloud_run_uri
terraform output gcp_bq_dataset
terraform output deploy_phase
```

**Recursos que crea:** Cloud Run (`cr-rutaexpress-mvp-projector`), BigQuery (`rutaexpress_mvp_tracking`), Secret Manager (metadata `rutaexpress-mvp-eventhub-conn`).

**Si fallo Secret Manager 403 (UTEC):** el modulo no gestiona versiones ni IAM del secreto. Connection string en env de Cloud Run. Limpia state y re-aplica:

```powershell
cd Implementacion\terraform\environments\mvp
terraform state rm 'module.gcp[0].google_secret_manager_secret_version.eventhub_bridge[0]' 2>$null
terraform state rm 'module.gcp[0].google_secret_manager_secret_iam_member.projector_accessor' 2>$null
terraform plan -out phase3.tfplan
terraform apply phase3.tfplan
```

---

### 8.3 Probar E8 (tracking CQRS)

**De qué trata:** El portal B2B consulta tracking. APIM expone `GET /mock/portal/v1/tracking/{id}`. Infra GCP (Cloud Run + BigQuery) se despliega en fase 3.

**Rol de GCP — lectura simple**

| Pregunta | Respuesta |
|---|---|
| ¿GCP responde el GET de Postman E8? | **No.** Responde **APIM en Azure** (política mock). |
| ¿Para qué sirve GCP en el MVP? | Infra multinube: proyector + BQ + Secret Manager (PLT-02). Diseño CQRS: eventos → proyección en BQ. |
| ¿BigQuery tiene datos al probar E8? | Puede estar vacío; el mock APIM no consulta BQ. |
| ¿Qué ver en consola GCP? | Cloud Run `cr-rutaexpress-mvp-projector`, dataset `rutaexpress_mvp_tracking`. |
| ¿Cómo contar E8 como multinube? | Demo en dos pantallas: Postman (Azure) + consola GCP (lectura materializada). |

**Dónde probar:** `Implementacion\terraform\environments\mvp`

```powershell
$apim = terraform output -raw apim_gateway_url
$subKey = "TU_APIM_SUBSCRIPTION_KEY"

Invoke-RestMethod -Method GET -Uri "$apim/mock/portal/v1/tracking/ORD-123" `
  -Headers @{ "Ocp-Apim-Subscription-Key" = $subKey }
```

**Respuesta esperada:**

```json
{
  "orderId": "ORD-123",
  "status": "IN_TRANSIT",
  "scenario": "E8",
  "source": "mock-portal-mvp"
}
```

**Postman:** carpeta **Azure APIM** → **E8 — Tracking portal (MVP)**.

> Tras cambiar la politica APIM en codigo, aplica en Azure: `cd mvp\` → `terraform plan -out phase1.tfplan` → `terraform apply phase1.tfplan` (solo actualiza APIM si cambio la politica E8).

**Ver recursos GCP:** consola GCP → **Cloud Run** `cr-rutaexpress-mvp-projector`, **BigQuery** `rutaexpress_mvp_tracking`.

---

## 9. Probar todos los escenarios E1–E8

Comandos y explicación detallada por escenario: **§6.7** (E1–E5, E8) · **§7.3** (E6–E7) · **§8.3** (E8 con GCP).

Colección Postman: `Implementacion/postman/RutaExpress-MVP-Azure.postman_collection.json` (**E1–E8**; E5 solo portal Azure).

### 9.1 Mapa rápido: qué nube interviene en cada prueba

| Escenario | Dónde probar | Nube(s) en la demo |
|---|---|---|
| **E1–E4** | Postman → APIM | **Azure** |
| **E5** | Postman E5 (pasos 1–3) + portal `$deadletterqueue` | **Azure** |
| **E6–E7** | Postman → ALB AWS | **AWS** |
| **E8** | Postman → APIM (`mock-portal`) | **Azure** (respuesta HTTP) + **GCP** (infra CQRS en consola) |

**Orden sugerido:** E1 → E2 → E3 → E4 → **E5 (portal)** → E8 → (fase 2) Health → E6 → E7 → (fase 3) ver GCP en consola.

**E5 y E8 — no confundir:** E5 es operación en Service Bus (DLQ). E8 es HTTP en Azure; GCP está desplegado para la proyección de lectura, no para el clic de Postman.

---

## 10. Problemas frecuentes

| Error | Causa | Solución |
|---|---|---|
| `dockerDesktopLinuxEngine` not found | Docker no corre | Abrir Docker Desktop → Running |
| `ParserError` en `setup-fase1.ps1` | Sintaxis PowerShell inválida | `git pull` y volver a ejecutar el script |
| `Authorization failed` al crear RG | Sin permiso en suscripción (común UTEC) | `azure_create_resource_group = false` y `azure_resource_group_name = "rg_Diego_Gonzales"` |
| `kubectl localhost:8080` | kubectl sin conectar al AKS | `az aks get-credentials -g rg_Diego_Gonzales -n aks-rutaexpress-mvp --overwrite-existing` |
| `PasswordNotComplex` tras cambiar tfvars | `phase1.tfplan` desactualizado | Borrar plan + `terraform plan -out phase1.tfplan` de nuevo |
| `build-push-images.ps1` falla en outputs ACR | Repo desactualizado | `git pull`; el script usa `az acr login` (no outputs de usuario/contraseña) |
| `cd Implementacion\...` duplica ruta | Ya estás dentro de `mvp` | Usar `cd ..\..\..\scripts` desde `mvp` |
| `PasswordNotComplex` SQL | Contraseña débil o plan desactualizado | Mín. 12 chars + 3 tipos (A/a/0/!); regenerar `terraform plan` |
| `Standard_D2s_v5 is not allowed` AKS | SKU no disponible en suscripción UTEC | `aks_vm_size = "Standard_D2s_v3"` en tfvars |
| `OIDCIssuerFeatureCannotBeDisabled` AKS | Cluster creado con OIDC; Terraform no lo tenía en código | Ya corregido en módulo (`oidc_issuer_enabled = true`); `terraform plan` + `apply` |
| APIM 30–45 min | Normal tier Developer | Esperar |
| `ImagePullBackOff` en pods | Imagen no en ACR | `.\build-push-images.ps1` |
| APIM 502 en orders | Backend URL incorrecta | Actualizar `order_api_backend_url` + `terraform apply` |
| APIM 401 subscription key | Falta header `Ocp-Apim-Subscription-Key` | Primary key: portal APIM → Subscriptions → Built-in all-access (§6.7) |
| APIM `ManagementApiRequestFailed` | Downtime normal del tier Developer | Esperar 10–15 min; obtener key por portal o reintentar `az rest` |
| `Invoke-OrderTest` / script no reconocido | Comando antiguo o sin `&` | Usar `& ..\..\..\scripts\test-order-api.ps1 -ApimBaseUrl $apim ...` (§6.7) |
| PowerShell rojo en E2/E3/E4 | HTTP 409/503 esperado | Revisar JSON en la salida del script; si dice `E2`/`E3`/`E4` está OK |
| PowerShell rojo en E7 hash invalido | HTTP 400 esperado | JSON `scenario: E7`, `error: Hash invalido` = prueba OK |
| E4 devuelve `CONFIRMED` / E1 | `order-service` viejo o sin `APIM_SUBSCRIPTION_KEY` | `build-push-images.ps1` + `deploy-helm-azure.ps1` + `terraform apply` (§6.7 E4) |
| E4 devuelve E2 o E3 | Body repetido de E1 o qty 9999 | `customerId` nuevo (ej. `B2B-E4-4`), qty 1, header `X-Mock-Wms-Status: 503` |
| `aws configure` / `NoCredentials` | Credenciales IAM no en sesión | `$env:AWS_*` + `AWS_SESSION_TOKEN` si key es `ASIA...` (§7.1) |
| ECS **CannotPullContainerError** | ECR sin imagen `latest` | `.\build-push-mobile-aws.ps1` tras `phase2-aws.ps1` (§7) |
| ALB **503** en E6 | ECS sin task healthy | Mismo paso: `build-push-mobile-aws.ps1`; luego `/health` |
| `push access denied` ECR | Login Docker falló | Credenciales AWS vigentes + Docker Desktop Running; si 400 en PowerShell usar script actualizado o login manual en cmd.exe (§7.4) |
| `terraform output` vacío en AWS | Mal directorio | Solo funciona en `Implementacion\terraform\environments\mvp` |
| GCP API disabled | APIs no habilitadas | `gcloud services enable ...` |
| GCP **secretmanager.versions.access** 403 | Cuenta UTEC sin leer versiones de secretos | `git pull` + `terraform state rm ...secret_version...` + `terraform apply` (§8.2) |
| GCP **secretmanager.secrets.setIamPolicy** 403 | Cuenta UTEC sin IAM en secretos | `git pull` (modulo sin IAM en Secret Manager) + `terraform apply` |

**Ver pods con error:**

```powershell
kubectl get pods -n rutaexpress
kubectl logs -n rutaexpress deploy/order-service
kubectl describe pod -n rutaexpress <nombre-pod>
```

**Ver fase desplegada:**

```powershell
cd Implementacion\terraform\environments\mvp
terraform output deploy_phase
```

---

## 11. Costos y destruir recursos

| Fase activa | Costo aprox./mes |
|---|:---:|
| Solo Azure | ~296 USD |
| Azure + AWS | ~389 USD |
| Azure + AWS + GCP | ~449 USD |

### Destruir todo (evitar cargos)

**Qué hace:** elimina todos los recursos creados por Terraform.

```powershell
cd Implementacion\terraform\environments\mvp
terraform destroy
```

Confirma con `yes`.

> Si solo quieres apagar AKS temporalmente, puedes escalar a 0 nodos desde portal Azure — pero `destroy` es lo limpio para fin de curso.

---

## Scripts

| Script | Función |
|---|---|
| `setup-fase1.ps1` | Azure + Docker + tfvars UTEC + terraform + build + helm (todo) |
| `setup-fase1.ps1 -SkipTerraform` | Solo build + helm (infra ya aplicada) |
| `build-push-images.ps1` | `docker build` + `az acr login` + `docker push` (3 apps) |
| `deploy-helm-azure.ps1` | `az aks get-credentials` + `helm upgrade --install` |
| `phase2-aws.ps1` | `enable_aws=true` + `terraform plan/apply phase2.tfplan` |
| `build-push-mobile-aws.ps1` | `docker build/push` mobile-api a **ECR** + redeploy ECS (obligatorio para E6) |
| `phase3-gcp.ps1` | `enable_gcp=true` + terraform apply |
| `test-order-api.ps1` | `POST` a APIM mostrando JSON en 409/503 — `& script -ApimBaseUrl $apim ...` (§6.7) |
| `e5-servicebus-dlq-demo.ps1` | E5 (recomendado): SDK Node + connection string vía `az`; encola + 10 abandons → `$deadletterqueue` (§6.7) |

---

*RutaExpress — Implementación MVP — UTEC*
