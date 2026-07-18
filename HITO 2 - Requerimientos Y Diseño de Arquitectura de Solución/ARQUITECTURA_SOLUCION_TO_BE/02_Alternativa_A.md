# Alternativa A — Hub Central Azure
## RutaExpress Fulfillment & Transporte — Hito 2 (diseño TO BE)

> **Modelo:** Azure como hub central de integración y gobierno.  
> **Diagramas C4:** [`diagramas_c4/`](diagramas_c4/).  
> **Decisión esperada:** validar este modelo como base del TO BE / implementación.

---

## 0. Nombres canónicos

| Nombre | Qué es | No usar |
|---|---|---|
| **OMS — APP-02** | Orquestador de Pedidos | “orquestador” sin ID |
| **Inventario — MS-INI01-02** | Microservicio de reservas | Confundirlo con WMS APP-06 |
| **`bus-workers`** | Deployment AKS: lee outbox SQL → Event Hubs | Publicador Outbox como único ingreso canónico al hub |
| **`retry-worker`** | Contenedor Fargate: SQS → EventBridge | “buffer” genérico |
| **Adaptador AWS→Azure** | Function: EventBridge → Event Hubs | “puente” sin nombre |
| **Backend móvil — APP-15** / `mobile-api` | API última milla | sin APP-15 |
| **Event Hubs** | Stream canónico | Decir que es Service Bus |
| **Service Bus** | Colas + DLQ | Decir que ahí publica `bus-workers` |

### Topología de eventos

```text
OMS / Inventario → Azure SQL (estado + outbox)
bus-workers → Azure SQL (consulta outbox) → Event Hubs
Event Hubs → Schema / Dispatcher → Service Bus → consumidores

OMS → Inventario por HTTP (Saga)
OMS → APIM → WMS

AWS: mobile-api → SQS → retry-worker → EventBridge → Adaptador AWS→Azure → Event Hubs
```

---

## 1. Resumen ejecutivo

La **Alternativa A** consolida APIM, OMS (APP-02), Inventario (MS-INI01-02), eventos, colas, identidad y observabilidad en **Azure**. El **Bus de Eventos Central (PLT-03)** combina:

- código **`bus-workers`** (lee outbox y publica);
- **Event Hubs** (stream);
- **Service Bus** (colas, DLQ, replay).

**AWS** permanece como dominio de última milla (APP-15, evidencias APP-16). **GCP** permanece como dominio analítico y de optimización.

**Ventaja:** menor complejidad operativa porque el hub de gobierno queda en un solo eje Azure.

---

## 2. Lineamientos de arquitectura

| Lineamiento | Implementación en Alternativa A |
|---|---|
| **Integración** | API-first con APIM (APP-01); EDA con PLT-03 (outbox → `bus-workers` → Event Hubs → Service Bus). |
| **Seguridad** | Entra ID, Key Vault, OAuth/OIDC, mínimo privilegio. |
| **Observabilidad** | OpenTelemetry, Azure Monitor, correlation ID. |
| **Resiliencia** | Outbox, DLQ, retry, replay, backpressure, circuit breaker (OMS → WMS vía APIM). |
| **Gobierno / IaC** | Terraform y pipelines. |
| **Datos** | Azure SQL (OLTP + outbox); S3/KMS evidencias; BigQuery lectura. |
| **Multinube** | Hub Azure; spokes AWS (móvil) y GCP (analítica). |

---

## 3. Patrones

| Patrón | Uso en Alternativa A |
|---|---|
| **Hub-and-Spoke** | PLT-03 en Azure; OMS, Inventario, WMS, TMS, móvil y GCP como productores/consumidores. |
| **EDA** | Eventos canónicos vía outbox + Event Hubs. |
| **Saga** | OMS coordina Inventario (HTTP) y WMS (vía APIM); compensación con Release. |
| **CQRS** | SQL operativo vs BigQuery lectura. |
| **Outbox** | OMS, Inventario y backend móvil. |
| **DLQ + Replay** | Service Bus + Replay Controller. |
| **Store-and-Forward** | APP-15 offline → sync a AWS. |

---

## 3.1 Aplicaciones impactadas

| Elemento AS IS | Disposición TO BE | Motivo |
|---|---|---|
| Orquestador de Pedidos (APP-02) | Evoluciona a **OMS** | Ciclo de vida, idempotencia, Saga. |
| WMS APP-06/07 | Integración gobernada vía **APIM** (OMS Saga) | Desacopla legado. |
| Punto a punto | Reemplazo por **PLT-03** | Menos acoplamiento. |
| App Conductores (APP-15) | Fortalecida en **AWS** | Offline, ACK, evidencias. |
| Evidencias (APP-16) | **S3 + KMS** | Inmutabilidad. |

---

## 4. Diagramas C4

### 4.1 Nivel 1 — Contexto

![C4 Contexto Alternativa A](diagramas_c4/alternativa_A_n1_contexto.png)

Personas: Cliente B2B, Conductor, Operaciones.  
Externos: WMS, TMS, ERP, Portal (contratos / mocks según fase).

### 4.2 Nivel 2 — Contenedores

![C4 Contenedores Alternativa A](diagramas_c4/alternativa_A_n2_contenedores.png)

| Contenedor | Nube | Responsabilidad |
|---|---|---|
| APIM (APP-01) | Azure | Gateway, OAuth, contratos legado. |
| OMS (APP-02) | Azure AKS | Órdenes, Saga, idempotencia; escribe outbox. |
| Inventario (MS-INI01-02) | Azure AKS | Reservas HTTP; escribe outbox. |
| **`bus-workers`** (PLT-03) | Azure AKS | Consulta outbox SQL → publica Event Hubs. |
| Azure SQL | Azure | Estado + tablas outbox. |
| Event Hubs | Azure | Stream canónico PLT-03. |
| Service Bus | Azure | Colas, DLQ, replay. |
| Backend móvil (`mobile-api`) APP-15 | AWS Fargate | Entregas / evidencias. |
| **`retry-worker`** | AWS Fargate | Consume SQS → EventBridge. |
| Adaptador AWS→Azure | Azure Function | EventBridge → Event Hubs. |
| DynamoDB / S3+KMS | AWS | Sync móvil y evidencias. |
| Proyector / BigQuery / Optimizador | GCP | Lectura CQRS y rutas. |

**Flujo clave:**

```text
Cliente → APIM → OMS → Inventario (HTTP)
                 ├→ APIM → WMS
                 └→ Azure SQL (orden + outbox)
bus-workers → SQL → Event Hubs → Service Bus → TMS / portal / GCP
mobile-api → SQS → retry-worker → EventBridge → Adaptador → Event Hubs
```

### 4.3 Nivel 3 — Componentes

#### Bus de Eventos / `bus-workers` (PLT-03)

![C4 N3 PLT-03](diagramas_c4/alternativa_A_n3_componentes.png)

| Pieza | Rol |
|---|---|
| Outbox Poller | Lee pendientes en Azure SQL |
| Event Hubs Publisher | Publica evento canónico |
| Schema Validator / Dispatcher / Replay / Backpressure | Evolución del bus |

#### OMS, Inventario y Backend móvil

![C4 N3 OMS](diagramas_c4/alternativa_A_n3_oms_componentes.png)

![C4 N3 Inventario](diagramas_c4/alternativa_A_n3_inventario_componentes.png)

![C4 N3 Móvil](diagramas_c4/alternativa_A_n3_mobile_componentes.png)

---

## 5. Trazabilidad INI → diseño

| Iniciativa | Elemento Alternativa A |
|---|---|
| INI-01 | OMS APP-02, Inventario MS-INI01-02, Azure SQL, Saga, WMS vía APIM |
| INI-02 | APIM, PLT-03 (`bus-workers` + Event Hubs + Service Bus), DLQ, replay |
| INI-03 | `mobile-api`, DynamoDB, S3/KMS, SQS → `retry-worker` → Adaptador |
| INI-04 | Optimizador GCP |
| INI-05 | PLT-01 / PLT-02 observabilidad e identidad |
| INI-06 | Evidencias + estados + ERP |

---

## 6. ADR (resumen)

| ADR | Decisión |
|---|---|
| **A-001** | Hub PLT-03 en Azure = Event Hubs + Service Bus + `bus-workers`. |
| **A-002** | APP-02 evoluciona a OMS (sin nuevo ID). |
| **A-003** | Última milla en AWS; puente nombrado hasta Event Hubs. |
| **A-004** | Observabilidad end-to-end con correlation ID. |

---

## 7. Vista de despliegue

```text
Azure                              AWS                         GCP
-----------------------------      ------------------------    ------------------
APIM (APP-01)                      mobile-api (APP-15)         Cloud Run proyector
OMS (APP-02) AKS                   retry-worker                BigQuery
Inventario (MS-INI01-02) AKS       DynamoDB / S3+KMS           Optimizador
bus-workers AKS                    SQS → EventBridge           Pub/Sub
Azure SQL (outbox)
Event Hubs ← Adaptador AWS→Azure
Service Bus (colas/DLQ)
Monitor / Key Vault / Entra

On premises / SaaS: WMS · TMS · ERP · Portal (vía APIM / eventos)
```

---

## 8. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Azure como hub crítico | HA, particiones, DR, monitoreo. |
| Saturación en campañas | Backpressure, colas por consumidor. |
| Pérdida offline | Store-and-forward + ACK. |
| Inconsistencia OMS/WMS | Saga + compensación + auditoría. |

---

## 9. Recomendación

Usar **Alternativa A** como base del TO BE.

- Menor complejidad de integración.
- Alineada al AS IS (APIM/OMS ya en Azure).
- APP-15/16 permanecen en AWS.
- GCP conserva rol analítico.
- Topología de eventos clara: outbox → `bus-workers` → Event Hubs.
