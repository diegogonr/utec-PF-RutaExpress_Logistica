# Alternativa A - C4 Nivel 2 Contenedores

## Proposito

Diagrama de contenedores C4 para la Alternativa A. Este nivel hace zoom dentro de la Plataforma Logistica RutaExpress TO BE y muestra aplicaciones, servicios ejecutables y repositorios de datos.

> Regla aplicada: los nombres priorizan la responsabilidad del contenedor; la tecnologia cloud aparece como detalle de implementacion.

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
            OMS centralizado / Orquestador de Pedidos (APP-02)["OMS centralizado<br/>APP-02 evolucionado sobre AKS"]
            INV["Servicio de Inventario y Reservas<br/>AKS"]
            OMS centralizado / Orquestador de Pedidos (APP-02)DB["Repositorio transaccional OMS centralizado / Orquestador de Pedidos (APP-02)/Inventario<br/>Azure SQL"]
            BUS["Bus de Eventos Central<br/>Bus de Eventos Central (PLT-03) sobre Event Hubs"]
            COLAS["Colas, DLQ y Replay<br/>Azure Service Bus"]
            TMS (Transportation Management) (APP-11)_CONT["Adaptador TMS (Transportation Management) (APP-11)<br/>integracion con APP-11"]
            OBS["Observabilidad unificada<br/>Plataforma de Observabilidad Unificada (PLT-01)"]
            IAM["Identidad, secretos y llaves<br/>Plataforma de Identidad y Accesos (IAM) (PLT-02)"]
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
        WMS Principal (On Premises) (APP-06)["WMS Principal / Satelite<br/>APP-06 / APP-07"]
        ERP Financiero (On Premises) (APP-25)["ERP Financiero<br/>APP-25"]
        PORTALCRM["Portal B2B / CRM<br/>APP-18 / APP-20"]
        LEGADO["Canales legados<br/>CSV / Excel / S3"]
    end

    B2B --> Azure API Management (APP-01)
    APP --> MOBILE_BACKEND
    OPS --> OBS

    Azure API Management (APP-01) --> OMS centralizado / Orquestador de Pedidos (APP-02)
    OMS centralizado / Orquestador de Pedidos (APP-02) --> OMS centralizado / Orquestador de Pedidos (APP-02)DB
    OMS centralizado / Orquestador de Pedidos (APP-02) --> INV
    INV --> OMS centralizado / Orquestador de Pedidos (APP-02)DB
    OMS centralizado / Orquestador de Pedidos (APP-02) --> BUS
    INV --> BUS
    BUS --> COLAS
    COLAS --> TMS (Transportation Management) (APP-11)_CONT
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
    ROUTE_OPT --> TMS (Transportation Management) (APP-11)_CONT
    INV --> WMS Principal (On Premises) (APP-06)
    INV --> ERP Financiero (On Premises) (APP-25)
    COLAS --> PORTALCRM
    LEGADO --> COLAS
    IAM --> Azure API Management (APP-01)
    IAM --> OMS centralizado / Orquestador de Pedidos (APP-02)
    IAM --> MOBILE_BACKEND
    OBS --> BUS
    OBS --> MOBILE_BACKEND
    OBS --> ROUTE_OPT
```

## Como leer este diagrama para el comite

Este diagrama responde a la pregunta: **como se reparte la plataforma en aplicaciones, servicios y repositorios de datos**. A diferencia del contexto, aqui ya aparecen decisiones tecnologicas principales y responsabilidades por nube.

| Elemento | Como interpretarlo |
|---|---|
| Cajas dentro de Azure, AWS y GCP | Contenedores C4: aplicaciones, servicios ejecutables, colas, buses o repositorios de datos que forman parte de RutaExpress TO BE. |
| Cajas de Personas y canales | Entradas principales al sistema: clientes B2B, App de Conductores (APP-15) y usuarios operativos. |
| Cajas de Sistemas externos | Sistemas con los que la plataforma convive o se integra, pero que no son responsabilidad interna de este diseno. |
| Flechas | Comunicacion principal entre contenedores: APIs, eventos, sincronizacion, persistencia o publicacion de estados. La flecha indica dependencia o flujo de informacion, no necesariamente una llamada sincrona. |
| Agrupaciones por nube | Ubicacion logica propuesta para la alternativa. No implican todavia detalle de despliegue fisico, alta disponibilidad o subredes; eso corresponderia a diagramas de despliegue. |

Flujo para explicar:

1. El cliente entra por el Gateway y Gobierno API en Azure, que valida seguridad, cuotas y contratos antes de llegar al OMS centralizado / Orquestador de Pedidos (APP-02).
2. El OMS centralizado coordina ordenes y llama al Servicio de Inventario y Reservas; ambos persisten estado en Azure SQL.
3. OMS centralizado / Orquestador de Pedidos (APP-02) e Inventario publican eventos al Bus de Eventos Central (PLT-03) (PLT-03) (Bus de Eventos Central (PLT-03)) (Bus de Eventos Central (PLT-03)) (Bus de Eventos Central (PLT-03)) de Eventos Central en Azure; las colas/DLQ/replay desacoplan consumidores y protegen ante fallas.
4. El Backend Movil en AWS se comunica con la App de Conductores (APP-15), mantiene sincronizacion offline en DynamoDB y almacena evidencias en S3 con KMS.
5. El buffer movil AWS se conecta al Bus de Eventos Central (PLT-03) (PLT-03) (Bus de Eventos Central (PLT-03)) (Bus de Eventos Central (PLT-03)) (Bus de Eventos Central (PLT-03)) Azure para que tracking, evidencias y excepciones entren al flujo corporativo.
6. GCP recibe eventos analiticos para optimizacion de rutas, procesamiento streaming, BigQuery y modelos predictivos.
7. WMS Principal (On Premises) (APP-06), ERP Financiero (On Premises) (APP-25), Portal/CRM y legados quedan integrados mediante APIs/eventos, sin acoplarse directamente entre si.

Mensaje clave para el comite: **la Alternativa A centraliza gobierno e integracion en Azure, manteniendo AWS y GCP en los dominios donde ya aportan valor operativo**.

## Contenedores principales

| Contenedor | Tecnologia | Responsabilidad |
|---|---|---|
| Gateway y Gobierno API | Azure API Management (APP-01) | Contratos, OAuth/OIDC, cuotas, rate limiting y APIs mock. |
| OMS centralizado | Azure AKS | Ciclo de vida de ordenes, validacion, deduplicacion e idempotencia. |
| Servicio de Inventario y Reservas | Azure AKS | Disponibilidad, reservas, liberaciones, movimientos y conciliacion. |
| Bus de Eventos Central | Azure Event Hubs / Service Bus | Eventos canonicos, colas, DLQ, replay y backpressure. |
| Backend movil | AWS ECS/Lambda | Store-and-forward, acks, tracking y excepciones. |
| Repositorio de evidencias | AWS S3 + KMS | Fotos, firmas, hash, cifrado y retencion. |
| Optimizador dinamico | GCP Cloud Run/GKE | Rutas, trafico, ventanas, capacidad y SLA. |
