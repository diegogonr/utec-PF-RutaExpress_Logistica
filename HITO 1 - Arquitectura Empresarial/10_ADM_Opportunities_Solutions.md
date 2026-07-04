# ADM - Fase E: Opportunities and Solutions
## RutaExpress Fulfillment & Transporte

> **Para el comité de arquitectura** — **Gap analysis** (negocio, datos, apps, tecnología) y **7 iniciativas** (INI-01 … INI-07) con arquitecturas de transición. **Mensaje clave:** priorizar **INI-01** (**PLT-03** Bus de Eventos Central) e **INI-02** (WMS Cloud reemplaza WMS Principal (On Premises) (APP-06) / WMS Satélite (On Premises local) (APP-07)); quick wins **INI-03** (**APP-15**) e **INI-06** (Servicio de Validación de Órdenes — reemplaza **APP-05**).

---

## 1. Propósito

Identificar y consolidar las brechas (gaps) entre el estado AS IS y el TO BE en las dimensiones de Negocio, Datos, Aplicaciones y Tecnología. Agrupar estas brechas en iniciativas o proyectos priorizados, y definir las arquitecturas de transición necesarias.

---

## 2. Análisis de Brechas (GAP Analysis)

### 2.1 Gaps de Negocio

| ID Gap | Descripción | Impacto | Dominio |
|---|---|---|---|
| GN-01 | Sin validación integral de órdenes (dirección, SKU, duplicados) antes de ingresar al flujo | Alto - 6% órdenes con defectos, incidente 32K duplicados | Recepción |
| GN-02 | Gestión de excepciones sin taxonomía normalizada impide aprender y prevenir | Alto - 34% fallas prevenibles, USD 1.20-2.80/reintento | Última Milla |
| GN-03 | Sin comunicación proactiva con destinatario antes de la entrega | Alto - ausencia/dirección = 34% de fallas | Última Milla |
| GN-04 | Proceso de liquidación manual con **APP-26** Sistema de Liquidación (Excel) y conciliación de 23 días | Alto - USD 2.4M retenidos, 7% facturas observadas | Liquidación |
| GN-05 | Sin visibilidad operativa en tiempo real (Plataforma de Analítica (GCP batch) (APP-22) en batch, sin Plataforma de Observabilidad Unificada (PLT-01)) | Medio - planners trabajan con datos del día anterior | Analítica |
| GN-06 | Asignación manual de rutas en 17% de casos sin causa documentada | Medio - costos elevados, SLA en riesgo | Transporte |

### 2.2 Gaps de Datos

| ID Gap | Descripción | Impacto | Dominio |
|---|---|---|---|
| GD-01 | Sin modelo canónico de estados entre **APP-06**, **APP-11**, **APP-15** y **APP-18** Portal B2B (Trazabilidad) | Crítico - estados contradictorios visibles al cliente | Todos |
| GD-02 | Múltiples fuentes de verdad para inventario (**APP-06**, **APP-07**, **APP-25** ERP) | Alto - 2.8% movimientos con ajuste, conflictos en reconexión | Almacén |
| GD-03 | Eventos de tracking sin orden garantizado, pérdida en offline | Alto - 1,200 entregas sin firma, clientes disputan estados | Tracking |
| GD-04 | **APP-22** Plataforma de Analítica semanal, sin **PLT-01** | Medio - no se detectan degradaciones hasta que explotan | Analítica |
| GD-05 | Datos de excepciones inconsistentes impiden entrenar **APP-24** ML | Medio - **APP-12** Optimizador aprende con datos sucios | ML/Rutas |

### 2.3 Gaps de Aplicaciones

| ID Gap | Descripción | Impacto | Dominio |
|---|---|---|---|
| GA-01 | **APP-06** WMS Principal (On Premises) sin capacidad de auto-scaling ni HA | Crítico - degradación en Cyber Days, USD 1.1M penalidades | Almacén |
| GA-02 | **APP-02** Orquestador sin backpressure por cliente ni prioridad SLA | Crítico - cola sin control ante degradación WMS | Recepción |
| GA-03 | **APP-12** Optimizador de Rutas en batch, no tiempo real | Alto - rutas inviables por datos de tráfico desactualizados | Transporte |
| GA-04 | **APP-15** App de Conductores con offline frágil y evidencias que se pierden | Alto - disputas de liquidación, reclamos de custodia | Última Milla |
| GA-05 | Sin **PLT-03** Bus de Eventos central, integraciones punto a punto | Alto - fragilidad, inconsistencia, difícil mantener | Todos |
| GA-06 | Liquidación con **APP-26** Sistema de Liquidación (Excel) sin control | Crítico - errores manuales, penalidades mal calculadas | Liquidación |
| GA-07 | Sin **PLT-01** Plataforma de Observabilidad unificada cross-cloud | Alto - sin visibilidad end-to-end, detección tardía de fallos | Todos |

### 2.4 Gaps de Tecnología

| ID Gap | Descripción | Impacto | Dominio |
|---|---|---|---|
| GT-01 | **APP-06** WMS Principal (On Premises) sobre SQL Server sin escalado ni HA | Crítico - degradación en campañas | Almacén |
| GT-02 | Sin **PLT-04** IaC | Alto - cambios manuales, no reproducibles | Todos |
| GT-03 | Sin **PLT-02** Zero Trust | Alto - APIs expuestas, datos personales en riesgo | Seguridad |
| GT-04 | Sin conexión privada entre nubes (tráfico por Internet público) | Medio - latencia variable, costos de egress, riesgo seguridad | Multinube |
| GT-05 | Sin DR definido para **APP-06** WMS Principal (On Premises) y **APP-11** TMS (Transportation Management) | Alto - RTO/RPO indefinidos | Resiliencia |

---

## 3. Iniciativas / Proyectos

> **Principio de solución:** usar **servicios nativos de Azure, AWS o GCP** (PaaS/IaaS del proveedor). No se proponen herramientas SaaS externas de observabilidad, seguridad o integración (ej. Datadog, OpenTelemetry como producto, Kafka autogestionado). Alcance **medio**: suficiente para operar multinube sin sobre-ingeniería.
>
> **Estructura por iniciativa:** primero los **gaps que cierra** (qué problema resuelve) y después los **beneficios que aporta** (qué valor genera al negocio y a TI).

### INI-01: Plataforma de Integración por Eventos — Bus de Eventos Central (PLT-03)
**Descripción**: Implementar Bus de Eventos Central (PLT-03) con **Azure Event Hubs** como hub principal en Azure, conectores hacia AWS (Amazon EventBridge) y GCP (Pub/Sub) para reemplazar integraciones P2P entre WMS Principal (On Premises) (APP-06), TMS (Transportation Management) (APP-11), App de Conductores (APP-15) y Plataforma de Analítica (GCP batch) (APP-22).

**Resumen de gaps que cierra (5):**

| ID | Dimensión | Brecha resumida |
|---|---|---|
| GA-05 | Aplicaciones | Integraciones punto a punto sin Bus de Eventos Central (PLT-03) — frágiles e inconsistentes |
| GD-01 | Datos | Sin modelo canónico de estados entre WMS (APP-06), TMS (APP-11), App de Conductores (APP-15) y Portal B2B (Trazabilidad) (APP-18) |
| GD-03 | Datos | Eventos de tracking sin orden garantizado; pérdida de datos en modo offline |
| GD-04 | Datos | Analítica en batch semanal; sin base de eventos para detectar degradaciones a tiempo |
| GT-02 | Tecnología | Infraestructura y despliegues del bus sin IaC reproducible (habilitado junto con PLT-04 en INI-07) |

**Beneficios que aporta:**

| Beneficio | Impacto esperado |
|---|---|
| Integración desacoplada | Nuevos consumidores (analítica, liquidación, portales) se conectan al bus sin modificar WMS (APP-06) ni TMS (APP-11) |
| Estados consistentes | Un solo modelo canónico de pedido visible en Portal B2B (Trazabilidad) (APP-18) y App de Conductores (APP-15) |
| Resiliencia operativa | Backpressure y circuit breaker protegen WMS Principal (On Premises) (APP-06) en picos de campaña |
| Auditoría y recuperación | Replay de eventos para reconstruir historial y resolver disputas con trazabilidad |
| Habilitador estratégico | Base obligatoria para WMS Cloud, liquidación automática y analítica en streaming |

**Complejidad**: Alta · **Duración estimada**: 6-9 meses

### INI-02: Modernización WMS — WMS Principal (On Premises) (APP-06) / WMS Satélite (On Premises local) (APP-07) → WMS Cloud
**Descripción**: Migrar WMS Principal (On Premises) (APP-06) y WMS Satélite (On Premises local) (APP-07) a **WMS Cloud custom** en **Azure AKS + Azure SQL Managed Instance** con auto-scaling, modo degradado y sync en tiempo real.

**Resumen de gaps que cierra (4):**

| ID | Dimensión | Brecha resumida |
|---|---|---|
| GA-01 | Aplicaciones | WMS Principal (On Premises) (APP-06) sin auto-scaling ni HA — caída de 6 h en Cyber Days |
| GD-02 | Datos | Inventario desalineado entre WMS Principal (APP-06), WMS Satélite (APP-07) y ERP Financiero (On Premises) (APP-25) |
| GT-01 | Tecnología | SQL Server on premises sin escalado ni alta disponibilidad bajo picos de campaña |
| GT-05 | Tecnología | Sin plan de DR (RTO/RPO) definido para WMS Principal (On Premises) (APP-06) |

**Beneficios que aporta:**

| Beneficio | Impacto esperado |
|---|---|
| Resiliencia en campaña | Auto-scaling absorbe picos de hasta 3× sin caídas de 6 h como en Cyber Days |
| Inventario confiable | Una sola fuente de verdad en tiempo real entre los 14 centros de distribución |
| Continuidad operativa | Modo degradado local con reconciliación automática al reconectar |
| Protección financiera | Evita USD 1.1M+ en penalidades por indisponibilidad en temporadas críticas |
| Precisión operativa | Reduce ajustes de inventario de 2.8% a menos de 0.5% |

**Complejidad**: Muy Alta · **Duración estimada**: 9-12 meses

### INI-03: App de Conductores (APP-15) Resiliente (Offline + Evidencias)
**Descripción**: Rediseñar App de Conductores (APP-15) con SQLite cifrado, sync atómica hacia Almacenamiento Evidencias (S3) (APP-16), taxonomía de excepciones y MDM.

**Resumen de gaps que cierra (3):**

| ID | Dimensión | Brecha resumida |
|---|---|---|
| GA-04 | Aplicaciones | App de Conductores (APP-15) con offline frágil y evidencias perdidas (1.200 firmas en campaña) |
| GD-03 | Datos | Tracking sin orden garantizado; eventos fuera de secuencia al reconectar |
| GN-02 | Negocio | Excepciones sin taxonomía normalizada — 34% de fallas prevenibles no se aprenden |

**Beneficios que aporta:**

| Beneficio | Impacto esperado |
|---|---|
| Evidencias inviolables | Firma, foto y GPS se preservan aunque el conductor reinstale la app o cambie de equipo |
| Confianza comercial | Elimina disputas de custodia y cobros retenidos (~USD 180K en un solo incidente) |
| Datos accionables | Taxonomía de excepciones alimenta ML / Optimización de Rutas (GCP) (APP-24) con datos limpios |
| Operación en campo | Conductores trabajan con seguridad en zonas sin señal 4G |
| Cumplimiento legal | Trazabilidad de entrega auditable para clientes y reguladores |

**Complejidad**: Media · **Duración estimada**: 3-4 meses

### INI-04: Optimizador de Rutas en Tiempo Real (reemplaza Optimizador de Rutas (GCP batch) (APP-12))
**Descripción**: Migrar Optimizador de Rutas (GCP batch) (APP-12) de batch a streaming (GKE + Cloud Pub/Sub) con re-optimización dinámica.

**Resumen de gaps que cierra (3):**

| ID | Dimensión | Brecha resumida |
|---|---|---|
| GA-03 | Aplicaciones | Optimizador de Rutas (GCP batch) (APP-12) solo en batch — rutas con tráfico desactualizado |
| GN-06 | Negocio | 17% de rutas corregidas manualmente sin causa documentada |
| GD-05 | Datos | Datos de excepciones inconsistentes impiden entrenar ML / Optimización de Rutas (GCP) (APP-24) |

**Beneficios que aporta:**

| Beneficio | Impacto esperado |
|---|---|
| Rutas viables | Re-optimización cada 30 min con tráfico y excepciones actualizados |
| Eficiencia operativa | Reduce el 17% de rutas corregidas manualmente por planners |
| Ahorro directo | Meta −15% costo por entrega → USD 2M+/año sobre 68K entregas diarias |
| Cumplimiento SLA | Menos entregas fuera de ventana por rutas obsoletas |
| Visibilidad para planners | Dashboard en tiempo real de rutas activas y desvíos |

**Complejidad**: Alta · **Duración estimada**: 6-8 meses

### INI-05: Automatización Liquidación — reemplaza Sistema de Liquidación (Excel) (APP-26)
**Descripción**: Reemplazar Sistema de Liquidación (Excel) (APP-26) con microservicio **.NET 8 en Azure AKS + Azure SQL Database** que concilia WMS Principal (On Premises) (APP-06), TMS (Transportation Management) (APP-11), App de Conductores (APP-15) y ERP Financiero (On Premises) (APP-25) en tiempo real.

**Resumen de gaps que cierra (3):**

| ID | Dimensión | Brecha resumida |
|---|---|---|
| GA-06 | Aplicaciones | Sistema de Liquidación (Excel) (APP-26) manual — errores y penalidades mal calculadas |
| GN-04 | Negocio | Conciliación de hasta 23 días; USD 2.4M retenidos; 7% facturas observadas |
| GD-04 | Datos | Datos de liquidación desactualizados; sin fuente única para conciliar en tiempo real |

**Beneficios que aporta:**

| Beneficio | Impacto esperado |
|---|---|
| Conciliación ágil | De 23 días a menos de 1 día entre operación y facturación |
| Recuperación de caja | Libera USD 2.4M retenidos por un solo cliente en disputa |
| Calidad de facturación | Facturas observadas bajan de 7% a menos de 1.5% |
| Automatización de reglas | Penalidades y tarifas calculadas sin Excel ni errores manuales |
| Transparencia B2B | Portal de conciliación para clientes con estados alineados al ERP Financiero (On Premises) (APP-25) |

**Complejidad**: Alta · **Duración estimada**: 5-7 meses

### INI-06: Servicio de Validación de Órdenes (reemplaza APP-05) + Orquestador de Pedidos (APP-02)
**Descripción**: Crear **Servicio de Validación de Órdenes** en Cloud MS Azure (EEUU) (NUEVO — reemplaza y elimina Validador de Pedidos (APP-05) en TO BE F1) y fortalecer Orquestador de Pedidos (APP-02) con validación en tiempo real y comunicación proactiva (Servicio de Notificación (SMS/Email) (APP-21)).

**Resumen de gaps que cierra (3):**

| ID | Dimensión | Brecha resumida |
|---|---|---|
| GN-01 | Negocio | Sin validación integral al ingreso — 6% órdenes con defectos; incidente 32K duplicados |
| GN-03 | Negocio | Sin comunicación proactiva al destinatario — 34% fallas por ausencia/dirección |
| GD-01 | Datos | Estados y validaciones inconsistentes desde el origen del pedido |

**Beneficios que aporta:**

| Beneficio | Impacto esperado |
|---|---|
| Calidad al ingreso | Dirección, SKU y duplicados validados antes de reservar inventario |
| Prevención de incidentes | Evita repetición de eventos masivos (32K pedidos duplicados) |
| Menos fallas en ruta | Reduce entregas fallidas de 12.5% hacia 7% al corregir dirección y ausencia |
| Experiencia destinatario | Ventana horaria confirmada por SMS/email antes de salir el camión |
| Ahorro operativo | USD 1.58M/año menos en reintentos (8,500 fallas/día × 34% prevenibles) |

**Complejidad**: Media · **Duración estimada**: 3-5 meses

### INI-07: Plataforma de Observabilidad Unificada (PLT-01) + Plataforma de Identidad y Accesos (IAM) (PLT-02) + Plataforma IaC (PLT-04)

**Descripción**: Habilitadores transversales usando **solo servicios nativos de nube** (Azure, AWS, GCP), con alcance **medio** — sin herramientas SaaS externas de observabilidad ni seguridad.

| PLT | Solución propuesta (servicios nativos) | Alcance |
|---|---|---|
| **PLT-01** Plataforma de Observabilidad Unificada | **Azure:** Azure Monitor + Application Insights + Log Analytics (tablero central operativo)<br>**AWS:** Amazon CloudWatch (métricas/logs de App de Conductores (APP-15), IoT Core (sensores temperatura) (APP-09))<br>**GCP:** Google Cloud Logging + Cloud Trace (Optimizador de Rutas (GCP batch) (APP-12), Plataforma de Analítica (GCP batch) (APP-22)) | Correlación básica cross-cloud vía exportación a Azure Monitor; alertas por umbral en servicios críticos |
| **PLT-02** Plataforma de Identidad y Accesos (IAM) | **Azure:** Microsoft Entra ID (Azure AD) + MFA + Azure Key Vault + políticas OAuth en Azure API Management (APP-01)<br>**AWS:** IAM roles/policies para App de Conductores (APP-15) y Almacenamiento Evidencias (S3) (APP-16) | Identidad central en Azure; accesos mínimos en AWS; sin SIEM/DLP de terceros en esta fase |
| **PLT-04** Plataforma IaC | **Terraform** (repos Git de TI) para Azure, AWS y GCP | Plantillas versionadas multinube; despliegue reproducible en ambientes dev/staging/prod |

**Resumen de gaps que cierra (5):**

| ID | Dimensión | Brecha resumida |
|---|---|---|
| GA-07 | Aplicaciones | Sin Plataforma de Observabilidad Unificada (PLT-01) cross-cloud — detección tardía de fallos |
| GN-05 | Negocio | Sin visibilidad operativa en tiempo real — planners con datos del día anterior |
| GT-02 | Tecnología | Sin Plataforma IaC (PLT-04) — cambios manuales, ambientes no reproducibles |
| GT-03 | Tecnología | Plataforma de Identidad y Accesos (IAM) (PLT-02) incompleta — APIs expuestas, sin MFA unificado |
| GT-04 | Tecnología | Tráfico entre nubes solo por Internet público — latencia y riesgo de seguridad (mejora con **VPN site-to-site cifrada (Azure VPN Gateway)** en fase 1) |

**Beneficios que aporta:**

| Beneficio | Impacto esperado |
|---|---|
| Visibilidad unificada | Tablero central con métricas, logs y trazas de Azure, AWS y GCP |
| Detección temprana | Alertas automáticas antes de que un fallo en WMS (APP-06) o TMS (APP-11) escale a campaña |
| Seguridad reforzada | MFA, WAF y Entra ID central reducen exposición de APIs y datos de destinatarios |
| Despliegues confiables | Terraform garantiza ambientes dev/staging/prod idénticos y auditables |
| Conectividad segura | VPN site-to-site cifrada entre nubes sin costo de ExpressRoute en fase 1 |

**Complejidad**: Media · **Duración estimada**: 4-6 meses

### 3.1 Matriz consolidada — Iniciativa ↔ Gaps ↔ Beneficio clave

| Iniciativa | Gaps (IDs) | Total | Beneficio clave |
|---|---|---|---|
| INI-01 Bus de Eventos Central (PLT-03) | GA-05, GD-01, GD-03, GD-04, GT-02* | 5 | Integración desacoplada y estados canónicos en toda la cadena |
| INI-02 WMS Cloud | GA-01, GD-02, GT-01, GT-05 | 4 | Resiliencia en campaña y inventario único en 14 CDs |
| INI-03 App de Conductores (APP-15) | GA-04, GD-03, GN-02 | 3 | Cero pérdida de evidencias y datos limpios para ML |
| INI-04 Optimizador tiempo real (APP-12) | GA-03, GN-06, GD-05 | 3 | Rutas viables en tiempo real y −15% costo por entrega |
| INI-05 Servicio de Liquidación (APP-26) | GA-06, GN-04, GD-04 | 3 | Conciliación <1 día y recuperación de caja retenida |
| INI-06 Servicio de Validación (reemplaza APP-05) + APP-02 | GN-01, GN-03, GD-01 | 3 | Órdenes válidas al ingreso y menos reintentos en ruta |
| INI-07 PLT-01 + PLT-02 + PLT-04 | GA-07, GN-05, GT-02, GT-03, GT-04 | 5 | Visibilidad multinube, seguridad y despliegues reproducibles |

*\* GT-02 se cierra principalmente en INI-07 (PLT-04); INI-01 lo habilita al estandarizar despliegue del bus.*

**Gaps sin iniciativa exclusiva (requieren combinación):** GA-02 (Orquestador de Pedidos (APP-02) sin backpressure) se aborda en INI-01 + INI-06; GD-01 y GD-03 son compartidos entre INI-01, INI-03 e INI-06.

---

## 4. Arquitecturas de Transición

### Estado AS IS → TO BE

```
AS IS (Año 0):
────────────────────────────────────────────────
• WMS Principal (On Premises) (APP-06) — SQL Server
• Integraciones P2P (sin Bus de Eventos Central (PLT-03))
• Optimizador de Rutas (GCP batch) (APP-12)
• App de Conductores (APP-15) offline frágil
• Sistema de Liquidación (Excel) (APP-26)
• Sin Plataforma de Observabilidad Unificada (PLT-01)

         │
         ▼

TRANSICIÓN 1 (Año 1 - primeros 12 meses):
────────────────────────────────────────────────
• Bus de Eventos Central (PLT-03) operativo (Azure Event Hubs)
• Orquestador de Pedidos (APP-02) con backpressure
• App de Conductores (APP-15) rediseñada (offline + taxonomía)
• Servicio de Validación de Órdenes (reemplaza Validador de Pedidos (APP-05))
• Plataforma IaC (PLT-04) — **Terraform** en repos Git
• Plataforma de Observabilidad Unificada (PLT-01) básica — **Azure Monitor + Application Insights** + CloudWatch
• WMS Principal (On Premises) (APP-06) en modo puente (API, sin migración aún)

         │
         ▼

TRANSICIÓN 2 (Año 2 - meses 12-24):
────────────────────────────────────────────────
• WMS Cloud (reemplaza WMS Principal (On Premises) (APP-06) / WMS Satélite (On Premises local) (APP-07))
• Optimizador de Rutas en Tiempo Real (reemplaza Optimizador de Rutas (GCP batch) (APP-12)) — GKE + Pub/Sub
• Servicio de Liquidación (reemplaza Sistema de Liquidación (Excel) (APP-26))
• Servicio de Notificación (SMS/Email) (APP-21) — comunicación proactiva
• Plataforma de Identidad y Accesos (IAM) (PLT-02) — Entra ID + MFA + Key Vault
• Plataforma de Analítica (GCP batch) (APP-22) streaming — BigQuery + Dataflow
• ERP Financiero (On Premises) (APP-25) integrado en tiempo real

         │
         ▼

TO BE (Año 3 - meses 24-36):
────────────────────────────────────────────────
• Plataforma logística digital completa
• Event Store canónico como fuente única de verdad
• ML predictivo para rutas y detección de excepciones
• Auto-scaling ante cualquier pico (hasta 3x)
• Disponibilidad 99.9% en campaña
• Conciliación automática <1 día
• 98% trazabilidad confiable
• Plataforma de Identidad y Accesos (IAM) (PLT-02) + observabilidad nativa multinube (PLT-01) operativas
```

### Diagrama de Transición

```
┌────────────┐     ┌────────────────────┐     ┌────────────────────┐     ┌──────────┐
│   AS IS    │────►│  TRANSICIÓN 1      │────►│  TRANSICIÓN 2      │────►│  TO BE   │
│            │     │                    │     │                    │     │          │
│ WMS        │     │ Bus de Eventos +   │     │ WMS Cloud +        │     │ Platform │
│ Principal  │     │ App de             │     │ Optimizador de     │     │ Digital  │
│ (On        │     │ Conductores v2 +   │     │ Rutas en Tiempo    │     │ Completa │
│ Premises)  │     │ Validación +       │     │ Real + Liquidación │     │          │
│ Batch      │     │ IaC + Observab.    │     │ + IAM (PLT-02) +   │     │          │
│ Integ P2P  │     │ nativa (PLT-01)    │     │ Analítica Stream.  │     │          │
│ Sistema de │     │                    │     │                    │     │          │
│ Liquidación│     │                    │     │                    │     │          │
│ (Excel)    │     │                    │     │                    │     │          │
└────────────┘     └────────────────────┘     └────────────────────┘     └──────────┘
   Hoy             Año 1 (mes 12)              Año 2 (mes 24)             Año 3 (mes 36)
```

---

## 5. Priorización de Iniciativas (Valor vs Esfuerzo)

```
ALTO VALOR / BAJO ESFUERZO (Quick Wins):
  ► INI-03: **APP-15** App de Conductores Resiliente (3-4 meses)
  ► INI-06: Servicio de Validación de Órdenes (reemplaza **APP-05**) (3-5 meses)

ALTO VALOR / ALTO ESFUERZO (Apuestas Estratégicas):
  ► INI-01: **PLT-03** Bus de Eventos Central
  ► INI-02: WMS Cloud (reemplaza **APP-06**/**APP-07**)
  ► INI-04: **APP-12** Optimizador Tiempo Real
  ► INI-05: Liquidación (reemplaza **APP-26**)

MEDIO VALOR / MEDIO ESFUERZO (Habilitadores nativos cloud):
  ► INI-07: Plataforma de Observabilidad Unificada (PLT-01) + Plataforma de Identidad y Accesos (IAM) (PLT-02) + Plataforma IaC (PLT-04) — servicios Azure/AWS/GCP, complejidad media
```

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
