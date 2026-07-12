# HU-INI03-RF05 - Reintentar envios fallidos

- Iniciativa: INI-03
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-05

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI03-RF05 | Logistica | conductor | que la app reintente automaticamente envios fallidos | no recapturar evidencias ni perder informacion por errores temporales | RF-05 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI03-RF05 @RF-05
Feature: Reintentos automaticos de sincronizacion movil
  Rule: Un error temporal no debe obligar al conductor a recapturar evidencia

    @ESC-INI03-RF05-P01 @positivo
    Scenario: Reintentar envio tras error temporal
      Given que un lote falla por timeout del backend
      When la app aplica la politica de reintento
      Then debe conservar los datos locales
      And debe reenviar el lote con la misma idempotency key

    @ESC-INI03-RF05-N01 @negativo
    Scenario: Enviar a remediacion tras reintentos agotados
      Given que un evento falla repetidamente por error no recuperable
      When se agotan los reintentos configurados
      Then debe quedar pendiente de remediacion
      And operacion debe poder verlo en el tablero

    @ESC-INI03-RF05-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Reintentar envios fallidos" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI03-RF05-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Reintentar envios fallidos" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
