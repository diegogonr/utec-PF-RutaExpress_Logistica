# ADM - Fase A: Architecture Vision
## RutaExpress Fulfillment & Transporte

> **Para el comité de arquitectura** — Responde **por qué transformar**: drivers de negocio (USD 1.1M penalidades Cyber Days), dolores operativos y **visión TO BE** con KPIs medibles (82%→94% cumplimiento promesa). **Mensaje clave:** la fragmentación entre **APP-06**, **APP-11**, **APP-15** y **APP-22** sin **PLT-03** impide trazabilidad end-to-end; este documento alinea a stakeholders antes de invertir.

---

## 1. Propósito

Definir la visión de arquitectura que guiará la transformación de RutaExpress en un operador logístico digital, predictivo y escalable para los próximos tres años. Esta fase establece el por qué del cambio, los objetivos y el alcance antes de diseñar soluciones.

---

## 2. Situación Actual (Problema)

### 2.1 Drivers del Cambio

| Driver | Descripción |
|---|---|
| Competencia del mercado | Los grandes marketplaces construyen redes logísticas propias. El mercado exige entrega el mismo día, trazabilidad en vivo y devoluciones simples. |
| Penalidades económicas | En el último Cyber Days se pagaron USD 1.1M en penalidades por 19% de entregas tardías. Una cadena retail retuvo USD 2.4M por falta de evidencia de entrega. |
| Fragmentación tecnológica | **APP-06** WMS Principal, **APP-11** TMS (Azure), **APP-15** App de Conductores (AWS), **APP-22** Plataforma de Analítica (GCP) y portales SaaS (**APP-03**, **APP-18**) operan sin integración real. No existe **PLT-01** ni **PLT-03**. |
| Problemas de datos | 6% de órdenes con defectos, 2.8% de movimientos de inventario con ajuste, 8% de eventos de tracking con retraso >20 min, 7% de facturas observadas por clientes. |
| Capacidad en campañas | **APP-06** WMS se degrada durante picos | En Cyber Days se acumularon 240,000 pedidos en cola durante 6 horas |
| Costos crecientes | Combustible, mano de obra y reintentos de entrega elevan costos sin mejorar la tasa de éxito. El 34% de entregas fallidas se debe a problemas prevenibles. |

### 2.2 Dolores Críticos Actuales

- **Pedidos duplicados** por fallo de deduplicación en API (caso: 32,000 pedidos duplicados)
- **Inventario desalineado** entre **APP-06** WMS Principal, **APP-07** WMS Satélite y **APP-25** ERP; sincronización horaria insuficiente
- **Rutas asignadas manualmente** en 17% de los casos por datos de tráfico y flota no confiables
- **Baja visibilidad de última milla**: 8% de eventos de tracking con >20 minutos de retraso
- **Evidencias perdidas** cuando conductores operan offline y reinstalan app (1,200 entregas sin firma)
- **Conciliación manual** entre nubes y ERP que toma hasta 23 días por disputa con cliente
- **Gestión de excepciones no normalizada**: motivos de fallo inconsistentes entre app, TMS, CRM

---

## 3. Visión de la Arquitectura TO BE

### 3.1 Declaración de Visión

> *"RutaExpress será una plataforma logística digital integrada, donde cada pedido tiene visibilidad en tiempo real desde la recepción hasta la entrega, los sistemas son resilientes a picos de campaña, los datos son confiables y la operación aprende continuamente de sus excepciones para mejorar el cumplimiento de promesa."*

### 3.2 Objetivos Estratégicos y Metas de Arquitectura

| Objetivo de Negocio | Meta Actual | Meta TO BE | Habilitador Arquitectónico |
|---|---|---|---|
| Cumplimiento de promesa de entrega | 82% | 94% | Integración en tiempo real, rutas dinámicas, validación de dirección anticipada |
| Reducir entregas fallidas | 12.5% | 7% | Pre-validación de direcciones, comunicación proactiva, taxonomía de excepciones |
| Tiempo orden→despacho | 9.5 horas | 4 horas | WMS cloud-ready, automatización de picking, integración WMS-TMS en tiempo real |
| Visibilidad de tracking | ~70% confiable | 98% | Plataforma de eventos unificada, sincronización offline robusta |
| Reducción costo por entrega | Línea base | -15% | Optimización dinámica de rutas, consolidación, control de flota |
| Disponibilidad sistemas críticos | ~95% (campañas) | 99.9% | Auto-scaling, circuit breakers, queues con backpressure, RTO <15 min |
| Seguridad de datos | Controles básicos | Security by Design | Cifrado, enmascaramiento, auditoría de accesos, OAuth 2.0 |

---

## 4. Stakeholders y sus Preocupaciones

| Stakeholder | Rol | Preocupación Principal |
|---|---|---|
| CEO / Directorio | Patrocinador | ROI de la transformación, reducción de penalidades, posición competitiva |
| CTO | Sponsor Tecnológico | Arquitectura sostenible, deuda técnica, disponibilidad en campañas |
| COO | Operaciones | Tiempo de ciclo, tasa de entrega exitosa, gestión de excepciones |
| CFO | Finanzas | Costo de transformación, ROI, reducción de penalidades, facturación correcta |
| Gerente de Almacén | Usuario Clave | WMS estable, inventario confiable, operación sin interrupciones |
| Gerente de Transporte | Usuario Clave | Rutas optimizadas, flota utilizada eficientemente, TMS integrado |
| Jefe de TI / Arquitectura | Ejecutor | Hoja de ruta técnica clara, herramientas y plataformas definidas |
| Clientes Empresariales | Externos | Visibilidad de pedidos, APIs confiables, reportes precisos, SLA cumplido |
| Conductores | Usuarios Finales | App estable, soporte offline, flujo simple de excepciones |
| Destinatarios Finales | Externos | Trazabilidad, comunicación proactiva, entrega en ventana horaria |

---

## 5. Alcance de la Arquitectura

### 5.1 En Alcance

- Integración de la cadena de valor completa: Recepción → Preparación → Despacho → Entrega → Excepciones → Liquidación
- Plataforma de integración (**APP-01** Azure API Management + **PLT-03** Event Streaming)
- Modernización del WMS (**APP-06** / **APP-07** → WMS Cloud)
- Integración **APP-11** TMS — **APP-06** WMS — **APP-15** App de Conductores — **APP-12** Optimizador de Rutas
- Plataforma de tracking y eventos unificada (**PLT-03**)
- Gestión de evidencias (**APP-16** Almacenamiento Evidencias S3) con resiliencia offline en **APP-15**
- Plataforma analítica predictiva (**APP-22**, **APP-24** ML) para rutas y excepciones
- Portal unificado B2B con trazabilidad en tiempo real (consolida **APP-03** y **APP-18** en TO BE)
- Seguridad de datos personales (destinatarios) y operación móvil

### 5.2 Fuera de Alcance (Hito 1)

- Rediseño del **APP-25** ERP Financiero (se integra, no se reemplaza)
- Rediseño del **APP-20** CRM SaaS (se mejora la taxonomía de excepciones)
- Operaciones internacionales o expansión de cobertura geográfica

---

## 6. KPIs de Éxito de la Arquitectura

| KPI | Baseline | Target 12m | Target 24m | Target 36m |
|---|---|---|---|---|
| % cumplimiento de promesa | 82% | 87% | 91% | 94% |
| % entregas fallidas | 12.5% | 10% | 8.5% | 7% |
| Tiempo orden→despacho | 9.5 h | 7 h | 5 h | 4 h |
| % tracking confiable | ~70% | 85% | 93% | 98% |
| Disponibilidad campaña | ~95% | 98% | 99.5% | 99.9% |
| % facturas observadas | 7% | 5% | 3% | 1.5% |
| Tiempo conciliación disputa | 23 días | 10 días | 5 días | 1 día |

---

## 7. Restricciones y Supuestos

### Restricciones

- **APP-06** WMS Principal no puede migrarse completamente en el primer año; debe convivir con WMS Cloud en transición progresiva (F1 → F2).
- Los clientes grandes tienen integraciones API que no pueden romperse; los cambios deben ser backward-compatible.
- Presupuesto de transformación debe ser aprobado por el Board Tecnológico por fases.
- Todos los datos de destinatarios deben cumplir con regulaciones de privacidad (Ley 29733 - Perú).

### Supuestos

- La empresa contará con un equipo de arquitectura dedicado de al menos 3 personas.
- Los proveedores cloud (AWS, Azure, GCP) ofrecerán soporte técnico en la migración.
- Los clientes empresariales aceptarán actualizar sus integraciones en un plazo de 6 meses con soporte de RutaExpress.
- Se dispondrá de datos históricos de tracking y rutas para entrenar los modelos predictivos.

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
