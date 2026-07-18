# Cuadro comparativo y recomendacion

## Criterios de evaluacion

Escala: 1 = bajo cumplimiento, 5 = alto cumplimiento.

| Criterio | Alternativa A: EDA + microservicios + hub Azure | Alternativa B: Orquestacion + monolito modular | Evaluacion |
|---|---:|---:|---|
| Alineamiento con Hito 1 | 5 | 4 | Ambas evolucionan APP-02; A materializa mejor PLT-03 y desacoplamiento previsto en ADM. |
| Cobertura RF/RNF INI-01 | 5 | 5 | Ambas cubren OMS/inventario; B gana consistencia local, A gana conciliacion distribuida. |
| Cobertura RF/RNF INI-02 | 5 | 3 | A implementa bus canonico, DLQ, replay y backpressure; B cubre API-first y notificaciones selectivas. |
| Cobertura RF/RNF INI-03 | 5 | 5 | Ambas mantienen AWS para app movil, store-and-forward y evidencias. |
| Diferenciacion de estilo arquitectonico | 5 | 5 | Contraste real: coreografia EDA vs orquestacion + modular monolith. |
| Complejidad de integracion | 3 | 4 | A tiene mas piezas (bus/colas/consumers); B concentra el core y reduce superficie distribuida. |
| Costo estimado relativo | 3 | 4 | B usa menos infraestructura de mensajeria corporativa; A paga resiliencia con mas servicios. |
| Seguridad | 5 | 4 | Ambas federan identidad; A centraliza mejor gobierno de eventos/APIs en un plano. |
| Observabilidad | 5 | 4 | A traza flujos async end-to-end via bus; B traza workflows + APIs con menos fan-out. |
| Resiliencia en campanas | 5 | 3 | A absorbe picos con colas/backpressure; B depende de throttle/circuit breaker en orquestador. |
| Escalabilidad | 5 | 3 | A escala por dominio; B escala el nucleo completo. |
| Impacto en aplicaciones existentes | 5 | 4 | A evoluciona APP-02 sin mezclar inventario en el mismo deploy; B concentra OMS+Inventario. |
| Riesgo de migracion | 4 | 4 | A migra hacia EDA; B es mas simple al inicio pero implica rework si luego se adopta EDA. |
| Facilidad de MVP con API mock | 4 | 5 | B permite mocks y flujo orden-reserva mas rapido de demostrar. |
| Gobierno FinOps | 4 | 4 | A tiene mas transferencia/eventos; B concentra compute en Azure core. |

## Puntaje

| Alternativa | Puntaje total | Resultado |
|---|---:|---|
| Alternativa A | 68 / 75 | Recomendada |
| Alternativa B | 61 / 75 | Viable como contraste de menor complejidad; no recomendada como primer TO BE |

## Recomendacion

La alternativa recomendada es la **Alternativa A**: Event-Driven Architecture con microservicios, Bus de Eventos Central (PLT-03) en Azure, AWS para ultima milla/evidencias y GCP para analitica/rutas.

Esta decision es la mas consistente con el caso RutaExpress (Cyber Days, WMS degradado, integridad multinube) y con el Hito 1: habilita INI-02 de forma completa, desacopla sistemas criticos y absorbe picos con colas, DLQ, replay y backpressure. La Alternativa B es un contraste arquitectonico valido cuando el comite prioriza time-to-MVP y simplicidad operativa, pero cede resiliencia de campana y madurez event-driven.

## Implicancias para implementacion

- Priorizar MVP sobre Alternativa A: Azure API Management (APP-01), OMS e Inventario en AKS, Azure SQL, Event Hubs/Service Bus, backend movil AWS, S3, DynamoDB y puente hacia GCP.
- Usar Alternativa B solo como escenario de comparacion de comite (estilo orquestado), no como baseline de implementacion.
- Mantener adaptadores transicionales hacia WMS Principal (APP-06), WMS Satelite (APP-07) y ERP Financiero (APP-25).
- Implementar primero los casos criticos de A: orden valida, duplicado/idempotencia, reserva, WMS degradado, DLQ/replay, entrega offline, evidencia corrupta y excepcion de ultima milla.
- Medir desde el inicio: correlation ID, backlog, DLQ, tracking tardio, evidencias pendientes, conflictos de inventario y SLA.
