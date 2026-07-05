# HU-INI02-RF01 - Registrar y publicar contratos API/eventos

- Iniciativa: INI-02
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-01

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI02-RF01 | Logistica | arquitecto de integracion | registrar y publicar contratos de APIs para orden, inventario, ruta, tracking, excepcion y liquidacion | gobernar consumidores, versiones y esquemas | RF-01 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI02-RF01 @RF-01
Feature: Gobierno de contratos API y eventos
  Rule: Todo contrato debe tener version, responsable, ambiente, esquema, seguridad y consumidores autorizados

    @ESC-INI02-RF01-P01 @positivo
    Scenario: Publicar contrato valido
      Given que el responsable registra un contrato con esquema, version y consumidores
      When la plataforma valida la definicion
      Then debe publicar el contrato como "Activo"
      And debe registrar responsable, ambiente y politica de seguridad

    @ESC-INI02-RF01-N01 @negativo
    Scenario: Rechazar contrato sin version
      Given que se intenta registrar un contrato sin version
      When la plataforma valida los metadatos
      Then debe rechazar el contrato
      And debe indicar que la version es obligatoria

    @ESC-INI02-RF01-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Registrar y publicar contratos API/eventos" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI02-RF01-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Registrar y publicar contratos API/eventos" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
