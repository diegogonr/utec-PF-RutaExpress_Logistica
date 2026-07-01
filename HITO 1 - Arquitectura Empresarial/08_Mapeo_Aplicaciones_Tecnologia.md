# Mapeo de Aplicaciones con Tecnología
## RutaExpress Fulfillment & Transporte

---

## 1. Propósito

Mostrar la relación entre cada aplicación del portafolio y las tecnologías, plataformas y servicios que la soportan. La columna **Fuente** indica si el dato viene directamente del caso o es una suposición técnica razonable marcada como tal.

**Convenciones:**
- ✅ Dato confirmado en el caso (Caso 6a o Caso 6b)
- ⚠️ Suposición técnica razonable (no mencionada explícitamente en el caso)

---

## 2. Mapeo AS IS

| ID | Aplicación | Plataforma / Infraestructura | Tecnología / Stack | Base de Datos | Fuente |
|---|---|---|---|---|---|
| APP-01 | Azure API Management | Azure (PaaS) | Azure API Management | N/A | ✅ Caso 6a F1 |
| APP-02 | Orquestador de Pedidos | Azure AKS | ⚠️ Suposición: posiblemente Java o .NET, no especificado en el caso | ⚠️ Suposición: BD relacional en Azure | ✅ AKS mencionado en Caso 6b |
| APP-03 | Portal B2B (Carga CSV/Excel) | SaaS (proveedor no especificado) | N/A (SaaS externo) | SaaS | ✅ Caso 6a F1 |
| APP-04 | Bucket S3 Legado (archivos) | AWS S3 | N/A | N/A | ✅ Caso 6a F1 |
| APP-05 | Validador de Pedidos | Azure AKS | ⚠️ Suposición: mismo stack que orquestador | ⚠️ Suposición: BD relacional en Azure | ⚠️ Inferido del problema de deduplicación (Caso 6a F1) |
| APP-06 | WMS Principal (On Premises) | On Premises | ⚠️ Suposición: tecnología COTS o custom, no especificada | SQL Server (✅ Caso 6b R1) | ✅ On premises + SQL Server en Caso 6b |
| APP-07 | WMS Satélite (On Premises local) | On Premises local | ⚠️ Suposición: versión reducida del mismo WMS | ⚠️ Suposición: BD local (tipo no especificado) | ✅ Caso 6a F2: "versión local con sincronización cada hora" |
| APP-08 | Control de Inventario | On Premises | ⚠️ Suposición: sistema complementario al WMS | ⚠️ Suposición: BD relacional on-prem (tipo no especificado) | ⚠️ Inferido de Caso 6a F2: ERP conserva inventario valorizado |
| APP-09 | IoT Core (sensores temperatura) | AWS IoT Core | AWS IoT Core / MQTT | ⚠️ Suposición: DynamoDB u otra BD AWS | ✅ Caso 6a F2 |
| APP-10 | App Handhelds (picking) | Wi-Fi interno | ⚠️ Suposición: Android nativo o similar | SQLite local (⚠️ Suposición) | ✅ Caso 6a F2: handhelds con Wi-Fi |
| APP-11 | TMS (Transportation Management) | Azure | ⚠️ Suposición: posiblemente COTS o custom, no especificado | ⚠️ Suposición: BD relacional en Azure | ✅ Caso 6a: "TMS está en Azure" |
| APP-12 | Optimizador de Rutas | GCP | ⚠️ Suposición: Python con librería de optimización (tipo no especificado) | ⚠️ Suposición: BigQuery u otra BD GCP | ✅ Caso 6a F3: "optimización de rutas en GCP con cargas batch" |
| APP-13 | Portal Transportistas Tercerizados | Azure | ⚠️ Suposición: aplicación web, tecnología no especificada | ⚠️ Suposición: BD relacional en Azure | ✅ Caso 6a F3: "transportistas tercerizados acceden por portal" |
| APP-14 | Sistema Impresión Manifiestos | On Premises (centros) | ⚠️ Suposición: aplicación local legacy | ⚠️ Suposición: BD local | ✅ Caso 6a F3: "manifiestos se imprimen localmente en cada centro" |
| APP-15 | App de Conductores | AWS | ⚠️ Suposición: React Native u otro framework mobile, no especificado | DynamoDB (✅ Caso 6a F4) | ✅ AWS + DynamoDB en Caso 6a F4 |
| APP-16 | Almacenamiento Evidencias (S3) | AWS S3 | N/A (storage) | AWS S3 | ✅ Caso 6a F4 |
| APP-17 | Pasarela de Pago Contra Entrega | SaaS (proveedor externo) | N/A (SaaS externo) | SaaS | ✅ Caso 6a F4 |
| APP-18 | Portal B2B (Trazabilidad) | SaaS (proveedor no especificado) | ⚠️ Suposición: aplicación web, tecnología no especificada | SaaS | ✅ Caso 6a F4: "portal SaaS de clientes" (función trazabilidad) |
| APP-19 | Portal Tracking Destinatarios | SaaS (proveedor no especificado) | ⚠️ Suposición: web/PWA, tecnología no especificada | SaaS | ⚠️ Inferido de Caso 6a F4: destinatarios consultan tracking |
| APP-20 | CRM de Atención al Cliente | SaaS (proveedor no especificado) | N/A (SaaS externo) | SaaS | ✅ Caso 6a F5: "Atención usa un CRM SaaS" |
| APP-21 | Servicio de Notificación (SMS/Email) | SaaS (proveedor externo) | N/A (SaaS externo) | SaaS | ⚠️ Inferido: comunicación proactiva a destinatarios |
| APP-22 | Plataforma de Analítica | GCP | ⚠️ Suposición: Python/Spark o herramienta GCP, no especificada | BigQuery (✅ GCP mencionado; herramienta específica es suposición) | ✅ Caso 6a F6: "Analítica en GCP consolida información semanalmente" |
| APP-23 | Dashboards Operativos | GCP | ⚠️ Suposición: herramienta de visualización GCP, no especificada | BigQuery (⚠️ Suposición) | ⚠️ Inferido de Caso 6a F6: reportes para clientes y operaciones |
| APP-24 | Optimización / ML de Rutas | GCP | ⚠️ Suposición: algoritmo ML o estadístico, tecnología no especificada | ⚠️ Suposición: usa datos históricos en GCP | ✅ Caso 6b R3: "el algoritmo de rutas en GCP no aprende correctamente" |
| APP-25 | ERP Financiero (On Premises) | On Premises | ⚠️ Suposición: ERP COTS (tipo no especificado) | ⚠️ Suposición: BD propia del ERP | ✅ Caso 6a F6: "facturación en el ERP on premises" |
| APP-26 | Sistema de Liquidación (Excel) | Local (PC usuario) | Excel / hojas de cálculo | Excel | ✅ Caso 6a F6: "notas de crédito se calculan con hojas Excel" |

---

## 3. Mapa Visual por Capa Tecnológica (AS IS)

```
┌──────────────────────────────────────────────────────────────────────────────┐
│              CAPAS TECNOLÓGICAS AS IS - RUTAEXPRESS                          │
├──────────────────────────────────────────────────────────────────────────────┤
│  CAPA CANALES                                                                │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐   │
│  │ Portal B2B     │ │ Portal B2B     │ │ App de         │ │ Portal Transport.│   │
│  │ (Carga CSV/    │ │ (Trazabilidad) │ │ Conductores    │ │ Tercerizados     │   │
│  │  Excel)        │ │ (SaaS)         │ │ (AWS)          │ │ (Azure)          │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘   │
├──────────────────────────────────────────────────────────────────────────────┤
│  CAPA API / INTEGRACIÓN                                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ Azure API Management  │  REST APIs  │  SFTP/CSV (Bucket S3 Legado (archivos)) │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────────────────────────┤
│  CAPA CORE / LÓGICA                                                          │
│  ┌────────────────┐ ┌────────────────┐ ┌─────────────────┐ ┌────────────┐  │
│  │ Orquestador    │ │ TMS            │ │ Optimizador     │ │ App de     │  │
│  │ Pedidos (AKS)  │ │ (Transportation│ │ de Rutas (GCP/  │ │ Conductores│  │
│  │                │ │  Management)   │ │ batch)          │ │ (AWS/      │  │
│  │                │ │                │ │                 │ │ DynamoDB)  │  │
│  └────────────────┘ └────────────────┘ └─────────────────┘ └────────────┘  │
├──────────────────────────────────────────────────────────────────────────────┤
│  CAPA DATOS                                                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐   │
│  │ SQL Server   │ │ BD Azure     │ │ DynamoDB     │ │ GCP (BigQuery    │   │
│  │ (WMS Principal)│ │ (AKS/TMS)   │ │ (App de       │ │ / analítica)     │   │
│  │ ✅ caso      │ │ ⚠️ supuesto  │ │  Conductores) │ │ ✅/⚠️ mixto     │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘   │
│  ┌──────────────┐ ┌──────────────┐                                          │
│  │ WMS Principal  │ │ ERP Financiero │                                          │
│  │ (On Premises)  │ │ (On Premises)  │                                          │
│  └──────────────┘ └──────────────┘                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│  CAPA INFRAESTRUCTURA                                                        │
│  ┌───────────────────┐ ┌──────────────────┐ ┌──────────────────────────┐   │
│  │  ON PREMISES      │ │     AZURE        │ │          AWS             │   │
│  │  WMS Principal,   │ │  AKS, Azure API  │ │  App de Conductores,    │   │
│  │  ERP Financiero,  │ │  Management,     │ │  Almacenamiento         │   │
│  │  Sistema Impresión│ │  TMS             │ │  Evidencias (S3),       │   │
│  │  Manifiestos      │ │                  │ │  DynamoDB, IoT Core     │   │
│  │  ✅ caso          │ │  ✅ caso         │ │  ✅ caso                │   │
│  └───────────────────┘ └──────────────────┘ └──────────────────────────┘   │
│  ┌──────────────────────────────────────────┐                               │
│  │                GCP                       │                               │
│  │  Optimizador rutas (batch), Analítica    │                               │
│  │  ✅ caso                                 │                               │
│  └──────────────────────────────────────────┘                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Mapeo TO BE — Tecnologías Objetivo

> Las tecnologías TO BE son propuestas del arquitecto basadas en los criterios del caso: plataformas ya usadas (AWS/Azure/GCP), objetivos de resiliencia, tiempo real y seguridad. Se indican como propuestas de diseño, no como hechos del caso.

| Dominio | AS IS (del caso) | Propuesta TO BE | Criterio de selección |
|---|---|---|---|
| Gateway de APIs — APP-01 | Azure API Management | Azure API Management + políticas de rate limiting, backpressure y OAuth 2.0 | Ya existe en el caso; ampliar capacidades |
| Orquestación Pedidos — APP-02 | AKS (Azure) sin backpressure | AKS + PLT-03 Event Hubs + Circuit Breaker | Mismo proveedor cloud (Azure) + patrones de resiliencia |
| WMS — APP-06 / APP-07 | On premises SQL Server | WMS Cloud (reemplaza APP-06 y APP-07) con auto-scaling | Eliminar punto único de falla; Azure ya usado para TMS |
| Optimizador de Rutas — APP-12 | GCP batch | GCP en tiempo real (GKE + Cloud Pub/Sub) | Misma nube GCP; pasar de batch a streaming |
| App de Conductores — APP-15 | AWS / DynamoDB | AWS ECS + DynamoDB + Kinesis + offline robusto | Mantener AWS donde ya está; agregar Kinesis para streaming |
| Almacenamiento Evidencias — APP-16 | AWS S3 | AWS S3 con cifrado AES-256 y hash de integridad | Misma plataforma; mejorar seguridad |
| Analítica — APP-22 | GCP batch semanal | GCP streaming (BigQuery + Dataflow) | Misma plataforma GCP; pasar a tiempo real |
| ML / Predicción Rutas — APP-24 | GCP batch | GCP con modelo ML (tecnología específica a definir en diseño de solución) | GCP ya tiene los datos históricos de rutas |
| Bus de Eventos — PLT-03 | Inexistente | Apache Kafka o Azure Event Hubs (decisión pendiente — ver ADR en HITO 2) | Azure Event Hubs se integra con AKS y TMS existentes |
| Liquidación — APP-26 | Sistema de Liquidación (Excel) | Microservicio en Azure (mismo proveedor que ERP integrado) | Reemplazar Excel; alineado con Azure como plataforma principal |
| Observabilidad — PLT-01 | Ninguna unificada | Plataforma cross-cloud (Datadog o Azure Monitor + OpenTelemetry) | OpenTelemetry es estándar abierto; compatible con las 3 nubes |
| Seguridad IAM — PLT-02 | OAuth básico en APP-01 | Azure AD + WAF en APP-01 + cifrado en tránsito/reposo | Azure AD ya disponible; alineado con Microsoft Azure existente |
| IaC — PLT-04 | Ninguna | Terraform (compatible con AWS, Azure y GCP) | Única herramienta para las 3 nubes del caso |

---

## 5. Matriz de Deuda Técnica y Obsolescencia (AS IS)

| Elemento | Aplicaciones | Riesgo | Fuente del problema |
|---|---|---|---|
| SQL Server on premises (versión y soporte) | APP-06 | Alto | ✅ Caso 6b R1: bloqueo de tablas bajo alta carga |
| Integración por archivos CSV/S3 | APP-04 | Medio | ✅ Caso 6a F1: canal legado aún activo |
| Sincronización horaria entre WMS | APP-07 | Alto | ✅ Caso 6a F2: 4,900 movimientos en conflicto |
| Optimizador en batch (no tiempo real) | APP-12 | Alto | ✅ Caso 6a F3: rutas generadas con datos atrasados |
| Offline frágil en App de Conductores | APP-15 | Crítico | ✅ Caso 6a F4: 1,200 entregas sin firma |
| Excel para liquidación | APP-26 | Crítico | ✅ Caso 6a F6: notas de crédito calculadas manualmente |
| Sin backpressure en orquestador | APP-02 | Crítico | ✅ Caso 6b R1: cola sin control ante degradación WMS |
| Falla deduplicación por ID externo | APP-05 | Crítico | ✅ Caso 6a F1: incidente 32,000 pedidos duplicados |

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
