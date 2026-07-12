# HU-INI03-RF02 - Almacenar localmente datos cifrados

- Iniciativa: INI-03
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-02

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI03-RF02 | Logistica | responsable de seguridad movil | que la app almacene localmente y de forma cifrada eventos, firma, foto, GPS, timestamp y excepciones | proteger evidencias y datos personales | RF-02 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI03-RF02 @RF-02
Feature: Almacenamiento local cifrado
  Rule: Los datos capturados offline deben permanecer disponibles tras cierre o reapertura de la app

    @ESC-INI03-RF02-P01 @positivo
    Scenario: Preservar evidencia tras reinicio de app
      Given que el conductor captura firma, foto, GPS y timestamp offline
      When cierra y vuelve a abrir la app
      Then la evidencia debe seguir disponible en almacenamiento cifrado
      And debe mantener estado "Pendiente de sincronizacion"

    @ESC-INI03-RF02-N01 @negativo
    Scenario: Impedir acceso local sin sesion valida
      Given que el dispositivo contiene datos offline cifrados
      When un usuario no autenticado intenta acceder a la app
      Then la app debe bloquear el acceso
      And no debe exponer datos de destinatario ni evidencias

    @ESC-INI03-RF02-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Almacenar localmente datos cifrados" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI03-RF02-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Almacenar localmente datos cifrados" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
