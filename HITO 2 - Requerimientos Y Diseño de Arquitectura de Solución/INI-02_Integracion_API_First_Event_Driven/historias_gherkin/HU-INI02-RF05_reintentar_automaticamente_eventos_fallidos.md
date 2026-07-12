# HU-INI02-RF05 - Reintentar automaticamente eventos fallidos

- Iniciativa: INI-02
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-05

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI02-RF05 | Logistica | operador de integracion | reintentos automaticos con politica configurable por tipo de evento | recuperar consumidores temporalmente no disponibles | RF-05 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI02-RF05 @RF-05
Feature: Reintentos automaticos de eventos
  Rule: Un consumidor temporalmente no disponible debe recibir el evento al recuperarse o tras reintentos programados

    @ESC-INI02-RF05-P01 @positivo
    Scenario: Reentregar evento tras recuperacion de consumidor
      Given que TMS esta temporalmente no disponible
      And existe un evento valido pendiente
      When TMS se recupera antes de agotar reintentos
      Then la plataforma debe reenviar el evento
      And debe registrar entrega exitosa

    @ESC-INI02-RF05-N01 @negativo
    Scenario: No perder evento por timeout temporal
      Given que un consumidor no responde dentro del timeout
      When la plataforma aplica la politica de retry
      Then debe conservar el mensaje durable
      And no debe marcarlo como entregado sin ACK

    @ESC-INI02-RF05-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Reintentar automaticamente eventos fallidos" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI02-RF05-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Reintentar automaticamente eventos fallidos" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
