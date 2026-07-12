# MS-INI02-02 - Mensajeria Resiliente y Replay

## Identificacion

- Iniciativa: INI-02 Integracion API-First y Event-Driven.
- Componente TO BE: capacidad logica del Bus de Eventos Central (PLT-03), implementable sobre Azure Event Hubs/Service Bus o AWS EventBridge/SQS segun alternativa.
- Fuentes: `01_Requerimientos_y_Criterios_Aceptacion.md` e historias `HU-INI02-RF03` a `HU-INI02-RF09` y `HU-INI02-RF11`.
- Alcance: publicacion de eventos canonicos, validacion de esquema, reintentos, DLQ, backpressure, prioridad, replay y secuencia logica por agregado.

## Responsabilidades

- Publicar eventos canonicos de OMS, WMS, TMS, app, ERP y portal.
- Validar esquema, version, productor, timestamp, correlation ID e idempotency key.
- Controlar reintentos con backoff, jitter, prioridad y DLQ.
- Aplicar backpressure ante degradacion de consumidores o sistemas on premises.
- Ejecutar replay controlado sin duplicar efectos de negocio.
- Preservar secuencia logica por orden, paquete, ruta, entrega, evidencia y liquidacion.

## Modelo de datos

```sql
CREATE TABLE event_envelope (
  event_id UUID PRIMARY KEY,
  aggregate_id VARCHAR(100) NOT NULL,
  aggregate_type VARCHAR(40) NOT NULL,
  event_type VARCHAR(100) NOT NULL,
  schema_version VARCHAR(20) NOT NULL,
  producer VARCHAR(80) NOT NULL,
  sequence_number BIGINT NOT NULL,
  idempotency_key VARCHAR(120) NOT NULL,
  correlation_id VARCHAR(100) NOT NULL,
  payload_json JSON NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE UNIQUE INDEX ux_event_idempotency
ON event_envelope(producer, idempotency_key);

CREATE TABLE consumer_inbox (
  consumer_name VARCHAR(80) NOT NULL,
  event_id UUID NOT NULL REFERENCES event_envelope(event_id),
  process_status VARCHAR(30) NOT NULL,
  attempts INTEGER NOT NULL DEFAULT 0,
  last_error TEXT,
  updated_at TIMESTAMP NOT NULL,
  PRIMARY KEY (consumer_name, event_id)
);

CREATE TABLE dead_letter_message (
  dlq_id UUID PRIMARY KEY,
  event_id UUID NOT NULL,
  consumer_name VARCHAR(80) NOT NULL,
  error_code VARCHAR(80) NOT NULL,
  error_detail TEXT NOT NULL,
  payload_json JSON NOT NULL,
  remediation_status VARCHAR(30) NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE replay_job (
  replay_job_id UUID PRIMARY KEY,
  aggregate_type VARCHAR(40) NOT NULL,
  from_timestamp TIMESTAMP NOT NULL,
  to_timestamp TIMESTAMP NOT NULL,
  requested_by VARCHAR(80) NOT NULL,
  approval_status VARCHAR(30) NOT NULL,
  created_at TIMESTAMP NOT NULL
);
```

## Funcionalidades

| Codigo | Funcionalidad | Contrato entrada | Contrato salida | Trazabilidad | Lineamientos |
|---|---|---|---|---|---|
| F-EVT-01 | Publicar y validar eventos | `EventEnvelope` con schemaVersion, producer, aggregateId, sequence, correlationId | Evento aceptado o rechazado por contrato | `HU-INI02-RF03`, `HU-INI02-RF04`, `ESC-INI02-RF04-N01` | INT-02, INT-04, ARQ-05, OBS-02 |
| F-EVT-02 | Reintentos, DLQ y backpressure | Error de consumidor, politica de retry, criticidad y SLA | Reintento programado, DLQ o throttling | `HU-INI02-RF05`, `HU-INI02-RF06`, `HU-INI02-RF07`, `HU-INI02-RF08` | INT-05, ESC-05, ESC-09, OBS-05 |
| F-EVT-03 | Replay y orden por agregado | Solicitud aprobada de replay, rango temporal, agregado y consumidor | Eventos reemitidos en secuencia o retenidos por riesgo | `HU-INI02-RF09`, `HU-INI02-RF11`, `ESC-INI02-RF11-N01` | INT-09, INT-12, SEG-07, OBS-09 |

## Algoritmos

### F-EVT-01 - Publicacion validada

```text
recibir evento de productor
validar contrato AsyncAPI y schemaVersion
verificar correlationId, idempotencyKey y timestamp
si esquema invalido:
  rechazar evento y registrar error de contrato
si idempotencyKey ya existe:
  devolver aceptado sin duplicar publicacion
persistir event_envelope
publicar a topico por dominio y aggregateType
```

### F-EVT-02 - Resiliencia de entrega

```text
consumidor informa fallo o timeout
incrementar attempts en inbox
si attempts <= maxRetries:
  calcular backoff con jitter segun criticidad
  reencolar con prioridad por SLA
si attempts supera maxRetries:
  mover a dead_letter_message con payload y error
si backlog supera umbral:
  activar backpressure para productores no criticos
```

### F-EVT-03 - Replay controlado

```text
recibir solicitud de replay aprobada
validar rol, ventana temporal y consumidor destino
leer eventos por aggregateType ordenados por aggregateId y sequence_number
para cada evento:
  verificar si el consumidor ya lo proceso
  reemitir solo si no duplica efecto de negocio
registrar auditoria, conteo reprocesado y errores
```

## Consideraciones de calidad

- Escalabilidad: particionamiento por `aggregate_id` y control de backlog para campanas.
- Resiliencia: DLQ remediable, replay aprobado, retry con backoff y jitter, bulkhead por consumidor.
- Seguridad: autorizacion por rol para replay y remediacion de DLQ.
- Observabilidad: metricas de lag, DLQ, eventos fuera de orden, tasa de errores y backpressure activo.
