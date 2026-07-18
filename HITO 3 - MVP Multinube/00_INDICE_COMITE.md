# Hito 3 — MVP Multinube RutaExpress
## Índice y guía de lectura

Paquete de documentación del **MVP multinube** (Alternativa A recortada). Consolida Hito 1 (empresa) y Hito 2 (TO BE) y define qué se demuestra en el prototipo.

> **Estado real del MVP (julio 2026):** núcleo Azure de órdenes (APIM → OMS → Inventario HTTP → outbox → `bus-workers` → Event Hubs) **implementado** en código/IaC. AWS última milla y puente **parcial / objetivo**. GCP lectura CQRS **objetivo** (tracking hoy = mock APIM). Detalle canónico: [`03_C4_Model_MVP.md`](03_C4_Model_MVP.md).

> **Marco de alcance:** [`01b_TOBE_vs_MVP_Alternativa_A.md`](01b_TOBE_vs_MVP_Alternativa_A.md) — **plano** (Alternativa A) → **maqueta** (MVP) → **casa entera** (producción).

---

## 1. Cómo leer este paquete

### Lectura corta (cualquier persona · ~25 min)

| Paso | Documento | Qué obtienes |
|:---:|---|---|
| 1 | Este índice (§2–§4) | Mapa, nombres y estado |
| 2 | [`01_Resumen_Empresa_RutaExpress.md`](01_Resumen_Empresa_RutaExpress.md) | Quién es RutaExpress y qué duele |
| 3 | [`01b_TOBE_vs_MVP_Alternativa_A.md`](01b_TOBE_vs_MVP_Alternativa_A.md) §1–2 | Plano vs maqueta vs producción |
| 4 | [`05_Servicios_por_Nube_MVP.md`](05_Servicios_por_Nube_MVP.md) **Parte I** | Qué hay en Azure / AWS / GCP |
| 5 | Diagramas en `diagramas_c4/imagenes/` + [`03b_Guion…`](03b_Guion_Exposicion_C4_PPT_6a_13.md) | Cómo se ve la arquitectura |

### Lectura de comité / defensa (~50–70 min)

| Paso | Documento | Para qué |
|:---:|---|---|
| 1 | Este índice completo | Orientación |
| 2 | `01` → `01b` | Negocio y alcance |
| 3 | [`02_Dossier_MVP_Alternativa_A.md`](02_Dossier_MVP_Alternativa_A.md) | Alcance, patrones, E1–E8 |
| 4 | [`03_C4_Model_MVP.md`](03_C4_Model_MVP.md) | **Fuente de verdad** C4 + estados |
| 5 | [`04_IaC_Costos_Despliegue.md`](04_IaC_Costos_Despliegue.md) | IaC, nube, personal, operación, ROI |
| 6 | [`05_Servicios_por_Nube_MVP.md`](05_Servicios_por_Nube_MVP.md) | Catálogo (Parte II si hace falta) |
| 7 | [`06_Preguntas_Argumentos_Comite.md`](06_Preguntas_Argumentos_Comite.md) | Defensa oral |

**Código IaC:** [`../Implementacion/`](../Implementacion/)  
**Regenerar diagramas:** `python diagramas_c4/generar_diagramas_mvp_c4.py`

---

## 2. Mensaje ejecutivo (30 segundos)

RutaExpress demuestra el flujo **orden → reserva → evento → entrega offline → evidencia → tracking**, repartido en **Azure + AWS + GCP**, con **IaC** (Terraform), **mocks** de legados y **seis patrones** (Microservicios, DDD, EDA, CQRS, Saga, Resiliencia).

El MVP es un **recorte** del TO BE: valida decisiones y una ruta evolutiva; **no** es toda la Alternativa A en producción.

---

## 3. Nombres canónicos (usar siempre estos)

| Nombre correcto | Qué es | No usar |
|---|---|---|
| **OMS — APP-02** | Orquestador de Pedidos | “el orquestador” sin ID en docs formales |
| **Inventario — MS-INI01-02** | Microservicio de reservas | Confundirlo con WMS (APP-06) o APP-08 |
| **`bus-workers`** | Deployment AKS: lee outbox SQL → Event Hubs | Publicador Outbox, Bus Workers |
| **`retry-worker`** | Contenedor Fargate: SQS → EventBridge | SQS Bridge Worker, Retry Worker |
| **BFF del MVP** | Backend for Frontend en AKS | Demo Comité BFF |
| **Backend móvil — APP-15** / `mobile-api` | API última milla en ECS | “backend movil ultima milla” |
| **Adaptador AWS→Azure** | Function objetivo EventBridge → Event Hubs | “adaptador” genérico (≠ mock WMS) |
| **Event Hubs** | Stream canónico | Decir que es Service Bus |
| **Service Bus** | Colas + DLQ | Decir que es donde publica `bus-workers` |

Taxonomía completa y protocolos: [`03_C4_Model_MVP.md`](03_C4_Model_MVP.md) §0.

---

## 4. Estado del MVP en una mirada

| Flujo | Estado | Dónde leer |
|---|---|---|
| Alta de orden + reserva HTTP + mock WMS | **Implementado** | C4 Flujo A · N3 OMS/Inventario |
| Outbox → `bus-workers` → Event Hubs | **Implementado** (órdenes) | C4 N3 PLT-03 |
| Service Bus → consumidor Inventario | **Objetivo** | C4 §3.4 / N3 Inventario |
| DLQ demo E5 (BFF → Service Bus) | **Demo parcial** (replay = objetivo) | C4 Flujo D |
| Entrega offline + evidencia AWS | **Parcial** | C4 Flujo B · N3 móvil |
| Puente SQS → `retry-worker` → EventBridge → Azure | **Objetivo** | C4 Flujo B |
| Tracking BigQuery / CQRS | **Objetivo** (hoy mock portal) | C4 Flujo C |

Leyenda: **Implementado** = en uso en el MVP · **Parcial** = infra o stub sin cadena completa · **Objetivo** = diseño no cableado · **Mock** = legado simulado.

---

## 5. Mapa de documentos

| Archivo | Contenido | Audiencia |
|---|---|---|
| `00` (este) | Índice, nombres, estado, lectura | Todos |
| `01` | Empresa, cadena de valor, dolores | Todos |
| `01b` | Alternativa A vs MVP vs producción | Comité |
| `02` | Dossier: alcance, patrones, E1–E8 | Comité |
| `03` | C4 N1–N3, flujos, canon | Técnico / defensa |
| `03b` | Guion oral solo diagramas C4 | Expositor |
| `04` | IaC, costos nube/personal/ops, ROI | Comité FinOps |
| `05` | Catálogo por nube | Comité + técnico |
| `06` | Preguntas y argumentos | Defensa oral |

---

## 6. Cumplimiento del enunciado (Hito 3)

| Requisito | Cumplimiento |
|---|---|
| Basado en TO BE Alternativa A | Hub Azure + AWS móvil + GCP lectura — [`01b`](01b_TOBE_vs_MVP_Alternativa_A.md) |
| Mínimo 2 nubes | **3:** Azure + AWS + GCP |
| Mínimo 3 patrones | **6:** Microservicios, DDD, EDA, CQRS, Saga, Resiliencia |
| Despliegue 100 % IaC | Terraform — [`04`](04_IaC_Costos_Despliegue.md) |
| Costos | Nube ~USD 449/mes; TCO Lima ~USD 37k/año — [`04`](04_IaC_Costos_Despliegue.md) §4–§7 |
| APIs mock | APIM + mocks WMS/ERP/Portal/TMS — dossier §4.3 |

---

## 7. Decisiones que el comité valida

1. **Hub Azure** — OMS, APIM y bus donde ya está el núcleo operativo.
2. **OMS = APP-02** evolucionado (mismo ID).
3. **PLT-03** = Event Hubs (stream) + Service Bus (colas/DLQ); `bus-workers` publica en Event Hubs.
4. **Inventario MS-INI01-02** en AKS — no es APP-XX ni el WMS.
5. Alcance parcial **INI-01 / INI-02 / INI-03** (escenarios E1–E8).
6. **GCP MVP:** Event Hubs → Cloud Run → BigQuery (**sin Pub/Sub** en v1).
7. Legados simulados con **mocks** en APIM.

---

## 8. Glosario breve

| Término | Significado |
|---|---|
| **ACK** | Acuse de recibo |
| **AKS** | Kubernetes administrado en Azure |
| **backpressure** | Frenar consumo cuando hay cola acumulada |
| **circuit breaker** | Cortar llamadas a un sistema que falla repetido |
| **CQRS** | Separar escritura operativa y lectura analítica |
| **DDD** | Diseño guiado por el dominio |
| **DLQ** | Cola de mensajes fallidos |
| **EDA** | Arquitectura orientada a eventos |
| **egress** | Tráfico de salida entre nubes (costo) |
| **Fargate** | Contenedores AWS sin administrar servidores |
| **IaC** | Infraestructura como código (Terraform) |
| **idempotencia** | Misma petición repetida sin duplicar efecto |
| **OLTP** | Procesamiento transaccional (órdenes, reservas) |
| **outbox** | Registro local de eventos pendientes de publicar |
| **ROI** | Retorno de inversión |
| **Saga** | Pasos coordinados con compensación si falla |
| **store-and-forward** | Guardar offline y reenviar con red |
| **TCO** | Costo total de propiedad |
| **vertical slice** | Corte end-to-end demostrable |

---

## 9. Trazabilidad

| Origen | Ubicación |
|---|---|
| Hito 1 | `HITO 1 - Arquitectura Empresarial/` |
| Hito 2 — Alternativa A (TO BE) | `HITO 2 - .../ARQUITECTURA_SOLUCION_TO_BE/02_Alternativa_A.md` · imágenes `diagramas_c4/alternativa_A_*.png` |
| Hito 2 — RF INI-01/02/03 | `HITO 2 - .../INI-*/` |
| Enunciado | `Enunciado del Proyecto Integrador Final.md` |
| Defensa | [`06_Preguntas_Argumentos_Comite.md`](06_Preguntas_Argumentos_Comite.md) |

---

*RutaExpress — Hito 3 MVP Multinube — UTEC*
