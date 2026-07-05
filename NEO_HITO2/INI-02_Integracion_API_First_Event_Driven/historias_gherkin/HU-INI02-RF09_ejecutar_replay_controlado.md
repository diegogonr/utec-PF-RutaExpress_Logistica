# HU-INI02-RF09 - Ejecutar replay controlado

- Iniciativa: INI-02
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-09

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI02-RF09 | Logistica | operador autorizado | reprocesar eventos por rango, tipo y correlation ID sin duplicar efectos de negocio | recuperar consumidores o reconstruir historial | RF-09 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI02-RF09 @RF-09
Feature: Replay controlado de eventos
  Rule: El replay debe respetar autorizacion, filtros e idempotencia de consumidores

    @ESC-INI02-RF09-P01 @positivo
    Scenario: Reprocesar eventos por correlation ID
      Given que un consumidor perdio una ventana de procesamiento
      And existe autorizacion para replay
      When el operador solicita replay por correlation ID
      Then la plataforma debe reenviar los eventos seleccionados
      And los consumidores deben aplicar idempotencia

    @ESC-INI02-RF09-N01 @negativo
    Scenario: Rechazar replay sin aprobacion
      Given que un usuario intenta ejecutar replay sin permiso
      When la plataforma valida el rol
      Then debe rechazar la solicitud
      And no debe reinyectar eventos al bus

    @ESC-INI02-RF09-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Ejecutar replay controlado" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI02-RF09-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Ejecutar replay controlado" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
