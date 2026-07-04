# Mapa Portafolio de Aplicaciones
## RutaExpress Fulfillment & Transporte

> **Para el comité de arquitectura** — **Catálogo maestro único del Hito 1**: veintiséis aplicaciones de negocio (APP-01 … APP-26) y cuatro plataformas (PLT-01 … PLT-04). **Convención obligatoria:** siempre **nombre oficial + (APP-XX)** o **(PLT-XX)** juntos en todo el Hito 1. Stack, BD y mapa tecnológico por entorno → doc `08`. Infraestructura y red → doc `07`.

---

## 1. Propósito

Inventario de las aplicaciones de RutaExpress, clasificadas por **capa arquitectónica**. Permite identificar redundancias, obsolescencia, riesgos tecnológicos y **brechas** (*gaps*) entre lo desplegado hoy (AS IS) y lo que exige la arquitectura objetivo (TO BE).

### Convención AS IS vs TO BE

| Pregunta | Respuesta |
|---|---|
| **¿Incluyo plataformas (PLT)?** | **Sí, si están desplegadas o parcialmente desplegadas** (ej. **PLT-02** Plataforma de Identidad y Accesos (IAM) con Azure AD + OAuth en **APP-01**). Son apps habilitadoras TOGAF, no APP de negocio. |
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

### Convención — Plataforma, origen y “tercerizado”

En el catálogo se usan **tres clasificaciones distintas**. No son intercambiables:

| Dimensión | Pregunta que responde | Valores típicos | Ejemplo |
|---|---|---|---|
| **Plataforma AS IS** | ¿**Dónde** corre o se despliega? | Azure, AWS, GCP, On Premises, SaaS *(catálogo)* · ver nombres con región en doc `07` §2.2 | App de Conductores (APP-15) → **AWS** |
| **Origen** | ¿**Quién** provee el software? | Custom, COTS, SaaS externo, PaaS/IaaS proveedor, Manual | CRM (APP-20) → **SaaS externo** (vendor, no código propio) |
| **Usuario de negocio** | ¿**Quién** lo usa en operación? | Interno RutaExpress, cliente B2B, destinatario, transportista tercerizado | Portal Transportistas (APP-13) → **transportistas tercerizados**; la app es **Custom** en **Azure** |

**Aclaraciones:**

- **SaaS** en *Plataforma* = el software lo **hostea un proveedor** (nube del vendor). No implica por sí solo que sea “tercerizado” en sentido operativo.
- **SaaS externo** en *Origen* = producto **contratado** a un vendor; RutaExpress **no desarrolla ni opera** el código (CRM, pasarela, portales B2B del caso).
- **Custom** = desarrollada o mantenida por **TI RutaExpress** (orquestador, app de conductores, portal transportistas, etc.).
- **COTS ⚠️** = producto comercial licenciado; el caso **no indica marca** (WMS, TMS, ERP).
- **PaaS/IaaS proveedor** = servicio gestionado de la nube (API Management, S3, IoT Core) — no es una app de negocio “propia”, sino capacidad del proveedor cloud.
- **Transportista tercerizado** ≠ **software externo**: APP-13 es **Custom en Azure** para usuarios externos a la nómina, pero **pertenece al ecosistema RutaExpress**.

Principio de arquitectura (doc `01`, PA-03): funciones **no diferenciadoras** (CRM, portales B2B, pagos) → preferencia por **SaaS externo** frente a desarrollo propio.

### Catálogo oficial de aplicaciones (APP-01 a APP-26)

| ID | Nombre oficial | Origen | Plataforma AS IS | Término en Caso 6a/6b |
|---|---|---|---|---|
| APP-01 | Azure API Management | PaaS proveedor (Microsoft) | Azure | Azure API Management |
| APP-02 | Orquestador de Pedidos | Custom | Azure AKS | Orquestador en AKS |
| APP-03 | Portal B2B (Carga CSV/Excel) | SaaS externo | SaaS | Portal SaaS — carga manual CSV/Excel |
| APP-04 | Bucket S3 Legado (archivos) | PaaS/IaaS proveedor (AWS) | AWS S3 | Bucket S3 histórico |
| APP-05 | Validador de Pedidos | Custom ⚠️ inferido | Azure AKS | Validador / deduplicación (inferido) |
| APP-06 | WMS Principal (On Premises) | COTS o Custom ⚠️ | On Premises · SQL Server | WMS principal / WMS on premises |
| APP-07 | WMS Satélite (On Premises local) | COTS o Custom ⚠️ | On Premises local | WMS local / versión local sync horaria |
| APP-08 | Control de Inventario | COTS o Custom ⚠️ inferido | On Premises | *(inferido del ERP/WMS)* |
| APP-09 | IoT Core (sensores temperatura) | PaaS proveedor (AWS) | AWS IoT Core | AWS IoT Core |
| APP-10 | App Handhelds (picking) | Custom ⚠️ inferido | On Premises · dispositivo móvil | Handhelds |
| APP-11 | TMS (Transportation Management) | COTS o Custom ⚠️ | Azure | TMS en Azure |
| APP-12 | Optimizador de Rutas (GCP batch) | Custom ⚠️ | GCP | Optimización de rutas en GCP (batch) |
| APP-13 | Portal Transportistas Tercerizados | Custom ⚠️ inferido | Azure | Portal transportistas tercerizados |
| APP-14 | Sistema Impresión Manifiestos | Custom legacy ⚠️ | On Premises | Manifiestos impresos localmente |
| APP-15 | App de Conductores | Custom | AWS · DynamoDB | App de conductores en AWS |
| APP-16 | Almacenamiento Evidencias (S3) | PaaS/IaaS proveedor (AWS) | AWS S3 | Evidencias en S3 |
| APP-17 | Pasarela de Pago Contra Entrega | SaaS externo | SaaS | Pasarela SaaS pagos contra entrega |
| APP-18 | Portal B2B (Trazabilidad) | SaaS externo | SaaS | Portal SaaS de clientes (trazabilidad) |
| APP-19 | Portal Tracking Destinatarios | SaaS externo ⚠️ inferido | SaaS | Tracking destinatarios finales *(inferido F4)* |
| APP-20 | CRM de Atención al Cliente | SaaS externo | SaaS | CRM SaaS |
| APP-21 | Servicio de Notificación (SMS/Email) | SaaS externo ⚠️ inferido | SaaS | Notificaciones a destinatarios *(inferido)* |
| APP-22 | Plataforma de Analítica (GCP batch) | Custom ⚠️ | GCP | Analítica en GCP (semanal) |
| APP-23 | Dashboards Operativos | Custom ⚠️ inferido | GCP | Reportes operativos *(inferido F6)* |
| APP-24 | ML / Optimización de Rutas (GCP) | Custom ⚠️ | GCP | Algoritmo de rutas en GCP (Caso 6b R3) |
| APP-25 | ERP Financiero (On Premises) | COTS ⚠️ | On Premises | ERP on premises |
| APP-26 | Sistema de Liquidación (Excel) | Manual (hoja de cálculo) | Local · Excel | Hojas Excel penalidades |

**Resumen por origen (AS IS):**

| Origen | APP | Cantidad |
|---|---|---|
| Custom (desarrollo RutaExpress) | APP-02, APP-05, APP-10, APP-12, APP-13, APP-14, APP-15, APP-22, APP-23, APP-24 | 10 |
| SaaS externo (vendor) | APP-03, APP-17, APP-18, APP-19, APP-20, APP-21 | 6 |
| COTS o Custom ⚠️ (caso no especifica) | APP-06, APP-07, APP-08, APP-11, APP-25 | 5 |
| PaaS/IaaS proveedor cloud | APP-01, APP-04, APP-09, APP-16 | 4 |
| Manual | APP-26 | 1 |

> En tablas, diagramas y narrativa usar **siempre nombre oficial + (APP-XX)** o **(PLT-XX)** juntos. Prohibido mencionar solo el ID o solo el nombre. Ejemplo: *Azure API Management (APP-01)* · *Plataforma de Observabilidad Unificada (PLT-01)*.
>
> **Plataforma vs conectividad:** en la columna *Plataforma* van Azure, AWS, GCP, On Premises, SaaS, etc. (dónde se ejecuta o despliega la app). La **red Wi-Fi interna del almacén** no es plataforma: es **conectividad** (Fase D — ver `07_Mapa_Infraestructura.md`, *Red almacenes*). Ejemplo: App Handhelds (APP-10) → plataforma **On Premises** (dispositivo en el CD); se conecta al WMS por **Wi-Fi interno**.

**Prohibido abreviar nombres oficiales:** no usar Mgmt, Svc, On-Prem, RT, Driver, Bucket sin el nombre completo del catálogo. Ejemplos incorrectos → correctos: `Azure API Mgmt` → **Azure API Management**; `S3 Bucket Legado` → **Bucket S3 Legado (archivos)**; `Notification Svc` → **Servicio de Notificación (SMS/Email)**; `Optimizador RT` → **Optimizador de Rutas en Tiempo Real**.

### Aplicaciones de plataforma (PLT-01 a PLT-04) — capa transversal TOGAF

Según **TOGAF ADM · Fase C (Arquitectura de Aplicaciones)**, el **Application Portfolio / Application Landscape** no incluye solo aplicaciones de negocio: también cataloga **aplicaciones habilitadoras o de plataforma** (*platform / enabling / infrastructure applications*) que dan servicio transversal al resto.

Por eso **sí corresponde** que aparezcan en este mapa, en la **capa transversal**, pero **clasificadas aparte** de APP-01 a APP-26:

| Clasificación TOGAF | ID RutaExpress | Qué incluye |
|---|---|---|
| **Aplicaciones de negocio u operacionales** | APP-01 … APP-26 | WMS, TMS, portales, App de Conductores, ERP, etc. |
| **Aplicaciones de plataforma / habilitadoras** | PLT-01 … PLT-04 | Observabilidad, identidad, bus de eventos (cuando existan como componentes desplegados) |
| **Servicios tecnológicos** (Fase D — Arq. Tecnológica) | *(sin ID APP/PLT)* | IaC (Terraform), redes, cómputo — ver `07_Mapa_Infraestructura.md` |

| ID | Aplicación de plataforma | Tipo TOGAF | Origen | AS IS (este mapa) | TO BE (§4 y doc 09) |
|---|---|---|---|---|---|
| PLT-01 | Plataforma de Observabilidad Unificada | Habilitadora | A crear — **Azure Monitor + Application Insights** | ❌ **Gap** — no desplegada; monitoreo aislado por APP | Crear: observabilidad unificada cross-cloud |
| PLT-02 | Plataforma de Identidad y Accesos (IAM) | Habilitadora | Híbrido — **PaaS Microsoft (Azure AD)** + políticas OAuth en **APP-01** (config propia) | ⚠️ **Parcial** | Completar: MFA + Zero Trust + políticas IAM |
| PLT-03 | Bus de Eventos Central | Integración / middleware | A crear — **Azure Event Hubs** | ❌ **Gap** — no existe; integraciones P2P | Crear: bus central multinube |
| PLT-04 | Plataforma IaC | Arq. Tecnológica (Fase D) | A crear — Terraform (capacidad propia TI + repos) | ❌ **Gap** — infra manual *(ver doc 07)* | Crear: IaC multinube |

> **Gap ≠ aplicación en producción.** Un gap es una **entrada de catálogo + brecha documentada**: identifica *qué falta* en AS IS y *qué se creará* en TO BE. No se cuenta como “26 + 4 apps activas”; se cuenta aparte en el resumen de brechas.

> **Política OAuth 2.0** no es una aplicación: es una **configuración** de **APP-01 Azure API Management**. **Azure AD** es el PaaS de Microsoft que **sustenta parcialmente** **PLT-02 Plataforma de Identidad y Accesos (IAM)** — no sustituye a PLT-02 ni convierte APP-01 en PLT-02.

---

## 2. Mapa Visual AS IS por Capas Arquitectónicas

### Regla del diagrama AS IS

El mapa AS IS incluye las veintiséis aplicaciones de negocio que el caso describe como existentes, aunque estén degradadas o marcadas para deprecación, más la Plataforma de Identidad (PLT-02) en estado parcial. Las brechas de Observabilidad (PLT-01), Bus de Eventos (PLT-03) e IaC (PLT-04) no se dibujan como cajas: se listan al pie como hallazgos. En cambio, componentes TO BE como WMS Cloud o el microservicio de liquidación no aparecen en AS IS porque hoy sí existe un WMS on premises y hojas Excel — lo que falta es la versión futura, no la función. Cualquier solución nueva se documenta en la sección TO BE y en el documento de fases.

| En el mapa AS IS **sí van** | En el mapa AS IS **no van** (van en **§4 TO BE** o doc `09`) |
|---|---|
| Aplicaciones desplegadas (APP-01 … APP-26), aunque tengan ⚠️ o 🗑️ | Plataformas en brecha: Observabilidad (PLT-01), Bus (PLT-03), IaC (PLT-04) |
| Plataforma de Identidad (PLT-02) parcial — Azure AD + OAuth en Azure API Management (APP-01) | Reemplazos TO BE: WMS Cloud, Servicio de Validación, Manifiesto Digital, etc. |
| Brechas anotadas en texto al pie, sin caja | Componentes que aún no existen en producción dibujados como si fueran apps |

### PLT-02 vs APP-01 — aclaración para la exposición

La Plataforma de Identidad y Accesos (PLT-02) y Azure API Management (APP-01) son dos entradas distintas del catálogo y no se fusionan en una sola caja. La plataforma IAM va en la capa transversal con estado parcial; el gateway de APIs va en la capa de integración como aplicación desplegada. La plataforma no “contiene” al gateway: hoy la identidad se cubre en parte con Azure AD y con una política OAuth configurada en Azure API Management (APP-01), pero eso no equivale a MFA, Zero Trust ni SIEM. Por eso documentamos la plataforma como parcial arriba y referenciamos al gateway; la caja desplegada de Azure API Management (APP-01) aparece una sola vez, en integración.

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│              MAPA PORTAFOLIO DE APLICACIONES — AS IS · RUTAEXPRESS                           │
│              (solo componentes desplegados o parciales — ver §4 para TO BE)                  │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA TRANSVERSAL — única PLT desplegada (parcial)                                           │
│  ┌──────────────────────────────────────────────────────────────────────────────────────┐  │
│  │  PLT-02 Plataforma de Identidad y Accesos (IAM)  ⚠️ PARCIAL                          │  │
│  │  Cobertura parcial AS IS: Azure AD (PaaS) + política OAuth 2.0 en                    │  │
│  │  APP-01 Azure API Management (ver caja APP-01 en capa Integración)                   │  │
│  │  ⚠️ Por qué: sin MFA · Zero Trust · SIEM · políticas IAM unificadas                   │  │
│  └──────────────────────────────────────────────────────────────────────────────────────┘  │
│  Brechas TO BE §4 (no desplegadas — sin caja en AS IS):                                      │
│  · PLT-01 Plataforma de Observabilidad Unificada                                             │
│  · PLT-03 Bus de Eventos Central                                                             │
│  · PLT-04 Plataforma IaC (detalle: doc 07)                                                   │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA CANALES (Puntos de contacto con clientes y conductores)                                │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌───────────────────┐  ┌─────────────┐  │
│  │  APP-03 ⚠️          │  │  APP-18 ⚠️          │  │  APP-19           │  │  APP-15 ⚠️ │  │
│  │  Portal B2B         │  │  Portal B2B         │  │  Portal Tracking  │  │  App de     │  │
│  │  (Carga CSV/Excel)  │  │  (Trazabilidad)     │  │  Destinatarios    │  │  Conductores│  │
│  │  (SaaS)             │  │  (SaaS)             │  │  (SaaS)           │  │  (AWS)      │  │
│  │  ⚠️ Carga manual ·  │  │  ⚠️ Estados         │  │                   │  │  ⚠️ Offline │  │
│  │  sin validación auto│  │  inconsistentes     │  │                   │  │  · 1.200    │  │
│  │                     │  │  (eventos desorden) │  │                   │  │  firmas perd.│  │
│  └─────────────────────┘  └─────────────────────┘  └───────────────────┘  └─────────────┘  │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA INTEGRACIÓN — sin PLT-03 Bus de Eventos Central (brecha → TO BE §4)                     │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌───────────────────┐                   │
│  │  APP-01             │  │  APP-04 🗑️          │  │  APP-21           │                   │
│  │  Azure API          │  │  Bucket S3 Legado   │  │  Servicio de      │                   │
│  │  Management         │  │  (archivos)         │  │  Notificación     │                   │
│  │                     │  │  🗑️ SFTP/CSV legado │  │  (SMS/Email)      │                   │
│  │                     │  │  sin validación     │  │                   │                   │
│  └─────────────────────┘  └─────────────────────┘  └───────────────────┘                   │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA CORE (Sistemas Operacionales Centrales del Negocio)                                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐ │
│  │  APP-02 ⚠️          │  │  APP-06 ⚠️          │  │  APP-11             │  │  APP-15 ⚠️            │ │
│  │  Orquestador de     │  │  WMS Principal      │  │  TMS (Transportation│  │  App de Conductores   │ │
│  │  Pedidos (AKS)      │  │  (On Premises)      │  │  Management)        │  │  (AWS / DynamoDB)     │ │
│  │  ⚠️ Sin backpressure│  │  ⚠️ 6 h caído       │  │  (Azure)            │  │  ⚠️ Offline frágil ·  │ │
│  │  · cola ilimitada   │  │  Cyber Days · bloq. │  │                     │  │  1.200 firmas perdidas│ │
│  │  ante WMS lento     │  │  tablas en campaña  │  │                     │  │                       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐ │
│  │  APP-05 ⚠️          │  │  APP-07 ⚠️          │  │  APP-12 ⚠️          │  │  APP-16                 │ │
│  │  Validador de       │  │  WMS Satélite       │  │  Optimizador de     │  │  Almacenamiento         │ │
│  │  Pedidos (AKS)      │  │  (On Premises local)│  │  Rutas (GCP batch)  │  │  Evidencias (S3)        │ │
│  │  ⚠️ Falló dedup.    │  │  ⚠️ Sync horaria ·  │  │  ⚠️ Solo batch ·    │  │                         │ │
│  │  · 32.000 pedidos   │  │  4.900 movim.       │  │  tráfico atrasado · │  │                         │ │
│  │  duplicados (caso)  │  │  en conflicto       │  │  380 rutas inviables│  │                         │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐                                                    │
│  │  APP-10         │  │  APP-13         │                                                    │
│  │  App Handhelds  │  │  Portal         │                                                    │
│  │  (picking)      │  │  Transportistas │                                                    │
│  │  (On Premises)  │  │  Tercerizados   │                                                    │
│  └─────────────────┘  └─────────────────┘                                                    │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA DATA (Almacenamiento · Eventos · Analítica · ML)                                      │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌───────────────────┐  ┌─────────────┐  │
│  │  APP-22 ⚠️          │  │  APP-23 ⚠️          │  │  APP-24 ⚠️          │  │  APP-09             │  │
│  │  Plataforma de      │  │  Dashboards         │  │  ML / Optimización  │  │  IoT Core           │  │
│  │  Analítica (GCP)    │  │  Operativos (GCP)     │  │  de Rutas (GCP)     │  │  (sensores temp.)   │  │
│  │  ⚠️ Solo batch      │  │  ⚠️ Sin datos en      │  │  ⚠️ Entrena con     │  │                     │  │
│  │  semanal · sin      │  │  tiempo real ·        │  │  excepciones        │  │                     │  │
│  │  alertas operativas │  │  fuentes múltiples    │  │  no normalizadas    │  │                     │  │
│  └─────────────────────┘  └─────────────────────┘  └───────────────────┘  └─────────────┘  │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA SOPORTE (Back-office · Operaciones Internas · Almacén)                                │
│  ┌─────────────────────┐  ┌─────────────────────┐  ┌───────────────────────────────────┐    │
│  │  APP-08 🗑️          │  │  APP-14 🗑️          │  │  APP-17                           │    │
│  │  Control de         │  │  Sistema Impresión  │  │  Pasarela de Pago                 │    │
│  │  Inventario         │  │  Manifiestos        │  │  Contra Entrega (SaaS)            │    │
│  │  (On Premises)      │  │  (On Premises)      │  │                                   │    │
│  │  🗑️ Eliminar F2 →   │  │  🗑️ Manifiestos en  │  │                                   │    │
│  │  WMS Cloud (sin     │  │  papel · sin traza  │  │                                   │    │
│  │  app TO BE)         │  │                     │  │                                   │    │
│  └─────────────────────┘  └─────────────────────┘  └───────────────────────────────────┘    │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA CRM / ATENCIÓN AL CLIENTE                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────────────────┐     │
│  │  APP-20 ⚠️                                                                          │     │
│  │  CRM de Atención al Cliente (SaaS) · 18.000 contactos/día                          │     │
│  │  ⚠️ Taxonomía de reclamos distinta a App de Conductores (APP-15) y TMS (Transportation Management) (APP-11) │
│  └─────────────────────────────────────────────────────────────────────────────────────┘     │
├──────────────────────────────────────────────────────────────────────────────────────────────┤
│  CAPA ERP / FINANZAS                                                                         │
│  ┌──────────────────────────────────────────┐  ┌───────────────────────────────────────┐    │
│  │  APP-25 ⚠️                               │  │  APP-26 🗑️                            │    │
│  │  ERP Financiero (On Premises)            │  │  Sistema de Liquidación (Excel)       │    │
│  │  ⚠️ Factura con datos del mes anterior · │  │  🗑️ Conciliación manual 23 días ·     │    │
│  │  sin API tiempo real con operaciones     │  │  USD 2.4M retenidos (1 caso)          │    │
│  └──────────────────────────────────────────┘  └───────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────────────────────────────┘

Leyenda:  ⚠️ = Problemas críticos / riesgos (ver tabla abajo)     🗑️ = Candidato a deprecar
```

Brechas AS IS (no son cajas en el mapa — definición TO BE en §4 y doc 09):

- Plataforma de Observabilidad Unificada (PLT-01)
- Bus de Eventos Central (PLT-03)
- Plataforma IaC (PLT-04)
- WMS Cloud reemplaza WMS Principal (APP-06) y WMS Satélite (APP-07). Control de Inventario (APP-08) **no tiene equivalente TO BE** — se **elimina** en F2 (función absorbida por WMS Cloud).

### Motivos ⚠️ y 🗑️ — consulta rápida

| Aplicación / plataforma | Por qué ⚠️ o 🗑️ |
|---|---|
| Plataforma de Identidad y Accesos (PLT-02) | ⚠️ Parcial: solo Azure AD y OAuth en Azure API Management (APP-01); faltan MFA, Zero Trust y SIEM |
| Portal B2B Carga CSV/Excel (APP-03) | ⚠️ Carga manual sin validación automática |
| Portal B2B Trazabilidad (APP-18) | ⚠️ Estados inconsistentes; eventos offline fuera de orden |
| App de Conductores (APP-15) | ⚠️ Offline frágil; 1.200 firmas perdidas; excepciones en texto libre |
| Orquestador de Pedidos (APP-02) | ⚠️ Sin backpressure; cola ilimitada si WMS Principal (On Premises) (APP-06) se degrada |
| Validador de Pedidos (APP-05) | ⚠️ Falló deduplicación → 32.000 pedidos duplicados |
| WMS Principal On Premises (APP-06) | ⚠️ Seis horas caído en Cyber Days; bloqueo de tablas |
| WMS Satélite On Premises local (APP-07) | ⚠️ Sync horaria → 4.900 movimientos en conflicto |
| Optimizador de Rutas GCP batch (APP-12) | ⚠️ Solo batch; 380 rutas inviables por tráfico atrasado |
| Plataforma de Analítica GCP batch (APP-22) | ⚠️ Consolidación semanal; sin visibilidad operativa |
| Dashboards Operativos (APP-23) | ⚠️ Fuentes múltiples; sin streaming |
| ML Optimización de Rutas (APP-24) | ⚠️ Entrena con excepciones no normalizadas |
| Control de Inventario (APP-08) | 🗑️ Sin app TO BE — eliminar en F2; función absorbida por WMS Cloud |
| CRM de Atención al Cliente (APP-20) | ⚠️ Taxonomía distinta a App de Conductores (APP-15) y TMS (Transportation Management) (APP-11) |
| ERP Financiero On Premises (APP-25) | ⚠️ Factura con datos desactualizados |
| Bucket S3 Legado (APP-04) | 🗑️ Canal CSV/SFTP legado |
| Sistema Impresión Manifiestos (APP-14) | 🗑️ Manifiestos en papel |
| Sistema de Liquidación Excel (APP-26) | 🗑️ Conciliación manual 23 días; USD 2.4M retenidos |

### Guion de exposición al comité

Texto para leer en voz alta (~6 min). Nombre oficial primero; identificador entre paréntesis. Detalle de cada ⚠️ en la tabla de consulta rápida.

#### Apertura

Comité, este es el mapa AS IS del portafolio de RutaExpress, de arriba hacia abajo por capas. Solo incluye lo desplegado hoy, más la Plataforma de Identidad (PLT-02) parcial. Observabilidad (PLT-01), Bus de Eventos (PLT-03) e IaC (PLT-04) son brechas al pie del diagrama; su solución está en TO BE. ⚠️ señala riesgo documentado; 🗑️ marca deprecación propuesta.

#### Capa transversal

Solo la Plataforma de Identidad (PLT-02) está desplegada, e incompleta: Azure AD y OAuth en Azure API Management (APP-01). No hay MFA ni Zero Trust. PLT-02 y APP-01 son catálogos distintos: el gateway aparece abajo, en integración. Observabilidad (PLT-01), Bus (PLT-03) e IaC (PLT-04) no existen aún.

#### Capa canales

Aquí interactúan clientes y conductores. Portal B2B (Carga CSV/Excel) (APP-03) es canal manual legado; Portal B2B (Trazabilidad) (APP-18) muestra estados inconsistentes; Portal Tracking Destinatarios (APP-19) atiende al destinatario final. App de Conductores (APP-15), en AWS, es crítica: offline frágil y mil doscientas firmas perdidas en campaña.

#### Capa integración

Azure API Management (APP-01) es el gateway para clientes grandes; el Bucket S3 Legado (APP-04) recibe CSV por SFTP y debe deprecarse; el Servicio de Notificación (APP-21) avisa a destinatarios. Lo central: no hay Bus de Eventos Central (PLT-03). WMS Principal (On Premises) (APP-06), TMS (Transportation Management) (APP-11), App de Conductores (APP-15) y Plataforma de Analítica (GCP batch) (APP-22) se integran punto a punto — ahí nace gran parte de la inconsistencia de datos.

#### Capa core

Corazón operativo repartido en on premises, Azure, AWS y GCP. En AKS: Orquestador de Pedidos (APP-02) sin backpressure, Validador de Pedidos (APP-05) con falla de deduplicación y TMS (Transportation Management) (APP-11). On premises: WMS Principal (On Premises) (APP-06) — seis horas caído en Cyber Days — y WMS Satélite (On Premises local) (APP-07) con sync horaria conflictiva; las App Handhelds (picking) (APP-10) corren en dispositivos del almacén y se enlazan al WMS por la red Wi-Fi interna del CD. En AWS: App de Conductores (APP-15) y Almacenamiento Evidencias (S3) (APP-16). En GCP batch: Optimizador de Rutas (GCP batch) (APP-12) sin tiempo real. Complementa el Portal Transportistas Tercerizados (APP-13), en Azure, donde los transportistas externos consultan manifiestos y rutas. Es la capa de mayor criticidad.

#### Capa data

Plataforma de Analítica (GCP batch) (APP-22) y Dashboards Operativos (APP-23) consolidan en batch, no sirven para operación en vivo. ML / Optimización de Rutas (GCP) (APP-24) aprende con excepciones no normalizadas. IoT Core (sensores temperatura) (APP-09) monitorea temperatura en cámaras frías pero no alerta a WMS Principal (On Premises) (APP-06). No hay almacén de eventos unificado.

#### Capa soporte

Control de Inventario (APP-08) no refleja stock en tiempo real frente a WMS Principal (On Premises) (APP-06) y WMS Satélite (On Premises local) (APP-07). Sistema Impresión Manifiestos (APP-14), a deprecar, sigue en papel. Pasarela de Pago Contra Entrega (APP-17) cumple su rol como SaaS externo.

#### Capa CRM

CRM de Atención al Cliente (APP-20) recibe unos dieciocho mil contactos al día. Su taxonomía de reclamos no coincide con la App de Conductores (APP-15) ni con el TMS (Transportation Management) (APP-11), lo que dificulta conciliar disputas y medir causas raíz.

#### Capa ERP y finanzas

ERP Financiero on premises (APP-25) factura con datos desactualizados, sin integración en tiempo real con la operación multinube. Sistema de Liquidación en Excel (APP-26), también a reemplazar: conciliación manual de hasta veintitrés días y USD 2.4M retenidos en un solo caso de disputa.

#### Cierre

Veintiséis apps en multinube sin estrategia unificada, identidad parcial (PLT-02) y tres brechas de plataforma. Quince componentes con riesgo; tres a deprecar. El TO BE — sección cuatro y documento nueve — define el camino; inversión y roadmap en el documento once. ¿Preguntas antes de pasar al TO BE?

---

## 3. Inventario Detallado por Capa

### Capa Transversal — PLT y brechas (AS IS)

> Solo **PLT-02** existe de forma parcial. El resto son **gaps** documentados; la creación TO BE está en §4.

| ID | Aplicación de plataforma | Tipo TOGAF | En AS IS | Estado AS IS | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| PLT-01 | Plataforma de Observabilidad Unificada | Habilitadora | No desplegada | ❌ Gap | Crítica | Monitoreo aislado por cada APP — **crear en TO BE** |
| PLT-02 | Plataforma de Identidad y Accesos (IAM) | Habilitadora | Sí (parcial) | ⚠️ Parcial | Alta | Azure AD (PaaS) + política OAuth 2.0 en **APP-01** Azure API Management |
| PLT-03 | Bus de Eventos Central | Integración | No desplegado | ❌ Gap | Crítica | Integraciones P2P — **crear en TO BE** |
| PLT-04 | Plataforma IaC | Arq. Tecnológica | No desplegada | ❌ Gap | Alta | Ver `07_Mapa_Infraestructura.md` — **crear en TO BE** |

---

### Capa Canales

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-03 | Portal B2B (Carga CSV/Excel) | SaaS externo | Nube proveedor | ⚠️ Activo | Media | Carga manual CSV/Excel — sin validación automática |
| APP-18 | Portal B2B (Trazabilidad) | SaaS externo | Nube proveedor | ⚠️ Activo | Alta | Muestra estados inconsistentes por eventos fuera de orden |
| APP-19 | Portal Tracking Destinatarios | Web/PWA | SaaS | Activo | Media | Seguimiento para destinatarios finales |
| APP-15 | App de Conductores | Custom Mobile | AWS (ECS Fargate) | ⚠️ Activo | Crítica | Android/iOS · Offline frágil · 1,200 firmas perdidas |

**Brechas de Canales:**
- No existe canal de comunicación proactiva al destinatario (WhatsApp/SMS antes de la entrega)
- Portal B2B (Trazabilidad) (APP-18) y Portal Tracking Destinatarios (APP-19) muestran datos de fuentes distintas → inconsistencia percibida por el cliente

---

### Capa Integración

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-01 | Azure API Management | PaaS | Azure | Activo | Alta | Gateway de APIs para clientes externos |
| APP-04 | Bucket S3 Legado (archivos) | IaaS | AWS S3 | 🗑️ Activo | Baja | Recepción de CSV/Excel histórica — deprecar |
| APP-21 | Servicio de Notificación (SMS/Email) | SaaS | Proveedor externo | Activo | Media | Notificaciones a destinatarios |
| — | Bus de Eventos / Message Broker | **PLT-03** (gap) | — | ❌ Gap | Crítica | **APP-06**↔**APP-11**↔**APP-15** van P2P |

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
| APP-10 | App Handhelds (picking) | ⚠️ Suposición: dispositivo Android o similar | On Premises · dispositivo móvil | Activo | Alta | Picking en almacén · Conectividad: Wi-Fi interno del CD (✅ caso) — ver red almacenes en doc 07 |
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
| APP-23 | Dashboards Operativos | ⚠️ Suposición: herramienta de BI en GCP, no especificada | GCP | ⚠️ Activo | Media | Datos de fuentes múltiples; sin streaming en tiempo real |
| APP-24 | ML / Optimización Rutas | GCP (✅ caso) · Algoritmo específico no mencionado | GCP (batch) | ⚠️ Activo | Alta | Caso 6b R3: "algoritmo no aprende por datos inconsistentes" |

**Brechas de Data:**
- Sin Event Store centralizado: cada sistema guarda sus propios eventos
- Analítica semanal (**APP-22**) → sin alertas operativas; requiere **PLT-01**
- APP-24 aprende con datos sucios (motivos de excepción no normalizados)

---

### Capa Soporte

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-08 | Control de Inventario | ⚠️ Suposición: sistema complementario al WMS, tecnología no especificada | On Premises | 🗑️ Activo → **eliminar F2** | Alta | No refleja inventario en tiempo real · TO BE: absorbido por WMS Cloud (sin app homóloga) |
| APP-14 | Sistema Impresión Manifiestos | ⚠️ Suposición: aplicación local legacy | On Premises (centros) | 🗑️ Activo | Baja | ✅ Caso 6a F3: manifiestos se imprimen localmente |
| APP-17 | Pasarela de Pago Contra Entrega | SaaS (proveedor no especificado) | SaaS externo | Activo | Alta | ✅ Caso 6a F4: pagos contra entrega integrados con pasarela SaaS |

---

### Capa CRM / Atención al Cliente

| ID | Aplicación | Tipo | Plataforma | Estado | Criticidad | Observaciones |
|---|---|---|---|---|---|---|
| APP-20 | CRM de Atención al Cliente | SaaS externo | Nube proveedor | ⚠️ Activo | Alta | 18,000 contactos/día · Taxonomía de reclamos diferente a TMS (Transportation Management) (APP-11) y App de Conductores (APP-15) |

**Brechas de CRM:**
- Taxonomía de motivos desconectada de TMS (Transportation Management) (APP-11) y App de Conductores (APP-15)
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
| Integración | Reemplazar P2P + deprecar legado | APP-04 (deprecar), APP-21 (mantener), **Azure Event Hubs (PLT-03)** |
| Core | Modernizar críticos + batch→RT | APP-06 y APP-07 → **WMS Cloud**; APP-08 **eliminar** (absorbido por WMS Cloud, sin app TO BE); APP-12 (batch→RT); APP-15 (offline robusto) |
| Data | Pasar a streaming + limpiar datos | APP-22 (streaming), APP-24 (datos limpios), Event Store nuevo |
| Soporte | Deprecar legado | APP-08 **eliminar** (→ WMS Cloud), APP-14 (deprecar), APP-17 (mantener) |
| CRM de Atención al Cliente (APP-20) | Integrar con fuente única | APP-20 (adoptar taxonomía canónica + integrar Event Store) |
| ERP/Finanzas | Automatizar liquidación | APP-25 (API tiempo real), APP-26 (reemplazar con microservicio) |

---

## 5. Resumen del Portafolio

| Dimensión | Cantidad |
|---|---|
| Total aplicaciones de negocio desplegadas (APP-01 a APP-26) | 26 |
| Aplicaciones de plataforma en AS IS | 1 parcial (PLT-02) |
| Brechas de plataforma documentadas (gaps) | 3 (PLT-01, PLT-03, PLT-04) — **a resolver en TO BE** |
| Aplicaciones con problemas críticos (⚠️) | 12 |
| Por **origen** — Custom (TI RutaExpress) | 10 |
| Por **origen** — SaaS externo (vendor) | 6 |
| Por **origen** — COTS o Custom ⚠️ (caso no especifica) | 5 |
| Por **origen** — PaaS/IaaS proveedor cloud | 4 |
| Por **origen** — Manual (Excel) | 1 |
| Por **plataforma** — on-premises | 6 |
| Por **plataforma** — SaaS (hosting vendor) | 6 |
| Por **plataforma** — cloud AWS / Azure / GCP | 13 |
| Candidatas a deprecar / eliminar (🗑️) | 4 (APP-04, APP-08, APP-14, APP-26) |

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
