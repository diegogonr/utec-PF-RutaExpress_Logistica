# HU-INI01-RF01 - Registrar orden con identificador interno unico

- Iniciativa: INI-01
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-01

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI01-RF01 | Logistica | operador de recepcion B2B | que el OMS centralizado / Orquestador de Pedidos (APP-02) registre toda orden recibida desde API, portal o carga masiva con un identificador interno unico | asegurar trazabilidad desde el ingreso | RF-01 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI01-RF01 @RF-01
Feature: Registro de ordenes en OMS
  Rule: Toda orden aceptada debe quedar registrada con ID interno, canal, cliente, timestamp y estado inicial Recibida

    @ESC-INI01-RF01-P01 @positivo
    Scenario: Registrar orden valida desde API
      Given que un cliente B2B envia una orden valida por API
      And la solicitud contiene cliente, canal, lineas, destinatario y ventana horaria
      When el OMS recibe la orden
      Then debe generar un identificador interno unico
      And debe registrar el estado inicial "Recibida"
      And debe asociar canal, cliente, timestamp y correlation ID

    @ESC-INI01-RF01-N01 @negativo
    Scenario: Rechazar registro sin cliente
      Given que una orden llega sin identificador de cliente
      When el OMS intenta registrarla
      Then no debe crear un identificador interno de orden aceptada
      And debe devolver un error funcional de contrato
      And debe registrar el rechazo con correlation ID

    @ESC-INI01-RF01-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Registrar orden con identificador interno unico" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI01-RF01-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Registrar orden con identificador interno unico" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
