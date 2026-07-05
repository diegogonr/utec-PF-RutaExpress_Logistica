# HU-INI03-RF01 - Operar entregas sin conectividad

- Iniciativa: INI-03
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-01

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI03-RF01 | Logistica | conductor | que App de Conductores (APP-15) permita operar entregas asignadas sin conectividad movil | continuar la ruta aun en zonas con mala senal | RF-01 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI03-RF01 @RF-01
Feature: Operacion offline de entregas
  Rule: El conductor debe visualizar ruta, paquetes, destinatario y registrar eventos offline

    @ESC-INI03-RF01-P01 @positivo
    Scenario: Consultar ruta descargada sin conexion
      Given que el conductor descargo su ruta antes de salir
      And el dispositivo no tiene conectividad
      When abre la App de Conductores
      Then debe visualizar ruta, paquetes y destinatarios asignados
      And debe poder iniciar registro de eventos offline

    @ESC-INI03-RF01-N01 @negativo
    Scenario: Bloquear ruta no descargada
      Given que el conductor no descargo la ruta
      And el dispositivo no tiene conectividad
      When intenta operar la ruta
      Then la app debe informar que no existe snapshot offline
      And no debe permitir registrar eventos sin ruta asociada

    @ESC-INI03-RF01-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Operar entregas sin conectividad" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI03-RF01-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Operar entregas sin conectividad" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
