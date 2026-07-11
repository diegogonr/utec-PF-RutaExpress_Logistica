# Cuadro comparativo y recomendacion

## Criterios de evaluacion

Escala: 1 = bajo cumplimiento, 5 = alto cumplimiento.

| Criterio | Alternativa A: Azure hub central | Alternativa B: AWS hub principal | Evaluacion |
|---|---:|---:|---|
| Alineamiento con Hito 1 | 5 | 3 | A mantiene OMS/API/TMS/eventos en el eje Azure ya descrito y conserva AWS/GCP en sus dominios actuales. |
| Cobertura RF/RNF INI-01 | 5 | 4 | Ambas cubren OMS e inventario, pero A reduce puentes entre OMS, API governance y bus. |
| Cobertura RF/RNF INI-02 | 5 | 4 | A concentra contratos, eventos, DLQ, replay y observabilidad operacional en un mismo plano de gobierno. |
| Cobertura RF/RNF INI-03 | 5 | 5 | Ambas mantienen AWS para app movil, store-and-forward y evidencias. |
| Complejidad de integracion | 4 | 3 | A requiere bridges AWS/GCP; B requiere puente permanente Azure OMS -> AWS hub y doble gobierno API/eventos. |
| Costo estimado relativo | 4 | 3 | A usa servicios administrados intermedios y evita duplicar gobierno; B aumenta transferencia y operacion cruzada. |
| Seguridad | 5 | 4 | A centraliza identidad, API governance y secretos con integracion federada; B reparte mas controles entre nubes. |
| Observabilidad | 5 | 4 | A facilita trazas end-to-end desde OMS/eventos; B necesita federacion mas intensa CloudWatch/Azure/GCP. |
| Resiliencia | 5 | 5 | Ambas soportan DLQ, retry, backpressure, outbox y store-and-forward. |
| Escalabilidad | 5 | 5 | Ambas soportan picos de 180,000 ordenes y eventos de tracking con colas y particiones. |
| Impacto en aplicaciones existentes | 5 | 4 | A evoluciona APP-02 y fortalece APP-15/APP-16 sin mover el hub hacia otra nube. |
| Riesgo de migracion | 4 | 3 | A minimiza cambios de topologia; B cambia el centro operativo de eventos hacia AWS. |
| Facilidad de MVP con API mock | 5 | 4 | A permite publicar mocks y contratos desde Azure API Management junto al OMS. |
| Gobierno FinOps | 4 | 3 | A tiene menor dispersion de costos de transferencia y operacion entre planos de control. |

## Puntaje

| Alternativa | Puntaje total | Resultado |
|---|---:|---|
| Alternativa A | 66 / 70 | Recomendada |
| Alternativa B | 54 / 70 | Viable, no recomendada para el primer TO BE |

## Recomendacion

La alternativa recomendada es la Alternativa A: Azure como hub central de integracion y gobierno, AWS para ultima milla/evidencias y GCP para analitica/rutas.

Esta decision es la mas consistente con el Hito 1 porque APP-02 evoluciona a OMS centralizado sin crear una aplicacion independiente, TMS permanece alineado a Azure, APP-15 y APP-16 conservan su ubicacion natural en AWS, y GCP se mantiene como plataforma de optimizacion y analitica. Tambien reduce el riesgo de que las integraciones API-first y event-driven queden repartidas en dos planos de gobierno durante el MVP.

## Implicancias para implementacion

- Priorizar un MVP con Azure API Management, OMS en AKS, Azure SQL, Event Hubs/Service Bus, backend movil AWS, S3, DynamoDB y un primer puente hacia GCP.
- Mantener adaptadores transicionales hacia WMS Principal (APP-06), WMS Satelite (APP-07) y ERP Financiero (APP-25).
- Implementar primero los casos criticos: orden valida, duplicado/idempotencia, reserva, WMS degradado, DLQ/replay, entrega offline, evidencia corrupta y excepcion de ultima milla.
- Medir desde el inicio: correlation ID, backlog, DLQ, tracking tardio, evidencias pendientes, conflictos de inventario y SLA.
