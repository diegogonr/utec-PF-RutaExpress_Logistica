# Preguntas frecuentes y argumentos para el comité

**Hito 3 — MVP Multinube RutaExpress**  
Documento de apoyo oral para la defensa. Complementa el dossier, el C4 y el índice del comité.

> **Convención:** toda sigla o palabra técnica en inglés lleva entre paréntesis su significado breve. Glosario completo: [`00_INDICE_COMITE.md`](00_INDICE_COMITE.md) §Glosario breve.

---

## Reglas de argumentación (leer antes de defender)

| Evitar (circular) | Usar en su lugar |
|---|---|
| «Porque la Alternativa A / el Hito 2 lo dice» | **AS IS del cliente**, dolores del caso (§`01`), perfil de carga, comparación técnica entre opciones |
| «Porque un ADR nuestro lo aprobó» | **Requisito verificable** (E1–E8), restricción del enunciado, límite del producto Azure/AWS |
| «Porque así lo documentamos» | **Qué pasa si se elige la otra opción** (riesgo, costo, qué escenario de demo se rompe) |

La columna **Evidencia** apunta al paquete solo para **ampliar** si preguntan; la respuesta oral debe bastar **sin** abrir el PDF.

---

## 1. Alcance del MVP

| Pregunta posible | Argumento para responder | Evidencia |
|---|---|---|
| ¿El MVP implementa todo el TO BE? | **No.** El TO BE describe 36 meses y seis iniciativas. El MVP es una **maqueta** que prueba el núcleo orden → reserva → evento → entrega offline → tracking (E1–E8), no la migración completa de 26 aplicaciones. | `01b`; `02` §1 |
| ¿Por qué mocks de WMS, ERP, portal y TMS? | El enunciado **permite APIs mock**. Los legados on premises no están en alcance de despliegue; los mocks permiten probar **contratos HTTP y eventos** (Saga — pasos compensables, circuit breaker — corte ante fallos, CQRS — separar escritura y lectura) sin VPN ni migración del CD. | Enunciado; `02` §4.3 |
| ¿Qué son E1–E8? | **Criterios de aceptación de la demo**, mapeados a dolores reales: 32.000 duplicados, Cyber Days, firmas perdidas, tracking inconsistente. | `01` §4; `02` §6 |
| ¿Qué queda fuera? | WMS Cloud real, optimizador de rutas/ML, liquidación automática, observabilidad plena, Pub/Sub (publicar/suscribir) GCP en v1. | `02` §2.2 |

---

## 2. Multinube (Azure + AWS + GCP)

### 2.1 Por qué tres nubes (argumento independiente)

**1. RutaExpress ya opera en tres nubes** (`01` §3). El problema AS IS es la **integración punto a punto**, no el multicloud en sí.

**2. Cada nube cubre un perfil de carga distinto:**

| Rol | Perfil | Por qué no mezclarlo todo en un vendor en la maqueta |
|---|---|---|
| **Azure** | OLTP (transaccional en línea), Saga (pasos compensables), bus, API gateway | Orquestador y TMS **ya están en Azure**; SQL + Event Hubs + Service Bus encajan transacción y campañas |
| **AWS** | Móvil offline, S3 evidencias | APP-15 y S3 **ya están en AWS**; ACK (acuse de recibo) al conductor y objetos grandes cerca del borde |
| **GCP** | Lectura analítica | Analítica **ya en GCP**; BigQuery evita que el tracking masivo golpee SQL transaccional (CQRS — separar escritura y lectura) |

**3. Consolidar en una sola nube en el MVP** = re-plataformar móvil y analítica **antes** de validar el bus — migración de años, no alcance de prototipo.

**Respuesta oral (30 s):** «El cliente **ya** está en Azure, AWS y GCP. Falló la **integración**, no tener tres proveedores. Separamos por **tipo de carga** y unimos con **eventos**. El MVP demuestra ese remedio en E1–E8.»

### 2.2 Otras preguntas multinube

| Pregunta | Argumento | Evidencia |
|---|---|---|
| ¿Más caro/complejo? | Egress (tráfico de salida entre nubes) ~USD 18/mes en demo baja; es el costo de **no migrar 68k entregas/día y S3** de golpe. Mitigación: eventos compactos, región coherente. | `04` §4.2 |
| ¿Azure = SPOF (punto único de falla)? | El **hub de decisión de negocio** (orden, bus) concentra donde ya está el OMS. Mitigación: particiones, DLQ/replay (cola de fallidos / reproceso auditado), backpressure (frenado de ingesta — caso 240k pedidos). Multi-región = post-MVP. | `01` §4; `03` Flujo D |
| ¿Conductor → Azure directo? | Última milla necesita **ACK local** y S3 donde ya está APP-15. Cada entrega dependería de red al hub; el caso perdió **1.200 firmas** por conectividad. Patrón objetivo: sync a AWS, luego puente async (asíncrono) al hub. | `01` §4; `03` §4.3 |
| ¿Integración entre nubes? | El diseño objetivo usa Móvil → SQS → `retry-worker` en Fargate → EventBridge → Adaptador AWS→Azure → Event Hubs, y Event Hubs → ingesta → Cloud Run → BigQuery. Esos puentes aún no están cableados de extremo a extremo. | `03` §3.4 |

---

## 3. Azure — compute y plataforma

### 3.1 ¿Por qué AKS y no Azure Functions / App Service?

**Contexto del workload:** tres piezas de dominio en Azure — OMS (orden, Saga, outbox), Inventario (reserva HTTP hoy), y **`bus-workers`** (lee outbox → Event Hubs). Carga siempre encendida en demo; consumidores Service Bus = diseño objetivo.

| Criterio | **AKS** (Kubernetes administrado en Azure) | **Azure Functions** | **App Service** |
|---|---|---|---|
| **API HTTP + procesos de fondo en el mismo equipo** | Un contenedor puede exponer REST **y** `bus-workers`/Saga en pods vecinos del mismo cluster | Functions separa HTTP de lógica larga; Saga + outbox + polling implica **Durable Functions** o varias funciones — más piezas y cold starts | App Service sirve web/API; segundo microservicio y bus suelen terminar en planes separados sin el control de K8s |
| **Duración / espera síncrona** | Sin límite de 10–30 min por «invocación»; la Saga **espera** respuesta mock-WMS (HTTP sync — síncrono) dentro del mismo proceso | Timeout por invocación (aunque extensible) y modelo evento-a-evento **no natural** para Saga síncrona con compensación en la misma unidad lógica | Similar a Functions para trabajos largos; menos idóneo para workers custom del bus |
| **Varios microservicios (OMS + inventario)** | **Dos deployments** en un cluster: aislamiento de dominio, red interna, políticas comunes (secretos, OTel — OpenTelemetry) | Un Function App por dominio o un monolito de funciones — peor frontera de dominio o peor operación | Varios App Services = varios planes; menos estándar para patrón microservicio + worker |
| **Integración con Event Hubs / Service Bus** | SDKs en proceso largo, reconexión, backpressure custom (E4, E5) | Posible pero fragmentado en triggers; lógica de replay auditado más incómoda | Menos flexible para consumidores dedicados con lógica propia |
| **Afinidad con lo existente** | Orquestador **APP-02 ya corre en Azure**; contenedores son el siguiente paso natural sin cambiar modelo mental del equipo | Cambio de paradigma (functions) para un dominio ya pensado como **servicio** | Intermedio; muchos equipos acaban en AKS cuando crecen microservicios + workers |
| **Costo MVP demo** | Cluster pequeño 2 nodos ~USD 140/mes — caro pero **un solo plano** para OMS + Inventario + `bus-workers` | Puede ser más barato en invocaciones bajas, pero **más funciones/apps** para el mismo alcance | Varios planes Web + workers → coste comparable sin ventaja clara |

**Qué escenario de demo se rompe si solo Functions/App Service:** E4/E5 (workers de bus con replay y backpressure acoplados al mismo runtime de dominio), operación de **dos microservicios** con outbox SQL, y Saga con paso WMS síncrono + compensación en un flujo continuo.

**Respuesta oral:** «Elegimos **AKS** porque tenemos **varios servicios de dominio con estado**, workers de fondo (outbox, bus) y **Saga con llamada síncrona al WMS mock**, no funciones aisladas de segundos. Functions encajaría para un endpoint puntual; aquí el Orquestador, Inventario y el bus son **procesos de vida larga** que comparten un cluster. App Service quedaría corto para workers custom y dos microservicios con escalado distinto.»

### 3.2 Otras preguntas Azure

| Pregunta | Argumento | Evidencia |
|---|---|---|
| ¿Event Hubs **y** Service Bus? | **Funciones distintas:** Hubs = **stream** (flujo continuo) de alto volumen; Service Bus = **colas por consumidor** con ACK y DLQ. El encadenamiento completo es objetivo. | `03` §4.1 |
| ¿Tantos componentes en el bus? | El caso **Cyber Days** exige DLQ con payload (cuerpo del mensaje) intacto y **replay auditado** (240k mensajes). Los brokers administrados no sustituyen **replay gobernado + validación de contrato** sin perder la narrativa E5. | `01` §4; `03` §4.1 |
| ¿SQL compartida OMS + inventario? | **Costo y operación MVP:** una instancia, **esquemas separados**, sin joins cross-dominio; integración por bus. Escalar a instancias separadas no cambia el contrato de dominio. | `03` §4.4 |
| ¿Redis además de SQL? | Dedup (deduplicación) e idempotencia (misma petición sin duplicar) (E1, E2) con **latencia ms** y TTL (tiempo de vida en caché) 24h sin martillar SQL en cada reintento del cliente. | `01` §4; `03` §4.2 |
| ¿APIM Developer? | Prototipo académico sin SLA: ~USD 50/mes vs ~700 Standard; suficiente para OAuth (autorización delegada), mocks y demo. | `04` §4.1 |
| ¿Saga → WMS por HTTP sync? | El contrato con WMS on premises en el caso es **confirmación síncrona** en almacén; la demo usa mock con 503/timeout (E4). WMS solo-async retrasaría saber si la orden queda confirmada y complicaría compensación **en la misma conversación de negocio**. | `02` §2.1 INI-01; Flujo A |
| ¿Sin Pub/Sub hacia GCP? | El productor canónico está en Azure. Añadir Pub/Sub en v1 sería otro broker; la ingesta compatible con Cloud Run permanece como decisión objetivo. | `03` §4.6 |

---

## 4. AWS — última milla

### 4.1 ¿Por qué ECS Fargate y no Lambda?

| Criterio | **ECS Fargate** (contenedores sin administrar servidores) | **Lambda** (funciones serverless) |
|---|---|---|
| **Modelo** | Servicio **HTTP continuo** (ALB — balanceador de carga): lote del móvil → S3 + DynamoDB → **ACK** en la misma sesión | Modelo por invocación; API + evidencias + ACK + relay suelen **fragmentarse** en varias funciones |
| **`retry-worker`** | Polling (consulta periódica) de todos los mensajes de SQS con **jitter** (espera aleatoria entre reintentos para no saturar) en el **mismo task** que la API; publica en EventBridge y reintenta fallos | Lambda + trigger SQS + posible segunda función para relay; más cold starts en el puente |
| **Duración** | Subida de evidencias y lotes offline sin techo rígido de invocación | Límite por invocación; lotes grandes o muchas fotos acercan al límite |
| **Store-and-forward** (guardar y reenviar) | Handler orquesta evidencia + outbox en **un flujo** en memoria | Más round-trips stateless (sin estado en servidor) a S3/DynamoDB entre pasos |
| **Costo demo** | ~USD 38/mes 24/7 — coherente con demo siempre disponible | Más barato a volumen mínimo; ahorro no compensa fragmentar INI-03 |

**Respuesta oral:** «El backend móvil es **una API REST con ACK inmediato al conductor**, evidencias S3 y **retry del puente en el mismo servicio**. Lambda obligaría a trocear eso y complicaría el patrón offline sin ganancia clara en la demo.»

### 4.2 ¿Por qué ECS Fargate y no EKS (Kubernetes en AWS)?

> **Aclaración de nombres:** **Fargate** es el cómputo sin servidores; puede usarse con **ECS** o con **EKS**. La pregunta del comité suele ser: ¿por qué no **EKS** (aunque sea EKS on Fargate) si ya hay **AKS** en Azure?

| Criterio | **ECS Fargate** | **EKS** (incl. EKS on Fargate) |
|---|---|---|
| **Carga en AWS** | **Una** aplicación: backend **App de Conductores (APP-15)** — API + `retry-worker` en el **mismo task** | Pensado para **varios** workloads, namespaces, Ingress, Helm… |
| **Kubernetes en el MVP** | **AKS (Azure)** ya concentra el hub: APP-02, MS-INI01-02, workers PLT-03, OTel | Segundo cluster K8s solo para la última milla = **simetría artificial** |
| **Control plane** | No hay cluster EKS; solo pagas el task Fargate (~USD 38/mes demo) | Control plane EKS ~**USD 73/mes** además del cómputo |
| **Operación** | Task + Service + ALB — Terraform directo | Cluster, RBAC, CNI, add-ons, posible segundo Helm chart |
| **Patrón GCP** | Mismo criterio que **Cloud Run vs GKE**: runtime **mínimo** por perfil de carga | GKE tampoco se usa en GCP para el proyector CQRS |

```text
Azure (hub)     AWS (última milla)    GCP (lectura)
    AKS      →   ECS Fargate      →   Cloud Run
  varios pods      1 task móvil         1 handler CQRS
```

| Pregunta frecuente | Respuesta |
|---|---|
| ¿EKS on Fargate no evita administrar nodos? | Sí, pero **sigue** el costo y la complejidad del **control plane EKS**; para **un** servicio HTTP, ECS es más simple |
| ¿No es mejor K8s en las 3 nubes? | Solo el **dominio transaccional** lo justifica; ver también **§10** («¿K8s en las 3 nubes?») |
| ¿ECS Fargate es «AWS Fargate» suelto? | **No.** Fargate es el motor; **ECS** es quien orquesta tasks y servicios |

**Respuesta oral:** «Kubernetes ya está donde hace falta: **AKS** con OMS, inventario y bus. En AWS solo va el **backend móvil**, un contenedor con API y retry. **ECS Fargate** es el runtime mínimo; **EKS** añadiría un segundo cluster y costo sin beneficio en E6–E7. En GCP hicimos lo mismo: **Cloud Run**, no GKE.»

### 4.3 Otras preguntas AWS

| Pregunta | Argumento | Evidencia |
|---|---|---|
| ¿DynamoDB vs RDS? | Outbox y ACK: acceso clave-valor, baja latencia, on-demand (pago por uso); sin administrar instancia SQL en AWS para colas PENDING. | `03` §4.3 |
| ¿S3 evidencias? | Objetos inmutables, KMS (gestión de llaves), costo por GB; encaja fotos/firmas y caso de firmas perdidas (E7). | `01` §4 |
| ¿Offline en DynamoDB? | **No.** Offline = teléfono. DynamoDB cuando hay red **hacia AWS**. | `03` §4.3 |
| ¿SQS + EventBridge? | SQS absorbe picos del móvil; EventBridge publica al hub — desacopla fallos del puente Azure. | `03` §3.3 |
| ¿ALB vs API Gateway? | ALB es el patrón estándar **TLS (cifrado en tránsito) + health check (sondeo de salud) → ECS Fargate**; API Gateway añade capa y costo sin requisito de API management en AWS (eso está en APIM). | `03` §3.2 |

---

## 5. GCP

| Pregunta | Argumento | Evidencia |
|---|---|---|
| ¿Qué hace GCP? | Prepara la lectura CQRS: Cloud Run y BigQuery están provisionados/parciales; proyección y consulta real siguen como objetivo. No transacciona órdenes. | `03` §4.6 |
| ¿Cloud Run vs GKE? | Handler **ligero**, escala a cero, pago por invocación; GKE (Kubernetes en GCP) sería overkill para un proyector mínimo. | `03` §4.6 |
| ¿BigQuery vs leer SQL Azure? | Tracking masivo **no debe** bloquear OLTP del OMS; CQRS separa escritura (SQL) y lectura (BQ). | `03` Flujo C |
| ¿Firestore u otro? | El diseño E8 usa proyecciones tabulares; BigQuery encaja consultas analíticas de tracking. El mock-portal aún no consulta BigQuery. | `03` §4.6 |
| ¿INI-04 rutas/ML? | Fuera del MVP; GCP en maqueta = proyector + sandbox BQ. | `01` §5 |

---

## 6. Patrones

| Pregunta | Argumento | Evidencia |
|---|---|---|
| ¿Los 6 patrones? | Caso **distribuido** (orden, stock, bus, móvil, lectura): microservicios, DDD (diseño por dominio), EDA (eventos), CQRS, Saga, resiliencia — cada uno responde un dolor (duplicados, desincronización, offline, tracking). | `02` §3; `01` §4 |
| ¿Outbox repetido? | Mismo **patrón** (cola de salida de eventos), distinto store: garantizar que el evento no se pierde si el broker falla **después** del commit SQL o del ACK al móvil. | `03` §1.2 |
| ¿Idempotencia + dedup? | Dos problemas AS IS: reintento con misma clave (E1) vs **misma orden con clave distinta** (E2, 32k duplicados). | `01` §4 |
| ¿CQRS duplica datos? | Sí **a propósito:** proyección eventual en BQ; fuente de verdad transaccional en SQL. | `03` Flujo C |

---

## 7. C4 y diagramas

| Pregunta | Argumento | Evidencia |
|---|---|---|
| ¿Muchas cajas N3? | **Módulos lógicos** (responsabilidades), no un pod (unidad en Kubernetes) por caja; pocos contenedores desplegables. | `03` §4.0 |
| ¿APIM sin flecha a Key Vault en N3 OMS? | N3 = zoom de **un contenedor**; seguridad transversal en N2 y configuración APIM (§4.5). | `03` §4.2 |
| ¿Query API vs tracking E8? | Query API = soporte sobre SQL; E8 = lectura CQRS objetivo. El mock-portal actual no consulta BigQuery. | `03` §4.2 |

---

## 8. Seguridad

| Pregunta | Argumento | Evidencia |
|---|---|---|
| ¿OAuth/JWT? | Es el diseño de seguridad; las policies APIM y la ausencia de secretos embebidos deben verificarse antes de afirmarlo como completo. | `03` §4.5; `04` §3 |
| ¿Evidencias? | El diseño usa S3 SSE-KMS + SHA-256; la cadena durable completa está parcial. | `03` §4.3 |

---

## 9. Costos e IaC

| Pregunta | Argumento | Evidencia |
|---|---|---|
| ¿Costo total? | Nube ~USD 449/mes; TCO año 1 Lima ~USD 37k (≈ S/ 138k); ROI ~164 % — `04` §4–§7. | `04` |
| ¿IaC 100%? | Requisito enunciado; módulos Terraform (infraestructura como código) por nube. | `04` §1 |

---

## 10. Preguntas incómodas

| Pregunta | Argumento | Evidencia |
|---|---|---|
| ¿Todo en Azure? | Ignora AS IS (APP-15, S3, analítica GCP); obliga a **migrar antes de probar** el bus; no demuestra integración multinube del caso. | `01` §3 |
| ¿K8s en las 3 nubes? | Solo el **dominio transaccional** justifica cluster (**AKS** en Azure); móvil → **ECS Fargate**; proyector → **Cloud Run**. Detalle ECS vs EKS: **§4.2**. | `02` §5; `05` §9 |
| ¿Microservicios overkill? | El caso ya tiene **dominios separados** (orden vs inventario vs móvil); el MVP usa **tres workloads**, no decenas. | `01` §2 cadena valor |

---

## 11. Guion 5 minutos

1. **Dolores** (`01` §4): duplicados, Cyber Days, offline, tracking.
2. **Multinube** (`06` §2.1): AS IS → hub por eventos; AWS entrega; GCP lee.
3. **Demo** (`03` Flujo A): orden → bus → inventario → Saga WMS mock.
4. **Diferencial:** DLQ/replay, móvil offline, CQRS E8.
5. **Cierre:** IaC, nube ~449 USD/mes, TCO/ROI en `04`, mocks = contratos legado.

---

*RutaExpress — Hito 3 — UTEC*
