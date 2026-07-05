## Hito 2 Documentos Requerimientos Y Diseño de Arquitectura de Solución

Toma las 3 iniciativas, "INI-01: Gestión unificada de órdenes e inventario end-to-end", "INI-02: Integración API-First y Event-Driven", "INI-03: Modernización de última milla y gestión de excepciones" y elabore los Requerimientos Funcionales / No Funcionales y sus criterios de aceptación


1. los requerimientoes  deben tener el siguiente formato
Enunciar requerimientos
Historias de Usuario (Scrum)
Ejemplos:
Estructura:
Como[rol]Quiero[funcionalidad]Para[beneficio]
Sector
Requerimiento Funcional
Requerimiento No Funcional
Seguros
Comocliente
Quieroemitir una póliza vehicular en línea
Paraobtener cobertura inmediata
ComoclienteQuieroque la emisión de la póliza sea menor a 5 minutosParatener cobertura inmediata
Banca
Comocliente
Quierotransferir dinero a otro banco
Parapagar mis obligaciones
Comocliente
Quieroque mis transferencias estén protegidas con autenticación multifactor
Paraevitar fraudes


2. Los Criterios deben tener el siguiente formato
 Enunciar CriteriosAceptación
Gherkin(BDD -Behavior-DrivenDevelopment)
Definen cuándo el requerimiento está bien implementado
Gherkin(BDD-Behavior-DrivenDevelopment)
Estructura:
Given(Dado)When(Cuando)Then(Entonces)
EJEMPLOS: 
-Escenarios Positivos
Scenario: Emisión exitosa de póliza vehicular
Givenque el cliente ingresa datos personales válidos
Andingresa datos válidos del vehículo
Andselecciona datos válidos de la póliza
Andacepta los términos y condiciones
Andacepta la política de tratamiento de datos
Andel riesgo de la solicitud es aceptable
Whenconfirma la emisión de la póliza
Thenel sistema debe calcular la prima
Anddebe generar el número de póliza
And debe registrar la póliza con estado "Emitida“
Anddeberegistrar los documentos de cobro
And debe mostrar el mensaje "Póliza emitida correctamente"
Anddebe enviar la póliza al correo del cliente

-Escenarios Negativos
Scenario: Rechazo por datos obligatorios incompletos
Givenque el cliente ingresa información incompleta
Andfalta al menos un campo obligatorio del cliente o del vehículo o de la póliza
Whenconfirma la emisión de la póliza
Thenel sistema no debe emitir la póliza
And debe mostrar los campos obligatorios faltantes
And debe mostrar el mensaje "Complete los campos obligatorios para continuar"



3. En base a los requerimientos y criterios de aceptación elabore dos alternativas de solución TO BE y para cada una presente un Diagrama de Arquitectura de Solución en C4 Model hasta nivel 3 (Contexto, Contenedores, Componentes) con íconos de AWS, Azure o GCP aplicando Lineamientos de Arquitectura (Ejemplo: Integración, Seguridad, Observabilidad, etc.) y Patrones de Arquitectura. Indique todas las Decisiones de diseño (Architectural Decision Records (ADR))tomadas. Presente un cuadro comparativo de ambas alternativas y sus recomendaciones.

NOTAS ADICIONALES: No se usarán servicios de tercero como telemetry ni datadog, ni algun otro serviico de tercero, siempre proioprizar los servicios de alguna de las 3 nubes aws, gcp o azure. Además, los servicios usados no deben ser muy caros, deben ser de nivel intermedio. recuerda que tampoco debes dar opciones para que yo elija tu debes elegir en base a todo el HITO1