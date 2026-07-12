# Secuencia INI-02 - API-first, eventos y resiliencia

## Trazabilidad

- RF cubiertos: RF-01 a RF-12 de INI-02.
- Historias cubiertas: `HU-INI02-RF01` a `HU-INI02-RF12`.
- Escenarios clave: contrato API, publicacion de evento, validacion de esquema, DLQ, backpressure, replay y evento fuera de orden.

## Diagrama Mermaid

```mermaid
sequenceDiagram
    autonumber
    participant Productor as OMS/WMS/TMS/App/ERP
    participant APIGW as Gobierno API
    participant Registry as Registro Contratos
    participant BUS as Bus de Eventos Central (PLT-03)
    participant Consumer as Consumidor de Dominio
    participant DLQ as Dead Letter Queue
    participant Replay as Consola Replay
    participant OBS as Observabilidad (PLT-01)

    Productor->>APIGW: Publicar contrato API/evento
    APIGW->>Registry: Validar version y compatibilidad
    alt Contrato compatible
        Registry-->>APIGW: Contrato publicado
        APIGW-->>Productor: Version activa
    else Contrato rompe compatibilidad
        Registry-->>APIGW: Requiere nueva version
        APIGW-->>Productor: Rechazo gobernado
    end

    Productor->>BUS: EventEnvelope + schemaVersion + correlationId
    BUS->>Registry: Validar esquema y productor
    alt Evento valido
        BUS->>Consumer: Entregar evento por aggregateId
        alt Procesamiento exitoso
            Consumer-->>BUS: Ack
            BUS->>OBS: Metrica de entrega exitosa
        else Consumidor falla
            Consumer--xBUS: Error o timeout
            BUS->>BUS: Retry con backoff + jitter
            alt Reintentos agotados
                BUS->>DLQ: Guardar payload, error y consumidor
                BUS->>OBS: Alerta DLQ
            end
        end
    else Esquema invalido
        Registry-->>BUS: Error de contrato
        BUS->>DLQ: Mensaje no procesable
        BUS->>OBS: Alerta evento invalido
    end

    opt Backpressure por degradacion
        Consumer--xBUS: Latencia alta / backlog
        BUS->>APIGW: Reducir tasa de productores no criticos
        APIGW-->>Productor: 429 / throttling controlado
        OBS->>OBS: Alerta backlog y saturacion
    end

    opt Replay y evento fuera de orden
        Replay->>BUS: Solicitud aprobada de replay
        BUS->>BUS: Leer eventos ordenados por agregado
        alt Secuencia completa
            BUS->>Consumer: Reemitir eventos idempotentes
        else Falta evento anterior
            BUS->>DLQ: Retener evento fuera de orden
            BUS->>OBS: Alerta secuencia incompleta
        end
    end
```

## Patrones aplicados

- API-first con OpenAPI/AsyncAPI y versionamiento.
- Event-Driven Architecture con envelopes canonicos.
- Outbox/Inbox, idempotencia, retry con backoff, backpressure y DLQ.
- Replay controlado, orden por agregado y auditoria.
