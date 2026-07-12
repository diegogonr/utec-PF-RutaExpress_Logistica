# HU-INI03-RF06 - Aplicar taxonomia unica de excepciones

- Iniciativa: INI-03
- Fuente: criterios_aceptacion_gherkin.md
- Requerimiento funcional: RF-06

## Historia de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
|---|---|---|---|---|---|
| HU-INI03-RF06 | Logistica | responsable de atencion y transporte | una taxonomia unica de excepciones | que app, TMS, CRM y portal usen los mismos codigos y descripciones | RF-06 |

## Criterios de aceptacion Gherkin

```gherkin
@HU-INI03-RF06 @RF-06
Feature: Taxonomia canonica de excepciones
  Rule: App, TMS, CRM y portal deben usar los mismos codigos oficiales

    @ESC-INI03-RF06-P01 @positivo
    Scenario: Registrar excepcion con codigo canonico
      Given que el conductor selecciona "Destinatario ausente"
      When la app registra la excepcion
      Then debe guardar el codigo canonico correspondiente
      And TMS, CRM y portal deben recibir el mismo codigo

    @ESC-INI03-RF06-N01 @negativo
    Scenario: Rechazar codigo no vigente
      Given que la app intenta enviar un codigo de excepcion obsoleto
      When el backend valida la taxonomia
      Then debe rechazar o remediar el evento
      And no debe mostrar un motivo inconsistente al cliente

    @ESC-INI03-RF06-P02 @positivo
    Scenario: Registrar trazabilidad y resultado operativo de la funcionalidad
      Given que la funcionalidad "Aplicar taxonomia unica de excepciones" se ejecuta correctamente
      And la operacion cuenta con correlation ID y datos minimos de auditoria
      When el sistema completa el procesamiento
      Then debe registrar resultado, timestamp, actor o sistema origen
      And debe dejar la informacion disponible para observabilidad y soporte

    @ESC-INI03-RF06-N02 @negativo
    Scenario: Retener o rechazar solicitud sin trazabilidad obligatoria
      Given que la funcionalidad "Aplicar taxonomia unica de excepciones" recibe una solicitud sin correlation ID obligatorio
      When el sistema valida los metadatos de la operacion
      Then debe rechazarla o enviarla a remediacion segun criticidad
      And no debe publicar estados inconsistentes a otros sistemas
```
