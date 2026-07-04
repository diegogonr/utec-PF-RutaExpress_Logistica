# ADM - Fase A: Architecture Vision
## RutaExpress Fulfillment & Transporte

> **Para el comité de arquitectura** — Fase A del ADM: **solo alineamos dirección y justificamos el cambio**. Aquí todavía no diseñamos aplicaciones ni tecnología.

---

## Situación:

RutaExpress opera la cadena logística completa (recepción de pedidos, preparación en almacén, transporte, última milla y liquidación) para clientes empresariales y destinatarios finales. Hoy la operación no sostiene las exigencias del mercado ni las campañas de alto volumen.

- En el último **Cyber Days**, el cumplimiento de la promesa de entrega fue del **82%**; se pagaron **USD 1.1M** en penalidades por entregas tardías y el WMS principal estuvo degradado **6 horas** con **240.000 pedidos** en cola.
- **12,5%** de entregas fallan diariamente (~8.500 paquetes); el **34%** de esas fallas se deben a causas prevenibles (dirección incorrecta, ausencia del destinatario, datos erróneos al ingreso).
- **6%** de órdenes llegan con defectos al flujo; un incidente generó **32.000 pedidos duplicados** por fallo de validación.
- **2,8%** de movimientos de inventario requieren ajuste manual; el inventario no está alineado entre almacenes centrales, satélites y finanzas.
- **~70%** de tracking es confiable; **8%** de eventos llega con más de **20 minutos** de retraso.
- En un incidente se perdieron **1.200 firmas** de entrega; un cliente retail retuvo **USD 2,4M** por falta de evidencia.
- La conciliación con clientes puede tomar hasta **23 días**; **7%** de facturas queda observada.
- El **17%** de rutas se corrige manualmente por datos de tráfico y operación poco confiables.
- Los sistemas críticos de la operación están fragmentados entre distintos entornos y proveedores, **sin integración unificada ni visibilidad end-to-end**.

---

## Drivers

● **Competencia de marketplaces y operadores digitales** — el mercado exige entrega el mismo día, trazabilidad en vivo y devoluciones simples; los competidores construyen redes logísticas propias.

● **Penalidades y retención de pagos** — USD 1.1M en penalidades por campaña; USD 2.4M retenidos por un solo cliente por disputas de evidencia y liquidación.

● **Mala experiencia digital** — clientes B2B y destinatarios finales ven estados contradictorios, tracking tardío y poca comunicación proactiva antes de la entrega.

● **Fragmentación operativa y de datos** — recepción, almacén, transporte, última milla y liquidación no comparten la misma información en tiempo real; múltiples fuentes de verdad generan errores y retrabajo.

● **Capacidad insuficiente en picos** — en campañas el volumen puede triplicarse; la operación actual no escala sin degradación ni caídas prolongadas.

● **Costos crecientes sin mejora de resultado** — combustible, mano de obra y reintentos elevan el costo por entrega sin reducir la tasa de éxito.

---

## Objetivo:

Transformar RutaExpress en un **operador logístico digital, predictivo y escalable** en un horizonte de **36 meses**, con trazabilidad confiable de punta a punta y operación resiliente en campañas.

Metas de negocio concretas:

| Meta | Situación actual | Objetivo TO BE |
|---|---|---|
| Cumplimiento de promesa de entrega | 82% | **94%** |
| Entregas fallidas | 12,5% | **7%** |
| Tiempo orden → despacho | 9,5 horas | **4 horas** |
| Tracking confiable | ~70% | **98%** |
| Disponibilidad en campaña | ~95% | **99,9%** |
| Facturas observadas por clientes | 7% | **1,5%** |
| Tiempo de conciliación en disputa | 23 días | **< 1 día** |
| Costo por entrega | Línea base | **−15%** |

> *"Cada pedido tendrá visibilidad en tiempo real desde la recepción hasta la entrega o liquidación; la operación absorberá picos de campaña sin caer, los datos serán confiables y las excepciones alimentarán la mejora continua del cumplimiento de promesa."*

---

## Alcance

**En alcance (Hito 1 — visión de transformación):**

● Cadena de valor completa: **Recepción → Preparación → Despacho → Entrega → Excepciones → Liquidación**

● **Operación de almacén** — inventario confiable, absorción de picos y sincronización en tiempo real entre centros de distribución

● **Transporte y planificación de rutas** — optimización dinámica y menos intervención manual en la asignación

● **Última milla** — evidencias de entrega inviolables, gestión estandarizada de excepciones y comunicación proactiva al destinatario

● **Trazabilidad y visibilidad B2B** — estados consistentes para clientes empresariales y destinatarios

● **Liquidación y conciliación** — cierre financiero ágil, sin procesos manuales prolongados

● **Integración y datos** — modelo común de estados y eventos entre dominios de la operación

● **Resiliencia en campaña** — continuidad operativa ante picos de hasta 3× el volumen normal

● **Seguridad y privacidad** — protección de datos personales de destinatarios (cumplimiento Ley 29733 — Perú)

**Fuera de alcance (Hito 1):**

● Rediseño del ERP financiero (se integra, no se reemplaza)

● Rediseño del CRM de atención al cliente (se mejora la taxonomía de excepciones)

● Expansión geográfica u operación internacional

---

## KPI

Indicadores para validar que la visión se cumple:

| KPI | Línea base | Meta 12 meses | Meta 24 meses | Meta 36 meses |
|---|---|---|---|---|
| **% cumplimiento de promesa** | 82% | 87% | 91% | **94%** |
| **% entregas fallidas** | 12,5% | 10% | 8,5% | **7%** |
| **Tiempo orden → despacho** | 9,5 h | 7 h | 5 h | **4 h** |
| **% tracking confiable** | ~70% | 85% | 93% | **98%** |
| **Disponibilidad en campaña** | ~95% | 98% | 99,5% | **99,9%** |
| **% facturas observadas** | 7% | 5% | 3% | **1,5%** |
| **Tiempo conciliación disputa** | 23 días | 10 días | 5 días | **< 1 día** |

Resumen ejecutivo de seguimiento:

● **Cumplimiento de promesa** — principal métrica de negocio y SLA contractual

● **Entregas fallidas** — refleja calidad de datos al ingreso, ruta y última milla

● **Tracking confiable** — visibilidad end-to-end para clientes y operación

● **Disponibilidad en campaña** — resiliencia ante Cyber Days y picos estacionales

● **Conciliación y facturación** — impacto directo en caja y relación con clientes B2B

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
