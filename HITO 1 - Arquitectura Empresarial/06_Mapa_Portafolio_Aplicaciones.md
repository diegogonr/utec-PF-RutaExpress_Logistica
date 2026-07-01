# Mapa Portafolio de Aplicaciones
## RutaExpress Fulfillment & Transporte

---

## 1. Propósito

Inventario de las aplicaciones de RutaExpress, clasificadas por **capa arquitectónica**. Permite identificar redundancias, obsolescencia, riesgos tecnológicos y **brechas** (*gaps*) entre lo desplegado hoy (AS IS) y lo que exige la arquitectura objetivo (TO BE).

### Convención AS IS vs TO BE

| Pregunta | Respuesta |
|---|---|
| **¿Incluyo plataformas (PLT)?** | **Sí, si están desplegadas o parcialmente desplegadas** (ej. PLT-02 con Azure AD básico). Son apps habilitadoras TOGAF, no APP de negocio. |
| **¿Qué es un “gap”?** | **Brecha**: algo **requerido pero ausente** hoy. No es un sistema en producción; es un hallazgo del análisis. |
| **¿Los gaps van en el mapa aunque no existan?** | **En AS IS no como app desplegada** — se marcan `❌ GAP`. **La definición del componente nuevo va en TO BE** (§4 y doc `09`). |
| **¿Azure / AWS / GCP son plataformas del portafolio?** | **No** — son nubes proveedoras (Arq. Tecnológica). Aquí solo se indica dónde corre cada APP/PLT. |

```
Mapa AS IS (§2)     →  APP existentes  +  PLT parcial  +  marcas GAP donde falta algo
Plan TO BE (§4, 09) →  PLT a crear/completar  +  APP a modificar/eliminar
```

### Nomenclatura oficial — Portales B2B

| ID | Nombre oficial | Función | Fase del caso |
|---|---|---|---|
| APP-03 | **Portal B2B (Carga CSV/Excel)** | Ingreso manual de órdenes por clientes medianos | Fase 1 — Recepción |
| APP-18 | **Portal B2B (Trazabilidad)** | Visibilidad de estados y tracking para clientes empresariales | Fases 2, 4 y 5 |

> En el caso de negocio (Caso 6a) ambos portales aparecen como un único “portal de clientes SaaS”. En el portafolio se descomponen en dos aplicaciones porque cumplen funciones distintas: **carga de órdenes** vs. **trazabilidad**. No usar el término genérico “Portal Clientes” sin especificar cuál.

### Nomenclatura oficial — WMS

| ID | Nombre oficial AS IS | Nombre oficial TO BE | Función |
|---|---|---|---|
| APP-06 | **WMS Principal (On Premises)** | **WMS Cloud** (reemplaza APP-06) | WMS central del CD principal; SQL Server on premises |
| APP-07 | **WMS Satélite (On Premises local)** | Absorbido por **WMS Cloud** (modo degradado local) | WMS local en almacenes pequeños; sync horaria con APP-06 |

> No usar indistintamente “WMS on premises”, “WMS central” o “WMS” en tablas de aplicaciones: referirse siempre al nombre oficial con ID (**APP-06** / **APP-07**). “WMS Cloud” es el reemplazo TO BE a partir de F2.

### Catálogo oficial de aplicaciones (APP-01 a APP-26)

| ID | Nombre oficial | Término en Caso 6a/6b | Plataforma AS IS |
|---|---|---|---|
| APP-01 | Azure API Management | Azure API Management | Azure |
| APP-02 | Orquestador de Pedidos | Orquestador en AKS | Azure AKS |
| APP-03 | Portal B2B (Carga CSV/Excel) | Portal SaaS — carga manual CSV/Excel | SaaS |
| APP-04 | Bucket S3 Legado (archivos) | Bucket S3 histórico | AWS S3 |
| APP-05 | Validador de Pedidos | Validador / deduplicación (inferido) | Azure AKS |
| APP-06 | WMS Principal (On Premises) | WMS principal / WMS on premises | On Premises · SQL Server |
| APP-07 | WMS Satélite (On Premises local) | WMS local / versión local sync horaria | On Premises local |
| APP-08 | Control de Inventario | *(inferido del ERP/WMS)* | On Premises |
| APP-09 | IoT Core (sensores temperatura) | AWS IoT Core | AWS IoT Core |
| APP-10 | App Handhelds (picking) | Handhelds | Wi-Fi interno |
| APP-11 | TMS (Transportation Management) | TMS en Azure | Azure |
| APP-12 | Optimizador de Rutas (GCP batch) | Optimización de rutas en GCP (batch) | GCP |
| APP-13 | Portal Transportistas Tercerizados | Portal transportistas tercerizados | Azure |
| APP-14 | Sistema Impresión Manifiestos | Manifiestos impresos localmente | On Premises |
| APP-15 | App de Conductores | App de conductores en AWS | AWS · DynamoDB |
| APP-16 | Almacenamiento Evidencias (S3) | Evidencias en S3 | AWS S3 |
| APP-17 | Pasarela de Pago Contra Entrega | Pasarela SaaS pagos contra entrega | SaaS |
| APP-18 | Portal B2B (Trazabilidad) | Portal SaaS de clientes (trazabilidad) | SaaS |
| APP-19 | Portal Tracking Destinatarios | Tracking para destinatarios finales *(inferido F4)* | SaaS |
| APP-20 | CRM de Atención al Cliente | CRM SaaS | SaaS |
| APP-21 | Servicio de Notificación (SMS/Email) | Notificaciones a destinatarios *(inferido)* | SaaS |
| APP-22 | Plataforma de Analítica (GCP batch) | Analítica en GCP (semanal) | GCP |
| APP-23 | Dashboards Operativos | Reportes operativos *(inferido F6)* | GCP |
| APP-24 | ML / Optimización de Rutas (GCP) | Algoritmo de rutas en GCP (Caso 6b R3) | GCP |
| APP-25 | ERP Financiero (On Premises) | ERP on premises | On Premises |
| APP-26 | Sistema de Liquidación (Excel) | Hojas Excel penalidades | Local · Excel |

> En tablas y diagramas usar siempre **nombre oficial + ID**. En narrativa se puede decir “app de conductores” o “portal SaaS” citando el caso, pero la primera mención en cada sección debe usar el nombre oficial.

**Prohibido abreviar nombres oficiales:** no usar Mgmt, Svc, On-Prem, RT, Driver, Bucket sin el nombre completo del catálogo. Ejemplos incorrectos → correctos: `Azure API Mgmt` → **Azure API Management**; `S3 Bucket Legado` → **Bucket S3 Legado (archivos)**; `Notification Svc` → **Servicio de Notificación (SMS/Email)**; `Optimizador RT` → **Optimizador de Rutas en Tiempo Real**.

### Aplicaciones de plataforma (PLT-01 a PLT-04) — capa transversal TOGAF

Según **TOGAF ADM · Fase C (Arquitectura de Aplicaciones)**, el **Application Portfolio / Application Landscape** no incluye solo aplicaciones de negocio: también cataloga **aplicaciones habilitadoras o de plataforma** (*platform / enabling / infrastructure applications*) que dan servicio transversal al resto.

Por eso **sí corresponde** que aparezcan en este mapa, en la **capa transversal**, pero **clasificadas aparte** de APP-01 a APP-26:

| Clasificación TOGAF | ID RutaExpress | Qué incluye |
|---|---|---|
| **Aplicaciones de negocio u operacionales** | APP-01 … APP-26 | WMS, TMS, portales, App de Conductores, ERP, etc. |
| **Aplicaciones de plataforma / habilitadoras** | PLT-01 … PLT-04 | Observabilidad, identidad, bus de eventos (cuando existan como componentes desplegados) |
| **Servicios tecnológicos** (Fase D — Arq. Tecnológica) | *(sin ID APP/PLT)* | IaC (Terraform), redes, cómputo — ver `07_Mapa_Infraestructura.md` |

| ID | Aplicación de plataforma | Tipo TOGAF | AS IS (este mapa) | TO BE (§4 y doc 09) |
|---|---|---|---|---|
| PLT-01 | Plataforma de Observabilidad Unificada | Habilitadora | ❌ **Gap** — no desplegada; monitoreo aislado por APP | Crear: Datadog o Azure Monitor + OpenTelemetry |
| PLT-02 | Plataforma de Identidad y Accesos (IAM) | Habilitadora | ⚠️ **Parcial** — Azure AD básico + OAuth en **APP-01** | Completar: MFA + Zero Trust + políticas IAM |
| PLT-03 | Bus de Eventos Central | Integración / middleware | ❌ **Gap** — no existe; integraciones P2P | Crear: Azure Event Hubs o Apache Kafka |
| PLT-04 | Plataforma IaC | Arq. Tecnológica (Fase D) | ❌ **Gap** — infra manual *(ver doc 07)* | Crear: Terraform multinube *(detalle en infra)* |

> **Gap ≠ aplicación en producción.** Un gap es una **entrada de catálogo + brecha documentada**: identifica *qué falta* en AS IS y *qué se creará* en TO BE. No se cuenta como “26 + 4 apps activas”; se cuenta aparte en el resumen de brechas.

> **OAuth básico** no es una aplicación: es una **política** de **Azure API Management (APP-01)**. **Azure AD** es el PaaS que sustenta **PLT-02** de forma incompleta hoy.

---

## 2. Mapa Visual AS IS por Capas Arquitectónicas

### Regla del diagrama AS IS

| En el mapa AS IS **sí van** | En el mapa AS IS **no van** (van en **§4 TO BE** o doc `09`) |
|---|---|
| Las **26 APP** que el caso describe como **existentes** (aunque estén malas, ⚠️ o 🗑️) | **PLT-01, PLT-03, PLT-04** — no están desplegadas; solo se listan como brecha abajo del diagrama |
| **PLT-02** IAM — **parcial** (Azure AD + OAuth en APP-01) | **WMS Cloud**, **Servicio de Validación de Órdenes**, **Manifiesto Digital**, etc. — son **reemplazos o apps nuevas TO BE**, no faltantes AS IS |
| Anotación de **brechas** en texto (pie del mapa), sin dibujarlas como cajas | Cualquier componente que **aún no existe en producción** dibujado como si fuera una app más |

**¿Por qué antes aparecían PLT inexistentes en el AS IS y no APP inexistentes?**  
Era **inconsistente**. Las PLT en gap se mostraban como cajas `❌ GAP` para marcar el hueco en la capa; las APP TO BE (WMS Cloud, microservicio de liquidación…) nunca se mostraron así porque **en AS IS sí hay WMS y Excel** — lo que falta es la **versión futura**, no la función. Lo mismo aplica a PLT: **no hay bus ni observabilidad unificada**, pero eso se documenta como **brecha**, no como componente del mapa. **La solución TO BE va en §4 y en `09`.**

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│              MAPA PORTAFOLIO DE APLICACIONES — AS IS · RUTAEXPRESS                           │
│              (solo componentes desplegados o parciales — ver §4 para TO BE)                  │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA TRANSVERSAL — único PLT desplegado (parcial)                                           │
│  ┌─────────────────────────────┐                                                             │
│  │  PLT-02 · IAM  ⚠️ PARCIAL   │   Brechas → TO BE §4: PLT-01 Observabilidad · PLT-03 Bus   │
│  │  Azure AD básico + OAuth    │   de Eventos · PLT-04 IaC (detalle en doc 07)              │
│  │  en APP-01                  │                                                             │
│  └─────────────────────────────┘                                                             │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA CANALES (Puntos de contacto con clientes y conductores)                                │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌───────────────────┐  ┌─────────────┐  │
│  │  APP-03             │  │  APP-18 ⚠️          │  │  APP-19           │  │  APP-15 ⚠️ │  │
│  │  Portal B2B        │  │  Portal B2B         │  │  Portal Tracking  │  │  App de     │  │
│  │  (Carga CSV/Excel) │  │  (Trazabilidad)     │  │  Destinatarios    │  │  Conductores│  │
│  │  (SaaS) ⚠️         │  │  (SaaS) ⚠️          │  │  (SaaS)           │  │  (AWS) ⚠️  │  │
│  └─────────────────────┘  └─────────────────────┘  └───────────────────┘  └─────────────┘  │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA INTEGRACIÓN (APIs · Mensajería · Conectores) — sin Bus de Eventos (brecha PLT-03 → TO BE)│
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌───────────────────┐                   │
│  │  APP-01             │  │  APP-04 🗑️          │  │  APP-21           │                   │
│  │  Azure API          │  │  Bucket S3 Legado   │  │  Servicio de      │                   │
│  │  Management         │  │  (archivos)         │  │  Notificación     │                   │
│  │  (Gateway APIs)     │  │  (SFTP/CSV)         │  │  (SMS/Email)      │                   │
│  └─────────────────────┘  └─────────────────────┘  └───────────────────┘                   │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA CORE (Sistemas Operacionales Centrales del Negocio)                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐ │
│  │  APP-02 ⚠️     │  │  APP-06 ⚠️     │  │  APP-11         │  │  APP-15 ⚠️             │ │
│  │  Orquestador    │  │  WMS Principal  │  │  TMS            │  │  App de                 │ │
│  │  Pedidos (AKS)  │  │  (On Premises)  │  │  (Transportation│  │  Conductores            │ │
│  │  Sin backpressure│  │  SQL Server ✅  │  │  Management)    │  │  (AWS / DynamoDB)       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐ │
│  │  APP-05 ⚠️     │  │  APP-07 ⚠️     │  │  APP-12 ⚠️     │  │  APP-16                 │ │
│  │  Validador      │  │  WMS Satélite   │  │  Optimizador    │  │  Almacenamiento         │ │
│  │  Pedidos (AKS)  │  │  On Premises    │  │  Rutas (GCP)    │  │  Evidencias (S3)        │ │
│  │  Falla dedup.   │  │  local          │  │  Solo batch     │  │                         │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐                                                    │
│  │  APP-10         │  │  APP-13         │                                                    │
│  │  App Handhelds  │  │  Portal         │                                                    │
│  │  (picking)      │  │  Transportistas │                                                    │
│  │  (Wi-Fi interno)│  │  Tercerizados   │                                                    │
│  └─────────────────┘  └─────────────────┘                                                    │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA DATA (Almacenamiento · Eventos · Analítica · ML)                                      │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌───────────────────┐  ┌─────────────┐  │
│  │  APP-22 ⚠️          │  │  APP-23             │  │  APP-24 ⚠️        │  │  APP-09     │  │
│  │  Plataforma         │  │  Dashboards         │  │  ML Modelos       │  │  IoT Core   │  │
│  │  Analítica (GCP)    │  │  Operativos         │  │  Rutas (GCP       │  │  (sensores     │  │
│  │  Batch semanal      │  │  (GCP) ⚠️           │  │  batch) ⚠️        │  │  temperatura)  │  │
│  └─────────────────────┘  └─────────────────────┘  └───────────────────┘  └─────────────┘  │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA SOPORTE (Back-office · Operaciones Internas · Almacén)                                │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌───────────────────────────────────┐    │
│  │  APP-08 ⚠️          │  │  APP-14 🗑️          │  │  APP-17                           │    │
│  │  Control de         │  │  Sistema Impresión  │  │  Pasarela de Pago                 │    │
│  │  Inventario         │  │  Manifiestos        │  │  Contra Entrega (SaaS)            │    │
│  │  (On Premises)      │  │  (On Premises)      │  │                                   │    │
│  │  No tiempo real     │  │  Deuda técnica      │  │                                   │    │
│  └─────────────────────┘  └─────────────────────┘  └───────────────────────────────────┘    │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA CRM / ATENCIÓN AL CLIENTE                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐     │
│  │  APP-20 ⚠️                                                                          │     │
│  │  CRM de Atención al Cliente (SaaS)                                                  │     │
│  │  Gestión reclamos 18,000 contactos/día · Taxonomía diferente a App de Conductores y TMS ⚠️        │     │
│  └─────────────────────────────────────────────────────────────────────────────────────┘     │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA ERP / FINANZAS                                                                         │
│  ┌──────────────────────────────────────────┐  ┌───────────────────────────────────────┐    │
│  │  APP-25 ⚠️                               │  │  APP-26 🗑️                            │    │
│  │  ERP Financiero (On Premises)            │  │  Sistema de Liquidación (Excel)     │    │
│  │  Facturación · Inv. Valorizado           │  │  Penalidades manuales · Error humano  │    │
│  │  Sin integración tiempo real             │  │  Conciliación 23 días · DEPRECAR      │    │
│  └──────────────────────────────────────────┘  └───────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────────────────────┘

Leyenda:  ⚠️ = Problemas críticos / riesgos     🗑️ = Candidato a deprecar

Brechas AS IS (no son cajas en este mapa — definición TO BE en §4 y doc 09):
  · PLT-01 Observabilidad · PLT-03 Bus de Eventos · PLT-04 IaC
  · APP futuras: WMS Cloud (reemplaza APP-06/07) · Servicio Validación (reemplaza APP-05) · Servicio Liquidación (reemplaza APP-26) · etc.
```

---

## 3. Inventario Detallado por Capa

### Capa Transversal — PLT y brechas (AS IS)

> Solo **PLT-02** existe de forma parcial. El resto son **gaps** documentados; la creación TO BE está en §4.

| ID | Aplicación de plataforma | Tipo TOGAF | En AS IS | Estado AS IS | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| PLT-01 | Plataforma de Observabilidad Unificada | Habilitadora | No desplegada | ❌ Gap | Crítica | Monitoreo aislado por cada APP — **crear en TO BE** |
| PLT-02 | Plataforma de Identidad y Accesos (IAM) | Habilitadora | Sí (parcial) | ⚠️ Parcial | Alta | Azure AD básico + OAuth en **APP-01** |
| PLT-03 | Bus de Eventos Central | Integración | No desplegado | ❌ Gap | Crítica | Integraciones P2P — **crear en TO BE** |
| PLT-04 | Plataforma IaC | Arq. Tecnológica | No desplegada | ❌ Gap | Alta | Ver `07_Mapa_Infraestructura.md` — **crear en TO BE** |

---

### Capa Canales

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-03 | Portal B2B (Carga CSV/Excel) | SaaS externo | Nube proveedor | Activo | Media | Carga manual CSV/Excel — deuda técnica a eliminar |
| APP-18 | Portal B2B (Trazabilidad) | SaaS externo | Nube proveedor | ⚠️ Activo | Alta | Muestra estados inconsistentes por eventos fuera de orden |
| APP-19 | Portal Tracking Destinatarios | Web/PWA | SaaS | Activo | Media | Seguimiento para destinatarios finales |
| APP-15 | App de Conductores | Custom Mobile | AWS (ECS/EC2) | ⚠️ Activo | Crítica | Android/iOS · Offline frágil · 1,200 firmas perdidas |

**Brechas de Canales:**
- No existe canal de comunicación proactiva al destinatario (WhatsApp/SMS antes de la entrega)
- APP-18 (Portal B2B de Trazabilidad) y APP-19 muestran datos de fuentes distintas → inconsistencia percibida por el cliente

---

### Capa Integración

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-01 | Azure API Management | PaaS | Azure | Activo | Alta | Gateway de APIs para clientes externos |
| APP-04 | Bucket S3 Legado (archivos) | IaaS | AWS S3 | 🗑️ Activo | Baja | Recepción de CSV/Excel histórica — deprecar |
| APP-21 | Servicio de Notificación (SMS/Email) | SaaS | Proveedor externo | Activo | Media | Notificaciones a destinatarios |
| — | Bus de Eventos / Message Broker | **PLT-03** (gap) | — | ❌ Gap | Crítica | WMS↔TMS↔App de Conductores van punto a punto |

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
| APP-06 | WMS Principal (On Premises) | On Premises · SQL Server (✅ caso) | On Premises | ⚠️ Activo | Crítica | Se degrada en campaña (6h Cyber Days) · Bloqueo de tablas |
| APP-07 | WMS Satélite (On Premises local) | On Premises local (✅ caso) | On Premises local | ⚠️ Activo | Alta | Sync horaria → 4,900 movimientos en conflicto |
| APP-10 | App Handhelds (picking) | ⚠️ Suposición: dispositivo Android o similar | Wi-Fi interno (✅ caso) | Activo | Alta | Operación de picking en almacén |
| APP-11 | TMS (Transportation Management) | Azure (✅ caso) · Tecnología interna no especificada | Azure | Activo | Crítica | Gestión rutas, manifiestos, transportistas |
| APP-12 | Optimizador de Rutas | GCP batch (✅ caso) · Stack interno no especificado | GCP (batch) | ⚠️ Activo | Alta | Solo batch · Datos tráfico desactualizados · 380 rutas inviables |
| APP-13 | Portal Transportistas Tercerizados | ⚠️ Suposición: aplicación web en Azure | Azure | Activo | Media | Acceso a manifiestos para terceros |
| APP-15 | App de Conductores | AWS + DynamoDB (✅ caso) · Framework mobile no especificado | AWS + DynamoDB | ⚠️ Activo | Crítica | Offline frágil · Evidencias perdibles · Motivos texto libre |
| APP-16 | Almacenamiento Evidencias (S3) | AWS S3 (✅ caso) | AWS S3 | Activo | Crítica | Fotos y firmas de entrega — sin hash de integridad |

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
| APP-17 | Pasarela de Pago Contra Entrega | SaaS (proveedor no especificado) | SaaS externo | Activo | Alta | ✅ Caso 6a F4: pagos contra entrega integrados con pasarela SaaS |

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
| APP-25 | ERP Financiero (On Premises) | ⚠️ Suposición: ERP COTS, marca no especificada en el caso | On Premises | ⚠️ Activo | Alta | ✅ Caso 6a F6: facturación en ERP on premises · Sin tiempo real |
| APP-26 | Sistema de Liquidación (penalidades) | Excel / hojas de cálculo | Local (PC usuario) | 🗑️ Activo | Crítica | ✅ Caso 6a F6: notas de crédito calculadas con hojas Excel |

**Brechas de ERP/Finanzas:**
- APP-26 es riesgo crítico operacional y financiero
- APP-25 no se integra en tiempo real con los sistemas cloud

---

## 4. Disposición TO BE — qué se crea, modifica o elimina

> Aquí van los **gaps** de PLT-01, PLT-03 y PLT-04 (y la **completitud** de PLT-02). En AS IS solo se anotan como brecha; **el componente desplegado se define en TO BE**.

| Capa | Acción TO BE | Componentes |
|---|---|---|
| Transversal | **Crear** PLT-01, PLT-03, PLT-04 · **Completar** PLT-02 | Ver iniciativas INI-01 (Bus), INI-07 (Observabilidad/IAM) en doc 10/11 |
| Canales | Mejorar integración + nuevo canal proactivo | APP-15 (rediseño), Portal B2B (Trazabilidad) / APP-18 (datos consistentes), nuevo canal WhatsApp |
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
| Total aplicaciones de negocio desplegadas (APP-01 a APP-26) | 26 |
| Aplicaciones de plataforma en AS IS | 1 parcial (PLT-02) |
| Brechas de plataforma documentadas (gaps) | 3 (PLT-01, PLT-03, PLT-04) — **a resolver en TO BE** |
| Aplicaciones con problemas críticos (⚠️) | 12 |
| Aplicaciones on-premises | 6 |
| Aplicaciones SaaS externas | 7 |
| Aplicaciones cloud (AWS / Azure / GCP) | 13 |
| Candidatas a deprecar (🗑️) | 3 |

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
