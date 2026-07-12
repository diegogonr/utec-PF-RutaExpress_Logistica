# HU-INI01-RF05 - Mantener estado canonico de orden

- Iniciativa: INI-01
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-05

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI01-RF05 | Logistica | operador logistico | que el OMS mantenga el estado canonico de la orden durante todo su ciclo de vida | que OMS, WMS, TMS, portal y ERP consulten la misma verdad operativa | RF-05 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI01-RF05 @RF-05
Feature: Estado canonico de la orden
  Rule: Los estados publicados deben ser consistentes entre sistemas consumidores

    @ESC-INI01-RF05-P01 @positivo
    Scenario: Publicar cambio de estado canonico
      Given que una orden pasa de "Validada" a "Reservada"
      When el OMS confirma la transicion de estado
      Then debe actualizar el estado canonico
      And debe registrar el historial de cambio
      And debe publicar "OrdenEstadoCambiado" con correlation ID

    @ESC-INI01-RF05-N01 @negativo
    Scenario: Bloquear transicion invalida de estado
      Given que una orden se encuentra en estado "Cancelada"
      When un sistema intenta cambiarla a "Reservada"
      Then el OMS debe rechazar la transicion
      And debe conservar el estado "Cancelada"
      And debe registrar el intento no permitido

    @ESC-INI01-RF05-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Mantener estado canonico de orden" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI01-RF05-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Mantener estado canonico de orden" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
