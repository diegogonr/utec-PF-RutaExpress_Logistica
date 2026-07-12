# HU-INI03-RF08 - Automatizar acciones por excepcion

- Iniciativa: INI-03
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-08

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI03-RF08 | Logistica | planner de ultima milla | automatizar acciones segun tipo de excepcion | generar reintentos, devoluciones, reasignaciones o escalamiento sin gestion manual innecesaria | RF-08 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI03-RF08 @RF-08
Feature: Automatizacion de excepciones
  Rule: Una excepcion confirmada debe disparar la accion definida por regla operativa

    @ESC-INI03-RF08-P01 @positivo
    Scenario: Crear reintento por destinatario ausente
      Given que una entrega tiene excepcion "Destinatario ausente"
      And la regla permite un reintento
      When el backend confirma la excepcion
      Then debe crear una tarea de reintento
      And debe notificar al TMS para replanificacion

    @ESC-INI03-RF08-N01 @negativo
    Scenario: Escalar excepcion sin regla automatica
      Given que una excepcion no tiene regla configurada
      When el servicio intenta automatizar la accion
      Then debe crear una tarea de revision manual
      And no debe generar reintento o devolucion sin autorizacion

    @ESC-INI03-RF08-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Automatizar acciones por excepcion" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI03-RF08-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Automatizar acciones por excepcion" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
