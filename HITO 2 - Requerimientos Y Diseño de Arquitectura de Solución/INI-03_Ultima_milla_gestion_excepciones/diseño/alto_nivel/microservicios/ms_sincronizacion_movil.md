# MS-INI03-01 - Sincronizacion Movil Offline

## Identificacion

- Iniciativa: INI-03 Modernizacion de ultima milla y gestion de excepciones.
- Componente TO BE: backend y protocolo de sincronizacion para App de Conductores (APP-15).
- Fuentes: `01_Requerimientos_y_Criterios_Aceptacion.md` e historias `HU-INI03-RF01` a `HU-INI03-RF05`, `HU-INI03-RF11` y `HU-INI03-RF12`.
- Alcance: operacion offline-first, almacenamiento local cifrado, store-and-forward, confirmacion backend, reintentos, cambio de dispositivo y tracking.

## Responsabilidades

- Permitir que la app opere sin conectividad durante reparto.
- Encolar eventos locales cifrados y sincronizarlos en orden logico por entrega.
- Confirmar recepcion backend antes de eliminar eventos locales.
- Reintentar envios fallidos con backoff y conservar timestamp original.
- Preservar evidencias y eventos ante cambio o perdida de dispositivo.
- Registrar ubicacion cada dos minutos y retener eventos retrasados sin publicar estados contradictorios.

## Modelo de datos

### En dispositivo movil

```sql
CREATE TABLE mobile_outbox (
  local_event_id TEXT PRIMARY KEY,
  delivery_id TEXT NOT NULL,
  event_type TEXT NOT NULL,
  sequence_number INTEGER NOT NULL,
  encrypted_payload BLOB NOT NULL,
  payload_hash TEXT NOT NULL,
  correlation_id TEXT NOT NULL,
  original_timestamp TEXT NOT NULL,
  sync_status TEXT NOT NULL,
  retry_count INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE mobile_delivery_state (
  delivery_id TEXT PRIMARY KEY,
  route_id TEXT NOT NULL,
  current_status TEXT NOT NULL,
  last_synced_sequence INTEGER NOT NULL,
  encrypted_snapshot BLOB NOT NULL,
  updated_at TEXT NOT NULL
);
```

### En backend

```sql
CREATE TABLE mobile_sync_batch (
  sync_batch_id UUID PRIMARY KEY,
  device_id VARCHAR(100) NOT NULL,
  driver_id VARCHAR(80) NOT NULL,
  route_id VARCHAR(80) NOT NULL,
  received_events INTEGER NOT NULL,
  accepted_events INTEGER NOT NULL,
  rejected_events INTEGER NOT NULL,
  correlation_id VARCHAR(100) NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE delivery_tracking_event (
  tracking_event_id UUID PRIMARY KEY,
  delivery_id VARCHAR(100) NOT NULL,
  route_id VARCHAR(80) NOT NULL,
  event_type VARCHAR(60) NOT NULL,
  latitude NUMERIC(10,7),
  longitude NUMERIC(10,7),
  original_timestamp TIMESTAMP NOT NULL,
  received_at TIMESTAMP NOT NULL,
  sequence_number BIGINT NOT NULL,
  correlation_id VARCHAR(100) NOT NULL
);
```

## Funcionalidades

| Codigo | Funcionalidad | Contrato entrada | Contrato salida | Trazabilidad | Lineamientos |
|---|---|---|---|---|---|
| F-MOB-01 | Operar offline con datos cifrados | Ruta, entregas, evidencias pendientes, llave local segura | Estado local disponible y cola cifrada | `HU-INI03-RF01`, `HU-INI03-RF02`, `ESC-INI03-RF01-P01` | SEG-02, SEG-09, ARQ-03 |
| F-MOB-02 | Sincronizar store-and-forward | Lote ordenado de eventos, sequence, hashes, correlationId | Ack por evento, rechazo por secuencia o error funcional | `HU-INI03-RF03`, `HU-INI03-RF04`, `HU-INI03-RF05` | INT-06, INT-12, OBS-07, ESC-09 |
| F-MOB-03 | Tracking y cambio de dispositivo | Eventos de ubicacion cada 2 minutos, deviceId, driverId, ruta | Tracking publicado o retenido; recuperacion de pendientes | `HU-INI03-RF11`, `HU-INI03-RF12`, `ESC-INI03-RF12-N01` | SEG-09, OBS-05, INT-05 |

## Algoritmos

### F-MOB-01 - Offline cifrado

```text
descargar manifiesto de ruta y entregas asignadas
validar sesion, dispositivo y vigencia de token
cifrar snapshot local con llave protegida
registrar cada accion del conductor en mobile_outbox
si no hay conectividad:
  conservar eventos y evidencias localmente
mostrar estado operativo desde cache local
```

### F-MOB-02 - Store-and-forward

```text
detectar conectividad estable
ordenar eventos por delivery_id y sequence_number
enviar lote con hashes, timestamp original y correlationId
backend valida idempotencia y secuencia
si evento aceptado:
  devolver ack individual
  app marca evento como sincronizado
si falta evento previo:
  retener evento y solicitar reenvio de secuencia incompleta
si falla red:
  incrementar retry_count y programar backoff
```

### F-MOB-03 - Tracking y dispositivo

```text
generar tracking cada dos minutos durante ruta activa
si app esta offline:
  encolar tracking con timestamp original
al sincronizar, calcular retraso contra received_at
si retraso > 20 minutos:
  publicar alerta de tracking tardio
si conductor cambia dispositivo:
  restaurar manifiesto, eventos aceptados y pendientes desde backend
```

## Consideraciones de calidad

- MVP: API mock de sincronizacion con acks por evento y almacenamiento local cifrado.
- Resiliencia: store-and-forward, retry, backoff, idempotencia y secuencia por entrega.
- Seguridad: cifrado local, bloqueo de sesion, control de dispositivo y minimo privilegio.
- Observabilidad: backlog movil, eventos pendientes, tracking tardio, rechazos por secuencia y cambios de dispositivo.
