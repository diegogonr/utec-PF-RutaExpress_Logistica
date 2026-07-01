# ADM - Fase E: Opportunities and Solutions
## RutaExpress Fulfillment & Transporte

> **Para el comité de arquitectura** — **Gap analysis** (negocio, datos, apps, tecnología) y **7 iniciativas** (INI-01 … INI-07) con arquitecturas de transición. **Mensaje clave:** priorizar **INI-01** (**PLT-03** Bus de Eventos) e **INI-02** (WMS Cloud reemplaza **APP-06**/**APP-07**); quick wins **INI-03** (**APP-15**) e **INI-06** (**APP-05** Validador).

---

## 1. Propósito

Identificar y consolidar las brechas (gaps) entre el estado AS IS y el TO BE en las dimensiones de Negocio, Datos, Aplicaciones y Tecnología. Agrupar estas brechas en iniciativas o proyectos priorizados, y definir las arquitecturas de transición necesarias.

---

## 2. Análisis de Brechas (GAP Analysis)

### 2.1 Gaps de Negocio

| ID Gap | Descripción | Impacto | Dominio |
|---|---|---|---|
| GN-01 | Sin validación integral de órdenes (dirección, SKU, duplicados) antes de ingresar al flujo | Alto - 6% órdenes con defectos, incidente 32K duplicados | Recepción |
| GN-02 | Gestión de excepciones sin taxonomía normalizada impide aprender y prevenir | Alto - 34% fallas prevenibles, USD 1.20-2.80/reintento | Última Milla |
| GN-03 | Sin comunicación proactiva con destinatario antes de la entrega | Alto - ausencia/dirección = 34% de fallas | Última Milla |
| GN-04 | Proceso de liquidación manual con **APP-26** Sistema de Liquidación (Excel) y conciliación de 23 días | Alto - USD 2.4M retenidos, 7% facturas observadas | Liquidación |
| GN-05 | Sin visibilidad operativa en tiempo real (**APP-22** batch, sin **PLT-01**) | Medio - planners trabajan con datos del día anterior | Analítica |
| GN-06 | Asignación manual de rutas en 17% de casos sin causa documentada | Medio - costos elevados, SLA en riesgo | Transporte |

### 2.2 Gaps de Datos

| ID Gap | Descripción | Impacto | Dominio |
|---|---|---|---|
| GD-01 | Sin modelo canónico de estados entre **APP-06**, **APP-11**, **APP-15** y **APP-18** Portal B2B (Trazabilidad) | Crítico - estados contradictorios visibles al cliente | Todos |
| GD-02 | Múltiples fuentes de verdad para inventario (**APP-06**, **APP-07**, **APP-25** ERP) | Alto - 2.8% movimientos con ajuste, conflictos en reconexión | Almacén |
| GD-03 | Eventos de tracking sin orden garantizado, pérdida en offline | Alto - 1,200 entregas sin firma, clientes disputan estados | Tracking |
| GD-04 | **APP-22** Plataforma de Analítica semanal, sin **PLT-01** | Medio - no se detectan degradaciones hasta que explotan | Analítica |
| GD-05 | Datos de excepciones inconsistentes impiden entrenar **APP-24** ML | Medio - **APP-12** Optimizador aprende con datos sucios | ML/Rutas |

### 2.3 Gaps de Aplicaciones

| ID Gap | Descripción | Impacto | Dominio |
|---|---|---|---|
| GA-01 | **APP-06** WMS Principal (On Premises) sin capacidad de auto-scaling ni HA | Crítico - degradación en Cyber Days, USD 1.1M penalidades | Almacén |
| GA-02 | **APP-02** Orquestador sin backpressure por cliente ni prioridad SLA | Crítico - cola sin control ante degradación WMS | Recepción |
| GA-03 | **APP-12** Optimizador de Rutas en batch, no tiempo real | Alto - rutas inviables por datos de tráfico desactualizados | Transporte |
| GA-04 | **APP-15** App de Conductores con offline frágil y evidencias que se pierden | Alto - disputas de liquidación, reclamos de custodia | Última Milla |
| GA-05 | Sin **PLT-03** Bus de Eventos central, integraciones punto a punto | Alto - fragilidad, inconsistencia, difícil mantener | Todos |
| GA-06 | Liquidación con **APP-26** Sistema de Liquidación (Excel) sin control | Crítico - errores manuales, penalidades mal calculadas | Liquidación |
| GA-07 | Sin **PLT-01** Plataforma de Observabilidad unificada cross-cloud | Alto - sin visibilidad end-to-end, detección tardía de fallos | Todos |

### 2.4 Gaps de Tecnología

| ID Gap | Descripción | Impacto | Dominio |
|---|---|---|---|
| GT-01 | **APP-06** WMS Principal sobre SQL Server sin escalado ni HA | Crítico - degradación en campañas | Almacén |
| GT-02 | Sin **PLT-04** IaC | Alto - cambios manuales, no reproducibles | Todos |
| GT-03 | Sin **PLT-02** Zero Trust | Alto - APIs expuestas, datos personales en riesgo | Seguridad |
| GT-04 | Sin conexión privada entre nubes (tráfico por Internet público) | Medio - latencia variable, costos de egress, riesgo seguridad | Multinube |
| GT-05 | Sin DR definido para **APP-06** WMS y **APP-11** TMS | Alto - RTO/RPO indefinidos | Resiliencia |

---

## 3. Iniciativas / Proyectos

### INI-01: Plataforma de Integración por Eventos — PLT-03 Bus Central
**Descripción**: Implementar **PLT-03** Bus de Eventos central (Apache Kafka / Azure Event Hubs) que reemplace las integraciones P2P entre **APP-06** WMS, **APP-11** TMS, **APP-15** App de Conductores y **APP-22** Analítica.
**Gaps que cierra**: GA-05, GD-01, GD-03, GD-04, GT-02
**Valor**: Elimina integraciones frágiles, habilita modelo canónico de estados, permite replay de eventos.
**Complejidad**: Alta
**Duración estimada**: 6-9 meses

### INI-02: Modernización WMS — APP-06 / APP-07 → WMS Cloud
**Descripción**: Migrar **APP-06** WMS Principal y **APP-07** WMS Satélite a WMS Cloud con auto-scaling, modo degradado y sync en tiempo real.
**Gaps que cierra**: GA-01, GD-02, GT-01, GT-05
**Valor**: Elimina el principal punto de falla en campañas, evita USD 1.1M+ en penalidades.
**Complejidad**: Muy Alta
**Duración estimada**: 9-12 meses

### INI-03: APP-15 App de Conductores Resiliente (Offline + Evidencias)
**Descripción**: Rediseñar **APP-15** con SQLite cifrado, sync atómica hacia **APP-16** Evidencias S3, taxonomía de excepciones y MDM.
**Gaps que cierra**: GA-04, GD-03, GN-02
**Valor**: Elimina pérdida de evidencias, normaliza datos de excepciones para ML.
**Complejidad**: Media
**Duración estimada**: 3-4 meses

### INI-04: APP-12 Optimizador de Rutas en Tiempo Real
**Descripción**: Migrar **APP-12** de batch a streaming (GKE + Cloud Pub/Sub) con re-optimización dinámica.
**Gaps que cierra**: GA-03, GN-06, GD-05
**Valor**: Reduce 17% rutas manuales, mejora cumplimiento SLA, ahorro en combustible.
**Complejidad**: Alta
**Duración estimada**: 6-8 meses

### INI-05: Automatización Liquidación — reemplaza APP-26
**Descripción**: Reemplazar **APP-26** Sistema de Liquidación (Excel) con microservicio que concilia **APP-06**, **APP-11**, **APP-15** y **APP-25** ERP en tiempo real.
**Gaps que cierra**: GA-06, GN-04, GD-04
**Valor**: Reduce conciliación de 23 días a <1 día, elimina USD 2.4M de disputas.
**Complejidad**: Alta
**Duración estimada**: 5-7 meses

### INI-06: Validación Integral de Órdenes — APP-05 / APP-02
**Descripción**: Fortalecer **APP-05** Validador y **APP-02** Orquestador con validación en tiempo real y comunicación proactiva (**APP-21** Servicio de Notificación).
**Gaps que cierra**: GN-01, GN-03, GD-01
**Valor**: Reducir entregas fallidas de 12.5% a 7%, ahorro en reintentos (USD 1.2-2.8/intento × 8,500/día).
**Complejidad**: Media
**Duración estimada**: 3-5 meses

### INI-07: PLT-01 Observabilidad + PLT-02 Seguridad + PLT-04 IaC
**Descripción**: Implementar **PLT-01** (Datadog + OpenTelemetry), **PLT-02** Zero Trust (Azure AD, WAF en **APP-01**, SIEM, DLP) y **PLT-04** Terraform multinube.
**Gaps que cierra**: GA-07, GT-02, GT-03, GT-04
**Valor**: Detección temprana de degradaciones, seguridad de datos personales, cumplimiento regulatorio.
**Complejidad**: Media-Alta
**Duración estimada**: 4-6 meses

---

## 4. Arquitecturas de Transición

### Estado AS IS → TO BE

```
AS IS (Año 0):
────────────────────────────────────────────────
• **APP-06** WMS Principal — SQL Server
• Integraciones P2P (sin **PLT-03**)
• **APP-12** Optimizador batch
• **APP-15** offline frágil
• **APP-26** Liquidación Excel
• Sin **PLT-01** observabilidad

         │
         ▼

TRANSICIÓN 1 (Año 1 - primeros 12 meses):
────────────────────────────────────────────────
• **PLT-03** Bus de eventos operativo
• **APP-02** Orquestador con backpressure
• **APP-15** rediseñada (offline + taxonomía)
• **APP-05** Validación de órdenes
• **PLT-04** IaC Terraform
• **PLT-01** Observabilidad básica
• **APP-06** en modo puente (API, sin migración aún)

         │
         ▼

TRANSICIÓN 2 (Año 2 - meses 12-24):
────────────────────────────────────────────────
• WMS Cloud (reemplaza **APP-06**/**APP-07**)
• **APP-12** Optimizador RT (GKE + Pub/Sub)
• Servicio Liquidación (reemplaza **APP-26**)
• Comunicación proactiva (**APP-21**)
• **PLT-02** Zero Trust
• **APP-22** Analítica streaming (BigQuery + Dataflow)
• **APP-25** ERP integrado en tiempo real

         │
         ▼

TO BE (Año 3 - meses 24-36):
────────────────────────────────────────────────
• Plataforma logística digital completa
• Event Store canónico como fuente única de verdad
• ML predictivo para rutas y detección de excepciones
• Auto-scaling ante cualquier pico (hasta 3x)
• Disponibilidad 99.9% en campaña
• Conciliación automática <1 día
• 98% trazabilidad confiable
• Zero Trust + Security by Design completo
```

### Diagrama de Transición

```
┌────────────┐     ┌────────────────────┐     ┌────────────────────┐     ┌──────────┐
│   AS IS    │────►│  TRANSICIÓN 1      │────►│  TRANSICIÓN 2      │────►│  TO BE   │
│            │     │                    │     │                    │     │          │
│ WMS        │     │ Bus de Eventos +   │     │ WMS Cloud +        │     │ Platform │
│ Principal  │     │ App de             │     │ Optimizador de     │     │ Digital  │
│ (On        │     │ Conductores v2 +   │     │ Rutas en Tiempo    │     │ Completa │
│ Premises)  │     │ Validación +       │     │ Real + Liquidación │     │          │
│ Batch      │     │ IaC + Observab.    │     │ Auto + Zero Trust +│     │          │
│ Integ P2P  │     │                    │     │ Analítica Stream.  │     │          │
│ Sistema de │     │                    │     │                    │     │          │
│ Liquidación│     │                    │     │                    │     │          │
│ (Excel)    │     │                    │     │                    │     │          │
└────────────┘     └────────────────────┘     └────────────────────┘     └──────────┘
   Hoy             Año 1 (mes 12)              Año 2 (mes 24)             Año 3 (mes 36)
```

---

## 5. Priorización de Iniciativas (Valor vs Esfuerzo)

```
ALTO VALOR / BAJO ESFUERZO (Quick Wins):
  ► INI-03: **APP-15** App de Conductores Resiliente (3-4 meses)
  ► INI-06: Validación Órdenes **APP-05** (3-5 meses)

ALTO VALOR / ALTO ESFUERZO (Apuestas Estratégicas):
  ► INI-01: **PLT-03** Bus de Eventos Central
  ► INI-02: WMS Cloud (reemplaza **APP-06**/**APP-07**)
  ► INI-04: **APP-12** Optimizador Tiempo Real
  ► INI-05: Liquidación (reemplaza **APP-26**)

MEDIO VALOR / MEDIO ESFUERZO (Necesarios):
  ► INI-07: **PLT-01** + **PLT-02** + **PLT-04**
```

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
