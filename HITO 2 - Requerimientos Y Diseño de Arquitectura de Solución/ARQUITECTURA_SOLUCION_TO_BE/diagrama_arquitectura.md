# Diagrama de arquitectura cloud transversal

> Maestro: [`02_Alternativa_A.md`](02_Alternativa_A.md). Imágenes C4: [`diagramas_c4/`](diagramas_c4/).

## Vista

Azure hub + AWS última milla + GCP analítica.

## Diagramas C4 Alternativa A

| Nivel | Archivo |
|---|---|
| N1 Contexto | `diagramas_c4/alternativa_A_n1_contexto.png` |
| N2 Contenedores | `diagramas_c4/alternativa_A_n2_contenedores.png` |
| N3 PLT-03 | `diagramas_c4/alternativa_A_n3_componentes.png` |
| N3 OMS / Inventario / Móvil | mismos nombres `*_oms_*`, `*_inventario_*`, `*_mobile_*` |

## Flujo canónico

```text
Cliente → APIM → OMS (APP-02) → Inventario (MS-INI01-02) HTTP
                              ├→ APIM → WMS
                              └→ Azure SQL outbox
bus-workers → SQL → Event Hubs → Service Bus → TMS / portal / GCP
mobile-api → SQS → retry-worker → EventBridge → Adaptador AWS→Azure → Event Hubs
```
