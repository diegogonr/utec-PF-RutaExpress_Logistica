# Mapa Portafolio de Aplicaciones
## RutaExpress Fulfillment & Transporte

---

## 1. Propósito

Inventario completo de las aplicaciones de RutaExpress, clasificadas por **capa arquitectónica**. Permite identificar redundancias, obsolescencia, riesgos tecnológicos y brechas de capacidad en cada capa del esquema de portafolio.

---

## 2. Mapa Visual por Capas Arquitectónicas

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│                        MAPA PORTAFOLIO DE APLICACIONES - RUTAEXPRESS                         │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA TRANSVERSAL (Seguridad · Observabilidad · Gobierno · IaC)                              │
│  ┌──────────────────────────────────────────────────────────────────────────────────────┐    │
│  │  [Sin plataforma unificada AS IS]  ──  Monitoreo aislado por sistema  ──  OAuth básico│    │
│  └──────────────────────────────────────────────────────────────────────────────────────┘    │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA CANALES (Puntos de contacto con clientes y conductores)                                │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌───────────────────┐  ┌─────────────┐  │
│  │  APP-03             │  │  APP-18 ⚠️          │  │  APP-19           │  │  APP-15 ⚠️ │  │
│  │  Portal Clientes    │  │  Portal Trazabilidad │  │  Portal Tracking  │  │  App        │  │
│  │  B2B (SaaS)         │  │  Clientes B2B (SaaS) │  │  Destinatarios    │  │  Conductores│  │
│  │  Carga CSV/Excel    │  │  Estados inconsist.  │  │  (PWA/SaaS)       │  │  (AWS)  ⚠️ │  │
│  └─────────────────────┘  └─────────────────────┘  └───────────────────┘  └─────────────┘  │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA INTEGRACIÓN (APIs · Bus de Eventos · Mensajería · Conectores)                         │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌───────────────────┐  ┌─────────────┐  │
│  │  APP-01             │  │  APP-04 🗑️          │  │  APP-21           │  │  [AUSENTE]  │  │
│  │  Azure API Mgmt     │  │  S3 Bucket Legado   │  │  Notification Svc │  │  Sin bus    │  │
│  │  (Gateway APIs)     │  │  (SFTP/CSV archivos)│  │  (SMS/Email SaaS) │  │  de eventos │  │
│  └─────────────────────┘  └─────────────────────┘  └───────────────────┘  └─────────────┘  │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA CORE (Sistemas Operacionales Centrales del Negocio)                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐ │
│  │  APP-02 ⚠️     │  │  APP-06 ⚠️     │  │  APP-11         │  │  APP-15 ⚠️             │ │
│  │  Orquestador    │  │  WMS Principal  │  │  TMS            │  │  App Conductores        │ │
│  │  Pedidos (AKS)  │  │  On-Premises    │  │  (Azure)        │  │  (AWS / DynamoDB)       │ │
│  │  Sin backpressure│  │  SQL Server ✅  │  │                 │  │  Offline frágil         │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐ │
│  │  APP-05 ⚠️     │  │  APP-07 ⚠️     │  │  APP-12 ⚠️     │  │  APP-16                 │ │
│  │  Validador      │  │  WMS Satélite   │  │  Optimizador    │  │  Almacenamiento         │ │
│  │  Pedidos (AKS)  │  │  On-Prem local  │  │  Rutas (GCP)    │  │  Evidencias (S3 AWS)    │ │
│  │  Falla dedup.   │  │  Sync horaria   │  │  Solo batch     │  │                         │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐                                                    │
│  │  APP-10         │  │  APP-13         │                                                    │
│  │  App Handhelds  │  │  Portal         │                                                    │
│  │  (Wi-Fi interno)│  │  Transportistas │                                                    │
│  │                 │  │  (Azure)        │                                                    │
│  └─────────────────┘  └─────────────────┘                                                    │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA DATA (Almacenamiento · Eventos · Analítica · ML)                                      │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌───────────────────┐  ┌─────────────┐  │
│  │  APP-22 ⚠️          │  │  APP-23             │  │  APP-24 ⚠️        │  │  APP-09     │  │
│  │  Plataforma         │  │  Dashboards         │  │  ML Modelos       │  │  IoT Core   │  │
│  │  Analítica (GCP)    │  │  Operativos         │  │  Rutas (GCP       │  │  Sensores   │  │
│  │  Batch semanal      │  │  (GCP) ⚠️           │  │  batch) ⚠️        │  │  Frío (AWS) │  │
│  └─────────────────────┘  └─────────────────────┘  └───────────────────┘  └─────────────┘  │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA SOPORTE (Back-office · Operaciones Internas · Almacén)                                │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌───────────────────────────────────┐    │
│  │  APP-08 ⚠️          │  │  APP-14 🗑️          │  │  APP-17                           │    │
│  │  Control de         │  │  Sistema de         │  │  Pasarela Pago                    │    │
│  │  Inventario         │  │  Impresión          │  │  Contra Entrega (SaaS)            │    │
│  │  (On-Premises)      │  │  Manifiestos On-P.  │  │                                   │    │
│  │  No tiempo real     │  │  Deuda técnica      │  │                                   │    │
│  └─────────────────────┘  └─────────────────────┘  └───────────────────────────────────┘    │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA CRM / ATENCIÓN AL CLIENTE                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐     │
│  │  APP-20 ⚠️                                                                          │     │
│  │  CRM de Atención al Cliente (SaaS)                                                  │     │
│  │  Gestión reclamos 18,000 contactos/día · Taxonomía diferente a App y TMS ⚠️        │     │
│  └─────────────────────────────────────────────────────────────────────────────────────┘     │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA ERP / FINANZAS                                                                         │
│  ┌──────────────────────────────────────────┐  ┌───────────────────────────────────────┐    │
│  │  APP-25 ⚠️                               │  │  APP-26 🗑️                            │    │
│  │  ERP Financiero (On-Premises)            │  │  Sistema de Liquidación (Excel VBA)   │    │
│  │  Facturación · Inv. Valorizado           │  │  Penalidades manuales · Error humano  │    │
│  │  Sin integración tiempo real             │  │  Conciliación 23 días · DEPRECAR      │    │
│  └──────────────────────────────────────────┘  └───────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────────────────────┘

Leyenda:  ⚠️ = Problemas críticos / riesgos     🗑️ = Candidato a deprecar
```

---

## 3. Inventario Detallado por Capa

### Capa Transversal

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| — | Observabilidad Unificada | **AUSENTE** | — | ❌ No existe | Crítica | Cada sistema tiene monitoreo aislado |
| — | Plataforma IaC | **AUSENTE** | — | ❌ No existe | Alta | Sin Terraform, infraestructura manual |
| — | Gestión de Identidad/Accesos | Parcial | Azure AD básico | ⚠️ Incompleto | Alta | Sin Zero Trust ni MFA para todos |
| — | Bus de Eventos Central | **AUSENTE** | — | ❌ No existe | Crítica | Principal brecha arquitectónica |

---

### Capa Canales

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-03 | Portal Clientes B2B (carga manual) | SaaS externo | Nube proveedor | Activo | Media | Carga CSV/Excel — deuda técnica a eliminar |
| APP-18 | Portal Trazabilidad Clientes B2B | SaaS externo | Nube proveedor | ⚠️ Activo | Alta | Muestra estados inconsistentes por eventos fuera de orden |
| APP-19 | Portal Tracking Destinatarios | Web/PWA | SaaS | Activo | Media | Seguimiento para destinatarios finales |
| APP-15 | App de Conductores | Custom Mobile | AWS (ECS/EC2) | ⚠️ Activo | Crítica | Android/iOS · Offline frágil · 1,200 firmas perdidas |

**Brechas de Canales:**
- No existe canal de comunicación proactiva al destinatario (WhatsApp/SMS antes de la entrega)
- APP-18 y APP-19 muestran datos de fuentes distintas → inconsistencia percibida por el cliente

---

### Capa Integración

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-01 | Azure API Management | PaaS | Azure | Activo | Alta | Gateway de APIs para clientes externos |
| APP-04 | Bucket S3 Legado (archivos) | IaaS | AWS S3 | 🗑️ Activo | Baja | Recepción de CSV/Excel histórica — deprecar |
| APP-21 | Notification Service (SMS/Email) | SaaS | Proveedor externo | Activo | Media | Notificaciones a destinatarios |
| — | Bus de Eventos / Message Broker | **AUSENTE** | — | ❌ No existe | Crítica | WMS↔TMS↔App van punto a punto |

**Brechas de Integración:**
- Sin bus de eventos central → todas las integraciones son punto a punto y frágiles
- Sin mecanismo de deduplicación confiable entre sistemas
- APP-04 sigue activo como canal legado de clientes medianos

---

### Capa Core

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-02 | Orquestador de Pedidos | Custom (tecnología no especificada en el caso) | Azure AKS | ⚠️ Activo | Crítica | Sin backpressure · Cola descontrolada ante degradación WMS |
| APP-05 | Validador de Pedidos | Custom (tecnología no especificada en el caso) | Azure AKS | ⚠️ Activo | Alta | Falla deduplicación cuando ID externo cambia |
| APP-06 | WMS Principal | On Premises · SQL Server (✅ caso) | On Premises | ⚠️ Activo | Crítica | Se degrada en campaña (6h Cyber Days) · Bloqueo de tablas |
| APP-07 | WMS Satélite (almacenes) | On Premises local (✅ caso) | On Premises local | ⚠️ Activo | Alta | Sync horaria → 4,900 movimientos en conflicto |
| APP-10 | App Handhelds (picking) | ⚠️ Suposición: dispositivo Android o similar | Wi-Fi interno (✅ caso) | Activo | Alta | Operación de picking en almacén |
| APP-11 | TMS (Transportation Mgmt) | Azure (✅ caso) · Tecnología interna no especificada | Azure | Activo | Crítica | Gestión rutas, manifiestos, transportistas |
| APP-12 | Optimizador de Rutas | GCP batch (✅ caso) · Stack interno no especificado | GCP (batch) | ⚠️ Activo | Alta | Solo batch · Datos tráfico desactualizados · 380 rutas inviables |
| APP-13 | Portal Transportistas Tercerizados | ⚠️ Suposición: aplicación web en Azure | Azure | Activo | Media | Acceso a manifiestos para terceros |
| APP-15 | App de Conductores | AWS + DynamoDB (✅ caso) · Framework mobile no especificado | AWS + DynamoDB | ⚠️ Activo | Crítica | Offline frágil · Evidencias perdibles · Motivos texto libre |
| APP-16 | Almacenamiento Evidencias | AWS S3 (✅ caso) | AWS S3 | Activo | Crítica | Fotos y firmas de entrega — sin hash de integridad |

**Brechas de Core:**
- APP-06 es el principal punto único de falla operacional
- APP-12 en batch impide rutas dinámicas en tiempo real
- APP-15 pierde evidencias que bloquean liquidación con clientes

---

### Capa Data

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-09 | IoT Core (sensores temperatura) | PaaS AWS | AWS IoT Core | Activo | Alta | Temperatura de cámaras refrigeradas — OK |
| APP-22 | Plataforma de Analítica | GCP batch semanal (✅ caso) · Herramienta específica no indicada | GCP (batch semanal) | ⚠️ Activo | Media | Consolidación semanal · Sin visibilidad operativa real |
| APP-23 | Dashboards Operativos | ⚠️ Suposición: herramienta de BI en GCP, no especificada | GCP | Activo | Media | Reportes para operaciones y clientes |
| APP-24 | ML / Optimización Rutas | GCP (✅ caso) · Algoritmo específico no mencionado | GCP (batch) | ⚠️ Activo | Alta | Caso 6b R3: "algoritmo no aprende por datos inconsistentes" |

**Brechas de Data:**
- Sin Event Store centralizado: cada sistema guarda sus propios eventos
- Analítica semanal → sin alertas operativas en tiempo real
- APP-24 aprende con datos sucios (motivos de excepción no normalizados)

---

### Capa Soporte

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-08 | Control de Inventario | ⚠️ Suposición: sistema complementario al WMS, tecnología no especificada | On Premises | ⚠️ Activo | Alta | No refleja inventario en tiempo real · Inferido de Caso 6a F2 |
| APP-14 | Sistema Impresión Manifiestos | ⚠️ Suposición: aplicación local legacy | On Premises (centros) | 🗑️ Activo | Baja | ✅ Caso 6a F3: manifiestos se imprimen localmente |
| APP-17 | Pasarela Pago Contra Entrega | SaaS (proveedor no especificado) | SaaS externo | Activo | Alta | ✅ Caso 6a F4: pagos contra entrega integrados con pasarela SaaS |

---

### Capa CRM / Atención al Cliente

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-20 | CRM de Atención al Cliente | SaaS externo | Nube proveedor | ⚠️ Activo | Alta | 18,000 contactos/día · Taxonomía de reclamos diferente a TMS y App |

**Brechas de CRM:**
- Taxonomía de motivos desconectada del TMS y la app de conductores
- Sin integración con Event Store → agentes no ven el estado real del pedido en tiempo real

---

### Capa ERP / Finanzas

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-25 | ERP Financiero | ⚠️ Suposición: ERP COTS, marca no especificada en el caso | On Premises | ⚠️ Activo | Alta | ✅ Caso 6a F6: facturación en ERP on premises · Sin tiempo real |
| APP-26 | Sistema de Liquidación (penalidades) | Excel / hojas de cálculo | Local (PC usuario) | 🗑️ Activo | Crítica | ✅ Caso 6a F6: notas de crédito calculadas con hojas Excel |

**Brechas de ERP/Finanzas:**
- APP-26 es riesgo crítico operacional y financiero
- APP-25 no se integra en tiempo real con los sistemas cloud

---

## 4. Clasificación por Estado y Acción TO BE

| Capa | Acción Principal | Aplicaciones |
|---|---|---|
| Transversal | Crear desde cero | Bus de eventos, IaC Terraform, Observabilidad unificada, Zero Trust |
| Canales | Mejorar integración + nuevo canal proactivo | APP-15 (rediseño), APP-18 (datos consistentes), nuevo canal WhatsApp |
| Integración | Reemplazar P2P + deprecar legado | APP-04 (deprecar), APP-21 (mantener), nuevo Event Hub/Kafka |
| Core | Modernizar críticos + batch→RT | APP-06 (migrar cloud), APP-12 (batch→RT), APP-15 (offline robusto) |
| Data | Pasar a streaming + limpiar datos | APP-22 (streaming), APP-24 (datos limpios), Event Store nuevo |
| Soporte | Deprecar legado | APP-08 (integrar RT), APP-14 (deprecar), APP-17 (mantener) |
| CRM | Integrar con fuente única | APP-20 (adoptar taxonomía canónica + integrar Event Store) |
| ERP/Finanzas | Automatizar liquidación | APP-25 (API tiempo real), APP-26 (reemplazar con microservicio) |

---

## 5. Resumen del Portafolio

| Dimensión | Cantidad |
|---|---|
| Total aplicaciones | 26 |
| Aplicaciones con problemas críticos (⚠️) | 12 |
| Capacidades ausentes que deben crearse | 4 |
| Aplicaciones on-premises | 6 |
| Aplicaciones SaaS externas | 7 |
| Aplicaciones cloud (AWS / Azure / GCP) | 13 |
| Candidatas a deprecar (🗑️) | 3 |

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
