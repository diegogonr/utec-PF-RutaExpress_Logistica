# Hito 3 — MVP Multinube RutaExpress
## Índice para el Comité de Arquitectura

> **Carpeta única de lectura.** Este Hito 3 consolida Hito 1 (arquitectura empresarial) y Hito 2 (diseño TO BE — Alternativa A recomendada) y define **qué se implementará** en el prototipo/MVP. **Aún no hay código desplegado**; este paquete es documentación de diseño de implementación aprobable por comité.

> **Regla de oro — nomenclatura:** en todo el paquete cada identificador va **siempre** con su **nombre oficial** (catálogo APP/PLT → `HITO 1 - .../06_Mapa_Portafolio_Aplicaciones.md`).

> **Regla de oro — términos técnicos:** toda sigla o palabra en inglés lleva entre paréntesis un significado breve en español — p. ej. **jitter** (espera aleatoria entre reintentos), **CQRS** (separar escritura y lectura). Glosario completo en la sección siguiente.

> **Marco de alcance:** [`01b_TOBE_vs_MVP_Alternativa_A.md`](01b_TOBE_vs_MVP_Alternativa_A.md) — **plano** (Alternativa A) → **maqueta** (MVP) → **casa entera** (producción).

---

## Glosario breve (términos técnicos del paquete)

| Término | Significado en español |
|---|---|
| **ACK** | Acuse de recibo — confirmación de que el destino guardó el dato |
| **AKS** | Kubernetes administrado en Azure (orquestador de contenedores) |
| **backoff** | Espera creciente entre reintentos |
| **backpressure** | Reducir velocidad de ingesta cuando un sistema downstream está degradado |
| **bounded context** | Límite de dominio de negocio (DDD) |
| **circuit breaker** | Corte automático de llamadas a un sistema que falla repetidamente |
| **cold start** | Arranque en frío — demora al activar una función serverless tras inactividad |
| **CQRS** | Separar escritura transaccional y lectura analítica |
| **DDD** | Diseño guiado por el dominio de negocio |
| **dedup / deduplicación** | Detectar y evitar registros duplicados |
| **DLQ** | Cola de mensajes fallidos (Dead Letter Queue) |
| **EDA** | Arquitectura orientada a eventos |
| **egress** | Tráfico de salida de datos (p. ej. entre nubes — costo de transferencia) |
| **fan-out** | Un evento entregado a varios consumidores |
| **Fargate** | Contenedores en AWS sin administrar servidores |
| **IaC** | Infraestructura como código (Terraform) |
| **idempotencia** | Misma petición repetida produce el mismo resultado sin duplicar |
| **jitter** | Espera aleatoria entre reintentos para no saturar el sistema |
| **KMS** | Gestión de llaves de cifrado en la nube |
| **OAuth** | Autorización delegada sin compartir contraseña |
| **OLTP** | Procesamiento transaccional en línea (altas, reservas, Saga) |
| **outbox** | Cola local de eventos pendientes de publicar al bus |
| **OTel / OpenTelemetry** | Estándar abierto de trazas, métricas y logs |
| **payload** | Cuerpo o contenido de un mensaje |
| **polling** | Consulta periódica de una cola hasta que haya mensajes |
| **replay** | Reprocesamiento auditado de mensajes desde DLQ |
| **Saga** | Secuencia coordinada de pasos con compensación si algo falla |
| **smoke test** | Prueba mínima de que el despliegue arranca y responde |
| **SPOF** | Punto único de falla |
| **store-and-forward** | Guardar en el dispositivo y reenviar cuando hay red |
| **throughput** | Volumen de mensajes u operaciones por unidad de tiempo |
| **TTL** | Tiempo de vida de un dato en caché antes de expirar |
| **vertical slice** | Corte que atraviesa todas las capas para demostrar un flujo end-to-end |

---

| Orden | Documento | Para qué sirve | Tiempo |
|:---:|---|---|:---:|
| 1 | **Este índice** | Orientación y mensajes clave | 3 min |
| 2 | [`01_Resumen_Empresa_RutaExpress.md`](01_Resumen_Empresa_RutaExpress.md) | Contexto de negocio — dolores, cadena de valor | 5 min |
| 3 | [`01b_TOBE_vs_MVP_Alternativa_A.md`](01b_TOBE_vs_MVP_Alternativa_A.md) | Marco TO BE vs MVP, hitos, INI parciales, E1–E8 | 8 min |
| 4 | [`02_Dossier_MVP_Alternativa_A.md`](02_Dossier_MVP_Alternativa_A.md) | Alcance, patrones, mocks, escenarios E1–E8 | 15 min |
| 5 | [`03_C4_Model_MVP.md`](03_C4_Model_MVP.md) | **C4 central** — N1–N3, flujos A–D, guía §4.0 (catálogo por figurita) + §4.0.7 FAQ | 15 min |
| 6 | [`04_IaC_Costos_Despliegue.md`](04_IaC_Costos_Despliegue.md) | Terraform, pipeline, costos (~USD 449/mes) | 8 min |

**Antes de la defensa oral:** [`06_Preguntas_Argumentos_Comite.md`](06_Preguntas_Argumentos_Comite.md) — preguntas frecuentes, argumentos (p. ej. Fargate vs Lambda, multinube §2.1) y guion de 5 min.

**Soporte para defensa oral:** [`06_Preguntas_Argumentos_Comite.md`](06_Preguntas_Argumentos_Comite.md) — incluye reglas para **no** argumentar solo con «porque el Hito 2 / Alternativa A lo dice».

**Diagramas:** `diagramas_c4/imagenes/` — regenerar con `python diagramas_c4/generar_diagramas_mvp_c4.py`.

---

## Mensaje ejecutivo

RutaExpress demostrará en el MVP el flujo crítico **orden → reserva → evento → entrega offline → evidencia → tracking CQRS** (separar escritura y lectura), en **Azure + AWS + GCP**, con **IaC** (infraestructura como código) completo, **mocks** de legados y **seis patrones** (Microservicios, DDD, EDA, CQRS, Saga, Resiliencia).

El MVP **implementa un recorte** del diseño TO BE (hub Azure + AWS móvil + GCP lectura), alineado al caso AS IS y a los escenarios E1–E8; **no** despliega todo el C4 TO BE ni cierra todos los RF de INI-01/02/03. Marco académico plano/maqueta: [`01b`](01b_TOBE_vs_MVP_Alternativa_A.md).

---

## Cumplimiento del enunciado (Hito 3)

| Requisito académico | Cómo se cumple |
|---|---|
| Basado en TO BE recomendado (Hito 2) | Hub Azure + reparto por carga (OLTP — transaccional/bus, móvil, CQRS — lectura); trazabilidad académica en [`01b`](01b_TOBE_vs_MVP_Alternativa_A.md) |
| Mínimo 2 nubes | **3:** Azure + AWS + GCP |
| Mínimo 3 patrones | **6:** Microservicios, DDD (diseño por dominio), EDA (eventos), CQRS (escritura/lectura), Saga (pasos compensables), Resiliencia |
| Despliegue 100 % IaC | Terraform modular — doc `04` |
| Costos por nube/mes | ~USD 449/mes — doc `04` §4 |
| API mock permitidas | APIM + mocks WMS/ERP/Portal/TMS — dossier §4.3 |

---

## Decisiones que el comité valida

1. **Hub central Azure** — OMS, API gateway y bus donde ya está el núcleo operativo del cliente; integración por eventos con AWS y GCP.
2. **Orquestador de Pedidos (APP-02)** evoluciona a OMS (mismo ID).
3. **Bus de Eventos Central (PLT-03)** = Event Hubs (stream) + Service Bus (colas con DLQ — mensajes fallidos).
4. **Microservicio Inventario (MS-INI01-02)** en AKS (Kubernetes administrado) — no es APP-XX.
5. **Alcance parcial** INI-01 (E1–E4), INI-02 (E5, E8 + backpressure — frenado de ingesta en E4), INI-03 (E6–E7).
6. **GCP MVP:** Event Hubs → Cloud Run → BigQuery (**sin Pub/Sub** en v1).
7. **Legados** simulados con mocks en APIM.

---

## Trazabilidad a entregables previos

| Origen | Ubicación |
|---|---|
| Hito 1 | `HITO 1 - Arquitectura Empresarial/` |
| Hito 2 — RF INI-01/02/03 | `HITO 2 - .../INI-*/` |
| Hito 2 — Alternativa A | `HITO 2 - .../ARQUITECTURA_SOLUCION_TO_BE/02_Alternativa_A.md` |
| Enunciado | `Enunciado del Proyecto Integrador Final.md` |
| Defensa oral — preguntas y argumentos | [`06_Preguntas_Argumentos_Comite.md`](06_Preguntas_Argumentos_Comite.md) |

---

*RutaExpress — Hito 3 MVP Multinube — UTEC*
