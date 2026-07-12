# Dossier MVP — Hub central Azure
## RutaExpress Fulfillment & Transporte

> **Audiencia:** Comité de Arquitectura y evaluación UTEC.  
> **Contexto de negocio:** ver primero [`01_Resumen_Empresa_RutaExpress.md`](01_Resumen_Empresa_RutaExpress.md) (5 min).  
> **TO BE vs MVP vs Alternativa A:** ver [`01b_TOBE_vs_MVP_Alternativa_A.md`](01b_TOBE_vs_MVP_Alternativa_A.md) — evita la confusión «¿el Hito 3 implementa toda la Alternativa A?».  
> **Estado:** Documentación de diseño de implementación — **sin despliegue aún**.  
> **Nomenclatura (regla de oro):** cada **APP-XX**, **PLT-XX** y **MS-INI01-02** va siempre con su **nombre oficial** — catálogo en `HITO 1 - .../06_Mapa_Portafolio_Aplicaciones.md`. El prefijo **MS** significa *microservicio*; **MS-INI01-02** identifica el microservicio de inventario de la iniciativa **INI-01**, con ID propio distinto del catálogo **APP-01…APP-26**.  
> **Términos técnicos:** siglas y palabras en inglés llevan entre paréntesis un significado breve — glosario: [`00_INDICE_COMITE.md`](00_INDICE_COMITE.md) §Glosario breve.

---

## 1. Resumen integrado Hito 1 + Hito 2

### 1.0 Cómo se nombran iniciativas, aplicaciones, plataformas, microservicios y servicios en la nube

En este dossier no se usan abreviaturas informales («apps», «ML» sin nombre de aplicación, «MS inventario»). Cada mención lleva el **nombre oficial** y el **ID** cuando corresponda.

| Tipo | ID | Rol en la documentación | En el MVP |
|---|---|---|---|
| **Iniciativa** | INI-01 … INI-06 | Programa de transformación del roadmap (capacidades de negocio). **No es una aplicación.** | El MVP demuestra un **núcleo parcial** de **INI-01**, **INI-02** e **INI-03** — ver [`01b_TOBE_vs_MVP_Alternativa_A.md`](01b_TOBE_vs_MVP_Alternativa_A.md) |
| **Aplicación** | APP-01 … APP-26 | Aplicación del portafolio empresarial Hito 1 | p. ej. **Orquestador de Pedidos (APP-02)**, **App de Conductores (APP-15)** |
| **Plataforma** | PLT-01 … PLT-04 | Capacidad transversal (bus de eventos, identidad, observabilidad, infraestructura como código) | p. ej. **Bus de Eventos Central (PLT-03)** |
| **Microservicio de iniciativa** | MS-INIxx-yy | Componente técnico **nuevo** de una iniciativa; desplegable en AKS o ECS; **sin** ID **APP-XX** | **Microservicio Inventario y Reservas (MS-INI01-02)** |
| **Servicio en la nube** | — (nombre del proveedor) | Infraestructura administrada: AKS, Azure SQL, Event Hubs, Amazon S3, BigQuery | Donde **corren** aplicaciones y microservicios; no son aplicaciones del catálogo |

#### 1.0.1 Diferencias: aplicación vs microservicio vs plataforma vs servicio en la nube

| Pregunta | Aplicación (APP-XX) | Microservicio (MS-INIxx-yy) | Plataforma (PLT-XX) | Servicio en la nube |
|---|---|---|---|---|
| ¿Qué es? | Unidad de **portafolio** de negocio | Unidad técnica **de dominio**, desplegable | Capacidad **compartida** por todo el ecosistema | Recurso del **proveedor** (Azure/AWS/GCP) |
| ¿Ejemplo MVP? | **Orquestador de Pedidos (APP-02)** | **Microservicio Inventario y Reservas (MS-INI01-02)** | **Bus de Eventos Central (PLT-03)** | **AKS**, **Azure SQL**, **Amazon DynamoDB** |
| ¿Se compone de varias APP? | Una APP = un ID; puede tener varios workloads | **No** contiene otras aplicaciones APP | **No** — es transversal | **No** — es infraestructura |
| ¿De qué se compone? | Código + datos + integraciones; en MVP un workload en AKS | Código (API, dominio, outbox) + uso de SQL/Event Hubs | Event Hubs + Service Bus, Entra ID, Terraform, etc. | Clusters, bases de datos, colas, almacenamiento |

**Aplicación y microservicio no son lo mismo:** **Orquestador de Pedidos (APP-02)** es una **aplicación** del catálogo (negocio la reconoce como APP-02). **Microservicio Inventario y Reservas (MS-INI01-02)** es un **microservicio** creado porque INI-01 necesita dominio de inventario sin reutilizar **Control de Inventario (APP-08)** legado. Ambos pueden ejecutarse en el **mismo servicio AKS**, pero son **dos contenedores** distintos con IDs distintos.

**Un microservicio no agrupa varias aplicaciones:** **Microservicio Inventario y Reservas (MS-INI01-02)** es **una** pieza desplegable. Internamente tiene componentes (nivel 3 C4: API de reserva, repositorio, publicador de eventos). Externamente **consume** servicios en la nube (Azure SQL, Event Hubs) y **colabora** con **Orquestador de Pedidos (APP-02)** vía API y eventos; no “contiene” APP-02 dentro.

**INI-01** descompone órdenes e inventario en: **Orquestador de Pedidos (APP-02)** (aplicación del catálogo, evoluciona a OMS centralizado) y **Microservicio Inventario y Reservas (MS-INI01-02)** (reservas y disponibilidad — distinto de **Control de Inventario (APP-08)** y de **WMS Principal (On Premises) (APP-06)**).

### 1.1 El negocio y el dolor (Hito 1)

RutaExpress es operador logístico B2B/B2C con **14 centros de distribución**, **68.000 entregas/día** (picos **180.000** en campañas). El caso documenta:

| Problema | Evidencia del caso | Fase cadena de valor |
|---|---|---|
| Pedidos duplicados / sin idempotencia | 32.000 duplicados en campaña | F1 Recepción |
| WMS Principal (On Premises) (APP-06) / WMS Satélite (On Premises local) (APP-07) sin HA | 6 h caído en Cyber Days | F2 Preparación |
| Integraciones P2P sin Bus de Eventos Central (PLT-03) | Estados inconsistentes entre nubes | Transversal |
| **App de Conductores (APP-15)** offline frágil | 1.200 firmas perdidas | F4 Entrega |
| Excepciones sin taxonomía única | 34% fallas prevenibles | F5 Excepciones |
| Liquidación en Excel | 23 días conciliación, USD 2.4M retenidos | F6 Liquidación |

**Cadena de valor TO BE:** F1 Recepción → F2 Preparación → F3 Despacho → F4 Entrega → F5 Excepciones → F6 Liquidación.

### 1.2 Visión TO BE (Hito 1) vs qué hará el MVP (Hito 3)

El Hito 1 definió **hacia dónde va** RutaExpress en 36 meses mediante **seis iniciativas INI-01 a INI-06**. Una **iniciativa (INI)** es un bloque de capacidades del roadmap; **no** es una aplicación: cada INI puede involucrar varias **APP-XX**, **PLT-XX** y microservicios **MS-INIxx-yy**. El MVP del Hito 3 **no implementa todo el roadmap ni toda la Alternativa A**: implementa un **subconjunto demostrable** (**vertical slice** — corte end-to-end por capas) alineado con **INI-01**, **INI-02** e **INI-03**, usando mocks donde el legado aún no se migra.

> **Marco de alcance TO BE vs MVP:** [`01b_TOBE_vs_MVP_Alternativa_A.md`](01b_TOBE_vs_MVP_Alternativa_A.md) — **plano** (Alternativa A) → **maqueta** (MVP) → **casa entera** (producción).

#### A) Decisiones de arquitectura (válidas para roadmap y MVP)

Estas decisiones responden al **AS IS** (`01` §3), a los **dolores** (`01` §4) y al **perfil de carga** de cada dominio. El Hito 2 las formalizó en el diseño TO BE; aquí se **justifican por el caso**, no solo por el documento previo:

| Decisión | Qué significa | Por qué (caso, no circular) |
|---|---|---|
| **OMS centralizado = Orquestador de Pedidos (APP-02) evolucionado** | Orquestador de Pedidos (APP-02) gobierna el ciclo de vida completo de la orden como OMS centralizado. | Punto único de verdad de orden; evita duplicados (32k) y estados inconsistentes entre sistemas. |
| **Bus de Eventos Central (PLT-03) en Azure** | Bus de Eventos Central (PLT-03) con **Azure Event Hubs + Azure Service Bus** para eventos canónicos, colas, DLQ (cola de mensajes fallidos) y replay (reproceso auditado). | Integraciones hoy punto a punto; Cyber Days (240k en cola) exige stream + colas con DLQ/replay. |
| **GCP para analítica** | Lecturas, tableros y modelos de **ML / Optimización de Rutas (GCP) (APP-24)**; GCP no gobierna órdenes ni entregas en tiempo real. | Analítica ya en GCP; tracking masivo no debe bloquear SQL transaccional del OMS (CQRS — separar escritura y lectura, E8). |
| **App de Conductores (APP-15) y Almacenamiento Evidencias (S3) (APP-16) en AWS** | Última milla y evidencias siguen en AWS; Azure es el hub, no reemplaza la **App de Conductores (APP-15)**. | APP-15 y S3 ya en AWS; ACK (acuse de recibo) local y evidencias cerca del borde (1.200 firmas perdidas por red). |
| **Hub central Azure** | Azure hub + AWS última milla + GCP analítica (detalle en §1.3). | Orquestador, APIM y TMS **ya en Azure**; concentra OLTP (transaccional), Saga (pasos compensables) y bus sin re-plataformar móvil ni BQ en el MVP. |

#### B) Qué SÍ se hará en el MVP (implementación real)

| Elemento | En el MVP se construye/despliega | Cómo |
|---|---|---|
| **OMS centralizado / Orquestador de Pedidos (APP-02)** | Sí — workload en AKS | Crear orden, idempotencia, deduplicación, estado canónico, Saga con inventario. Es **aplicación del catálogo** (evolución de aplicación existente). |
| **Microservicio Inventario y Reservas (MS-INI01-02)** | Sí — workload en AKS | Reserva, liberación, consulta disponibilidad. Es **microservicio de INI-01** (ID **MS-INI01-02**); **no** tiene **APP-XX** ni es **Control de Inventario (APP-08)**. |
| **Bus de Eventos Central (PLT-03)** | Sí — Event Hubs + Service Bus | Publicar/consumir eventos, DLQ (cola de fallidos), retry (reintento), replay (reproceso), backpressure (frenado de ingesta) |
| **API Gateway + mocks** | Sí — Azure API Management (APP-01) | Entrada única; **simula** WMS Principal (On Premises) (APP-06), ERP Financiero (On Premises) (APP-25), Portal y TMS (Transportation Management) (APP-11) |
| **Backend móvil — App de Conductores (APP-15)** | Sí — **ECS Fargate** (contenedores sin administrar servidores en AWS) | Entrega offline, store-and-forward (guardar y reenviar), outbox (cola de salida) DynamoDB, retry SQS en el mismo task (tarea de contenedor) |
| **Almacenamiento Evidencias (S3) (APP-16)** | Sí — S3 + KMS (gestión de llaves de cifrado) | Firma/foto con hash SHA-256 (huella criptográfica) |
| **Proyección CQRS** (separar escritura y lectura) | Sí — Cloud Run + BigQuery | Consulta de tracking vía **`mock-portal`** en Azure API Management (APP-01) |
| **Observabilidad** | Sí — OpenTelemetry (trazas y métricas estándar) + Monitor/CloudWatch | Correlation ID (identificador de trazabilidad) end-to-end |
| **IaC** (infraestructura como código) | Sí — Terraform | 100% del despliegue MVP en las 3 nubes |

**Flujo que debe funcionar en la demo:** orden → reserva → evento → entrega offline → evidencia → consulta tracking.

#### C) Qué NO se hará en el MVP (queda en roadmap Hito 1)

| Elemento | En roadmap TO BE (Hito 1) | En el MVP |
|---|---|---|
| **WMS Cloud** (reemplazo **WMS Principal (On Premises) (APP-06)** / **WMS Satélite (On Premises local) (APP-07)**) | Sí — objetivo F2 | **No** — se usa **mock de WMS Principal (On Premises) (APP-06)** vía Azure API Management (APP-01) |
| **Migrar WMS Principal (On Premises) (APP-06) / WMS Satélite (On Premises local) (APP-07) real** | Sí — transición gradual | **No** — sin conexión VPN a CD Lima |
| **Liquidación automática** (INI-06, reemplazo **Sistema de Liquidación (Excel) (APP-26)**) | Sí — F6 | **No** |
| **Rutas dinámicas / aprendizaje automático en producción** (INI-04, **Optimizador de Rutas (GCP batch) (APP-12)** / **ML / Optimización de Rutas (GCP) (APP-24)**) | Sí — F3 | **No** — GCP solo proyección analítica básica |
| **Observabilidad/seguridad completa** (INI-05, **Plataforma de Observabilidad Unificada (PLT-01)** / **Plataforma de Identidad y Accesos (IAM) (PLT-02)** / **Plataforma IaC (PLT-04)** al 100%) | Sí — fundacional | **Parcial** — OTel + identidad básica, sin SIEM/MFA completo |
| **Deprecar Bucket S3 Legado (APP-04), Control de Inventario (APP-08), Sistema Impresión Manifiestos (APP-14), Sistema de Liquidación (Excel) (APP-26)** | Sí — roadmap | **No** — fuera de alcance demo |
| **Carga 180.000 órdenes/día** | Sí — diseño para campaña | **No** — smoke test (prueba mínima de arranque) con volumen bajo |
| **Vertex AI entrenado** | Sí — predicción excepciones | **No** — solo preparación de dataset en BigQuery |

#### D) Las 6 iniciativas del roadmap y el MVP

Cada fila es una **iniciativa (INI)** — programa de transformación, no una aplicación. La columna «En MVP v1» indica si el **prototipo** demuestra un **núcleo** de esa iniciativa (no el programa completo ni todos sus RF del Hito 2).

| Iniciativa | Nombre | Componentes típicos (aplicaciones / microservicios / plataformas) | En MVP v1 |
|:---:|---|---|:---:|
| **INI-01** | Órdenes e inventario end-to-end | **Orquestador de Pedidos (APP-02)** + **Microservicio Inventario y Reservas (MS-INI01-02)** | **Parcial** — núcleo demo (E1–E4) |
| **INI-02** | Integración API-First y Event-Driven | **Azure API Management (APP-01)** + **Bus de Eventos Central (PLT-03)** | **Parcial** — núcleo demo (E5, E8; backpressure — frenado de ingesta en E4) |
| **INI-03** | Última milla y excepciones | **App de Conductores (APP-15)** + **Almacenamiento Evidencias (S3) (APP-16)** + backend AWS | **Parcial** — núcleo demo (E6–E7) |
| **INI-04** | Optimización dinámica de rutas | **Optimizador de Rutas (GCP batch) (APP-12)**, **ML / Optimización de Rutas (GCP) (APP-24)** | No |
| **INI-05** | Observabilidad, seguridad y gobierno multinube | **Plataforma de Observabilidad Unificada (PLT-01)**, **Plataforma de Identidad y Accesos (IAM) (PLT-02)** | Parcial (solo base) |
| **INI-06** | Liquidación automatizada | Reemplazo **Sistema de Liquidación (Excel) (APP-26)** | No |

**Resumen en una frase:** el MVP prueba el **corazón operativo** (orden + bus + entrega + evidencia) en tres nubes; el **resto del TO BE** (WMS Cloud real, liquidación, optimización de rutas con **ML / Optimización de Rutas (GCP) (APP-24)**, seguridad plena) sigue planificado en el roadmap de 36 meses del Hito 1.

### 1.3 Reparto multinube del MVP

El prototipo concentra **gobierno operativo** en Azure, **última milla** en AWS y **lectura analítica** en GCP — el mismo reparto que el caso ya tiene en producción (`01` §3), unificado por **eventos** en lugar de integraciones ad hoc:

| Rol | Nube | Componentes principales |
|---|---|---|
| Gobierno API, OMS, inventario y reservas, bus de eventos | **Azure** | **Azure API Management (APP-01)**, **Orquestador de Pedidos (APP-02)** evolucionado a OMS, **Microservicio Inventario y Reservas (MS-INI01-02)**, **Bus de Eventos Central (PLT-03)**, Azure SQL, identidad y observabilidad base |
| Última milla y evidencias | **AWS** | App de Conductores (APP-15), backend móvil, Almacenamiento Evidencias (S3) (APP-16) |
| Analítica y proyección de lectura | **GCP** | Cloud Run, BigQuery (proyector CQRS en MVP; Pub/Sub y rutas = TO BE) |

**Por qué este reparto:** concentra en Azure el gobierno operativo (orden, eventos, colas, APIs) donde ya viven Orquestador de Pedidos (APP-02) y Azure API Management (APP-01); mantiene en AWS lo que el caso ya tiene en campo; usa GCP para consultas y analítica sin mezclar el plano transaccional.

| Dominio | Nube | Servicios seleccionados (criterio: costo intermedio + afinidad AS IS) |
|---|---|---|
| Gobierno API, OMS centralizado / Orquestador de Pedidos (APP-02), Microservicio Inventario y Reservas (MS-INI01-02), bus | **Azure** | API Management, AKS, Azure SQL, Event Hubs, Service Bus, Entra ID, Key Vault, Monitor |
| Última milla, evidencias | **AWS** | ECS Fargate, DynamoDB, S3+KMS, SQS, EventBridge |
| Analítica y eventos de rutas | **GCP** | Cloud Run, BigQuery (MVP); Pub/Sub, Vertex AI (TO BE / INI-04) |
| Transversal | Multinube | OpenTelemetry, Terraform (Plataforma IaC (PLT-04)), correlation ID |

**Patrones aplicados en el MVP** (referencia cruzada con ADR del Hito 2 — usar el **requisito del caso**, no el número ADR, ante el comité):

| Patrón | Qué resuelve en RutaExpress | Escenario demo |
|---|---|---|
| Hub de eventos (ADR-001) | Integraciones punto a punto → bus canónico | E5, E8 |
| OMS centralizado (ADR-002) | Orden dispersa entre sistemas | E1–E4 |
| Idempotencia (ADR-003) | Reintentos de red duplican órdenes | E1, E2 |
| Saga compensable (ADR-005) | Reserva + WMS sin transacción distribuida | E3, E4 |
| Store-and-forward (ADR-006) | Conductor sin red pierde evidencias | E6, E7 |
| DLQ y replay (ADR-008) | Cyber Days — mensajes fallidos recuperables | E4, E5 |
| IaC (ADR-012) | Requisito enunciado Hito 3 | Despliegue reproducible |

> Diseño TO BE completo y ADR: `HITO 2 - .../ARQUITECTURA_SOLUCION_TO_BE/02_Alternativa_A.md`

---

## 2. Objetivo del MVP (Hito 3)

Demostrar en prototipo desplegable —no en producción completa— que la **arquitectura hub central Azure** soporta el flujo crítico end-to-end con resiliencia y trazabilidad:

```text
Cliente B2B → Azure API Management (APP-01) — POST /api/v1/orders → OMS centralizado / Orquestador de Pedidos (APP-02) → Microservicio Inventario y Reservas (MS-INI01-02) → Bus de Eventos Central (PLT-03)
    → TMS (Transportation Management) (APP-11) (mock) → Backend móvil AWS → Entrega offline → Evidencia S3
    → Evento tracking/excepción → Bus de Eventos Central (PLT-03) → Consulta CQRS → mock-portal en **Azure API Management (APP-01)** / Tablero GCP
```

**Canales del MVP** (cada caso de uso tiene **un** canal en el prototipo; en producción pueden coexistir API y portal):

| Interacción | Canal definido en el MVP | Tecnología | Nota |
|---|---|---|---|
| **Alta de órdenes** (escritura) | API REST única | `POST /api/v1/orders` vía **Azure API Management (APP-01)** → **Orquestador de Pedidos (APP-02)** | Demo con Postman, script o cliente de prueba. **No** hay portal SaaS ni carga CSV en el MVP. |
| **Consulta de tracking** (lectura) | Mock de portal B2B | `GET /mock/portal/v1/tracking/{id}` en **Azure API Management (APP-01)** (`mock-portal`) | Simula **Portal B2B (Trazabilidad) (APP-18)**; lee proyección **CQRS** en BigQuery (GCP). |
| **Legado WMS / ERP / TMS** | Mocks en el mismo gateway | `mock-wms`, `mock-erp`, `mock-tms` en **Azure API Management (APP-01)** | Sustituyen **WMS Principal (On Premises) (APP-06)**, **ERP Financiero (On Premises) (APP-25)** y **TMS (Transportation Management) (APP-11)** on premises; no hay VPN al CD en el MVP. |

> En producción futura el cliente B2B podrá usar API y **Portal B2B (Trazabilidad) (APP-18)** real; en el **prototipo Hito 3** cada caso de uso tiene **un solo canal** implementado, con stack ya definido en §5.

### 2.1 Dentro del alcance MVP

Cada capacidad siguiente se **implementa y despliega** en el prototipo (código + infraestructura en las tres nubes), no solo se describe en diagramas. Los términos técnicos se mantienen porque son los del diseño; entre paréntesis va una explicación breve para el comité.

#### INI-01 — Órdenes e inventario end-to-end

Esta **iniciativa** cubre dos dominios desplegados en AKS: **Orquestador de Pedidos (APP-02)** (aplicación del catálogo) y **Microservicio Inventario y Reservas (MS-INI01-02)** (microservicio nuevo con ID **MS-INI01-02**, sin **APP-XX**).

**Registrar orden con idempotencia y deduplicación**

| Aspecto | Cómo se hará en el MVP |
|---|---|
| Entrada | Cliente B2B llama `POST /api/v1/orders` vía **Azure API Management (APP-01)** (puerta de entrada única: autenticación OAuth, cuotas y enrutamiento al backend). |
| Idempotencia | Cabecera HTTP **`Idempotency-Key`** (si el cliente reintenta por timeout de red, el sistema responde con la **misma orden ya creada**, sin duplicar). |
| Deduplicación | **Hash logístico** del pedido (huella calculada a partir de SKU, cantidades y dirección) + ventana temporal en **Orquestador de Pedidos (APP-02)** (detecta el mismo pedido enviado dos veces con claves distintas). |
| Persistencia | **Orquestador de Pedidos (APP-02)** en **AKS** (Kubernetes administrado en Azure) guarda la orden en **Azure SQL** con estado canónico (`CREATED` → `VALIDATED` → …). |
| Demo escenario E1–E2 | Crear orden válida; reenviar con misma idempotency-key o mismo hash y verificar que no se duplica. |

**Reservar inventario con Saga compensable**

| Aspecto | Cómo se hará en el MVP |
|---|---|
| Servicio | **Microservicio Inventario y Reservas (MS-INI01-02)** en AKS — microservicio de **INI-01** con ID **MS-INI01-02** (prefijo **MS** = microservicio; **no** es **APP-XX** del portafolio). Distinto de **Control de Inventario (APP-08)** (legado) y de **WMS Principal (On Premises) (APP-06)** (confirmación vía mock en MVP). |
| Reserva | Consulta disponibilidad por SKU/almacén en Azure SQL, crea registro de reserva y publica evento `InventoryReserved`. |
| Saga | **Saga** (secuencia coordinada de pasos **sin** una sola transacción de base de datos entre nubes) une: orden validada → reserva → llamada al **mock de WMS Principal (On Premises) (APP-06)**. |
| Compensación | Si el mock WMS responde error o timeout, se ejecuta **`ReleaseInventory`** (libera stock reservado) y la orden pasa a `ON_HOLD` (en espera, no se pierde la orden). |
| Demo escenario E3 | Inventario insuficiente → error de negocio; sin evento `ReservationConfirmed`. |
| Demo escenario E4 | Mock WMS 503/timeout → `ReleaseInventory` + orden `ON_HOLD`; circuit breaker (Saga INI-01) y backpressure (INI-02). |

#### INI-02 — Integración API-First y Event-Driven

Iniciativa centrada en **Azure API Management (APP-01)** y **Bus de Eventos Central (PLT-03)** — plataforma de mensajería, no una aplicación de negocio aislada.

**Publicar y consumir eventos canónicos**

| Aspecto | Cómo se hará en el MVP |
|---|---|
| Patrón Outbox | Tras guardar en SQL, el **Orquestador de Pedidos (APP-02)** y el **Microservicio Inventario y Reservas (MS-INI01-02)** escriben en tabla **outbox** (cola local en la misma BD: el evento solo se publica si la transacción de escritura fue exitosa). |
| Publicación | Worker en AKS lee outbox y publica a **Azure Event Hubs** (bus de ingesta de eventos en streaming, parte del **Bus de Eventos Central (PLT-03)**). |
| Entrega | **Azure Service Bus** (colas por consumidor con acuse de recibo) entrega a: **Microservicio Inventario y Reservas (MS-INI01-02)**, mock **TMS (Transportation Management) (APP-11)**, puente hacia AWS y proyector GCP. |
| Contrato | **Schema Validator** valida mensajes contra contrato **AsyncAPI** (especificación formal del formato del evento: campos, tipos y versión). |
| Demo | Ver evento `OrderValidated` → `InventoryReserved` en Monitor/Service Bus con el mismo **correlation ID** (identificador único que atraviesa todo el flujo). |

**DLQ, retry y replay controlado**

| Aspecto | Cómo se hará en el MVP |
|---|---|
| Retry | **Retry Scheduler** reintenta consumidores caídos con **backoff + jitter** (espera creciente entre reintentos, con aleatoriedad para no saturar). |
| DLQ | Mensajes que agotan reintentos van a **DLQ** (Dead Letter Queue: cola de mensajes fallidos con payload y causa del error). |
| Replay | **Replay Controller** permite reprocesar desde DLQ con rol autorizado (auditoría de quién relanzó qué mensaje). |
| Backpressure | Si el mock **WMS Principal (On Premises) (APP-06)** está degradado, **Backpressure Controller** reduce la velocidad de ingesta (evita colapsar el **Orquestador de Pedidos (APP-02)** como en Cyber Days). |
| Demo escenario E4 | Mock WMS 503/timeout: circuit breaker en Saga + backpressure activo; sin cola infinita (cruza INI-01 e INI-02). |
| Demo escenario E5 | Enviar evento inválido → cae en DLQ; operaciones hace replay y se registra en auditoría. |

#### INI-03 — Última milla y excepciones

Iniciativa materializada en las aplicaciones **App de Conductores (APP-15)** y **Almacenamiento Evidencias (S3) (APP-16)** en AWS, con backend móvil en **ECS Fargate**.

**Entrega offline (store-and-forward)**

| Aspecto | Cómo se hará en el MVP |
|---|---|
| Backend | API en **ECS Fargate** (contenedores serverless en AWS) soporta **App de Conductores (APP-15)**. |
| Offline | **Store-and-forward** en dos capas: (1) **outbox local cifrado en el dispositivo** mientras no hay red — firma, foto, GPS y evento quedan en el teléfono (INI-03 RF-02); (2) al recuperar conectividad hacia AWS, la aplicación envía el lote a **ECS Fargate**, que escribe en **DynamoDB** (outbox del backend) y **S3**, y responde ACK al móvil (RF-03, RF-04). |
| Sincronización | El backend AWS reintenta el **puente** **SQS** + **EventBridge** → **Event Hubs** en Azure cuando hay conectividad multinube (el móvil no habla con Azure). |
| Ack | **Ack Tracker** en DynamoDB: el móvil solo borra la copia local cuando el backend confirmó recepción y persistencia en AWS. |
| Demo escenario E6 | Simular sin red → datos solo en outbox local del dispositivo; al reconectar con AWS → sync a DynamoDB/S3 sin pérdida; puente a Azure puede demorarse. |

**Evidencia con integridad en S3**

| Aspecto | Cómo se hará en el MVP |
|---|---|
| Almacenamiento | Fotos/firmas en **Almacenamiento Evidencias (S3) (APP-16)** con cifrado **KMS** (llaves gestionadas por AWS). |
| Integridad | **SHA-256** (huella digital del archivo: cualquier cambio altera el hash) calculado al subir; se rechaza si no coincide al conciliar. |
| Manifest | Archivo **manifest** de auditoría (lista de evidencias con hash, timestamp y orden asociada). |
| Demo escenario E7 | Subir evidencia corrupta → rechazo; evidencia válida → hash verificable. |

**Taxonomía de excepciones**

| Aspecto | Cómo se hará en el MVP |
|---|---|
| Validación | **Exception Taxonomy Validator**: motivo obligatorio desde lista cerrada (ej. `RECIPIENT_ABSENT`, `ADDRESS_WRONG`) — no texto libre. |
| Evento | Publica `ExceptionRaised` al **Bus de Eventos Central (PLT-03)** para CRM/portal y analítica futura. |
| Demo | Registrar entrega fallida sin motivo → error; con motivo válido → evento trazable. |

#### Transversal — Observabilidad, mocks e IaC

**Observabilidad end-to-end**

| Aspecto | Cómo se hará en el MVP |
|---|---|
| Trazas | **OpenTelemetry** (estándar abierto de métricas, logs y trazas) en **Orquestador de Pedidos (APP-02)**, **Microservicio Inventario y Reservas (MS-INI01-02)**, backend móvil y proyector GCP. |
| Correlación | **`correlation-id`** propagado en HTTP headers y metadatos de eventos (mismo ID desde la orden hasta la entrega para seguir el hilo en logs). |
| Destinos | **Azure Monitor** + **CloudWatch** + **Cloud Logging** (paneles básicos; sin SIEM corporativo completo). |
| Demo | Buscar un `correlation-id` y ver el recorrido en las tres nubes. |

**APIs mock de sistemas legados**

| Mock | Simula | Comportamiento en MVP |
|---|---|---|
| `mock-wms` | **WMS Principal (On Premises) (APP-06)** | Confirmación de reserva; modo **503** (servicio no disponible) para probar **circuit breaker** (corte automático de llamadas a sistema degradado). |
| `mock-erp` | **ERP Financiero (On Premises) (APP-25)** | Valorización async (respuesta 202: aceptado, procesa después). |
| `mock-portal` | **Portal B2B (Trazabilidad) (APP-18)** | Consulta tracking desde proyección **CQRS** (lectura en BigQuery, separada de la escritura transaccional). |
| `mock-tms` | **TMS (Transportation Management) (APP-11)** | Recibe evento de despacho / manifiesto. |
| Despliegue | Contratos **OpenAPI** (especificación REST) importados en **Azure API Management (APP-01)** vía Terraform. |

**Consulta de tracking (CQRS)**

| Aspecto | Cómo se hará en el MVP |
|---|---|
| Escritura | Orden, reserva y estados en **Azure SQL** (lado transaccional). |
| Lectura | **Cloud Run** (GCP) consume eventos y proyecta a **BigQuery** (almacén analítico de consultas). |
| API consulta | Portal mock lee tabla de proyección — sin consultar SQL transaccional en cada refresh. |
| Demo escenario E8 | Misma versión de estado en evento origen y en API de consulta. |

**Infraestructura como código (IaC)**

| Aspecto | Cómo se hará en el MVP |
|---|---|
| Herramienta | **Terraform** bajo **Plataforma IaC (PLT-04)**: módulos por nube (Azure, AWS, GCP). |
| Aplicaciones y microservicios en AKS | **Helm** (empaquetado de manifiestos Kubernetes) despliega **Orquestador de Pedidos (APP-02)**, **Microservicio Inventario y Reservas (MS-INI01-02)** y workers en AKS. |
| Pipeline | `plan` → aprobación manual → `apply` secuencial por nube; smoke tests E1–E8 al final. |

### 2.2 Fuera del alcance MVP (roadmap post-MVP)

- Liquidación automática completa (INI-06).
- Optimización dinámica de rutas en producción (INI-04).
- Migración real WMS Cloud / deprecación **WMS Principal (On Premises) (APP-06)** / **WMS Satélite (On Premises local) (APP-07)**.
- MFA/Zero Trust completo, private endpoints y SIEM corporativo.
- Carga de 180.000 órdenes/día (solo prueba de diseño y smoke test).
- Validación de direcciones / geocoding y **ingesta CSV/S3** de clientes medianos (Fase 1 TO BE).
- Colas Service Bus **por prioridad SLA** (express/estándar) y cuotas por cliente B2B más allá del rate limit genérico de APIM.
- Confirmación WMS **asíncrona diferida** ante caída prolongada del legado on premises (modo degradado producción).
- **Pub/Sub (GCP)** como entrada alternativa al proyector; el MVP usa **Event Hubs → Cloud Run** directo.

---

## 3. Patrones de arquitectura aplicados

El enunciado exige mínimo 3; el MVP implementa **seis** de forma explícita:

| Patrón | Dónde se aplica en el MVP | Por qué |
|---|---|---|
| **Microservicios** | OMS centralizado / Orquestador de Pedidos (APP-02), Microservicio Inventario y Reservas (MS-INI01-02), Integración eventos, Backend móvil, Consumidor analítico GCP | Dominios desacoplados; solo **Orquestador de Pedidos (APP-02)**, **App de Conductores (APP-15)** y **Almacenamiento Evidencias (S3) (APP-16)** son aplicaciones del catálogo |
| **DDD** | Bounded contexts (límites de dominio): Orden (**Orquestador de Pedidos (APP-02)**), Inventario (**Microservicio Inventario y Reservas (MS-INI01-02)**), Integración (**Bus de Eventos Central (PLT-03)**), Última milla (**App de Conductores (APP-15)**), Analítica | Evita reglas de negocio en canales; lenguaje ubicuo del caso |
| **EDA** (arquitectura orientada a eventos) | Bus de Eventos Central (PLT-03) como backbone; eventos OrderCreated, InventoryReserved, DeliveryCompleted, ExceptionRaised | Desacopla Azure/AWS/GCP y reemplaza P2P (punto a punto) |
| **CQRS** (separar escritura y lectura) | Escritura en Azure SQL (**Orquestador de Pedidos (APP-02)** + **Microservicio Inventario y Reservas (MS-INI01-02)**); lecturas en proyección BigQuery + API consulta tracking | Portales/tableros sin cargar transaccional |
| **Saga** | Orden → reserva → confirmación WMS Principal (On Premises) (APP-06) (mock) → despacho; compensación ReleaseInventory | No hay transacción distribuida única con on premises |
| **Resiliencia** | Outbox, idempotencia, retry+jitter (reintento con espera aleatoria), circuit breaker (corte ante fallos) hacia mocks, DLQ, backpressure, store-and-forward | Caso Cyber Days: colas, WMS Principal (On Premises) (APP-06) degradado, offline móvil |

---

## 4. Arquitectura lógica del MVP

### 4.1 Bounded contexts (DDD)

```text
┌─────────────────────────────────────────┐   ┌──────────────────────────────────┐   ┌─────────────────────────────────────┐
│ Orden — OMS centralizado /              │   │ Microservicio Inventario y       │   │ Integración — Bus de Eventos        │
│ Orquestador de Pedidos (APP-02)         │   │ Reservas (MS-INI01-02)           │   │ Central (PLT-03) Event Hubs + SB    │
│ Azure AKS                               │──▶│ ID MS-INI01-02, no APP-XX        │──▶│                                     │
└────────┬────────────────────────────────┘   └────────┬─────────────────────────┘   └──────────┬──────────────────────────┘
         │ Saga                                        │ eventos                          │ fan-out (un evento a varios consumidores)
         ▼                                             ▼                                  ▼
┌─────────────────────────┐   ┌──────────────────────────────────┐   ┌─────────────────────────────────────┐
│ Última milla            │   │ Evidencias                       │   │ Analítica (GCP)                      │
│ App de Conductores      │   │ Almacenamiento Evidencias (S3)   │   │ Cloud Run + BigQuery (CQRS)          │
│ (APP-15) AWS            │   │ (APP-16)                         │   │                                      │
└─────────────────────────┘   └──────────────────────────────────┘   └─────────────────────────────────────┘
```

### 4.2 Flujo Saga — orden con reserva (happy path)

1. Cliente invoca `POST /api/v1/orders` (Azure API Management (APP-01)) con `Idempotency-Key`.
2. **OMS centralizado / Orquestador de Pedidos (APP-02)** valida, deduplica, persiste orden, escribe **outbox**.
3. Worker publica `OrderValidated` a **Event Hubs**.
4. **Microservicio Inventario y Reservas (MS-INI01-02)** consume, reserva stock, publica `InventoryReserved`.
5. Adaptador llama **mock de WMS Principal (On Premises) (APP-06)**; si OK, publica `ReservationConfirmed`.
6. **mock de TMS (Transportation Management) (APP-11)** recibe evento de despacho (opcional en demo).
7. Conductor completa entrega offline → **backend móvil** outbox → SQS → puente → Event Hubs.
8. Evidencia a **S3** con hash; evento `DeliveryCompleted` al Bus de Eventos Central (PLT-03).
9. Proyector **GCP** actualiza tabla consulta tracking/SLA.

**Compensación:** si mock de WMS Principal (On Premises) (APP-06) falla → `ReleaseInventory` + orden `ON_HOLD`.

### 4.3 APIs mock (Azure API Management (APP-01))

| Mock | Simula | Comportamiento configurable |
|---|---|---|
| `mock-wms` | **WMS Principal (On Premises) (APP-06)** | 200 OK / 503 degradado / timeout (circuit breaker) |
| `mock-erp` | **ERP Financiero (On Premises) (APP-25)** | Valorización inventario async |
| `mock-portal` | **Portal B2B (Trazabilidad) (APP-18)** | **Solo lectura:** `GET /mock/portal/v1/tracking/{id}` desde proyección CQRS (no crea órdenes) |
| `mock-tms` | **TMS (Transportation Management) (APP-11)** | Recibe despacho y actualiza manifiesto |

Los mocks permiten MVP sin VPN a on premises; contratos OpenAPI versionados en Azure API Management (APP-01).

---

## 5. Stack seleccionado por nube

> Servicios **administrados de costo intermedio**, elegidos por **perfil de carga**, **dolores E1–E8** y **AS IS** del cliente. Comparativas (AKS vs Functions, Fargate vs Lambda): [`06_Preguntas_Argumentos_Comite.md`](06_Preguntas_Argumentos_Comite.md) §3–4.

### Azure (hub operativo)

| Servicio | Rol en MVP | Justificación |
|---|---|---|
| Azure API Management (APP-01) (Developer/Standard) | Gateway, OAuth, rate limit, mocks | Entrada única; mocks sin VPN; OAuth y cuotas antes del backend |
| AKS (2–3 nodos) | **Orquestador de Pedidos (APP-02)** (aplicación), **Microservicio Inventario y Reservas (MS-INI01-02)** (microservicio), workers outbox | API + Saga + workers de fondo (outbox, bus) en procesos de vida larga; dos dominios en un cluster |
| Azure SQL (S1/S2) | Estado transaccional **Orquestador de Pedidos (APP-02)** + **Microservicio Inventario y Reservas (MS-INI01-02)** | Consistencia relacional Saga/outbox |
| Event Hubs (Standard, 1 TU) | Ingesta eventos canónicos Bus de Eventos Central (PLT-03) | Throughput para campañas y flujos orden → inventario → tracking |
| Service Bus (Standard) | Colas, DLQ, replay | Colas por consumidor, mensajes fallidos y reproceso auditado |
| Azure Cache for Redis (Basic) | Catálogo SLA, dedup (deduplicación) cache | Latencia validación sin cargar SQL |
| Entra ID + Key Vault | Identidad y secretos Plataforma de Identidad y Accesos (IAM) (PLT-02) | Federación; sin secretos en código |
| Azure Monitor + App Insights | Métricas y trazas Azure | Plataforma de Observabilidad Unificada (PLT-01) parcial; OpenTelemetry export |

### AWS (última milla)

| Servicio | Rol en MVP | Por qué |
|---|---|---|
| ECS Fargate | API backend móvil + Retry Worker (mismo task) | **App de Conductores (APP-15)**: un solo servicio; polling (consulta periódica) de SQS con jitter (espera aleatoria entre reintentos) hacia el puente Azure |
| DynamoDB on-demand | Outbox móvil, estado sync | Baja latencia offline; ya en caso |
| S3 + KMS | Evidencias **Almacenamiento Evidencias (S3) (APP-16)** | Integridad, costo, escalabilidad |
| SQS + EventBridge | Buffer y puente hacia Azure | Desacopla móvil del hub |
| CloudWatch + X-Ray | Observabilidad AWS | Trazas federadas con OTel |

### GCP (analítica)

| Servicio | Rol en MVP | Por qué |
|---|---|---|
| Cloud Run | Proyector CQRS — consume eventos desde **Event Hubs** (puente Azure) | Escala a cero; camino MVP: EH → Cloud Run → BigQuery |
| BigQuery (sandbox) | Proyección CQRS tracking/SLA | Alimenta `GET /mock/portal/v1/tracking/{id}` en **Azure API Management (APP-01)** |
| Pub/Sub | *(post-MVP / TO BE)* | Patrón GCP nativo alternativo; **no** en v1 del prototipo |
| Vertex AI | **Solo preparación** dataset excepciones | INI-03 futuro; no entrenamiento pesado en MVP |

---

## 6. Criterios de éxito del MVP (demo comité)

| # | Escenario | Resultado esperado |
|---|---|---|
| E1 | Crear orden válida con idempotency-key | Una sola orden; replay devuelve misma respuesta |
| E2 | Reenviar orden duplicada (mismo hash) | Rechazo o vínculo a orden existente |
| E3 | Reservar inventario insuficiente | Error negocio; sin evento ReservationConfirmed |
| E4 | mock de WMS Principal (On Premises) (APP-06) en 503 | Circuit breaker; backpressure; sin cola infinita |
| E5 | Mensaje inválido al **Bus de Eventos Central (PLT-03)** | DLQ con payload; replay auditado |
| E6 | Entrega offline | Eventos en DynamoDB outbox; sync al reconectar |
| E7 | Evidencia corrupta (hash inválido) | Rechazo; no concilia |
| E8 | Consulta tracking | Misma versión en API consulta (CQRS) y evento origen |

---

## 7. Riesgos del MVP y mitigación

| Riesgo | Mitigación |
|---|---|
| Costo egress intercloud | Eventos compactos, batch, una región US-East coherente |
| Complejidad Terraform 3 nubes | Módulos por proveedor; un `environment/mvp` |
| Azure como SPOF | Particiones Event Hubs, health checks, runbook DLQ |
| Scope creep | Alcance fijado a INI-01/02/03; mocks para legado |

---

## 8. Próximo paso (post-aprobación comité)

1. Crear repositorio `terraform/` según doc `04`.
2. Implementar microservicios **Orquestador de Pedidos (APP-02)** y **Microservicio Inventario y Reservas (MS-INI01-02)** (.NET o Node en AKS — stack **Orquestador de Pedidos (APP-02)**).
3. Implementar backend móvil en AWS.
4. Configurar Azure API Management (APP-01) mocks y políticas.
5. Pipeline CI/CD: plan/apply por nube con aprobación manual.
6. Ejecutar suite escenarios E1–E8 con datos del caso.

---

*Ver diagramas C4 detallados en [`03_C4_Model_MVP.md`](03_C4_Model_MVP.md) e IaC/costos en [`04_IaC_Costos_Despliegue.md`](04_IaC_Costos_Despliegue.md).*
