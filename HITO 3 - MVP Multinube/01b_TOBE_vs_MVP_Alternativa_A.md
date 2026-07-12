# TO BE, Alternativa A y MVP — Guía de alcance para el comité

**Audiencia:** Comité de Arquitectura y equipo RutaExpress  
**Paquete:** Hito 3 — MVP Multinube

> **Uso de este documento:** explica la **relación académica** entre hitos (plano → maqueta → casa entera). Para **defender** decisiones técnicas ante el comité, use AS IS, dolores (`01` §4), escenarios E1–E8 y [`06_Preguntas_Argumentos_Comite.md`](06_Preguntas_Argumentos_Comite.md) — no cite solo «porque Alternativa A / Hito 2 lo dice». **Términos técnicos:** glosario en [`00_INDICE_COMITE.md`](00_INDICE_COMITE.md) §Glosario breve.

Este documento explica la relación entre la visión TO BE (Hitos 1 y 2) y el prototipo que se implementará en el Hito 3. El mensaje central es que el MVP **sigue la dirección** de la **Alternativa A** recomendada en el Hito 2, pero **no despliega** todo su diagrama ni cierra todos los requerimientos funcionales de INI-01, INI-02 e INI-03.

> ### Marco de referencia (lectura obligatoria)
>
> | Capa | Qué es | Qué hace con los RF |
> |---|---|---|
> | **Alternativa A** | **Plano** | Diseña **cómo** se resuelven los RF en la arquitectura objetivo (Hito 2) |
> | **MVP** | **Maqueta** | Prueba **una parte** en código — que el plano funciona (Hito 3) |
> | **Producción** | **Casa entera** | Cierra el **100 %** de RF en el tiempo del roadmap (36 meses) |
>
> El Hito 3 entrega la **maqueta**, no la casa entera. Eso no invalida el **plano** (Alternativa A).

---

## 1. Resumen ejecutivo

RutaExpress avanza en tres capas académicas: el **Hito 1** define el roadmap de transformación; el **Hito 2** documenta requerimientos y diseña la arquitectura TO BE (Alternativa A recomendada); el **Hito 3** implementa un **prototipo (MVP)** que demuestra viabilidad técnica con un recorte acotado.

El MVP **reparte cargas** como el cliente hoy (hub **Azure**, última milla **AWS**, lectura **GCP** — `01` §3), usa **mocks** para sistemas legados (autorizado por el enunciado) y valida el camino crítico mediante los escenarios **E1–E8**. El roadmap completo de seis iniciativas (INI-01…INI-06) permanece en el Hito 1; cerrar todos los RF corresponde a **producción** (casa entera), no al prototipo (maqueta).

---

## 2. Conceptos clave

Cuatro niveles distintos aparecen en la documentación del proyecto. No son intercambiables.

| Concepto | Definición | Horizonte | Rol en el Hito 3 |
|---|---|---|---|
| **AS IS** | Operación actual: 26 aplicaciones, integraciones P2P, WMS on premises, liquidación en Excel | Presente | Punto de partida del caso; no se despliega |
| **TO BE (visión)** | Destino estratégico a 36 meses: seis iniciativas INI-01…INI-06, cadena de valor F1–F6 | Roadmap (Hito 1) | Guía de transformación; no es código |
| **Alternativa A** | Arquitectura objetivo del Hito 2: hub Azure, AWS móvil, GCP analítica/rutas; C4 y ADR | Diseño aprobable | El MVP **hereda** sus decisiones, no todos sus contenedores |
| **MVP (Hito 3)** | Prototipo desplegable: vertical slice, patrones, IaC, demo | Entrega académica | **Lo que se implementa** en este hito |

```text
    AS IS              TO BE (36 meses)           Alternativa A            MVP Hito 3
┌─────────────┐    ┌──────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Fragmentado │───►│ 6 INI, F1–F6     │───►│ C4 + ADR         │───►│ Slice demostrable│
│ 26 apps     │    │ programas negocio│    │ arquitectura     │    │ mocks, E1–E8    │
└─────────────┘    └──────────────────┘    │ objetivo completa│    │ ~USD 449/mes    │
                                           └──────────────────┘    └─────────────────┘
                                                    │                        │
                                                    └── misma dirección ─────┘
                                                         (distinto alcance)
```

---

## 3. Entregables por hito

### 3.1 Hito 1 — Arquitectura empresarial (entregado)

| Entregado | Fuera de alcance |
|---|---|
| Caso RutaExpress: AS IS, dolores operativos, cadena de valor F1–F6 | Código y despliegue |
| Roadmap TO BE con **seis iniciativas INI-01…INI-06** | RF detallados por iniciativa |
| Migration Planning y catálogo APP-01…APP-26, PLT-01…PLT-04 | Diseño C4 ni ADR |

Una **iniciativa (INI)** es un programa de transformación de negocio; agrupa capacidades sobre varias aplicaciones y plataformas, pero **no es** una aplicación desplegable.

### 3.2 Hito 2 — Requerimientos y diseño TO BE (entregado)

| Entregado | Fuera de alcance |
|---|---|
| RF y RNF de **INI-01, INI-02 e INI-03** (mínimo enunciado: ≥3 iniciativas) | RF detallados de INI-04, INI-05 e INI-06 |
| **Alternativa A** (hub Azure) y **Alternativa B**, cada una con C4 N1–N3 y ADR | Implementación ni prototipo |
| Recomendación de **Alternativa A** como base del primer TO BE/MVP (`02_Alternativa_A.md` §9) | Cierre del 100 % de RF en producción |

El Hito 2 responde **cómo** se abordarían los requerimientos en una arquitectura objetivo. Su producto es **diseño**, no software en ejecución.

### 3.3 Hito 3 — Prototipo / MVP (este paquete)

| Entregado / por entregar | Fuera de alcance |
|---|---|
| Prototipo basado en **Alternativa A** del Hito 2 | Réplica íntegra del C4 TO BE |
| Tres nubes: Azure (hub), AWS (móvil), GCP (proyector CQRS) | Migración de los 26 legados |
| Seis patrones: Microservicios, DDD, EDA, CQRS, Saga, Resiliencia | Cierre de todos los RF de INI-01/02/03 |
| 100 % IaC (Terraform) y costos mensuales | Escala de campaña (180.000 órdenes/día) |
| Mocks de WMS, ERP, Portal y TMS en APIM | INI-04 (rutas/ML) e INI-06 (liquidación) completos |
| Flujo crítico demostrable y escenarios **E1–E8** | App móvil ni portal como producto final |

El Hito 3 **no elige** arquitectura nueva: **implementa** la Alternativa A recortada a lo demostrable en el plazo y presupuesto académicos.

### 3.4 Exigencias del enunciado por hito

| Hito | Exige el enunciado | No exige explícitamente |
|---|---|---|
| **Hito 1** | Arquitectura empresarial, TO BE en ADM, Migration Planning | Código |
| **Hito 2** | RF de ≥3 iniciativas; dos alternativas TO BE (C4 + ADR); recomendación | MVP; RF de las seis INI; cierre total de RF |
| **Hito 3** | Prototipo del TO BE recomendado; ≥2 nubes; ≥3 patrones; 100 % IaC; costos/mes; mocks permitidos | Alternativa A completa; todos los RF; lista E1–E8 |

Fuente: [`Enunciado del Proyecto Integrador Final.md`](../Enunciado%20del%20Proyecto%20Integrador%20Final.md) — ítem «TO BE: Implementación».

### 3.5 Cadena documental

```text
Enunciado UTEC
    │
    ├─ Hito 1 ──► Roadmap INI-01…06, F1–F6, catálogo APP/PLT
    │
    ├─ Hito 2 ──► RF INI-01/02/03 + Alternativa A (recomendada) y B + C4 + ADR
    │
    └─ Hito 3 ──► MVP (Alternativa A recortada)
            ├─ 02_Dossier_MVP_Alternativa_A.md
            ├─ 03_C4_Model_MVP.md
            └─ 04_IaC_Costos_Despliegue.md
```

---

## 4. Alternativa A — arquitectura TO BE del Hito 2

Documento de referencia: `HITO 2 - .../ARQUITECTURA_SOLUCION_TO_BE/02_Alternativa_A.md`

### 4.1 Decisiones arquitectónicas (vigentes en TO BE y MVP)

| Decisión | Contenido |
|---|---|
| Hub central | **Azure** — APIM (APP-01), OMS (APP-02), inventario, **Bus de Eventos Central (PLT-03)** |
| Última milla | **AWS** — App de Conductores (APP-15), backend móvil, evidencias S3 (APP-16) |
| Analítica y rutas | **GCP** — BigQuery, optimización, ML (INI-04 en TO BE) |
| OMS | Orquestador de Pedidos (APP-02) evoluciona a OMS centralizado (ADR-002) |
| Integración | API-first, EDA, Saga, CQRS, outbox, DLQ, replay |
| Legados | WMS, ERP, Portal y TMS integrados por APIs/eventos en transición gradual |

### 4.2 Cobertura de iniciativas en el diseño

La Alternativa A **ubica** las seis iniciativas del roadmap en el diagrama C4. Solo **INI-01, INI-02 e INI-03** tienen RF documentados en el Hito 2.

| Iniciativa | RF en Hito 2 | Componentes en Alternativa A |
|---|---|---|
| **INI-01** | Sí | OMS (APP-02), Inventario y Reservas, Azure SQL, idempotencia, Saga con WMS |
| **INI-02** | Sí | APIM (APP-01), PLT-03, DLQ, replay, backpressure, contratos |
| **INI-03** | Sí | Backend móvil AWS, store-and-forward, DynamoDB, S3/KMS, excepciones |
| **INI-04** | No (roadmap Hito 1) | Optimizador dinámico GCP + TMS |
| **INI-05** | No | Observabilidad (PLT-01), identidad (PLT-02), IaC (PLT-04) |
| **INI-06** | No | Conciliación vía evidencias, tracking, ERP |

### 4.3 Diseño, MVP y producción — plano, maqueta y casa entera

En el proyecto, **resolver** un requerimiento no significa lo mismo en cada capa. Esta es la regla que ordena todo el paquete Hito 3:

| Capa | Metáfora | Entregable | Relación con los RF |
|---|---|---|---|
| **Alternativa A (Hito 2)** | **Plano** | C4, ADR, diagramas | **Diseña cómo** se resuelven los RF |
| **MVP (Hito 3)** | **Maqueta** | Código, IaC, demo E1–E8 | **Prueba una parte** — valida que el plano funciona |
| **Producción (roadmap)** | **Casa entera** | Sistemas en operación real | **Cierra el 100 %** de RF en el horizonte de 36 meses |

```text
Hito 2 — Alternativa A     →  PLANO   →  «Así se resolverían los RF en arquitectura»
Hito 3 — MVP               →  MAQUETA →  «Así demostramos que el plano funciona»
Producción (36 meses)      →  CASA    →  «Así cerramos todos los RF»
```

| Capa | ¿Incluye código? | ¿Cierra RF al 100 %? |
|---|---|---|
| Alternativa A | No | No — solo diseño |
| MVP | Sí (recortado) | No — solo núcleo demostrable |
| Producción | Sí (completo) | Sí — meta del programa INI |

El cuadro comparativo del Hito 2 (puntaje 5/5 en INI-01/02/03) evalúa si el **plano** es adecuado frente a la Alternativa B. **No** significa que la casa ya esté construida.

### 4.4 Ejemplos: mismo RF en diseño, MVP y post-MVP

| RF / capacidad | Alternativa A (diseño Hito 2) | MVP (Hito 3) | Post-MVP / producción |
|---|---|---|---|
| **INI-01 — no duplicar órdenes** (idempotencia) | OMS (APP-02) + idempotency-key + dedup en Azure SQL | Implementado; escenarios **E1**, **E2** | Escala campaña 180k/día, todos los canales de ingreso |
| **INI-01 — reserva y Saga con WMS** | Saga orden → inventario → mock/real WMS; compensación | Implementado con **mock WMS**; **E3**, **E4** | WMS on premises real, conciliación ERP plena |
| **INI-02 — DLQ y replay** | PLT-03: Service Bus DLQ + Replay Controller en AKS | Implementado; escenario **E5** | Priorización por SLA de cliente (RF-08) |
| **INI-03 — entrega offline** | Backend AWS, store-and-forward, DynamoDB outbox | Implementado; escenario **E6** | App móvil producto, GPS cada 2 min (RF-12) |
| **INI-03 — evidencias inmutables** | S3 + KMS, hash, APP-16 | Implementado; escenario **E7** | Integración conciliación INI-06 |

Un RF puede estar **cubierto en el plano (Alternativa A)** y aun así **no estar en la maqueta (MVP)**. Eso no invalida el diseño: el plano indica cómo se haría; la maqueta muestra una parte verificable en el plazo académico. El cierre total queda en **producción (casa entera)**.

### 4.5 Alcance del diseño de Alternativa A en INI-01, INI-02 e INI-03

**Sí:** la Alternativa A incluye diseño arquitectónico para las **tres iniciativas** con RF documentados en el Hito 2. No es solo una mención en el roadmap: tiene **componentes, patrones, C4 y trazabilidad** por iniciativa.

| Iniciativa | Qué incluye el diseño de Alternativa A | Dónde está detallado |
|---|---|---|
| **INI-01** | OMS (APP-02), Inventario y Reservas, Azure SQL, idempotencia, deduplicación, Saga, conciliación WMS/ERP | `02_Alternativa_A.md` §5; C4 N2/N3; carpetas `INI-01_.../diseño/` y microservicios OMS e inventario |
| **INI-02** | APIM (APP-01), PLT-03 (Event Hubs + Service Bus), DLQ, replay, backpressure, contratos canónicos | `02_Alternativa_A.md` §5; C4 N3 PLT-03; carpeta `INI-02_.../diseño/` |
| **INI-03** | Backend móvil AWS, store-and-forward, DynamoDB, S3/KMS, ACKs, taxonomía de excepciones | `02_Alternativa_A.md` §5; C4 N3 móvil; carpeta `INI-03_.../diseño/` |

**Nivel de detalle:** el diseño cubre cada **iniciativa completa** a nivel de contenedores, patrones y flujos principales. La trazabilidad **RF individual → componente** está distribuida en los documentos de cada INI (requerimientos, historias Gherkin, microservicios), no repetida fila por fila en el PDF principal de Alternativa A.

| Afirmación | Verdad |
|---|---|
| Alternativa A diseña INI-01, INI-02 e INI-03 | **Sí** — el **plano** TO BE cubre las tres iniciativas |
| Alternativa A implementa todos los RF en código | **No** — eso corresponde a **maqueta** (MVP, parcial) y **casa entera** (producción) |
| Cada RF-01…RF-12 tiene su propio diagrama N3 en Alternativa A | **No siempre** — algunos RF se cubren por **patrón transversal** (p. ej. idempotencia en OMS) o quedan en docs de INI |
| El MVP debe implementar todo lo diseñado en Alternativa A | **No** — la **maqueta** solo cubre el núcleo E1–E8; el **plano** sigue vigente para fases siguientes |

### 4.6 Grado de cobertura de requerimientos

La Alternativa A define **dónde y cómo** se resolverían los RF en producción. Ni el diseño TO BE ni el MVP posterior cierran el catálogo completo de requerimientos.

| Iniciativa | Alcance RF (Hito 2) | Capacidades diseñadas en TO BE no incluidas en el MVP |
|---|---|---|
| **INI-01** | RF-01…RF-12 + RNF | Validación dirección (RF-02), priorización SLA campaña (RF-11), carga masiva CSV (RF-01), escala 180k/día (RNF-04) |
| **INI-02** | RF-01…RF-12 + RNF | Priorización eventos por SLA (RF-08), tableros operativos (RF-10), convivencia P2P (RF-12) |
| **INI-03** | RF-01…RF-13 + RNF | GPS cada 2 min (RF-12), reintentos/devoluciones automáticos (RF-08), acciones preventivas (RF-13), portal/CRM real (RF-09) |

El cuadro comparativo A vs B del Hito 2 evalúa **idoneidad arquitectónica** entre alternativas; no certifica implementación completa de RF.

### 4.7 Nivel de resolución por capa

| Capa | INI-01 | INI-02 | INI-03 |
|---|---|---|---|
| **Hito 1** | Define el programa de transformación | Igual | Igual |
| **Hito 2 — Alternativa A** | Diseña componentes, patrones y flujos | Diseña | Diseña |
| **Hito 3 — MVP** | Demuestra núcleo parcial (E1–E4) | Demuestra núcleo parcial (E5, E8; backpressure en E4) | Demuestra núcleo parcial (E6–E7) |

---

## 5. Alcance del MVP — qué se implementa en el Hito 3

### 5.1 Flujo crítico

```text
Cliente B2B → APIM → OMS (APP-02) → Bus → Inventario (MS-INI01-02) → mock WMS
Conductor → backend AWS → evidencia S3 → puente → Bus → proyector GCP → mock-portal (tracking)
```

Detalle operativo: [`02_Dossier_MVP_Alternativa_A.md`](02_Dossier_MVP_Alternativa_A.md) §2.

### 5.2 Contenedores: Alternativa A vs MVP

| Capacidad (Alternativa A) | MVP Hito 3 |
|---|---|
| Azure API Management (APP-01) | Sí — entrada real + mocks legados |
| Orquestador de Pedidos (APP-02) en AKS | Sí — núcleo transaccional |
| Microservicio Inventario (MS-INI01-02) | Sí |
| Bus de Eventos Central (PLT-03) | Sí — AKS + Event Hubs + Service Bus |
| Azure SQL, Redis, Key Vault | Sí |
| Backend móvil AWS, DynamoDB, S3 | Sí |
| Cloud Run + BigQuery (proyector CQRS) | Sí — mínimo para tracking (E8) |
| Optimizador GCP (APP-12 / APP-24) | No — INI-04 |
| Pub/Sub, Dataflow, Vertex AI plenos | No — MVP usa Event Hubs → Cloud Run |
| WMS, ERP, Portal, TMS reales | No — mocks en APIM |
| Liquidación (INI-06) | No |
| Observabilidad / seguridad plena (INI-05) | Parcial — OTel y paneles básicos |
| 180.000 órdenes/día | No — smoke test de volumen reducido |

### 5.3 Iniciativas en el MVP

| Iniciativa | Cobertura en MVP | Límite explícito |
|---|---|---|
| **INI-01** | Núcleo: orden, deduplicación, reserva, Saga con mock WMS (E1–E4) | No implementa los 12 RF + RNF completos |
| **INI-02** | Núcleo: APIM, bus, outbox, DLQ, replay (E5, E8); backpressure en E4 | No incluye catálogo API de todos los dominios ni priorización SLA plena |
| **INI-03** | Núcleo: offline, ACK, evidencias, taxonomía de excepciones | No es app móvil producto; sin GPS 2 min ni ML de excepciones |

### 5.4 Decisiones de alcance sujetas a validación del comité

| Decisión | Justificación |
|---|---|
| Alcance parcial de INI-01, INI-02 e INI-03 | Prototipo académico sin migrar 26 sistemas legados |
| Mocks de WMS, ERP, Portal y TMS | Autorizado por enunciado; valida integración por contrato |
| GCP = proyector CQRS únicamente | INI-04 diferido; tracking E8 vía BigQuery |
| Componentes en post-MVP (dossier §2.2) | Pub/Sub pleno, escala campaña, liquidación INI-06, observabilidad plena INI-05 |

**Regla de recorte:** todo contenedor del C4 Hito 2 innecesario para demostrar E1–E8 dentro del presupuesto demo pasa a post-MVP o se sustituye por mock. Permanece en el TO BE; solo se excluye del prototipo.

---

## 6. Criterios de aceptación E1–E8

El enunciado del Hito 3 no define escenarios de prueba concretos. El equipo estableció **ocho escenarios** como Definition of Done del prototipo: cubren el flujo crítico, trazan a RF de INI-01/02/03 y dolores del Hito 1, y alimentan los smoke tests del pipeline IaC (`04_IaC_Costos_Despliegue.md`).

| # | Escenario | Trazabilidad |
|---|---|---|
| **E1** | Orden válida con idempotency-key | INI-01 — duplicados |
| **E2** | Mismo hash logístico sin duplicar orden | INI-01 — RF-03 |
| **E3** | Inventario insuficiente y compensación Saga | INI-01 — Saga |
| **E4** | Mock WMS 503 y circuit breaker | INI-01 Saga (+ backpressure INI-02) |
| **E5** | DLQ y replay auditado | INI-02 |
| **E6** | Entrega offline y sincronización | INI-03 |
| **E7** | Evidencia con hash inválido rechazada | INI-03 — APP-16 |
| **E8** | Tracking CQRS coherente entre evento y consulta | INI-02 + CQRS |

Detalle completo: [`02_Dossier_MVP_Alternativa_A.md`](02_Dossier_MVP_Alternativa_A.md) §6.

---

## 7. Documentación del paquete Hito 3

| Documento | Rol | Deriva de |
|---|---|---|
| `02_Dossier_MVP_Alternativa_A.md` | Alcance, patrones, mocks, decisiones post-MVP | Dolores + AS IS + enunciado Hito 3 |
| `03_C4_Model_MVP.md` | C4 del implementable (no copia literal del Hito 2) | Dossier §1.3, recortado a E1–E8 |
| `04_IaC_Costos_Despliegue.md` | Terraform multinube y FinOps (~USD 449/mes) | Stack del dossier §1.3 |
| `01b_TOBE_vs_MVP_Alternativa_A.md` (este doc) | Marco plano / maqueta / casa entera | Síntesis Hitos 1–3 |
| `06_Preguntas_Argumentos_Comite.md` | Defensa oral — argumentos no circulares | Dolores, AS IS, comparativas técnicas |
| `00_INDICE_COMITE.md` | Índice y cumplimiento enunciado | Punto de entrada del paquete |

### Derivación del alcance del dossier

El dossier MVP se construyó aplicando, en orden: (1) **dolores y AS IS** del caso RutaExpress (`01`); (2) restricciones del **enunciado Hito 3**; (3) recorte a vertical slice multinube con mocks; (4) definición de **E1–E8** como criterios verificables; (5) **coherencia** con el diseño TO BE (Alternativa A del Hito 2) como plano de referencia — no como único motivo de cada decisión técnica. Detalle de stack: Event Hubs + Service Bus, workloads core en AKS, Fargate en AWS, Cloud Run en GCP.

---

## 8. Comparativa diseño vs implementación

| Dimensión | Alternativa A (Hito 2) | MVP (Hito 3) |
|---|---|---|
| **Propósito** | Arquitectura objetivo recomendada | Prototipo demostrable |
| **Producto** | C4, ADR, decisiones | Código, IaC, demo |
| **Iniciativas** | Ubica INI-01…06 en diagrama; RF detallados en INI-01/02/03 | Núcleo parcial demostrable de INI-01/02/03 |
| **Legados** | Integración real progresiva | Mocks en APIM |
| **GCP** | Rutas, analítica, ML (INI-04) | Solo proyector CQRS + BigQuery |
| **Escala** | Diseño para campaña 180k órdenes/día | Smoke test de volumen reducido |
| **Diagrama C4** | `alternativa_A_n1/n2/n3` | `mvp_c4_n*` |
| **Criterio de éxito** | Aprobación del diseño TO BE | E1–E8 + cumplimiento enunciado Hito 3 |

El C4 del Hito 3 **no debe replicar** el del Hito 2: elimina contenedores no desplegados, incorpora mocks y detalla solo lo implementable. El enunciado autoriza mocks; la demo valida contratos de integración, no la migración on premises completa.

---

## 9. Referencias

| Documento | Ubicación |
|---|---|
| Enunciado oficial | [`Enunciado del Proyecto Integrador Final.md`](../Enunciado%20del%20Proyecto%20Integrador%20Final.md) |
| Alternativa A | [`02_Alternativa_A.md`](../HITO%202%20-%20Requerimientos%20Y%20Diseño%20de%20Arquitectura%20de%20Solución/ARQUITECTURA_SOLUCION_TO_BE/02_Alternativa_A.md) |
| Cuadro comparativo A vs B | [`cuadro_comparativo_recomendacion.md`](../HITO%202%20-%20Requerimientos%20Y%20Diseño%20de%20Arquitectura%20de%20Solución/ARQUITECTURA_SOLUCION_TO_BE/cuadro_comparativo_recomendacion.md) |
| RF INI-01 / 02 / 03 | `HITO 2 - .../INI-*/01_Requerimientos_y_Criterios_Aceptacion.md` |
| Dossier MVP | [`02_Dossier_MVP_Alternativa_A.md`](02_Dossier_MVP_Alternativa_A.md) |
| C4 del MVP | [`03_C4_Model_MVP.md`](03_C4_Model_MVP.md) |

---

*RutaExpress — Guía de alcance TO BE vs MVP — UTEC Arquitectura Multinube*
