## **Empresa: RutaExpress Fulfillment & Transporte (Ficticia)** 

## **Sector Económico** 

Logística y Transporte 

## **Resumen ejecutivo** 

RutaExpress Fulfillment & Transporte es un operador logístico que atiende comercio electrónico, retail, farmacéuticas y consumo masivo. Administra 14 centros de distribución, 2,700 vehículos propios y tercerizados, 9,500 colaboradores, 68,000 entregas diarias promedio y picos de 180,000 durante campañas. Sus servicios incluyen almacenamiento, preparación de pedidos, última milla, logística inversa, entregas refrigeradas y visibilidad para clientes empresariales. 

La empresa compite en un sector marcado por promesas de entrega cada vez más cortas, presión de costos, clientes finales impacientes y grandes marketplaces con capacidades logísticas propias. RutaExpress creció rápido, integrando clientes por APIs, portales y archivos, pero su arquitectura quedó fragmentada: WMS (Warehouse Management System) on premises, TMS (Transportation Management System) en Azure, app de conductores en AWS, analítica de rutas en GCP, portales de clientes SaaS, bases de datos por almacén y múltiples integraciones punto a punto. 

La organización busca en tres años convertirse en un operador logístico digital, predictivo y escalable. Necesita mejorar cumplimiento de promesa, reducir entregas fallidas, optimizar rutas, integrar inventario y ofrecer trazabilidad confiable. Los problemas actuales son severos: pedidos duplicados, inventario desalineado, congestión en centros de distribución, asignación manual de rutas, baja visibilidad de última milla, costos crecientes de combustible, reclamos masivos y baja resiliencia tecnológica en campañas. 

El caso describe la cadena de valor desde la recepción de órdenes hasta la devolución y liquidación. En cada fase se detallan roles, aplicaciones, datos, infraestructura y problemas con volumetría. La narrativa ofrece un escenario integral para analizar arquitectura empresarial, solución multinube, APIs, eventos, dominios, resiliencia, observabilidad, seguridad, IaC y optimización de costos en logística moderna. 

## **Contexto de la Organización** 

RutaExpress nació como una empresa de transporte urbano para tiendas por departamento. Su ventaja era conocer la ciudad, tener conductores confiables y entregar en zonas donde otros operadores fallaban. Con el auge del comercio electrónico, la empresa se transformó en un operador logístico integral. Abrió centros de distribución, integró marketplaces, adquirió una flota refrigerada y ofreció servicios de fulfillment para marcas que no querían construir su propia operación. 

El modelo de negocio combina contratos por volumen, tarifas por almacenamiento, picking, packing, transporte, entrega, devolución, servicios premium y penalidades o bonificaciones por cumplimiento de SLA. Sus clientes son retailers, marketplaces, farmacias, supermercados, fabricantes y empresas de venta directa. Su propuesta de valor se basa en cobertura, velocidad, trazabilidad, flexibilidad operativa y capacidad de absorber picos. 

La empresa procesa diariamente 68,000 entregas promedio, 210,000 movimientos de inventario, 44,000 eventos de tracking y 18,000 contactos de atención. En campañas como Cyber Days, Navidad o vuelta a clases, el volumen se triplica. La operación depende de almacenes, transportistas, conductores, planificadores, atención al cliente, tecnología, seguridad, clientes empresariales y destinatarios finales. 

El sector logístico se volvió una carrera de promesas. Entrega al día siguiente dejó de ser diferencial; ahora se exige entrega el mismo día, ventanas horarias precisas, trazabilidad en vivo, devoluciones simples y atención inmediata. Los marketplaces más grandes construyen redes propias y presionan a operadores externos con tarifas bajas y penalidades. El costo de combustible, seguridad y mano de obra sube, mientras los clientes esperan pagar menos. 

RutaExpress tiene sistemas fuertes en partes de la operación, pero no una arquitectura integrada. El WMS principal corre on premises en el centro de distribución central. El TMS está en Azure. La app de conductores corre en AWS y usa DynamoDB. La optimización de rutas se ejecuta en GCP con cargas batch. El portal de clientes es SaaS. Los clientes grandes envían órdenes por APIs, pero clientes medianos aún envían archivos CSV o Excel. Cada centro de distribución conserva bases locales para contingencia. 

Los problemas se manifiestan en los momentos de mayor presión. En el último Cyber Days, el WMS se degradó durante seis horas. Se acumularon 240,000 pedidos en cola. El TMS recibió órdenes incompletas, la app de conductores mostró rutas con paquetes faltantes y atención al cliente no pudo responder con certeza. Se entregó tarde el 19% de pedidos de la campaña y se pagaron penalidades por USD 1.1 millones. 

La aspiración del directorio es que RutaExpress deje de operar como una suma de centros y sistemas, y actúe como una plataforma logística digital. Para lograrlo debe integrar pedidos, inventario, almacén, transporte, tracking, devoluciones, facturación y analítica bajo una arquitectura resiliente, observable y segura. 

## **Objetivos Estratégicos** 

1. Incrementar el cumplimiento de promesa de entrega de 82% a 94% en tres años, considerando fecha, ventana horaria, producto correcto y evidencia de entrega. 

2. Reducir entregas fallidas de 12.5% a 7% mediante mejor validación de dirección, comunicación con destinatario, optimización de rutas y gestión de excepciones. 

3. Disminuir el tiempo de ciclo desde orden recibida hasta despacho de 9.5 horas a 4 horas para pedidos fulfillment estándar. 

4. Alcanzar visibilidad de tracking confiable para el 98% de pedidos, desde recepción hasta entrega, devolución o incidencia. 

5. Reducir costos de transporte por entrega en 15% mediante consolidación, rutas dinámicas, mejor utilización de flota y control de combustible. 

6. Lograr disponibilidad de 99.9% para sistemas críticos en campañas, incluyendo recepción de órdenes, WMS, TMS, app de conductores y tracking. 

7. Fortalecer la seguridad de integraciones con clientes, datos personales de destinatarios, evidencia de entrega y operación móvil de conductores. 

## **Cadena de Valor** 

## **Fase 1: Recepción de órdenes** 

La cadena comienza cuando un cliente empresarial envía órdenes de venta a RutaExpress. Un marketplace transmite miles de pedidos por API; una cadena de farmacias envía órdenes cada quince minutos; una marca mediana carga un Excel en el portal. Para el cliente, la promesa ya fue hecha al comprador final. Para RutaExpress, cada orden es un compromiso que debe convertirse en inventario reservado, picking, transporte, entrega y evidencia. 

Las APIs de clientes se exponen en Azure API Management. El portal SaaS permite carga manual. Algunos archivos llegan a un bucket S3 en AWS por integración histórica. El sistema de orquestación de pedidos corre en Azure Kubernetes Service. El WMS on premises recibe las órdenes para preparación. Las bases de datos incluyen pedidos, clientes, destinatarios, SKUs, direcciones, SLA y ventanas. 

Participan cliente empresarial, integración TI, mesa B2B, planeamiento, almacén y atención. Entidades de datos: orden, línea de pedido, SKU, destinatario, dirección, promesa, SLA, cliente, canal y prioridad. El problema grave es que no todas las órdenes se validan igual. Direcciones incompletas, SKUs inexistentes o pedidos duplicados entran al flujo y explotan más adelante. 

En un día regular se reciben 68,000 órdenes; en campaña, 180,000. El 6% presenta algún defecto de datos. Aunque parece manejable, significa miles de excepciones diarias. En una campaña, un cliente envió dos veces el mismo lote de 32,000 pedidos por reintento de API. La deduplicación falló porque el identificador externo cambió. Se separó inventario innecesariamente, se generaron rutas fantasma y se consumieron horas de operación corrigiendo el problema. 

## **Fase 2: Preparación de pedidos** 

Una vez aceptada la orden, el almacén debe preparar el pedido. En los centros de distribución, montacargas, bandas transportadoras, handhelds y operarios se mueven con ritmo intenso. El WMS indica ubicación, cantidad, lote, vencimiento y secuencia de picking. Para productos farmacéuticos se controla temperatura y cadena de custodia. 

El WMS principal corre on premises sobre SQL Server. Algunos almacenes pequeños usan una versión local con sincronización cada hora. Los handhelds se conectan por Wi-Fi interno. El inventario maestro se replica hacia el portal de clientes y hacia el TMS. Los sensores de temperatura de cámaras refrigeradas envían datos a AWS IoT Core. El ERP financiero conserva inventario valorizado, pero no siempre actualizado en tiempo real. 

Roles: jefe de almacén, picker, verificador, control de calidad, supervisor de frío, inventario, seguridad y cliente. Entidades de datos: SKU, ubicación, lote, vencimiento, pedido, ola de picking, caja, contenedor, temperatura, inventario y excepción. La dificultad es que el inventario físico se mueve más rápido que las sincronizaciones. 

RutaExpress realiza 210,000 movimientos de inventario diarios. El 2.8% genera ajuste por diferencia, daño, vencimiento, ubicación incorrecta o conteo tardío. En productos de alta rotación, una diferencia pequeña provoca cancelaciones. Durante un pico, el WMS local de un almacén perdió conectividad con el centro durante 74 minutos. Se siguió operando con contingencia, pero al sincronizar aparecieron 4,900 movimientos en conflicto. Se retrasaron 18,000 pedidos. 

## **Fase 3: Despacho de pedidos** 

El pedido preparado pasa a consolidación y despacho. Las cajas se agrupan por zona, ruta, transportista, ventana horaria y tipo de servicio. Un pedido de farmacia refrigerada no puede viajar 

con cualquier carga; un producto de alto valor requiere validación de seguridad; una entrega express tiene prioridad. La operación parece un rompecabezas que cambia cada hora. 

El TMS alojado en Azure recibe pedidos liberados por el WMS. La optimización de rutas se ejecuta en GCP con datos de tráfico, capacidad, restricciones y ubicación. Las rutas resultantes se envían a la app de conductores en AWS. Los transportistas tercerizados acceden por portal. Los manifiestos se imprimen localmente en cada centro. 

Participan planner de transporte, supervisor de despacho, transportista, conductor, seguridad, cliente y atención. Entidades de datos: ruta, manifiesto, vehículo, conductor, capacidad, zona, paquete, ventana, prioridad y restricción. El problema es que la asignación aún requiere intervención manual porque los datos de volumen, disponibilidad de flota y restricciones no siempre son confiables. 

En un día normal salen 2,700 vehículos. En campaña se suman 1,400 unidades tercerizadas. El 17% de rutas se modifica manualmente después de generarse. Cada modificación puede afectar promesa, costo y tracking. En una jornada de lluvias, el optimizador recibió datos de tráfico con retraso y generó rutas inviables. Los planners corrigieron a mano 380 rutas. Aun así, 24,000 entregas llegaron fuera de ventana. 

## **Fase 4: Entrega del pedido** 

La última milla es donde RutaExpress se encuentra con el destinatario. El conductor recibe ruta, paquetes, evidencias requeridas y contacto del cliente final. Debe navegar tráfico, edificios sin recepción, direcciones ambiguas, zonas inseguras, pagos contra entrega y cambios de última hora. Una entrega exitosa depende de tecnología, criterio y contexto urbano. 

La app de conductores corre en AWS, usa DynamoDB para eventos y sincronización offline, y envía ubicación cada dos minutos. Los eventos de tracking se publican hacia el portal SaaS de clientes y hacia el centro de atención. El TMS actualiza estados en Azure. Las evidencias de entrega, fotos y firmas se almacenan en S3. Los pagos contra entrega se integran con una pasarela SaaS. 

Roles: conductor, destinatario, supervisor de ruta, atención al cliente, seguridad y cliente empresarial. Entidades de datos: paquete, evento, ubicación, evidencia, firma, foto, intento, motivo de fallo, pago y contacto. El problema es que la operación móvil enfrenta conectividad variable, errores humanos y excepciones no estandarizadas. 

Se generan 44,000 eventos de tracking diarios en promedio, pero en campañas superan 130,000. El 8% de eventos llega con retraso mayor a 20 minutos. Los clientes llaman preguntando por paquetes que ya fueron entregados o que aún figuran en ruta. En zonas con mala señal, la app guarda eventos offline, pero si el conductor reinstala la aplicación o cambia de equipo se pierden evidencias. En un 

caso, 1,200 entregas aparecieron sin firma digital y el cliente retuvo el pago del servicio hasta recibir conciliación manual. 

## **Fase 5: Gestión de excepciones** 

Cuando una entrega falla, empieza la gestión de excepciones. El destinatario no estaba, la dirección era incorrecta, el paquete se dañó, el edificio no permitió ingreso, faltó documentación o hubo riesgo de seguridad. Cada excepción requiere decisión: reintentar, devolver, llamar, cambiar dirección, cobrar penalidad o escalar al cliente. 

Las excepciones se registran en la app de conductores, se visualizan en TMS y se notifican al portal de clientes. Atención usa un CRM SaaS. Los reintentos se planifican en el TMS. Las devoluciones vuelven al WMS. La información sobre motivos no está normalizada; cada conductor puede seleccionar categorías distintas o escribir texto libre. 

Participan conductor, destinatario, atención, cliente empresarial, planner, almacén y finanzas. Entidades de datos: intento, excepción, motivo, reintento, devolución, autorización, costo y reclamo. La falta de datos consistentes impide aprender de las fallas. 

La tasa de entrega fallida es 12.5%. En volumen promedio equivale a 8,500 paquetes diarios. Cada reintento cuesta entre USD 1.20 y USD 2.80 según zona. El 34% de fallas se relaciona con dirección o ausencia, problemas que podrían mitigarse antes de salir a ruta. Sin embargo, validación de dirección, comunicación previa y ajuste de ventanas no están integrados. La empresa gasta millones moviendo paquetes que no estaban listos para ser entregados. 

## **Fase 6: Liquidación y devoluciones** 

El ciclo cierra con liquidación, reportes y devoluciones. RutaExpress debe informar al cliente qué se entregó, qué falló, qué se devolvió, qué penalidades aplican y cuánto se factura. Los clientes grandes exigen reportes diarios y APIs de trazabilidad. Finanzas necesita facturar con evidencia. Operaciones necesita aprender de errores. 

La facturación se realiza en el ERP on premises. Los eventos de entrega están en AWS. El TMS en Azure conserva rutas y costos. El WMS contiene devoluciones. El portal SaaS muestra reportes para clientes. Analítica en GCP consolida información semanalmente. Las notas de crédito por penalidades se calculan con hojas Excel cuando el contrato tiene reglas especiales. 

Roles: finanzas, operaciones, cliente empresarial, atención, legal, analítica y almacén. Entidades de datos: entrega, evidencia, SLA, penalidad, factura, devolución, reclamo, costo, liquidación y reporte. El problema es que el cierre económico depende de conciliar datos entre nubes y sistemas locales. 

Mensualmente se facturan más de 2 millones de servicios logísticos. El 7% queda observado por clientes debido a diferencias de estado, evidencia, tarifa o penalidad. Una cadena de retail retuvo USD 2.4 millones porque sus reportes internos indicaban menos entregas exitosas que RutaExpress. La conciliación tomó 23 días e involucró archivos de AWS, reportes del TMS, capturas del portal y registros del WMS. La operación había cumplido mejor de lo que el sistema podía demostrar. 

