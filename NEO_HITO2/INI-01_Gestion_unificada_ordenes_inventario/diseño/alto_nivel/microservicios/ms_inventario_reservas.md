# MS-INI01-02 - Inventario y Reservas

## Identificacion

- Iniciativa: INI-01 Gestion unificada de ordenes e inventario end-to-end.
- Componente TO BE: servicio de dominio asociado al OMS centralizado, WMS Cloud y WMS Principal (On Premises) (APP-06) durante transicion.
- Fuentes: `01_Requerimientos_y_Criterios_Aceptacion.md` e historias `HU-INI01-RF06` a `HU-INI01-RF09` y `HU-INI01-RF12`.
- Alcance: disponibilidad por SKU, almacen, ubicacion, lote y estado; reservas, liberaciones, movimientos y conciliacion de conflictos.

## Responsabilidades

- Mantener vista unificada de inventario disponible, reservado, bloqueado y en conflicto.
- Consultar disponibilidad antes de confirmar reservas.
- Coordinar reserva fisica con WMS y valorizacion o impacto financiero con ERP.
- Registrar eventos auditables de movimientos y reservas.
- Conciliar diferencias entre WMS central, WMS locales y reconexiones post-degradacion.
- Proteger WMS on premises con backpressure y procesamiento asincrono cuando aplique.

## Modelo de datos

```sql
CREATE TABLE inventory_position (
  position_id UUID PRIMARY KEY,
  sku VARCHAR(60) NOT NULL,
  warehouse_id VARCHAR(40) NOT NULL,
  location_id VARCHAR(60) NOT NULL,
  lot_id VARCHAR(60),
  stock_status VARCHAR(30) NOT NULL,
  available_qty NUMERIC(14,3) NOT NULL,
  reserved_qty NUMERIC(14,3) NOT NULL DEFAULT 0,
  blocked_qty NUMERIC(14,3) NOT NULL DEFAULT 0,
  version BIGINT NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

CREATE UNIQUE INDEX ux_inventory_dimension
ON inventory_position(sku, warehouse_id, location_id, COALESCE(lot_id, ''), stock_status);

CREATE TABLE inventory_reservation (
  reservation_id UUID PRIMARY KEY,
  order_id UUID NOT NULL,
  sku VARCHAR(60) NOT NULL,
  warehouse_id VARCHAR(40) NOT NULL,
  lot_id VARCHAR(60),
  reserved_qty NUMERIC(14,3) NOT NULL,
  reservation_status VARCHAR(30) NOT NULL,
  expires_at TIMESTAMP,
  correlation_id VARCHAR(100) NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE inventory_conflict (
  conflict_id UUID PRIMARY KEY,
  sku VARCHAR(60) NOT NULL,
  warehouse_id VARCHAR(40) NOT NULL,
  source_system VARCHAR(40) NOT NULL,
  detected_qty NUMERIC(14,3) NOT NULL,
  canonical_qty NUMERIC(14,3) NOT NULL,
  conflict_status VARCHAR(30) NOT NULL,
  resolution_rule VARCHAR(60),
  correlation_id VARCHAR(100) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  resolved_at TIMESTAMP NULL
);

CREATE TABLE inventory_event_log (
  event_id UUID PRIMARY KEY,
  aggregate_id UUID NOT NULL,
  event_type VARCHAR(80) NOT NULL,
  payload_json JSON NOT NULL,
  source_system VARCHAR(40) NOT NULL,
  correlation_id VARCHAR(100) NOT NULL,
  created_at TIMESTAMP NOT NULL
);
```

## Funcionalidades

| Codigo | Funcionalidad | Contrato entrada | Contrato salida | Trazabilidad | Lineamientos |
|---|---|---|---|---|---|
| F-INV-01 | Consultar disponibilidad y reservar | `ReserveInventoryCommand` con `orderId`, SKUs, cantidad, almacen preferido, SLA y `correlationId` | `ReservationConfirmed`, `ReservationRejected` o `InventoryInsufficient` | `HU-INI01-RF06`, `HU-INI01-RF08`, `ESC-INI01-RF06-P01`, `ESC-INI01-RF08-N01` | ARQ-01, INT-02, INT-06, ESC-07 |
| F-INV-02 | Registrar movimientos auditables | Evento de WMS/OMS con SKU, almacen, ubicacion, lote, cantidad, estado y version | Movimiento persistido, evento canonico y metricas | `HU-INI01-RF07`, `ESC-INI01-RF07-P01`, `ESC-INI01-RF07-N02` | SEG-07, OBS-04, OBS-09 |
| F-INV-03 | Conciliar conflictos | Snapshot WMS local, snapshot WMS central, reglas de precedencia y tolerancias | Conflicto resuelto, ajuste pendiente o bloqueo operativo | `HU-INI01-RF09`, `HU-INI01-RF12`, `ESC-INI01-RF09-P01`, `ESC-INI01-RF12-N01` | ARQ-09, INT-11, ESC-06, OBS-05 |

## Algoritmos

### F-INV-01 - Reserva de inventario

```text
recibir comando de reserva desde OMS
validar correlationId y version de contrato
leer posiciones candidatas por SKU, almacen, lote y estado
si disponibilidad total < cantidad:
  publicar InventoryInsufficient
  responder rechazo funcional al OMS
abrir transaccion por posicion con control optimista de version
descontar available_qty y aumentar reserved_qty
crear inventory_reservation
publicar InventoryReserved y solicitar valorizacion a ERP si aplica
```

### F-INV-02 - Movimiento auditable

```text
validar esquema de evento recibido
verificar idempotencyKey del movimiento
persistir movimiento en inventory_event_log
actualizar inventory_position con version incremental
si el evento llega fuera de orden:
  retener en inbox y marcar secuencia incompleta
emitir metrica de movimientos, ajustes y retrasos
```

### F-INV-03 - Conciliacion

```text
recibir lote de reconciliacion desde WMS local o central
comparar snapshot contra inventario canonico por SKU, almacen, ubicacion, lote y estado
clasificar diferencia: tolerable, requiere ajuste, requiere bloqueo
si existe reserva afectada:
  notificar OMS y priorizar por SLA
si WMS esta degradado:
  activar backpressure y cola durable
registrar conflicto y resolucion con auditoria
publicar InventoryConflictResolved o InventoryConflictPending
```

## Consideraciones de calidad

- Dimensionamiento: 210,000 movimientos diarios y picos de campana con proteccion al WMS on premises.
- Consistencia: control optimista, idempotencia y secuencia logica por SKU/almacen/lote.
- Resiliencia: colas durables, DLQ para eventos no conciliables y circuit breaker hacia WMS/ERP.
- Observabilidad: alertas de conflictos, reservas rechazadas, backlog WMS, DLQ y latencia de conciliacion.
- Seguridad: minimo privilegio sobre reservas, auditoria de ajustes y cifrado de datos sensibles.
