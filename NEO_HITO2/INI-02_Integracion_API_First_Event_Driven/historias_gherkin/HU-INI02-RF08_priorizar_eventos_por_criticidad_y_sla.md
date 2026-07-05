# HU-INI02-RF08 - Priorizar eventos por criticidad y SLA

- Iniciativa: INI-02
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-08

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI02-RF08 | Logistica | operador de campana | priorizar eventos por criticidad y SLA | que reservas, entregas y liquidacion se atiendan antes que eventos informativos | RF-08 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI02-RF08 @RF-08
Feature: Priorizacion de eventos
  Rule: Los eventos criticos deben procesarse antes que eventos informativos

    @ESC-INI02-RF08-P01 @positivo
    Scenario: Procesar reserva critica antes que evento informativo
      Given que existe un evento "InventarioReservado" critico
      And existe un evento informativo de auditoria
      When la cola selecciona el siguiente mensaje
      Then debe procesar primero el evento critico
      And debe conservar trazabilidad de prioridad

    @ESC-INI02-RF08-N01 @negativo
    Scenario: Evitar prioridad no autorizada
      Given que un productor intenta marcar un evento informativo como critico
      When la plataforma valida la politica de prioridad
      Then debe corregir o rechazar la prioridad
      And debe registrar el evento de gobierno

    @ESC-INI02-RF08-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Priorizar eventos por criticidad y SLA" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI02-RF08-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Priorizar eventos por criticidad y SLA" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
