# Secuencia INI-01 - Ordenes, inventario y conciliacion

## Trazabilidad

- RF cubiertos: RF-01 a RF-12 de INI-01.
- Historias cubiertas: `HU-INI01-RF01` a `HU-INI01-RF12`.
- Escenarios clave: orden valida, pedido duplicado, reserva de inventario, inventario insuficiente, degradacion de WMS y conciliacion de inventario.

## Diagrama Mermaid

```mermaid
sequenceDiagram
    autonumber
    participant Cliente as Cliente B2B / Portal
    participant APIGW as API Gateway gobernado
    participant OMS as OMS Ordenes (APP-02 evolucionado)
    participant Dedupe as Idempotencia y Deduplicacion
    participant INV as Inventario y Reservas
    participant WMS as WMS Cloud / WMS On Premises
    participant ERP as ERP Financiero (APP-25)
    participant BUS as Bus de Eventos Central (PLT-03)
    participant OBS as Observabilidad (PLT-01)

    Cliente->>APIGW: POST /orders + idempotencyKey + correlationId
    APIGW->>OMS: Solicitud validada por contrato y seguridad
    OMS->>Dedupe: Validar clave idempotente y hash logistico
    alt Orden duplicada
        Dedupe-->>OMS: Orden original encontrada
        OMS->>BUS: Publicar OrderDuplicateDetected
        OMS-->>Cliente: 200 referencia de orden original
        OMS->>OBS: Metrica orden duplicada
    else Orden nueva y valida
        Dedupe-->>OMS: Sin duplicidad
        OMS->>OMS: Validar datos, SLA y estado inicial
        OMS->>INV: ReserveInventoryCommand
        INV->>WMS: Consultar disponibilidad SKU/almacen/lote
        alt Inventario suficiente
            WMS-->>INV: Disponibilidad confirmada
            INV->>INV: Persistir reserva con control de version
            INV->>ERP: Solicitar valorizacion / impacto financiero
            ERP-->>INV: Valorizacion aceptada
            INV->>BUS: InventoryReserved
            OMS->>BUS: OrderAccepted
            OMS-->>Cliente: 201 orderId y estado ACCEPTED
        else Inventario insuficiente
            WMS-->>INV: Stock insuficiente
            INV->>BUS: InventoryInsufficient
            OMS->>BUS: OrderRejectedByInventory
            OMS-->>Cliente: 409 inventario insuficiente
        else WMS degradado
            WMS--xINV: Timeout / saturacion
            INV->>INV: Activar circuit breaker y backpressure
            INV->>BUS: ReservationPendingDueWmsDegradation
            OMS-->>Cliente: 202 orden retenida por validacion asincrona
            OBS->>OBS: Alerta backlog WMS y latencia
        end
    end

    opt Reconexion de WMS local
        WMS->>INV: Snapshot de inventario local
        INV->>INV: Comparar contra vista canonica
        alt Conflicto conciliable
            INV->>BUS: InventoryConflictResolved
            INV->>OBS: Auditoria de ajuste
        else Conflicto afecta orden SLA
            INV->>BUS: InventoryConflictPending
            INV->>OMS: Notificar orden en riesgo
            OMS->>BUS: OrderAtRisk
        end
    end
```

## Patrones aplicados

- DDD y microservicios por dominio de orden e inventario.
- API Gateway, contratos versionados, idempotency key y deduplicacion por hash.
- Saga orden-inventario-valorizacion con eventos de compensacion.
- Outbox, circuit breaker, backpressure, DLQ y retry con backoff.
- Correlation ID end-to-end y auditoria funcional.
