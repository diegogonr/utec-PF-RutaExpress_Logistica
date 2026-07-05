```gherkin
Feature: Emisión de póliza vehicular en línea
  Como cliente
  Quiero emitir una póliza vehicular en línea
  Para obtener cobertura inmediata

  # Escenarios positivos

  Scenario: Emisión exitosa de póliza vehicular
    Given que el cliente ingresa datos personales válidos
    And ingresa datos válidos del vehículo
    And selecciona datos válidos de la póliza
    And acepta los términos y condiciones
    And acepta la política de tratamiento de datos
    And el riesgo de la solicitud es aceptable
    When confirma la emisión de la póliza
    Then el sistema debe calcular la prima
    And debe generar el número de póliza
    And debe registrar la póliza con estado "Emitida"
    And debe registrar los documentos de cobro
    And debe mostrar el mensaje "Póliza emitida correctamente"
    And debe enviar la póliza al correo del cliente

  # Escenarios negativos

  Scenario: Rechazo por datos obligatorios incompletos
    Given que el cliente ingresa información incompleta
    And falta al menos un campo obligatorio del cliente o del vehículo o de la póliza
    When confirma la emisión de la póliza
    Then el sistema no debe emitir la póliza
    And debe mostrar los campos obligatorios faltantes
    And debe mostrar el mensaje "Complete los campos obligatorios para continuar"

  Scenario: Derivación por riesgo alto
    Given que el cliente ingresa datos válidos
    And la evaluación de riesgo clasifica la solicitud como riesgo alto
    When confirma la emisión de la póliza
    Then el sistema no debe emitir la póliza automáticamente
    And debe registrar la solicitud en estado "Pendiente de evaluación"
    And debe mostrar el mensaje "Tu solicitud será revisada por un analista"

  Scenario: Rechazo por póliza vigente existente
    Given que el cliente ingresa una placa con póliza vigente
    When confirma la emisión de una nueva póliza
    Then el sistema no debe emitir la póliza
    And debe mostrar el mensaje "Ya existe una póliza vigente para este vehículo"

  Scenario: Error técnico durante la emisión
    Given que la solicitud fue validada correctamente
    And la emisión fue autorizada
    When ocurre un error técnico al registrar la póliza
    Then el sistema no debe marcar la póliza como emitida
    And debe mostrar el mensaje "No fue posible completar la emisión en este momento"
    And debe registrar el incidente técnico
```
    