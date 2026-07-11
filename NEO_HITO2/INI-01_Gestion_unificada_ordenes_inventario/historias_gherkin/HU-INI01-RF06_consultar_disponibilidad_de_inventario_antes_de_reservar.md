# HU-INI01-RF06 - Consultar disponibilidad de inventario antes de reservar

- Iniciativa: INI-01
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-06

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI01-RF06 | Logistica | planificador de almacen | que el OMS consulte disponibilidad por SKU, almacen, ubicacion, lote y estado antes de confirmar reserva | asegurar que solo se comprometa stock elegible | RF-06 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI01-RF06 @RF-06
Feature: Consulta de disponibilidad de inventario
  Rule: La reserva solo debe confirmarse si existe stock disponible y elegible

    @ESC-INI01-RF06-P01 @positivo
    Scenario: Confirmar disponibilidad elegible
      Given que una orden validada solicita un SKU con lote apto
      And WMS Cloud reporta cantidad disponible en estado "Disponible"
      When el OMS consulta disponibilidad
      Then debe recibir posiciones elegibles por almacen, ubicacion, lote y estado
      And debe permitir la solicitud de reserva

    @ESC-INI01-RF06-N01 @negativo
    Scenario: Bloquear reserva con inventario no elegible
      Given que existe stock del SKU en estado "Dañado" o "Bloqueado"
      When el OMS consulta disponibilidad
      Then no debe considerar ese stock como elegible
      And debe marcar la orden como "Sin stock" si no hay otra posicion disponible

    @ESC-INI01-RF06-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Consultar disponibilidad de inventario antes de reservar" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI01-RF06-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Consultar disponibilidad de inventario antes de reservar" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
