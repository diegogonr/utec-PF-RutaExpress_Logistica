# HU-INI01-RF02 - Validar datos obligatorios y reglas logisticas

- Iniciativa: INI-01
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-02

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI01-RF02 | Logistica | analista de mesa B2B | que el OMS valide campos obligatorios, direccion, SKU, cliente, promesa SLA y ventana horaria antes de aceptar la orden | evitar errores que impacten almacen, ruta y entrega | RF-02 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI01-RF02 @RF-02
Feature: Validacion de ordenes
  Rule: Una orden con datos invalidos no debe reservar inventario

    @ESC-INI01-RF02-P01 @positivo
    Scenario: Validar orden completa
      Given que la orden contiene direccion completa, SKU existente, cliente activo, SLA y ventana valida
      When el OMS ejecuta la validacion funcional
      Then debe marcar la orden como "Validada"
      And debe permitir continuar con la consulta de inventario
      And debe publicar el evento "OrdenValidada"

    @ESC-INI01-RF02-N01 @negativo
    Scenario: Marcar orden pendiente por direccion incompleta
      Given que la orden no contiene distrito o referencia de entrega
      When el OMS valida los datos de direccion
      Then debe marcar la orden como "Pendiente de correccion"
      And no debe solicitar reserva de inventario
      And debe publicar el motivo "Direccion incompleta"

    @ESC-INI01-RF02-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Validar datos obligatorios y reglas logisticas" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI01-RF02-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Validar datos obligatorios y reglas logisticas" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
