# ADM - Fase E: Opportunities and Solutions
## RutaExpress Fulfillment & Transporte

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
| GN-04 | Proceso de liquidación manual con Excel y conciliación de 23 días | Alto - USD 2.4M retenidos, 7% facturas observadas | Liquidación |
| GN-05 | Sin visibilidad operativa en tiempo real para toma de decisiones | Medio - planners trabajan con datos del día anterior | Analítica |
| GN-06 | Asignación manual de rutas en 17% de casos sin causa documentada | Medio - costos elevados, SLA en riesgo | Transporte |

### 2.2 Gaps de Datos

| ID Gap | Descripción | Impacto | Dominio |
|---|---|---|---|
| GD-01 | Sin modelo canónico de estados de pedido entre WMS, TMS, App y Portal | Crítico - estados contradictorios visibles al cliente | Todos |
| GD-02 | Múltiples fuentes de verdad para inventario (WMS on-prem, satélites, ERP) | Alto - 2.8% movimientos con ajuste, conflictos en reconexión | Almacén |
| GD-03 | Eventos de tracking sin orden garantizado, pérdida en offline | Alto - 1,200 entregas sin firma, clientes disputan estados | Tracking |
| GD-04 | Analítica consolidada semanalmente, sin visibilidad operativa real | Medio - no se detectan degradaciones hasta que explotan | Analítica |
| GD-05 | Datos de excepciones inconsistentes impiden entrenar modelos ML correctamente | Medio - optimizador GCP aprende con datos sucios | ML/Rutas |

### 2.3 Gaps de Aplicaciones

| ID Gap | Descripción | Impacto | Dominio |
|---|---|---|---|
| GA-01 | WMS on premises sin capacidad de auto-scaling ni HA | Crítico - degradación en Cyber Days, USD 1.1M penalidades | Almacén |
| GA-02 | Orquestador sin backpressure por cliente ni prioridad SLA | Crítico - cola sin control ante degradación WMS | Recepción |
| GA-03 | Optimizador de rutas en batch, no tiempo real | Alto - rutas inviables por datos de tráfico desactualizados | Transporte |
| GA-04 | App conductores con offline frágil y evidencias que se pierden | Alto - disputas de liquidación, reclamos de custodia | Última Milla |
| GA-05 | Sin bus de eventos central, integraciones punto a punto | Alto - fragilidad, inconsistencia, difícil mantener | Todos |
| GA-06 | Liquidación con Excel VBA (APP-26) sin control | Crítico - errores manuales, penalidades mal calculadas | Liquidación |
| GA-07 | Sin plataforma de observabilidad unificada cross-cloud | Alto - sin visibilidad end-to-end, detección tardía de fallos | Todos |

### 2.4 Gaps de Tecnología

| ID Gap | Descripción | Impacto | Dominio |
|---|---|---|---|
| GT-01 | WMS sobre SQL Server 2016 on premises (fin de soporte extendido) | Crítico - vulnerabilidades de seguridad, sin escalabilidad | Almacén |
| GT-02 | Sin IaC para infraestructura actual | Alto - cambios manuales, no reproducibles, riesgo en campaña | Todos |
| GT-03 | Sin seguridad Zero Trust ni Security by Design | Alto - APIs expuestas, datos personales en riesgo | Seguridad |
| GT-04 | Sin conexión privada entre nubes (tráfico por Internet público) | Medio - latencia variable, costos de egress, riesgo seguridad | Multinube |
| GT-05 | Sin estrategia de disaster recovery definida para sistemas críticos | Alto - RTO/RPO indefinidos para WMS y TMS | Resiliencia |

---

## 3. Iniciativas / Proyectos

### Iniciativa 1: Plataforma de Integración por Eventos (Bus Central)
**Descripción**: Implementar un bus de eventos central (Apache Kafka / Azure Event Hubs) que reemplace las integraciones punto a punto entre WMS, TMS, App Conductores y sistemas analíticos.
**Gaps que cierra**: GA-05, GD-01, GD-03, GD-04, GT-02
**Valor**: Elimina integraciones frágiles, habilita modelo canónico de estados, permite replay de eventos.
**Complejidad**: Alta
**Duración estimada**: 6-9 meses

### Iniciativa 2: Modernización del WMS (Cloud-Ready)
**Descripción**: Migrar o modernizar el WMS on premises a una plataforma cloud con auto-scaling, modo degradado automático y sincronización en tiempo real.
**Gaps que cierra**: GA-01, GD-02, GT-01, GT-05
**Valor**: Elimina el principal punto de falla en campañas, evita USD 1.1M+ en penalidades.
**Complejidad**: Muy Alta
**Duración estimada**: 9-12 meses

### Iniciativa 3: App de Conductores Resiliente (Offline Robusto + Evidencias)
**Descripción**: Rediseñar el módulo offline de la app de conductores con SQLite cifrado, sincronización atómica de evidencias, taxonomía normalizada de excepciones y gestión de MDM.
**Gaps que cierra**: GA-04, GD-03, GN-02
**Valor**: Elimina pérdida de evidencias, normaliza datos de excepciones para ML.
**Complejidad**: Media
**Duración estimada**: 3-4 meses

### Iniciativa 4: Optimizador de Rutas en Tiempo Real
**Descripción**: Migrar el optimizador de rutas de batch a streaming usando GKE + Cloud Pub/Sub con datos de tráfico en tiempo real y re-optimización dinámica durante la jornada.
**Gaps que cierra**: GA-03, GN-06, GD-05
**Valor**: Reduce 17% rutas manuales, mejora cumplimiento SLA, ahorro en combustible.
**Complejidad**: Alta
**Duración estimada**: 6-8 meses

### Iniciativa 5: Automatización de Liquidación y Conciliación
**Descripción**: Reemplazar el proceso manual de liquidación (Excel VBA) con un microservicio de liquidación que concilia automáticamente WMS, TMS, App y ERP en tiempo real.
**Gaps que cierra**: GA-06, GN-04, GD-04
**Valor**: Reduce conciliación de 23 días a <1 día, elimina USD 2.4M de disputas.
**Complejidad**: Alta
**Duración estimada**: 5-7 meses

### Iniciativa 6: Validación Integral de Órdenes y Pre-Entrega
**Descripción**: Implementar servicio de validación en tiempo real (dirección, SKU, duplicados, SLA) y comunicación proactiva con destinatario antes de salir a ruta.
**Gaps que cierra**: GN-01, GN-03, GD-01
**Valor**: Reducir entregas fallidas de 12.5% a 7%, ahorro en reintentos (USD 1.2-2.8/intento × 8,500/día).
**Complejidad**: Media
**Duración estimada**: 3-5 meses

### Iniciativa 7: Observabilidad y Seguridad Unificada
**Descripción**: Implementar plataforma de observabilidad cross-cloud (Datadog + OpenTelemetry) y modelo de seguridad Zero Trust (Azure AD, WAF, SIEM, DLP, IaC con Terraform).
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
• WMS on premises SQL Server
• Integraciones punto a punto
• Optimizador batch semanal/diario
• App offline frágil
• Liquidación en Excel
• Sin observabilidad unificada

         │
         ▼

TRANSICIÓN 1 (Año 1 - primeros 12 meses):
────────────────────────────────────────────────
• Bus de eventos central (Kafka/Event Hubs) operativo
• Orquestador con backpressure y circuit breakers
• App conductores rediseñada (offline robusto + taxonomía)
• Servicio de validación de órdenes
• IaC con Terraform para infraestructura cloud
• Observabilidad básica unificada (logs + métricas)
• WMS en modo "puente": API sobre WMS on-prem (no migrado aún)

         │
         ▼

TRANSICIÓN 2 (Año 2 - meses 12-24):
────────────────────────────────────────────────
• WMS modernizado en cloud (migración completada)
• Optimizador de rutas en tiempo real (GKE + Pub/Sub)
• Servicio de Liquidación automatizado (reemplaza Excel)
• Comunicación proactiva con destinatarios
• Seguridad Zero Trust implementada
• Analítica en streaming (BigQuery + Dataflow)
• ERP integrado en tiempo real vía API

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
│ WMS On-P.  │     │ Bus Eventos +      │     │ WMS Cloud +        │     │ Platform │
│ Batch RT   │     │ App Driver v2 +    │     │ Optimizador RT +   │     │ Digital  │
│ Integ P2P  │     │ Validación +       │     │ Liquidación Auto + │     │ Completa │
│ Excel VBA  │     │ IaC + Observab.    │     │ Zero Trust +       │     │          │
│            │     │                    │     │ Analítica Stream.  │     │          │
└────────────┘     └────────────────────┘     └────────────────────┘     └──────────┘
   Hoy             Año 1 (mes 12)              Año 2 (mes 24)             Año 3 (mes 36)
```

---

## 5. Priorización de Iniciativas (Valor vs Esfuerzo)

```
ALTO VALOR / BAJO ESFUERZO (Quick Wins):
  ► INI-03: App Conductores Resiliente (3-4 meses, impacto inmediato en evidencias)
  ► INI-06: Validación Órdenes + Pre-Entrega (3-5 meses, reduce fallas inmediatamente)

ALTO VALOR / ALTO ESFUERZO (Apuestas Estratégicas):
  ► INI-01: Bus de Eventos Central (fundamento de toda la arquitectura TO BE)
  ► INI-02: Modernización WMS (elimina principal punto de falla)
  ► INI-04: Optimizador Tiempo Real (diferenciación competitiva)
  ► INI-05: Automatización Liquidación (recupera millones en disputas)

MEDIO VALOR / MEDIO ESFUERZO (Necesarios):
  ► INI-07: Observabilidad y Seguridad (habilitador transversal)
```

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
