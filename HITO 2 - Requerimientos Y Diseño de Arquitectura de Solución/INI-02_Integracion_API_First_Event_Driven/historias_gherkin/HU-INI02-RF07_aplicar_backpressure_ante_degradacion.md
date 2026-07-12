# HU-INI02-RF07 - Aplicar backpressure ante degradacion

- Iniciativa: INI-02
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-07

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI02-RF07 | Logistica | administrador de plataforma | aplicar backpressure para proteger WMS, ERP u otros destinos degradados | no saturar sistemas criticos ni perder orden | RF-07 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI02-RF07 @RF-07
Feature: Backpressure de integraciones
  Rule: Los mensajes deben regularse sin perder orden ni saturar el destino degradado

    @ESC-INI02-RF07-P01 @positivo
    Scenario: Regular envios hacia WMS degradado
      Given que WMS Cloud reporta latencia alta
      And existen eventos de reserva pendientes
      When la plataforma detecta el umbral de degradacion
      Then debe reducir la tasa de envio
      And debe mantener mensajes en cola priorizada

    @ESC-INI02-RF07-N01 @negativo
    Scenario: No descartar mensajes por saturacion
      Given que la cola de reservas crece durante campana
      When se activa backpressure
      Then la plataforma no debe descartar mensajes aceptados
      And debe alertar por saturacion y backlog

    @ESC-INI02-RF07-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Aplicar backpressure ante degradacion" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI02-RF07-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Aplicar backpressure ante degradacion" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
