# HU-INI02-RF10 - Exponer tableros de salud

- Iniciativa: INI-02
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-10

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI02-RF10 | Logistica | equipo de operaciones | tableros de salud de APIs, colas y eventos | monitorear latencia, errores, pendientes, DLQ y throughput por dominio | RF-10 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI02-RF10 @RF-10
Feature: Tableros de salud de integracion
  Rule: Operacion debe visualizar salud tecnica y de negocio por dominio

    @ESC-INI02-RF10-P01 @positivo
    Scenario: Visualizar backlog y DLQ por dominio
      Given que existen eventos pendientes y mensajes en DLQ
      When el operador abre el tablero de integracion
      Then debe ver latencia, errores, pendientes, DLQ y throughput
      And debe filtrar por dominio y consumidor

    @ESC-INI02-RF10-N01 @negativo
    Scenario: Alertar falta de telemetria
      Given que un consumidor deja de emitir metricas
      When el tablero detecta ausencia de telemetria
      Then debe mostrar estado desconocido o degradado
      And debe generar una alerta operativa

    @ESC-INI02-RF10-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Exponer tableros de salud" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI02-RF10-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Exponer tableros de salud" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
