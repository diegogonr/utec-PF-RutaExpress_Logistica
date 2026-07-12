# HU-INI03-RF12 - Registrar y sincronizar ubicacion cada dos minutos

- Iniciativa: INI-03
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-12

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI03-RF12 | Logistica | supervisor de transporte | que la app registre y sincronice ubicacion cada 2 minutos con timestamp original | mejorar tracking confiable y trazabilidad de ruta | RF-12 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI03-RF12 @RF-12
Feature: Tracking periodico de ubicacion
  Rule: TMS y portal deben recibir eventos con secuencia, timestamp original y estado de sincronizacion

    @ESC-INI03-RF12-P01 @positivo
    Scenario: Enviar ubicacion periodica con conectividad
      Given que el conductor esta en ruta con conectividad
      When transcurren 2 minutos desde el ultimo tracking
      Then la app debe registrar ubicacion GPS
      And debe sincronizarla al backend con secuencia y timestamp

    @ESC-INI03-RF12-N01 @negativo
    Scenario: Encolar ubicaciones durante perdida de red
      Given que el dispositivo pierde conectividad durante 20 minutos
      When la app captura eventos de ubicacion
      Then debe encolarlos localmente
      And al recuperar red debe enviarlos con timestamp original

    @ESC-INI03-RF12-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Registrar y sincronizar ubicacion cada dos minutos" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI03-RF12-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Registrar y sincronizar ubicacion cada dos minutos" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
