# HU-INI03-RF07 - Exigir motivo obligatorio para entrega fallida

- Iniciativa: INI-03
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-07

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI03-RF07 | Logistica | supervisor de ruta | que el conductor seleccione un motivo obligatorio cuando una entrega no se completa | evitar texto libre no clasificable | RF-07 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI03-RF07 @RF-07
Feature: Motivo obligatorio de entrega fallida
  Rule: No se puede cerrar una entrega fallida sin clasificacion canonica

    @ESC-INI03-RF07-P01 @positivo
    Scenario: Cerrar entrega fallida con motivo canonico
      Given que el conductor no puede completar una entrega
      And selecciona un motivo canonico vigente
      When confirma la entrega fallida
      Then la app debe registrar la excepcion
      And debe permitir comentario opcional y evidencia

    @ESC-INI03-RF07-N01 @negativo
    Scenario: Bloquear cierre sin motivo
      Given que el conductor intenta cerrar una entrega como fallida
      And no selecciona motivo de excepcion
      When presiona confirmar
      Then la app debe bloquear el cierre
      And debe mostrar "Seleccione un motivo de excepcion"

    @ESC-INI03-RF07-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Exigir motivo obligatorio para entrega fallida" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI03-RF07-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Exigir motivo obligatorio para entrega fallida" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
