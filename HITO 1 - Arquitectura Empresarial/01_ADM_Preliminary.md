# ADM - Preliminary
## RutaExpress Fulfillment & Transporte

> **Para el comité de arquitectura** — Este documento fija el **marco de gobierno** (Comité quincenal, Board mensual), los **principios** que toda iniciativa debe cumplir (PN/PD/PA/PT) y las **herramientas** de trabajo (Jira, draw.io, Terraform). **Mensaje clave:** antes de aprobar diseños, validar que respeten principios como API-First (PA-01), Bus de Eventos Central (PLT-03) event-driven y migración progresiva de **APP-06** hacia WMS Cloud.

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
- Todo cambio en sistemas críticos (WMS Principal (On Premises) (APP-06), TMS (Transportation Management) (APP-11), App de Conductores (APP-15), Azure API Management (APP-01)) requiere Architecture Decision Record (ADR) aprobado.
- Se usará TOGAF ADM como metodología de Arquitectura Empresarial.
- Los entregables se documentan en plantillas estándar y se registran en **Jira** (iniciativas, ADRs y trazabilidad de entregables).

> **Convención de nomenclatura (Hito 1):** catálogo maestro → [`06_Mapa_Portafolio_Aplicaciones.md`](06_Mapa_Portafolio_Aplicaciones.md). **Obligatorio en todo el Hito 1:** siempre **nombre oficial + (APP-XX)** o **(PLT-XX)** juntos; prohibido usar solo el ID o solo el nombre.

### 2.3 Herramientas y Repositorio

| Herramienta | Uso |
|---|---|
| **Jira** | Gestión de iniciativas, tareas de arquitectura, ADRs y trazabilidad de entregables |
| **draw.io** | Diagramas de arquitectura (C4, flujos, topología) |
| **Terraform** | Infraestructura como Código (IaC) |
| **ArchiMate** | Notación para modelos formales de arquitectura empresarial |

> **Criterio:** una sola herramienta por uso (la más simple de adoptar). Sin alternativas abiertas en documentación del Hito 1.

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
| PA-02 | Evitar acoplamiento directo | Los sistemas no deben llamarse directamente en flujos críticos. Se usarán **Bus de Eventos Central (PLT-03)** Bus de Eventos Central (PLT-03) o **APP-01** Azure API Management (APP-01) como intermediarios. |
| PA-03 | Preferencia SaaS cuando sea viable | Para funcionalidades no diferenciadas (CRM, portales B2B de carga y trazabilidad, firma digital, pagos) se preferirán soluciones SaaS sobre desarrollo propio. |
| PA-04 | Dominios de negocio alineados a arquitectura | Los sistemas se alinearán a dominios: Gestión de Pedidos, Almacén, Transporte, Última Milla, Trazabilidad, Liquidación. Cada dominio tendrá su propio equipo y responsabilidad. |
| PA-05 | Idempotencia y deduplicación | Todos los servicios receptores de mensajes deben implementar idempotencia para evitar duplicaciones como el incidente de los 32,000 pedidos repetidos. |

### 3.4 Principios de Arquitectura Tecnológica

| # | Principio | Descripción |
|---|---|---|
| PT-01 | Cloud-First (Nube pública) | Las nuevas capacidades se construirán en nube pública (AWS, Azure, GCP). WMS Principal (On Premises) — APP-06 — migrará progresivamente a WMS Cloud. |
| PT-02 | Infraestructura como Código (IaC) | Toda la infraestructura se define con **Terraform** (repos Git de TI). No se aprovisiona infraestructura manualmente en producción. |
| PT-03 | Seguridad desde el diseño (Security by Design) | La seguridad se incorpora en el diseño, no como capa posterior. Incluye autenticación, autorización, cifrado en tránsito y reposo, y auditoría de accesos. |
| PT-04 | Observabilidad nativa | Los sistemas deben emitir métricas, logs y trazas distribuidas desde el inicio. Se centralizará en **Plataforma de Observabilidad Unificada (PLT-01)** Plataforma de Observabilidad Unificada. |
| PT-05 | Multinube por resiliencia y capacidad | AWS, Azure y GCP según fortaleza: Azure para Orquestador de Pedidos (APP-02) y TMS (Transportation Management) (APP-11); AWS para App de Conductores (APP-15) e IoT Core (sensores temperatura) (APP-09); GCP para Optimizador de Rutas (GCP batch) (APP-12) y Plataforma de Analítica (GCP batch) (APP-22). |

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
