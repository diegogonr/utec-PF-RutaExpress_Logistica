# HU-INI03-RF04 - Confirmar recepcion backend

- Iniciativa: INI-03
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-04

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI03-RF04 | Logistica | conductor | que el backend confirme recepcion y persistencia de cada evento o evidencia | que la app elimine datos locales solo cuando sea seguro | RF-04 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI03-RF04 @RF-04
Feature: Confirmacion backend de eventos y evidencias
  Rule: La app no debe eliminar datos locales hasta recibir confirmacion backend

    @ESC-INI03-RF04-P01 @positivo
    Scenario: Liberar evidencia tras confirmacion backend
      Given que la app envio una evidencia pendiente
      And el backend confirma persistencia en S3 y metadata
      When la app recibe el ACK
      Then debe marcar la evidencia como "Sincronizada"
      And puede liberar la copia local segun politica

    @ESC-INI03-RF04-N01 @negativo
    Scenario: Conservar evidencia sin ACK
      Given que la app envio una evidencia al backend
      And no recibio confirmacion de persistencia
      When finaliza el intento de sincronizacion
      Then no debe eliminar la evidencia local
      And debe programar reintento automatico

    @ESC-INI03-RF04-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Confirmar recepcion backend" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI03-RF04-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Confirmar recepcion backend" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
