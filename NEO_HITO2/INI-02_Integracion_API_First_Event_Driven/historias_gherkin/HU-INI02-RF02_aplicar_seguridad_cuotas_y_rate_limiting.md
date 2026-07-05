# HU-INI02-RF02 - Aplicar seguridad, cuotas y rate limiting

- Iniciativa: INI-02
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-02

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI02-RF02 | Logistica | administrador de APIs | que Azure API Management (APP-01) aplique autenticacion, autorizacion, cuotas y rate limiting | proteger servicios backend y contratos por cliente | RF-02 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI02-RF02 @RF-02
Feature: Seguridad y control de trafico API
  Rule: Una solicitud sin credenciales o fuera de cuota debe rechazarse con codigo y mensaje estandar

    @ESC-INI02-RF02-P01 @positivo
    Scenario: Permitir solicitud autorizada dentro de cuota
      Given que un cliente B2B tiene credenciales validas
      And no supera su cuota por minuto
      When invoca una API versionada
      Then Azure API Management debe enrutar la solicitud al backend
      And debe registrar la metrica de consumo

    @ESC-INI02-RF02-N01 @negativo
    Scenario: Rechazar solicitud fuera de cuota
      Given que un cliente supera la cuota configurada
      When invoca nuevamente la API
      Then la plataforma debe responder con error 429
      And no debe enviar trafico al servicio backend

    @ESC-INI02-RF02-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Aplicar seguridad, cuotas y rate limiting" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI02-RF02-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Aplicar seguridad, cuotas y rate limiting" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
