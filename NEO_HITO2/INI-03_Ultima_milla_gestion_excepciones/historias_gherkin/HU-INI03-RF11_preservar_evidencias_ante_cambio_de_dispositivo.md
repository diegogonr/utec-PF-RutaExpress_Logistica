# HU-INI03-RF11 - Preservar evidencias ante cambio de dispositivo

- Iniciativa: INI-03
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-11

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI03-RF11 | Logistica | supervisor de conductores | preservar evidencias pendientes ante cierre de sesion, reinicio, reinstalacion controlada o cambio de dispositivo gestionado | evitar entregas sin firma o foto | RF-11 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI03-RF11 @RF-11
Feature: Preservacion de evidencias pendientes
  Rule: Ninguna evidencia confirmada localmente debe quedar sin sincronizar o sin registro de remediacion

    @ESC-INI03-RF11-P01 @positivo
    Scenario: Bloquear cambio de dispositivo con pendientes
      Given que el conductor tiene evidencias pendientes
      When solicita cambio de dispositivo gestionado
      Then la app debe bloquear el descarte local
      And debe sincronizar, respaldar o transferir evidencias segun politica MDM

    @ESC-INI03-RF11-N01 @negativo
    Scenario: Registrar remediacion si evidencia no puede recuperarse
      Given que un dispositivo se pierde antes de sincronizar
      When no existe respaldo recuperable
      Then el sistema debe crear incidencia de remediacion
      And debe registrar responsable, ordenes afectadas y causa

    @ESC-INI03-RF11-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Preservar evidencias ante cambio de dispositivo" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI03-RF11-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Preservar evidencias ante cambio de dispositivo" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
