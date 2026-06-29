# Mapeo de Aplicaciones con Tecnología
## RutaExpress Fulfillment & Transporte

---

## 1. Propósito

Mostrar la relación entre cada aplicación del portafolio y las tecnologías, plataformas, lenguajes y servicios que la soportan. Permite identificar dependencias tecnológicas, obsolescencia y oportunidades de modernización.

---

## 2. Mapeo Completo AS IS

| ID App | Aplicación | Lenguaje/Framework | Base de Datos | Infraestructura | Integración | Estado |
|---|---|---|---|---|---|---|
| APP-01 | Azure API Management | N/A (SaaS/PaaS) | N/A | Azure (PaaS) | REST APIs, OAuth | Activo |
| APP-02 | Orquestador de Pedidos | Java / Spring Boot | Azure SQL | Azure AKS | REST, Queues | ⚠️ Sin backpressure |
| APP-03 | Portal Clientes (carga manual) | N/A (SaaS externo) | SaaS | Nube proveedor | SFTP, CSV/Excel | Activo |
| APP-04 | Bucket S3 legado | N/A | N/A | AWS S3 | SFTP, archivos | 🗑️ Deprecar |
| APP-05 | Validador de Pedidos | Java / Spring Boot | Azure SQL | Azure AKS | REST | ⚠️ Falla deduplicación |
| APP-06 | WMS Principal | C# / .NET Framework | SQL Server 2016 | On Premises (VMware) | SOAP/REST | ⚠️ Crítico |
| APP-07 | WMS Satélites | C# / .NET Framework | SQL Server Express | On Premises local | Batch sync | ⚠️ Sync horaria |
| APP-08 | Control de Inventario | Java / JSP legacy | Oracle DB | On Premises | Batch | ⚠️ No tiempo real |
| APP-09 | IoT Sensores Frío | N/A (IoT Core) | DynamoDB | AWS IoT Core | MQTT | Activo |
| APP-10 | App Handhelds | Android nativo | SQLite local | Wi-Fi interno | REST/Wi-Fi | Activo |
| APP-11 | TMS | .NET Core | Azure SQL | Azure VMs | REST, Event Grid | Activo |
| APP-12 | Optimizador de Rutas | Python / OR-Tools | BigQuery | GCP GCE (batch) | REST (batch) | ⚠️ Solo batch |
| APP-13 | Portal Transportistas | Angular / .NET | Azure SQL | Azure App Service | REST | Activo |
| APP-14 | Manifiestos Impresión | Legacy VB.NET | SQL Server local | On Premises | Local | 🗑️ Deprecar |
| APP-15 | App Conductores | React Native | DynamoDB | AWS (ECS+EC2) | REST, WebSocket | ⚠️ Offline frágil |
| APP-16 | S3 Evidencias | N/A | S3 | AWS S3 | SDK S3 | Activo |
| APP-17 | Pasarela Pagos | N/A (SaaS) | SaaS | Proveedor externo | REST | Activo |
| APP-18 | Portal Trazabilidad Clientes | React / Node.js | SaaS | Nube proveedor | REST, Webhooks | ⚠️ Datos inconsistentes |
| APP-19 | Portal Tracking Destinatarios | PWA / Vue.js | N/A | Nube proveedor | REST | Activo |
| APP-20 | CRM Atención | N/A (SaaS) | SaaS | Nube proveedor | REST API | ⚠️ Taxonomía diferente |
| APP-21 | Notification Service | N/A (SaaS) | SaaS | Proveedor externo | REST, Webhooks | Activo |
| APP-22 | Plataforma Analítica | Python / Spark | BigQuery | GCP (Dataflow batch) | Batch ETL | ⚠️ Solo semanal |
| APP-23 | Dashboards Operativos | Looker / Data Studio | BigQuery | GCP | BigQuery | Activo |
| APP-24 | ML Modelos Rutas | Python / TensorFlow | BigQuery | GCP Vertex AI | REST | ⚠️ Datos sucios |
| APP-25 | ERP Financiero | SAP / ABAP | SAP HANA / Oracle | On Premises | RFC/BAPI, archivos | ⚠️ No tiempo real |
| APP-26 | Sistema Liquidación | VBA / Excel | Excel | Local | Manual | 🗑️ Deprecar urgente |

---

## 3. Mapa Visual por Capa Tecnológica

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    CAPAS TECNOLÓGICAS - RUTAEXPRESS AS IS                    │
├──────────────────────────────────────────────────────────────────────────────┤
│  CAPA PRESENTACIÓN / CANALES                                                 │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐   │
│  │ Portal B2B   │ │ Portal Track.│ │ App Drivers  │ │ Portal Transport │   │
│  │ (SaaS/React) │ │ (PWA/Vue)    │ │ (React Native│ │ (Angular/.NET)   │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘   │
├──────────────────────────────────────────────────────────────────────────────┤
│  CAPA API / INTEGRACIÓN                                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │ Azure API Management  │  REST APIs  │  SOAP (WMS)  │  SFTP/CSV     │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
├──────────────────────────────────────────────────────────────────────────────┤
│  CAPA LÓGICA DE NEGOCIO / SERVICIOS                                          │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌──────────────┐ │
│  │ Orquestador    │ │ TMS            │ │ Optimizador    │ │ App Drivers  │ │
│  │ (Java/AKS)     │ │ (.NET/Azure VM)│ │ (Python/GCP)   │ │ (RN/AWS ECS) │ │
│  └────────────────┘ └────────────────┘ └────────────────┘ └──────────────┘ │
├──────────────────────────────────────────────────────────────────────────────┤
│  CAPA DATOS                                                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐   │
│  │ SQL Server   │ │ Azure SQL    │ │ DynamoDB     │ │ BigQuery         │   │
│  │ (On-Prem WMS)│ │ (AKS/TMS)   │ │ (AWS Events) │ │ (GCP Analítica)  │   │
│  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────────┘   │
│  ┌──────────────┐ ┌──────────────┐                                          │
│  │ Oracle DB    │ │ SAP HANA     │                                          │
│  │ (Inv. On-P.) │ │ (ERP On-P.)  │                                          │
│  └──────────────┘ └──────────────┘                                          │
├──────────────────────────────────────────────────────────────────────────────┤
│  CAPA INFRAESTRUCTURA                                                        │
│  ┌───────────────────┐ ┌──────────────────┐ ┌──────────────────────────┐   │
│  │  ON PREMISES      │ │     AZURE        │ │          AWS             │   │
│  │  VMware vSphere   │ │  AKS, App Svc,   │ │  ECS, EC2, S3,          │   │
│  │  SQL Server       │ │  Azure SQL, VM   │ │  DynamoDB, IoT Core,    │   │
│  │  SAP on-prem      │ │  API Mgmt        │ │  Kinesis                │   │
│  └───────────────────┘ └──────────────────┘ └──────────────────────────┘   │
│  ┌──────────────────────────────────────────┐                               │
│  │                GCP                       │                               │
│  │  GKE, GCE, BigQuery, Vertex AI,         │                               │
│  │  Dataflow, Pub/Sub                      │                               │
│  └──────────────────────────────────────────┘                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Mapeo TO BE - Tecnologías Objetivo

| Dominio | Tecnología AS IS | Tecnología TO BE | Justificación |
|---|---|---|---|
| Integración de APIs | Azure API Management (aislado) | Azure API Management + Event Hub (Kafka) | Añadir bus de eventos para desacoplamiento |
| Orquestación Pedidos | AKS (Java/Spring Boot) sin backpressure | AKS + Azure Service Bus + Circuit Breaker (Resilience4j) | Resiliencia y backpressure por cliente/SLA |
| WMS | On Premises SQL Server (.NET) | WMS cloud-ready (Azure/AWS) o WMS modernizado con API | Eliminar punto único de falla, auto-scaling |
| Optimizador Rutas | Python/OR-Tools en GCP batch | Python/OR-Tools en GKE + Pub/Sub (tiempo real) | De batch a tiempo real con datos de tráfico fresh |
| App Conductores | React Native (offline frágil) | React Native + SQLite cifrado + retry robusto + MDM | Evidencias nunca perdidas, seguridad móvil |
| Tracking / Eventos | DynamoDB (aislado) | DynamoDB + Kinesis Data Streams + Event Store | Modelo canónico, eventos ordenados, replay |
| Analítica | GCP BigQuery batch semanal | BigQuery + Dataflow streaming + Looker tiempo real | Visibilidad operativa en tiempo real |
| Liquidación | Excel VBA manual | Microservicio de Liquidación (.NET/Java + Azure SQL) | Automatización, eliminar errores manuales |
| Observabilidad | Monitoring aislado por plataforma | Datadog/New Relic + OpenTelemetry (cross-cloud) | Visibilidad end-to-end única |
| Seguridad | OAuth básico, sin Zero Trust | Azure AD + OAuth 2.0 + WAF + SIEM + DLP | Security by Design |

---

## 5. Stack Tecnológico TO BE por Plataforma

### Azure (Orquestación y TMS)
```
• Azure Kubernetes Service (AKS) con HPA y KEDA
• Azure API Management (Gateway unificado)
• Azure Event Hubs / Service Bus (bus de eventos/mensajes)
• Azure SQL Managed Instance (datos transaccionales)
• Azure Monitor + Log Analytics
• Azure Active Directory B2C (identidad clientes)
• Azure Key Vault (secretos y certificados)
• Terraform (IaC para Azure)
```

### AWS (Última Milla y Evidencias)
```
• Amazon ECS Fargate (app conductores, sin gestión de servidores)
• Amazon DynamoDB Global Tables (eventos tracking, baja latencia)
• Amazon Kinesis Data Streams (streaming de eventos tracking)
• Amazon S3 + S3 Intelligent-Tiering (evidencias con archivado)
• AWS IoT Core (sensores temperatura)
• AWS Secrets Manager
• Terraform (IaC para AWS)
```

### GCP (Analítica y Optimización)
```
• Google Kubernetes Engine (GKE Autopilot para optimizador)
• Cloud Pub/Sub (eventos de tráfico tiempo real)
• BigQuery (Data Lakehouse Medallion: Bronze/Silver/Gold)
• Dataflow (ETL streaming)
• Vertex AI (modelos ML de optimización y predicción)
• Looker Studio (dashboards operativos)
• Terraform (IaC para GCP)
```

---

## 6. Matriz de Obsolescencia Tecnológica

| Tecnología | Aplicaciones Afectadas | Riesgo | Plan |
|---|---|---|---|
| SQL Server 2016 on premises | APP-06, APP-07 | Alto (sin soporte extendido 2026) | Migrar a SQL Managed Instance en Azure |
| .NET Framework (no .NET 8+) | APP-06, APP-07 | Alto | Modernizar a .NET 8 |
| Oracle DB on premises | APP-08 | Alto | Migrar a Azure SQL o eliminar |
| VB.NET legacy | APP-14 | Alto | Deprecar APP-14 |
| Excel/VBA (APP-26) | APP-26 | Crítico | Reemplazar urgente por microservicio |
| SOAP (integración WMS) | APP-06 | Medio | Modernizar a REST/eventos |
| Batch GCP (semanal) | APP-22 | Medio | Migrar a streaming con Dataflow |

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
