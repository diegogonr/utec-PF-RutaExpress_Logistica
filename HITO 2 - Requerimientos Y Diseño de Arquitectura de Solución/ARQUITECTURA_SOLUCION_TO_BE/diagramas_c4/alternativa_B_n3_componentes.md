# Alternativa B — C4 Nivel 3 Componentes

> Cuatro diagramas N3, paralelos a Alternativa A (orquestador/notificaciones · OMS · Inventario · móvil).  
> Imágenes: [`imagenes_alternativa_B/`](imagenes_alternativa_B/).

## Orquestador / notificaciones (~ PLT-03 en A)

![Orquestador](imagenes_alternativa_B/alternativa_B_c4_n3_orquestador_componentes.png)

Durable Functions (Saga Starter, Process Orchestrator, compensaciones, actividades WMS/ERP) + canal de notificaciones Service Bus (sin hub PLT-03 completo).

## Módulo OMS del núcleo modular (~ OMS en A)

![OMS](imagenes_alternativa_B/alternativa_B_c4_n3_oms_componentes.png)

Command/Query API, AuthZ, Create Order Handler, Order Lifecycle, Unit of Work, Notification Outbox; dispara Durable Functions y reserva in-proc al módulo Inventario.

## Módulo Inventario del núcleo modular (~ Inventario en A)

![Inventario](imagenes_alternativa_B/alternativa_B_c4_n3_inventario_componentes.png)

Reserve/Release/Availability, Inventory Aggregate, Compensation Hook, WMS ACL + Circuit Breaker; misma BD Azure SQL del núcleo.

## Backend móvil (~ móvil en A)

![Móvil](imagenes_alternativa_B/alternativa_B_c4_n3_mobile_componentes.png)

`mobile-api` + evidencias S3/KMS + DynamoDB outbox; en B la confirmación al núcleo es **API idempotente vía APIM** (no adaptador EventBridge → Event Hubs).
