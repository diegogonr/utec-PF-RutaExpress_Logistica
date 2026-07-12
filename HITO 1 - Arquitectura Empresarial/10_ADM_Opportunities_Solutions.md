# ADM - Fase E: Opportunities and Solutions
## RutaExpress Fulfillment & Transporte

> **Para el comité de arquitectura** — **Gap analysis** de negocio, datos, aplicaciones y tecnología, consolidado en **6 iniciativas** de transformación. **Mensaje clave:** mantener el catálogo de aplicaciones del Hito 1 sin cambios, modelando el **OMS centralizado** como evolución funcional de Orquestador de Pedidos (APP-02), y usando WMS Cloud, Servicio de Validación, Servicio de Liquidación, Bus de Eventos Central (PLT-03), Plataforma de Observabilidad Unificada (PLT-01), Plataforma de Identidad y Accesos (IAM) (PLT-02) y Plataforma IaC (PLT-04) como componentes TO BE ya reconocidos en los documentos `06`, `08` y `09`.

---

## 1. Propósito

Identificar y consolidar las brechas entre el estado AS IS y el TO BE de RutaExpress en las dimensiones de negocio, datos, aplicaciones y tecnología. La fase E agrupa esas brechas en iniciativas accionables, priorizadas y consistentes con el portafolio de aplicaciones del Hito 1.

**Criterio de consistencia aplicado:** no se crean nuevos IDs de aplicación en este documento. Cuando la iniciativa menciona un componente nuevo, se trata como:

- evolución de una aplicación existente, por ejemplo Orquestador de Pedidos (APP-02) hacia capacidad OMS centralizado / Orquestador de Pedidos (APP-02);
- reemplazo TO BE ya documentado, por ejemplo WMS Cloud reemplaza WMS Principal (On Premises) (APP-06) y WMS Satélite (On Premises local) (APP-07);
- plataforma habilitadora ya catalogada como brecha, por ejemplo Bus de Eventos Central (PLT-03).

---

## 2. Análisis de Brechas (GAP Analysis)

### 2.1 Gaps de Negocio

| ID Gap | Descripción | Impacto | Dominio |
|---|---|---|---|
| GN-01 | El ciclo de vida de órdenes no se gestiona end-to-end desde una fuente única; la validación depende de Orquestador de Pedidos (APP-02), Validador de Pedidos (APP-05), WMS Principal (On Premises) (APP-06) y canales externos sin control uniforme | Alto - 6% de órdenes con defectos e incidente de 32,000 duplicados | Recepción |
| GN-02 | Inventario sin vista unificada por SKU, almacén, ubicación, lote y estado; reservas y liberaciones no se coordinan de forma consistente | Crítico - 2.8% de movimientos con ajuste y conflictos al reconectar WMS Satélite (On Premises local) (APP-07) | Almacén |
| GN-03 | Integraciones punto a punto dificultan escalar, priorizar clientes y operar con contratos estandarizados | Alto - fallas de integración se propagan entre WMS Principal (On Premises) (APP-06), TMS (Transportation Management) (APP-11), app, ERP Financiero (On Premises) (APP-25) y portales | Integración |
| GN-04 | Gestión de última milla y excepciones sin taxonomía única ni persistencia offline robusta | Alto - 1,200 entregas sin firma y 34% de fallas prevenibles | Última Milla |
| GN-05 | Planificación de rutas rígida y con intervención manual no trazada | Medio - 17% de rutas corregidas manualmente y SLA en riesgo | Despacho |
| GN-06 | Visibilidad operativa, seguridad y gobierno multinube insuficientes | Alto - detección tardía de incidentes y riesgo en APIs, secretos y costos cloud | Gobierno TI |
| GN-07 | Liquidación financiera manual, basada en hojas Excel y conciliaciones tardías | Crítico - 23 días de conciliación, USD 2.4M retenidos y 7% de facturas observadas | Finanzas |

### 2.2 Gaps de Datos

| ID Gap | Descripción | Impacto | Dominio |
|---|---|---|---|
| GD-01 | No existe modelo canónico de orden, estado, reserva, entrega y excepción entre Orquestador de Pedidos (APP-02), WMS Principal (On Premises) (APP-06), TMS (Transportation Management) (APP-11), App de Conductores (APP-15) y Portal B2B (Trazabilidad) (APP-18) | Crítico - estados contradictorios visibles para clientes | Todos |
| GD-02 | Inventario distribuido entre WMS Principal (On Premises) (APP-06), WMS Satélite (On Premises local) (APP-07), Control de Inventario (APP-08) y ERP Financiero (On Premises) (APP-25) | Alto - reservas duplicadas, ajustes manuales y conflicto de stock | Almacén |
| GD-03 | Pedidos sin idempotencia y deduplicación robusta ante cambios de identificador externo | Alto - duplicados masivos y reprocesos manuales | Recepción |
| GD-04 | Eventos sin contratos estándar, orden garantizado, reintentos ni manejo consistente de mensajes fallidos | Alto - pérdida de tracking, datos fuera de secuencia y reprocesos | Integración |
| GD-05 | Excepciones, reclamos y motivos de no entrega no comparten taxonomía entre App de Conductores (APP-15), TMS (Transportation Management) (APP-11), CRM de Atención al Cliente (APP-20) y Portal B2B (Trazabilidad) (APP-18) | Medio - aprendizaje ML y causa raíz poco confiables | Última Milla |
| GD-06 | Datos de SLA, tarifas, penalidades, evidencias y estados financieros no se concilian automáticamente | Crítico - liquidaciones discutibles y notas de crédito manuales | Finanzas |

### 2.3 Gaps de Aplicaciones

| ID Gap | Descripción | Impacto | Dominio |
|---|---|---|---|
| GA-01 | Orquestador de Pedidos (APP-02) no actúa como OMS centralizado; Validador de Pedidos (APP-05) cubre validación parcial y falló en deduplicación | Crítico - órdenes defectuosas entran al flujo y consumen inventario | Recepción |
| GA-02 | WMS Principal (On Premises) (APP-06), WMS Satélite (On Premises local) (APP-07) y Control de Inventario (APP-08) no ofrecen inventario único, resiliente y reconciliado | Crítico - indisponibilidad en campañas y stock inconsistente | Almacén |
| GA-03 | Sin gobierno API-first ni Bus de Eventos Central (PLT-03); Azure API Management (APP-01) opera como gateway, pero no como gobierno completo de contratos, cuotas y políticas end-to-end | Alto - integraciones frágiles y costosas de mantener | Integración |
| GA-04 | App de Conductores (APP-15) tiene offline frágil; Almacenamiento Evidencias (S3) (APP-16) no garantiza integridad completa; TMS (Transportation Management) (APP-11), CRM de Atención al Cliente (APP-20) y portales no comparten excepciones | Alto - disputas de custodia y reintentos manuales | Última Milla |
| GA-05 | Optimizador de Rutas (GCP batch) (APP-12) planifica en batch; ML / Optimización de Rutas (GCP) (APP-24) aprende con datos sucios | Alto - rutas inviables y costo por entrega elevado | Despacho |
| GA-06 | Sin Plataforma de Observabilidad Unificada (PLT-01), Plataforma de Identidad y Accesos (IAM) (PLT-02) completa ni Plataforma IaC (PLT-04) operativa | Alto - baja trazabilidad, gobierno manual y seguridad parcial | Gobierno TI |
| GA-07 | Sistema de Liquidación (Excel) (APP-26) no escala ni controla reglas; ERP Financiero (On Premises) (APP-25) no integra en tiempo real | Crítico - liquidaciones lentas, errores y penalidades mal calculadas | Finanzas |

### 2.4 Gaps de Tecnología

| ID Gap | Descripción | Impacto | Dominio |
|---|---|---|---|
| GT-01 | WMS Principal (On Premises) (APP-06) sobre SQL Server sin alta disponibilidad, auto-scaling ni DR definido | Crítico - caída de 6 horas en campaña | Almacén |
| GT-02 | Integraciones sin colas gobernadas, reintentos, priorización, backpressure ni dead-letter queues | Crítico - acumulación de mensajes y pérdida de trazabilidad | Integración |
| GT-03 | Sin identificadores de correlación end-to-end para pedidos, inventario, rutas, entregas, evidencias y liquidación | Alto - causa raíz difícil y auditoría incompleta | Observabilidad |
| GT-04 | Identidad, secretos y cifrado no están gobernados de manera homogénea entre Azure, AWS, GCP, SaaS y on premises | Alto - exposición de APIs y datos sensibles | Seguridad |
| GT-05 | Infraestructura multinube aprovisionada con procesos manuales y bajo control FinOps limitado | Medio - ambientes no reproducibles y costos difíciles de explicar | Gobierno |

---

## 3. Iniciativas / Proyectos

> **Principio de solución:** priorizar servicios nativos de Azure, AWS y GCP, reutilizando aplicaciones existentes o reemplazos TO BE ya definidos. No se propone cambiar el catálogo maestro de aplicaciones del documento `06` salvo que el comité decida separar formalmente el OMS centralizado / Orquestador de Pedidos (APP-02) como una nueva aplicación, decisión que no es necesaria para estas iniciativas.

### INI-01: Gestión unificada de órdenes e inventario end-to-end

**Descripción:** Crear una capacidad OMS centralizado / Orquestador de Pedidos (APP-02) centralizada sobre Orquestador de Pedidos (APP-02), fortalecida con validación, deduplicación, idempotencia y modelo canónico de órdenes. Integrar reservas, liberaciones y movimientos entre WMS Cloud, TMS (Transportation Management) (APP-11), ERP Financiero (On Premises) (APP-25) y canales B2B. La vista de inventario será única por SKU, almacén, ubicación, lote y estado, con reconciliación automática de conflictos entre WMS Cloud y almacenes locales.

**Componentes principales:**

- Orquestador de Pedidos (APP-02) evoluciona a capacidad OMS centralizado / Orquestador de Pedidos (APP-02) centralizada.
- Validador de Pedidos (APP-05) se absorbe como reglas/servicio de validación dentro del flujo TO BE ya previsto.
- WMS Cloud reemplaza WMS Principal (On Premises) (APP-06) y WMS Satélite (On Premises local) (APP-07).
- Control de Inventario (APP-08) se elimina como app separada; su función queda absorbida por WMS Cloud.
- ERP Financiero (On Premises) (APP-25) integra inventario valorizado y estados financieros por API/eventos.

**Resumen de gaps que cierra:**

| ID | Dimensión | Brecha resumida |
|---|---|---|
| GN-01 | Negocio | Ciclo de vida de órdenes sin fuente única ni validación integral |
| GN-02 | Negocio | Inventario sin vista unificada y reservas inconsistentes |
| GD-01 | Datos | Modelo canónico de orden y estado inexistente |
| GD-02 | Datos | Múltiples fuentes de verdad de inventario |
| GD-03 | Datos | Falta de idempotencia y deduplicación robusta |
| GA-01 | Aplicaciones | Orquestador de Pedidos (APP-02) no cumple rol OMS centralizado / Orquestador de Pedidos (APP-02) |
| GA-02 | Aplicaciones | WMS Principal/Satélite e inventario local no están reconciliados |
| GT-01 | Tecnología | WMS Principal (On Premises) (APP-06) sin HA, escalado ni DR |

**Beneficios que aporta:**

| Beneficio | Impacto esperado |
|---|---|
| Órdenes confiables desde el ingreso | Menos duplicados, errores de dirección y pedidos inválidos antes de reservar stock |
| Inventario único operativo | Disminución de ajustes de inventario y conflictos de stock entre centros |
| Menor impacto de campañas | WMS Cloud con HA y escalado reduce riesgo de caída en Cyber Days |
| Trazabilidad de reservas y liberaciones | OMS centralizado / Orquestador de Pedidos (APP-02), WMS Principal (On Premises) (APP-06), TMS (Transportation Management) (APP-11) y ERP Financiero (On Premises) (APP-25) comparten estados auditables |
| Base para liquidación automática | Estados e inventario conciliables alimentan el motor financiero |

**Complejidad:** Muy Alta · **Duración estimada:** 9-12 meses

### INI-02: Integración API-First y Event-Driven

**Descripción:** Implementar una capa central de gestión y gobierno de APIs usando Azure API Management (APP-01) y crear Bus de Eventos Central (PLT-03) como plataforma event-driven entre Orquestador de Pedidos (APP-02), WMS Cloud, TMS (Transportation Management) (APP-11), App de Conductores (APP-15), ERP Financiero (On Premises) (APP-25), Portal B2B (Trazabilidad) (APP-18), Plataforma de Analítica (GCP batch) (APP-22) y Dashboards Operativos (APP-23).

**Alcance clave:**

- Contratos estandarizados de APIs, eventos y modelos de datos.
- Reemplazo progresivo de integraciones punto a punto.
- Colas, reintentos, priorización por SLA, backpressure, circuit breakers y dead-letter queues.
- Versionamiento de contratos y gobierno de cambios.
- **Bus de Eventos Central (PLT-03)** (Azure Event Hubs + Service Bus) canónico con replay para auditoría y recuperación.

**Resumen de gaps que cierra:**

| ID | Dimensión | Brecha resumida |
|---|---|---|
| GN-03 | Negocio | Integraciones punto a punto dificultan escalabilidad y priorización |
| GD-04 | Datos | Eventos sin contratos, orden garantizado ni manejo de fallidos |
| GA-03 | Aplicaciones | Falta Bus de Eventos Central (PLT-03) y gobierno API completo |
| GT-02 | Tecnología | Sin backpressure, reintentos, priorización ni DLQ |
| GT-03 | Tecnología | Sin correlación end-to-end |

**Beneficios que aporta:**

| Beneficio | Impacto esperado |
|---|---|
| Integración desacoplada | Nuevos consumidores se integran sin modificar sistemas core |
| Resiliencia operativa | Colas y backpressure protegen WMS Cloud, TMS (Transportation Management) (APP-11) y App de Conductores (APP-15) |
| Auditoría y replay | Reconstrucción de historial de pedido, inventario, ruta y liquidación |
| Menor costo de cambio | Contratos versionados reducen dependencias ocultas |
| Habilitador transversal | Soporta OMS centralizado / Orquestador de Pedidos (APP-02), última milla, rutas dinámicas, observabilidad y liquidación |

**Complejidad:** Alta · **Duración estimada:** 6-8 meses

### INI-03: Modernización de última milla y gestión de excepciones

**Descripción:** Fortalecer App de Conductores (APP-15) con operación offline-first, almacenamiento local cifrado, persistencia store-and-forward, confirmación backend, reintentos automáticos y sincronización idempotente. Definir taxonomía única de excepciones para App de Conductores (APP-15), TMS (Transportation Management) (APP-11), CRM de Atención al Cliente (APP-20) y Portal B2B (Trazabilidad) (APP-18), automatizando reintentos, devoluciones, reasignaciones y escalamiento.

**Resumen de gaps que cierra:**

| ID | Dimensión | Brecha resumida |
|---|---|---|
| GN-04 | Negocio | Última milla con evidencias perdidas y excepciones manuales |
| GD-05 | Datos | Taxonomías distintas entre app, TMS (Transportation Management) (APP-11), CRM y portal |
| GA-04 | Aplicaciones | Offline frágil en App de Conductores (APP-15) y evidencias sin integridad completa |
| GD-04 | Datos | Tracking fuera de orden al reconectar |

**Beneficios que aporta:**

| Beneficio | Impacto esperado |
|---|---|
| Cero pérdida funcional de evidencias | Firma, foto, GPS y timestamp se preservan aunque no haya señal |
| Excepciones accionables | Misma taxonomía para operación, atención al cliente y aprendizaje ML |
| Menos reintentos manuales | Reasignación, devolución y escalamiento con reglas automáticas |
| Mayor confianza de clientes | Evidencias íntegras reducen disputas de custodia |
| Datos limpios para rutas | ML / Optimización de Rutas (GCP) (APP-24) aprende de causas normalizadas |

**Complejidad:** Media · **Duración estimada:** 4-5 meses

### INI-04: Optimización dinámica de rutas y despacho

**Descripción:** Evolucionar Optimizador de Rutas (GCP batch) (APP-12) hacia planificación dinámica integrada con TMS (Transportation Management) (APP-11) mediante APIs y eventos. La solución incorpora tráfico, capacidad vehicular, ventanas horarias, cadena de frío, seguridad, SLA, disponibilidad de conductores y restricciones de paquetes. Registra cambios manuales de rutas y automatiza asignación de vehículos, conductores y paquetes.

**Resumen de gaps que cierra:**

| ID | Dimensión | Brecha resumida |
|---|---|---|
| GN-05 | Negocio | Rutas corregidas manualmente sin trazabilidad |
| GD-05 | Datos | Excepciones no normalizadas degradan planificación |
| GA-05 | Aplicaciones | Optimizador de Rutas (GCP batch) (APP-12) opera en batch |
| GT-02 | Tecnología | Integración con TMS (Transportation Management) (APP-11) sin eventos ni reintentos robustos |

**Beneficios que aporta:**

| Beneficio | Impacto esperado |
|---|---|
| Rutas dinámicas | Reoptimización ante tráfico, excepción, cambio de capacidad o incumplimiento SLA |
| Mejor uso de flota | Asignación automática de vehículos, conductores y paquetes |
| Menos intervención manual | Cambios manuales quedan registrados con motivo, usuario e impacto |
| Reducción de costo por entrega | Meta de hasta 15% en costo por entrega sobre operación de alto volumen |
| Cumplimiento de cadena de frío | Reglas de temperatura y seguridad integradas al plan |

**Complejidad:** Alta · **Duración estimada:** 6-8 meses

### INI-05: Observabilidad, seguridad y gobierno multinube

**Descripción:** Centralizar métricas, logs y trazas de Azure, AWS, GCP, SaaS y on premises mediante Plataforma de Observabilidad Unificada (PLT-01), completando Plataforma de Identidad y Accesos (IAM) (PLT-02) y Plataforma IaC (PLT-04). Incorporar identificadores de correlación end-to-end, tableros y alertas para colas, pedidos, inventario, rutas, entregas y SLA; aplicar identidad federada, mínimo privilegio, gestión central de secretos, cifrado, auditoría, infraestructura como código y gobierno FinOps.

**Resumen de gaps que cierra:**

| ID | Dimensión | Brecha resumida |
|---|---|---|
| GN-06 | Negocio | Gobierno multinube y visibilidad operativa insuficientes |
| GA-06 | Aplicaciones | Falta Plataforma de Observabilidad Unificada (PLT-01), IAM completo e IaC |
| GT-03 | Tecnología | Sin correlación end-to-end |
| GT-04 | Tecnología | Identidad, secretos y cifrado no homogéneos |
| GT-05 | Tecnología | Infraestructura manual y FinOps limitado |

**Beneficios que aporta:**

| Beneficio | Impacto esperado |
|---|---|
| Visibilidad end-to-end | Pedido, inventario, ruta, entrega y liquidación trazados con un mismo correlation ID |
| Menor tiempo de detección | Alertas de colas, errores, SLA, evidencias y fallas de integración |
| Seguridad reforzada | Identidad federada, mínimo privilegio y secretos centralizados |
| Ambientes reproducibles | Terraform y pipelines reducen cambios manuales |
| Control de costos | Gobierno FinOps para uso multinube y campañas |

**Complejidad:** Media · **Duración estimada:** 5-6 meses

### INI-06: Conciliación financiera y liquidación automatizada

**Descripción:** Implementar un motor de liquidación que integre OMS centralizado / Orquestador de Pedidos (APP-02), WMS Cloud, TMS (Transportation Management) (APP-11), tracking, evidencias en Almacenamiento Evidencias (S3) (APP-16), Portal B2B (Trazabilidad) (APP-18) y ERP Financiero (On Premises) (APP-25). El motor concilia órdenes, estados, evidencias, SLA, tarifas y penalidades; automatiza bonificaciones, penalidades y notas de crédito; y reemplaza el uso operativo de Sistema de Liquidación (Excel) (APP-26).

**Resumen de gaps que cierra:**

| ID | Dimensión | Brecha resumida |
|---|---|---|
| GN-07 | Negocio | Liquidación manual con conciliación de 23 días |
| GD-06 | Datos | Estados, evidencias, SLA, tarifas y penalidades no conciliados |
| GA-07 | Aplicaciones | Sistema de Liquidación (Excel) (APP-26) no controla reglas ni auditoría |
| GT-03 | Tecnología | Sin trazabilidad end-to-end para auditoría financiera |

**Beneficios que aporta:**

| Beneficio | Impacto esperado |
|---|---|
| Liquidación rápida | De 23 días a menos de 1 día en conciliación estándar |
| Menos facturas observadas | Reglas automáticas reducen errores manuales y notas de crédito tardías |
| Recuperación de caja | Menos retenciones por disputas de evidencia o SLA |
| Transparencia B2B | Portal con estado de liquidación y trazabilidad auditable |
| Menor dependencia de Excel | Sistema de Liquidación (Excel) (APP-26) deja de ser fuente operativa |

**Complejidad:** Alta · **Duración estimada:** 6-7 meses

### 3.1 Matriz consolidada - Iniciativa, gaps y beneficio clave

| Iniciativa | Gaps principales | Beneficio clave |
|---|---|---|
| INI-01 Gestión unificada de órdenes e inventario end-to-end | GN-01, GN-02, GD-01, GD-02, GD-03, GA-01, GA-02, GT-01 | Órdenes e inventario con fuente única, idempotencia y reservas trazables |
| INI-02 Integración API-First y Event-Driven | GN-03, GD-04, GA-03, GT-02, GT-03 | Integración desacoplada, gobernada y resiliente |
| INI-03 Modernización de última milla y gestión de excepciones | GN-04, GD-05, GA-04, GD-04 | Offline robusto y excepciones normalizadas entre app, TMS (Transportation Management) (APP-11), CRM y portal |
| INI-04 Optimización dinámica de rutas y despacho | GN-05, GD-05, GA-05, GT-02 | Rutas dinámicas, trazabilidad de cambios manuales y menor costo por entrega |
| INI-05 Observabilidad, seguridad y gobierno multinube | GN-06, GA-06, GT-03, GT-04, GT-05 | Correlación end-to-end, gobierno de seguridad e IaC multinube |
| INI-06 Conciliación financiera y liquidación automatizada | GN-07, GD-06, GA-07, GT-03 | Liquidación automática, auditable y sin dependencia operativa de Excel |

---

## 4. Arquitecturas de Transición

### Estado AS IS -> TO BE

```text
AS IS (Año 0)
------------------------------------------------
- Orquestador de Pedidos (APP-02) sin rol OMS centralizado / Orquestador de Pedidos (APP-02) completo.
- Validador de Pedidos (APP-05) con deduplicación frágil.
- WMS Principal (On Premises) (APP-06), WMS Satélite (On Premises local) (APP-07)
  y Control de Inventario (APP-08) con inventario fragmentado.
- Integraciones punto a punto; no existe Bus de Eventos Central (PLT-03).
- App de Conductores (APP-15) con offline frágil.
- Optimizador de Rutas (GCP batch) (APP-12) en batch.
- Plataforma de Observabilidad Unificada (PLT-01) ausente, IAM parcial e IaC ausente.
- Sistema de Liquidación (Excel) (APP-26) manual.

        |
        v

TRANSICIÓN 1 (Meses 1-12)
------------------------------------------------
- Bus de Eventos Central (PLT-03) y gobierno API-first operativo para flujos críticos.
- Orquestador de Pedidos (APP-02) evoluciona a OMS centralizado / Orquestador de Pedidos (APP-02) MVP con validación, idempotencia
  y modelo canónico de orden.
- WMS Principal (On Premises) (APP-06) opera en modo puente mientras se prepara WMS Cloud.
- App de Conductores (APP-15) offline-first y taxonomía de excepciones inicial.
- Plataforma de Observabilidad Unificada (PLT-01), IAM e IaC con cobertura base.
- Primeros tableros de colas, pedidos, inventario, rutas y SLA.

        |
        v

TRANSICIÓN 2 (Meses 12-24)
------------------------------------------------
- WMS Cloud reemplaza WMS Principal (On Premises) (APP-06) y WMS Satélite (On Premises local) (APP-07).
- Vista unificada de inventario y reconciliación de conflictos.
- Optimizador de Rutas en Tiempo Real reemplaza Optimizador de Rutas (GCP batch) (APP-12).
- Motor de liquidación reemplaza Sistema de Liquidación (Excel) (APP-26).
- ERP Financiero (On Premises) (APP-25), Portal B2B (Trazabilidad) (APP-18)
  y Almacenamiento Evidencias (S3) (APP-16) integrados al flujo financiero.

        |
        v

TO BE (Meses 24-36)
------------------------------------------------
- Plataforma logística digital con OMS centralizado / Orquestador de Pedidos (APP-02), WMS Cloud, TMS (Transportation Management) (APP-11), app, ERP Financiero (On Premises) (APP-25) y portales integrados.
- **Bus de Eventos Central (PLT-03)** canónico para tracking operativo y financiero.
- Rutas dinámicas con aprendizaje de excepciones.
- Observabilidad, seguridad, secretos, cifrado, auditoría, IaC y FinOps gobernados.
- Liquidación automática en menos de 1 día y trazabilidad auditable end-to-end.
```

---

## 5. Priorización de Iniciativas (Valor vs Esfuerzo)

```text
FUNDACIONALES / HABILITADORES TRANSVERSALES
  - INI-05: Observabilidad, seguridad y gobierno multinube
  - INI-02: Integración API-First y Event-Driven

ALTO VALOR / TRANSFORMACIÓN CORE
  - INI-01: Gestión unificada de órdenes e inventario end-to-end
  - INI-06: Conciliación financiera y liquidación automatizada

ALTO VALOR / OPERACIÓN
  - INI-03: Modernización de última milla y gestión de excepciones
  - INI-04: Optimización dinámica de rutas y despacho
```

**Orden recomendado:** iniciar INI-05 e INI-02 en el mes 1 porque habilitan trazabilidad, seguridad, contratos y eventos para el resto. Ejecutar INI-03 temprano como quick win operativo. Implementar INI-01 con despliegue progresivo porque concentra el mayor cambio core. Encadenar INI-04 e INI-06 sobre los datos y eventos estabilizados.

---

## 6. Verificación de consistencia con hojas de aplicaciones

| Iniciativa | Componentes de aplicaciones/plataformas usados | ¿Requiere cambiar `06`/`08`? | Justificación |
|---|---|---|---|
| INI-01 | Orquestador de Pedidos (APP-02), Validador de Pedidos (APP-05), WMS Principal (On Premises) (APP-06), WMS Satélite (On Premises local) (APP-07), Control de Inventario (APP-08), ERP Financiero (On Premises) (APP-25), WMS Cloud TO BE | No | El OMS centralizado / Orquestador de Pedidos (APP-02) queda documentado como evolución TO BE de Orquestador de Pedidos (APP-02); WMS Cloud y eliminación de Control de Inventario (APP-08) ya están documentados como TO BE |
| INI-02 | Azure API Management (APP-01), Bus de Eventos Central (PLT-03), Plataforma de Analítica (GCP batch) (APP-22), Dashboards Operativos (APP-23) | No | Bus de Eventos Central (PLT-03) ya existe como gap/plataforma TO BE; Azure API Management (APP-01) ya está en catálogo |
| INI-03 | App de Conductores (APP-15), Almacenamiento Evidencias (S3) (APP-16), TMS (Transportation Management) (APP-11), CRM de Atención al Cliente (APP-20), Portal B2B (Trazabilidad) (APP-18) | No | Son modificaciones funcionales y de integración sobre aplicaciones existentes |
| INI-04 | Optimizador de Rutas (GCP batch) (APP-12), ML / Optimización de Rutas (GCP) (APP-24), TMS (Transportation Management) (APP-11), App de Conductores (APP-15) | No | El reemplazo TO BE del optimizador batch por uno en tiempo real ya está previsto en `09` |
| INI-05 | Plataforma de Observabilidad Unificada (PLT-01), Plataforma de Identidad y Accesos (IAM) (PLT-02), Plataforma IaC (PLT-04), Azure API Management (APP-01) | No | Plataforma de Observabilidad Unificada (PLT-01)/Plataforma IaC (PLT-04) son gaps TO BE y Plataforma de Identidad y Accesos (IAM) (PLT-02) ya existe como parcial en el catálogo |
| INI-06 | Sistema de Liquidación (Excel) (APP-26), ERP Financiero (On Premises) (APP-25), TMS (Transportation Management) (APP-11), App de Conductores (APP-15), Almacenamiento Evidencias (S3) (APP-16), Portal B2B (Trazabilidad) (APP-18) | No | El reemplazo del Sistema de Liquidación (Excel) (APP-26) por servicio/motor de liquidación ya está documentado como TO BE |

**Conclusión de consistencia:** la documentación TO BE deja explícito que el "OMS centralizado" es la evolución de Orquestador de Pedidos (APP-02), sin crear un nuevo ID de aplicación. La única decisión que podría forzar cambios adicionales sería exigir que el OMS centralizado / Orquestador de Pedidos (APP-02) tenga un ID propio e independiente; no se recomienda para este Hito porque aumenta el alcance sin agregar claridad arquitectónica.

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
