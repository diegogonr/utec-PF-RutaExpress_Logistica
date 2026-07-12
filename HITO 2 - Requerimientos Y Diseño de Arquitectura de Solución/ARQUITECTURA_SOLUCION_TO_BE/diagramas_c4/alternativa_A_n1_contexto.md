# Alternativa A - C4 Nivel 1 Contexto

## Proposito

Diagrama de contexto C4 para la Alternativa A. Este nivel muestra un unico sistema de software en alcance, sus personas usuarias y los sistemas externos con los que interactua.

> Regla aplicada: en C4 Contexto no se muestran contenedores internos, tecnologias ni componentes. La decision de Azure como hub central se documenta como nota de alternativa y se desarrolla en el Nivel 2.

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
        WMS Principal (On Premises) (APP-06)["WMS Principal / WMS Satelite<br/>APP-06 / APP-07"]
        TMS (Transportation Management) (APP-11)["TMS (Transportation Management) (APP-11) Transportation Management<br/>APP-11"]
        ERP Financiero (On Premises) (APP-25)["ERP Financiero On Premises<br/>APP-25"]
        PORTAL["Portal B2B / CRM<br/>APP-18 / APP-20"]
        SAAS["Clientes SaaS y canales legados<br/>CSV / Excel / S3"]
        MAPAS["Servicios de trafico, mapas y geocodificacion"]
    end

    CLIENTE -->|"crea ordenes / consulta estado"| SISTEMA
    CONDUCTOR -->|"entregas, tracking y evidencias"| SISTEMA
    OPERADOR -->|"monitoreo y gestion operativa"| SISTEMA
    FINANZAS -->|"consulta soportes de liquidacion"| SISTEMA

    SISTEMA -->|"consulta y concilia inventario"| WMS Principal (On Premises) (APP-06)
    SISTEMA -->|"sincroniza despacho, rutas y entregas"| TMS (Transportation Management) (APP-11)
    SISTEMA -->|"envia valorizacion, estados y evidencias"| ERP Financiero (On Premises) (APP-25)
    SISTEMA -->|"publica trazabilidad e incidencias"| PORTAL
    SISTEMA -->|"recibe ordenes e intercambios transicionales"| SAAS
    SISTEMA -->|"consulta trafico, zonas y tiempos estimados"| MAPAS
```

## Como leer este diagrama para el comite

Este diagrama responde a la pregunta: **que sistema estamos cambiando y con quienes se relaciona**. No busca explicar tecnologia interna, sino delimitar alcance, usuarios y dependencias externas.

| Elemento | Como interpretarlo |
|---|---|
| Cajas verdes de Personas | Roles que usan o dependen de la plataforma: clientes, conductores, operacion y finanzas. |
| Caja central | Sistema en alcance: la Plataforma Logistica RutaExpress TO BE. Todo lo que se disena en Hito 2 vive dentro de esta caja, aunque en niveles posteriores se despliegue en varias nubes. |
| Cajas de Sistemas externos | Sistemas que interactuan con RutaExpress pero no son el foco del diseno C4 en este nivel: WMS Principal (On Premises) (APP-06), TMS (Transportation Management) (APP-11), ERP Financiero (On Premises) (APP-25), Portal/CRM, canales legados y servicios de mapas. |
| Flechas | Relaciones funcionales entre actores, sistema central y externos. No representan aun protocolos, APIs, colas ni tecnologias especificas. |

Flujo para explicar:

1. Los clientes B2B envian ordenes y consultan trazabilidad a traves de la plataforma.
2. Los conductores registran entregas, tracking y evidencias desde la operacion de ultima milla.
3. Operacion supervisa inventario, rutas, pedidos y SLA; finanzas usa estados y evidencias para conciliacion.
4. La plataforma se integra con WMS Principal (On Premises) (APP-06), TMS (Transportation Management) (APP-11), ERP Financiero (On Premises) (APP-25), Portal/CRM y canales legados para completar el ciclo logistico end-to-end.
5. En esta alternativa, el detalle tecnologico se explica en el Nivel 2: Azure sera el centro de gobierno e integracion, AWS soportara ultima milla/evidencias y GCP optimizacion/analitica.

Mensaje clave para el comite: **el alcance no es una aplicacion aislada, sino la plataforma logistica que coordina orden, inventario, despacho, ultima milla, evidencias y trazabilidad con sistemas existentes**.

## Lectura C4

| Elemento C4 | Representacion |
|---|---|
| Sistema en alcance | Plataforma Logistica RutaExpress TO BE. |
| Personas | Cliente B2B/Retail, Conductor, Operacion RutaExpress y Finanzas. |
| Sistemas externos | WMS Principal (On Premises) (APP-06), TMS (Transportation Management) (APP-11), ERP Financiero (On Premises) (APP-25), Portal/CRM, canales legados y servicios de mapas/trafico. |
| Diferencia de alternativa | La distribucion tecnologica se detalla en el Nivel 2: Azure como hub central de gobierno e integracion. |

## Trazabilidad

- INI-01: ordenes, inventario, reservas y conciliacion.
- INI-02: APIs, eventos, contratos, DLQ, replay y backpressure.
- INI-03: ultima milla offline, evidencias, tracking y excepciones.
