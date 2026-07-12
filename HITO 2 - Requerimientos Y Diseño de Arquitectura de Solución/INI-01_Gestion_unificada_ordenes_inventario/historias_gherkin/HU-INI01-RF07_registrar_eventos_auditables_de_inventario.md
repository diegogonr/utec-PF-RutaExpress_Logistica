# HU-INI01-RF07 - Registrar eventos auditables de inventario

- Iniciativa: INI-01
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-07

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI01-RF07 | Logistica | auditor operativo | que reservas, liberaciones, cancelaciones y movimientos de inventario queden como eventos auditables | reconstruir cada cambio con responsable, motivo y correlation ID | RF-07 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI01-RF07 @RF-07
Feature: Auditoria de eventos de inventario
  Rule: Cada cambio de inventario debe tener orden asociada, actor, timestamp, motivo y correlation ID

    @ESC-INI01-RF07-P01 @positivo
    Scenario: Registrar reserva como evento auditable
      Given que WMS Cloud confirma una reserva de inventario
      When el servicio de inventario actualiza la reserva
      Then debe publicar el evento "InventarioReservado"
      And debe guardar orderId, actor, timestamp, motivo y correlation ID

    @ESC-INI01-RF07-N01 @negativo
    Scenario: Rechazar movimiento sin motivo
      Given que un sistema intenta registrar una liberacion sin motivo funcional
      When el servicio de inventario valida el evento
      Then debe rechazar el movimiento
      And debe registrar el error de auditoria
      And no debe modificar la disponibilidad del inventario

    @ESC-INI01-RF07-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Registrar eventos auditables de inventario" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI01-RF07-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Registrar eventos auditables de inventario" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
