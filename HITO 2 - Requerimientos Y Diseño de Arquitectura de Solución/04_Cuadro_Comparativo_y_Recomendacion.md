# Cuadro Comparativo y Recomendación
## Alternativa A vs Alternativa B — RutaExpress Hito 2

> **Documentos relacionados:**  
> - [`02_Alternativa_A_Hub_Central_Azure.md`](02_Alternativa_A_Hub_Central_Azure.md)  
> - [`03_Alternativa_B_Malla_Federada_Multinube.md`](03_Alternativa_B_Malla_Federada_Multinube.md)  
> - [`01_Requerimientos_y_Criterios_Aceptacion.md`](01_Requerimientos_y_Criterios_Aceptacion.md)

> **Iniciativas evaluadas:** INI-01, INI-02, INI-03 — selección y criterios en [`01_Requerimientos_y_Criterios_Aceptacion.md` §1.1](01_Requerimientos_y_Criterios_Aceptacion.md#11-por-qué-se-eligieron-ini-01-ini-02-e-ini-03).

> **Principio rector (Hito 1 doc 10):** solo servicios nativos **Azure / AWS / GCP**, alcance **medio**, sin SaaS de observabilidad o integración de terceros (Datadog, Apicurio, Kafka autogestionado, etc.).

---

## 1. Criterios de evaluación

Los criterios se alinean con la priorización del [`11_ADM_Migration_Planning.md`](../HITO%201%20-%20Arquitectura%20Empresarial/11_ADM_Migration_Planning.md): impacto negocio, riesgo operativo, habilitación de iniciativas, time-to-value y complejidad.

Escala: **1 (bajo)** — **5 (alto)** salvo **Costo** y **Complejidad** donde **5 = más costo / más complejo**.

---

## 2. Cuadro comparativo

| Dimensión | Alternativa A — Hub Central Azure | Alternativa B — Malla Federada Multinube |
|---|---|---|
| **Alineación Hito 1 / INI-01** | ★★★★★ PLT-03 Event Hubs único — idéntico a Migration Planning | ★★★ Tres buses + enrutador no presupuestado |
| **Cumplimiento RF/RNF INI-01** | ★★★★★ Replay central nativo Event Hubs | ★★★ Replay compuesto — agregador adicional |
| **Cumplimiento RF/RNF INI-02** | ★★★★★ WMS → bus directo; latencia mínima intra-Azure | ★★★★ WMS → bus_az → enrutador → TMS |
| **Cumplimiento RF/RNF INI-03** | ★★★★★ Kinesis + conector — alineado INI-03 | ★★★★ Kinesis + EventBridge + enrutador |
| **Time-to-value (mes 1–6)** | ★★★★★ INI-01 + INI-03 en paralelo según roadmap | ★★★ Enrutador 4–6 meses antes de valor |
| **Complejidad operativa (1–5)** | **2** — un hub, un conector | **5** — 3 buses + enrutador + Redis + DLQs |
| **Costo infraestructura anual (est.)** | **~USD 55K** Event Hubs Standard + Kinesis + Monitor | **~USD 140K** 3 buses + AKS enrutador + Redis |
| **Servicios nativos nube (sin terceros)** | ★★★★★ 100% Azure/AWS/GCP | ★★★★★ Tras revisión; igual restricción |
| **Latencia p95 publicación→consumo** | **≤ 5 s** (RNF-INI01-01) | **6–10 s** típico |
| **Disponibilidad integración** | **99.9%** hub + CB conector | **99.5–99.7%** cadena más larga |
| **Observabilidad PLT-01** | Monitor + App Insights + CloudWatch | Monitor + CloudWatch + Cloud Logging |
| **Escalabilidad campaña 3×** | Event Hubs Standard (TU escalables) | Riesgo cuello en enrutador |
| **Patrones aplicados** | Hub-and-Spoke, EDA, CQRS, Strangler, Circuit Breaker | Event Mesh, ACL, Bulkhead |
| **Deuda técnica post go-live** | Baja — convergencia TO BE Hito 1 | Media-alta — malla permanente |

---

## 3. Matriz ponderada (score normalizado)

| Criterio | Peso | Alt A (1–5) | Alt B (1–5) | Puntos A | Puntos B |
|---|---:|---:|---:|---:|---:|
| Impacto reducción penalidades / ingresos | 30% | 5 | 4 | 1.50 | 1.20 |
| Reducción riesgo operativo | 25% | 5 | 3 | 1.25 | 0.75 |
| Habilitador otras iniciativas | 20% | 5 | 4 | 1.00 | 0.80 |
| Time-to-value | 15% | 5 | 3 | 0.75 | 0.45 |
| Complejidad / riesgo impl. (invertido) | 10% | 4 | 2 | 0.40 | 0.20 |
| **Total ponderado** | **100%** | | | **4.90** | **3.40** |

---

## 4. Análisis por iniciativa

### INI-01 — PLT-03 Bus de Eventos Central

Alternativa A implementa **Azure Event Hubs Standard** como hub único con esquemas en Blob Storage + Azure Function — cumple RF-INI01-01/02/03 con menor riesgo y costo intermedio. Alternativa B requiere agregador de replay y tres buses operativos.

### INI-02 — WMS Cloud

Ambas comparten AKS + SQL MI General Purpose + KEDA. Alternativa A publica directo a PLT-03; evita salto de enrutador en el camino crítico reserva→TMS (RNF-INI02-01, pico 3×).

### INI-03 — APP-15

Alternativa A (**Kinesis → conector → Event Hubs**) es la topología exacta de INI-03 y doc 11. Alternativa B añade EventBridge sin eliminar Kinesis — más componentes, mismo origen Hito 1.

---

## 5. Decisión del comité de arquitectura

### Se adopta: **Alternativa A — Hub Central Azure**

Esta es la **única alternativa de implementación** para RutaExpress. La Alternativa B queda documentada únicamente como contraste exigido por el enunciado del Hito 2 y **queda descartada** para el roadmap de 36 meses.

**Fundamentos de la decisión:**

1. **Coherencia Hito 1:** INI-01, doc 09 TO BE, doc 10 (servicios nativos) y doc 11 (costos/roadmap) definen hub único Event Hubs + PLT-01 nativo.
2. **Costo nivel intermedio:** Event Hubs **Standard** (no Premium), Monitor + CloudWatch (no Datadog), SQL MI General Purpose.
3. **Time-to-value:** INI-01 mes 1 e INI-03 meses 2–6 sin construir enrutador multinube.
4. **RNF cumplidos:** p95 ≤ 5 s y E2E ≤ 30 s con margen operativo.
5. **Score ponderado:** 4.90 vs 3.40 — diferencia decisiva en riesgo y complejidad.

**Extensión futura controlada (mes 18+):** APP-24 (GCP) se conectará como **consumidor adicional** del hub PLT-03 mediante suscripción nativa Azure→Pub/Sub (spoke), **sin** migrar a malla federada completa.

---

## 6. Plan de acción (Alternativa A)

| Fase | Acción | Plazo |
|---|---|---|
| 1 | Aprobar ADR-A-001 … ADR-A-006 | Comité mes 0 |
| 2 | Desplegar PLT-03 Standard + esquemas Blob/Function (Terraform PLT-04) | Mes 1–3 |
| 3 | Desplegar PLT-01: Monitor + App Insights + export CloudWatch | Mes 1–5 (INI-07) |
| 4 | APP-15 offline + Kinesis→Event Hubs | Mes 2–6 |
| 5 | WMS Cloud piloto 1 CD + publicación eventos | Mes 4–8 |
| 6 | Prueba carga 3× + validación escenarios Gherkin | Pre Cyber Days |
| 7 | Suscripción PLT-03 → Pub/Sub para APP-24 | Mes 18 |

---

## 7. Resumen visual de decisión

```
                    ┌─────────────────────────────────────┐
                    │   DECISIÓN: ALTERNATIVA A           │
                    │   Hub Central — Event Hubs Standard │
                    │   PLT-01 nativo (Monitor+CW)      │
                    └─────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
    INI-01 PLT-03              INI-02 WMS Cloud            INI-03 APP-15
    Event Hubs Standard        AKS + SQL MI GP             Kinesis → Hub
    Blob/Function esquemas     KEDA + degradado            Offline + S3

    Alternativa B: DOCUMENTADA / NO IMPLEMENTADA
```

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*  
*Fecha: Julio 2026*
