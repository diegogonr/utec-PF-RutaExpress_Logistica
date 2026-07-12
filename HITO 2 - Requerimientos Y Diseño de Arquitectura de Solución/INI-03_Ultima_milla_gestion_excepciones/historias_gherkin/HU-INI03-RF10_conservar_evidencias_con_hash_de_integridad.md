# HU-INI03-RF10 - Conservar evidencias con hash de integridad

- Iniciativa: INI-03
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-10

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI03-RF10 | Logistica | responsable de liquidacion | que Almacenamiento Evidencias (S3) (APP-16) conserve evidencias con hash de integridad y referencia a orden/entrega | demostrar cumplimiento y resolver observaciones | RF-10 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI03-RF10 @RF-10
Feature: Evidencias con integridad verificable
  Rule: Toda evidencia debe verificarse contra hash y correlation ID

    @ESC-INI03-RF10-P01 @positivo
    Scenario: Guardar evidencia con hash valido
      Given que la app envia una foto de entrega con hash local
      When el backend almacena el objeto en S3
      Then debe calcular y comparar el hash
      And debe asociar evidencia, orden, entrega y correlation ID

    @ESC-INI03-RF10-N01 @negativo
    Scenario: Bloquear evidencia corrupta
      Given que la evidencia recibida no coincide con su hash
      When el backend valida integridad
      Then debe marcarla como corrupta
      And no debe usarla para liquidacion

    @ESC-INI03-RF10-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Conservar evidencias con hash de integridad" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI03-RF10-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Conservar evidencias con hash de integridad" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
