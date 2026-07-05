# Alternativa B - AWS como hub principal de eventos y backend movil

## Resumen ejecutivo

La Alternativa B usa AWS como centro principal de eventos, backend movil y resiliencia operativa, mientras Azure conserva APIs, TMS y OMS, y GCP mantiene optimizacion/analitica. Es viable, pero desplaza el hub de mensajeria hacia AWS, aumentando la distancia con el gobierno API y OMS que permanecen en Azure.

## Cobertura del alcance

| Iniciativa | Cobertura principal |
|---|---|
| INI-01 | OMS centralizado en Azure AKS, integrado con WMS/ERP mediante APIs y eventos enviados al hub AWS. |
| INI-02 | AWS EventBridge, SQS y SNS implementan el hub de eventos, DLQ y replay; Azure API Management gobierna APIs. |
| INI-03 | AWS concentra App de Conductores, sincronizacion offline, DynamoDB, S3, SQS y eventos moviles. |

## Distribucion por nube

| Nube | Servicios propuestos | Uso |
|---|---|---|
| AWS | EventBridge, SQS, SNS, Lambda, ECS Fargate, DynamoDB, S3, KMS, CloudWatch, X-Ray, Secrets Manager | Hub de eventos, backend movil, evidencias, colas, DLQ y observabilidad AWS. |
| Azure | API Management, AKS, Azure SQL, Entra ID, Key Vault, Monitor | APIs, OMS, TMS, identidad federada y servicios de orden/inventario. |
| GCP | Cloud Run/GKE, Pub/Sub, Dataflow, BigQuery, Vertex AI | Optimizacion, analitica y modelos predictivos. |
| On premises | WMS/ERP con conectividad privada | Transicion de inventario y conciliacion financiera. |

## Diagramas C4 separados

- Nivel 1 Contexto: `diagramas_c4/alternativa_B_n1_contexto.md`.
- Nivel 2 Contenedores: `diagramas_c4/alternativa_B_n2_contenedores.md`.
- Nivel 3 Componentes: `diagramas_c4/alternativa_B_n3_componentes.md`.

Cada archivo separado incluye una seccion de lectura para comite con: significado de cajas, significado de flechas, flujo principal y mensaje clave. En este documento se mantienen los diagramas embebidos como resumen visual.

## Guia de lectura para comite

| Nivel | Que debe observar el comite | Como interpretar cajas y flechas |
|---|---|---|
| Contexto | Alcance del cambio y sistemas externos impactados. | La caja central es la Plataforma Logistica RutaExpress TO BE; las cajas externas son personas o sistemas que interactuan con ella; las flechas son relaciones funcionales. |
| Contenedores | Distribucion de responsabilidades entre Azure, AWS, GCP y sistemas existentes. | Cada caja es una aplicacion, servicio ejecutable, cola, bus o repositorio de datos; las flechas muestran comunicacion principal, no necesariamente llamadas sincronas. |
| Componentes | Funcionamiento interno del contenedor critico PLT-03 en AWS. | Solo las cajas dentro de "Contenedor en foco" son componentes internos; productores y consumidores son contenedores externos que envian o reciben eventos. |

Lectura ejecutiva: la Alternativa B mueve el centro de eventos y resiliencia a AWS, manteniendo Azure para APIs/OMS/TMS y GCP para optimizacion/analitica.

## C4 Nivel 1 - Contexto

```mermaid
graph TB
    subgraph Personas["Personas"]
        CLIENTE["Cliente B2B / Retail<br/>Carga ordenes y consulta trazabilidad"]
        CONDUCTOR["Conductor<br/>Ejecuta entregas y registra evidencias"]
        OPERADOR["Operacion RutaExpress<br/>Supervisa pedidos, inventario, rutas y SLA"]
        FINANZAS["Finanzas<br/>Valida estados, evidencias y conciliacion"]
    end

    SISTEMA["Sistema en alcance:<br/>Plataforma Logistica RutaExpress TO BE<br/><br/>Alternativa B: eventos y ultima milla priorizados"]

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
            OMS["OMS e Inventario<br/>APP-02 evolucionado sobre AKS"]
            OMSDB["Repositorio transaccional OMS/Inventario<br/>Azure SQL"]
            TMS_CONT["Adaptador TMS<br/>integracion con APP-11"]
            AZ_OBS["Telemetria Azure<br/>Azure Monitor"]
            AZ_IAM["Identidad y secretos Azure<br/>Entra ID + Key Vault"]
        end
        subgraph AWS["Contenedores en AWS"]
            EVENT_HUB["Hub principal de eventos<br/>EventBridge PLT-03"]
            EVENT_QUEUES["Colas, DLQ y Replay<br/>SQS + workers"]
            EVENT_ADAPTERS["Adaptadores y validadores<br/>Lambda/ECS"]
            MOBILE_BACKEND["Backend movil de ultima milla<br/>ECS/Lambda"]
            MOBILE_DB["Repositorio de sincronizacion movil<br/>DynamoDB"]
            EVIDENCE_STORE["Repositorio de evidencias<br/>S3 + KMS APP-16"]
            AWS_OBS["Telemetria AWS<br/>CloudWatch + X-Ray"]
            AWS_IAM["Secretos y roles AWS<br/>Secrets Manager + IAM"]
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
    OPS --> AZ_OBS
    OPS --> AWS_OBS
    APIM --> OMS
    OMS --> OMSDB
    OMS --> EVENT_HUB
    OMS --> WMS
    OMS --> ERP
    EVENT_HUB --> EVENT_QUEUES
    EVENT_QUEUES --> EVENT_ADAPTERS
    EVENT_ADAPTERS --> TMS_CONT
    EVENT_ADAPTERS --> PORTALCRM
    EVENT_ADAPTERS --> LEGADO
    MOBILE_BACKEND --> MOBILE_DB
    MOBILE_BACKEND --> EVIDENCE_STORE
    MOBILE_BACKEND --> EVENT_HUB
    EVENT_HUB --> ANALYTICS_BUS
    ANALYTICS_BUS --> ROUTE_OPT
    ANALYTICS_BUS --> STREAMING
    STREAMING --> DWH
    DWH --> ML
    ROUTE_OPT --> TMS_CONT
    AZ_IAM --> APIM
    AZ_IAM --> OMS
    AWS_IAM --> MOBILE_BACKEND
    AWS_IAM --> EVENT_HUB
```

## C4 Nivel 3 - Componentes principales

```mermaid
graph TB
    subgraph SoporteEntrada["Contenedores productores"]
        OMS["OMS e Inventario<br/>APP-02 sobre Azure AKS"]
        MOBILE["Backend movil<br/>AWS ECS/Lambda"]
        API_GW["Gateway y Gobierno API<br/>Azure API Management"]
        LEGADO["Adaptadores transicionales<br/>CSV / Excel / S3"]
    end

    subgraph PLT03["Contenedor en foco: Hub principal de eventos PLT-03<br/>AWS EventBridge + SQS"]
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
        TMS["Adaptador TMS<br/>APP-11"]
        PORTAL["Portal B2B / CRM<br/>APP-18 / APP-20"]
        ROUTE_OPT["Optimizador dinamico<br/>GCP Cloud Run/GKE"]
        OBS["Observabilidad federada<br/>CloudWatch + Azure Monitor + GCP"]
        IAM["Secretos y roles<br/>AWS IAM + Secrets Manager"]
    end

    API_GW -->|"contratos / politicas"| OMS
    OMS -->|"OrderEvents / InventoryEvents"| INGEST
    MOBILE -->|"Tracking / Evidence / Exception Events"| INGEST
    LEGADO -->|"LegacyNormalizedEvents"| INGEST
    INGEST --> SCHEMA
    SCHEMA --> RULES
    RULES --> QUEUES
    QUEUES --> ORDERING
    ORDERING --> RETRY
    RETRY --> TMS
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

## Lineamientos y patrones aplicados

- Arquitectura: separacion por dominios, APP-02 evoluciona a OMS y APP-15/APP-16 permanecen en AWS.
- Integracion: EventBridge/SQS como hub, Azure API Management para APIs y puentes seguros entre Azure/AWS/GCP.
- Seguridad: federacion, WAF, IAM por nube, Secrets Manager/Key Vault y cifrado con KMS.
- Observabilidad: OpenTelemetry con consolidacion federada desde CloudWatch, Azure Monitor y GCP Monitoring.
- Patrones: Microservicios, DDD, EDA, Event Sourcing selectivo para auditoria operacional, Outbox/Inbox, Saga, DLQ, replay, backpressure, store-and-forward y retry con jitter.

## Evaluacion

- Ventajas: fortalece el dominio movil/evidencias ya ubicado en AWS y simplifica colas de ultima milla.
- Desventajas: el hub principal queda separado del OMS y API governance, aumentando puentes, latencia operativa, gobierno cruzado y riesgo de doble plano de control.
- Nivel de costo relativo: intermedio-alto por mayor cantidad de bridges, duplicidad parcial de observabilidad y gobierno entre Azure y AWS.
