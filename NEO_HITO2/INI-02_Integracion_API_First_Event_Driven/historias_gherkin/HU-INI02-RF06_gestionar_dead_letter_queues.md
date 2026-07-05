# HU-INI02-RF06 - Gestionar dead-letter queues

- Iniciativa: INI-02
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-06

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI02-RF06 | Logistica | equipo de soporte | que los mensajes fallidos lleguen a DLQ con payload, error, timestamp y responsable | remediar fallas persistentes sin perder informacion | RF-06 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI02-RF06 @RF-06
Feature: Dead-letter queues
  Rule: Todo mensaje que supera reintentos debe quedar en DLQ con datos de remediacion

    @ESC-INI02-RF06-P01 @positivo
    Scenario: Enviar mensaje a DLQ tras reintentos agotados
      Given que un consumidor falla de forma persistente
      And se agotaron los reintentos configurados
      When la plataforma evalua el mensaje
      Then debe moverlo a DLQ
      And debe guardar payload, error, timestamp y consumidor responsable

    @ESC-INI02-RF06-N01 @negativo
    Scenario: Evitar reproceso manual sin autorizacion
      Given que un mensaje esta en DLQ
      And un usuario sin rol intenta reprocesarlo
      When solicita la remediacion
      Then la plataforma debe rechazar la accion
      And debe registrar el intento no autorizado

    @ESC-INI02-RF06-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Gestionar dead-letter queues" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI02-RF06-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Gestionar dead-letter queues" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
