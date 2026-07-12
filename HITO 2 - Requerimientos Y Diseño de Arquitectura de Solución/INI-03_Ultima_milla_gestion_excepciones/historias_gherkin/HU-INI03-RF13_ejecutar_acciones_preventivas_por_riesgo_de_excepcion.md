# HU-INI03-RF13 - Ejecutar acciones preventivas por riesgo de excepcion

- Iniciativa: INI-03
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-13

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI03-RF13 | Logistica | equipo de atencion preventiva | generar acciones preventivas por direccion o ausencia | reducir fallas antes del siguiente intento de entrega | RF-13 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI03-RF13 @RF-13
Feature: Prevencion de excepciones
  Rule: Cuando se detecta riesgo de direccion o ausencia se debe generar tarea de contacto, ajuste de ventana o validacion

    @ESC-INI03-RF13-P01 @positivo
    Scenario: Crear tarea preventiva por direccion riesgosa
      Given que el sistema detecta historial de direccion incorrecta para una entrega
      When evalua el riesgo antes de la ruta
      Then debe crear una tarea de contacto o validacion
      And debe informar al TMS si se ajusta la ventana

    @ESC-INI03-RF13-N01 @negativo
    Scenario: No crear accion preventiva sin evidencia de riesgo
      Given que una entrega no tiene historial de fallas ni alertas de direccion
      When el sistema evalua riesgo de excepcion
      Then no debe crear tareas preventivas innecesarias
      And debe conservar la planificacion original

    @ESC-INI03-RF13-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Ejecutar acciones preventivas por riesgo de excepcion" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI03-RF13-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Ejecutar acciones preventivas por riesgo de excepcion" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
