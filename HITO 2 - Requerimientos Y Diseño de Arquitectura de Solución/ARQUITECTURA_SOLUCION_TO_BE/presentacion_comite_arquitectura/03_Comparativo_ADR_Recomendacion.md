# Comparativo, ADRs y recomendacion para Comite de Arquitectura

## Objetivo del comparativo

Este documento compara el Modelo A y el Modelo B despues de haberlos presentado como arquitecturas completas e independientes. La comparacion no busca demostrar que una alternativa sea inviable, sino identificar cual es mas conveniente para el primer TO BE/MVP de RutaExpress.

## Resumen de los modelos

| Aspecto | Modelo A | Modelo B |
|---|---|---|
| Tesis | Hub Azure: microservicios + PLT-03 (outbox → `bus-workers` → Event Hubs → Service Bus). | Orquestacion + monolito modular para el core orden/inventario. |
| Estilo de coordinacion (orden-reserva) | Saga orquestada por **OMS vía HTTP** (Inventario) y APIM (WMS). | Saga orquestada por **Durable Functions**. |
| Rol de los eventos | EDA canónica vía PLT-03 para fan-out, DLQ, replay y backpressure. | Eventos solo como **notificacion** selectiva (sin hub completo). |
| Empaquetado del core | OMS (APP-02) e Inventario (MS-INI01-02) como servicios separados en AKS. | OMS + Inventario en un Nucleo Logistico Modular (un deploy). |
| Integracion principal | API-first (APIM) + EDA completa en el bus. | API-first sincrono en el nucleo; notificaciones livianas. |
| Centro de eventos | Bus de Eventos Central (PLT-03) en Azure. | Sin PLT-03 completo; Service Bus topics livianos. |
| OMS / APP-02 | Azure AKS, cercano a APIM y PLT-03; escribe outbox. | Azure AKS como nucleo modular + orquestador de workflow. |
| Ultima milla | AWS: `mobile-api` → SQS → `retry-worker` → EventBridge → Adaptador → Event Hubs. | AWS (store-and-forward, evidencias) con confirmacion API al nucleo. |
| Optimizacion y analitica | GCP consume desde Event Hubs / Service Bus. | GCP consume notificaciones/APIs desde Azure. |
| Complejidad dominante | Mas piezas async; mejor absorcion de picos. | Menos piezas; orquestador/nucleo como punto critico. |

## Evaluacion por criterios

Escala: 1 = bajo cumplimiento, 5 = alto cumplimiento.

| Criterio | Modelo A | Modelo B | Lectura para comite |
|---|---:|---:|---|
| Alineamiento con Hito 1 | 5 | 4 | A materializa mejor PLT-03 y desacoplamiento del ADM. |
| Cobertura INI-01 | 5 | 5 | Ambas cubren OMS/inventario; A separa servicios, B concentra en un deploy. |
| Cobertura INI-02 | 5 | 3 | A cubre bus, DLQ, replay y backpressure; B prioriza API-first + notificaciones. |
| Cobertura INI-03 | 5 | 5 | Ambas mantienen AWS para movil y evidencias. |
| Diferenciacion de estilo | 5 | 5 | Contraste real: microservicios + PLT-03 vs monolito + Durable Functions. |
| Complejidad de integracion | 3 | 4 | B es mas simple; A tiene mas superficie async (`bus-workers`, hubs, colas). |
| Seguridad | 5 | 4 | A centraliza mejor gobierno API+eventos. |
| Observabilidad | 5 | 4 | A traza mejor flujos async; B traza workflows. |
| Resiliencia en campanas | 5 | 3 | A absorbe picos con colas; B depende del orquestador. |
| Escalabilidad | 5 | 3 | A escala por dominio; B escala el nucleo. |
| Impacto en aplicaciones existentes | 5 | 4 | B concentra mas responsabilidad en APP-02. |
| Riesgo de migracion | 4 | 4 | A adopta EDA/PLT-03 desde el diseño; B implica rework si luego se adopta el hub. |
| Facilidad de MVP | 4 | 5 | B acelera demo del core orden-reserva. |
| Gobierno FinOps | 4 | 4 | Trade-off: mas eventos/transferencia vs compute concentrado. |

## Puntaje ejecutivo

| Modelo | Puntaje | Resultado |
|---|---:|---|
| Modelo A | 65 / 70 | Recomendado para primer TO BE/MVP |
| Modelo B | 57 / 70 | Viable como contraste de menor complejidad; no recomendado como primer modelo |

## Diferencias clave para decision

| Pregunta de decision | Modelo A | Modelo B |
|---|---|---|
| Cual es el centro de gravedad? | Bus de Eventos Central (PLT-03) + hub Azure. | Nucleo modular + orquestador Durable Functions. |
| Como se coordina orden-reserva? | OMS orquesta por **HTTP** (Inventario) y APIM (WMS). | Workflow orquesta pasos y compensaciones. |
| Como se empaqueta el core? | Microservicios (OMS ≠ Inventario). | Modular monolith. |
| Que hace el bus de eventos? | Publica outbox canónico, fan-out, DLQ, replay. | Notificaciones selectivas; no gobierna el estado core. |
| Que pasa si WMS se degrada en campana? | Circuit breaker en OMS/APIM + colas/backpressure en PLT-03. | Throttle/circuit breaker; riesgo de cuello de botella en el orquestador. |
| Que modelo reduce riesgo MVP de campana? | A. | B reduce complejidad, no riesgo de pico. |
| Cuando conviene B? | - | Si el comite prioriza time-to-value y simplicidad del core. |

## ADRs clave que sustentan la recomendacion

| ADR | Decision | Relacion con la recomendacion |
|---|---|---|
| ADR-001 Hub central de eventos | Usar PLT-03 Azure: Event Hubs + Service Bus + `bus-workers` (outbox) en A. | Descarta B como baseline porque no materializa el hub completo. |
| ADR-002 Estrategia OMS | APP-02 evoluciona a OMS centralizado. | Valido en ambas; en B se amplía a nucleo modular con Inventario. |
| ADR-003 Idempotencia y deduplicacion | Idempotency key + hash logistico. | Critico en A y B. |
| ADR-005 Saga orden-inventario-WMS | En A: orquestacion por OMS (HTTP/APIM); en B: Durable Functions. | Ambas orquestan; A combina eso con EDA/PLT-03 para fan-out y resiliencia. |
| ADR-006 Store-and-forward movil | Offline-first en AWS (`mobile-api` / `retry-worker` en A). | Comun a ambos modelos. |
| ADR-008 DLQ y replay | Obligatorio en A (Service Bus). | En B se sustituye parcialmente por reproceso de comandos. |
| ADR-009 Backpressure y circuit breaker | Proteccion ante degradacion WMS/ERP. | A lo combina con colas; B depende mas del orquestador. |

## Comparativo visual

### Modelo A - Contenedores C4

![Modelo A - C4 Nivel 2 Contenedores](../diagramas_c4/alternativa_A_n2_contenedores.png)

Lectura ejecutiva:

- OMS, Inventario, API governance, outbox/`bus-workers`, Event Hubs, Service Bus y observabilidad se concentran en Azure.
- AWS queda enfocado en ultima milla y evidencias, con puente nombrado hasta Event Hubs.
- El bus PLT-03 es el mecanismo de resiliencia y desacoplamiento **downstream**; la Saga del core es HTTP desde OMS.

### Modelo B - Contenedores C4

![Modelo B - C4 Nivel 2 Contenedores](../diagramas_c4/imagenes_alternativa_B/alternativa_B_c4_n2_contenedores.png)

Lectura ejecutiva:

- El Nucleo Modular y el Orquestador (Durable Functions) concentran el flujo orden-reserva.
- No hay hub event-driven corporativo equivalente a PLT-03.
- AWS y GCP mantienen roles especializados; la diferencia es de estilo, no solo de nube.


## Recomendacion

Se recomienda aprobar el **Modelo A - hub Azure + microservicios + PLT-03** como arquitectura base del primer TO BE/MVP.

Justificacion:

- Responde mejor a Cyber Days, colas y degradacion WMS del caso.
- Cubre INI-02 de forma completa (contratos, outbox, Event Hubs, Service Bus, DLQ, replay, backpressure).
- Desacopla OMS e Inventario y facilita trazabilidad multinube.
- Conserva AWS para ultima milla y GCP para analitica.
- El Modelo B se mantiene como alternativa de contraste: valida el trade-off simplicidad (monolito + Durable Functions) vs resiliencia del hub event-driven.

## Cuando elegir el Modelo B

El Modelo B podria preferirse si:

- El comite prioriza time-to-MVP y menor superficie operativa.
- El dolor inmediato esta en ordenes/inventario locales, no en fan-out event-driven.
- Se acepta cobertura parcial de capacidades PLT-03 en la primera ola.
- Existe un plan explicito para evolucionar luego a EDA/PLT-03 sin rehacer el dominio.

## Decision solicitada al comite

| Punto | Decision propuesta |
|---|---|
| Modelo base TO BE/MVP | Aprobar Modelo A. |
| Modelo alternativo | Mantener Modelo B como contraste de estilo (orquestacion Durable Functions + monolito modular). |
| OMS | Confirmar evolucion de APP-02 a OMS (servicio en A; nucleo modular en B). |
| Bus de Eventos Central (PLT-03) | Confirmar hub Azure en el MVP (Modelo A): outbox → `bus-workers` → Event Hubs → Service Bus. |
| Ultima milla | Confirmar AWS para APP-15/APP-16. |
| Controles minimos | Idempotencia, observabilidad, seguridad federada, store-and-forward e IaC desde el inicio. |

## Cierre para presentacion

> "Ambos modelos cubren INI-01, INI-02 e INI-03, pero no son la misma arquitectura. El Modelo A separa OMS e Inventario, orquesta la Saga por HTTP y usa PLT-03 para eventos canonicos, DLQ y replay. El Modelo B concentra el core en un monolito modular y orquesta con Durable Functions, usando eventos solo como notificacion. Para RutaExpress, el Modelo A reduce el riesgo del primer TO BE porque absorbe mejor picos e integridad distribuida. El Modelo B es util para discutir simplicidad y time-to-MVP, no como baseline por defecto."
