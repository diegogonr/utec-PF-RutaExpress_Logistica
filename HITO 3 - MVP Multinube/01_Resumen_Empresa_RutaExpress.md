# Resumen de la empresa — RutaExpress
## Fulfillment & Transporte

> **Para el comité** — Contexto de negocio en **5 minutos** antes del dossier MVP. Empieza por [`00_INDICE_COMITE.md`](00_INDICE_COMITE.md). Glosario: índice §8. Detalle Hito 1 → `HITO 1 - Arquitectura Empresarial/`.

---

## 1. Quién es RutaExpress

**RutaExpress Fulfillment & Transporte** es un operador logístico peruano que ofrece **almacenaje (fulfillment)** y **transporte de última milla** para clientes **B2B** (retail, e-commerce, distribuidores) y destinatarios finales **B2C**.

| Dato | Valor |
|---|---|
| Centros de distribución (CD) | **14** en el país |
| Entregas operativas | **~68.000 / día** |
| Picos de campaña (Cyber Days, Navidad) | Hasta **~180.000 / día** |
| Modelo de negocio | Fulfillment + transporte + visibilidad para el cliente |
| Clientes típicos | Marcas que externalizan inventario, picking, despacho y entrega |

---

## 2. Qué hace hoy (cadena de valor)

```text
F1 Recepción → F2 Preparación → F3 Despacho → F4 Entrega → F5 Excepciones → F6 Liquidación
   órdenes        picking/WMS      rutas/TMS       conductores      incidencias      conciliación
```

| Fase | Qué ocurre | Sistemas relevantes (catálogo Hito 1) |
|---|---|---|
| **F1** Recepción | El cliente carga órdenes (API, CSV, portal) | Azure API Management (APP-01), Orquestador de Pedidos (APP-02), Portal B2B (Carga CSV/Excel) (APP-03) / Portal B2B (Trazabilidad) (APP-18) |
| **F2** Preparación | Reserva y picking en almacén | WMS Principal (On Premises) (APP-06), WMS Satélite (APP-07) |
| **F3** Despacho | Rutas y manifiestos | TMS (Transportation Management) (APP-11), Optimizador de Rutas (GCP batch) (APP-12) |
| **F4** Entrega | Conductor entrega y registra evidencia | App de Conductores (APP-15), Almacenamiento Evidencias (S3) (APP-16) |
| **F5** Excepciones | Rechazos, reintentos, devoluciones | App de Conductores (APP-15), CRM de Atención al Cliente (APP-20), portales |
| **F6** Liquidación | Cobro, penalidades, conciliación con cliente | ERP Financiero (On Premises) (APP-25), Sistema de Liquidación (Excel) (APP-26) |

---

## 3. Panorama tecnológico actual (AS IS)

RutaExpress opera en **tres nubes** más sistemas **on premises**:

| Nube / entorno | Rol principal hoy |
|---|---|
| **Azure** | Azure API Management (APP-01), Orquestador de Pedidos (APP-02), TMS (Transportation Management) (APP-11) |
| **AWS** | App de Conductores (APP-15), Almacenamiento Evidencias (S3) (APP-16), IoT Core (sensores temperatura) (APP-09) |
| **GCP** | Optimizador de Rutas (GCP batch) (APP-12), Plataforma de Analítica (GCP batch) (APP-22) |
| **On premises (Lima)** | WMS Principal (On Premises) (APP-06) / WMS Satélite (APP-07), ERP Financiero (On Premises) (APP-25), impresión legada |

**Problema transversal:** muchas integraciones son **punto a punto** (sistema llama directo a sistema), sin **Bus de Eventos Central (PLT-03)** ni observabilidad unificada (**Plataforma de Observabilidad Unificada (PLT-01)** aún no desplegada).

---

## 4. Dolores que motivan la transformación

| Problema del caso | Impacto |
|---|---|
| **32.000 pedidos duplicados** en una campaña | Costo operativo, clientes insatisfechos |
| **WMS on premises 6 h caído** en Cyber Days | **240.000 pedidos** en cola; SLA incumplido |
| **App de Conductores (APP-15)** sin conectividad | 1.200 firmas/evidencias perdidas; disputas y conciliación manual |
| **Inventario fragmentado** entre WMS, Control de Inventario (APP-08) y ERP | Reservas inconsistentes |
| **Liquidación en Excel** — **Sistema de Liquidación (Excel) (APP-26)** | **23 días** de conciliación; capital retenido |
| **Integraciones sin bus de eventos** | Estados distintos entre Azure, AWS y GCP |

---

## 5. Hacia dónde va (TO BE) y qué demuestra este MVP

| Horizonte | Objetivo |
|---|---|
| **Roadmap Hito 1 (36 meses)** | OMS centralizado, WMS Cloud, bus de eventos, última milla resiliente, liquidación automática, observabilidad multinube — **6 iniciativas de transformación INI-01 a INI-06** (cada iniciativa agrupa varias **aplicaciones (APP-XX)**, **plataformas (PLT-XX)** y, donde aplica, **microservicios (MS-INIxx-yy)**; las iniciativas **no** son aplicaciones) |
| **MVP Hito 3 (este paquete)** | Prototipo desplegable que prueba el **núcleo**: orden → reserva → evento → entrega offline → evidencia, en **Azure + AWS + GCP**, con mocks del legado |

El MVP **no reemplaza** todavía el WMS real ni la liquidación completa; demuestra que un **hub central en Azure** (donde ya viven Orquestador de Pedidos (APP-02) y Azure API Management (APP-01)) puede **orquestar orden, bus y Saga** con última milla en AWS y lectura en GCP — antes de invertir en la migración total del legado.

---

## 6. Lectura siguiente

| Orden | Documento |
|:---:|---|
| 1 | [`00_INDICE_COMITE.md`](00_INDICE_COMITE.md) — índice del paquete |
| 2 | **Este resumen** ✓ |
| 3 | [`01b_TOBE_vs_MVP_Alternativa_A.md`](01b_TOBE_vs_MVP_Alternativa_A.md) — marco plano / maqueta / casa entera |
| 4 | [`02_Dossier_MVP_Alternativa_A.md`](02_Dossier_MVP_Alternativa_A.md) — alcance, patrones y decisiones del MVP |
| 5 | [`05_Servicios_por_Nube_MVP.md`](05_Servicios_por_Nube_MVP.md) — catálogo unificado (por nube + explicación de cada servicio) |
| 6 | [`03_C4_Model_MVP.md`](03_C4_Model_MVP.md) — diagramas C4 |
| 7 | [`04_IaC_Costos_Despliegue.md`](04_IaC_Costos_Despliegue.md) — Terraform y costos |
| — | [`06_Preguntas_Argumentos_Comite.md`](06_Preguntas_Argumentos_Comite.md) — *(opcional)* preguntas y argumentos para la defensa oral |

---

*RutaExpress Fulfillment & Transporte — Proyecto Integrador Final UTEC — Arquitectura de Soluciones Multinube*
