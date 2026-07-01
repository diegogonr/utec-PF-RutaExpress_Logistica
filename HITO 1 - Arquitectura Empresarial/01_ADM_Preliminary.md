# ADM - Preliminary
## RutaExpress Fulfillment & Transporte

> **Para el comité de arquitectura** — Este documento fija el **marco de gobierno** (Comité quincenal, Board mensual), los **principios** que toda iniciativa debe cumplir (PN/PD/PA/PT) y la **madurez actual** (gobierno e observabilidad en nivel 1). **Mensaje clave:** antes de aprobar diseños, validar que respeten principios como API-First (PA-01), PLT-03 event-driven y migración progresiva de **APP-06** hacia WMS Cloud.

---

## 1. Propósito

Esta fase establece el marco de trabajo, el modelo de gobierno y los principios de arquitectura que guiarán todas las fases del ADM de TOGAF para RutaExpress. Define cómo se organizará, gestionará y ejecutará la arquitectura empresarial en los próximos tres años.

---

## 2. Modelo de Gobierno de Arquitectura

### 2.1 Estructura de Gobierno

| Instancia | Frecuencia | Participantes | Responsabilidad |
|---|---|---|---|
| Comité de Arquitectura | Quincenal | Gerente de Arquitectura, Arquitectos Empresariales, Arquitectos de Dominio, CTO | Revisar y aprobar iniciativas arquitectónicas, resolver conflictos de diseño |
| Board Tecnológico | Mensual | CEO, CTO, CFO, COO | Validar roadmap tecnológico, aprobar inversiones, revisar riesgos críticos |
| Comunidad de Práctica | Semanal | Arquitectos de Solución, Tech Leads, DevOps | Compartir estándares, revisar patrones, resolver problemas técnicos |
| Revisión de Seguridad | Mensual | CISO, Arquitecto de Seguridad, Compliance | Auditar controles, revisar incidencias, actualizar políticas |

### 2.2 Proceso de Gobierno

- Todas las iniciativas de la empresa se presentan al Comité de Arquitectura antes de iniciar diseño.
- Se asigna un Arquitecto Empresarial por cada iniciativa de impacto transversal.
- Las iniciativas de menor alcance son validadas por el Arquitecto de Dominio correspondiente.
- Todo cambio en sistemas críticos (**APP-06** WMS Principal, **APP-11** TMS, **APP-15** App de Conductores, **APP-01** Azure API Management) requiere Architecture Decision Record (ADR) aprobado.
- Se usará TOGAF ADM como metodología de Arquitectura Empresarial.
- Los entregables se documentarán en plantillas estándar y se almacenarán en el SharePoint de Arquitectura con control de versiones.

### 2.3 Herramientas y Repositorio

| Herramienta | Uso |
|---|---|
| Confluence / SharePoint | Repositorio de documentos de arquitectura |
| draw.io / Lucidchart | Diagramas de arquitectura (C4, flujos, topología) |
| Azure DevOps / Jira | Gestión de iniciativas y tareas de arquitectura |
| Terraform / Bicep | Infraestructura como Código (IaC) |
| ArchiMate | Modelos formales de arquitectura empresarial |

---

## 3. Principios de Arquitectura

### 3.1 Principios de Arquitectura de Negocio

| # | Principio | Descripción |
|---|---|---|
| PN-01 | Digital-First | Todos los procesos logísticos deben poder ejecutarse y monitorearse digitalmente, sin depender de papel o intervención manual para el flujo principal. |
| PN-02 | Experiencia centrada en el cliente | Las decisiones de diseño deben priorizar la visibilidad, la comunicación proactiva y la satisfacción del cliente empresarial y el destinatario final. |
| PN-03 | Resiliencia operativa | Los sistemas deben mantenerse operativos durante picos de campaña (hasta 3x el volumen normal) sin degradación de servicio. |
| PN-04 | Trazabilidad end-to-end | Cada pedido debe tener trazabilidad completa desde la recepción hasta la entrega, devolución o liquidación, accesible en tiempo real. |
| PN-05 | Cumplimiento SLA prioritario | El diseño debe favorecer el cumplimiento de promesas de entrega y SLA contractuales como métrica principal del negocio. |

### 3.2 Principios de Arquitectura de Datos

| # | Principio | Descripción |
|---|---|---|
| PD-01 | Única fuente de verdad (Single Source of Truth) | Cada entidad de datos (pedido, inventario, ruta, evento de tracking, evidencia) debe tener un sistema maestro definido. Las demás son réplicas de lectura. |
| PD-02 | Modelo canónico de datos | Se definirá un modelo canónico para pedidos, SKUs, rutas, eventos y evidencias que sea adoptado por todos los sistemas integrados. |
| PD-03 | Integridad referencial entre nubes | Las integraciones entre AWS, Azure y GCP deben garantizar consistencia eventual con mecanismos de reconciliación y auditoría. |
| PD-04 | Privacidad por diseño | Los datos personales de destinatarios (nombre, dirección, teléfono, firma, foto) deben cifrados, enmascarados en ambientes no productivos y sujetos a retención regulada. |
| PD-05 | Arquitectura Medallion para analítica | Los datos operacionales se procesarán en capas Bronze → Silver → Gold para análisis, reportes y predicciones. |

### 3.3 Principios de Arquitectura de Aplicaciones

| # | Principio | Descripción |
|---|---|---|
| PA-01 | API-First | Toda integración entre sistemas internos y con clientes externos se realizará vía APIs RESTful o eventos, eliminando integraciones punto a punto y archivos. |
| PA-02 | Evitar acoplamiento directo | Los sistemas no deben llamarse directamente en flujos críticos. Se usarán **PLT-03** Bus de Eventos o **APP-01** Azure API Management como intermediarios. |
| PA-03 | Preferencia SaaS cuando sea viable | Para funcionalidades no diferenciadas (CRM, portales B2B de carga y trazabilidad, firma digital, pagos) se preferirán soluciones SaaS sobre desarrollo propio. |
| PA-04 | Dominios de negocio alineados a arquitectura | Los sistemas se alinearán a dominios: Gestión de Pedidos, Almacén, Transporte, Última Milla, Trazabilidad, Liquidación. Cada dominio tendrá su propio equipo y responsabilidad. |
| PA-05 | Idempotencia y deduplicación | Todos los servicios receptores de mensajes deben implementar idempotencia para evitar duplicaciones como el incidente de los 32,000 pedidos repetidos. |

### 3.4 Principios de Arquitectura Tecnológica

| # | Principio | Descripción |
|---|---|---|
| PT-01 | Cloud-First (Nube pública) | Las nuevas capacidades se construirán en nube pública (AWS, Azure, GCP). WMS Principal (On Premises) — APP-06 — migrará progresivamente a WMS Cloud. |
| PT-02 | Infraestructura como Código (IaC) | Toda la infraestructura debe definirse con Terraform o herramientas nativas cloud. No se aprovisiona infraestructura manualmente en producción. |
| PT-03 | Seguridad desde el diseño (Security by Design) | La seguridad se incorpora en el diseño, no como capa posterior. Incluye autenticación, autorización, cifrado en tránsito y reposo, y auditoría de accesos. |
| PT-04 | Observabilidad nativa | Los sistemas deben emitir métricas, logs y trazas distribuidas desde el inicio. Se centralizará en **PLT-01** Plataforma de Observabilidad Unificada. |
| PT-05 | Multinube por resiliencia y capacidad | AWS, Azure y GCP se usarán según fortaleza: Azure para **APP-02** Orquestador y **APP-11** TMS, AWS para **APP-15** App de Conductores e **APP-09** IoT Core, GCP para **APP-12** Optimizador y **APP-22** Analítica. |

---

## 4. Alcance de la Arquitectura Empresarial

### 4.1 Dominios cubiertos

- Arquitectura de Negocio (Business Architecture)
- Arquitectura de Datos (Data Architecture)
- Arquitectura de Aplicaciones (Application Architecture)
- Arquitectura Tecnológica (Technology Architecture)

### 4.2 Unidades organizativas involucradas

- Operaciones Logísticas (Almacén, Transporte, Última Milla)
- Tecnología e Innovación
- Finanzas y Facturación
- Atención al Cliente
- Seguridad y Cumplimiento
- Analítica y Datos

### 4.3 Horizonte temporal

- AS IS: Situación actual documentada al año 1
- Transición 1: 12 meses
- Transición 2: 24 meses
- TO BE: 36 meses

---

## 5. Madurez de Arquitectura Actual

| Dimensión | Nivel Actual | Descripción |
|---|---|---|
| Gobierno | 1 - Inicial | Sin comité formal, decisiones reactivas por proyecto |
| Integración | 2 - Repetible | APIs en algunos puntos, pero aún hay integraciones punto a punto y archivos |
| Datos | 1 - Inicial | Sin modelo canónico, múltiples fuentes de verdad por sistema |
| Infraestructura | 2 - Repetible | Multinube real pero sin estrategia unificada |
| Seguridad | 2 - Repetible | Controles básicos, sin Security by Design |
| Observabilidad | 1 - Inicial | Monitoreo parcial por APP; sin **PLT-01** unificada ni visibilidad end-to-end |

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
