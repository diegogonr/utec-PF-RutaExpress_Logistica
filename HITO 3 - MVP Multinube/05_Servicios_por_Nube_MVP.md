# Catálogo de servicios, componentes y herramientas — por nube
## RutaExpress Fulfillment & Transporte — Hito 3 MVP

> **Audiencia:** Comité (~5 min con **Parte I**) y equipo técnico (~20 min con **Parte II**).  
> **Diagramas y flujos:** [`03_C4_Model_MVP.md`](03_C4_Model_MVP.md).  
> **IaC y costos:** [`04_IaC_Costos_Despliegue.md`](04_IaC_Costos_Despliegue.md) · [`../Implementacion/`](../Implementacion/).

---

## Cómo leer este documento

Un solo catálogo con **dos partes**:

| Parte | Secciones | Para qué | Tiempo |
|---|---|---|:---:|
| **I — Vista por nube** | §1–§6 | Tablas, matrices, E1–E8, qué va en cada proveedor | ~5 min |
| **II — Explicación de cada pieza** | §7–§13 | Qué es y para qué sirve cada APP/PLT/MS, servicio cloud y herramienta | ~15 min |

**Niveles de detalle (Parte II):** 🟢 simple · 🟡 medio · 🔴 complejo — más texto donde el elemento es más crítico o fácil de confundir.

---

# Parte I — Vista por nube (referencia rápida)

## 1. Mensaje en una frase

El MVP despliega **3 nubes** con roles distintos: **Azure** = hub transaccional y bus; **AWS** = última milla y evidencias; **GCP** = solo lectura analítica (**CQRS** — separar escritura y lectura). Todo se provisiona con **IaC** (Terraform).

| Nube | Rol | % costo demo (~USD 449/mes) |
|---|---|---:|
| **Azure** | Hub operativo — API, OMS, inventario, bus | ~65 % (~296) |
| **AWS** | Última milla — móvil, evidencias, puente al hub | ~21 % (~93) |
| **GCP** | Lectura — proyector + BigQuery | ~14 % (~60) |

---

## 2. Tipos de elementos (no mezclar nombres)

| Tipo | Símbolo | ¿Servicio de nube? | Ejemplo MVP |
|---|---|:---:|---|
| **Iniciativa** | INI-XX | No | INI-01, INI-02, INI-03 |
| **Aplicación** | APP-XX | No (software de negocio) | **Orquestador de Pedidos (APP-02)** |
| **Plataforma** | PLT-XX | A veces | **Bus de Eventos Central (PLT-03)** |
| **Microservicio** | MS-INIxx-yy | No | **Microservicio Inventario (MS-INI01-02)** |
| **Servicio cloud** | Proveedor | **Sí** | AKS, ECS Fargate, BigQuery |
| **Herramienta** | Repo / vendor | No (salvo OTel Collector) | Terraform, Helm, OpenAPI |
| **Mock** | mock-* en APIM | No | mock-wms → **WMS (APP-06)** |

```text
Negocio (INI, APP, MS)  →  corre sobre  →  Servicios cloud
Plataforma (PLT)        →  implementada con  →  Servicios cloud
Construcción            →  Herramientas (F)  →  afectan una o más nubes
```

> Taxonomía completa APP vs MS vs PLT: [`03_C4_Model_MVP.md`](03_C4_Model_MVP.md) §0.1 · Explicación por pieza: **§7–§11** abajo.

---

## 3. Servicios por nube (tabla compacta)

### 3.1 Azure — hub operativo

| Servicio cloud | Componente (APP/PLT/MS) | Qué hace en el MVP |
|---|---|---|
| **Azure API Management** | APP-01 | Entrada: `POST /api/v1/orders`; mocks WMS, ERP, portal, TMS |
| **AKS** | APP-02, MS-INI01-02, `bus-workers`, BFF del MVP | OMS, Inventario (HTTP), outbox → Event Hubs vía `bus-workers` |
| **Azure SQL** (S1) | Datos APP-02 + MS | Estado transaccional; tablas outbox |
| **Event Hubs** (1 TU) | PLT-03 — stream | Eventos canónicos; alimenta GCP (objetivo) |
| **Service Bus** | PLT-03 — colas | Colas/DLQ; consumidor Inventario = **objetivo**; demo E5 parcial |
| **Azure Cache for Redis** | Caché transversal | Idempotencia y dedup (E1, E2) |
| **Entra ID** | PLT-02 parcial | OAuth en APIM |
| **Key Vault** | PLT-02 | Connection strings bus |
| **Azure Monitor + App Insights** | PLT-01 parcial | Métricas y trazas Azure |

### 3.2 AWS — última milla

| Servicio cloud | Componente | Qué hace en el MVP |
|---|---|---|
| **ECS Fargate** + **ALB** | Backend **APP-15** | API móvil + **`retry-worker`** en el **mismo task** |
| **DynamoDB** | Outbox backend móvil | Persistencia post-offline hacia AWS |
| **S3 + KMS** | APP-16 | Fotos/firmas cifradas; hash SHA-256 (E7) |
| **SQS + DLQ** | Cola del puente | Buffer móvil → hub Azure |
| **EventBridge** | Puente multinube (**objetivo**) | Publica hacia Adaptador AWS→Azure → Event Hubs |
| **CloudWatch + X-Ray** | Observabilidad AWS | Logs y trazas backend móvil |

### 3.3 GCP — lectura CQRS

| Servicio cloud | Componente | Qué hace en el MVP |
|---|---|---|
| **Cloud Run** | Proyector CQRS | Eventos → filas BigQuery |
| **BigQuery** | Proyección tracking (**objetivo**) | Lectura E8; hoy mock-portal en APIM no consulta BQ |
| **Secret Manager** | Credenciales puente | Connection string Event Hubs |

### 3.4 Transversal — herramientas (no es «cuarta nube»)

| Herramienta | ¿Servicio cloud? | Dónde está | Nubes que afecta |
|---|---|:---:|---|
| **Terraform** | No | `Implementacion/terraform/` | **Las 3** (crea infra) |
| Estado Terraform | Sí (storage) | `terraform/bootstrap/` | **Las 3** (solo estado) |
| **Helm** | No | `Implementacion/helm/` | **Solo Azure** (AKS) |
| **OTel Collector** | Sí (pod AKS) | `helm/otel/` | Azure (trazas) |
| **OpenAPI YAML** | No | `Implementacion/apis/mock/` | **Solo Azure** (APIM) |

```text
Tu PC / GitHub Actions
    ├─► Terraform ──► Azure + AWS + GCP
    └─► Helm ───────► AKS (pods OMS, Inventario, `bus-workers`, OTel)
```

> Detalle de Terraform, Helm, OTel: **§11**. Confusión frecuente: «transversal» = propósito multinube, **no** que cada herramienta se instale en las 3 nubes.

---

## 4. Matriz servicio × nube

Leyenda: **●** = provisionado / en uso · **◐** = parcial u objetivo cableado a medias · **○** = consume / integra · **—** = no en MVP v1

### 4.1 Servicios cloud del proveedor

| Servicio cloud | Azure | AWS | GCP |
|---|:---:|:---:|:---:|
| API Management / Gateway | **●** APIM | — | — |
| Kubernetes / contenedores | **●** AKS | **●** ECS Fargate | **◐** Cloud Run |
| Base transaccional SQL | **●** Azure SQL | — | — |
| Bus streaming | **●** Event Hubs | — | — |
| Bus colas / DLQ | **◐** Service Bus | **◐** SQS | — |
| Caché | **●** Redis | — | — |
| NoSQL outbox | — | **◐** DynamoDB | — |
| Object storage evidencias | — | **◐** S3 + KMS | — |
| Puente eventos | — | **◐** EventBridge | — |
| Data warehouse lectura | — | — | **◐** BigQuery |
| Identidad / secretos | **●** Entra, KV | **●** IAM, KMS | **●** Secret Manager |
| Observabilidad | **●** Monitor | **●** CloudWatch | **●** Cloud Logging |
| ML / Pub/Sub | — | — | **—** (post-MVP) |

### 4.2 Componentes de negocio (APP / PLT / MS)

| Componente | Azure | AWS | GCP | Nota |
|---|:---:|:---:|:---:|---|
| **APP-01** APIM | **●** | — | — | Incluye mocks |
| **APP-02** OMS | **●** AKS | — | — | |
| **MS-INI01-02** Inventario | **●** AKS | — | — | No es APP-XX |
| **PLT-03** Bus | **●** EH + **◐** SB | **◐** puente | **◐** consume | `bus-workers` → Event Hubs implementado |
| **APP-15** Conductores | — | **◐** ECS | — | Offline = dispositivo; puente objetivo |
| **APP-16** Evidencias | — | **◐** S3 | — | Infra parcial |
| **APP-18** Portal tracking | **●** mock APIM | — | **◐** BQ | E8: mock hoy; BQ objetivo |
| WMS / ERP / TMS legado | **●** mocks | — | — | |
| Proyección CQRS | **○** eventos | **○** entregas | **●** BQ+Run | |
| **PLT-04** IaC | **●** | **●** | **●** | Terraform |

---

## 5. Escenarios E1–E8 × servicio × nube

| Escenario | Qué se prueba | Servicios | Nube(s) |
|---|---|---|---|
| **E1** | Orden con idempotency-key | APIM → APP-02 → Redis/SQL | **Azure** |
| **E2** | Orden duplicada (mismo hash) | APP-02, Redis, SQL | **Azure** |
| **E3** | Inventario insuficiente | MS-INI01-02, SQL | **Azure** |
| **E4** | WMS mock 503 + backpressure | Saga APP-02, mock-wms, Service Bus | **Azure** |
| **E5** | Mensaje inválido → DLQ → replay | EH, Service Bus, workers AKS | **Azure** |
| **E6** | Entrega offline → sync | APP-15, ECS, DynamoDB, SQS | **AWS** |
| **E7** | Evidencia hash inválido | ECS, S3 + KMS | **AWS** |
| **E8** | Tracking CQRS | mock-portal APIM, Cloud Run, BQ | **Azure** + **GCP** |

### Flujo end-to-end

```text
Cliente B2B
  └─► APIM (Azure) ─► APP-02 + MS-INI01-02 (AKS)
        │                    └─► SQL, Redis, Event Hubs + Service Bus
App Conductores (APP-15)
  └─► ECS Fargate (AWS) ─► DynamoDB, S3 ─► SQS/EventBridge ─► Event Hubs
                                                                  └─► Cloud Run ─► BigQuery
Cliente tracking
  └─► mock-portal APIM (Azure) ──lectura──► BigQuery (GCP)
```

---

## 6. Fuera de alcance e iniciativas

### 6.1 Qué NO va en MVP v1

| Nube | Fuera de alcance |
|---|---|
| **Azure** | WMS/ERP reales on premises; multi-región HA plena |
| **AWS** | RDS; Lambda como compute principal; IoT (APP-09) |
| **GCP** | Pub/Sub; Vertex AI; optimizador rutas (INI-04) |
| **Todas** | Carga 180k órdenes/día; SIEM pleno (INI-05) |

### 6.2 INI cubiertas por nube

| Iniciativa | Demo | Nube principal |
|---|---|---|
| **INI-01** Órdenes e inventario | E1–E4 | **Azure** |
| **INI-02** API-First y eventos | E5, E8; E4 backpressure | **Azure** |
| **INI-03** Última milla | E6–E7 | **AWS** |
| INI-04 / INI-06 | No | — |

---

# Parte II — Explicación de cada pieza

## 7. Componentes de negocio y plataforma

### 7.1 Hub Azure

#### APP-01 — Azure API Management 🔴

**Qué es:** API Gateway administrado — puerta de entrada HTTP del MVP.

**Para qué:** `POST /api/v1/orders` hacia APP-02; mocks WMS/ERP/portal/TMS sin servidores aparte. OAuth vía Entra ID, rate limiting.

**No confundir con:** APP-02 (APIM expone; OMS ejecuta en AKS).

---

#### APP-02 — Orquestador de Pedidos (OMS) 🔴

**Qué es:** Cerebro transaccional del hub — órdenes, Saga, outbox, eventos.

**Flujo resumido:** Idempotency-Key → Redis → SQL+outbox → reserva MS-INI01-02 → Saga mock-WMS → worker publica a Event Hubs.

**Dónde:** AKS, chart `order-service`. **Escenarios:** E1–E5.

---

#### MS-INI01-02 — Microservicio Inventario y Reservas 🔴

**Qué es:** Dominio inventario — reserva/liberación de stock, desacoplado del OMS.

**Para qué:** E3 (sin stock), E4 (liberación en compensación). Outbox para `StockReserved`/`StockReleased`.

**Dónde:** AKS, chart `inventory-service`. **No es** APP-08 ni WMS (APP-06).

---

#### PLT-03 — Bus de Eventos Central 🔴

**Qué es:** Plataforma de mensajería = **Event Hubs** (stream fan-out) + **Service Bus** (colas con DLQ por consumidor).

**Para qué:** Desacoplar productores y consumidores; E5 replay; alimentar proyector GCP.

**No confundir con:** EventBridge AWS (puente desde móvil, no bus del hub).

---

#### PLT-02 IAM · PLT-01 Observabilidad · PLT-04 IaC 🟡

| ID | Qué es | MVP |
|---|---|---|
| **PLT-02** | Entra ID + Key Vault | OAuth en APIM; secretos del bus |
| **PLT-01** | Monitor + OTel | Trazas multinube parciales |
| **PLT-04** | Terraform en repo | Provisiona las 3 nubes |

---

### 7.2 AWS — última milla

#### APP-15 — App de Conductores 🔴

**Qué es:** App móvil + backend en AWS. **Store-and-forward:** outbox local sin red → sync a ECS → ACK → borrar local → puente a Azure.

**Dónde:** Dispositivo + **ECS Fargate** detrás de ALB. **Escenarios:** E6, E7.

---

#### APP-16 — Almacenamiento Evidencias (S3) 🟡

Fotos y firmas en **S3+KMS**, hash SHA-256 (E7). No guarda binarios en DynamoDB.

---

### 7.3 Mocks y lectura

| ID | Qué es | MVP |
|---|---|---|
| **APP-18** Portal B2B 🟡 | API mock tracking | E8 — lectura BQ vía APIM |
| **APP-06** WMS mock 🟡 | Política APIM 200/503 | E4 — compensación Saga |
| **APP-25** ERP mock 🟢 | Demo opcional | No bloquea E1–E8 |
| **APP-11** TMS mock 🟡 | Consumidor Service Bus | Integración async por eventos |

---

## 8. Servicios cloud — Azure (detalle)

| Servicio | Nivel | Explicación |
|---|---|---|
| **AKS** | 🔴 | Kubernetes administrado. Ejecuta APP-02, MS, workers, OTel. Terraform crea cluster; Helm despliega pods. E1–E5. |
| **Azure SQL** | 🟡 | OLTP transaccional: órdenes, reservas, outbox. No es BigQuery. E1–E4. |
| **Event Hubs** | 🟡 | Stream alto volumen, fan-out. Publicación desde outbox; alimenta GCP. |
| **Service Bus** | 🟡 | Colas con DLQ por consumidor; replay E5. |
| **Redis** | 🟢 | Caché idempotencia/dedup con TTL ~24 h. E1, E2. |
| **Entra ID** | 🟢 | Tokens OAuth/JWT para APIM. |
| **Key Vault** | 🟢 | Secretos; nunca en Git. |
| **Monitor + App Insights** | 🟡 | Métricas, trazas del hub; receptor OTel Collector. |

---

## 9. Servicios cloud — AWS (detalle)

| Servicio | Nivel | Explicación |
|---|---|---|
| **ALB** | 🟢 | TLS + health check hacia ECS. E6, E7. |
| **ECS Fargate** | 🔴 | **ECS** orquesta; **Fargate** es el cómputo sin servidores. Un **task** con API + `retry-worker`, que consume todos los mensajes de SQS y reintenta los fallidos. No es producto aparte de «AWS Fargate». |
| **DynamoDB** | 🟡 | Outbox backend móvil tras sync. E6. |
| **S3 + KMS** | 🟡 | Evidencias APP-16. E7. |
| **SQS + DLQ** | 🟡 | Buffer antes de EventBridge. |
| **EventBridge** | 🔴 | Puente multinube → Event Hubs Azure. No es PLT-03. |
| **CloudWatch + X-Ray** | 🟢 | Logs/trazas backend móvil. |

> **¿Por qué ECS Fargate y no EKS (Kubernetes) en AWS?** El hub transaccional ya usa **AKS** con varios workloads. En AWS solo corre el backend móvil (una app). EKS añadiría un segundo cluster sin beneficio en la demo — mismo criterio que **Cloud Run vs GKE** en GCP. Ver [`06_Preguntas_Argumentos_Comite.md`](06_Preguntas_Argumentos_Comite.md) **§4.2** y §10.

---

## 10. Servicios cloud — GCP (detalle)

| Servicio | Nivel | Explicación |
|---|---|---|
| **Cloud Run** | 🔴 | Proyector CQRS serverless: eventos → BigQuery. No atiende al cliente en E8 (eso es mock-portal APIM). |
| **BigQuery** | 🟡 | Lectura analítica tracking; réplica eventual, no OLTP. E8. |
| **Secret Manager** | 🟢 | Credenciales puente Event Hubs. |
| **Pub/Sub · Vertex AI** | 🟢 | **No en MVP v1** — post-MVP / INI-04. |

---

## 11. Herramientas y artefactos

### Terraform 🔴

Lee `.tf` y crea infra en Azure, AWS, GCP. Se ejecuta en PC/CI; **no** corre en el cluster. Estado remoto en `bootstrap/`. Gratis el software; ~USD 449/mes los recursos.

### Helm 🟡

Paquetes Kubernetes para AKS: `order-service`, `inventory-service`, `bus-workers`, `otel`. No despliega ECS ni Cloud Run.

### OpenTelemetry 🟡

- **SDK:** librerías en APP-02, MS, móvil (gratis, en proceso).
- **Collector:** pod en AKS que exporta a Azure Monitor.

### OpenAPI · GitHub Actions · Kubernetes 🟢

YAML mock en APIM; CI `fmt`/`validate`/`plan`; K8s viene con AKS.

---

## 12. Patrones de diseño

| Patrón | Nivel | Rol en MVP |
|---|---|---|
| **Outbox** | 🔴 | Evento en misma transacción que el dato; worker publica al bus |
| **Saga** | 🔴 | Pasos + compensación sin 2PC — APP-02 |
| **CQRS** | 🟡 | Escritura SQL / lectura BigQuery |
| **Store-and-forward** | 🟡 | Offline en dispositivo → AWS |
| **Idempotencia / dedup** | 🟡 | APP-02 + Redis — E1, E2 |
| **DLQ + replay** | 🟡 | Service Bus — E5 |

---

## 13. Mapa rápido — «¿esto qué es?»

| Pregunta | Respuesta |
|---|---|
| ¿AKS es APP-02? | **No.** AKS = servicio cloud; APP-02 = app dentro |
| ¿ECS Fargate vs «AWS Fargate»? | **Fargate es el cómputo; ECS es el orquestador.** No hay Fargate suelto |
| ¿Por qué no EKS en AWS? | Solo 1 app móvil; AKS ya cubre el hub con varios workloads |
| ¿Helm es de Azure? | Herramienta externa que habla con **AKS** |
| ¿Terraform en las 3 nubes? | **Crea** en las 3; **se ejecuta** fuera |
| ¿mock-wms es un servidor? | **No** — política en APIM |
| ¿BigQuery guarda órdenes? | **No** transaccional — solo lectura CQRS |
| ¿PLT-03 es un programa? | Plataforma = Event Hubs + Service Bus |
| ¿Event Hubs vs Service Bus? | Hubs = stream fan-out; SB = colas con DLQ |

---

## 14. Referencias

| Documento | Contenido |
|---|---|
| [`02_Dossier_MVP_Alternativa_A.md`](02_Dossier_MVP_Alternativa_A.md) | Alcance, patrones, justificación |
| [`03_C4_Model_MVP.md`](03_C4_Model_MVP.md) | Diagramas N1–N3, flujos A–D |
| [`04_IaC_Costos_Despliegue.md`](04_IaC_Costos_Despliegue.md) | Terraform, costos |
| [`06_Preguntas_Argumentos_Comite.md`](06_Preguntas_Argumentos_Comite.md) | Defensa oral — Fargate vs Lambda, multinube |
| [`../Implementacion/`](../Implementacion/) | Código IaC, Helm, mocks |

---

*RutaExpress — Hito 3 — UTEC*
