# Alternativa B - C4 Nivel 2 Contenedores

## Proposito

Diagrama de contenedores C4 para la Alternativa B. Este nivel hace zoom dentro de la Plataforma Logistica RutaExpress TO BE y muestra aplicaciones, servicios ejecutables y repositorios de datos.

> Regla aplicada: los nombres priorizan la responsabilidad del contenedor; la tecnologia cloud aparece como detalle de implementacion.

```mermaid
graph TB
    subgraph Personas["Personas y canales"]
        B2B["Cliente B2B / Portal"]
        APP["App de Conductores (APP-15)"]
        OPS["Operacion / Soporte / Finanzas"]
    end

    subgraph Sistema["Plataforma Logistica RutaExpress TO BE"]
        subgraph Azure["Contenedores en Azure"]
            APIM["Gateway y Gobierno API<br/>Azure API Management (APP-01)"]
            CORE["Nucleo Logistico Modular<br/>APP-02 OMS + Inventario en AKS"]
            ORCH["Orquestador de Procesos<br/>Durable Functions"]
            SQL["Repositorio transaccional<br/>Azure SQL"]
            NOTIF["Canal de notificaciones<br/>Service Bus topics"]
            ACL["Adaptadores ACL<br/>WMS / TMS / ERP"]
            OBS["Observabilidad unificada<br/>Plataforma de Observabilidad Unificada (PLT-01)"]
            IAM["Identidad y secretos<br/>Plataforma de Identidad y Accesos (IAM) (PLT-02)"]
        end

        subgraph AWS["Contenedores en AWS"]
            MOBILE_BACKEND["Backend movil de ultima milla<br/>ECS/Lambda"]
            MOBILE_DB["Repositorio de sincronizacion movil<br/>DynamoDB"]
            EVIDENCE_STORE["Repositorio de evidencias<br/>S3 + KMS APP-16"]
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
        TMS["TMS Transportation Management<br/>APP-11"]
        PORTALCRM["Portal B2B / CRM<br/>APP-18 / APP-20"]
        LEGADO["Canales legados<br/>CSV / Excel / S3"]
    end

    B2B --> APIM
    APP --> MOBILE_BACKEND
    OPS --> OBS

    APIM --> CORE
    CORE --> SQL
    CORE --> ORCH
    ORCH --> CORE
    ORCH --> ACL
    ACL --> WMS
    ACL --> ERP
    ACL --> TMS
    CORE --> NOTIF
    ORCH --> NOTIF
    NOTIF --> PORTALCRM
    NOTIF --> MOBILE_BACKEND
    NOTIF --> ANALYTICS_BUS
    MOBILE_BACKEND --> MOBILE_DB
    MOBILE_BACKEND --> EVIDENCE_STORE
    MOBILE_BACKEND -->|"confirmacion API idempotente"| APIM
    ANALYTICS_BUS --> ROUTE_OPT
    ANALYTICS_BUS --> STREAMING
    STREAMING --> DWH
    DWH --> ML
    ROUTE_OPT --> ACL
    LEGADO --> APIM
    IAM --> APIM
    IAM --> CORE
    IAM --> MOBILE_BACKEND
    OBS --> CORE
    OBS --> ORCH
    OBS --> MOBILE_BACKEND
```

## Como leer este diagrama para el comite

Este diagrama responde a la pregunta: **como se reparte la plataforma en aplicaciones, servicios y repositorios de datos en la Alternativa B**. El cambio respecto a A no es “mover el bus a otra nube”, sino **empaquetar el core y coordinarlo por orquestacion**.

| Elemento | Como interpretarlo |
|---|---|
| Nucleo Logistico Modular | Un contenedor con OMS + Inventario; no hay microservicio de inventario separado. |
| Orquestador de Procesos | Coordina la Saga sincrona/semi-sincrona y compensaciones. |
| Canal de notificaciones | Fan-out informativo; no es Bus de Eventos Central (PLT-03) de consistencia. |
| Backend movil AWS | Offline-first; confirma al nucleo por API tras sincronizar. |
| Flechas | Preferentemente comandos/APIs en el core; notificaciones hacia consumidores. |

Flujo para explicar:

1. El cliente entra por Azure API Management (APP-01).
2. El Nucleo Modular registra/valida la orden y dispara el Orquestador.
3. El Orquestador ejecuta reserva/liberacion via modulos internos y ACL hacia WMS/ERP/TMS.
4. Al completar pasos, se publican notificaciones a portal, movil y GCP.
5. La App de Conductores opera offline; el backend AWS confirma eventos al nucleo por API idempotente.
6. No existe un hub event-driven corporativo equivalente a PLT-03 de la Alternativa A.

Mensaje clave para el comite: **la Alternativa B simplifica el core con monolito modular y orquestacion, a costa de menor desacoplamiento y menor absorcion natural de picos frente a A**.

## Contenedores principales

| Contenedor | Tecnologia | Responsabilidad |
|---|---|---|
| Gateway y Gobierno API | Azure API Management (APP-01) | Contratos, OAuth/OIDC, cuotas, rate limiting y APIs mock. |
| Nucleo Logistico Modular | Azure AKS | OMS + Inventario + validacion/idempotencia. |
| Orquestador de Procesos | Azure Durable Functions | Saga orquestada y compensaciones. |
| Canal de notificaciones | Azure Service Bus topics | Fan-out informativo a consumidores. |
| Backend movil | AWS ECS/Lambda | Store-and-forward, acks, tracking y excepciones. |
| Evidencias | AWS S3 + KMS | Integridad y retencion de firmas/fotos. |
| Optimizador / analitica | GCP | Rutas dinamicas, BigQuery y modelos. |
