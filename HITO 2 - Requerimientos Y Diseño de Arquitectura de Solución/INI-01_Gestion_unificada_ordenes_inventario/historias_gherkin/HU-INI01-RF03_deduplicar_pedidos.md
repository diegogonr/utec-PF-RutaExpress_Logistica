# HU-INI01-RF03 - Deduplicar pedidos

- Iniciativa: INI-01
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-03

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI01-RF03 | Logistica | responsable de integracion | que el OMS aplique deduplicacion por hash de contenido, identificador externo, cliente, destinatario y ventana temporal configurable | evitar doble procesamiento por reintentos de clientes | RF-03 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI01-RF03 @RF-03
Feature: Deduplicacion de pedidos
  Rule: Una orden duplicada debe devolver la referencia de la orden original y no procesarse dos veces

    @ESC-INI01-RF03-P01 @positivo
    Scenario: Detectar duplicado con identificador externo diferente
      Given que existe una orden previa con mismo cliente, destinatario, SKU, cantidad y ventana
      And el cliente reenvia la orden con otro identificador externo
      When el OMS calcula el hash de contenido
      Then debe detectar la orden como duplicada
      And debe devolver el identificador de la orden original
      And no debe crear una nueva reserva

    @ESC-INI01-RF03-N01 @negativo
    Scenario: No marcar como duplicada una orden similar fuera de ventana
      Given que existe una orden similar del mismo cliente y destinatario
      And la nueva orden corresponde a una ventana temporal distinta
      When el OMS ejecuta la regla de deduplicacion
      Then no debe clasificarla como duplicada
      And debe continuar con la validacion normal

    @ESC-INI01-RF03-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Deduplicar pedidos" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI01-RF03-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Deduplicar pedidos" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
