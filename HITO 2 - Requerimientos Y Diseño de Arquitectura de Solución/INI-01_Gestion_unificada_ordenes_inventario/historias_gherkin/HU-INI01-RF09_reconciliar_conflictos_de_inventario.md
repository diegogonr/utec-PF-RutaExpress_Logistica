# HU-INI01-RF09 - Reconciliar conflictos de inventario

- Iniciativa: INI-01
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-09

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI01-RF09 | Logistica | jefe de inventario | reconciliar conflictos entre WMS Cloud y almacenes locales | evitar liberar pedidos con inventario dudoso y reducir retrasos operativos | RF-09 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI01-RF09 @RF-09
Feature: Conciliacion de inventario
  Rule: Todo conflicto debe clasificarse, priorizarse y resolverse automaticamente o derivarse con trazabilidad

    @ESC-INI01-RF09-P01 @positivo
    Scenario: Resolver conflicto por regla automatica
      Given que WMS Cloud y un almacen local reportan diferencias menores para el mismo SKU y lote
      And existe una regla de prioridad de fuente
      When el proceso de conciliacion compara los movimientos
      Then debe aplicar la regla automatica
      And debe publicar "InventarioConciliado"

    @ESC-INI01-RF09-N01 @negativo
    Scenario: Derivar conflicto severo a operador
      Given que un almacen reconectado envia movimientos que afectan pedidos reservados
      When el proceso detecta un conflicto de alto impacto
      Then debe bloquear las posiciones dudosas
      And debe crear una tarea de conciliacion manual
      And debe evitar liberar pedidos afectados

    @ESC-INI01-RF09-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Reconciliar conflictos de inventario" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI01-RF09-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Reconciliar conflictos de inventario" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
