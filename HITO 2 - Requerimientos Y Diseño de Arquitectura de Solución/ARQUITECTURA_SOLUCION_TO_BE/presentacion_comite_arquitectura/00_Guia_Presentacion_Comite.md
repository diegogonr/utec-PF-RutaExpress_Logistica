# Guia de presentacion para Comite de Arquitectura

## Proposito

Este paquete organiza la presentacion de las dos alternativas TO BE de RutaExpress como **modelos completos e independientes**. Cada modelo se expone con su propia narrativa, sus tres niveles C4 y su evaluacion tecnica. La comparacion se realiza despues de presentar ambos modelos, para evitar que una alternativa sea entendida solo como variacion de la otra.

## Entregables incluidos

| Orden | Archivo | Objetivo |
|---:|---|---|
| 1 | `00_Guia_Presentacion_Comite.md` | Explicar el orden recomendado de exposicion y el mensaje de decision. |
| 2 | `01_Modelo_A_Azure_Hub_Central.md` | Presentar el Modelo A como arquitectura completa: Azure como hub central de integracion y gobierno. |
| 3 | `02_Modelo_B_Orquestacion_Monolito_Modular.md` | Presentar el Modelo B como arquitectura completa: orquestacion + monolito modular (estilo distinto a A). |
| 4 | `03_Comparativo_ADR_Recomendacion.md` | Comparar ambos modelos, resumir ADRs clave y proponer la decision recomendada. |

## Fuente de diagramas

Todos los diagramas embebidos en estos entregables usan las imagenes generadas en:

- Modelo A: `../diagramas_c4/imagenes_python_graphviz`
- Modelo B: `../diagramas_c4/imagenes_alternativa_B` (generadas con `generar_diagramas_alternativa_B_c4.py`, estilo Hito 3)

| Modelo | Nivel C4 | Imagen utilizada |
|---|---|---|
| A | Nivel 1 Contexto | `alternativa_A_n1_contexto.png` |
| A | Nivel 2 Contenedores | `alternativa_A_n2_contenedores.png` |
| A | Nivel 3 PLT-03 / OMS / Inventario / Móvil | `alternativa_A_n3_*.png` (4 imágenes) |
| B | Nivel 1 Contexto | `imagenes_alternativa_B/alternativa_B_c4_n1_contexto.png` |
| B | Nivel 2 Contenedores | `imagenes_alternativa_B/alternativa_B_c4_n2_contenedores.png` |
| B | Nivel 3 Orquestador / OMS / Inventario / Móvil | `imagenes_alternativa_B/alternativa_B_c4_n3_*_componentes.png` (4 imágenes) |

## Orden recomendado para la sesion

### 1. Apertura ejecutiva

Duracion sugerida: 5 minutos.

Objetivo:

- Recordar la casuistica de RutaExpress: duplicidad de pedidos, inconsistencias de inventario, integraciones punto a punto, ultima milla offline con perdida de evidencias, baja trazabilidad y conciliacion manual.
- Presentar el objetivo TO BE: OMS centralizado, integracion API-first/event-driven, observabilidad end-to-end, resiliencia operativa, seguridad y gobierno multinube.
- Aclarar que se evaluan dos modelos completos de arquitectura.

Mensaje sugerido:

> "El objetivo de esta sesion no es revisar componentes aislados, sino decidir que estilo de arquitectura habilita mejor el primer TO BE de RutaExpress, con menor riesgo y mayor trazabilidad."

### 2. Modelo A completo

Duracion sugerida: 18 a 22 minutos.

Secuencia:

1. Tesis del modelo: Azure como hub central de integracion y gobierno.
2. C4 Nivel 1 Contexto.
3. C4 Nivel 2 Contenedores.
4. C4 Nivel 3 Componentes del Bus de Eventos Central (PLT-03) en Azure.
5. Flujo de negocio explicado sobre el modelo.
6. Fortalezas, riesgos y controles.

Decision que debe evaluar el comite:

- Si acepta centralizar APIs, OMS centralizado / Orquestador de Pedidos (APP-02), eventos, colas, observabilidad e identidad principalmente en Azure.
- Si acepta mantener AWS como dominio de ultima milla/evidencias y GCP como dominio de optimizacion/analitica.

### 3. Modelo B completo

Duracion sugerida: 18 a 22 minutos.

Secuencia:

1. Tesis del modelo: orquestacion + monolito modular (estilo distinto a EDA).
2. C4 Nivel 1 Contexto.
3. C4 Nivel 2 Contenedores.
4. C4 Nivel 3 (4 diagramas): Orquestador/notificaciones, modulo OMS, modulo Inventario, backend movil.
5. Flujo de negocio explicado sobre el modelo.
6. Fortalezas, riesgos y controles.

Decision que debe evaluar el comite:

- Si acepta concentrar OMS + Inventario en un monolito modular orquestado.
- Si acepta cubrir INI-02 con API-first fuerte y eventos solo como notificacion (sin PLT-03 completo).

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
- Bus de Eventos Central (PLT-03) opera como hub de integración.
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
- Mantener el **Modelo B** como alternativa de contraste (orquestacion + monolito modular) cuando se priorice simplicidad y time-to-MVP del core.

## Criterio de exposicion

La presentacion debe evitar comparar cada lamina de A contra B. La regla recomendada es:

1. Presentar Modelo A completo.
2. Presentar Modelo B completo.
3. Comparar ambos modelos al final.

Esto permite que el comite evalue cada alternativa con justicia y entienda que A y B difieren por estilo arquitectonico (microservicios + PLT-03 vs orquestacion Durable Functions + monolito modular), no solo por proveedor de nube.

## Resultado esperado del comite

Al finalizar la sesion, el comite deberia poder decidir:

- Que modelo sera la arquitectura base para el TO BE.
- Que riesgos deben quedar como condiciones de aprobacion.
- Que ADRs se aprueban formalmente.
- Que componentes deben entrar al MVP.
- Que controles de seguridad, observabilidad y FinOps deben implementarse desde el inicio.
