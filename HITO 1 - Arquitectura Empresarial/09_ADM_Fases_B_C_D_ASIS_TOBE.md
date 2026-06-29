# ADM - Fases B, C y D: AS IS y TO BE con Cadena de Valor
## RutaExpress Fulfillment & Transporte

---

# PARTE 1: CADENA DE VALOR

## Value Stream: Entrega de Pedido Logístico

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                     CADENA DE VALOR - RUTAEXPRESS FULFILLMENT                            │
│                                                                                           │
│  CLIENTE ENVÍA ORDEN                                                CLIENTE RECIBE PAGO  │
│         │                                                                    ▲            │
│         ▼                                                                    │            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │     F1       │  │     F2       │  │     F3       │  │     F4       │  │    F6    │  │
│  │  RECEPCIÓN   │─►│ PREPARACIÓN  │─►│  DESPACHO   │─►│   ENTREGA    │─►│ LIQUIDAC.│  │
│  │  DE ÓRDENES  │  │  DE PEDIDOS  │  │  DE PEDIDOS │  │  DEL PEDIDO  │  │Y DEVOLUC.│  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────┬───────┘  └──────────┘  │
│                                                                  │                        │
│                                                        ┌─────────▼──────────┐            │
│                                                        │        F5          │            │
│                                                        │  GESTIÓN DE        │            │
│                                                        │  EXCEPCIONES       │            │
│                                                        └────────────────────┘            │
└──────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# PARTE 2: FASE B - ARQUITECTURA DE NEGOCIO

## AS IS - Arquitectura de Negocio

### Capacidades de Negocio AS IS

| Capacidad | Descripción | Madurez |
|---|---|---|
| Recepción multi-canal | API, portal, CSV/Excel, SFTP | Media - Canal CSV es deuda |
| Validación de órdenes | Validación básica de SKU y dirección | Baja - 6% órdenes con defectos |
| Gestión de almacén | Picking, packing, control de temperatura | Media - WMS estable pero sin escala |
| Gestión de transporte | Asignación manual + TMS Azure | Baja - 17% rutas modificadas a mano |
| Optimización de rutas | Batch con GCP, no tiempo real | Baja - Datos de tráfico desactualizados |
| Tracking última milla | App móvil conductores + eventos | Baja - 8% eventos con >20 min retraso |
| Gestión de excepciones | Registro en app + CRM | Baja - Sin taxonomía normalizada |
| Liquidación y facturación | ERP on premises + Excel manual | Muy Baja - Conciliación 23 días |
| Atención al cliente | CRM SaaS | Media - Taxonomía desconectada |
| Analítica | Batch semanal GCP | Baja - Sin visibilidad tiempo real |

### Procesos de Negocio AS IS con Problemas

```
F1 RECEPCIÓN:
  API → [Azure APIM] → [Orquestador AKS] → [WMS on-prem]
  CSV/Excel → [Portal SaaS] ──────────────►
  
  PROBLEMA: Deduplicación falla si cambia ID externo
  PROBLEMA: Sin backpressure ante degradación WMS
  PROBLEMA: 6% de órdenes con defectos entran al flujo

F2 PREPARACIÓN:
  [WMS on-prem] → picking → [control calidad] → [WMS]
  Sincronización horaria con almacenes satélite
  
  PROBLEMA: WMS se degrada bajo alta carga
  PROBLEMA: Sincronización horaria genera conflictos
  PROBLEMA: Inventario no disponible en tiempo real para otros sistemas

F3 DESPACHO:
  [WMS] → pedidos liberados → [TMS Azure] → [Optimizador GCP batch] → [App Conductores AWS]
  
  PROBLEMA: Optimizador batch recibe datos de tráfico tarde
  PROBLEMA: Rutas generadas sin todos los paquetes confirmados (WMS lento)
  PROBLEMA: 17% rutas corregidas manualmente sin trazabilidad

F4 ENTREGA:
  [App Conductores] → navegación → entrega → [eventos DynamoDB] → [portal clientes]
  
  PROBLEMA: Offline frágil, pérdida de evidencias al reinstalar app
  PROBLEMA: 8% eventos con retraso >20 min
  PROBLEMA: Estados contradictorios en portal vs realidad

F5 EXCEPCIONES:
  [App conductores] → excepción → [TMS] → [CRM] → reintento/devolución
  
  PROBLEMA: Motivos no normalizados (texto libre)
  PROBLEMA: Sin validación previa de dirección antes de salir
  PROBLEMA: 34% fallas son prevenibles (dirección, ausencia)

F6 LIQUIDACIÓN:
  [ERP] ← concilia ← [AWS events + TMS + WMS + portal]
  
  PROBLEMA: Conciliación manual 23 días
  PROBLEMA: Penalidades calculadas en Excel con reglas especiales
  PROBLEMA: 7% facturas observadas por clientes
```

---

## TO BE - Arquitectura de Negocio

### Capacidades de Negocio TO BE

| Capacidad | Descripción TO BE | Madurez Objetivo |
|---|---|---|
| Recepción multi-canal | API + portal web (eliminar CSV/SFTP) | Alta - Validación automática completa |
| Validación de órdenes | Validación en tiempo real: dirección, SKU, duplicados, SLA | Alta - <1% defectos |
| Gestión de almacén | WMS cloud con auto-scaling y modo degradado | Alta - 99.9% disponibilidad |
| Gestión de transporte | TMS integrado en tiempo real con WMS y optimizador | Alta - <5% rutas manuales |
| Optimización de rutas | Tiempo real con datos de tráfico live y ML | Alta - Rutas dinámicas |
| Tracking última milla | Tiempo real, offline robusto, evidencias garantizadas | Alta - 98% trazabilidad |
| Gestión de excepciones | Taxonomía normalizada, predicción de excepciones, validación previa | Alta - -40% excepciones prevenibles |
| Liquidación y facturación | Automatizada, conciliación en tiempo real | Alta - Cierre en 1 día |
| Atención al cliente | CRM integrado con misma fuente de datos | Alta - Resolución primer contacto |
| Analítica | Streaming en tiempo real + ML predictivo | Alta - Dashboards operativos live |

### Procesos de Negocio TO BE

```
F1 RECEPCIÓN:
  API → [Azure APIM + validación SLA] → [Orquestador AKS + backpressure] → [Event Hub]
       → [Servicio Validación: dirección + SKU + deduplicación idempotente]
       → [WMS cloud / Event Store]

F2 PREPARACIÓN:
  [WMS cloud] → ola de picking en tiempo real → [handhelds] → [movimientos a Event Hub]
  Modo degradado automático con reconciliación automática al reconectar

F3 DESPACHO:
  [Event Hub] → [TMS] → [Optimizador GKE tiempo real] → manifiestos digitales
              → [App Conductores AWS]
  Rutas generadas solo con paquetes confirmados, cierre de manifiestos en tiempo real

F4 ENTREGA:
  [App conductores] → offline seguro (SQLite cifrado) → evidencias atómicas
                   → [Kinesis] → [Event Store] → [Portal clientes tiempo real]
  Pre-validación de dirección y contacto con destinatario antes de salir a ruta

F5 EXCEPCIONES:
  Taxonomía normalizada obligatoria → [Servicio Excepciones] → [ML predicción]
  Validación anticipada: dirección + contacto + ventana = -34% excepciones prevenibles

F6 LIQUIDACIÓN:
  [Event Store unificado] → [Servicio Liquidación] → conciliación automática
                         → [ERP via API] → factura en 24h del cierre del ciclo
```

---

# PARTE 3: FASE C - ARQUITECTURA DE SISTEMAS DE INFORMACIÓN

## AS IS - Arquitectura de Aplicaciones y Datos

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA DE SISTEMAS AS IS                                        │
│                                                                                          │
│  Clientes ──► APIM Azure ──► Orquestador AKS ──► WMS SQL On-Prem                       │
│             (REST)         (Java/Spring)        (.NET/SQL Server)                        │
│                                │                      │                                  │
│                                ▼                      ▼                                  │
│                            TMS Azure ◄──────── Inventario On-Prem                       │
│                          (.NET/Azure SQL)      (Oracle/SQL Server)                       │
│                                │                                                         │
│                                ▼                                                         │
│                        Optimizador GCP ─────────────────────────────► App Driver AWS    │
│                        (Python/BigQuery)      (batch, no RT)          (React Native      │
│                                                                         DynamoDB)         │
│                                                      │                                   │
│                                              S3 Evidencias AWS                          │
│                                              (fotos, firmas)                            │
│                                                                                          │
│  Analítica semanal ◄── BigQuery GCP ◄── ETL batch desde cada sistema                   │
│  ERP On-Prem ◄── reportes mensuales (sin tiempo real)                                   │
│  Portal Clientes SaaS ◄── eventos DynamoDB (con retraso)                               │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Problemas de Arquitectura de Información AS IS

| Problema | Sistema Afectado | Impacto |
|---|---|---|
| Sin modelo canónico de estados | WMS, TMS, App, Portal | Estados contradictorios visibles al cliente |
| Múltiples fuentes de verdad para inventario | WMS on-prem, WMS satélites, ERP | 2.8% movimientos con ajuste diario |
| Sin bus de eventos central | Todos | Integraciones punto a punto, frágiles |
| Batch diario/semanal para analítica | GCP BigQuery | Sin visibilidad operativa en tiempo real |
| Deduplicación por ID externo | Orquestador AKS | 32,000 pedidos duplicados en un incidente |
| Evidencias sin hash de integridad | S3 AWS | 1,200 entregas sin firma reconocida |

---

## TO BE - Arquitectura de Aplicaciones y Datos

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                    ARQUITECTURA DE SISTEMAS TO BE                                        │
│                                                                                          │
│  Clientes ──► APIM Azure ──► Servicio Pedidos (AKS) ──► [EVENT HUB] ◄── WMS Cloud      │
│  (API/Web)   (validación     (idempotente,              (Kafka/Azure   (AKS, auto-scale) │
│               OAuth2)         backpressure)              Event Hubs)                    │
│                                                               │                          │
│                    ┌──────────────────────────────────────────┤                         │
│                    │                  │                        │                          │
│                    ▼                  ▼                        ▼                          │
│              TMS (Azure)      Optimizador (GKE)       App Driver (ECS)                  │
│              .NET Core         Python + RT            React Native                      │
│              Azure SQL         Pub/Sub                DynamoDB Global                   │
│                    │                  │               S3 Evidencias cifradas             │
│                    │                  │               Kinesis Events                     │
│                    └──────────────────┴──────────────────────┘                          │
│                                       │                                                  │
│                              EVENT STORE (Canónico)                                     │
│                       Modelo: recibido→validado→...→liquidado                           │
│                                       │                                                  │
│              ┌────────────────────────┤                                                  │
│              │                        │                                                  │
│              ▼                        ▼                                                  │
│     BigQuery Streaming         Servicio Liquidación                                     │
│     (Medallion: B→S→G)         (Azure SQL + API ERP)                                   │
│     Looker RT Dashboards        Conciliación automática                                 │
│     Vertex AI ML                                                                        │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Nuevos Servicios/Capacidades TO BE

| Servicio | Descripción | Plataforma |
|---|---|---|
| Servicio de Validación | Valida SKU, dirección, duplicados, SLA en tiempo real | Azure AKS |
| Event Store Canónico | Fuente única de verdad para estados de pedido y eventos | Azure Event Hub + DynamoDB |
| Servicio de Excepciones | Gestión normalizada de excepciones con taxonomía controlada | Azure AKS |
| Servicio de Liquidación | Calcula automáticamente servicios, penalidades y genera conciliación | Azure AKS + Azure SQL |
| Plataforma de Observabilidad | Trazas, métricas y logs unificados cross-cloud | Datadog / OpenTelemetry |
| Validador de Dirección | API de geocodificación y validación de dirección antes de salir a ruta | Azure / Google Maps API |
| Servicio de Notificaciones | Comunicación proactiva con destinatario (SMS, WhatsApp, email) | AWS SNS / SaaS |

---

# PARTE 4: FASE D - ARQUITECTURA TECNOLÓGICA

## AS IS - Arquitectura Tecnológica

| Capa | Componente | Tecnología | Problema |
|---|---|---|---|
| Orquestación | AKS | Kubernetes (Azure) | Sin HPA configurado para campañas |
| WMS | On premises | VMware + SQL Server 2016 | Sin HA, sin auto-scale, se degrada |
| TMS | Azure VM / App Service | .NET / Azure SQL | Funciona, poco integrado |
| Optimizador | GCP GCE | Python batch | Sin streaming, retraso en datos tráfico |
| App Driver | AWS EC2/ECS | React Native + DynamoDB | Offline frágil |
| Analítica | GCP | BigQuery batch | Solo semanal |
| Integración | REST punto a punto | Sin bus central | N integraciones frágiles |
| Observabilidad | Por sistema | Sin unificación | Sin visibilidad end-to-end |
| Seguridad | OAuth básico | Sin Zero Trust | Riesgo en APIs y móvil |

## TO BE - Arquitectura Tecnológica

| Capa | Componente | Tecnología TO BE | Mejora |
|---|---|---|---|
| API Gateway | APIM | Azure API Management (Pro) + WAF | Seguridad, rate limiting, OAuth 2.0 |
| Orquestación Pedidos | AKS + KEDA | Kubernetes + auto-scaling por eventos | Escala a 3x en campaña automáticamente |
| WMS | Cloud híbrido | WMS modernizado (Azure / contenedores) | HA, auto-scale, modo degradado |
| TMS | AKS Azure | .NET 8 / AKS con HA multi-zona | Sin single point of failure |
| Optimizador Rutas | GKE Autopilot | Python + GKE + Pub/Sub | Tiempo real, escala automática |
| App Driver | ECS Fargate | React Native + SQLite cifrado + Kinesis | Offline robusto, evidencias seguras |
| Bus de Eventos | Event Hub / Kafka | Apache Kafka o Azure Event Hubs | Desacoplamiento, replay, exactly-once |
| Analítica | BigQuery + Dataflow | Streaming, Medallion, Vertex AI | Tiempo real + ML predictivo |
| Observabilidad | Datadog + OpenTelemetry | Cross-cloud unificado | Visibilidad end-to-end total |
| Seguridad | Zero Trust | Azure AD + WAF + SIEM + DLP | Security by Design |
| IaC | Terraform | Terraform + GitOps (ArgoCD) | Infraestructura reproducible |

---

## Resumen de Brechas AS IS → TO BE

| Dimensión | AS IS | TO BE | Brecha |
|---|---|---|---|
| Disponibilidad campaña | ~95% | 99.9% | Auto-scaling, HA, Circuit Breakers |
| Integración | Punto a punto | Bus de eventos central | Implementar Kafka/Event Hub |
| WMS | On-premises sin escala | Cloud con auto-scaling | Migración/modernización WMS |
| Optimización rutas | Batch | Tiempo real | GKE + Pub/Sub streaming |
| Tracking | Eventual inconsistente | Tiempo real confiable | Event Store canónico |
| Liquidación | Manual 23 días | Automática <1 día | Servicio de Liquidación nuevo |
| Observabilidad | Aislada por sistema | Cross-cloud unificada | Datadog + OpenTelemetry |
| Seguridad | OAuth básico | Zero Trust + Security by Design | Azure AD + WAF + SIEM |

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
