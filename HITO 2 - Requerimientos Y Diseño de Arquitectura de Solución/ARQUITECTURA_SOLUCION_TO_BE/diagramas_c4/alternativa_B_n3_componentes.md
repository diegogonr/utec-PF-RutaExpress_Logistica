# Alternativa B - C4 Nivel 3 Componentes

## Proposito

Diagrama de componentes C4 para la Alternativa B. Este nivel hace zoom sobre un unico contenedor: **Hub principal de eventos (Bus de Eventos Central (PLT-03))** en AWS.

> Regla aplicada: C4 Component debe descomponer un solo contenedor. OMS centralizado / Orquestador de Pedidos (APP-02), Backend Movil, TMS (Transportation Management) (APP-11), Portal/CRM y GCP aparecen como contenedores o sistemas de soporte, no como componentes internos.

```mermaid
graph TB
    subgraph SoporteEntrada["Contenedores productores"]
        OMS centralizado / Orquestador de Pedidos (APP-02)["OMS centralizado / Orquestador de Pedidos (APP-02) e Inventario<br/>APP-02 sobre Azure AKS"]
        MOBILE["Backend movil<br/>AWS ECS/Lambda"]
        API_GW["Gateway y Gobierno API<br/>Azure API Management (APP-01)"]
        LEGADO["Adaptadores transicionales<br/>CSV / Excel / S3"]
    end

    subgraph PLT03["Contenedor en foco: Hub principal de eventos Bus de Eventos Central (PLT-03)<br/>AWS EventBridge + SQS"]
        INGEST["Event Ingestion<br/>PutEvents / API de eventos"]
        SCHEMA["Schema Lambda<br/>contratos AsyncAPI y versionado"]
        RULES["EventBridge Rules<br/>ruteo, filtros y fan-out"]
        QUEUES["SQS Queues<br/>buffer por consumidor y prioridad"]
        ORDERING["Ordering Guard<br/>secuencia por agregado"]
        RETRY["Retry Worker<br/>backoff + jitter"]
        DLQ["DLQ Processor<br/>mensajes fallidos y remediacion"]
        REPLAY["Replay Worker<br/>reproceso auditado"]
        THROTTLE["Backpressure Controller<br/>cuotas y throttling"]
        AUDIT["Audit/Event Store<br/>trazabilidad y evidencias de intercambio"]
    end

    subgraph SoporteSalida["Contenedores consumidores"]
        TMS (Transportation Management) (APP-11)["Adaptador TMS (Transportation Management) (APP-11)<br/>APP-11"]
        PORTAL["Portal B2B / CRM<br/>APP-18 / APP-20"]
        ROUTE_OPT["Optimizador dinamico<br/>GCP Cloud Run/GKE"]
        OBS["Observabilidad federada<br/>CloudWatch + Azure Monitor + GCP"]
        IAM["Secretos y roles<br/>AWS IAM + Secrets Manager"]
    end

    API_GW -->|"contratos / politicas"| OMS centralizado / Orquestador de Pedidos (APP-02)
    OMS centralizado / Orquestador de Pedidos (APP-02) -->|"OrderEvents / InventoryEvents"| INGEST
    MOBILE -->|"Tracking / Evidence / Exception Events"| INGEST
    LEGADO -->|"LegacyNormalizedEvents"| INGEST

    INGEST --> SCHEMA
    SCHEMA --> RULES
    RULES --> QUEUES
    QUEUES --> ORDERING
    ORDERING --> RETRY
    RETRY --> TMS (Transportation Management) (APP-11)
    RETRY --> PORTAL
    RETRY --> ROUTE_OPT
    QUEUES --> DLQ
    DLQ --> REPLAY
    REPLAY --> RULES
    THROTTLE --> RULES
    SCHEMA --> AUDIT
    RULES --> AUDIT
    DLQ --> AUDIT
    AUDIT --> OBS
    IAM --> INGEST
    IAM --> REPLAY
```

## Como leer este diagrama para el comite

Este diagrama responde a la pregunta: **como funciona internamente el contenedor Bus de Eventos Central (PLT-03) cuando AWS es el hub principal**. El foco es el Bus de Eventos Central (PLT-03) en AWS; los demas bloques son productores o consumidores externos al contenedor.

| Elemento | Como interpretarlo |
|---|---|
| Contenedores productores | OMS centralizado / Orquestador de Pedidos (APP-02)/Inventario en Azure, Backend Movil en AWS, Gateway API y adaptadores legados que generan o habilitan eventos. |
| Contenedor en foco | Hub principal de eventos Bus de Eventos Central (PLT-03) sobre AWS EventBridge + SQS. Solo las cajas dentro de este bloque son componentes internos. |
| Contenedores consumidores | TMS (Transportation Management) (APP-11), Portal/CRM, Optimizador GCP, Observabilidad e IAM/Secrets que reciben eventos o soportan la operacion. |
| Flechas de entrada | Eventos o politicas que llegan al hub AWS desde Azure, backend movil y legados. |
| Flechas internas | Flujo de procesamiento dentro del hub AWS: ingestion, validacion, reglas, colas, orden, retry, DLQ, replay y auditoria. |
| Flechas de salida | Entrega de eventos a sistemas consumidores y plataformas de monitoreo. |

Flujo para explicar:

1. Azure API Management (APP-01) gobierna contratos y politicas antes de que OMS centralizado / Orquestador de Pedidos (APP-02)/Inventario publique eventos.
2. OMS centralizado / Orquestador de Pedidos (APP-02)/Inventario envia eventos de orden e inventario hacia Event Ingestion en AWS.
3. Backend Movil publica tracking, evidencias y excepciones de forma nativa hacia el hub AWS.
4. Schema Lambda valida contrato, version, productor, correlation ID e idempotency key.
5. EventBridge Rules enruta eventos por dominio, consumidor, SLA, filtros y criticidad.
6. SQS Queues desacopla consumidores y permite buffering, prioridad y control de carga.
7. Ordering Guard preserva secuencia por agregado; Retry Worker maneja fallas transitorias.
8. DLQ Processor retiene eventos no procesables y Replay Worker permite reproceso controlado.
9. Audit/Event Store conserva trazabilidad para soporte, auditoria, observabilidad y conciliacion.

Mensaje clave para el comite: **esta alternativa concentra la resiliencia de eventos en AWS y simplifica ultima milla, pero exige control fuerte de puentes Azure-AWS para no duplicar gobierno ni perder trazabilidad**.

## Componentes del contenedor en foco

| Componente | Responsabilidad | Trazabilidad |
|---|---|---|
| Event Ingestion | Recibir eventos canonicos desde OMS centralizado / Orquestador de Pedidos (APP-02), backend movil y adaptadores. | INI-02 RF-03 |
| Schema Lambda | Validar contrato, version, productor, correlation ID e idempotency key. | INI-02 RF-01, RF-04 |
| EventBridge Rules | Enrutar eventos por dominio, consumidor, SLA y filtros. | INI-02 RF-08 |
| SQS Queues | Desacoplar consumidores, soportar buffering y prioridades. | INI-02 RF-05, RF-07 |
| Ordering Guard | Preservar secuencia logica por orden, paquete, ruta, entrega y evidencia. | INI-02 RF-11 |
| Retry Worker | Ejecutar reintentos con backoff y jitter. | INI-02 RF-05 |
| DLQ Processor | Mantener payload, error, timestamp, consumidor y responsable de remediacion. | INI-02 RF-06 |
| Replay Worker | Reprocesar eventos bajo aprobacion y sin duplicar efectos de negocio. | INI-02 RF-09 |
| Backpressure Controller | Regular productores/consumidores ante degradacion o saturacion. | INI-02 RF-07 |
| Audit/Event Store | Guardar evidencias de intercambio y trazabilidad operativa. | INI-02 RF-10, INT-10 |
