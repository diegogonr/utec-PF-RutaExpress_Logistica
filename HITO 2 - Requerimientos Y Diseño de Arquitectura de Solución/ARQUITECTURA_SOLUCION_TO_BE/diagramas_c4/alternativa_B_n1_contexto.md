# Alternativa B - C4 Nivel 1 Contexto

## Proposito

Diagrama de contexto C4 para la Alternativa B. Este nivel muestra un unico sistema de software en alcance, sus personas usuarias y los sistemas externos con los que interactua.

> Regla aplicada: en C4 Contexto no se muestran contenedores internos, tecnologias ni componentes. La decision de AWS como hub principal de eventos se desarrolla en el Nivel 2.

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

Este diagrama responde a la pregunta: **que sistema estamos cambiando y con quienes se relaciona**. No muestra tecnologia interna; muestra alcance, actores y dependencias externas.

| Elemento | Como interpretarlo |
|---|---|
| Cajas verdes de Personas | Roles que usan o dependen de la plataforma: clientes, conductores, operacion y finanzas. |
| Caja central | Sistema en alcance: la Plataforma Logistica RutaExpress TO BE. Representa el conjunto de capacidades del Hito 2 sin entrar todavia en contenedores o componentes. |
| Cajas de Sistemas externos | Sistemas que interactuan con RutaExpress: WMS Principal (On Premises) (APP-06), TMS (Transportation Management) (APP-11), ERP Financiero (On Premises) (APP-25), Portal/CRM, canales legados y servicios de mapas. |
| Flechas | Relaciones funcionales de negocio. No son aun APIs, eventos, colas ni decisiones de despliegue. |

Flujo para explicar:

1. Clientes y conductores son los principales puntos de entrada operativa.
2. Operacion y finanzas consumen la informacion consolidada para controlar SLA, incidencias, evidencias y conciliacion.
3. La plataforma interactua con WMS Principal (On Premises) (APP-06) para inventario, TMS (Transportation Management) (APP-11) para despacho/rutas, ERP Financiero (On Premises) (APP-25) para valorizacion/liquidacion y Portal/CRM para trazabilidad y atencion.
4. Los canales legados siguen existiendo durante la transicion, pero quedan fuera del core nuevo.
5. En esta alternativa, el detalle tecnologico se explica en el Nivel 2: AWS toma el rol principal de eventos y ultima milla; Azure conserva APIs/OMS/TMS; GCP conserva optimizacion/analitica.

Mensaje clave para el comite: **la diferencia de la Alternativa B no cambia el alcance funcional, sino el centro tecnologico de integracion y resiliencia, que se desplaza hacia AWS**.

## Lectura C4

| Elemento C4 | Representacion |
|---|---|
| Sistema en alcance | Plataforma Logistica RutaExpress TO BE. |
| Personas | Cliente B2B/Retail, Conductor, Operacion RutaExpress y Finanzas. |
| Sistemas externos | WMS Principal (On Premises) (APP-06), TMS (Transportation Management) (APP-11), ERP Financiero (On Premises) (APP-25), Portal/CRM, canales legados y servicios de mapas/trafico. |
| Diferencia de alternativa | La distribucion tecnologica se detalla en el Nivel 2: AWS como hub principal de eventos y ultima milla. |

## Trazabilidad

- INI-01: ordenes, inventario, reservas y conciliacion.
- INI-02: APIs, eventos, contratos, DLQ, replay y backpressure.
- INI-03: ultima milla offline, evidencias, tracking y excepciones.
