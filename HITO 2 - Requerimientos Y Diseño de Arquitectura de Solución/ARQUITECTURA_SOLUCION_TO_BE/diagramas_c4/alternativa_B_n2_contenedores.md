# Alternativa B - C4 Nivel 2 Contenedores

## Proposito

Diagrama de contenedores C4 para la Alternativa B. Este nivel hace zoom dentro de la Plataforma Logistica RutaExpress TO BE y muestra aplicaciones, servicios ejecutables y repositorios de datos.

> Regla aplicada: AWS concentra el hub principal de eventos y ultima milla; Azure conserva APIs, OMS centralizado / Orquestador de Pedidos (APP-02) y TMS (Transportation Management) (APP-11); GCP conserva optimizacion y analitica.

```mermaid
graph TB
    subgraph Personas["Personas y canales"]
        B2B["Cliente B2B / Portal"]
        APP["App de Conductores (APP-15)<br/>APP-15"]
        OPS["Operacion / Soporte / Finanzas"]
    end

    subgraph Sistema["Plataforma Logistica RutaExpress TO BE"]
        subgraph Azure["Contenedores en Azure"]
            Azure API Management (APP-01)["Gateway y Gobierno API<br/>Azure API Management (APP-01)"]
            OMS centralizado / Orquestador de Pedidos (APP-02)["OMS centralizado / Orquestador de Pedidos (APP-02) e Inventario<br/>APP-02 evolucionado sobre AKS"]
            OMS centralizado / Orquestador de Pedidos (APP-02)DB["Repositorio transaccional OMS centralizado / Orquestador de Pedidos (APP-02)/Inventario<br/>Azure SQL"]
            TMS (Transportation Management) (APP-11)_CONT["Adaptador TMS (Transportation Management) (APP-11)<br/>integracion con APP-11"]
            AZ_OBS["Telemetria Azure<br/>Azure Monitor"]
            AZ_IAM["Identidad y secretos Azure<br/>Entra ID + Key Vault"]
        end

        subgraph AWS["Contenedores en AWS"]
            EVENT_HUB["Hub principal de eventos<br/>EventBridge Bus de Eventos Central (PLT-03)"]
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
        WMS Principal (On Premises) (APP-06)["WMS Principal / Satelite<br/>APP-06 / APP-07"]
        ERP Financiero (On Premises) (APP-25)["ERP Financiero<br/>APP-25"]
        PORTALCRM["Portal B2B / CRM<br/>APP-18 / APP-20"]
        LEGADO["Canales legados<br/>CSV / Excel / S3"]
    end

    B2B --> Azure API Management (APP-01)
    APP --> MOBILE_BACKEND
    OPS --> AZ_OBS
    OPS --> AWS_OBS

    Azure API Management (APP-01) --> OMS centralizado / Orquestador de Pedidos (APP-02)
    OMS centralizado / Orquestador de Pedidos (APP-02) --> OMS centralizado / Orquestador de Pedidos (APP-02)DB
    OMS centralizado / Orquestador de Pedidos (APP-02) --> EVENT_HUB
    OMS centralizado / Orquestador de Pedidos (APP-02) --> WMS Principal (On Premises) (APP-06)
    OMS centralizado / Orquestador de Pedidos (APP-02) --> ERP Financiero (On Premises) (APP-25)
    EVENT_HUB --> EVENT_QUEUES
    EVENT_QUEUES --> EVENT_ADAPTERS
    EVENT_ADAPTERS --> TMS (Transportation Management) (APP-11)_CONT
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
    ROUTE_OPT --> TMS (Transportation Management) (APP-11)_CONT
    AZ_IAM --> Azure API Management (APP-01)
    AZ_IAM --> OMS centralizado / Orquestador de Pedidos (APP-02)
    AWS_IAM --> MOBILE_BACKEND
    AWS_IAM --> EVENT_HUB
```

## Como leer este diagrama para el comite

Este diagrama responde a la pregunta: **como se reparte la plataforma en aplicaciones, servicios y repositorios de datos en la Alternativa B**. Aqui se ve el cambio mas importante respecto a la Alternativa A: el hub principal de eventos se ubica en AWS.

| Elemento | Como interpretarlo |
|---|---|
| Cajas dentro de Azure, AWS y GCP | Contenedores C4: aplicaciones, servicios ejecutables, colas, buses o repositorios de datos dentro de la plataforma RutaExpress TO BE. |
| Cajas de Personas y canales | Entradas y consumidores humanos principales: clientes, conductores y operacion/soporte/finanzas. |
| Cajas de Sistemas externos | Sistemas que se integran con la plataforma, pero que no se descomponen en este diagrama. |
| Flechas | Flujos principales de informacion. Pueden representar APIs, eventos, persistencia, sincronizacion movil o entrega de mensajes. |
| Agrupaciones por nube | Ubicacion logica propuesta para esta alternativa. No representa redes, subredes ni topologia fisica final. |

Flujo para explicar:

1. El cliente entra por Azure API Management (APP-01) y las solicitudes llegan al OMS centralizado / Orquestador de Pedidos (APP-02) e Inventario desplegado en Azure.
2. El OMS centralizado / Orquestador de Pedidos (APP-02) persiste en Azure SQL, consulta WMS Principal (On Premises) (APP-06)/ERP cuando corresponde y publica eventos hacia el hub principal en AWS.
3. AWS EventBridge recibe eventos corporativos y los deriva a SQS, DLQ, workers de validacion, replay y adaptadores.
4. El Backend Movil tambien queda en AWS, por lo que tracking, evidencias y excepciones entran de forma nativa al hub AWS.
5. Los adaptadores publican estados hacia TMS (Transportation Management) (APP-11), Portal/CRM y canales legados.
6. GCP recibe eventos desde AWS para optimizacion, analitica, BigQuery y modelos predictivos.
7. La observabilidad queda federada entre Azure y AWS, lo que requiere una disciplina mayor de correlacion y gobierno.

Mensaje clave para el comite: **la Alternativa B fortalece AWS como centro de eventos y ultima milla, pero aumenta la necesidad de puentes y gobierno cruzado entre Azure y AWS**.

## Contenedores principales

| Contenedor | Tecnologia | Responsabilidad |
|---|---|---|
| Gateway y Gobierno API | Azure API Management (APP-01) | Contratos, OAuth/OIDC, cuotas, rate limiting y APIs mock. |
| OMS centralizado / Orquestador de Pedidos (APP-02) e Inventario | Azure AKS | Ordenes, validacion, deduplicacion, reservas y conciliacion. |
| Hub principal de eventos | AWS EventBridge | Eventos canonicos, ruteo y fan-out. |
| Colas, DLQ y Replay | AWS SQS + workers | Retry, mensajes fallidos, reproceso y backpressure. |
| Backend movil | AWS ECS/Lambda | Store-and-forward, acks, tracking y excepciones. |
| Repositorio de evidencias | AWS S3 + KMS | Fotos, firmas, hash, cifrado y retencion. |
| Optimizador dinamico | GCP Cloud Run/GKE | Rutas, trafico, ventanas, capacidad y SLA. |
