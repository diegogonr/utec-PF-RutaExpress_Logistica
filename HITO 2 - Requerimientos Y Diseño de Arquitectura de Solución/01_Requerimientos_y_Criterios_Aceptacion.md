# Requerimientos Funcionales / No Funcionales y Criterios de Aceptación
## RutaExpress Fulfillment & Transporte — Hito 2

> **Fuente:** iniciativas del [`11_ADM_Migration_Planning.md`](../HITO%201%20-%20Arquitectura%20Empresarial/11_ADM_Migration_Planning.md) (ADM Fase F).  
> **Iniciativas seleccionadas (≥3):** **INI-01** (PLT-03 Bus de Eventos Central), **INI-02** (WMS Cloud), **INI-03** (APP-15 App de Conductores Resiliente).  
> **Convención:** nombre oficial + **(APP-XX)** / **(PLT-XX)** según catálogo Hito 1.  
> **Servicios:** solo nativos **Azure / AWS / GCP**, alcance **medio** (sin Datadog, Apicurio, Kafka autogestionado ni SaaS de observabilidad).

---

## 1. Propósito

Detallar historias de usuario, requerimientos funcionales (RF), requerimientos no funcionales (RNF) y criterios de aceptación en **Gherkin (BDD)** para las tres iniciativas prioritarias que habilitan el TO BE de RutaExpress.

---

## 2. INI-01 — PLT-03 Bus de Eventos Central

**Referencia Hito 1:** Azure Event Hubs como hub principal; modelo canónico de estados; desacopla WMS Principal (On Premises) (APP-06), TMS (Transportation Management) (APP-11) y App de Conductores (APP-15).

### 2.1 Historias de usuario

| ID | Sector | Como | Quiero | Para |
|---|---|---|---|---|
| HU-INI01-01 | Logística | **Arquitecto de integración** | publicar y consumir eventos de pedido por un bus central (PLT-03) | eliminar integraciones punto a punto frágiles entre nubes |
| HU-INI01-02 | Logística | **Operador de mesa B2B** | ver el mismo estado canónico del pedido que TMS (APP-11) y la app de conductores | evitar reclamos por estados inconsistentes |
| HU-INI01-03 | Logística | **Auditor de calidad** | reproducir (replay) el historial de eventos de un pedido | resolver disputas y reconstruir trazabilidad |

### 2.2 Requerimientos

| ID | Tipo | Descripción |
|---|---|---|
| **RF-INI01-01** | Funcional | El **Bus de Eventos Central (PLT-03)** debe aceptar eventos de dominio *Pedido*, *Inventario* y *Entrega* con esquema canónico versionado. |
| **RF-INI01-02** | Funcional | TMS (Transportation Management) (APP-11) y WMS Principal (On Premises) (APP-06) / WMS Cloud deben publicar y consumir estados vía PLT-03 sin llamadas P2P directas en flujos críticos F1–F4. |
| **RF-INI01-03** | Funcional | El bus debe soportar **replay** de eventos por `orderId` en ventana configurable para auditoría. |
| **RNF-INI01-01** | No funcional | Latencia publicación→consumo **p95 ≤ 5 s** en operación normal (≤ 30 s en campaña 3× volumen). |
| **RNF-INI01-02** | No funcional | Disponibilidad del hub **≥ 99.9%** mensual; eventos persistidos mínimo **7 días** (retención configurable). |
| **RNF-INI01-03** | No funcional | Todos los productores/consumidores autenticados vía **Microsoft Entra ID (PLT-02)** con principio de mínimo privilegio. |

### 2.3 Criterios de aceptación (Gherkin)

#### Escenario positivo — Publicación y consumo de estado canónico

```gherkin
Feature: Bus de Eventos Central (PLT-03)

  Scenario: TMS publica cambio de estado y Portal B2B (Trazabilidad) (APP-18) consume el mismo estado
    Given que el Bus de Eventos Central (PLT-03) está operativo en Cloud MS Azure (EEUU)
    And TMS (Transportation Management) (APP-11) tiene permiso de publicación en el tópico "order-status"
    And Portal B2B (Trazabilidad) (APP-18) está suscrito al mismo tópico vía API
    When TMS (Transportation Management) (APP-11) publica el evento "OrderDispatched" para el pedido "ORD-2026-001"
    Then el evento debe persistirse en Azure Event Hubs (PLT-03)
    And Portal B2B (Trazabilidad) (APP-18) debe recibir el estado "DESPACHADO" canónico en menos de 5 segundos
    And el estado mostrado debe coincidir con el registrado en TMS (Transportation Management) (APP-11)
```

#### Escenario negativo — Rechazo de evento con esquema inválido

```gherkin
  Scenario: Rechazo de evento sin campos obligatorios del modelo canónico
    Given que el Bus de Eventos Central (PLT-03) valida el esquema "order-status-v1"
    And un productor intenta publicar un evento sin "orderId" ni "timestamp"
    When el productor envía el evento al hub
    Then el sistema no debe encolar el evento para consumidores de negocio
    And debe registrar el error en Azure Monitor (PLT-01) con código "SCHEMA_VALIDATION_FAILED"
    And debe devolver respuesta de rechazo al productor
```

#### Escenario positivo — Replay para auditoría

```gherkin
  Scenario: Replay de eventos de un pedido para auditoría
    Given que existen al menos 10 eventos históricos para el pedido "ORD-2026-001" en PLT-03
    And el auditor tiene rol "EventReplayReader" en Entra ID (PLT-02)
    When solicita replay del pedido "ORD-2026-001" en las últimas 72 horas
    Then el sistema debe entregar la secuencia completa ordenada por timestamp
    And cada evento debe incluir productor, versión de esquema y hash de integridad
```

---

## 3. INI-02 — WMS Cloud (reemplaza APP-06 / APP-07)

**Referencia Hito 1:** WMS Cloud custom en **Azure AKS + Azure SQL Managed Instance**; auto-scaling KEDA; modo degradado; migración por fases (1 → 3 → 14 CDs). Control de Inventario (APP-08) se **elimina** (sin app TO BE homóloga).

### 3.1 Historias de usuario

| ID | Sector | Como | Quiero | Para |
|---|---|---|---|---|
| HU-INI02-01 | Logística | **Supervisor de almacén** | que el WMS escale automáticamente en campaña Cyber Days | evitar caídas de 6 horas y penalidades de USD 1.1M |
| HU-INI02-02 | Logística | **Picker con App Handhelds (picking) (APP-10)** | reservar y confirmar picking con inventario actualizado en tiempo real | no generar olas con stock desactualizado |
| HU-INI02-03 | Logística | **Planner de transporte** | recibir confirmación de picking vía eventos antes de cerrar manifiesto | evitar rutas con paquetes faltantes |

### 3.2 Requerimientos

| ID | Tipo | Descripción |
|---|---|---|
| **RF-INI02-01** | Funcional | **WMS Cloud** debe mantener inventario único en tiempo real para los 14 centros de distribución, reemplazando WMS Principal (On Premises) (APP-06) y WMS Satélite (On Premises local) (APP-07). |
| **RF-INI02-02** | Funcional | Debe publicar movimientos de inventario (*reserva*, *picking*, *ajuste*) a **PLT-03** para consumo de TMS (APP-11) y ERP Financiero (On Premises) (APP-25). |
| **RF-INI02-03** | Funcional | Modo **degradado local**: si un CD pierde conectividad, debe operar con cola local y reconciliar automáticamente al reconectar (reemplaza sync horaria APP-07). |
| **RNF-INI02-01** | No funcional | Auto-scaling horizontal: absorber **3×** volumen de órdenes/hora sin degradación > 10% en latencia de reserva. |
| **RNF-INI02-02** | No funcional | **RTO ≤ 4 h** y **RPO ≤ 15 min** con despliegue multi-zona en Cloud MS Azure (EEUU). |
| **RNF-INI02-03** | No funcional | Infraestructura aprovisionada con **Terraform (PLT-04)**; sin cambios manuales en producción. |

### 3.3 Criterios de aceptación (Gherkin)

#### Escenario positivo — Auto-scaling en campaña

```gherkin
Feature: WMS Cloud — resiliencia en campaña

  Scenario: Escalamiento automático durante pico Cyber Days
    Given que WMS Cloud está desplegado en Azure AKS con KEDA configurado
    And la carga supera 200% del baseline de reservas por minuto durante 5 minutos
    When el HPA/KEDA detecta la métrica de cola de reservas
    Then debe incrementar réplicas del servicio WMS Cloud en menos de 3 minutos
    And la tasa de error de reserva debe mantenerse por debajo del 1%
    And Azure Monitor (PLT-01) debe registrar el evento de escalamiento
```

#### Escenario negativo — Rechazo de reserva por stock insuficiente

```gherkin
  Scenario: Reserva rechazada cuando no hay stock disponible
    Given que el SKU "SKU-999" tiene stock disponible 0 en el CD "CD-LIM-01"
    And Orquestador de Pedidos (APP-02) envía solicitud de reserva vía PLT-03
    When WMS Cloud procesa la reserva
    Then debe publicar evento "ReservationRejected" con motivo "INSUFFICIENT_STOCK"
    And no debe dejar reserva parcial inconsistente en Azure SQL
    And TMS (Transportation Management) (APP-11) no debe incluir el ítem en manifiesto
```

#### Escenario positivo — Reconciliación tras desconexión

```gherkin
  Scenario: Reconciliación automática tras reconexión de CD satélite
    Given que el CD "CD-ARE-03" estuvo offline 74 minutos con movimientos en cola local
    And WMS Cloud activó modo degradado con idempotencia por "movementId"
    When se restablece la conectividad WAN
    Then WMS Cloud debe reconciliar movimientos en menos de 15 minutos
    And debe generar reporte de conflictos resueltos vs pendientes de intervención
    And no debe quedar diferencia > 0.1% vs inventario físico contado en piloto
```

---

## 4. INI-03 — APP-15 App de Conductores Resiliente

**Referencia Hito 1:** Backend **AWS ECS Fargate**; **AWS Kinesis**; SQLite cifrado offline; evidencias atómicas; taxonomía obligatoria de excepciones.

### 4.1 Historias de usuario

| ID | Sector | Como | Quiero | Para |
|---|---|---|---|---|
| HU-INI03-01 | Logística | **Conductor** | registrar entrega y evidencias aunque pierda señal 4G | no perder firmas ni fotos al cambiar de equipo |
| HU-INI03-02 | Logística | **Cliente empresarial** | ver tracking actualizado en menos de 30 segundos | reducir llamadas a atención al cliente |
| HU-INI03-03 | Logística | **Supervisor de ruta** | recibir excepciones con motivos normalizados obligatorios | alimentar ML / Optimización de Rutas (GCP) (APP-24) |

### 4.2 Requerimientos

| ID | Tipo | Descripción |
|---|---|---|
| **RF-INI03-01** | Funcional | App de Conductores (APP-15) debe almacenar offline en **SQLite cifrado (AES-256)** eventos de tracking y evidencias hasta sincronización exitosa. |
| **RF-INI03-02** | Funcional | Subida **atómica** de evidencia (foto + firma + GPS + timestamp + hash) a Almacenamiento Evidencias (S3) (APP-16); reintento idempotente tras reinstalación. |
| **RF-INI03-03** | Funcional | Publicar eventos de tracking a **AWS Kinesis** integrados al **Event Store** canónico vía PLT-03. |
| **RF-INI03-04** | Funcional | Motivos de excepción **obligatorios** desde taxonomía canónica (sin texto libre). |
| **RNF-INI03-01** | No funcional | **98%** de eventos de tracking visibles end-to-end en **≤ 30 s** bajo conectividad normal. |
| **RNF-INI03-02** | No funcional | **Cero** pérdida de evidencias en prueba de estrés: 1.000 entregas offline + reinstalación de app. |
| **RNF-INI03-03** | No funcional | Dispositivos gestionados por **MDM** (Cloud SaaS - Software as a Service (EEUU)); datos personales cifrados en tránsito (TLS 1.2+) y reposo. |

### 4.3 Criterios de aceptación (Gherkin)

#### Escenario positivo — Sincronización atómica de evidencias

```gherkin
Feature: App de Conductores (APP-15) — evidencias resilientes

  Scenario: Entrega registrada offline se sincroniza completamente al reconectar
    Given que el conductor completó la entrega "ORD-2026-500" sin señal 4G
    And capturó foto, firma y GPS en SQLite cifrado local
    When el dispositivo recupera conectividad con Cloud AWS (EEUU)
    Then App de Conductores (APP-15) debe subir evidencia atómica a Almacenamiento Evidencias (S3) (APP-16)
    And debe publicar evento "DeliveryCompleted" en AWS Kinesis
    And Portal B2B (Trazabilidad) (APP-18) debe mostrar estado "ENTREGADO" en menos de 30 segundos
    And el hash de integridad en S3 debe coincidir con el generado en dispositivo
```

#### Escenario negativo — Bloqueo por motivo de excepción no normalizado

```gherkin
  Scenario: No se permite excepción con texto libre
    Given que el conductor intenta registrar una excepción de entrega
    And selecciona categoría "OTRO" sin elegir subcódigo válido de la taxonomía
    When confirma el registro de excepción
    Then la app no debe enviar el evento a AWS Kinesis
    And debe mostrar "Seleccione un motivo válido de la lista"
    And debe conservar borrador local hasta corrección
```

#### Escenario negativo — Reinstalación con evidencias pendientes

```gherkin
  Scenario: Reinstalación de app preserva evidencias pendientes
    Given que hay 3 entregas con evidencias pendientes de sync en SQLite cifrado
    When el conductor reinstala App de Conductores (APP-15) en nuevo dispositivo MDM enrolado
    And restaura backup autorizado de cola offline
    Then las 3 evidencias deben sincronizarse sin duplicar eventos en Kinesis
    And ninguna evidencia debe quedar con estado "PERDIDA"
```

---

## 5. Trazabilidad INI ↔ RF/RNF

| Iniciativa | Historias | RF | RNF | Escenarios Gherkin |
|---|---|---|---|---|
| INI-01 PLT-03 | 3 | 3 | 3 | 3 (2 positivos, 1 negativo) |
| INI-02 WMS Cloud | 3 | 3 | 3 | 3 (2 positivos, 1 negativo) |
| INI-03 APP-15 | 3 | 4 | 3 | 3 (1 positivo, 2 negativos) |

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*  
*Fecha: Julio 2026*
