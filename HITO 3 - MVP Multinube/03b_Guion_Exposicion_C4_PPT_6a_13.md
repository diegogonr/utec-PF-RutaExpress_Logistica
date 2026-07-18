# Guion de exposición C4 — solo diagramas

Texto oral para explicar los diagramas C4. Fuente: [03_C4_Model_MVP.md](03_C4_Model_MVP.md).

**Regla:** distinguir **implementado**, **parcial** y **objetivo**. Flecha discontinua ≠ terminado.

**Nombres canónicos:** `bus-workers`, `retry-worker`, BFF del MVP, Adaptador AWS→Azure, Inventario y Reservas (no “el WMS”).

---

## Antes del primer diagrama

> "Usamos C4 enriquecido con despliegue multinube. N1: personas y sistemas. N2: contenedores e infraestructura. N3: módulos internos con su runtime. Son diagramas híbridos, no C4 puros."

---

## N1 — Contexto

**Señalar:** Cliente B2B, Conductor, Operaciones, plataforma central, legados.

> "Quién usa RutaExpress y con quién habla. El Cliente B2B crea órdenes y consulta tracking. El conductor registra entregas y evidencias. Operaciones supervisa. La plataforma coordina Azure, AWS y GCP. WMS, ERP, Portal B2B y TMS son contratos externos; en el MVP se simulan."

**Clave:** N1 es negocio y fronteras; aún no hay pods ni microservicios.

---

## N2 — Contenedores

**Señalar:** Azure (APIM, AKS, SQL, Event Hubs, Service Bus) · AWS (Fargate, SQS, EventBridge) · GCP (Cloud Run, BigQuery).

> "Cada nube tiene un rol. Azure es hub operativo: órdenes, inventario y eventos. AWS es última milla y evidencias. GCP prepara lectura CQRS. No es simetría: ubicamos cada capacidad donde aporta valor."

> "APIM es el gateway. Un AKS compartido ejecuta BFF, OMS, Inventario y bus-workers. Azure SQL guarda estado y outbox. Event Hubs es el stream implementado. Service Bus es cola/DLQ, en gran parte objetivo."

> "La Saga reserva inventario por HTTP. El WMS mock pasa por APIM. bus-workers lee el outbox en SQL y publica en Event Hubs; no es Service Bus."

> "En AWS: mobile-api y retry-worker en Fargate. Puente objetivo: SQS → retry-worker → EventBridge → Adaptador AWS→Azure → Event Hubs. En GCP el tracking real sigue objetivo; hoy el portal es mock en APIM."

**Clave:** AKS = runtime compartido; cada Docker = un deployment. Docker empaqueta; el contenedor C4 es la unidad ejecutable.

---

## N3 — OMS (Orquestador de Pedidos)

**Señalar:** Order API → dominio → SQL/outbox → Saga → Inventario; Saga → Circuit Breaker → APIM → mock WMS.

> "Componentes lógicos del mismo Deployment, no pods aparte. Order API recibe; Dedup e Idempotency evitan duplicados; Aggregate y State Machine aplican reglas; repositorios persisten orden y outbox en Azure SQL."

> "La Saga reserva en Inventario por HTTP y confirma al WMS vía Circuit Breaker y APIM mock-wms. Si el WMS falla después de reservar, Release compensa. La publicación canónica la completa bus-workers desde el outbox hacia Event Hubs."

**Clave:** HTTP a Inventario hoy; Service Bus para esa reserva es objetivo.

---

## N3 — Inventario y Reservas

**Señalar:** Reserve/Release API → handlers → Aggregate → SQL; Queue Consumer discontinuo.

> "Dominio nuevo de reservas; no es el WMS legado. Reserve y Release reciben al OMS. Idempotency, Aggregate y Policy aplican reglas; repositorios escriben en Azure SQL con outbox."

> "Entrada HTTP implementada. Queue Consumer y Backpressure muestran el camino objetivo por Service Bus."

**Clave:** Separar Inventario del WMS permite demostrar reserva y compensación sin integrar el legado real.

---

## N3 — Bus de Eventos (`bus-workers`)

**Señalar:** Outbox Poller → SQL → Event Hubs Publisher → Event Hubs; bloques objetivo; BFF → Service Bus (E5).

> "PLT-03 combina código y PaaS. bus-workers: el poller lee pendientes en Azure SQL y el publisher envía a Event Hubs. Schema Validator, Dispatcher, Replay y Backpressure son objetivo."

> "Tramo confirmado: productor escribe outbox → bus-workers consulta → Event Hubs. En E5 el BFF demuestra la DLQ nativa de Service Bus; replay automático sigue objetivo."

**Clave:** Outbox = intención de publicar. Event Hubs = stream. Service Bus = cola. No son el mismo servicio.

---

## N3 — Backend móvil

**Señalar:** App + SQLite; ALB → Delivery API; DynamoDB/S3; SQS → retry-worker → EventBridge (discontinuo).

> "Última milla en AWS. Sin red, SQLite en el dispositivo. Con red: BFF → ALB → Delivery API en mobile-api sobre Fargate. Dominio valida novedad y evidencia; DynamoDB/S3/KMS son la persistencia prevista, aún parcial."

> "Puente objetivo: Outbox Relay → SQS → retry-worker consume → EventBridge → Adaptador AWS→Azure → Event Hubs. La flecha de consumo sale de SQS hacia el worker."

**Clave:** Infra AWS lista; ACK durable y puente a Azure no son cadena productiva cerrada.

---

## Cierre

> "El MVP demuestra el flujo crítico de órdenes en Azure, con mocks gobernados y outbox hacia Event Hubs, más la base multinube en AWS y GCP. Evaluamos decisiones y ruta evolutiva, no una Alternativa A ya cableada por completo."
