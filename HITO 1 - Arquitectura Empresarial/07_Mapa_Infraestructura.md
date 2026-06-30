# Mapa de Infraestructura
## RutaExpress Fulfillment & Transporte

---

## 1. Propósito

Documentar la infraestructura tecnológica actual (AS IS) y objetivo (TO BE) de RutaExpress, mostrando la topología de nubes, centros de datos y redes que soportan la operación logística.

---

## 2. Infraestructura AS IS

### 2.1 Descripción General

RutaExpress opera en una arquitectura multinube real pero sin estrategia unificada. Cada sistema fue adoptando la plataforma que le convenía en su momento, generando una topología fragmentada con integraciones punto a punto y sin visibilidad centralizada.

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                        INFRAESTRUCTURA AS IS - RUTAEXPRESS                               │
│                                                                                           │
│  ┌─────────────────────────┐   ┌──────────────────────────┐   ┌─────────────────────┐   │
│  │        ON PREMISES       │   │          AZURE           │   │         AWS         │   │
│  │  (Centro Distribución    │   │                          │   │                     │   │
│  │       Central)           │   │  ┌──────────────────┐   │   │  ┌───────────────┐  │   │
│  │                          │   │  │  Azure API Mgmt   │   │   │  │  App Driver   │  │   │
│  │  ┌──────────────────┐   │   │  │  (Entrada APIs)  │   │   │  │  (ECS/EC2)    │  │   │
│  │  │  WMS Principal   │   │   │  └────────┬─────────┘   │   │  └───────┬───────┘  │   │
│  │  │  SQL Server      │◄──┼───┼──────────►│              │   │          │           │   │
│  │  │  (degradación    │   │   │  ┌────────▼─────────┐   │   │  ┌───────▼───────┐  │   │
│  │  │  en campaña)     │   │   │  │  Orquestador     │   │   │  │  DynamoDB     │  │   │
│  │  └──────────────────┘   │   │  │  Pedidos (AKS)   │   │   │  │  (eventos     │  │   │
│  │                          │   │  └────────┬─────────┘   │   │  │  tracking)    │  │   │
│  │  ┌──────────────────┐   │   │  ┌────────▼─────────┐   │   │  └───────────────┘  │   │
│  │  │  WMS Satélites   │   │   │  │  TMS             │   │   │                     │   │
│  │  │  (sync. horaria) │   │   │  │  (Azure VM/      │   │   │  ┌───────────────┐  │   │
│  │  └──────────────────┘   │   │  │  App Service)    │   │   │  │  S3 Evidencias│  │   │
│  │                          │   │  └────────┬─────────┘   │   │  │  (fotos/firmas│  │   │
│  │  ┌──────────────────┐   │   │           │              │   │  └───────────────┘  │   │
│  │  │  ERP Financiero  │   │   └───────────┼──────────────┘   │                     │   │
│  │  │  (on premises)   │   │               │                   │  ┌───────────────┐  │   │
│  │  └──────────────────┘   │               │                   │  │  IoT Core     │  │   │
│  │                          │               │                   │  │  (sensores    │  │   │
│  │  ┌──────────────────┐   │               │                   │  │  temperatura) │  │   │
│  │  │  Manifiestos     │   │               │                   │  └───────────────┘  │   │
│  │  │  Impresión local │   │               │                   │                     │   │
│  │  └──────────────────┘   │               │                   │  ┌───────────────┐  │   │
│  └─────────────────────────┘               │                   │  │  S3 bucket    │  │   │
│                                             │                   │  │  (archivos    │  │   │
│  ┌─────────────────────────────────────────▼────────────────┐  │  │  legacy CSV) │  │   │
│  │                          GCP                              │  │  └───────────────┘  │   │
│  │  ┌──────────────────────────────────────────────────┐    │  └─────────────────────┘   │
│  │  │  Optimizador de Rutas (batch - GCP)              │    │                            │
│  │  │  Analítica (batch semanal - GCP)                 │    │  ┌─────────────────────┐   │
│  │  │  ML / Algoritmo de Rutas (GCP)                   │    │  │  SAAS EXTERNOS      │   │
│  │  └──────────────────────────────────────────────────┘    │  │  • Portal Clientes  │   │
│  └───────────────────────────────────────────────────────────┘  │  • Portal Tracking  │   │
│                                                                   │  • CRM Atención     │   │
│  ┌──────────────────────────────────────────────────────────┐   │  • Pagos (POS)      │   │
│  │              REDES DE ALMACENES (14 CDs)                 │   │  • Notificaciones   │   │
│  │  Wi-Fi interno para handhelds + Red local para WMS sat.  │   └─────────────────────┘   │
│  └──────────────────────────────────────────────────────────┘                             │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Problemas de Infraestructura AS IS

| Componente | Problema | Impacto |
|---|---|---|
| WMS on premises | Sin capacidad de auto-scaling | Se degrada en campañas (Cyber Days: 6h caído) |
| WMS Satélites | Sincronización horaria por lotes | 4,900 movimientos en conflicto en una sola desconexión |
| Integraciones multinube | Punto a punto sin bus de eventos | Datos inconsistentes entre sistemas |
| Optimizador GCP | Proceso batch, no tiempo real | Rutas generadas con datos de tráfico desactualizados |
| Analítica GCP | Consolidación semanal | Sin visibilidad operativa en tiempo real |
| ERP on premises | Sin integración en tiempo real | Facturación con datos del mes anterior |
| Red almacenes | Wi-Fi sin redundancia | App conductores pierde conectividad |

---

## 3. Infraestructura TO BE

### 3.1 Principios de Diseño TO BE

- **Cloud-First**: Migrar WMS y ERP a cloud o integrar en tiempo real
- **Auto-scaling**: Todos los servicios críticos con escalado automático
- **Event-Driven**: Bus de eventos central (Kafka/Event Hub) para integración entre nubes
- **Observabilidad**: Plataforma unificada de logs, métricas y trazas
- **Seguridad perimetral**: Zero Trust Network Access para accesos externos y móviles
- **Redundancia multi-zona**: Servicios críticos desplegados en múltiples zonas de disponibilidad

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                        INFRAESTRUCTURA TO BE - RUTAEXPRESS                               │
│                                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐     │
│  │                    CAPA DE INTEGRACIÓN (Event Streaming)                         │     │
│  │         Azure Event Hub / Apache Kafka  ←── Bus Central de Eventos ──►          │     │
│  └───────────────┬─────────────────────────────────────────────┬───────────────────┘     │
│                  │                                               │                         │
│  ┌───────────────▼──────────────┐         ┌────────────────────▼────────────────────┐    │
│  │           AZURE              │         │                  AWS                     │    │
│  │                              │         │                                          │    │
│  │  Azure API Management        │         │  App Conductores (ECS Fargate)           │    │
│  │  (Gateway central)           │         │  Auto-scaling + multi-AZ                 │    │
│  │                              │         │                                          │    │
│  │  Orquestador Pedidos (AKS)   │         │  DynamoDB (eventos tracking)             │    │
│  │  - Auto-scaling Horizontal   │         │  Global Tables para latencia baja        │    │
│  │  - Circuit Breakers          │         │                                          │    │
│  │  - Backpressure por cliente  │         │  S3 Evidencias + Glacier (archivado)     │    │
│  │                              │         │  con cifrado AES-256                     │    │
│  │  TMS (AKS modernizado)       │         │                                          │    │
│  │  - Integración tiempo real   │         │  Kinesis Data Streams                    │    │
│  │    con WMS vía eventos       │         │  (eventos tracking tiempo real)          │    │
│  │                              │         │                                          │    │
│  │  WMS Cloud (Azure o híbrido) │         │  IoT Core (sensores temperatura)         │    │
│  │  - Réplica hot-standby       │         │  con alertas automáticas                 │    │
│  │  - Modo degradado automático │         │                                          │    │
│  └──────────────────────────────┘         └──────────────────────────────────────────┘    │
│                  │                                               │                         │
│  ┌───────────────▼───────────────────────────────────────────────▼────────────────────┐   │
│  │                              GCP                                                    │   │
│  │  Optimizador Rutas (GKE) - TIEMPO REAL  │  BigQuery (Data Lakehouse)              │   │
│  │  Cloud Pub/Sub para eventos de tráfico  │  Herramienta BI / dashboards (GCP)      │   │
│  │  ⚠️ ML predictivo (tecnología a definir │  Dataflow (ETL streaming)               │   │
│  │  en diseño de solución - HITO 2)        │                                         │   │
│  └────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                            │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐   │
│  │           OBSERVABILIDAD UNIFICADA (Cross-Cloud)                                   │   │
│  │  Datadog / New Relic / Azure Monitor + OpenTelemetry                               │   │
│  │  Logs centralizados + Métricas + Trazas distribuidas + Alertas                     │   │
│  └────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                            │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐   │
│  │           SEGURIDAD (Zero Trust)                                                   │   │
│  │  Azure AD B2C (clientes) + OAuth 2.0 (APIs) + VPN/PrivateLink entre nubes         │   │
│  │  WAF en API Gateway + DLP para datos personales + SIEM centralizado                │   │
│  └────────────────────────────────────────────────────────────────────────────────────┘   │
│                                                                                            │
│  ┌────────────────────────────────────────────────────────────────────────────────────┐   │
│  │           ON PREMISES (Reducido - Solo Transición)                                 │   │
│  │  ERP Financiero (integrado vía API con Event Hub)                                  │   │
│  │  WMS Legacy (modo puente durante migración)                                        │   │
│  └────────────────────────────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Infraestructura de Red y Conectividad

### AS IS
| Conexión | Tipo | Problema |
|---|---|---|
| Centros de distribución ↔ WMS central | LAN / WAN privada | Sin redundancia, cortes de 74 min registrados |
| Handhelds ↔ WMS | Wi-Fi interno | Sin failover, dependencia total de conectividad local |
| App conductores ↔ Backend AWS | Internet móvil (4G) | Zonas sin señal → modo offline → eventos fuera de orden |
| Azure ↔ GCP | Internet público | Sin SLA de latencia garantizado |
| Azure ↔ AWS | Internet público | Sin cifrado de tránsito garantizado entre nubes |

### TO BE
| Conexión | Tipo | Mejora |
|---|---|---|
| Centros de distribución ↔ Cloud | SD-WAN + Link redundante | Failover automático en <30 segundos |
| Handhelds ↔ WMS cloud | Wi-Fi con 4G backup | Operación continua ante fallo de Wi-Fi |
| App conductores ↔ Backend AWS | 4G/5G + modo offline robusto | Sincronización cifrada garantizada |
| Azure ↔ GCP | Azure ExpressRoute + Google Interconnect | Baja latencia, alta disponibilidad, cifrado |
| Azure ↔ AWS | Azure ExpressRoute + AWS Direct Connect | Tráfico privado entre nubes |

---

## 5. Capacidades de Infraestructura por Plataforma

| Plataforma | Fortaleza | Uso Estratégico |
|---|---|---|
| Azure | AKS, API Management, Event Hub, AD | Orquestación de pedidos, TMS, integraciones, identidad |
| AWS | ECS, DynamoDB, S3, Kinesis, IoT Core | App conductores, evidencias, tracking, IoT temperatura |
| GCP | BigQuery, GKE, Pub/Sub | Analítica, ML, optimización de rutas en tiempo real |
| On Premises | ERP, WMS legacy | Transición hasta migración completa |

---

## 6. Riesgos de Infraestructura y Mitigación

| Riesgo | Probabilidad | Impacto | Mitigación TO BE |
|---|---|---|---|
| WMS on premises degradado en campaña | Alta | Crítico | Migración a cloud con auto-scaling |
| Pérdida de conectividad en almacenes | Media | Alto | SD-WAN con failover 4G |
| Inconsistencia de datos entre nubes | Alta | Alto | Bus de eventos central con exactly-once |
| Pérdida de evidencias en app móvil | Media | Alto | Cifrado local + retry robusto + MDM |
| Coste de tráfico entre nubes | Media | Medio | PrivateLink / Interconnect entre proveedores |

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
