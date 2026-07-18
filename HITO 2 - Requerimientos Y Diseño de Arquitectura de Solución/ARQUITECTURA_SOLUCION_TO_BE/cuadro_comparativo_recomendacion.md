# Cuadro comparativo y recomendacion

## Criterios de evaluacion

Escala: 1 = bajo cumplimiento, 5 = alto cumplimiento.

| Criterio | Alternativa A: hub Azure + microservicios + PLT-03 | Alternativa B: Orquestacion + monolito modular | Evaluacion |
|---|---:|---:|---|
| Alineamiento con Hito 1 | 5 | 4 | Ambas evolucionan APP-02; A materializa mejor PLT-03 (outbox → `bus-workers` → Event Hubs → Service Bus) y desacoplamiento del ADM. |
| Cobertura RF/RNF INI-01 | 5 | 5 | Ambas cubren OMS/inventario; A separa servicios (OMS HTTP → Inventario); B concentra en un solo deploy. |
| Cobertura RF/RNF INI-02 | 5 | 3 | A implementa bus canonico, DLQ, replay y backpressure; B cubre API-first y notificaciones selectivas. |
| Cobertura RF/RNF INI-03 | 5 | 5 | Ambas mantienen AWS para app movil, store-and-forward y evidencias (`retry-worker` / adaptador en A). |
| Diferenciacion de estilo arquitectonico | 5 | 5 | Contraste real: microservicios + Saga OMS (HTTP) + EDA/PLT-03 vs orquestacion Durable Functions + monolito modular. |
| Complejidad de integracion | 3 | 4 | A tiene mas piezas async (outbox, `bus-workers`, Event Hubs, Service Bus); B concentra el core y reduce superficie distribuida. |
| Costo estimado relativo | 3 | 4 | B usa menos infraestructura de mensajeria corporativa; A paga resiliencia con mas servicios del bus. |
| Seguridad | 5 | 4 | Ambas federan identidad; A centraliza mejor gobierno de APIs + eventos en un plano Azure. |
| Observabilidad | 5 | 4 | A traza flujos async end-to-end via PLT-03; B traza workflows + APIs con menos fan-out. |
| Resiliencia en campanas | 5 | 3 | A absorbe picos con colas/backpressure; B depende de throttle/circuit breaker en el orquestador. |
| Escalabilidad | 5 | 3 | A escala por dominio (OMS, Inventario, bus); B escala el nucleo completo. |
| Impacto en aplicaciones existentes | 5 | 4 | A evoluciona APP-02 sin mezclar inventario en el mismo deploy; B concentra OMS+Inventario. |
| Riesgo de migracion | 4 | 4 | A adopta EDA/PLT-03 desde el diseño; B es mas simple al inicio pero implica rework si luego se adopta el hub completo. |
| Facilidad de MVP con API mock | 4 | 5 | B permite mocks y flujo orden-reserva mas rapido de demostrar. |
| Gobierno FinOps | 4 | 4 | A tiene mas transferencia/eventos; B concentra compute en Azure core. |

## Puntaje

| Alternativa | Puntaje total | Resultado |
|---|---:|---|
| Alternativa A | 68 / 75 | Recomendada |
| Alternativa B | 61 / 75 | Viable como contraste de menor complejidad; no recomendada como primer TO BE |

## Recomendacion

La alternativa recomendada es la **Alternativa A**: hub central Azure con microservicios (OMS APP-02 e Inventario MS-INI01-02), Saga orquestada por OMS vía HTTP hacia Inventario/WMS, y **Bus de Eventos Central (PLT-03)** — outbox SQL → `bus-workers` → Event Hubs → Service Bus — para fan-out, DLQ y replay. AWS cubre ultima milla/evidencias; GCP, analitica/rutas.

Esta decision es la mas consistente con el caso RutaExpress (Cyber Days, WMS degradado, integridad multinube) y con el Hito 1: habilita INI-02 de forma completa, desacopla sistemas criticos y absorbe picos con colas, DLQ, replay y backpressure. La Alternativa B es un contraste arquitectonico valido cuando el comite prioriza time-to-MVP y simplicidad operativa (monolito modular + Durable Functions), pero cede resiliencia de campana y madurez del hub event-driven.

## Implicancias para implementacion

- Priorizar MVP sobre Alternativa A: Azure API Management (APP-01), OMS e Inventario en AKS, Azure SQL (estado + outbox), `bus-workers`, Event Hubs/Service Bus, backend movil AWS (`mobile-api` + `retry-worker`), S3, DynamoDB y adaptador hacia Event Hubs / GCP.
- Usar Alternativa B solo como escenario de comparacion de comite (estilo orquestado + monolito modular), no como baseline de implementacion.
- Mantener adaptadores transicionales hacia WMS Principal (APP-06), WMS Satelite (APP-07) y ERP Financiero (APP-25).
- Implementar primero los casos criticos de A: orden valida, duplicado/idempotencia, reserva HTTP, WMS degradado, DLQ/replay, entrega offline, evidencia corrupta y excepcion de ultima milla.
- Medir desde el inicio: correlation ID, backlog de outbox, DLQ, tracking tardio, evidencias pendientes, conflictos de inventario y SLA.
