# Requerimientos Funcionales / No Funcionales y Criterios de Aceptacion
## RutaExpress Fulfillment & Transporte - Hito 2

> **Fuente:** `requerimientos.md` y `criterios_aceptacion_gherkin.md`.
> **Iniciativa:** **INI-02** - Integracion API-First y Event-Driven.
> **Convencion:** nombres oficiales de aplicaciones y plataformas del Hito 1 cuando aplican.
> **Nota de alcance:** este consolidado no incluye bloques Gherkin completos de historias de usuario. Los escenarios completos permanecen en `criterios_aceptacion_gherkin.md` y `historias_gherkin/`.

---

## 1. Proposito

Definir los requerimientos para implementar una capa de integracion API-first y event-driven que reemplace progresivamente integraciones punto a punto entre OMS, WMS Cloud, TMS (Transportation Management) (APP-11), App de Conductores (APP-15), ERP Financiero (On Premises) (APP-25), portales y analitica.

---

## 2. Alineamiento con casuistica y lineamientos

| Fuente | Elemento considerado | Implicancia para los requerimientos |
|---|---|---|
| Caso 6a - Contexto | Arquitectura fragmentada: WMS on premises, TMS Azure, app AWS/DynamoDB, optimizador GCP, portales SaaS e integraciones punto a punto | Se requiere una plataforma API-first y event-driven que conecte sistemas multinube |
| Caso 6a - Cyber Days | 240,000 pedidos en cola, WMS degradado, TMS con ordenes incompletas y rutas con paquetes faltantes | Backpressure, priorizacion, colas y reintentos son requisitos funcionales obligatorios |
| Caso 6a - Objetivos | 99.9% disponibilidad, 98% tracking confiable y reduccion del ciclo orden-despacho de 9.5h a 4h | Los RNF incluyen disponibilidad, observabilidad y escalabilidad |
| Caso 6b - Riesgos 1 y 2 | Disponibilidad e integridad afectadas por mensajes fuera de orden, duplicados o perdidos | Se agregan validacion de contratos, secuenciacion por agregado, replay y DLQ |
| Enunciado Hito 2 | Base para diseno TO BE con integracion, seguridad, observabilidad y patrones como EDA, resiliencia e IaC | Los requerimientos habilitan arquitectura multinube y patrones para siguientes entregables |

---

## 3. Alcance funcional

- Gobierno central de APIs con contratos versionados.
- Bus de Eventos Central (PLT-03) para eventos operativos y financieros.
- Publicacion, suscripcion, reintentos, priorizacion, backpressure y dead-letter queues.
- Modelo canonico de eventos y datos.
- Observabilidad tecnica de colas, APIs y eventos.
- Migracion progresiva desde integraciones punto a punto.

---

## 4. Requerimientos funcionales y no funcionales

| ID | Tipo | Descripcion | Criterio de aceptacion |
| --- | --- | --- | --- |
| RF-01 | Funcional | La plataforma debe registrar y publicar contratos de APIs para los dominios de orden, inventario, ruta, tracking, excepcion y liquidacion. | Todo contrato tiene version, responsable, ambiente, esquema, politica de seguridad y consumidores autorizados. |
| RF-02 | Funcional | Azure API Management (APP-01) debe aplicar autenticacion, autorizacion, cuotas, rate limiting y politicas por cliente o consumidor. | Una solicitud sin credenciales o fuera de cuota es rechazada con codigo y mensaje estandar. |
| RF-03 | Funcional | Bus de Eventos Central (PLT-03) debe permitir publicar eventos canonicos desde OMS, WMS Cloud, TMS, App de Conductores (APP-15) y ERP. | Cada productor puede publicar eventos validos contra esquema y con correlation ID obligatorio. |
| RF-04 | Funcional | La plataforma debe validar esquemas de eventos antes de aceptarlos. | Un evento con esquema invalido se rechaza o envia a cola de errores con motivo registrado. |
| RF-05 | Funcional | La plataforma debe soportar reintentos automaticos con politica configurable por tipo de evento. | Un consumidor temporalmente no disponible recibe el evento al recuperarse o tras reintentos programados. |
| RF-06 | Funcional | La plataforma debe soportar dead-letter queues para mensajes fallidos. | Todo mensaje que supera reintentos queda en DLQ con payload, error, timestamp y responsable de remediacion. |
| RF-07 | Funcional | La plataforma debe aplicar backpressure para proteger sistemas degradados. | Si WMS Principal (On Premises) (APP-06) durante la transicion, WMS Cloud en TO BE o ERP degradan, los mensajes se regulan sin perder orden ni saturar el destino. |
| RF-08 | Funcional | La plataforma debe priorizar eventos por criticidad y SLA. | Eventos criticos como reserva, entrega y liquidacion se procesan antes que eventos informativos. |
| RF-09 | Funcional | La plataforma debe habilitar replay controlado de eventos. | Un usuario autorizado puede reprocesar eventos por rango, tipo y correlation ID sin duplicar efectos de negocio. |
| RF-10 | Funcional | La plataforma debe exponer tableros de salud de APIs, colas y eventos. | Operacion visualiza latencia, errores, mensajes pendientes, DLQ y throughput por dominio. |
| RF-11 | Funcional | La plataforma debe conservar secuencia logica por agregado de negocio, como orden, ruta, paquete o liquidacion. | Eventos fuera de orden se retienen, reordenan o marcan para remediacion antes de afectar estados visibles al cliente. |
| RF-12 | Funcional | La plataforma debe soportar convivencia transicional entre integraciones punto a punto y flujos event-driven. | Cada integracion migrada tiene adaptador, contrato, monitoreo y plan de rollback documentado. |
| RNF-01 | No funcional | Disponibilidad de la capa de integracion de al menos 99.9%. | Monitoreo mensual evidencia cumplimiento del objetivo. |
| RNF-02 | No funcional | Latencia de publicacion de eventos menor a 1 segundo p95 para eventos criticos. | Pruebas de rendimiento validan p95 menor a 1 segundo en volumen nominal. |
| RNF-03 | No funcional | Durabilidad de mensajes criticos. | Ningun evento aceptado se pierde ante falla de consumidor o reinicio de plataforma. |
| RNF-04 | No funcional | Seguridad de APIs y eventos con cifrado en transito y control de acceso. | Todo endpoint usa TLS, autenticacion y autorizacion por rol/cliente. |
| RNF-05 | No funcional | Compatibilidad hacia atras por al menos dos versiones de contrato activas. | Consumidores existentes siguen operando durante la ventana de migracion definida. |
| RNF-06 | No funcional | Observabilidad con correlation ID en el 100% de eventos y solicitudes. | Trazas permiten reconstruir el flujo completo de una orden o entrega. |
| RNF-07 | No funcional | Escalabilidad elastica para picos de campana. | La plataforma procesa 180,000 ordenes diarias y mas de 130,000 eventos de tracking en campana sin perdida de mensajes ni degradacion critica. |
| RNF-08 | No funcional | Gobernanza de cambios. | Ningun contrato productivo se modifica sin aprobacion, versionado y pruebas de contrato. |
| RNF-09 | No funcional | Portabilidad de lineamientos para diseno de solucion. | Los contratos, eventos y politicas pueden representarse en C4 y ADR para las alternativas de solucion del Hito 2. |

---

## 5. Historias de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
| --- | --- | --- | --- | --- | --- |
| HU-INI02-RF01 | Logistica | arquitecto de integracion | registrar y publicar contratos de APIs para orden, inventario, ruta, tracking, excepcion y liquidacion | gobernar consumidores, versiones y esquemas | RF-01 |
| HU-INI02-RF02 | Logistica | administrador de APIs | que Azure API Management (APP-01) aplique autenticacion, autorizacion, cuotas y rate limiting | proteger servicios backend y contratos por cliente | RF-02 |
| HU-INI02-RF03 | Logistica | productor de eventos | publicar eventos canonicos desde OMS, WMS Cloud, TMS, App de Conductores y ERP | desacoplar consumidores y mantener trazabilidad | RF-03 |
| HU-INI02-RF04 | Logistica | responsable de calidad de integracion | validar esquemas de eventos antes de aceptarlos | evitar datos incompletos o incompatibles en consumidores | RF-04 |
| HU-INI02-RF05 | Logistica | operador de integracion | reintentos automaticos con politica configurable por tipo de evento | recuperar consumidores temporalmente no disponibles | RF-05 |
| HU-INI02-RF06 | Logistica | equipo de soporte | que los mensajes fallidos lleguen a DLQ con payload, error, timestamp y responsable | remediar fallas persistentes sin perder informacion | RF-06 |
| HU-INI02-RF07 | Logistica | administrador de plataforma | aplicar backpressure para proteger WMS, ERP u otros destinos degradados | no saturar sistemas criticos ni perder orden | RF-07 |
| HU-INI02-RF08 | Logistica | operador de campana | priorizar eventos por criticidad y SLA | que reservas, entregas y liquidacion se atiendan antes que eventos informativos | RF-08 |
| HU-INI02-RF09 | Logistica | operador autorizado | reprocesar eventos por rango, tipo y correlation ID sin duplicar efectos de negocio | recuperar consumidores o reconstruir historial | RF-09 |
| HU-INI02-RF10 | Logistica | equipo de operaciones | tableros de salud de APIs, colas y eventos | monitorear latencia, errores, pendientes, DLQ y throughput por dominio | RF-10 |
| HU-INI02-RF11 | Logistica | responsable de integridad | conservar secuencia logica por orden, ruta, paquete o liquidacion | evitar estados visibles inconsistentes | RF-11 |
| HU-INI02-RF12 | Logistica | arquitecto de migracion | soportar convivencia transicional entre integraciones punto a punto y flujos event-driven | migrar sin romper la operacion | RF-12 |

---

## 6. Matriz de escenarios de aceptacion sin Gherkin

| Codigo | Historia | Tipo | Escenario |
| --- | --- | --- | --- |
| ESC-INI02-RF01-P01 | HU-INI02-RF01 | positivo | Publicar contrato valido |
| ESC-INI02-RF01-N01 | HU-INI02-RF01 | negativo | Rechazar contrato sin version |
| ESC-INI02-RF02-P01 | HU-INI02-RF02 | positivo | Permitir solicitud autorizada dentro de cuota |
| ESC-INI02-RF02-N01 | HU-INI02-RF02 | negativo | Rechazar solicitud fuera de cuota |
| ESC-INI02-RF03-P01 | HU-INI02-RF03 | positivo | Publicar evento OrdenValidada |
| ESC-INI02-RF03-N01 | HU-INI02-RF03 | negativo | Rechazar evento sin correlation ID |
| ESC-INI02-RF04-P01 | HU-INI02-RF04 | positivo | Aceptar evento con esquema valido |
| ESC-INI02-RF04-N01 | HU-INI02-RF04 | negativo | Enviar evento invalido a cola de errores |
| ESC-INI02-RF05-P01 | HU-INI02-RF05 | positivo | Reentregar evento tras recuperacion de consumidor |
| ESC-INI02-RF05-N01 | HU-INI02-RF05 | negativo | No perder evento por timeout temporal |
| ESC-INI02-RF06-P01 | HU-INI02-RF06 | positivo | Enviar mensaje a DLQ tras reintentos agotados |
| ESC-INI02-RF06-N01 | HU-INI02-RF06 | negativo | Evitar reproceso manual sin autorizacion |
| ESC-INI02-RF07-P01 | HU-INI02-RF07 | positivo | Regular envios hacia WMS degradado |
| ESC-INI02-RF07-N01 | HU-INI02-RF07 | negativo | No descartar mensajes por saturacion |
| ESC-INI02-RF08-P01 | HU-INI02-RF08 | positivo | Procesar reserva critica antes que evento informativo |
| ESC-INI02-RF08-N01 | HU-INI02-RF08 | negativo | Evitar prioridad no autorizada |
| ESC-INI02-RF09-P01 | HU-INI02-RF09 | positivo | Reprocesar eventos por correlation ID |
| ESC-INI02-RF09-N01 | HU-INI02-RF09 | negativo | Rechazar replay sin aprobacion |
| ESC-INI02-RF10-P01 | HU-INI02-RF10 | positivo | Visualizar backlog y DLQ por dominio |
| ESC-INI02-RF10-N01 | HU-INI02-RF10 | negativo | Alertar falta de telemetria |
| ESC-INI02-RF11-P01 | HU-INI02-RF11 | positivo | Procesar eventos en orden por paquete |
| ESC-INI02-RF11-N01 | HU-INI02-RF11 | negativo | Retener intento fallido posterior a entrega |
| ESC-INI02-RF12-P01 | HU-INI02-RF12 | positivo | Migrar integracion con adaptador monitoreado |
| ESC-INI02-RF12-N01 | HU-INI02-RF12 | negativo | Bloquear migracion sin contrato documentado |

---

## 7. Trazabilidad

| Iniciativa | Historias | RF | RNF | Escenarios referenciados |
| --- | --- | --- | --- | --- |
| INI-02 | 12 | 12 | 9 | 24 |

---

*Documento consolidado para el Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC.*
*Fecha: Julio 2026.*
