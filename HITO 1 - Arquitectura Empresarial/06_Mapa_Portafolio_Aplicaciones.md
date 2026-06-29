# Mapa Portafolio de Aplicaciones
## RutaExpress Fulfillment & Transporte

---

## 1. Propósito

Inventario completo de las aplicaciones de RutaExpress, clasificadas por dominio de negocio. Permite identificar redundancias, obsolescencia, riesgos tecnológicos y brechas de capacidad.

---

## 2. Inventario de Aplicaciones por Dominio

### Dominio 1: Gestión de Pedidos (Order Management)

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-01 | Azure API Management | SaaS/PaaS | Azure | Activo | Alta | Exposición de APIs para clientes |
| APP-02 | Orquestador de Pedidos | Custom | Azure AKS | Activo | Crítica | Recibe y procesa todas las órdenes |
| APP-03 | Portal de Clientes (carga manual) | SaaS | Nube (proveedor) | Activo | Media | Carga CSV/Excel para clientes medianos |
| APP-04 | Bucket S3 (integración legado) | IaaS | AWS S3 | Activo | Baja | Recepción de archivos histórica |
| APP-05 | Validador de Pedidos | Custom | Azure AKS | Activo | Alta | Validación de SKU, dirección, duplicados - CON PROBLEMAS |

**Problemas identificados (AS IS):**
- APP-05 falla en deduplicación cuando cambia el ID externo del cliente
- No hay backpressure en APP-02 ante degradación del WMS
- APP-04 (integración por archivos) es deuda técnica a eliminar

---

### Dominio 2: Gestión de Almacén (WMS)

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-06 | WMS Principal | COTS + Custom | On Premises (SQL Server) | Activo | Crítica | Centro distribución central. Se degrada en campañas |
| APP-07 | WMS Satélite (almacenes pequeños) | COTS reducido | On Premises local | Activo | Alta | Sincronización horaria con WMS principal - RIESGO |
| APP-08 | Sistema de Control de Inventario | Custom | On Premises (SQL Server) | Activo | Alta | Integrado con WMS, no en tiempo real |
| APP-09 | AWS IoT Core (sensores frío) | PaaS | AWS | Activo | Alta | Temperatura de cámaras refrigeradas |
| APP-10 | Sistema de Handhelds | Custom | Wi-Fi interno | Activo | Alta | Operación de picking con handhelds |

**Problemas identificados (AS IS):**
- APP-06 bloquea tablas de inventario bajo alta carga (Cyber Days: 6h degradado)
- APP-07 pierde sincronización → conflictos de movimientos (caso 4,900 movimientos en conflicto)
- APP-08 no refleja inventario en tiempo real hacia sistemas externos

---

### Dominio 3: Transporte y Despacho (TMS)

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-11 | TMS (Transportation Management) | COTS/Custom | Azure | Activo | Crítica | Gestión de rutas, manifiestos, transportistas |
| APP-12 | Optimizador de Rutas | Custom | GCP (batch) | Activo | Alta | Algoritmo de optimización con datos de tráfico - BATCH |
| APP-13 | Portal de Transportistas Tercerizados | Web Custom | Azure | Activo | Media | Acceso de terceros a manifiestos |
| APP-14 | Sistema de Impresión de Manifiestos | Custom local | On Premises (centros) | Activo | Baja | Impresión local en cada centro |

**Problemas identificados (AS IS):**
- APP-12 usa datos de tráfico con retraso (caso lluvias: 380 rutas inviables)
- APP-12 es batch, no tiempo real → rutas se generan sin todos los paquetes confirmados
- APP-14 es deuda técnica, manifiestos en papel como respaldo

---

### Dominio 4: Última Milla y Conductores

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-15 | App de Conductores | Custom Mobile | AWS (backend) | Activo | Crítica | Android/iOS, DynamoDB para eventos offline |
| APP-16 | Almacenamiento de Evidencias | Cloud Storage | AWS S3 | Activo | Crítica | Fotos y firmas de entrega |
| APP-17 | Pasarela de Pago Contra Entrega | SaaS | Proveedor externo | Activo | Alta | Pagos en efectivo y tarjeta en campo |

**Problemas identificados (AS IS):**
- APP-15: Pérdida de evidencias al reinstalar app o cambiar dispositivo (caso 1,200 firmas)
- APP-15: Motivos de excepción no normalizados (texto libre)
- APP-15: Sincronización offline puede generar eventos fuera de orden

---

### Dominio 5: Trazabilidad y Atención al Cliente

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-18 | Portal de Trazabilidad para Clientes | SaaS | Nube (proveedor) | Activo | Alta | Visibilidad de pedidos para clientes B2B |
| APP-19 | Portal de Tracking para Destinatarios | Web/PWA | SaaS | Activo | Media | Seguimiento para destinatarios finales |
| APP-20 | CRM de Atención al Cliente | SaaS | Nube (proveedor) | Activo | Alta | Gestión de reclamos y contacto 18,000/día |
| APP-21 | Notification Service (SMS/Email) | SaaS | Proveedor externo | Activo | Media | Notificaciones a destinatarios |

**Problemas identificados (AS IS):**
- APP-18 muestra estados inconsistentes con el estado real (eventos fuera de orden)
- APP-20 tiene taxonomía de reclamos diferente a la app conductores y TMS

---

### Dominio 6: Analítica y Datos

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-22 | Plataforma de Analítica | Custom | GCP (batch semanal) | Activo | Media | Consolidación de datos de todas las nubes - SEMANAL |
| APP-23 | Dashboards Operativos | Custom | GCP / Looker | Activo | Media | Reportes para operaciones y clientes |
| APP-24 | Modelos de Optimización de Rutas (ML) | Custom | GCP | Activo | Alta | Usa históricos de rutas, tráfico y excepciones |

**Problemas identificados (AS IS):**
- APP-22 consolida semanalmente → no hay visibilidad operativa en tiempo real
- APP-24 aprende con datos de excepciones inconsistentes (motivos no normalizados)

---

### Dominio 7: Finanzas y ERP

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-25 | ERP Financiero | COTS (ERP) | On Premises | Activo | Alta | Facturación, inventario valorizado, liquidaciones |
| APP-26 | Sistema de Liquidación | Custom | On Premises + Excel | Activo | Alta | Cálculo de penalidades con reglas especiales - MANUAL |

**Problemas identificados (AS IS):**
- APP-25 no se actualiza en tiempo real, factura desde reportes mensuales
- APP-26 usa Excel para penalidades especiales → error manual, conciliación 23 días

---

## 3. Mapa Visual de Aplicaciones por Dominio

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                      PORTAFOLIO DE APLICACIONES - RUTAEXPRESS                    │
├───────────────┬──────────────┬──────────────┬──────────────┬────────────────────┤
│  GESTIÓN      │  ALMACÉN     │  TRANSPORTE  │  ÚLTIMA      │  ANALÍTICA         │
│  PEDIDOS      │  (WMS)       │  (TMS)       │  MILLA       │  Y DATOS           │
├───────────────┼──────────────┼──────────────┼──────────────┼────────────────────┤
│ APP-01        │ APP-06 ⚠️    │ APP-11       │ APP-15 ⚠️   │ APP-22 ⚠️          │
│ Azure APIM    │ WMS On-Prem  │ TMS Azure    │ App Driver   │ GCP Analítica      │
│               │              │              │ AWS          │ (semanal)          │
│ APP-02 ⚠️    │ APP-07 ⚠️   │ APP-12 ⚠️   │              │                    │
│ Orquestador   │ WMS Satélite │ Optimizador  │ APP-16       │ APP-23             │
│ AKS           │ On-Prem      │ GCP (batch)  │ Evidencias   │ Dashboards         │
│               │              │              │ S3 AWS       │                    │
│ APP-03        │ APP-08 ⚠️   │ APP-13       │              │ APP-24 ⚠️          │
│ Portal SaaS   │ Control Inv. │ Portal       │ APP-17       │ ML Rutas           │
│               │ On-Prem      │ Tercerizado  │ Pasarela     │ GCP                │
│ APP-04 🗑️    │              │              │ Pago         │                    │
│ S3 legacy     │ APP-09       │ APP-14 🗑️  │              │                    │
│               │ IoT Frío AWS │ Manifiestos  │              │                    │
│ APP-05 ⚠️    │              │ On-Prem      │              │                    │
│ Validador     │ APP-10       │              │              │                    │
│ AKS           │ Handhelds    │              │              │                    │
├───────────────┴──────────────┴──────────────┴──────────────┴────────────────────┤
│           TRAZABILIDAD / ATENCIÓN                    FINANZAS                    │
│  APP-18 Portal Clientes SaaS ⚠️     APP-25 ERP On-Premises ⚠️                  │
│  APP-19 Portal Destinatarios SaaS   APP-26 Liquidación Excel ⚠️                 │
│  APP-20 CRM SaaS ⚠️                                                             │
│  APP-21 Notificaciones SaaS                                                      │
└──────────────────────────────────────────────────────────────────────────────────┘

Leyenda: ⚠️ = Tiene problemas críticos / riesgos  🗑️ = Candidato a deprecar
```

---

## 4. Clasificación por Estado y Acción TO BE

| Estado | Aplicaciones | Acción |
|---|---|---|
| Crítica con problemas | APP-02, APP-05, APP-06, APP-07, APP-12, APP-15 | Modernizar / Reemplazar (prioridad alta) |
| Activa sin problemas graves | APP-01, APP-09, APP-11, APP-16, APP-17, APP-18 | Mantener / Integrar mejor |
| SaaS a mantener | APP-03, APP-13, APP-18, APP-19, APP-20, APP-21 | Integrar con modelo canónico |
| Deuda técnica a eliminar | APP-04, APP-14, APP-26 (Excel) | Deprecar en TO BE |
| On-premises a migrar | APP-06, APP-07, APP-08, APP-25 | Migración progresiva a cloud |

---

## 5. Resumen del Portafolio

| Dimensión | Cantidad |
|---|---|
| Total aplicaciones | 26 |
| Aplicaciones críticas | 8 |
| Aplicaciones con problemas graves | 10 |
| Aplicaciones on-premises | 6 |
| Aplicaciones SaaS | 7 |
| Aplicaciones cloud (AWS/Azure/GCP) | 13 |
| Deuda técnica a eliminar | 3 |

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
