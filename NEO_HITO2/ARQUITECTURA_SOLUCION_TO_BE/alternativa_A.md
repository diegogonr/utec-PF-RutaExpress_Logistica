# Alternativa A - Azure como hub central de integracion y gobierno

## Resumen ejecutivo

La Alternativa A usa Azure como centro de gobierno API, OMS, eventos y observabilidad operacional; mantiene AWS como dominio natural de ultima milla, app movil y evidencias; y usa GCP para optimizacion, analitica y modelos predictivos. Esta alternativa conserva la ubicacion tecnologica mas cercana al Hito 1: TMS y capacidades de integracion en Azure, App de Conductores y S3 en AWS, y rutas/analitica en GCP.

## Cobertura del alcance

| Iniciativa | Cobertura principal |
|---|---|
| INI-01 | Orquestador de Pedidos (APP-02) evoluciona a OMS centralizado en Azure AKS; inventario y reservas se integran con WMS Cloud, WMS on premises y ERP mediante APIs/eventos. |
| INI-02 | Azure API Management gobierna APIs; Azure Event Hubs y Azure Service Bus implementan Bus de Eventos Central (PLT-03), DLQ, replay, backpressure y contratos. |
| INI-03 | AWS ECS/Lambda/DynamoDB soporta backend movil offline; S3 conserva evidencias; eventos se conectan al hub Azure y sincronizan TMS, portal y CRM. |

## Distribucion por nube

| Nube | Servicios propuestos | Uso |
|---|---|---|
| Azure | Azure API Management, AKS, Azure SQL, Event Hubs, Service Bus, Key Vault, Monitor, Application Insights, Entra ID | OMS, APIs, gobierno, eventos, colas, trazabilidad y seguridad central. |
| AWS | ECS Fargate, Lambda, DynamoDB, S3, SQS, EventBridge, KMS, CloudWatch | App de Conductores (APP-15), backend movil, evidencias (APP-16), colas locales y sincronizacion offline. |
| GCP | Cloud Run/GKE Autopilot, Pub/Sub, Dataflow, BigQuery, Vertex AI, Cloud Monitoring | Optimizacion dinamica, analitica, prediccion de excepciones y tableros de negocio. |
| On premises | WMS Principal (APP-06), WMS Satelite (APP-07), ERP Financiero (APP-25), conectividad privada | Transicion segura, conciliacion y liquidacion. |

## Diagramas C4 separados

- Nivel 1 Contexto: `diagramas_c4/alternativa_A_n1_contexto.md`.
- Nivel 2 Contenedores: `diagramas_c4/alternativa_A_n2_contenedores.md`.
- Nivel 3 Componentes: `diagramas_c4/alternativa_A_n3_componentes.md`.

Cada archivo separado incluye una seccion de lectura para comite con: significado de cajas, significado de flechas, flujo principal y mensaje clave. En este documento se mantienen los diagramas embebidos como resumen visual.

## Guia de lectura para comite

| Nivel | Que debe observar el comite | Como interpretar cajas y flechas |
|---|---|---|
| Contexto | Alcance del cambio y sistemas externos impactados. | La caja central es la Plataforma Logistica RutaExpress TO BE; las cajas externas son personas o sistemas que interactuan con ella; las flechas son relaciones funcionales. |
| Contenedores | Distribucion de responsabilidades entre Azure, AWS, GCP y sistemas existentes. | Cada caja es una aplicacion, servicio ejecutable, cola, bus o repositorio de datos; las flechas muestran comunicacion principal, no necesariamente llamadas sincronas. |
| Componentes | Funcionamiento interno del contenedor critico PLT-03 en Azure. | Solo las cajas dentro de "Contenedor en foco" son componentes internos; productores y consumidores son contenedores externos que envian o reciben eventos. |

Lectura ejecutiva: la Alternativa A centraliza gobierno, APIs y eventos en Azure, conserva AWS para ultima milla/evidencias y usa GCP para optimizacion/analitica.

## C4 Nivel 1 - Contexto

```mermaid
graph TB
    subgraph Personas["Personas"]
        CLIENTE["Cliente B2B / Retail<br/>Carga ordenes y consulta trazabilidad"]
        CONDUCTOR["Conductor<br/>Ejecuta entregas y registra evidencias"]
        OPERADOR["Operacion RutaExpress<br/>Supervisa pedidos, inventario, rutas y SLA"]
        FINANZAS["Finanzas<br/>Valida estados, evidencias y conciliacion"]
    end

    SISTEMA["Sistema en alcance:<br/>Plataforma Logistica RutaExpress TO BE<br/><br/>Alternativa A: gobierno e integracion centralizados"]

    subgraph Externos["Sistemas externos"]
        WMS["WMS Principal / WMS Satelite<br/>APP-06 / APP-07"]
        TMS["TMS Transportation Management<br/>APP-11"]
        ERP["ERP Financiero On Premises<br/>APP-25"]
        PORTAL["Portal B2B / CRM<br/>APP-18 / APP-20"]
        SAAS["Clientes SaaS y canales legados<br/>CSV / Excel / S3"]
        MAPAS["Servicios de trafico, mapas y geocodificacion"]
    end

    CLIENTE -->|"crea ordenes / consulta estado"| SISTEMA
    CONDUCTOR -->|"entregas, tracking y evidencias"| SISTEMA
    OPERADOR -->|"monitoreo y gestion operativa"| SISTEMA
    FINANZAS -->|"consulta soportes de liquidacion"| SISTEMA
    SISTEMA -->|"consulta y concilia inventario"| WMS
    SISTEMA -->|"sincroniza despacho, rutas y entregas"| TMS
    SISTEMA -->|"envia valorizacion, estados y evidencias"| ERP
    SISTEMA -->|"publica trazabilidad e incidencias"| PORTAL
    SISTEMA -->|"recibe ordenes e intercambios transicionales"| SAAS
    SISTEMA -->|"consulta trafico, zonas y tiempos estimados"| MAPAS
```

## C4 Nivel 2 - Contenedores

```mermaid
graph TB
    subgraph Personas["Personas y canales"]
        B2B["Cliente B2B / Portal"]
        APP["App de Conductores<br/>APP-15"]
        OPS["Operacion / Soporte / Finanzas"]
    end

    subgraph Sistema["Plataforma Logistica RutaExpress TO BE"]
        subgraph Azure["Contenedores en Azure"]
            APIM["Gateway y Gobierno API<br/>Azure API Management"]
            OMS["OMS centralizado<br/>APP-02 evolucionado sobre AKS"]
            INV["Servicio de Inventario y Reservas<br/>AKS"]
            OMSDB["Repositorio transaccional OMS/Inventario<br/>Azure SQL"]
            BUS["Bus de Eventos Central<br/>PLT-03 sobre Event Hubs"]
            COLAS["Colas, DLQ y Replay<br/>Azure Service Bus"]
            TMS_CONT["Adaptador TMS<br/>integracion con APP-11"]
            OBS["Observabilidad unificada<br/>PLT-01"]
            IAM["Identidad, secretos y llaves<br/>PLT-02"]
        end
        subgraph AWS["Contenedores en AWS"]
            MOBILE_BACKEND["Backend movil de ultima milla<br/>ECS/Lambda"]
            MOBILE_DB["Repositorio de sincronizacion movil<br/>DynamoDB"]
            EVIDENCE_STORE["Repositorio de evidencias<br/>S3 + KMS APP-16"]
            AWS_BUFFER["Buffer movil y puente de eventos<br/>SQS/EventBridge"]
        end
        subgraph GCP["Contenedores en GCP"]
            ROUTE_OPT["Optimizador dinamico de rutas<br/>Cloud Run/GKE"]
            ANALYTICS_BUS["Canal analitico<br/>Pub/Sub"]
            STREAMING["Procesamiento analitico<br/>Dataflow"]
            DWH["Repositorio analitico<br/>BigQuery"]
            ML["Prediccion de riesgo y demanda<br/>Vertex AI"]
        end
    end

    subgraph Externos["Sistemas externos"]
        WMS["WMS Principal / Satelite<br/>APP-06 / APP-07"]
        ERP["ERP Financiero<br/>APP-25"]
        PORTALCRM["Portal B2B / CRM<br/>APP-18 / APP-20"]
        LEGADO["Canales legados<br/>CSV / Excel / S3"]
    end

    B2B --> APIM
    APP --> MOBILE_BACKEND
    OPS --> OBS
    APIM --> OMS
    OMS --> OMSDB
    OMS --> INV
    INV --> OMSDB
    OMS --> BUS
    INV --> BUS
    BUS --> COLAS
    COLAS --> TMS_CONT
    COLAS --> MOBILE_BACKEND
    MOBILE_BACKEND --> MOBILE_DB
    MOBILE_BACKEND --> EVIDENCE_STORE
    MOBILE_BACKEND --> AWS_BUFFER
    AWS_BUFFER --> BUS
    BUS --> ANALYTICS_BUS
    ANALYTICS_BUS --> ROUTE_OPT
    ANALYTICS_BUS --> STREAMING
    STREAMING --> DWH
    DWH --> ML
    ROUTE_OPT --> TMS_CONT
    INV --> WMS
    INV --> ERP
    COLAS --> PORTALCRM
    LEGADO --> COLAS
    IAM --> APIM
    IAM --> OMS
    IAM --> MOBILE_BACKEND
    OBS --> BUS
    OBS --> MOBILE_BACKEND
    OBS --> ROUTE_OPT
```

## C4 Nivel 3 - Componentes principales

```mermaid
graph TB
    subgraph SoporteEntrada["Contenedores productores"]
        OMS["OMS centralizado<br/>APP-02 sobre AKS"]
        INV["Servicio de Inventario y Reservas<br/>AKS"]
        MOBILE["Backend movil<br/>AWS ECS/Lambda"]
        LEGADO["Adaptadores transicionales<br/>CSV / Excel / S3"]
    end

    subgraph PLT03["Contenedor en foco: Bus de Eventos Central PLT-03<br/>Azure Event Hubs + Azure Service Bus"]
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
        TMS["Adaptador TMS<br/>APP-11"]
        PORTAL["Portal B2B / CRM<br/>APP-18 / APP-20"]
        ROUTE_OPT["Optimizador dinamico<br/>GCP Cloud Run/GKE"]
        OBS["Observabilidad unificada<br/>PLT-01"]
        IAM["Identidad y secretos<br/>PLT-02"]
    end

    OMS -->|"OrderEvents"| API_EVENTS
    INV -->|"InventoryEvents"| API_EVENTS
    MOBILE -->|"Tracking / Evidence / Exception Events"| API_EVENTS
    LEGADO -->|"LegacyNormalizedEvents"| API_EVENTS
    API_EVENTS --> SCHEMA
    SCHEMA --> ROUTER
    ROUTER --> ORDERING
    ORDERING --> RETRY
    RETRY --> TMS
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

## Lineamientos y patrones aplicados

- Arquitectura: ARQ-01 a ARQ-10, especialmente APP-02 evolucionando a OMS sin crear nuevo ID.
- Integracion: APIs versionadas, eventos canonicos, correlation ID, idempotencia, secuencia por agregado y adaptadores transicionales.
- Seguridad: identidad federada, minimo privilegio, cifrado en transito/reposo, WAF, Key Vault, KMS y secretos administrados.
- Observabilidad: OpenTelemetry, logs estructurados, tableros de ordenes, inventario, colas, tracking, evidencias, excepciones y SLA.
- Escalabilidad: particiones por agregado, colas durables, backpressure, circuit breaker y pruebas de carga para 180,000 ordenes en campana.
- Patrones: Microservicios, DDD, EDA, Event Sourcing selectivo para trazabilidad operacional, Outbox/Inbox, Saga, CQRS selectivo, DLQ, replay controlado, store-and-forward y retry con backoff + jitter.

## Evaluacion

- Ventajas: mayor alineamiento con Hito 1, menor cambio sobre APP-15/APP-16, gobierno centralizado, buen soporte para APIs mock de MVP y menor riesgo de migracion.
- Desventajas: Azure queda como punto central de gobierno, por lo que requiere buen diseno de resiliencia y conectividad multinube.
- Nivel de costo relativo: intermedio, al priorizar servicios administrados existentes y evitar plataformas premium innecesarias para el MVP.
