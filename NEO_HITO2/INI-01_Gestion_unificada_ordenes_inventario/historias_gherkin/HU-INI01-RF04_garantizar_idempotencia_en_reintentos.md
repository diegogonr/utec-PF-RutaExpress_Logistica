# HU-INI01-RF04 - Garantizar idempotencia en reintentos

- Iniciativa: INI-01
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-04

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI01-RF04 | Logistica | cliente integrador | que los reintentos de creacion, actualizacion, reserva y cancelacion sean idempotentes | que errores temporales no generen doble orden, doble reserva ni doble movimiento | RF-04 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI01-RF04 @RF-04
Feature: Idempotencia de operaciones de orden e inventario
  Rule: Reenviar la misma solicitud no debe duplicar efectos de negocio

    @ESC-INI01-RF04-P01 @positivo
    Scenario: Reintentar creacion con la misma clave idempotente
      Given que una solicitud de creacion fue procesada correctamente
      And el cliente reenvia la misma solicitud con la misma idempotency key
      When el OMS recibe el reintento
      Then debe devolver el mismo orderId original
      And no debe crear una orden adicional
      And debe registrar el intento como idempotente

    @ESC-INI01-RF04-N01 @negativo
    Scenario: Rechazar reuso de clave idempotente con payload distinto
      Given que existe una idempotency key asociada a una orden previa
      And el cliente envia otra orden con la misma clave pero distinto contenido
      When el OMS compara el hash del payload
      Then debe rechazar la solicitud por conflicto de idempotencia
      And no debe modificar la orden original

    @ESC-INI01-RF04-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Garantizar idempotencia en reintentos" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI01-RF04-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Garantizar idempotencia en reintentos" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
