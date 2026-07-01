# ADM - Requirements Management
## RutaExpress Fulfillment & Transporte

> **Para el comité de arquitectura** — Catálogo de **requisitos funcionales (RF)** y **no funcionales (RNF)** con trazabilidad a fases ADM. **Mensaje clave:** cada requisito crítico debe poder vincularse a una APP o PLT (ej. RF-18 → **PLT-03**, RF-14 → **APP-15**, RNF-21 → alertas sobre **APP-06**, **APP-11**, **APP-15**); sirve para validar que el diseño TO BE no deje huecos.

---

## 1. Propósito

Capturar, clasificar y mantener trazabilidad de todos los requisitos que guían las fases del ADM de RutaExpress. Esta gestión es transversal a todas las fases del ADM (A hasta F) y garantiza que los requisitos se incorporan y satisfacen en el diseño de la arquitectura.

---

## 2. Fuentes de Requisitos

| Fuente | Descripción |
|---|---|
| Estrategia del negocio | Objetivos del directorio: cumplimiento de promesa 94%, visibilidad 98%, disponibilidad 99.9% |
| Riesgos tecnológicos | Tres riesgos críticos identificados: Disponibilidad, Integridad de datos, Operación |
| Stakeholders | Gerentes de almacén, transporte, finanzas, TI, atención al cliente |
| Incidentes operativos | Cyber Days: 240K pedidos en cola, USD 1.1M en penalidades, 19% entregas tardías |
| Clientes empresariales | SLA contractuales, APIs de integración, reportes de trazabilidad, facturación |
| Regulación | Ley 29733 de Protección de Datos Personales (Perú) para datos de destinatarios |
| Auditoría | Diferencias de conciliación con clientes (USD 2.4M retenidos), evidencias de entrega |

---

## 3. Catálogo de Requisitos

### 3.1 Requisitos Funcionales

#### Dominio: Gestión de Pedidos

| ID | Requisito | Fuente | Prioridad | Fase ADM |
|---|---|---|---|---|
| RF-01 | El sistema debe validar automáticamente la dirección, SKU y duplicación de cada orden antes de aceptarla en el flujo | Incidente duplicados | Alta | B, C |
| RF-02 | Se debe implementar deduplicación idempotente usando ID externo del cliente + hash de contenido | Incidente 32K pedidos | Alta | C |
| RF-03 | Las órdenes deben procesarse en tiempo real desde APIs, archivos y **APP-03** Portal B2B (Carga CSV/Excel), con prioridad por SLA | Operaciones | Alta | C |
| RF-04 | El estado del pedido debe propagarse en tiempo real a todos los sistemas consumidores (**APP-06** WMS, **APP-11** TMS, **APP-18** Portal B2B Trazabilidad) | Trazabilidad | Alta | B, C |
| RF-05 | Se deben manejar picos de hasta 180,000 órdenes/día sin degradación | Cyber Days | Alta | D |

#### Dominio: Almacén / WMS

| ID | Requisito | Fuente | Prioridad | Fase ADM |
|---|---|---|---|---|
| RF-06 | El inventario debe sincronizarse en tiempo real (no por lotes horarios) entre **APP-06**/**APP-07** WMS y los sistemas cloud | Incidente 74 min sin conectividad | Alta | C, D |
| RF-07 | **APP-06**/**APP-07** WMS debe soportar operación en modo degradado con reconciliación automática al reconectar | Incidente 4,900 movimientos en conflicto | Alta | D |
| RF-08 | Los movimientos de inventario deben generar eventos auditables con usuario, timestamp y motivo | Auditoría | Media | C |
| RF-09 | El control de cadena de frío debe integrarse con **APP-06** WMS para bloquear despacho fuera de temperatura | Farmacéuticas | Alta | C |

#### Dominio: Transporte / TMS

| ID | Requisito | Fuente | Prioridad | Fase ADM |
|---|---|---|---|---|
| RF-10 | Las rutas deben generarse automáticamente con datos de tráfico en tiempo real desde **APP-12** Optimizador de Rutas (GCP) | Rutas manuales 17% | Alta | C, D |
| RF-11 | Los manifiestos de despacho deben incluir todos los paquetes confirmados por **APP-06** WMS antes de cerrarse | Rutas con paquetes faltantes | Alta | C |
| RF-12 | Los cambios manuales de rutas en **APP-11** TMS deben registrarse con motivo estructurado, aprobador y timestamp | Auditoría de rutas | Media | C |
| RF-13 | **APP-11** TMS debe gestionar restricciones de vehículos, zonas, capacidad y tipo de carga | Operaciones | Alta | C |

#### Dominio: Última Milla / APP-15 App de Conductores

| ID | Requisito | Fuente | Prioridad | Fase ADM |
|---|---|---|---|---|
| RF-14 | **APP-15** App de Conductores debe funcionar completamente offline con sincronización segura al reconectar | Incidente 1,200 firmas perdidas | Alta | C, D |
| RF-15 | Las evidencias en **APP-15**/**APP-16** (foto, firma, geolocalización, timestamp) deben cifrarse localmente y subirse de forma atómica | Seguridad + Auditoría | Alta | C, D |
| RF-16 | Los motivos de excepción deben ser taxonomía normalizada y obligatoria (sin texto libre para el motivo principal) | Incidente excepciones no comparables | Alta | B, C |
| RF-17 | El tracking de ubicación debe publicarse cada 2 minutos hacia **APP-18** Portal B2B (Trazabilidad) y **APP-20** CRM Atención al Cliente | Visibilidad | Alta | C |

#### Dominio: Trazabilidad y Eventos

| ID | Requisito | Fuente | Prioridad | Fase ADM |
|---|---|---|---|---|
| RF-18 | Todos los eventos del ciclo de vida del pedido deben publicarse en **PLT-03** Bus de Eventos centralizado | Arquitectura | Alta | C, D |
| RF-19 | El modelo canónico de estados debe incluir: recibido, validado, reservado, pickeado, despachado, en ruta, entregado, fallido, devuelto, liquidado | Integridad de datos | Alta | B, C |
| RF-20 | Los eventos fuera de orden deben ser detectados y reordenados antes de actualizar el estado visible | Incidente eventos offline | Alta | C |

#### Dominio: Liquidación y Facturación

| ID | Requisito | Fuente | Prioridad | Fase ADM |
|---|---|---|---|---|
| RF-21 | La conciliación entre **APP-06** WMS, **APP-11** TMS, **APP-15** App de Conductores y **APP-25** ERP debe ser automatizada con detección de diferencias | Incidente 23 días conciliación | Alta | C |
| RF-22 | Los reportes de trazabilidad para clientes deben generarse en tiempo real con la misma fuente de datos que la facturación | Disputa USD 2.4M | Alta | C |
| RF-23 | Las penalidades por SLA deben calcularse automáticamente al cierre de cada ciclo de entrega | Finanzas | Media | C |

---

### 3.2 Requisitos No Funcionales

#### Disponibilidad y Resiliencia

| ID | Requisito | Target | Fuente |
|---|---|---|---|
| RNF-01 | Disponibilidad de sistemas críticos (**APP-02** Orquestador, **APP-06** WMS, **APP-11** TMS, **APP-15** App de Conductores, **APP-19** Portal Tracking Destinatarios) en campaña | 99.9% | Objetivo estratégico |
| RNF-02 | RTO (Recovery Time Objective) para **APP-06** WMS y **APP-11** TMS | < 15 minutos | Riesgo disponibilidad |
| RNF-03 | RPO (Recovery Point Objective) para datos de pedidos y tracking | < 5 minutos | Riesgo disponibilidad |
| RNF-04 | El sistema debe escalar automáticamente ante picos de hasta 3x el volumen normal | Auto-scaling | Cyber Days |
| RNF-05 | Implementar circuit breakers entre **APP-06** WMS, **APP-11** TMS y **APP-02** Orquestador para evitar fallos en cascada | Resiliencia | Riesgo disponibilidad |
| RNF-06 | Las colas de mensajes deben implementar backpressure por cliente y prioridad por SLA | Resiliencia | Cyber Days |

#### Rendimiento

| ID | Requisito | Target | Fuente |
|---|---|---|---|
| RNF-07 | Tiempo de respuesta para validación y aceptación de orden | < 2 segundos p95 | Integración API |
| RNF-08 | Tiempo máximo de latencia para publicación de evento de tracking | < 30 segundos end-to-end | Visibilidad |
| RNF-09 | Tiempo de generación de ruta optimizada | < 5 minutos para batch de 2,700 vehículos | Operaciones |
| RNF-10 | Throughput de recepción de órdenes en campaña | 180,000 órdenes/día, pico de 500 órdenes/minuto | Volumen |

#### Seguridad

| ID | Requisito | Descripción | Fuente |
|---|---|---|---|
| RNF-11 | Autenticación y autorización para todas las APIs de clientes | OAuth 2.0 / API Keys con scopes | Seguridad |
| RNF-12 | Cifrado de datos en tránsito y en reposo para datos de destinatarios | TLS 1.3 + AES-256 | Ley 29733 |
| RNF-13 | Enmascaramiento de datos personales en ambientes no productivos | PII Masking | Privacidad |
| RNF-14 | Auditoría de accesos a datos sensibles (firmas, fotos, datos personales) | Logs inmutables | Compliance |
| RNF-15 | Operación segura de la app móvil: cifrado local, certificado de dispositivo | MDM / App Security | Operación móvil |

#### Integridad y Consistencia

| ID | Requisito | Descripción | Fuente |
|---|---|---|---|
| RNF-16 | Deduplicación idempotente en todos los puntos de entrada de mensajes | Exactamente-una-vez semántica | Incidente duplicados |
| RNF-17 | Consistencia eventual garantizada con tiempo máximo de convergencia | < 60 segundos entre sistemas | Integridad |
| RNF-18 | Detección y alerta automática de inconsistencias entre **APP-06** WMS, **APP-11** TMS y **APP-18** Portal B2B (Trazabilidad) | Monitoreo activo | Riesgo integridad |

#### Observabilidad — PLT-01

| ID | Requisito | Descripción | Fuente |
|---|---|---|---|
| RNF-19 | Trazas distribuidas end-to-end para cada pedido (desde recepción hasta entrega) | OpenTelemetry en **PLT-01** | Observabilidad |
| RNF-20 | **APP-23** Dashboards operativos en tiempo real: cola de pedidos, rutas en curso, tracking, excepciones | Operaciones | Visibilidad |
| RNF-21 | Alertas automáticas ante degradación de **APP-06** WMS, **APP-11** TMS, **APP-15** App de Conductores o **APP-19** Portal Tracking Destinatarios | SRE | Riesgo disponibilidad |

---

## 4. Trazabilidad de Requisitos por Fase ADM

| Fase ADM | Requisitos Funcionales | Requisitos No Funcionales |
|---|---|---|
| A - Architecture Vision | Todos (contexto) | Todos (contexto) |
| B - Business Architecture | RF-01, RF-04, RF-16, RF-19 | RNF-01, RNF-05 |
| C - Information Systems Architecture | RF-02 a RF-23 | RNF-11 a RNF-18 |
| D - Technology Architecture | RF-05, RF-06, RF-07, RF-14, RF-15 | RNF-01 a RNF-10, RNF-19 a RNF-21 |
| E - Opportunities & Solutions | Todos (gaps identificados) | Todos (capacidades requeridas) |
| F - Migration Planning | Todos (priorizados por valor) | Todos (viabilidad técnica) |

---

## 5. Gestión de Cambios en Requisitos

- Los requisitos se versionan en el repositorio de arquitectura (SharePoint/Confluence).
- Todo cambio de requisito en fase C o D requiere análisis de impacto y aprobación del Comité de Arquitectura.
- Los requisitos nuevos que emergen de fases posteriores (E, F) se incorporan al catálogo y se trazan hacia atrás.
- Los requisitos con conflicto entre dominios se escalan al Comité de Arquitectura para resolución.

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
