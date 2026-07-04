# ADM - Fase F: Migration Planning
## RutaExpress Fulfillment & Transporte

> **Para el comité de arquitectura** — **Plan de migración 36 meses**: costos (USD 1.53M), roadmap, dependencias y ROI (~4.6x). **Mensaje clave:** arrancar **INI-07** (**PLT-01**, **PLT-02**, **PLT-04**) e **INI-01** (**PLT-03**) en mes 1; quick wins **INI-03** (**APP-15**) e **INI-06** (Servicio de Validación de Órdenes — reemplaza **APP-05**) en meses 2–6.

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

### INI-01: PLT-03 Bus de Eventos Central
**Prioridad**: 1 (Fundacional)
**Duración**: 6 meses
**Equipo**: 2 arquitectos + 4 ingenieros backend + 1 DevOps
**Alcance**:
- Desplegar **PLT-03** con **Azure Event Hubs** (hub central en Azure)
- Migrar integración **APP-06** WMS Principal (On Premises) → **APP-11** TMS (Transportation Management) a eventos
- Migrar integración **APP-11** TMS (Transportation Management) → **APP-15** App de Conductores a eventos
- Implementar modelo canónico de estados de pedido
- Replay y auditoría de eventos

| Componente de Costo | Estimación Mensual | 6 meses |
|---|---|---|
| Azure Event Hubs (Premium) | USD 800/mes | USD 4,800 |
| Azure AKS (nodos adicionales) | USD 1,200/mes | USD 7,200 |
| Equipo desarrollo (7 personas) | USD 35,000/mes | USD 210,000 |
| Infraestructura adicional (staging, monitoring) | USD 500/mes | USD 3,000 |
| **TOTAL INI-01** | | **USD 225,000** |

**Beneficios que aporta:**
- Integración desacoplada: nuevos sistemas se conectan al bus sin tocar WMS (APP-06) ni TMS (APP-11).
- Estados canónicos visibles al cliente en Portal B2B (Trazabilidad) (APP-18) y App de Conductores (APP-15).
- Replay y auditoría de eventos para resolver disputas y reconstruir historial.
- Habilita WMS Cloud, liquidación automática y analítica en streaming.

**ROI esperado**: Reducción de incidentes de integración. Habilita todas las iniciativas siguientes.

---

### INI-02: WMS Cloud — reemplaza APP-06 / APP-07
**Prioridad**: 2 (Crítica)
**Duración**: 10 meses
**Equipo**: 1 arquitecto senior + 5 ingenieros + 1 DBA + 1 DevOps + consultoría WMS
**Alcance**:
- Implementar **WMS Cloud custom** en **Azure AKS + Azure SQL Managed Instance** (sin COTS de licencia elevada)
- Migración datos históricos (ETL)
- Implementación HA multi-zona en Azure
- Auto-scaling horizontal con KEDA
- Modo degradado automático con reconciliación
- Integración vía Event Hub (reemplaza integración directa)
- Migración por fases: 1 CD piloto → 3 CDs → todos los 14 CDs

| Componente de Costo | Estimación | Total |
|---|---|---|
| Azure AKS + Azure SQL Managed Instance | USD 3,500/mes | USD 35,000 (10m) |
| Equipo desarrollo + consultoría (8 personas) | USD 45,000/mes | USD 450,000 (10m) |
| Migración de datos y testing | USD 30,000 (one-time) | USD 30,000 |
| Capacitación operadores almacén | USD 20,000 (one-time) | USD 20,000 |
| **TOTAL INI-02** | | **USD 535,000** |

**Beneficios que aporta:**
- Auto-scaling que absorbe picos 3× sin caídas de 6 h en campañas.
- Inventario único en tiempo real entre los 14 centros de distribución.
- Modo degradado con reconciliación automática al reconectar.
- DR multi-zona con RTO/RPO definidos.

**ROI esperado**: Evitar USD 1.1M en penalidades solo en próximo Cyber Days. Payback < 1 año.

---

### INI-03: APP-15 App de Conductores Resiliente
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

**Beneficios que aporta:**
- Cero pérdida de firmas, fotos y GPS aunque el conductor cambie de equipo.
- Elimina disputas de custodia y cobros retenidos por evidencias faltantes.
- Taxonomía de excepciones lista para entrenar ML / Optimización de Rutas (GCP) (APP-24).
- Conductores operan con confianza en zonas sin señal 4G.

**ROI esperado**: Eliminar disputas por evidencias (1,200 firmas perdidas = ~USD 180K retenidos en 1 incidente). Datos de excepciones limpios para ML.

---

### INI-04: APP-12 Optimizador de Rutas en Tiempo Real
**Prioridad**: 4 (Estratégica)
**Duración**: 7 meses
**Equipo**: 1 arquitecto + 2 ingenieros ML + 2 ingenieros backend + 1 DevOps
**Alcance**:
- Migración de GCE batch a GKE Autopilot
- Integración con Google Cloud Pub/Sub para datos de tráfico en tiempo real
- Re-optimización dinámica durante jornada (cada 30 min o ante evento crítico)
- Integración con **APP-11** TMS (Transportation Management) vía **PLT-03** Event Hub
- Dashboard de rutas en tiempo real para planners

| Componente de Costo | Estimación | Total |
|---|---|---|
| GKE Autopilot | USD 1,500/mes | USD 10,500 (7m) |
| Cloud Pub/Sub + Google Maps Platform | USD 2,000/mes | USD 14,000 (7m) |
| Equipo desarrollo (6 personas) | USD 30,000/mes | USD 210,000 (7m) |
| Datos de tráfico histórico y entrenamiento | USD 15,000 one-time | USD 15,000 |
| **TOTAL INI-04** | | **USD 249,500** |

**Beneficios que aporta:**
- Re-optimización dinámica con tráfico y excepciones actualizados cada 30 min.
- Menos correcciones manuales del 17% de rutas que hoy arreglan los planners.
- Dashboard en tiempo real para supervisión de rutas activas.
- Mejor cumplimiento de ventanas de entrega SLA.

**ROI esperado**: Reducir 17% rutas manuales → ahorro en combustible y tiempo. Meta: -15% costo por entrega = USD 2M+/año en volumen de 68K entregas.

---

### INI-05: Liquidación automatizada — reemplaza APP-26
**Prioridad**: 5 (Alto Impacto Financiero)
**Duración**: 6 meses
**Equipo**: 1 arquitecto + 3 ingenieros backend + 1 analista de negocio + 1 QA
**Alcance**:
- Microservicio de Liquidación (**.NET 8 en Azure AKS** + Azure SQL Database)
- Integración con Event Store para estados de pedido
- Reglas de negocio (reemplaza **APP-26** Sistema de Liquidación Excel)
- API conciliación con **APP-25** ERP Financiero (On Premises)
- Portal de conciliación para clientes (reemplaza proceso manual 23 días)
- Alertas automáticas ante diferencias

| Componente de Costo | Estimación | Total |
|---|---|---|
| Azure AKS + Azure SQL | USD 1,000/mes | USD 6,000 (6m) |
| Equipo desarrollo + analista (6 personas) | USD 28,000/mes | USD 168,000 (6m) |
| Integración ERP (consultoría de integración) | USD 40,000 one-time | USD 40,000 |
| Testing y validación financiera | USD 15,000 one-time | USD 15,000 |
| **TOTAL INI-05** | | **USD 229,000** |

**Beneficios que aporta:**
- Conciliación de 23 días a menos de 1 día entre operación y facturación.
- Penalidades y tarifas calculadas automáticamente, sin Excel ni errores manuales.
- Portal de conciliación B2B alineado al ERP Financiero (On Premises) (APP-25).
- Finanzas liberadas de trabajo manual repetitivo.

**ROI esperado**: Recuperar USD 2.4M retenidos por un solo cliente. Reducir 7% facturas observadas a <1.5%. Payback inmediato.

---

### INI-06: Servicio de Validación de Órdenes (reemplaza APP-05) + Orquestador de Pedidos (APP-02)
**Prioridad**: 6 (Quick Win)
**Duración**: 4 meses
**Equipo**: 1 arquitecto + 2 ingenieros backend + 1 QA
**Alcance**:
- **Servicio de Validación de Órdenes** (NUEVO en Cloud MS Azure (EEUU)) — reemplaza Validador de Pedidos (APP-05), que se **elimina** en TO BE F1
- Validación en tiempo real (dirección geo-validada, SKU existente, deduplicación hash)
- Integración con API de geocodificación (**Google Maps Platform**)
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

**Beneficios que aporta:**
- Dirección, SKU y duplicados validados antes de reservar inventario.
- Ventana horaria confirmada con destinatario vía Servicio de Notificación (SMS/Email) (APP-21).
- Evita incidentes masivos de pedidos duplicados.
- Menos entregas fallidas por dirección incorrecta o ausencia del destinatario.

**ROI esperado**: Reducir entregas fallidas del 34% de causas prevenibles. Ahorro en reintentos: 8,500 fallas/día × 34% × USD 1.50 × 365 = USD 1.58M/año.

---

### INI-07: PLT-01 Plataforma de Observabilidad Unificada + PLT-02 Plataforma de Identidad y Accesos (IAM) + PLT-04 Plataforma IaC
**Prioridad**: 7 (Habilitador Transversal)
**Duración**: 5 meses (en paralelo con otras iniciativas)
**Equipo**: 1 arquitecto seguridad + 2 ingenieros DevSecOps + 1 SRE
**Alcance** (alineado con doc `10`, servicios nativos, alcance medio):
- **Azure Monitor + Application Insights** + Amazon CloudWatch + Google Cloud Logging (PLT-01)
- **Terraform** para toda la infraestructura cloud (PLT-04)
- Microsoft Entra ID + MFA + Azure Key Vault + WAF en **APP-01** Azure API Management (PLT-02)
- Conectividad entre nubes: **VPN site-to-site cifrada (Azure VPN Gateway)**

| Componente de Costo | Estimación | Total |
|---|---|---|
| Azure Monitor + Application Insights + CloudWatch export | USD 800/mes | USD 4,000 (5m) |
| Entra ID + Key Vault + WAF (setup) | USD 1,500/mes | USD 7,500 (5m) |
| Azure VPN Gateway (site-to-site) | USD 300/mes | USD 1,500 (5m) |
| Equipo DevSecOps (4 personas) | USD 20,000/mes | USD 100,000 (5m) |
| Terraform repos + pipelines CI | USD 10,000 one-time | USD 10,000 |
| **TOTAL INI-07** | | **USD 123,000** |

**Beneficios que aporta:**
- Tablero central con métricas, logs y trazas de Azure, AWS y GCP.
- Alertas automáticas antes de que un fallo escale a indisponibilidad de campaña.
- MFA, WAF y Entra ID central refuerzan acceso a APIs y datos personales.
- Terraform y VPN site-to-site: despliegues reproducibles y conectividad cifrada a bajo costo.

**ROI esperado**: Detección temprana de incidentes, menor tiempo de recuperación y base segura para el resto de iniciativas.

---

## 4. Resumen de Costos por Iniciativa

| Iniciativa | Duración | Costo Estimado | Prioridad |
|---|---|---|---|
| INI-01: Bus de Eventos Central (PLT-03) | 6 meses | USD 225,000 | 1 (Fundacional) |
| INI-02: WMS Cloud (reemplaza WMS Principal (On Premises) (APP-06) / WMS Satélite (On Premises local) (APP-07)) | 10 meses | USD 535,000 | 2 (Crítica) |
| INI-03: App de Conductores (APP-15) | 4 meses | USD 105,800 | 3 (Quick Win) |
| INI-04: Optimizador de Rutas en Tiempo Real (reemplaza APP-12) | 7 meses | USD 249,500 | 4 (Estratégica) |
| INI-05: Servicio de Liquidación (reemplaza Sistema de Liquidación (Excel) (APP-26)) | 6 meses | USD 229,000 | 5 (Alto Impacto) |
| INI-06: Servicio de Validación de Órdenes (reemplaza Validador de Pedidos (APP-05)) | 4 meses | USD 66,000 | 6 (Quick Win) |
| INI-07: Plataforma de Observabilidad Unificada (PLT-01) + Plataforma de Identidad y Accesos (IAM) (PLT-02) + Plataforma IaC (PLT-04) | 5 meses | USD 123,000 | 7 (Habilitador) |
| **TOTAL TRANSFORMACIÓN** | **36 meses** | **USD 1,533,300** | |

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
| H1 | Mes 3 | **PLT-03** Bus de Eventos Central operativo (piloto WMS Principal (On Premises) (APP-06) ↔ TMS (Transportation Management) (APP-11)) | Integración desacoplada WMS Principal ↔ TMS |
| H2 | Mes 5 | **APP-15** v2 en producción | 0 pérdidas de evidencias |
| H3 | Mes 6 | Validación órdenes y pre-entrega activos | Defectos <3%, -20% fallas |
| H4 | Mes 6 | **PLT-03** completo (todas las integraciones) | Estados consistentes |
| H5 | Mes 10 | Liquidación automatizada en producción | Conciliación <3 días |
| H6 | Mes 12 | WMS Cloud + Optimizador de Rutas en Tiempo Real (APP-12) | Disponibilidad 98% campaña |
| H7 | Mes 12 | **Transición 1 completa** | 91% cumplimiento promesa |
| H8 | Mes 24 | **Transición 2 completa** | 93% cumplimiento, 99.5% disponib. |
| H9 | Mes 36 | **TO BE completo** | 94%, 99.9%, 98% tracking |

---

## 6. Análisis de Dependencias

```
INI-07 (**PLT-01**, **PLT-02**, **PLT-04**) ──► Todas las iniciativas
INI-01 (**PLT-03**) ──► INI-02, INI-04, INI-05
INI-03 (**APP-15**) ──► INI-05
INI-02 (WMS Cloud) ──► INI-04 (**APP-12** RT)
```

---

## 7. Gestión de Riesgos del Plan de Migración

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Resistencia al cambio en almacenes (WMS nuevo) | Alta | Alto | Plan de change management, capacitación, piloto en 1 CD |
| Migración WMS más larga de lo esperado | Media | Alto | Modo puente: API sobre WMS Principal (On Premises) (APP-06) durante transición a WMS Cloud |
| Clientes que no actualizan sus integraciones | Media | Medio | Backward-compatibility garantizada 18 meses |
| Costo real superior al estimado (desarrollo WMS custom) | Media | Alto | Reserva de contingencia 20% del presupuesto |
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
| **Inversión total transformación** | **USD 1,533,300** |
| **ROI** | **~4.6x** |

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
