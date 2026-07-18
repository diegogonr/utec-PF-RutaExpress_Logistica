# Comparativo, ADRs y recomendacion para Comite de Arquitectura

## Objetivo del comparativo

Este documento compara el Modelo A y el Modelo B despues de haberlos presentado como arquitecturas completas e independientes. La comparacion no busca demostrar que una alternativa sea inviable, sino identificar cual es mas conveniente para el primer TO BE/MVP de RutaExpress.

## Resumen de los modelos

| Aspecto | Modelo A | Modelo B |
|---|---|---|
| Tesis | EDA + microservicios con Azure como hub de integracion y gobierno. | Orquestacion + monolito modular para el core orden/inventario. |
| Estilo de coordinacion | Saga coreografiada por eventos (PLT-03). | Saga orquestada (Durable Functions). |
| Empaquetado del core | OMS e Inventario como servicios separados. | OMS + Inventario en un Nucleo Logistico Modular. |
| Integracion principal | API-first + Event-Driven completo. | API-first sincrono; eventos solo como notificacion. |
| Centro de eventos | Bus de Eventos Central (PLT-03) en Azure. | Sin PLT-03 completo; Service Bus topics livianos. |
| OMS / APP-02 | Azure AKS, cercano a APIM y PLT-03. | Azure AKS como nucleo modular + orquestador. |
| Ultima milla | AWS (store-and-forward, evidencias) conectada al hub Azure. | AWS (store-and-forward, evidencias) con confirmacion API al nucleo. |
| Optimizacion y analitica | GCP consume eventos desde Azure. | GCP consume notificaciones/APIs desde Azure. |
| Complejidad dominante | Mas piezas async; mejor absorcion de picos. | Menos piezas; orquestador/nucleo como punto critico. |

## Comparativo visual

### Modelo A - Contenedores C4

![Modelo A - C4 Nivel 2 Contenedores](../diagramas_c4/alternativa_A_n2_contenedores.png)

Lectura ejecutiva:

- OMS, Inventario, API governance, bus de eventos, colas y observabilidad se concentran en Azure.
- AWS queda enfocado en ultima milla y evidencias.
- El bus es el mecanismo de resiliencia y desacoplamiento.

### Modelo B - Contenedores C4

![Modelo B - C4 Nivel 2 Contenedores](../diagramas_c4/imagenes_alternativa_B/alternativa_B_c4_n2_contenedores.png)

Lectura ejecutiva:

- El Nucleo Modular y el Orquestador concentran el flujo orden-reserva.
- No hay hub event-driven corporativo equivalente a PLT-03.
- AWS y GCP mantienen roles especializados; la diferencia es de estilo, no solo de nube.

## Evaluacion por criterios

Escala: 1 = bajo cumplimiento, 5 = alto cumplimiento.

| Criterio | Modelo A: EDA + microservicios | Modelo B: Orquestacion + monolito modular | Lectura para comite |
|---|---:|---:|---|
| Alineamiento con Hito 1 | 5 | 4 | A materializa mejor PLT-03 y desacoplamiento del ADM. |
| Cobertura INI-01 | 5 | 5 | Ambas cubren OMS/inventario con trade-offs distintos de consistencia. |
| Cobertura INI-02 | 5 | 3 | A cubre bus, DLQ, replay y backpressure; B prioriza API-first. |
| Cobertura INI-03 | 5 | 5 | Ambas mantienen AWS para movil y evidencias. |
| Diferenciacion de estilo | 5 | 5 | Contraste real de patrones, no solo de proveedor. |
| Complejidad de integracion | 3 | 4 | B es mas simple; A tiene mas superficie async. |
| Seguridad | 5 | 4 | A centraliza mejor gobierno API+eventos. |
| Observabilidad | 5 | 4 | A traza mejor flujos async; B traza workflows. |
| Resiliencia en campanas | 5 | 3 | A absorbe picos con colas; B depende del orquestador. |
| Escalabilidad | 5 | 3 | A escala por dominio; B escala el nucleo. |
| Impacto en aplicaciones existentes | 5 | 4 | B concentra mas responsabilidad en APP-02. |
| Riesgo de migracion | 4 | 4 | A migra a EDA; B implica rework si luego se adopta EDA. |
| Facilidad de MVP | 4 | 5 | B acelera demo del core orden-reserva. |
| Gobierno FinOps | 4 | 4 | Trade-off distinto: mas eventos vs mas compute concentrado. |

## Puntaje ejecutivo

| Modelo | Puntaje | Resultado |
|---|---:|---|
| Modelo A | 65 / 70 | Recomendado para primer TO BE/MVP |
| Modelo B | 57 / 70 | Viable como contraste de menor complejidad; no recomendado como primer modelo |

## Diferencias clave para decision

| Pregunta de decision | Modelo A | Modelo B |
|---|---|---|
| Cual es el centro de gravedad? | Bus de Eventos Central (PLT-03). | Nucleo modular + orquestador. |
| Como se coordina orden-reserva? | Coreografia por eventos. | Orquestacion por workflow. |
| Como se empaqueta el core? | Microservicios. | Modular monolith. |
| Que pasa si WMS se degrada en campana? | Colas + backpressure absorben. | Throttle/circuit breaker; riesgo de cuello de botella. |
| Que modelo reduce riesgo MVP de campana? | A. | B reduce complejidad, no riesgo de pico. |
| Cuando conviene B? | - | Si el comite prioriza time-to-value y simplicidad del core. |

## ADRs clave que sustentan la recomendacion

| ADR | Decision | Relacion con la recomendacion |
|---|---|---|
| ADR-001 Hub central de eventos | Usar PLT-03 Azure Event Hubs + Service Bus en A. | Descarta B como baseline porque no materializa el hub completo. |
| ADR-002 Estrategia OMS | APP-02 evoluciona a OMS centralizado. | Valido en ambas; en B se amplía a nucleo modular con Inventario. |
| ADR-003 Idempotencia y deduplicacion | Idempotency key + hash logistico. | Critico en A y B. |
| ADR-005 Saga orden-inventario-ERP | En A: coreografia; en B: orquestacion. | A se alinea mejor a resiliencia distribuida del caso. |
| ADR-006 Store-and-forward movil | Offline-first en AWS. | Comun a ambos modelos. |
| ADR-008 DLQ y replay | Obligatorio en A. | En B se sustituye parcialmente por reproceso de comandos. |
| ADR-009 Backpressure y circuit breaker | Proteccion ante degradacion WMS/ERP. | A lo combina con colas; B depende mas del orquestador. |

## Recomendacion

Se recomienda aprobar el **Modelo A - EDA + microservicios con Azure como hub** como arquitectura base del primer TO BE/MVP.

Justificacion:

- Responde mejor a Cyber Days, colas y degradacion WMS del caso.
- Cubre INI-02 de forma completa (contratos, eventos, DLQ, replay, backpressure).
- Desacopla sistemas criticos y facilita trazabilidad multinube.
- Conserva AWS para ultima milla y GCP para analitica.
- El Modelo B se mantiene como alternativa de contraste: valida el trade-off simplicidad vs resiliencia distribuida.

## Cuando elegir el Modelo B

El Modelo B podria preferirse si:

- El comite prioriza time-to-MVP y menor superficie operativa.
- El dolor inmediato esta en ordenes/inventario locales, no en fan-out event-driven.
- Se acepta cobertura parcial de capacidades PLT-03 en la primera ola.
- Existe un plan explicito para evolucionar luego a EDA sin rehacer el dominio.

## Decision solicitada al comite

| Punto | Decision propuesta |
|---|---|
| Modelo base TO BE/MVP | Aprobar Modelo A. |
| Modelo alternativo | Mantener Modelo B como contraste de estilo (orquestacion + monolito modular). |
| OMS | Confirmar evolucion de APP-02 a OMS (servicio en A; nucleo modular en B). |
| Bus de Eventos Central (PLT-03) | Confirmar hub Azure en el MVP (Modelo A). |
| Ultima milla | Confirmar AWS para APP-15/APP-16. |
| Controles minimos | Idempotencia, observabilidad, seguridad federada, store-and-forward e IaC desde el inicio. |

## Cierre para presentacion

> "Ambos modelos cubren INI-01, INI-02 e INI-03, pero no son la misma arquitectura con distinto proveedor. El Modelo A es event-driven y desacoplado; el Modelo B es orquestado y modular-monolitico. Para RutaExpress, el Modelo A reduce el riesgo del primer TO BE porque absorbe mejor picos e integridad distribuida. El Modelo B es util para discutir simplicidad y time-to-MVP, no como baseline por defecto."
