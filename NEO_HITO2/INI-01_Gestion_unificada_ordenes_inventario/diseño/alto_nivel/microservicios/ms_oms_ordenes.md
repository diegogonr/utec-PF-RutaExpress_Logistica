# MS-INI01-01 - OMS Ordenes

## Identificacion

- Iniciativa: INI-01 Gestion unificada de ordenes e inventario end-to-end.
- Componente TO BE: evolucion del Orquestador de Pedidos (APP-02) hacia OMS centralizado.
- Fuentes: `01_Requerimientos_y_Criterios_Aceptacion.md` e historias `HU-INI01-RF01` a `HU-INI01-RF05`, `HU-INI01-RF10`, `HU-INI01-RF11` y `HU-INI01-RF12`.
- Alcance: ciclo de vida de ordenes, validacion, deduplicacion, idempotencia, estado canonico, APIs de consulta y compatibilidad transicional con WMS on premises.

## Responsabilidades

- Recibir ordenes desde clientes B2B, portal, app y canales transicionales.
- Asignar identificador interno unico y mantener el estado canonico de la orden.
- Validar datos obligatorios, reglas logisticas, SLA y canal.
- Detectar duplicados por identificador externo, hash de contenido y ventana temporal.
- Garantizar idempotencia ante reintentos de clientes o integraciones.
- Publicar eventos confiables hacia inventario, TMS, portal, CRM, observabilidad y ERP.
- Exponer APIs de consulta sin acoplar canales a reglas internas del OMS.

## Modelo de datos

```sql
CREATE TABLE oms_order (
  order_id UUID PRIMARY KEY,
  client_id VARCHAR(40) NOT NULL,
  external_order_id VARCHAR(100),
  content_hash CHAR(64) NOT NULL,
  canonical_status VARCHAR(30) NOT NULL,
  sla_tier VARCHAR(20) NOT NULL,
  source_channel VARCHAR(30) NOT NULL,
  priority_score NUMERIC(8,2) NOT NULL DEFAULT 0,
  correlation_id VARCHAR(100) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

CREATE UNIQUE INDEX ux_oms_order_external
ON oms_order(client_id, external_order_id)
WHERE external_order_id IS NOT NULL;

CREATE INDEX ix_oms_order_dedupe
ON oms_order(client_id, content_hash, created_at);

CREATE TABLE oms_idempotency_key (
  idempotency_key VARCHAR(120) PRIMARY KEY,
  client_id VARCHAR(40) NOT NULL,
  request_hash CHAR(64) NOT NULL,
  response_order_id UUID,
  response_status VARCHAR(30),
  expires_at TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE oms_order_state_history (
  history_id UUID PRIMARY KEY,
  order_id UUID NOT NULL REFERENCES oms_order(order_id),
  previous_status VARCHAR(30),
  new_status VARCHAR(30) NOT NULL,
  reason_code VARCHAR(40),
  actor_type VARCHAR(30) NOT NULL,
  correlation_id VARCHAR(100) NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE oms_outbox_event (
  event_id UUID PRIMARY KEY,
  aggregate_id UUID NOT NULL,
  aggregate_type VARCHAR(40) NOT NULL,
  event_type VARCHAR(80) NOT NULL,
  schema_version VARCHAR(20) NOT NULL,
  payload_json JSON NOT NULL,
  correlation_id VARCHAR(100) NOT NULL,
  published_at TIMESTAMP NULL,
  created_at TIMESTAMP NOT NULL
);
```

## Funcionalidades

| Codigo | Funcionalidad | Contrato entrada | Contrato salida | Trazabilidad | Lineamientos |
|---|---|---|---|---|---|
| F-OMS-01 | Registrar y validar orden | `POST /orders`, `clientId`, `externalOrderId`, destinatario, SKUs, ventana, SLA, `idempotencyKey`, `correlationId` | `201 orderId` si valida, `422` con errores funcionales si no valida | `HU-INI01-RF01`, `HU-INI01-RF02`, `ESC-INI01-RF01-P01`, `ESC-INI01-RF02-N01` | ARQ-02, ARQ-03, INT-01, INT-03, SEG-07, OBS-02 |
| F-OMS-02 | Deduplicar e idempotencia | Hash normalizado de orden, cliente, destinatario, ventana y clave idempotente | Orden original si es duplicada, rechazo trazable si la clave no coincide | `HU-INI01-RF03`, `HU-INI01-RF04`, `ESC-INI01-RF03-P01`, `ESC-INI01-RF04-P01` | INT-06, INT-09, OBS-04, ESC-09 |
| F-OMS-03 | Estado canonico y publicacion | Cambio solicitado de estado, motivo, actor y correlacion | Estado persistido, evento `OrderStatusChanged`, auditoria | `HU-INI01-RF05`, `HU-INI01-RF10`, `HU-INI01-RF11`, `HU-INI01-RF12` | ARQ-05, INT-02, INT-04, OBS-07, SEG-07 |

## Algoritmos

### F-OMS-01 - Registro y validacion

```text
recibir solicitud
validar correlationId, idempotencyKey y esquema
normalizar direccion, destinatario, SKUs, ventana y SLA
si faltan datos obligatorios:
  registrar auditoria funcional
  responder 422 sin publicar evento de aceptacion
calcular priorityScore por SLA, canal y promesa
persistir orden en estado RECEIVED
registrar outbox OrderReceived
responder orderId y estado canonico
```

### F-OMS-02 - Deduplicacion e idempotencia

```text
buscar idempotencyKey vigente
si existe y requestHash coincide:
  devolver respuesta anterior sin crear nueva orden
si existe y requestHash difiere:
  rechazar con conflicto idempotente
calcular contentHash con campos logisticos normalizados
buscar orden previa por cliente, hash y ventana
si existe duplicado:
  guardar respuesta con orderId original
  publicar OrderDuplicateDetected
  responder referencia original
continuar validacion normal
```

### F-OMS-03 - Estado canonico

```text
recibir comando o evento de dominio
verificar transicion permitida en maquina de estados
si transicion invalida:
  registrar rechazo con correlationId
  no propagar estado inconsistente
persistir nuevo estado e historial
crear evento en outbox con version de esquema
publicador outbox entrega evento al Bus de Eventos Central (PLT-03)
```

## Consideraciones de calidad

- Disponibilidad objetivo: 99.9% para recepcion y consulta de ordenes en campana.
- Escalabilidad: servicios stateless y particionamiento por `client_id` y `order_id`.
- Resiliencia: Outbox, retry con backoff y circuit breaker hacia WMS/ERP.
- Seguridad: OAuth/OIDC, minimo privilegio, cifrado en transito y auditoria de cambios de estado.
- Observabilidad: logs estructurados sin PII, metricas de ordenes recibidas, rechazadas, duplicadas, latencia e idempotencia.
