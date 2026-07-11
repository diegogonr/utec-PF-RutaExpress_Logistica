# Alternativa B - Hub Principal AWS
## RutaExpress Fulfillment & Transporte - Hito 2

> **Modelo presentado:** AWS como hub principal de eventos y ultima milla.

---

## 1. Resumen ejecutivo

La **Alternativa B** consolida eventos, colas, backend movil, store-and-forward y evidencias en **AWS**. APP-02 tambien evoluciona a un **OMS centralizado**, pero permanece en Azure junto con Azure API Management y el repositorio transaccional.

La diferencia principal respecto al Modelo A es que PLT-03 se ubica en AWS, usando EventBridge, SQS y workers para ruteo, colas, DLQ, retry, replay y backpressure. GCP se conserva para optimizacion dinamica, analitica y modelos predictivos.

**Ventaja principal:** AWS queda como centro natural de eventos moviles y ultima milla, reduciendo friccion para tracking, evidencias y excepciones generadas en campo.

**Riesgo principal:** OMS y gobierno API quedan separados del hub de eventos, por lo que el puente Azure -> AWS se vuelve componente critico.

---

## 2. Lineamientos de arquitectura aplicados

| Lineamiento | Implementacion en Alternativa B |
|---|---|
| **Integracion** | API-first en Azure API Management; Event-Driven Architecture con PLT-03 en AWS; puente Azure -> AWS para eventos de OMS/Inventario. |
| **Seguridad** | Entra ID/Key Vault para Azure; IAM/Secrets Manager/KMS para AWS; federacion, minimo privilegio y cifrado en transito/reposo. |
| **Observabilidad** | CloudWatch/X-Ray, Azure Monitor, GCP Monitoring y OpenTelemetry con correlation ID end-to-end. |
| **Resiliencia** | EventBridge, SQS, DLQ, replay, retry con jitter, backpressure, outbox/inbox y store-and-forward movil. |
| **Gobierno / IaC** | Terraform, pipelines, politicas por nube y RACI explicito entre gobierno API y gobierno de eventos. |
| **Datos** | Azure SQL para estado OMS/Inventario; DynamoDB logico y S3/KMS para ultima milla; BigQuery para analitica. |
| **Multinube** | Modelo federado: Azure conserva APIs/OMS, AWS gobierna eventos y ultima milla, GCP opera optimizacion/analitica. |

---

## 3. Patrones de arquitectura

| Patron | Uso en Alternativa B |
|---|---|
| **Hub-and-Spoke federado** | AWS PLT-03 como hub de eventos; OMS Azure, backend movil, TMS, portal y GCP como productores/consumidores. |
| **Event-Driven Architecture** | EventBridge/SQS para eventos canonicos, fan-out, colas por consumidor y replay. |
| **Saga** | Coordinacion orden -> reserva -> despacho -> entrega -> liquidacion mediante eventos entre Azure y AWS. |
| **CQRS selectivo** | Lecturas de tracking, SLA, inventario consultivo y tableros sin cargar bases transaccionales. |
| **Outbox/Inbox** | Publicacion confiable desde OMS en Azure hacia EventBridge en AWS. |
| **DLQ + Replay** | Manejo de mensajes fallidos y reproceso auditado en AWS. |
| **Store-and-Forward** | APP-15 y backend movil en AWS para persistencia offline, acks y reintentos. |
| **Circuit Breaker / Backpressure** | Proteccion del bridge Azure -> AWS y de consumidores degradados. |

---

## 3.1 Aplicaciones, plataformas y servicios modificados o fuera del foco

### Aplicaciones AS IS impactadas directamente

| Elemento AS IS | Disposicion TO BE en Alternativa B | Motivo |
|---|---|---|
| Orquestador de Pedidos (APP-02) | **Evoluciona a OMS e Inventario en Azure** | Mantiene gobierno API y estado transaccional cerca de Azure. |
| WMS Principal / Satelite (APP-06 / APP-07) | **Integracion desde OMS/Inventario en Azure** | Conserva transicion, pero publica eventos hacia AWS. |
| Integraciones punto a punto | **Reemplazo progresivo por hub AWS** | EventBridge/SQS asumen fan-out, retry, DLQ y replay. |
| App de Conductores (APP-15) | **Fortalecida en AWS** | Queda cerca del hub de eventos, backend movil y evidencias. |
| Evidencias (APP-16) | **Conservada en AWS S3/KMS** | Hash, cifrado, retencion, manifest y auditoria. |

### Plataformas y dominios

| Dominio | En Alternativa B | Motivo |
|---|---|---|
| **AWS** | Hub principal de eventos, colas, ultima milla, evidencias y observabilidad AWS. | Alinea eventos moviles, SQS, EventBridge y S3. |
| **Azure** | API Management, OMS, TMS/adaptadores, Azure SQL, identidad corporativa. | Mantiene APP-02 y gobierno API en su eje actual. |
| **GCP** | Optimizacion dinamica, analitica, BigQuery y modelos predictivos. | Consume eventos desde AWS para rutas y tableros. |
| **On premises / SaaS** | Sistemas transicionales integrados por APIs/eventos. | Permite migracion gradual sin corte brusco. |

---

## 4. Diagramas C4


### 4.1 Nivel 1 - Contexto

![C4 Contexto Alternativa B](diagramas_c4/imagenes_python_graphviz/alternativa_B_n1_contexto.png)

**Lectura:** el alcance funcional es la Plataforma Logistica RutaExpress TO BE. Actores y sistemas externos son equivalentes a la alternativa A; la diferencia no esta en el alcance sino en la topologia interna de eventos y resiliencia.

**Actores:** cliente B2B/Retail, conductor, operacion RutaExpress y finanzas.
**Sistemas externos:** WMS APP-06/APP-07, TMS APP-11, ERP APP-25, Portal B2B/CRM, canales legados y servicios de mapas/trafico.

### 4.2 Nivel 2 - Contenedores

![C4 Contenedores Alternativa B](diagramas_c4/imagenes_python_graphviz/alternativa_B_n2_contenedores.png)

| Contenedor | Plataforma | Tecnologia / responsabilidad |
|---|---|---|
| Gateway y Gobierno API | Azure | Azure API Management; contratos, OAuth/OIDC, cuotas, rate limiting y APIs mock. |
| OMS e Inventario APP-02 | Azure | AKS; ordenes, validacion, deduplicacion, reservas, liberaciones y conciliacion. |
| Repositorio transaccional | Azure | Azure SQL; ordenes, inventario y estado operacional. |
| Adaptador TMS | Azure | Integracion con APP-11 para despacho y rutas. |
| Hub principal de eventos PLT-03 | AWS | EventBridge; eventos canonicos, reglas, fan-out y ruteo. |
| Colas, DLQ y Replay | AWS | SQS + workers; retry, mensajes fallidos, reproceso y backpressure. |
| Adaptadores y validadores | AWS | Lambda/ECS; normalizacion, validacion y consumidores por dominio. |
| Backend movil | AWS | ECS/Lambda; store-and-forward, acks, tracking y excepciones. |
| Repositorio sync movil | AWS | DynamoDB logico; eventos pendientes y estado offline. |
| Repositorio evidencias | AWS | S3 + KMS; fotos, firmas, hash, cifrado y retencion. |
| Optimizador dinamico | GCP | Cloud Run/GKE; trafico, capacidad, ventanas, cadena de frio, seguridad y SLA. |
| Analitica | GCP | Pub/Sub, Dataflow, BigQuery y Vertex AI. |

**Flujo clave:** Cliente -> API Management -> OMS Azure -> EventBridge AWS -> SQS/workers -> TMS, portal/CRM, backend movil y GCP.

### 4.3 Nivel 3 - Componentes de PLT-03

![C4 Componentes Alternativa B](diagramas_c4/imagenes_python_graphviz/alternativa_B_n3_componentes.png)

Componentes principales **PLT-03 en AWS**:

- **Event Ingestion:** recibe eventos desde OMS/Inventario, backend movil y legados.
- **Schema Lambda:** valida contratos, versionado y compatibilidad.
- **EventBridge Rules:** enruta eventos por dominio, prioridad, SLA y consumidor.
- **SQS Queues:** desacopla consumidores y permite absorcion de picos.
- **Ordering Guard:** mantiene secuencia por agregado.
- **Retry Worker:** aplica reintentos con backoff y jitter.
- **DLQ Processor:** captura mensajes fallidos y registra causa/responsable.
- **Replay Worker:** permite reproceso auditado por rol.
- **Backpressure Controller:** regula velocidad cuando consumidores se degradan.
- **Audit / Event Store:** conserva trazabilidad de intercambio.

---

## 5. Trazabilidad requerimientos - diseno

| Requerimiento / iniciativa | Elemento de diseno Alternativa B |
|---|---|
| INI-01 ordenes e inventario | OMS/Inventario en Azure, Azure SQL, publicacion hacia AWS, idempotencia y conciliacion WMS/ERP. |
| INI-02 API-first/event-driven | Azure API Management, AWS EventBridge, SQS, DLQ, replay, backpressure y contratos canonicos. |
| INI-03 ultima milla | Backend movil AWS, store-and-forward, DynamoDB logico, S3/KMS, acks y taxonomia de excepciones. |
| INI-04 rutas | Optimizador dinamico GCP integrado por eventos consumidos desde AWS. |
| INI-05 observabilidad/seguridad | CloudWatch/X-Ray, Azure Monitor, correlation ID, Secrets Manager, Key Vault, KMS e IaC. |
| INI-06 conciliacion | Evidencias, estados, tracking, OMS, TMS, ERP y auditoria de eventos federada. |

---

## 6. Architectural Decision Records (ADR)

### ADR-B-001 - Hub principal en AWS

| Campo | Decision |
|---|---|
| Estado | Propuesto |
| Contexto | Ultima milla, tracking, evidencias y excepciones se originan naturalmente en AWS. |
| Decision | Implementar PLT-03 en AWS con EventBridge, SQS y workers. |
| Consecuencias | Ultima milla mas integrada; mayor puente critico Azure -> AWS. |
| Alternativas descartadas | Hub central Azure para eventos corporativos; integraciones punto a punto. |

### ADR-B-002 - APP-02 permanece en Azure como OMS

| Campo | Decision |
|---|---|
| Estado | Propuesto |
| Contexto | Hito 1 ya ubica APP-02 en el eje Azure/API governance. |
| Decision | APP-02 evoluciona a OMS en Azure y publica eventos hacia AWS. |
| Consecuencias | Menor cambio para OMS; mayor necesidad de bridge confiable. |
| Alternativas descartadas | Migrar OMS a AWS durante el MVP. |

### ADR-B-003 - Ultima milla y eventos moviles en AWS

| Campo | Decision |
|---|---|
| Estado | Propuesto |
| Contexto | APP-15, APP-16, S3, DynamoDB logico y backend movil se benefician de cercania al hub AWS. |
| Decision | Mantener mobile backend, evidencias y eventos moviles dentro de AWS. |
| Consecuencias | Menor latencia movil; mayor gobierno cruzado con Azure. |
| Alternativas descartadas | Enviar eventos moviles primero a Azure como hub central. |

### ADR-B-004 - Observabilidad federada

| Campo | Decision |
|---|---|
| Estado | Propuesto |
| Contexto | El plano operacional queda distribuido entre Azure, AWS y GCP. |
| Decision | Usar OpenTelemetry, correlation ID, CloudWatch/X-Ray, Azure Monitor y GCP Monitoring. |
| Consecuencias | Permite trazabilidad; exige mayor disciplina de correlacion y dashboards federados. |

---

## 7. Vista de despliegue por plataforma

```text
Cloud AWS (EEUU)              Cloud MS Azure (EEUU)          Cloud GCP (EEUU)
----------------              ---------------------          ----------------
PLT-03 EventBridge            Azure API Management           Pub/Sub analitico
SQS colas / DLQ / replay      OMS APP-02 en AKS              Cloud Run/GKE rutas
Lambda/ECS validators         Azure SQL                      Dataflow
Backend movil ECS/Lambda      Adaptador TMS                  BigQuery
DynamoDB logico               Entra ID + Key Vault           Vertex AI
S3 + KMS evidencias           Azure Monitor
CloudWatch + X-Ray
Secrets Manager + IAM

On premises / SaaS
------------------
WMS APP-06 / APP-07
TMS APP-11
ERP APP-25
Portal B2B / CRM
Canales legados
```

---

## 8. Riesgos y mitigaciones

| Riesgo | Mitigacion |
|---|---|
| Bridge Azure -> AWS se vuelve critico. | Outbox en OMS, retry, DLQ, circuit breaker, health checks y monitoreo de latencia. |
| Doble gobierno API/eventos. | RACI formal, contratos canonicos, ownership de eventos y revision de arquitectura. |
| Observabilidad distribuida. | Correlation ID obligatorio, OpenTelemetry y tableros federados. |
| Costos de transferencia intercloud. | FinOps por dominio, medicion de trafico, presupuestos y limites por SLA. |
| Inconsistencia OMS/EventBridge. | Idempotencia, ordering guard, reconciliacion y auditoria de eventos. |

---

## 9. Recomendacion

La **Alternativa B** es viable, especialmente si RutaExpress decide priorizar AWS como plataforma estrategica de eventos y ultima milla.

