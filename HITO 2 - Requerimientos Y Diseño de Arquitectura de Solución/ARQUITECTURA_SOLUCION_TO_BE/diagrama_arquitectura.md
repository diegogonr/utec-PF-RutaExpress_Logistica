# Diagrama de arquitectura cloud transversal

## Vista representada

Este diagrama representa la arquitectura cloud transversal de la Alternativa A recomendada: Azure como hub central de integracion y gobierno, AWS para ultima milla/evidencias y GCP para optimizacion/analitica.

No reemplaza los diagramas C4. Los diagramas C4 corregidos segun la documentacion oficial estan separados por alternativa y nivel en la tabla siguiente.

## Diagramas C4 por alternativa

| Alternativa | Nivel 1 Contexto | Nivel 2 Contenedores | Nivel 3 Componentes |
|---|---|---|---|
| Alternativa A | `diagramas_c4/alternativa_A_n1_contexto.md` | `diagramas_c4/alternativa_A_n2_contenedores.md` | `diagramas_c4/alternativa_A_n3_componentes.md` |
| Alternativa B | `diagramas_c4/alternativa_B_n1_contexto.md` | `diagramas_c4/alternativa_B_n2_contenedores.md` | `diagramas_c4/alternativa_B_n3_componentes.md` |

## Diagrama cloud transversal

```mermaid
flowchart LR
    subgraph Users["Usuarios y canales"]
        B2B["Clientes B2B / Retail"]
        Driver["Conductores"]
        Ops["Operacion / Soporte / Finanzas"]
    end

    subgraph Azure["Azure - Gobierno, OMS centralizado / Orquestador de Pedidos (APP-02), TMS (Transportation Management) (APP-11) e integracion"]
        Azure API Management (APP-01)["[Azure] Azure API Management (APP-01)<br/>Contratos, OAuth/OIDC, cuotas, APIs mock"]
        OMS centralizado / Orquestador de Pedidos (APP-02)["[Azure AKS] OMS centralizado<br/>Orquestador de Pedidos (APP-02) evolucionado"]
        INV["[Azure AKS] Inventario y Reservas<br/>SKU, almacen, ubicacion, lote, estado"]
        AZSQL["[Azure SQL] Ordenes, reservas, outbox, auditoria"]
        EVH["[Azure Event Hubs] Bus de Eventos Central (PLT-03)<br/>Eventos canonicos"]
        ASB["[Azure Service Bus] Colas, DLQ, retry, replay"]
        TMS (Transportation Management) (APP-11)["[Azure] TMS (Transportation Management) (APP-11) (APP-11)<br/>Despacho y rutas"]
        OBS["[Azure Monitor + OpenTelemetry] Plataforma de Observabilidad Unificada (PLT-01)<br/>Metricas, logs, trazas, alertas"]
        IAM["[Entra ID + Key Vault] Plataforma de Identidad y Accesos (IAM) (PLT-02)<br/>Identidad, secretos, llaves"]
        IAC["[Terraform/Pipelines] Plataforma IaC (PLT-04)<br/>Infraestructura como codigo y politicas"]
    end

    subgraph AWS["AWS - Ultima milla y evidencias"]
        APP["[AWS] App de Conductores (APP-15)<br/>Offline-first"]
        MOB["[ECS/Lambda] Backend movil<br/>Store-and-forward, acks, tracking"]
        DDB["[DynamoDB] Estado movil y eventos pendientes"]
        S3["[S3 + KMS] Almacenamiento Evidencias (APP-16)<br/>Fotos, firmas, hash"]
        SQS["[SQS/EventBridge] Buffer movil y puente de eventos"]
    end

    subgraph GCP["GCP - Optimizacion y analitica"]
        OPT["[Cloud Run/GKE] Optimizador dinamico<br/>trafico, capacidad, ventanas, SLA"]
        PUBSUB["[Pub/Sub] Eventos analiticos"]
        BQ["[BigQuery] SLA, rutas, tracking, excepciones"]
        VTX["[Vertex AI] Prediccion de excepciones y demanda"]
    end

    subgraph OnPrem["On premises y SaaS transicional"]
        WMS Principal (On Premises) (APP-06)P["WMS Principal (APP-06)"]
        WMS Principal (On Premises) (APP-06)S["WMS Satelite (APP-07)"]
        ERP Financiero (On Premises) (APP-25)["ERP Financiero (APP-25)"]
        PORTAL["Portal B2B / CRM"]
    end

    B2B --> Azure API Management (APP-01)
    Driver --> APP
    Ops --> OBS
    Azure API Management (APP-01) --> OMS centralizado / Orquestador de Pedidos (APP-02)
    OMS centralizado / Orquestador de Pedidos (APP-02) --> AZSQL
    OMS centralizado / Orquestador de Pedidos (APP-02) --> INV
    INV --> AZSQL
    OMS centralizado / Orquestador de Pedidos (APP-02) --> EVH
    INV --> EVH
    EVH --> ASB
    ASB --> TMS (Transportation Management) (APP-11)
    ASB --> PORTAL
    INV --> WMS Principal (On Premises) (APP-06)P
    INV --> WMS Principal (On Premises) (APP-06)S
    INV --> ERP Financiero (On Premises) (APP-25)
    MOB --> DDB
    APP --> MOB
    MOB --> S3
    MOB --> SQS
    SQS --> EVH
    EVH --> PUBSUB
    PUBSUB --> OPT
    OPT --> BQ
    BQ --> VTX
    OPT --> TMS (Transportation Management) (APP-11)
    TMS (Transportation Management) (APP-11) --> EVH
    EVH --> OBS
    ASB --> OBS
    MOB --> OBS
    S3 --> OBS
    OPT --> OBS
    IAM --> Azure API Management (APP-01)
    IAM --> OMS centralizado / Orquestador de Pedidos (APP-02)
    IAM --> MOB
    IAM --> S3
    IAC --> Azure API Management (APP-01)
    IAC --> OMS centralizado / Orquestador de Pedidos (APP-02)
    IAC --> MOB
    IAC --> OPT
```

## Como leer este diagrama para el comite

Este diagrama no es C4; es una vista cloud transversal de la Alternativa A recomendada. Sirve para explicar **donde vive cada capacidad tecnologica** y como se conectan los dominios Azure, AWS, GCP y on premises.

| Elemento | Como interpretarlo |
|---|---|
| Subgrafo Azure | Centro de gobierno, OMS centralizado / Orquestador de Pedidos (APP-02), TMS (Transportation Management) (APP-11), APIs, eventos, colas, identidad, observabilidad e IaC. |
| Subgrafo AWS | Dominio de ultima milla: App de Conductores (APP-15), backend movil, DynamoDB, S3, SQS/EventBridge y evidencias. |
| Subgrafo GCP | Dominio de optimizacion, analitica, BigQuery y prediccion. |
| Subgrafo On premises y SaaS | Sistemas existentes que se mantienen durante la transicion: WMS Principal (On Premises) (APP-06), ERP Financiero (On Premises) (APP-25), Portal/CRM. |
| Flechas | Flujo principal de informacion entre capacidades: APIs, eventos, sincronizacion, persistencia o integraciones. |

Flujo para explicar:

1. Clientes y operadores entran por Azure API Management (APP-01) y observabilidad.
2. OMS centralizado coordina ordenes e inventario; Inventario se integra con WMS Principal (On Premises) (APP-06) y ERP Financiero (On Premises) (APP-25).
3. OMS centralizado / Orquestador de Pedidos (APP-02) e Inventario publican eventos al Bus de Eventos Central (PLT-03) (PLT-03) (Bus de Eventos Central (PLT-03)) (Bus de Eventos Central (PLT-03)) (Bus de Eventos Central (PLT-03)) de Eventos Central en Azure.
4. Service Bus maneja colas, DLQ, reintentos y replay para desacoplar consumidores.
5. La App de Conductores (APP-15) opera en AWS con backend movil, DynamoDB y evidencias en S3.
6. El buffer movil AWS envia tracking, evidencias y excepciones hacia el Bus de Eventos Central (PLT-03).
7. GCP recibe eventos para optimizacion de rutas, analitica y prediccion.
8. Observabilidad, identidad e IaC atraviesan todos los dominios para mantener trazabilidad, seguridad y gobierno.

Mensaje clave para el comite: **la vista cloud muestra la topologia recomendada; los diagramas C4 explican el alcance, los contenedores y el detalle interno del componente de eventos**.

## Notas de implementacion

- El Bus de Eventos Central (PLT-03) queda en Azure con puentes controlados hacia AWS y GCP.
- La App de Conductores (APP-15) no cambia de dominio tecnologico; se fortalece con backend movil, DynamoDB, SQS y store-and-forward.
- El Almacenamiento Evidencias (S3) (APP-16) se mantiene y se gobierna con hash, KMS, politicas de retencion y eventos de auditoria.
- OMS centralizado es la evolucion de APP-02; no se crea un nuevo ID de aplicacion.
- Los sistemas on premises se integran mediante APIs/eventos, circuit breaker, backpressure y adaptadores transicionales.
