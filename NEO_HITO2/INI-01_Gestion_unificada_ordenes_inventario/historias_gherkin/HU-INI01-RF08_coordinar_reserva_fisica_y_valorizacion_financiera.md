# HU-INI01-RF08 - Coordinar reserva fisica y valorizacion financiera

- Iniciativa: INI-01
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-08

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI01-RF08 | Logistica | responsable de operaciones y finanzas | que el OMS coordine con WMS Cloud la reserva fisica y con ERP Financiero (APP-25) el inventario valorizado | que la operacion y la liquidacion usen datos consistentes | RF-08 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI01-RF08 @RF-08
Feature: Coordinacion OMS, WMS Cloud y ERP
  Rule: Una reserva confirmada por WMS Cloud debe quedar disponible para ERP mediante API o evento

    @ESC-INI01-RF08-P01 @positivo
    Scenario: Notificar reserva confirmada al ERP
      Given que WMS Cloud confirma la reserva fisica de una orden
      When el OMS recibe la confirmacion
      Then debe publicar el evento "InventarioReservado"
      And ERP Financiero debe recibir la informacion de inventario valorizado
      And ambos mensajes deben conservar el mismo correlation ID

    @ESC-INI01-RF08-N01 @negativo
    Scenario: No notificar valorizacion sin reserva fisica
      Given que WMS Cloud rechaza la reserva por falta de stock
      When el OMS procesa la respuesta
      Then no debe enviar inventario valorizado como reservado al ERP
      And debe publicar "InventarioNoDisponible"

    @ESC-INI01-RF08-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Coordinar reserva fisica y valorizacion financiera" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI01-RF08-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Coordinar reserva fisica y valorizacion financiera" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
