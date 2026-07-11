# Guia de presentacion para Comite de Arquitectura

## Proposito

Este paquete organiza la presentacion de las dos alternativas TO BE de RutaExpress como **modelos completos e independientes**. Cada modelo se expone con su propia narrativa, sus tres niveles C4 y su evaluacion tecnica. La comparacion se realiza despues de presentar ambos modelos, para evitar que una alternativa sea entendida solo como variacion de la otra.

## Entregables incluidos

| Orden | Archivo | Objetivo |
|---:|---|---|
| 1 | `00_Guia_Presentacion_Comite.md` | Explicar el orden recomendado de exposicion y el mensaje de decision. |
| 2 | `01_Modelo_A_Azure_Hub_Central.md` | Presentar el Modelo A como arquitectura completa: Azure como hub central de integracion y gobierno. |
| 3 | `02_Modelo_B_AWS_Hub_Eventos.md` | Presentar el Modelo B como arquitectura completa: AWS como hub principal de eventos y ultima milla. |
| 4 | `03_Comparativo_ADR_Recomendacion.md` | Comparar ambos modelos, resumir ADRs clave y proponer la decision recomendada. |

## Fuente de diagramas

Todos los diagramas embebidos en estos entregables usan las imagenes generadas en:

`../diagramas_c4/imagenes_python_graphviz`

| Modelo | Nivel C4 | Imagen utilizada |
|---|---|---|
| A | Nivel 1 Contexto | `alternativa_A_n1_contexto.png` |
| A | Nivel 2 Contenedores | `alternativa_A_n2_contenedores.png` |
| A | Nivel 3 Componentes | `alternativa_A_n3_componentes.png` |
| B | Nivel 1 Contexto | `alternativa_B_n1_contexto.png` |
| B | Nivel 2 Contenedores | `alternativa_B_n2_contenedores.png` |
| B | Nivel 3 Componentes | `alternativa_B_n3_componentes.png` |

## Orden recomendado para la sesion

### 1. Apertura ejecutiva

Duracion sugerida: 5 minutos.

Objetivo:

- Recordar la casuistica de RutaExpress: duplicidad de pedidos, inconsistencias de inventario, integraciones punto a punto, ultima milla offline con perdida de evidencias, baja trazabilidad y conciliacion manual.
- Presentar el objetivo TO BE: OMS centralizado, integracion API-first/event-driven, observabilidad end-to-end, resiliencia operativa, seguridad y gobierno multinube.
- Aclarar que se evaluan dos modelos completos de arquitectura.

Mensaje sugerido:

> "El objetivo de esta sesion no es revisar componentes aislados, sino decidir que topologia de arquitectura habilita mejor el primer TO BE de RutaExpress, con menor riesgo y mayor trazabilidad."

### 2. Modelo A completo

Duracion sugerida: 18 a 22 minutos.

Secuencia:

1. Tesis del modelo: Azure como hub central de integracion y gobierno.
2. C4 Nivel 1 Contexto.
3. C4 Nivel 2 Contenedores.
4. C4 Nivel 3 Componentes del PLT-03 en Azure.
5. Flujo de negocio explicado sobre el modelo.
6. Fortalezas, riesgos y controles.

Decision que debe evaluar el comite:

- Si acepta centralizar APIs, OMS, eventos, colas, observabilidad e identidad principalmente en Azure.
- Si acepta mantener AWS como dominio de ultima milla/evidencias y GCP como dominio de optimizacion/analitica.

### 3. Modelo B completo

Duracion sugerida: 18 a 22 minutos.

Secuencia:

1. Tesis del modelo: AWS como hub principal de eventos y ultima milla.
2. C4 Nivel 1 Contexto.
3. C4 Nivel 2 Contenedores.
4. C4 Nivel 3 Componentes del PLT-03 en AWS.
5. Flujo de negocio explicado sobre el modelo.
6. Fortalezas, riesgos y controles.

Decision que debe evaluar el comite:

- Si acepta desplazar el hub principal de eventos hacia AWS.
- Si acepta operar un puente permanente Azure-AWS entre OMS/API governance y eventos corporativos.

### 4. Comparativo ejecutivo

Duracion sugerida: 10 minutos.

Evaluar:

- Alineamiento con Hito 1.
- Cobertura de RF/RNF.
- Complejidad de integracion.
- Seguridad y observabilidad.
- Resiliencia.
- Impacto en aplicaciones existentes.
- Riesgo de migracion.
- Facilidad de MVP.
- Gobierno FinOps.

### 5. ADRs clave

Duracion sugerida: 8 minutos.

No se recomienda presentar todos los ADR en detalle. Se deben destacar solo las decisiones que condicionan la topologia:

- APP-02 evoluciona a OMS centralizado.
- PLT-03 opera como hub de eventos.
- Gobierno API centralizado.
- DLQ, replay, retry, backpressure e idempotencia.
- Observabilidad end-to-end con correlation ID.
- Seguridad federada y gestion central de secretos.
- AWS se conserva para app movil y evidencias.
- GCP se conserva para optimizacion y analitica.

### 6. Recomendacion y decision solicitada

Duracion sugerida: 5 minutos.

Decision propuesta:

- Aprobar el **Modelo A** como base del primer TO BE/MVP.
- Mantener el **Modelo B** como alternativa viable para un escenario donde la organizacion decida priorizar AWS como plataforma dominante de eventos y ultima milla.

## Criterio de exposicion

La presentacion debe evitar comparar cada lamina de A contra B. La regla recomendada es:

1. Presentar Modelo A completo.
2. Presentar Modelo B completo.
3. Comparar ambos modelos al final.

Esto permite que el comite evalue cada alternativa con justicia, entienda sus implicancias de gobierno y no confunda diferencias de topologia con diferencias funcionales.

## Resultado esperado del comite

Al finalizar la sesion, el comite deberia poder decidir:

- Que modelo sera la arquitectura base para el TO BE.
- Que riesgos deben quedar como condiciones de aprobacion.
- Que ADRs se aprueban formalmente.
- Que componentes deben entrar al MVP.
- Que controles de seguridad, observabilidad y FinOps deben implementarse desde el inicio.
