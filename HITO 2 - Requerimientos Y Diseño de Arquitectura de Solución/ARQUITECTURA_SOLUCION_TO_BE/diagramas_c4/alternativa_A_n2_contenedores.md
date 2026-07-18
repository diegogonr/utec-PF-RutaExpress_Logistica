# Alternativa A — C4 Nivel 2 Contenedores

![Contenedores](alternativa_A_n2_contenedores.png)

Azure hub: APIM → OMS (APP-02) → Inventario (MS-INI01-02) por HTTP.  
Outbox: OMS/Inventario escriben Azure SQL; **`bus-workers`** consulta y publica en **Event Hubs**.  
WMS: **OMS → APIM → WMS**.  
AWS: `mobile-api` → SQS → **`retry-worker`** → EventBridge → **Adaptador AWS→Azure** → Event Hubs.
