# Alternativa A - C4 Nivel 3 Componentes

## Proposito

Diagrama de componentes C4 para la Alternativa A. Este nivel hace zoom sobre un unico contenedor: **Bus de Eventos Central (PLT-03)** en Azure.

> Regla aplicada: C4 Component debe descomponer un solo contenedor. OMS centralizado / Orquestador de Pedidos (APP-02), Inventario, Backend Movil, TMS (Transportation Management) (APP-11), Portal/CRM y GCP aparecen como contenedores o sistemas de soporte, no como componentes internos.

```mermaid
graph TB
    subgraph SoporteEntrada["Contenedores productores"]
        OMS centralizado / Orquestador de Pedidos (APP-02)["OMS centralizado<br/>APP-02 sobre AKS"]
        INV["Servicio de Inventario y Reservas<br/>AKS"]
        MOBILE["Backend movil<br/>AWS ECS/Lambda"]
        LEGADO["Adaptadores transicionales<br/>CSV / Excel / S3"]
    end

    subgraph PLT03["Contenedor en foco: Bus de Eventos Central (PLT-03)<br/>Azure Event Hubs + Azure Service Bus"]
        API_EVENTS["Event Ingestion API<br/>recepcion de eventos canonicos"]
        SCHEMA["Schema Validator<br/>contratos AsyncAPI y versionado"]
        ROUTER["Event Router<br/>topicos, particiones y prioridad"]
        ORDERING["Ordering Guard<br/>secuencia por agregado"]
        RETRY["Retry Scheduler<br/>backoff + jitter"]
        DLQ["DLQ Manager<br/>mensajes fallidos y remediacion"]
        REPLAY["Replay Controller<br/>reproceso auditado"]
        BACKPRESSURE["Backpressure Controller<br/>control de saturacion"]
        AUDIT["Audit/Event Store<br/>trazabilidad y evidencias de intercambio"]
    end

    subgraph SoporteSalida["Contenedores consumidores"]
        TMS (Transportation Management) (APP-11)["Adaptador TMS (Transportation Management) (APP-11)<br/>APP-11"]
        PORTAL["Portal B2B / CRM<br/>APP-18 / APP-20"]
        ROUTE_OPT["Optimizador dinamico<br/>GCP Cloud Run/GKE"]
        OBS["Observabilidad unificada<br/>Plataforma de Observabilidad Unificada (PLT-01)"]
        IAM["Identidad y secretos<br/>Plataforma de Identidad y Accesos (IAM) (PLT-02)"]
    end

    OMS centralizado / Orquestador de Pedidos (APP-02) -->|"OrderEvents"| API_EVENTS
    INV -->|"InventoryEvents"| API_EVENTS
    MOBILE -->|"Tracking / Evidence / Exception Events"| API_EVENTS
    LEGADO -->|"LegacyNormalizedEvents"| API_EVENTS

    API_EVENTS --> SCHEMA
    SCHEMA --> ROUTER
    ROUTER --> ORDERING
    ORDERING --> RETRY
    RETRY --> TMS (Transportation Management) (APP-11)
    RETRY --> PORTAL
    RETRY --> ROUTE_OPT
    ROUTER --> DLQ
    DLQ --> REPLAY
    REPLAY --> ROUTER
    BACKPRESSURE --> ROUTER
    SCHEMA --> AUDIT
    ROUTER --> AUDIT
    DLQ --> AUDIT
    AUDIT --> OBS
    IAM --> API_EVENTS
    IAM --> REPLAY
```

## Como leer este diagrama para el comite

Este diagrama responde a la pregunta: **como funciona internamente el contenedor Bus de Eventos Central (PLT-03) cuando Azure es el hub central**. El foco no esta en toda la plataforma, sino en el Bus de Eventos Central.

| Elemento | Como interpretarlo |
|---|---|
| Contenedores productores | Sistemas que generan eventos: OMS centralizado / Orquestador de Pedidos (APP-02), Inventario, Backend Movil y adaptadores legados. Estan fuera del contenedor en foco. |
| Contenedor en foco | Bus de Eventos Central (PLT-03). Solo las cajas dentro de este bloque son componentes internos del contenedor. |
| Contenedores consumidores | Sistemas que reciben eventos ya validados/enrutados: TMS (Transportation Management) (APP-11), Portal/CRM, Optimizador GCP y Observabilidad. |
| Flechas de entrada | Eventos que ingresan al Bus de Eventos Central (PLT-03) (PLT-03) (Bus de Eventos Central (PLT-03)) (Bus de Eventos Central (PLT-03)) (Bus de Eventos Central (PLT-03)): ordenes, inventario, tracking, evidencias, excepciones y eventos normalizados desde legados. |
| Flechas internas | Flujo de procesamiento dentro de Bus de Eventos Central (PLT-03): ingestion, validacion, ruteo, orden, retry, DLQ, replay y auditoria. |
| Flechas de salida | Entrega de eventos a consumidores finales o plataformas de monitoreo. |

Flujo para explicar:

1. OMS centralizado / Orquestador de Pedidos (APP-02), Inventario, Backend Movil y legados envian eventos canonicos al Event Ingestion API.
2. Schema Validator verifica que cada evento tenga contrato, version, productor, correlation ID e idempotency key.
3. Event Router decide a que topico, cola o consumidor enviar el evento segun dominio, SLA y criticidad.
4. Ordering Guard protege la secuencia por agregado: orden, paquete, ruta, entrega o evidencia.
5. Retry Scheduler reintenta fallas transitorias con backoff y jitter.
6. Si el evento no puede procesarse, DLQ Manager conserva payload, error, consumidor y responsable de remediacion.
7. Replay Controller permite reprocesar eventos bajo control y auditoria, sin duplicar efectos de negocio.
8. Audit/Event Store deja evidencia del intercambio para soporte, observabilidad y conciliacion.
9. Backpressure Controller reduce o regula carga cuando WMS Principal (On Premises) (APP-06), TMS (Transportation Management) (APP-11), app o consumidores se degradan.

Mensaje clave para el comite: **Bus de Eventos Central (PLT-03) no es solo un bus tecnico; es el mecanismo de gobierno, resiliencia y trazabilidad que evita mensajes perdidos, duplicados o fuera de orden**.

## Componentes del contenedor en foco

| Componente | Responsabilidad | Trazabilidad |
|---|---|---|
| Event Ingestion API | Recibir eventos canonicos desde OMS centralizado / Orquestador de Pedidos (APP-02), Inventario, backend movil y adaptadores. | INI-02 RF-03 |
| Schema Validator | Validar contrato, version, productor, correlation ID e idempotency key. | INI-02 RF-01, RF-04 |
| Event Router | Enrutar eventos a topicos/colas por agregado, consumidor, prioridad y SLA. | INI-02 RF-08, RF-11 |
| Ordering Guard | Preservar secuencia logica por orden, paquete, ruta, entrega y evidencia. | INI-02 RF-11 |
| Retry Scheduler | Reintentar fallas transitorias con backoff y jitter. | INI-02 RF-05 |
| DLQ Manager | Mantener payload, error, timestamp, consumidor y responsable de remediacion. | INI-02 RF-06 |
| Replay Controller | Reprocesar eventos bajo aprobacion y sin duplicar efectos de negocio. | INI-02 RF-09 |
| Backpressure Controller | Regular productores/consumidores ante degradacion o saturacion. | INI-02 RF-07 |
| Audit/Event Store | Guardar evidencias de intercambio y trazabilidad operativa. | INI-02 RF-10, INT-10 |
