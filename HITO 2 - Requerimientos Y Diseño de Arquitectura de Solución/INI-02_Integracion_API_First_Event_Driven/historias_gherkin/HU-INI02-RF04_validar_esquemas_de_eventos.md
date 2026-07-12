# HU-INI02-RF04 - Validar esquemas de eventos

- Iniciativa: INI-02
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-04

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI02-RF04 | Logistica | responsable de calidad de integracion | validar esquemas de eventos antes de aceptarlos | evitar datos incompletos o incompatibles en consumidores | RF-04 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI02-RF04 @RF-04
Feature: Validacion de esquemas de eventos
  Rule: Un evento con esquema invalido debe rechazarse o enviarse a cola de errores con motivo

    @ESC-INI02-RF04-P01 @positivo
    Scenario: Aceptar evento con esquema valido
      Given que un evento "InventarioReservado" contiene todos los campos obligatorios
      When el validador de esquemas lo procesa
      Then debe marcarlo como valido
      And debe permitir su publicacion a consumidores

    @ESC-INI02-RF04-N01 @negativo
    Scenario: Enviar evento invalido a cola de errores
      Given que un evento "OrdenValidada" no contiene orderId
      When el validador procesa el evento
      Then no debe entregarlo a consumidores
      And debe enviarlo a cola de errores con detalle funcional

    @ESC-INI02-RF04-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Validar esquemas de eventos" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI02-RF04-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Validar esquemas de eventos" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
