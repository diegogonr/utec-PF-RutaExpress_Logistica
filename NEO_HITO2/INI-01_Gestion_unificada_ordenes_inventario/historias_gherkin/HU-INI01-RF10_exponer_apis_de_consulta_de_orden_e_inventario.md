# HU-INI01-RF10 - Exponer APIs de consulta de orden e inventario

- Iniciativa: INI-01
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-10

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI01-RF10 | Logistica | consumidor autorizado de TMS, portal B2B o liquidacion | consultar estado de orden, reserva e inventario disponible mediante APIs versionadas | operar con informacion confiable | RF-10 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI01-RF10 @RF-10
Feature: APIs de consulta OMS e inventario
  Rule: Solo consumidores autorizados deben consultar contratos versionados de orden e inventario

    @ESC-INI01-RF10-P01 @positivo
    Scenario: Consultar estado de orden con autorizacion
      Given que TMS tiene credenciales validas y contrato vigente
      When consulta el estado de una orden por API
      Then debe recibir estado canonico, reserva, timestamp y correlation ID
      And la consulta debe quedar auditada

    @ESC-INI01-RF10-N01 @negativo
    Scenario: Rechazar consulta no autorizada
      Given que un consumidor no registrado invoca la API de inventario
      When Azure API Management valida la solicitud
      Then debe rechazarla con error de autorizacion
      And no debe exponer datos de orden ni inventario

    @ESC-INI01-RF10-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Exponer APIs de consulta de orden e inventario" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI01-RF10-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Exponer APIs de consulta de orden e inventario" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
