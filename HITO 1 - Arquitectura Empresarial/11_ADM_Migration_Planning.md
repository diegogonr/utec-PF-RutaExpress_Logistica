# ADM - Fase F: Migration Planning
## RutaExpress Fulfillment & Transporte

---

## 1. Propósito

Definir el plan de migración para llevar la arquitectura desde el estado AS IS al TO BE, con estimaciones de tiempo, costo y priorización de iniciativas según el valor que generan al negocio. Incluye el roadmap de implementación con dependencias entre iniciativas.

---

## 2. Iniciativas Priorizadas

### Criterios de Priorización

| Criterio | Peso |
|---|---|
| Impacto en reducción de penalidades / ingresos | 30% |
| Reducción de riesgo operativo (disponibilidad, integridad) | 25% |
| Habilitador de otras iniciativas | 20% |
| Velocidad de entrega de valor (time-to-value) | 15% |
| Complejidad / Riesgo de implementación | 10% |

---

## 3. Fichas de Iniciativas con Estimación

### INI-01: Plataforma de Integración por Eventos (Bus Central)
**Prioridad**: 1 (Fundacional)
**Duración**: 6 meses
**Equipo**: 2 arquitectos + 4 ingenieros backend + 1 DevOps
**Alcance**:
- Desplegar Apache Kafka / Azure Event Hubs
- Migrar integración WMS → TMS a eventos
- Migrar integración TMS → App Conductores a eventos
- Implementar modelo canónico de estados de pedido
- Replay y auditoría de eventos

| Componente de Costo | Estimación Mensual | 6 meses |
|---|---|---|
| Azure Event Hubs (Premium) | USD 800/mes | USD 4,800 |
| Azure AKS (nodos adicionales) | USD 1,200/mes | USD 7,200 |
| Equipo desarrollo (7 personas) | USD 35,000/mes | USD 210,000 |
| Infraestructura adicional (staging, monitoring) | USD 500/mes | USD 3,000 |
| **TOTAL INI-01** | | **USD 225,000** |

**ROI esperado**: Reducción de incidentes de integración. Habilita todas las iniciativas siguientes.

---

### INI-02: Modernización del WMS (Cloud-Ready)
**Prioridad**: 2 (Crítica)
**Duración**: 10 meses
**Equipo**: 1 arquitecto senior + 5 ingenieros + 1 DBA + 1 DevOps + consultoría WMS
**Alcance**:
- Evaluación y selección de WMS cloud (Blue Yonder, Manhattan, o modernización custom)
- Migración datos históricos (ETL)
- Implementación HA multi-zona en Azure
- Auto-scaling horizontal con KEDA
- Modo degradado automático con reconciliación
- Integración vía Event Hub (reemplaza integración directa)
- Migración por fases: 1 CD piloto → 3 CDs → todos los 14 CDs

| Componente de Costo | Estimación | Total |
|---|---|---|
| Licencia WMS cloud (si aplica COTS) | USD 15,000/mes | USD 150,000 (10m) |
| Azure AKS + Azure SQL Managed Instance | USD 3,500/mes | USD 35,000 (10m) |
| Equipo desarrollo + consultoría (8 personas) | USD 45,000/mes | USD 450,000 (10m) |
| Migración de datos y testing | USD 30,000 (one-time) | USD 30,000 |
| Capacitación operadores almacén | USD 20,000 (one-time) | USD 20,000 |
| **TOTAL INI-02** | | **USD 685,000** |

**ROI esperado**: Evitar USD 1.1M en penalidades solo en próximo Cyber Days. Payback < 1 año.

---

### INI-03: App de Conductores Resiliente
**Prioridad**: 3 (Quick Win)
**Duración**: 4 meses
**Equipo**: 1 arquitecto + 3 ingenieros mobile/backend + 1 QA
**Alcance**:
- Rediseño módulo offline (SQLite cifrado AES-256)
- Sincronización atómica de evidencias (foto + firma + GPS + timestamp)
- Retry robusto con preservación de evidencias ante reinstalación/cambio de equipo
- Taxonomía normalizada de motivos de excepción (obligatoria)
- MDM (Mobile Device Management) para gestión de dispositivos
- Integración con Kinesis para eventos en tiempo real

| Componente de Costo | Estimación | Total |
|---|---|---|
| AWS ECS Fargate (backend) | USD 800/mes | USD 3,200 (4m) |
| AWS Kinesis Data Streams | USD 400/mes | USD 1,600 (4m) |
| Equipo desarrollo (5 personas) | USD 22,000/mes | USD 88,000 (4m) |
| MDM (licencias y setup) | USD 5,000 one-time | USD 5,000 |
| Testing y QA (campo) | USD 8,000 one-time | USD 8,000 |
| **TOTAL INI-03** | | **USD 105,800** |

**ROI esperado**: Eliminar disputas por evidencias (1,200 firmas perdidas = ~USD 180K retenidos en 1 incidente). Datos de excepciones limpios para ML.

---

### INI-04: Optimizador de Rutas en Tiempo Real
**Prioridad**: 4 (Estratégica)
**Duración**: 7 meses
**Equipo**: 1 arquitecto + 2 ingenieros ML + 2 ingenieros backend + 1 DevOps
**Alcance**:
- Migración de GCE batch a GKE Autopilot
- Integración con Google Cloud Pub/Sub para datos de tráfico en tiempo real
- Re-optimización dinámica durante jornada (cada 30 min o ante evento crítico)
- Integración con TMS vía Event Hub
- Dashboard de rutas en tiempo real para planners

| Componente de Costo | Estimación | Total |
|---|---|---|
| GKE Autopilot | USD 1,500/mes | USD 10,500 (7m) |
| Cloud Pub/Sub + Google Maps Platform | USD 2,000/mes | USD 14,000 (7m) |
| Equipo desarrollo (6 personas) | USD 30,000/mes | USD 210,000 (7m) |
| Datos de tráfico histórico y entrenamiento | USD 15,000 one-time | USD 15,000 |
| **TOTAL INI-04** | | **USD 249,500** |

**ROI esperado**: Reducir 17% rutas manuales → ahorro en combustible y tiempo. Meta: -15% costo por entrega = USD 2M+/año en volumen de 68K entregas.

---

### INI-05: Automatización de Liquidación y Conciliación
**Prioridad**: 5 (Alto Impacto Financiero)
**Duración**: 6 meses
**Equipo**: 1 arquitecto + 3 ingenieros backend + 1 analista de negocio + 1 QA
**Alcance**:
- Microservicio de Liquidación (.NET 8 / Java en Azure AKS)
- Integración con Event Store para estados de pedido
- Reglas de negocio de penalidades y bonificaciones (reemplaza Excel VBA)
- API de conciliación para integración con ERP (SAP/ABAP)
- Portal de conciliación para clientes (reemplaza proceso manual 23 días)
- Alertas automáticas ante diferencias

| Componente de Costo | Estimación | Total |
|---|---|---|
| Azure AKS + Azure SQL | USD 1,000/mes | USD 6,000 (6m) |
| Equipo desarrollo + analista (6 personas) | USD 28,000/mes | USD 168,000 (6m) |
| Integración ERP (consultoría SAP) | USD 40,000 one-time | USD 40,000 |
| Testing y validación financiera | USD 15,000 one-time | USD 15,000 |
| **TOTAL INI-05** | | **USD 229,000** |

**ROI esperado**: Recuperar USD 2.4M retenidos por un solo cliente. Reducir 7% facturas observadas a <1.5%. Payback inmediato.

---

### INI-06: Validación de Órdenes y Pre-Entrega
**Prioridad**: 6 (Quick Win)
**Duración**: 4 meses
**Equipo**: 1 arquitecto + 2 ingenieros backend + 1 QA
**Alcance**:
- Servicio de validación en tiempo real (dirección geo-validada, SKU existente, deduplicación hash)
- Integración con API de geocodificación (Google Maps / HERE)
- Comunicación proactiva con destinatario (WhatsApp/SMS/email antes de la entrega)
- Confirmación de ventana horaria con el destinatario
- Dashboard de órdenes con defectos para mesa B2B

| Componente de Costo | Estimación | Total |
|---|---|---|
| Azure AKS (servicio validación) | USD 500/mes | USD 2,000 (4m) |
| APIs geocodificación (Google Maps) | USD 1,200/mes | USD 4,800 (4m) |
| Plataforma notificaciones (WhatsApp Business API) | USD 800/mes | USD 3,200 (4m) |
| Equipo desarrollo (3 personas) | USD 14,000/mes | USD 56,000 (4m) |
| **TOTAL INI-06** | | **USD 66,000** |

**ROI esperado**: Reducir entregas fallidas del 34% de causas prevenibles. Ahorro en reintentos: 8,500 fallas/día × 34% × USD 1.50 × 365 = USD 1.58M/año.

---

### INI-07: Observabilidad y Seguridad Unificada
**Prioridad**: 7 (Habilitador Transversal)
**Duración**: 5 meses (en paralelo con otras iniciativas)
**Equipo**: 1 arquitecto seguridad + 2 ingenieros DevSecOps + 1 SRE
**Alcance**:
- Datadog o Azure Monitor + OpenTelemetry (trazas distribuidas cross-cloud)
- Terraform para toda la infraestructura cloud (IaC)
- Azure AD B2C para identidad de clientes externos
- WAF en Azure API Management
- SIEM centralizado (Azure Sentinel)
- DLP para datos personales de destinatarios
- Conexiones privadas entre nubes (ExpressRoute + Direct Connect)

| Componente de Costo | Estimación | Total |
|---|---|---|
| Datadog Pro (cross-cloud) | USD 3,000/mes | USD 15,000 (5m) |
| Azure Sentinel + Defender | USD 1,500/mes | USD 7,500 (5m) |
| ExpressRoute + AWS Direct Connect | USD 2,000/mes | USD 10,000 (5m) |
| Equipo DevSecOps (4 personas) | USD 20,000/mes | USD 100,000 (5m) |
| Licencias y setup WAF, DLP | USD 10,000 one-time | USD 10,000 |
| **TOTAL INI-07** | | **USD 142,500** |

---

## 4. Resumen de Costos por Iniciativa

| Iniciativa | Duración | Costo Estimado | Prioridad |
|---|---|---|---|
| INI-01: Bus de Eventos Central | 6 meses | USD 225,000 | 1 (Fundacional) |
| INI-02: Modernización WMS | 10 meses | USD 685,000 | 2 (Crítica) |
| INI-03: App Conductores Resiliente | 4 meses | USD 105,800 | 3 (Quick Win) |
| INI-04: Optimizador RT | 7 meses | USD 249,500 | 4 (Estratégica) |
| INI-05: Liquidación Automatizada | 6 meses | USD 229,000 | 5 (Alto Impacto) |
| INI-06: Validación Órdenes + Pre-Entrega | 4 meses | USD 66,000 | 6 (Quick Win) |
| INI-07: Observabilidad y Seguridad | 5 meses | USD 142,500 | 7 (Habilitador) |
| **TOTAL TRANSFORMACIÓN** | **36 meses** | **USD 1,702,800** | |

**Nota**: Costos operativos recurrentes de infraestructura cloud no incluidos en el estimado de proyecto (se incorporan al presupuesto operativo de TI).

---

## 5. Roadmap de Implementación

```
MES:    1    2    3    4    5    6    7    8    9    10   11   12
        │    │    │    │    │    │    │    │    │    │    │    │
INI-07  ████████████████████████████████████                        (Paralelo desde M1)
INI-01  ████████████████████████████████████████████               (M1-M6)
INI-03       ████████████████████████████████                      (M2-M5, Quick Win)
INI-06            ████████████████████████████                     (M3-M6, Quick Win)
INI-02                 ████████████████████████████████████████████ (M4-M13)
INI-05                      ████████████████████████████████       (M5-M10)
INI-04                           ███████████████████████████████   (M6-M12)

MES:    13   14   15   16   17   18   19   20   21   22   23   24
        │    │    │    │    │    │    │    │    │    │    │    │
INI-02  ████                                                        (Finaliza M13)
        [TRANSICIÓN 1 COMPLETA - Fin mes 12]
        [TRANSICIÓN 2 INICIA]
        Ajustes, estabilización, ML predictivo                    ████████████████

MES:    25   26   27   28   29   30   31   32   33   34   35   36
        [TO BE COMPLETO - Fin mes 36]
        KPIs objetivo: 94% cumplimiento, 99.9% disponibilidad, 98% trazabilidad
```

### Hitos del Roadmap

| Hito | Mes | Descripción | KPI Esperado |
|---|---|---|---|
| H1 | Mes 3 | Bus de eventos operativo (Piloto WMS-TMS) | Integración desacoplada WMS↔TMS |
| H2 | Mes 5 | App conductores v2 en producción | 0 pérdidas de evidencias |
| H3 | Mes 6 | Validación órdenes y pre-entrega activos | Defectos <3%, -20% fallas |
| H4 | Mes 6 | Bus de eventos completo (todas las integraciones) | Estados consistentes |
| H5 | Mes 10 | Liquidación automatizada en producción | Conciliación <3 días |
| H6 | Mes 12 | WMS cloud (14 CDs migrados) + Optimizador RT | Disponibilidad 98% campaña |
| H7 | Mes 12 | **Transición 1 completa** | 91% cumplimiento promesa |
| H8 | Mes 24 | **Transición 2 completa** | 93% cumplimiento, 99.5% disponib. |
| H9 | Mes 36 | **TO BE completo** | 94%, 99.9%, 98% tracking |

---

## 6. Análisis de Dependencias

```
INI-07 (Seguridad/Observabilidad) ──────────► Todas las iniciativas (fundamento)
INI-01 (Bus Eventos) ────────────────────────► INI-02, INI-04, INI-05 (habilita integración)
INI-03 (App Conductores) ────────────────────► INI-05 (datos limpios para liquidación)
INI-06 (Validación Órdenes) ─────────────────► INI-05 (menos fallas = liquidación más simple)
INI-02 (WMS Cloud) ──────────────────────────► INI-04 (rutas en RT solo con WMS en RT)
INI-04 (Optimizador RT) ─────────────────────► INI-05 (rutas trazadas correctamente)
```

---

## 7. Gestión de Riesgos del Plan de Migración

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Resistencia al cambio en almacenes (WMS nuevo) | Alta | Alto | Plan de change management, capacitación, piloto en 1 CD |
| Migración WMS más larga de lo esperado | Media | Alto | Modo puente: API sobre WMS legacy durante transición |
| Clientes que no actualizan sus integraciones | Media | Medio | Backward-compatibility garantizada 18 meses |
| Costo real superior al estimado (COTS WMS) | Media | Alto | Reserva de contingencia 20% del presupuesto |
| Disponibilidad del equipo técnico | Baja | Medio | Contratación anticipada + alianza con consultoras |

---

## 8. Beneficios Esperados y ROI

| Beneficio | Valor Anual Estimado |
|---|---|
| Evitar penalidades en campañas | USD 1,100,000+ |
| Reducción entregas fallidas (reintentos) | USD 1,580,000 |
| Recuperación disputas de liquidación | USD 2,400,000 (solo 1 cliente) |
| Reducción costo/entrega (-15%) | USD 2,000,000+ |
| **Beneficio total estimado año 1 post-TO BE** | **USD 7,080,000+** |
| **Inversión total transformación** | **USD 1,702,800** |
| **ROI** | **~4.2x** |

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
