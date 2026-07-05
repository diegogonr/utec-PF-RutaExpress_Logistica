# HU-INI02-RF03 - Publicar eventos canonicos

- Iniciativa: INI-02
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-03

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI02-RF03 | Logistica | productor de eventos | publicar eventos canonicos desde OMS, WMS Cloud, TMS, App de Conductores y ERP | desacoplar consumidores y mantener trazabilidad | RF-03 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI02-RF03 @RF-03
Feature: Publicacion de eventos canonicos
  Rule: Cada productor debe publicar eventos validos con esquema y correlation ID obligatorio

    @ESC-INI02-RF03-P01 @positivo
    Scenario: Publicar evento OrdenValidada
      Given que OMS genera el evento "OrdenValidada"
      And el evento cumple el esquema vigente
      When se publica en Bus de Eventos Central (PLT-03)
      Then el bus debe aceptar el evento
      And debe entregarlo a consumidores suscritos

    @ESC-INI02-RF03-N01 @negativo
    Scenario: Rechazar evento sin correlation ID
      Given que un productor envia un evento sin correlation ID
      When el bus valida los metadatos
      Then debe rechazar el evento
      And debe registrar el motivo de rechazo

    @ESC-INI02-RF03-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Publicar eventos canonicos" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI02-RF03-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Publicar eventos canonicos" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
