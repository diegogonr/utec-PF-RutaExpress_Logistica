## **ANEXO: RIESGOS TECNOLÓGICOS** 

## **Caso asociado:** RutaExpress Fulfillment & Transporte 

**propósito del anexo:** Este anexo identifica los 3 principales riesgos tecnológicos del caso. 

## **Riesgos tecnológicos priorizados** 

|||||
|---|---|---|---|
|**Prioridad**|**Categoría**|**Riesgo tecnológico**|**Aplicaciones e infraestructura**<br>**involucradas**|
|1|Disponibilidad|Degradación de sistemas críticos<br>en campañas, provocando colas<br>de pedidos, rutas incompletas,<br>tracking incierto y penalidades.|WMS SQL Server on premises, TMS<br>Azure, AKS de orquestación, app<br>AWS/DynamoDB, GCP optimizador,<br>portal SaaS, redes de almacenes.|
|2|Integridad|Pedidos, inventario, rutas, eventos<br>y evidencias inconsistentes entre<br>WMS, TMS, app móvil, portales y<br>ERP.|Azure API Management, S3, AKS, WMS,<br>TMS, DynamoDB, ERP on premises,<br>portal SaaS, GCP analitica.|
|3|Operación|Errores humanos y mala<br>confguración en excepciones,<br>datos de dirección, categorías de<br>fallo y operación ofline móvil.|App de conductores AWS, CRM SaaS,<br>TMS, WMS, validadores de dirección,<br>portales de clientes, integraciones con<br>clientes.|



## **1. Riesgo de Disponibilidad: sistemas logísticos no resilientes a picos de campaña** 

## **Descripción del riesgo** 

RutaExpress triplica volumen en campañas. La recepción de órdenes, WMS, TMS, optimizador de rutas, app de conductores y tracking deben operar coordinados. Una degradación de WMS o integraciones genera acumulación de pedidos, rutas incompletas y reclamos masivos. 

## **Problemática técnica crítica** 

El orquestador de pedidos en AKS recibe ordenes desde APIs en Azure API Management, portal SaaS y buckets S3 históricos. El WMS on premises confirma reserva y liberación de picking. Durante Cyber Days, el WMS se degrada por bloqueo de tablas de inventario y lentitud en consultas de 

ubicación. AKS sigue recibiendo ordenes, pero la cola hacia WMS crece sin control porque no hay backpressure por cliente ni prioridad por SLA. 

El TMS en Azure recibe pedidos liberados incompletos y solicita rutas al optimizador en GCP. Algunas rutas se generan sin todos los paquetes porque la confirmación de picking llega tarde. La app de conductores en AWS sincroniza manifiestos parciales. Cuando el WMS se recupera, aparecen pedidos listos que ya no calzan con rutas cerradas. Atención al cliente ve estados contradictorios en el portal. 

## **Evidencias AS IS a relevar** 

   - Arquitectura de recepción, orquestación, WMS, TMS, optimizador, app móvil y tracking. 

   - Límites de capacidad por componente, colas, timeouts, reintentos y políticas de prioridad. 

   - Comportamiento ante degradación de WMS y desconexión de almacenes. 

   - RTO/RPO por proceso critico en campaña. 

   - Monitoreo de flujo end to end: orden recibida, inventario reservado, picking, despacho, ruta y entrega. 

**2. Riesgo de Integridad: datos logísticos inconsistentes y conciliación costosa** 

## **Descripción del riesgo** 

El negocio se cobra y se defiende con evidencia: orden, inventario, ruta, evento, firma, foto, SLA, penalidad y factura. Si esos datos difieren entre WMS, TMS, app, portal y ERP, RutaExpress puede haber cumplido la operación, pero no demostrarlo, o facturar incorrectamente. 

## **Problemática técnica crítica** 

Un cliente envía 32,000 pedidos por API. Por reintento, cambia el identificador externo y falla la de duplicación. El orquestador crea ordenes duplicadas, el WMS reserva inventario dos veces y el TMS genera rutas fantasma. La app de conductores recibe algunos manifiestos, pero el portal SaaS muestra estados a partir de eventos de tracking y no de la reserva real. 

En entrega, las evidencias se guardan en S3 y los eventos en DynamoDB. El TMS actualiza estado en Azure y el ERP factura desde un reporte mensual. Si un conductor opera offline y luego sincroniza eventos fuera de orden, el portal puede mostrar intento fallido después de entrega exitosa. El cliente observa la liquidación porque su sistema recibió otro estado. 

## **Evidencias AS IS a relevar** 

   - Claves únicas y reglas de duplicación por cliente, canal y orden. 

   - Modelo canónico de estados: recibido, validado, reservado, pickeado, despachado, en ruta, entregado, fallido, devuelto y liquidado. 

   - Flujos de evidencias: fotos, firmas, geolocalización, pagos contra entrega y custodia. 

   - Conciliaciones mensuales entre WMS, TMS, app, portal y ERP. 

   - Casos de mensajes fuera de orden, duplicados o perdidos. 

**3. Riesgo de Operación: errores humanos y datos de excepción poco normalizados** 

## **Descripción del riesgo** 

La última milla depende de conductores, destinatarios, planners y atención. Direcciones incompletas, excepciones mal categorizadas, evidencias perdidas y cambios manuales de ruta elevan entregas fallidas y costos. El riesgo tecnológico se manifiesta como operación difícil de controlar. 

## **Problemática técnica crítica** 

La app de conductores permite seleccionar motivos de fallo y escribir texto libre. Algunos conductores usan "destinatario ausente", otros "no contesta", otros "dirección mala" para un mismo problema. El TMS recibe categorías distintas y el CRM SaaS abre reclamos con otra taxonomía. El algoritmo de rutas en GCP no aprende correctamente porque los motivos históricos no son comparables. 

En zonas con mala señal, la app guarda eventos offline. Si el conductor reinstala la app o cambia de equipo antes de sincronizar, se pierden firmas y fotos. En entregas de alto valor o farmacéuticas, esa pérdida bloquea liquidación y puede abrir reclamos de custodia. además, planners modifican rutas manualmente 

sin registrar causa estructurada, por lo que no se sabe si el problema fue clima, capacidad, tráfico, restricción de cliente o mala planificación. 

## **Evidencias AS IS a relevar** 

- Taxonomía actual de excepciones en app, TMS, CRM y portal de clientes. 

- Controles de obligatoriedad para firma, foto, geolocalización, hora, motivo y comentarios. 

- Manejo offline de la app: cifrado local, reintentos, retención y recuperación ante reinstalación. 

- Reglas de modificación manual de rutas y trazabilidad de aprobaciones. 

- Análisis de causas de entrega fallida por dirección, ausencia, seguridad, daño, clima y cliente. 

