# HU-INI01-RF11 - Priorizar ordenes por SLA y canal

- Iniciativa: INI-01
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-11

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI01-RF11 | Logistica | planner de campana | que el OMS priorice ordenes por SLA y canal durante picos | procesar ordenes criticas sin bloquear el flujo regular | RF-11 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI01-RF11 @RF-11
Feature: Priorizacion de ordenes en campana
  Rule: Las ordenes criticas deben procesarse con prioridad configurable sin detener el flujo normal

    @ESC-INI01-RF11-P01 @positivo
    Scenario: Procesar orden express con prioridad alta
      Given que una orden tiene SLA "Express" y canal prioritario
      When el OMS la encola para validacion y reserva
      Then debe asignarle prioridad alta
      And debe procesarla antes que ordenes informativas o de menor SLA

    @ESC-INI01-RF11-N01 @negativo
    Scenario: Evitar starvation de ordenes regulares
      Given que existe una alta cantidad de ordenes prioritarias
      And tambien hay ordenes regulares pendientes
      When el OMS aplica la politica de prioridad
      Then no debe bloquear indefinidamente las ordenes regulares
      And debe registrar metricas de espera por prioridad

    @ESC-INI01-RF11-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Priorizar ordenes por SLA y canal" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI01-RF11-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Priorizar ordenes por SLA y canal" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
