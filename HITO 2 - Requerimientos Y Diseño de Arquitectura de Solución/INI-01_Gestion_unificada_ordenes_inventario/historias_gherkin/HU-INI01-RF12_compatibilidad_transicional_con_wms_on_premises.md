# HU-INI01-RF12 - Compatibilidad transicional con WMS on premises

- Iniciativa: INI-01
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-12

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI01-RF12 | Logistica | arquitecto de transicion | conservar compatibilidad con WMS Principal (On Premises) (APP-06) mientras WMS Cloud no este completamente desplegado | no interrumpir la operacion de almacenes | RF-12 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI01-RF12 @RF-12
Feature: Compatibilidad transicional WMS
  Rule: Las reservas via WMS Principal deben publicarse con el mismo modelo canonico y correlation ID

    @ESC-INI01-RF12-P01 @positivo
    Scenario: Procesar reserva mediante WMS Principal
      Given que un almacen aun opera con WMS Principal on premises
      When el OMS solicita una reserva transicional
      Then el adaptador WMS debe transformar la respuesta al modelo canonico
      And debe publicar el evento con correlation ID

    @ESC-INI01-RF12-N01 @negativo
    Scenario: Activar backpressure por degradacion de WMS Principal
      Given que WMS Principal presenta latencia alta o errores recurrentes
      When el adaptador detecta degradacion
      Then debe reducir la tasa de envio
      And debe encolar solicitudes pendientes sin perder mensajes
      And no debe marcar reservas como confirmadas sin respuesta consistente

    @ESC-INI01-RF12-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Compatibilidad transicional con WMS on premises" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI01-RF12-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Compatibilidad transicional con WMS on premises" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
