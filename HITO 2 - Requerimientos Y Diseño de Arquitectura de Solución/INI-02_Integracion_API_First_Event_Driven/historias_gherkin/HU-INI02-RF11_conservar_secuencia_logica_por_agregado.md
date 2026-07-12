# HU-INI02-RF11 - Conservar secuencia logica por agregado

- Iniciativa: INI-02
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-11

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI02-RF11 | Logistica | responsable de integridad | conservar secuencia logica por orden, ruta, paquete o liquidacion | evitar estados visibles inconsistentes | RF-11 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI02-RF11 @RF-11
Feature: Secuencia logica de eventos
  Rule: Eventos fuera de orden deben retenerse, reordenarse o marcarse para remediacion antes de afectar estados visibles

    @ESC-INI02-RF11-P01 @positivo
    Scenario: Procesar eventos en orden por paquete
      Given que llegan eventos de un paquete con secuencia 1, 2 y 3
      When el consumidor actualiza el estado
      Then debe aplicar los eventos en orden
      And debe actualizar el portal con estado consistente

    @ESC-INI02-RF11-N01 @negativo
    Scenario: Retener intento fallido posterior a entrega
      Given que el evento "Entregado" ya fue aplicado
      And llega un evento anterior "IntentoFallido"
      When la plataforma valida la secuencia
      Then no debe sobrescribir el estado visible como fallido
      And debe enviar el caso a remediacion o reordenamiento

    @ESC-INI02-RF11-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Conservar secuencia logica por agregado" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI02-RF11-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Conservar secuencia logica por agregado" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
