# Mapa de Infraestructura
## RutaExpress Fulfillment & Transporte

> **Para el comité de arquitectura** — Topología **multinube AS IS**. **Plataformas de infraestructura:** On Premises (Lima), Cloud MS Azure (EEUU), Cloud AWS (EEUU), Cloud GCP (EEUU), Cloud SaaS - Software as a Service (EEUU). **Mensaje clave:** hoy las integraciones son P2P sin **PLT-03** Bus de Eventos Central; no hay **PLT-01** ni **PLT-04** desplegados. Propuesta TO BE → docs `09`, `10` y `11`.

---

## 1. Propósito

Documentar la **infraestructura tecnológica actual (AS IS)** de RutaExpress: topología de nubes, centros de datos y redes que soportan la operación logística hoy.

---

## 2. Infraestructura AS IS

**Brechas AS IS (plataformas no desplegadas):** PLT-03 Bus de Eventos Central · PLT-01 Plataforma de Observabilidad Unificada · PLT-02 Plataforma de Identidad y Accesos (IAM) (parcial) · PLT-04 Plataforma IaC.

> **Convención:** nombres oficiales en [`06_Mapa_Portafolio_Aplicaciones.md`](06_Mapa_Portafolio_Aplicaciones.md). Formato: **Nombre completo (APP-XX)** o **(PLT-XX)**.

### 2.1 Problemas de Infraestructura AS IS

| Componente | Problema | Impacto |
|---|---|---|
| WMS Principal (On Premises) (APP-06) | Sin capacidad de auto-scaling | Se degrada en campañas (Cyber Days: 6 h caído) |
| WMS Satélite (On Premises local) (APP-07) | Sincronización horaria por lotes | 4.900 movimientos en conflicto en una sola desconexión |
| Integraciones multinube | Punto a punto sin PLT-03 Bus de Eventos Central | Datos inconsistentes entre sistemas |
| Optimizador de Rutas (GCP batch) (APP-12) | Proceso batch, no tiempo real | Rutas con datos de tráfico desactualizados |
| Plataforma de Analítica (GCP batch) (APP-22) | Consolidación semanal | Sin visibilidad operativa en tiempo real |
| ERP Financiero (On Premises) (APP-25) | Sin integración en tiempo real | Facturación con datos desactualizados |
| Red almacenes (conectividad App Handhelds (picking) (APP-10) ↔ WMS) | Wi-Fi sin redundancia | Pérdida de enlace con WMS Principal (On Premises) (APP-06) |

### 2.2 Stack tecnológico AS IS por entorno

> Vista **por plataforma de infraestructura** (nomenclatura unificada con docs `08` y `09`): stack desplegado hoy y comunicación global.

| Plataforma de infraestructura | Stack tecnológico AS IS | Aplicaciones (nombre + ID) |
|---|---|---|
| **On Premises (Lima)** | **Red:** LAN de almacén + WAN privada (sin redundancia)<br>**Cómputo:** servidores/VM legacy<br>**Datos:** SQL Server + BD local + archivos Excel<br>**Seguridad/Operación:** controles perimetrales tradicionales; monitoreo aislado por app | WMS Principal (On Premises) (APP-06), WMS Satélite (On Premises local) (APP-07), Control de Inventario (APP-08), App Handhelds (picking) (APP-10), Sistema Impresión Manifiestos (APP-14), ERP Financiero (On Premises) (APP-25), Sistema de Liquidación (Excel) (APP-26) |
| **Cloud MS Azure (EEUU)** | **Red:** Internet/WAN (sin enlace dedicado)<br>**Servicios:** Azure API Management, AKS<br>**Datos:** BD relacional Azure (suposición APP-02/APP-05/APP-11)<br>**Seguridad/Operación:** OAuth parcial en Azure API Management (APP-01) | Azure API Management (APP-01), Orquestador de Pedidos (APP-02), Validador de Pedidos (APP-05), TMS (Transportation Management) (APP-11), Portal Transportistas Tercerizados (APP-13) |
| **Cloud AWS (EEUU)** | **Red:** Internet público + 4G móvil en campo<br>**Servicios:** Amazon S3, IoT Core, DynamoDB, ECS Fargate<br>**Datos:** DynamoDB (APP-15) + S3 (evidencias/archivos)<br>**Seguridad/Operación:** controles por servicio, sin capa transversal | Bucket S3 Legado (archivos) (APP-04), IoT Core (sensores temperatura) (APP-09), App de Conductores (APP-15), Almacenamiento Evidencias (S3) (APP-16) |
| **Cloud GCP (EEUU)** | **Red:** Internet público desde Azure/AWS<br>**Servicios:** procesamiento batch<br>**Datos:** BigQuery (suposición parcial)<br>**Seguridad/Operación:** operación aislada por dominio analítico | Optimizador de Rutas (GCP batch) (APP-12), Plataforma de Analítica (GCP batch) (APP-22), Dashboards Operativos (APP-23), ML / Optimización de Rutas (GCP) (APP-24) |
| **Cloud SaaS - Software as a Service (EEUU)** | **Red:** HTTPS/API + CSV/SFTP legado<br>**Servicios:** portales, CRM, pagos, notificaciones<br>**Datos:** persistencia del proveedor SaaS | Portal B2B (Carga CSV/Excel) (APP-03), Portal B2B (Trazabilidad) (APP-18), Portal Tracking Destinatarios (APP-19), CRM de Atención al Cliente (APP-20), Pasarela de Pago Contra Entrega (APP-17), Servicio de Notificación (SMS/Email) (APP-21) |

#### Comunicación global AS IS (resumen ejecutivo)

- **On Premises (Lima) ↔ Cloud MS Azure (EEUU):** integración directa P2P por WAN/Internet (sin bus central).
- **Cloud MS Azure (EEUU) ↔ Cloud AWS (EEUU) ↔ Cloud GCP (EEUU):** tráfico por Internet público, sin enlace privado dedicado entre nubes.
- **Campo móvil:** App de Conductores (APP-15) depende de 4G; App Handhelds (picking) (APP-10) depende de Wi-Fi local.
- **Cloud SaaS - Software as a Service (EEUU):** APIs/HTTPS y canal legado CSV/SFTP vía Bucket S3 Legado (archivos) (APP-04).
- **Gap estructural:** no existe Bus de Eventos Central (PLT-03); comunicación acoplada y frágil.

---

## 3. Infraestructura de Red y Conectividad (AS IS)

> **Nota:** Wi-Fi interno del almacén es **conectividad** (red LAN del CD), no plataforma. App Handhelds (picking) (APP-10) corre en **On Premises (Lima)** y se conecta al WMS Principal (On Premises) (APP-06) / WMS Satélite (On Premises local) (APP-07).

| Conexión | Tipo | Problema |
|---|---|---|
| Centros de distribución ↔ WMS Principal (On Premises) (APP-06) | LAN / WAN privada | Sin redundancia, cortes de 74 min registrados |
| App Handhelds (picking) (APP-10) ↔ WMS Principal (On Premises) (APP-06) / WMS Satélite (On Premises local) (APP-07) | Wi-Fi interno | Sin failover, dependencia total de conectividad local |
| App de Conductores (APP-15) ↔ Backend AWS | Internet móvil (4G) | Zonas sin señal → offline → eventos fuera de orden |
| Cloud MS Azure (EEUU) ↔ Cloud GCP (EEUU) | Internet público | Sin SLA de latencia garantizado |
| Cloud MS Azure (EEUU) ↔ Cloud AWS (EEUU) | Internet público | Sin cifrado de tránsito garantizado entre nubes |

---

## 4. Capacidades de Infraestructura por Plataforma (AS IS)

| Plataforma de infraestructura | Fortaleza en AS IS | Aplicaciones desplegadas hoy |
|---|---|---|
| Cloud MS Azure (EEUU) | API Management, AKS | Azure API Management (APP-01), Orquestador de Pedidos (APP-02), Validador de Pedidos (APP-05), TMS (Transportation Management) (APP-11), Portal Transportistas Tercerizados (APP-13) |
| Cloud AWS (EEUU) | S3, DynamoDB, IoT Core, ECS Fargate | App de Conductores (APP-15), Almacenamiento Evidencias (S3) (APP-16), IoT Core (sensores temperatura) (APP-09), Bucket S3 Legado (archivos) (APP-04) |
| Cloud GCP (EEUU) | BigQuery, batch | Optimizador de Rutas (GCP batch) (APP-12), Plataforma de Analítica (GCP batch) (APP-22), ML / Optimización de Rutas (GCP) (APP-24), Dashboards Operativos (APP-23) |
| On Premises (Lima) | ERP, WMS legacy | WMS Principal (On Premises) (APP-06), WMS Satélite (On Premises local) (APP-07), ERP Financiero (On Premises) (APP-25), Sistema de Liquidación (Excel) (APP-26) |
| Cloud SaaS - Software as a Service (EEUU) | Portales, CRM, pagos, notificaciones | Portal B2B (Carga CSV/Excel) (APP-03), Portal B2B (Trazabilidad) (APP-18), Portal Tracking Destinatarios (APP-19), CRM de Atención al Cliente (APP-20), Pasarela de Pago Contra Entrega (APP-17), Servicio de Notificación (SMS/Email) (APP-21) |

---

## 5. Riesgos de Infraestructura (AS IS)

| Riesgo | Probabilidad | Impacto | Situación actual |
|---|---|---|---|
| WMS Principal (On Premises) (APP-06) degradado en campaña | Alta | Crítico | Sin auto-scaling; caídas documentadas en Cyber Days |
| Pérdida de conectividad en almacenes (App Handhelds (picking) (APP-10)) | Media | Alto | Wi-Fi sin redundancia |
| Inconsistencia de datos entre nubes | Alta | Alto | Integraciones P2P sin bus central (PLT-03 no existe) |
| Pérdida de evidencias en App de Conductores (APP-15) | Media | Alto | Offline frágil; sync no atómica |
| Tráfico entre nubes por Internet público | Media | Medio | Latencia variable; costos de egress; sin VPN dedicada |

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
