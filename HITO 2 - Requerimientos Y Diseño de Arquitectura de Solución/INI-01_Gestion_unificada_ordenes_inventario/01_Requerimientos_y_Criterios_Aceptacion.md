# Requerimientos Funcionales / No Funcionales y Criterios de Aceptacion
## RutaExpress Fulfillment & Transporte - Hito 2

> **Fuente:** `requerimientos.md` y `criterios_aceptacion_gherkin.md`.
> **Iniciativa:** **INI-01** - Gestion unificada de ordenes e inventario end-to-end.
> **Convencion:** nombres oficiales de aplicaciones y plataformas del Hito 1 cuando aplican.
> **Nota de alcance:** este consolidado no incluye bloques Gherkin completos de historias de usuario. Los escenarios completos permanecen en `criterios_aceptacion_gherkin.md` y `historias_gherkin/`.

---

## 1. Proposito

Definir los requerimientos para que Orquestador de Pedidos (APP-02) evolucione a un OMS centralizado, capaz de gobernar el ciclo de vida de la orden, validar pedidos, asegurar idempotencia, coordinar reservas/liberaciones y mantener una vista unica de inventario junto con WMS Cloud, TMS (Transportation Management) (APP-11) y ERP Financiero (On Premises) (APP-25).

---

## 2. Alineamiento con casuistica y lineamientos

| Fuente | Elemento considerado | Implicancia para los requerimientos |
|---|---|---|
| Caso 6a - Fase 1 | 68,000 ordenes diarias, 180,000 en campana, 6% con defectos y lote duplicado de 32,000 pedidos | Validacion, deduplicacion, idempotencia y control de ingreso son capacidades obligatorias del OMS centralizado / Orquestador de Pedidos (APP-02) |
| Caso 6a - Fase 2 | 210,000 movimientos de inventario diarios, 2.8% con ajuste, 4,900 conflictos al reconectar y 18,000 pedidos retrasados | Vista unificada de inventario y conciliacion automatica son requerimientos core |
| Caso 6b - Riesgo 1 | Degradacion de WMS Principal (On Premises) (APP-06) genero colas, rutas incompletas, tracking incierto y penalidades | El OMS centralizado / Orquestador de Pedidos (APP-02) no debe confirmar estados sin respuesta consistente de inventario y debe operar con backpressure/eventos |
| Caso 6b - Riesgo 2 | Duplicados provocan doble reserva, rutas fantasma y estados inconsistentes | Los criterios de aceptacion deben verificar que no existan dobles reservas ni efectos duplicados |
| Enunciado Hito 2 | RF/RNF y criterios de aceptacion para iniciativas del ADM F | El documento separa RF, RNF y escenarios Gherkin, y prepara insumos para diseno TO BE multinube |

---

## 3. Alcance funcional

- Gestion centralizada del ciclo de vida de la orden.
- Validacion de direccion, SKU, cliente, SLA, ventana horaria y reglas comerciales.
- Deduplicacion e idempotencia por hash de contenido y clave externa.
- Vista unificada de inventario por SKU, almacen, ubicacion, lote y estado.
- Reserva, liberacion y movimiento de inventario coordinados con WMS Cloud.
- Conciliacion de conflictos entre WMS Cloud, almacenes locales y ERP Financiero (On Premises) (APP-25).

---

## 4. Requerimientos funcionales y no funcionales

| ID | Tipo | Descripcion | Criterio de aceptacion |
| --- | --- | --- | --- |
| RF-01 | Funcional | El OMS centralizado / Orquestador de Pedidos (APP-02) debe registrar toda orden recibida desde API, portal o carga masiva con un identificador interno unico. | Toda orden aceptada queda registrada con ID interno, canal de origen, cliente, timestamp y estado inicial "Recibida". |
| RF-02 | Funcional | El OMS centralizado / Orquestador de Pedidos (APP-02) debe validar campos obligatorios, direccion, SKU, cliente, promesa SLA y ventana horaria antes de aceptar la orden. | Una orden con datos invalidos queda en estado "Rechazada" o "Pendiente de correccion" y no reserva inventario. |
| RF-03 | Funcional | El OMS centralizado / Orquestador de Pedidos (APP-02) debe aplicar deduplicacion por hash de contenido, identificador externo, cliente, destinatario y ventana temporal configurable. | Una orden duplicada no se procesa dos veces y devuelve la referencia de la orden original. |
| RF-04 | Funcional | El OMS centralizado / Orquestador de Pedidos (APP-02) debe garantizar idempotencia en reintentos de creacion, actualizacion, reserva y cancelacion. | Reenviar la misma solicitud no genera doble orden, doble reserva ni doble movimiento. |
| RF-05 | Funcional | El OMS centralizado / Orquestador de Pedidos (APP-02) debe mantener el estado canonico de la orden durante todo su ciclo de vida. | Los estados publicados son consistentes entre OMS centralizado / Orquestador de Pedidos (APP-02), WMS Cloud, TMS (Transportation Management) (APP-11), portal y ERP Financiero (On Premises) (APP-25). |
| RF-06 | Funcional | El OMS centralizado / Orquestador de Pedidos (APP-02) debe consultar disponibilidad de inventario por SKU, almacen, ubicacion, lote y estado antes de confirmar reserva. | La reserva solo se confirma si existe stock disponible y elegible para la orden. |
| RF-07 | Funcional | El OMS centralizado / Orquestador de Pedidos (APP-02) debe registrar reservas, liberaciones, cancelaciones y movimientos de inventario como eventos auditables. | Cada cambio de inventario tiene orden asociada, usuario/sistema, timestamp, motivo y correlation ID. |
| RF-08 | Funcional | El OMS centralizado / Orquestador de Pedidos (APP-02) debe coordinar con WMS Cloud la reserva fisica del inventario y con ERP Financiero (On Premises) (APP-25) el inventario valorizado. | Una reserva confirmada por WMS Cloud queda disponible para ERP Financiero (On Premises) (APP-25) mediante API o evento. |
| RF-09 | Funcional | El sistema debe reconciliar conflictos de inventario entre WMS Cloud y almacenes locales. | Todo conflicto queda clasificado, priorizado y resuelto automaticamente o derivado a operador con trazabilidad. |
| RF-10 | Funcional | El OMS centralizado / Orquestador de Pedidos (APP-02) debe exponer APIs de consulta de orden e inventario para TMS (Transportation Management) (APP-11), portal B2B y liquidacion. | Los consumidores autorizados pueden consultar estado de orden, reserva e inventario disponible con contratos versionados. |
| RF-11 | Funcional | El OMS centralizado / Orquestador de Pedidos (APP-02) debe soportar priorizacion por SLA y canal durante campanas. | Ordenes criticas se procesan con prioridad configurable sin bloquear el flujo regular. |
| RF-12 | Funcional | El OMS centralizado / Orquestador de Pedidos (APP-02) debe conservar compatibilidad transicional con WMS Principal (On Premises) (APP-06) mientras WMS Cloud no este completamente desplegado. | Durante la transicion, las reservas via WMS Principal (On Premises) (APP-06) se publican con el mismo modelo canonico y correlation ID. |
| RNF-01 | No funcional | Disponibilidad del OMS centralizado / Orquestador de Pedidos (APP-02) de al menos 99.9% en ventanas criticas de campana. | Monitoreo mensual evidencia disponibilidad igual o superior al objetivo, excluyendo ventanas aprobadas de mantenimiento. |
| RNF-02 | No funcional | Tiempo de respuesta para validacion sin reserva menor a 500 ms p95. | Pruebas de rendimiento validan p95 menor a 500 ms para volumen nominal. |
| RNF-03 | No funcional | Tiempo de respuesta para reserva de inventario menor a 2 segundos p95. | Pruebas integradas OMS centralizado / Orquestador de Pedidos (APP-02)-WMS Cloud validan p95 menor a 2 segundos. |
| RNF-04 | No funcional | Escalabilidad para soportar picos de 3x sobre volumen promedio del caso. | Pruebas de carga demuestran procesamiento de hasta 180,000 ordenes por dia y 210,000 movimientos de inventario diarios sin perdida de eventos. |
| RNF-05 | No funcional | Trazabilidad end-to-end con correlation ID obligatorio. | Toda orden, reserva, liberacion y movimiento puede rastrearse en logs, metricas y eventos. |
| RNF-06 | No funcional | Seguridad por minimo privilegio y cifrado en transito y reposo. | APIs usan autenticacion/autorizacion, TLS y secretos gestionados centralmente. |
| RNF-07 | No funcional | Recuperabilidad ante fallas de integracion. | Reintentos, colas y eventos pendientes permiten recuperar procesamiento sin inconsistencias. |
| RNF-08 | No funcional | Auditoria completa para orden e inventario segun politica contractual y regulatoria de RutaExpress. | Las consultas historicas muestran cambios, responsables y motivos sin alteracion manual no auditada. |
| RNF-09 | No funcional | Consistencia eventual controlada entre OMS centralizado / Orquestador de Pedidos (APP-02), WMS Cloud, TMS (Transportation Management) (APP-11) y ERP Financiero (On Premises) (APP-25). | Las diferencias entre sistemas quedan visibles, con estado de sincronizacion y mecanismo de compensacion. |

---

## 5. Historias de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
| --- | --- | --- | --- | --- | --- |
| HU-INI01-RF01 | Logistica | operador de recepcion B2B | que el OMS centralizado / Orquestador de Pedidos (APP-02) registre toda orden recibida desde API, portal o carga masiva con un identificador interno unico | asegurar trazabilidad desde el ingreso | RF-01 |
| HU-INI01-RF02 | Logistica | analista de mesa B2B | que el OMS centralizado / Orquestador de Pedidos (APP-02) valide campos obligatorios, direccion, SKU, cliente, promesa SLA y ventana horaria antes de aceptar la orden | evitar errores que impacten almacen, ruta y entrega | RF-02 |
| HU-INI01-RF03 | Logistica | responsable de integracion | que el OMS centralizado / Orquestador de Pedidos (APP-02) aplique deduplicacion por hash de contenido, identificador externo, cliente, destinatario y ventana temporal configurable | evitar doble procesamiento por reintentos de clientes | RF-03 |
| HU-INI01-RF04 | Logistica | cliente integrador | que los reintentos de creacion, actualizacion, reserva y cancelacion sean idempotentes | que errores temporales no generen doble orden, doble reserva ni doble movimiento | RF-04 |
| HU-INI01-RF05 | Logistica | operador logistico | que el OMS centralizado / Orquestador de Pedidos (APP-02) mantenga el estado canonico de la orden durante todo su ciclo de vida | que OMS centralizado / Orquestador de Pedidos (APP-02), WMS Principal (On Premises) (APP-06), TMS (Transportation Management) (APP-11), portal y ERP Financiero (On Premises) (APP-25) consulten la misma verdad operativa | RF-05 |
| HU-INI01-RF06 | Logistica | planificador de almacen | que el OMS centralizado / Orquestador de Pedidos (APP-02) consulte disponibilidad por SKU, almacen, ubicacion, lote y estado antes de confirmar reserva | asegurar que solo se comprometa stock elegible | RF-06 |
| HU-INI01-RF07 | Logistica | auditor operativo | que reservas, liberaciones, cancelaciones y movimientos de inventario queden como eventos auditables | reconstruir cada cambio con responsable, motivo y correlation ID | RF-07 |
| HU-INI01-RF08 | Logistica | responsable de operaciones y finanzas | que el OMS centralizado / Orquestador de Pedidos (APP-02) coordine con WMS Cloud la reserva fisica y con ERP Financiero (APP-25) el inventario valorizado | que la operacion y la liquidacion usen datos consistentes | RF-08 |
| HU-INI01-RF09 | Logistica | jefe de inventario | reconciliar conflictos entre WMS Cloud y almacenes locales | evitar liberar pedidos con inventario dudoso y reducir retrasos operativos | RF-09 |
| HU-INI01-RF10 | Logistica | consumidor autorizado de TMS (Transportation Management) (APP-11), portal B2B o liquidacion | consultar estado de orden, reserva e inventario disponible mediante APIs versionadas | operar con informacion confiable | RF-10 |
| HU-INI01-RF11 | Logistica | planner de campana | que el OMS centralizado / Orquestador de Pedidos (APP-02) priorice ordenes por SLA y canal durante picos | procesar ordenes criticas sin bloquear el flujo regular | RF-11 |
| HU-INI01-RF12 | Logistica | arquitecto de transicion | conservar compatibilidad con WMS Principal (On Premises) (APP-06) mientras WMS Cloud no este completamente desplegado | no interrumpir la operacion de almacenes | RF-12 |

---

## 6. Matriz de escenarios de aceptacion sin Gherkin

| Codigo | Historia | Tipo | Escenario |
| --- | --- | --- | --- |
| ESC-INI01-RF01-P01 | HU-INI01-RF01 | positivo | Registrar orden valida desde API |
| ESC-INI01-RF01-N01 | HU-INI01-RF01 | negativo | Rechazar registro sin cliente |
| ESC-INI01-RF02-P01 | HU-INI01-RF02 | positivo | Validar orden completa |
| ESC-INI01-RF02-N01 | HU-INI01-RF02 | negativo | Marcar orden pendiente por direccion incompleta |
| ESC-INI01-RF03-P01 | HU-INI01-RF03 | positivo | Detectar duplicado con identificador externo diferente |
| ESC-INI01-RF03-N01 | HU-INI01-RF03 | negativo | No marcar como duplicada una orden similar fuera de ventana |
| ESC-INI01-RF04-P01 | HU-INI01-RF04 | positivo | Reintentar creacion con la misma clave idempotente |
| ESC-INI01-RF04-N01 | HU-INI01-RF04 | negativo | Rechazar reuso de clave idempotente con payload distinto |
| ESC-INI01-RF05-P01 | HU-INI01-RF05 | positivo | Publicar cambio de estado canonico |
| ESC-INI01-RF05-N01 | HU-INI01-RF05 | negativo | Bloquear transicion invalida de estado |
| ESC-INI01-RF06-P01 | HU-INI01-RF06 | positivo | Confirmar disponibilidad elegible |
| ESC-INI01-RF06-N01 | HU-INI01-RF06 | negativo | Bloquear reserva con inventario no elegible |
| ESC-INI01-RF07-P01 | HU-INI01-RF07 | positivo | Registrar reserva como evento auditable |
| ESC-INI01-RF07-N01 | HU-INI01-RF07 | negativo | Rechazar movimiento sin motivo |
| ESC-INI01-RF08-P01 | HU-INI01-RF08 | positivo | Notificar reserva confirmada al ERP Financiero (On Premises) (APP-25) |
| ESC-INI01-RF08-N01 | HU-INI01-RF08 | negativo | No notificar valorizacion sin reserva fisica |
| ESC-INI01-RF09-P01 | HU-INI01-RF09 | positivo | Resolver conflicto por regla automatica |
| ESC-INI01-RF09-N01 | HU-INI01-RF09 | negativo | Derivar conflicto severo a operador |
| ESC-INI01-RF10-P01 | HU-INI01-RF10 | positivo | Consultar estado de orden con autorizacion |
| ESC-INI01-RF10-N01 | HU-INI01-RF10 | negativo | Rechazar consulta no autorizada |
| ESC-INI01-RF11-P01 | HU-INI01-RF11 | positivo | Procesar orden express con prioridad alta |
| ESC-INI01-RF11-N01 | HU-INI01-RF11 | negativo | Evitar starvation de ordenes regulares |
| ESC-INI01-RF12-P01 | HU-INI01-RF12 | positivo | Procesar reserva mediante WMS Principal |
| ESC-INI01-RF12-N01 | HU-INI01-RF12 | negativo | Activar backpressure por degradacion de WMS Principal |

---

## 7. Trazabilidad

| Iniciativa | Historias | RF | RNF | Escenarios referenciados |
| --- | --- | --- | --- | --- |
| INI-01 | 12 | 12 | 9 | 24 |

---

*Documento consolidado para el Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC.*
*Fecha: Julio 2026.*
