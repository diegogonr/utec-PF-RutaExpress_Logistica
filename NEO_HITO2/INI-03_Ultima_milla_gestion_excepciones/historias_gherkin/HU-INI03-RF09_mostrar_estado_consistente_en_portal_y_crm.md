# HU-INI03-RF09 - Mostrar estado consistente en Portal y CRM

- Iniciativa: INI-03
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-09

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI03-RF09 | Logistica | agente de atencion y cliente B2B | que Portal B2B (APP-18) y CRM (APP-20) visualicen el mismo estado y motivo de excepcion | evitar respuestas contradictorias | RF-09 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI03-RF09 @RF-09
Feature: Consistencia de estado en canales
  Rule: Cliente y agente deben ver estado consistente con el evento confirmado por backend

    @ESC-INI03-RF09-P01 @positivo
    Scenario: Actualizar portal y CRM con la misma excepcion
      Given que el backend confirma una excepcion canonica
      When publica el evento de excepcion
      Then Portal B2B debe mostrar el mismo motivo que CRM
      And ambos deben conservar correlation ID

    @ESC-INI03-RF09-N01 @negativo
    Scenario: No mostrar excepcion no confirmada
      Given que una excepcion esta pendiente de sincronizacion
      When el portal consulta el estado de la entrega
      Then no debe mostrarla como confirmada
      And debe indicar estado pendiente o ultima informacion confiable

    @ESC-INI03-RF09-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Mostrar estado consistente en Portal y CRM" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI03-RF09-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Mostrar estado consistente en Portal y CRM" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
