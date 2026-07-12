# HU-INI02-RF12 - Convivir con integraciones punto a punto

- Iniciativa: INI-02
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-12

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI02-RF12 | Logistica | arquitecto de migracion | soportar convivencia transicional entre integraciones punto a punto y flujos event-driven | migrar sin romper la operacion | RF-12 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI02-RF12 @RF-12
Feature: Convivencia transicional de integraciones
  Rule: Cada integracion migrada debe tener adaptador, contrato, monitoreo y plan de rollback

    @ESC-INI02-RF12-P01 @positivo
    Scenario: Migrar integracion con adaptador monitoreado
      Given que una integracion legacy por archivo sera migrada a eventos
      When se habilita el adaptador transicional
      Then debe publicar eventos canonicos
      And debe registrar metricas y plan de rollback

    @ESC-INI02-RF12-N01 @negativo
    Scenario: Bloquear migracion sin contrato documentado
      Given que un flujo punto a punto no tiene contrato versionado
      When se solicita pasarlo a produccion event-driven
      Then la plataforma debe bloquear la migracion
      And debe solicitar contrato, pruebas y monitoreo

    @ESC-INI02-RF12-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Convivir con integraciones punto a punto" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI02-RF12-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Convivir con integraciones punto a punto" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
