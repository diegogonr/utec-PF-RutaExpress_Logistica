# C4 Model — MVP Hub central Azure
## RutaExpress Fulfillment & Transporte

> **Este es el documento más importante del Hito 3.** Explica qué es el C4 Model, cómo leerlo en este proyecto y presenta los tres niveles con detalle de componentes — incluyendo vistas tipo **cuadro físico** para el nivel 3. **Guía detallada de todos los diagramas N3 → §4.0.**

**Imágenes generadas:** ejecutar `python diagramas_c4/generar_diagramas_mvp_c4.py` → salida en `diagramas_c4/imagenes/`.

> **Convención obligatoria (regla de oro):** en textos, tablas y diagramas de este documento cada identificador va **siempre** con su nombre oficial. Catálogo APP/PLT → `HITO 1 - .../06_Mapa_Portafolio_Aplicaciones.md`. **Término técnico en inglés o sigla:** la primera vez va con el significado breve entre paréntesis — p. ej. **ACK** (acuse de recibo), **outbox** (cola de salida de eventos), **DLQ** (cola de mensajes fallidos).

### 0.1 Iniciativas (INI), aplicaciones (APP), plataformas (PLT), microservicios (MS) y servicios en la nube

En este documento no se usan abreviaturas informales («apps», «ML» sin nombre de aplicación, «MS inventario»). Cada identificador va con su **nombre oficial** completo.

Al leer los diagramas y flujos conviven **cuatro familias de ID** de negocio/arquitectura, más una quinta capa de **servicios en la nube** del proveedor:

| Prefijo | Significado | Ejemplo en este MVP | ¿Es una aplicación del portafolio? |
|---|---|---|---|
| **INI-XX** | **Iniciativa** del roadmap Hito 1 (bloque de capacidades de negocio). Agrupa cambios sobre varias aplicaciones, plataformas y microservicios. | **INI-01**, **INI-02**, **INI-03** en alcance MVP | **No** — una iniciativa **no** es una aplicación |
| **APP-XX** | **Aplicación** del catálogo empresarial (26 aplicaciones: APP-01 … APP-26). Unidad reconocida por negocio y gobierno de TI. | **Orquestador de Pedidos (APP-02)**, **App de Conductores (APP-15)** | **Sí** |
| **PLT-XX** | **Plataforma** transversal habilitadora (observabilidad, identidad, bus de eventos, infraestructura como código). | **Bus de Eventos Central (PLT-03)** | Es plataforma, no aplicación de negocio |
| **MS-INIxx-yy** | **Microservicio** de una iniciativa. El prefijo **MS** abrevia solo el tipo *microservicio* en el ID; el nombre completo es obligatorio en el texto. | **Microservicio Inventario y Reservas (MS-INI01-02)** | **No** — ID **MS-INI01-02**, no **APP-XX** |

#### Diferencias: aplicación vs microservicio vs plataforma vs servicio en la nube

| Concepto | Qué representa | ¿Se despliega? | Relación con los demás |
|---|---|---|---|
| **Aplicación (APP-XX)** | Capacidad de negocio del portafolio Hito 1 (qué hace RutaExpress para el usuario o la operación). | Sí — como uno o más **contenedores** (workloads) en AKS, ECS, SaaS, etc. | Una aplicación **puede** implementarse con uno o varios microservicios, pero conserva **un solo ID APP**. Ej.: **Orquestador de Pedidos (APP-02)** corre en AKS. |
| **Microservicio (MS-INIxx-yy)** | Unidad técnica **acotada por dominio** (un bounded context), desplegable de forma independiente. Nace de una **iniciativa** cuando no existe aplicación en el catálogo. | Sí — típicamente un contenedor en **AKS** o **ECS Fargate**. | **No** agrupa varias aplicaciones APP dentro. **No** es un catálogo de APP-XX. Usa **servicios en la nube** (Azure SQL, Event Hubs, DynamoDB) como dependencias. |
| **Plataforma (PLT-XX)** | Capacidad compartida por muchas aplicaciones (bus, identidad, observabilidad). | Sí — como servicios administrados multinube. | Las aplicaciones y microservicios **publican/consumen** la plataforma; no la contienen. |
| **Servicio en la nube** | Recurso del proveedor (Azure, AWS, GCP): **AKS**, **Azure SQL**, **Event Hubs**, **Amazon S3**, **BigQuery**. | Lo provisiona Terraform (**Plataforma IaC (PLT-04)**). | Es **infraestructura** donde corren aplicaciones y microservicios; **no** es una aplicación del portafolio ni un microservicio de negocio. |

**¿De qué se compone un microservicio?** Un microservicio —por ejemplo **Microservicio Inventario y Reservas (MS-INI01-02)**— es **una** unidad desplegable (imagen de contenedor en **AKS**), con **componentes internos** de software (API, repositorio, publicador de eventos — nivel 3 C4). Se apoya en **servicios en la nube** (Azure SQL, **Bus de Eventos Central (PLT-03)** vía Event Hubs). **No** está formado por varias aplicaciones APP-XX; convive con **Orquestador de Pedidos (APP-02)** como otro workload en el mismo cluster, pero cada uno con responsabilidad de dominio distinta.

**Aplicación y microservicio no son lo mismo:** **Orquestador de Pedidos (APP-02)** es una **aplicación** del catálogo (dominio Orden; evoluciona a OMS centralizado). **Microservicio Inventario y Reservas (MS-INI01-02)** es un **microservicio** creado porque **INI-01** necesita dominio de inventario sin reutilizar **Control de Inventario (APP-08)** legado. No equivale a **Control de Inventario (APP-08)** (legado) ni sustituye al **WMS Principal (On Premises) (APP-06)** (en MVP se simula con mock).

---

El **C4 Model** (Simon Brown) documenta arquitectura de software en **cuatro niveles de zoom**, de lo abstracto a lo concreto. Solo usamos **tres niveles** en este proyecto (el nivel 4 — código — no aplica aún porque no hay implementación).

| Nivel | Nombre | Pregunta que responde | Audiencia |
|:---:|---|---|---|
| **1** | **Contexto** | ¿Quién usa el sistema y con qué sistemas externos se conecta? | Negocio, comité, gerencia |
| **2** | **Contenedores** | ¿Qué aplicaciones/servicios/data stores componen la solución y en qué nube corren? | Arquitectos, líderes técnicos |
| **3** | **Componentes** | ¿Qué piezas internas tiene **un** contenedor elegido? | Desarrollo, operaciones, seguridad |

### Reglas que seguimos (importante para el comité)

1. **Un diagrama de componentes = un solo contenedor en foco.** Los demás aparecen como cajas externas o sistemas de soporte.
2. **No mezclar niveles** en una misma figura (error común: poner AKS y DynamoDB como “componentes” del mismo diagrama).
3. **Cada caja tiene nombre + tecnología + responsabilidad** en una línea.
4. **Las flechas llevan significado:** HTTP, evento, comando, lectura, publicación. Ver **§1.1 Glosario de integraciones** antes de leer cualquier figura.
5. **Etiqueta de cada caja (PNG y Mermaid):** tres líneas — **(1)** nombre del **servicio cloud** o tecnología; **(2)** nombre **oficial** (aplicación, microservicio o plataforma); **(3)** **identificador** (`APP-XX`, `MS-INIxx-yy`, `PLT-XX`) o rol si es infraestructura compartida (p. ej. `Azure SQL` → datos de `APP-02` + `MS-INI01-02`).
6. **Términos técnicos:** siglas y palabras en inglés llevan entre paréntesis un significado corto en español la **primera vez** que aparecen en cada sección — ver glosarios §1.1–§1.3.

### 1.1 Glosario de integraciones (flechas del diagrama)

En los diagramas C4 del MVP aparecen **cinco tipos de conexión**. No son intercambiables: cada flecha indica **protocolo**, **dirección** y **quién inicia** la interacción.

| Etiqueta en diagrama | Qué es | Protocolo | Dirección | Quién inicia | Ejemplo concreto en el MVP |
|---|---|---|---|---|---|
| **HTTPS API** | Canal **síncrono** del cliente B2B hacia el hub | REST sobre TLS | Cliente → **Azure API Management (APP-01)** | Cliente B2B / script de demo | `POST /api/v1/orders` (alta de orden). El cliente **espera** respuesta HTTP 201/4xx en la misma llamada. |
| **HTTPS móvil** | Canal **síncrono** de **App de Conductores (APP-15)** hacia AWS | REST sobre TLS | Conductor → **Backend móvil** (ALB + Fargate) | **App de Conductores (APP-15)** | `POST /deliveries/{id}/complete`, subida de metadatos de evidencia. Respuesta inmediata; si no hay red, se guarda en outbox local. |
| **HTTPS monitoreo** | Canal **síncrono** de operaciones hacia dashboards y herramientas | REST / portal web TLS | Operaciones → Plataforma MVP | Equipo de soporte | Consulta DLQ, replay auditado, métricas OpenTelemetry. No participa en el flujo de negocio de órdenes. |
| **HTTPS mock sync** | Llamada **síncrona** del hub hacia un **legado simulado** en **Azure API Management (APP-01)** | REST sobre TLS | Orquestador de Pedidos (APP-02) / Saga → **mock-wms** o **mock-erp** en **Azure API Management (APP-01)** | Orquestador de Pedidos (APP-02) | Saga confirma reserva: `POST /mock/wms/v1/reservations/confirm`. Respuesta 200/503/timeout configurable. **No** es el WMS real on premises. |
| **HTTPS GET lectura** | Consulta **solo lectura** (patrón **CQRS**) | REST GET sobre TLS | Cliente → **mock-portal** en **Azure API Management (APP-01)** | Cliente B2B | `GET /mock/portal/v1/tracking/{orderId}`. Lee proyección en BigQuery; **no** escribe en Azure SQL ni crea órdenes. |
| **Eventos async** | Integración **asíncrona** vía bus de mensajes | Event Hubs + Service Bus (AMQP) | Productor → **Bus de Eventos Central (PLT-03)** → consumidor | Orquestador de Pedidos (APP-02), Microservicio Inventario y Reservas (MS-INI01-02), backend móvil | `OrderCreated`, `DeliveryCompleted` publicados a Event Hubs; **mock-tms** (simula **TMS (Transportation Management) (APP-11)**) y proyector GCP **consumen** sin bloquear al emisor. |

**Diferencias clave (lo que suele confundir):**

| Pregunta | Respuesta |
|---|---|
| ¿**HTTPS API** y **HTTPS mock sync** son lo mismo? | **No.** HTTPS API es la **entrada** del cliente al hub. HTTPS mock sync es una **salida** del hub hacia sistemas legados **simulados** (WMS/ERP). |
| ¿El **portal mock** recibe eventos directamente? | **No en el diagrama de contexto.** El portal expone **HTTPS GET lectura**. Los eventos alimentan BigQuery vía proyector GCP; el portal **consulta** esa proyección, no escucha el bus. |
| ¿**HTTPS móvil** usa el bus de eventos? | **Indirectamente.** **App de Conductores (APP-15)** habla REST al backend AWS; el backend **después** publica eventos al bus (SQS → EventBridge → Event Hubs). En Nivel 1 se simplifica: conductor → plataforma. |
| ¿**API** vs **eventos**? | **API (HTTPS):** pregunta-respuesta inmediata, acoplamiento temporal (quien llama espera). **Eventos:** el emisor publica y sigue; el consumidor procesa cuando puede (desacoplamiento). |

> **Regla práctica:** si la flecha sale de un **Person** (cliente, conductor, operaciones) → es **HTTPS**. Si sale del **MVP hacia un mock legado** con Saga → **HTTPS mock sync** o **HTTPS GET lectura**. Si conecta **contenedores internos** o el **Bus de Eventos Central (PLT-03)** → **eventos async**.

### 1.2 Glosario de patrones — Outbox (patrón *Transactional Outbox*)

En varios diagramas y flujos aparece la palabra **outbox**. No es un producto de nube: es un **patrón de diseño** para publicar eventos **sin perderlos** ni crear inconsistencias entre la base de datos y el **Bus de Eventos Central (PLT-03)**.

**Idea en una frase:** primero se guarda el dato de negocio **y** el evento pendiente en la **misma transacción** (operación atómica en base de datos); después un **worker** (proceso en segundo plano) lee esa cola y publica al bus. Si la publicación falla, el evento **sigue en la outbox** (cola de salida) y se reintenta.

#### Problema que resuelve

Sin outbox puede ocurrir:

1. Se guarda la orden en **Azure SQL** ✅  
2. Se intenta publicar `OrderValidated` a **Event Hubs** ❌ (falla red o timeout)  
3. Resultado: hay orden en la base, pero ningún consumidor se enteró → estados inconsistentes entre nubes.

Con outbox:

1. Se guardan orden **y** fila en tabla `outbox` en **una sola transacción** ✅  
2. Un worker lee `outbox` y publica a **Event Hubs** / **Service Bus** ✅ (si falla, reintenta)  
3. Se marca el registro como enviado cuando el bus confirma recepción.

#### Analogía

Como un **sobre en la bandeja de salida** del mostrador: la venta queda registrada y el sobre (evento) espera al mensajero (worker). Si el mensajero no pudo salir, el sobre **no desaparece** — se reintenta en el siguiente ciclo.

#### Los tres outbox del MVP (no confundirlos)

| Outbox | Dónde vive | Tecnología | Quién lo usa | Cuándo actúa |
|---|---|---|---|---|
| **Outbox local (dispositivo)** | Teléfono del conductor | Almacenamiento local cifrado (SQLite) | **App de Conductores (APP-15)** | **Sin red:** firma, foto y evento quedan en el móvil hasta poder sincronizar (INI-03 RF-02, RF-03). |
| **Outbox transaccional (hub Azure)** | Misma base que la orden/reserva | Tabla `outbox` en **Azure SQL** | **Orquestador de Pedidos (APP-02)** y **Microservicio Inventario y Reservas (MS-INI01-02)** | Tras crear orden o reserva: evento pendiente hasta publicarse en **Bus de Eventos Central (PLT-03)**. |
| **Outbox backend (AWS)** | Backend móvil en la nube | **DynamoDB** | Backend que soporta **App de Conductores (APP-15)** | El móvil **ya** llegó a AWS; el servidor guarda el evento y reintenta el **puente hacia Azure** si falla. |

> **Aclaración:** «Sin red» **no** escribe directo en DynamoDB ni en S3. Sin conectividad solo existe el **outbox local** en el dispositivo. DynamoDB y S3 intervienen en la **Fase 2** del Flujo B (§3.3), cuando hay red hacia AWS.

#### Flujo resumido — orden en Azure (outbox transaccional)

```text
1. Orquestador de Pedidos (APP-02) guarda orden en Azure SQL
2. En la misma transacción escribe en outbox: "publicar OrderValidated"
3. Worker lee outbox → publica a Event Hubs (PLT-03)
4. Marca el registro outbox como enviado
```

#### Flujo resumido — entrega offline (tres capas)

```text
Fase 1 — sin red:     APP-15 → outbox LOCAL (dispositivo)
Fase 2 — red a AWS:   APP-15 → ECS Fargate → DynamoDB outbox + S3 (APP-16)
Fase 3 — puente:      DynamoDB → SQS → EventBridge → Event Hubs (PLT-03)
```

#### Relación con otros patrones del MVP

| Patrón | Cómo se relaciona con outbox |
|---|---|
| **Store-and-forward** (guardar y reenviar — INI-03) | El outbox **local** del móvil es la implementación offline del conductor. |
| **EDA** (arquitectura orientada a eventos) | El outbox garantiza que los eventos salgan al **Bus de Eventos Central (PLT-03)** de forma fiable. |
| **Saga** (secuencia de pasos compensables — INI-01) | Los pasos de compensación (p. ej. `ReleaseInventory`) también pueden dispararse vía eventos publicados desde outbox. |
| **Resiliencia** (INI-02) | Complementa **DLQ** (cola de mensajes fallidos), **retry** (reintento) y **replay** (reprocesamiento auditado): el mensaje no se pierde **antes** de llegar al bus. |

### 1.3 Glosario de patrones — ACK (acuse de recibo)

**ACK** (*acknowledgment* — acuse de recibo) es la **confirmación explícita** de que el receptor **recibió, entendió y persistió** el mensaje o la evidencia. No basta con que el paquete viajó por la red: el emisor necesita saber que el destino **guardó** el dato de forma segura.

**Idea en una frase:** el backend le dice a **App de Conductores (APP-15)**: «ya guardé tu entrega; puedes borrar tu copia local».

#### Por qué importa en RutaExpress

El caso documenta **1.200 firmas/evidencias perdidas** cuando la aplicación borraba datos locales **antes** de que el servidor confirmara la recepción. El **Ack Tracker** (registro de acuses) en **DynamoDB** y el requerimiento **INI-03 RF-04** corrigen eso.

#### Flujo con ACK en última milla (INI-03)

```text
1. Conductor registra entrega sin red → outbox LOCAL en el dispositivo
2. Al reconectar, APP-15 envía lote al backend (ECS Fargate en AWS)
3. Backend persiste en DynamoDB + S3 (APP-16) y responde ACK al móvil
4. Solo tras ACK: APP-15 borra la copia local cifrada
```

| Paso | Sin ACK (frágil) | Con ACK (diseño MVP) |
|---|---|---|
| Conductor completa entrega offline | Datos solo en el teléfono | Datos en outbox local cifrado |
| Reconexión | La app asume éxito y borra local | La app **espera** respuesta del backend |
| Backend cae a mitad de sync | Se pierde evidencia | La copia local **permanece** hasta nuevo intento |
| Backend confirma | — | ACK → borrado local seguro |

#### ACK en el bus de mensajes (PLT-03)

En **Azure Service Bus** (colas del **Bus de Eventos Central (PLT-03)**) el consumidor también envía ACK al terminar de procesar un mensaje (operación `complete`). Si no lo hace, el mensaje **vuelve a la cola** para reintento — mismo concepto a nivel de mensajería asíncrona.

#### No confundir ACK con…

| Término | Significado | Diferencia con ACK |
|---|---|---|
| **HTTP 200/201** | Código de respuesta exitosa de una API | Puede incluir un ACK en el cuerpo, pero no siempre garantiza persistencia durable |
| **Outbox** (§1.2) | Cola donde el evento espera **antes** de publicarse al bus | El ACK confirma recepción **después** de que el destino guardó |
| **DLQ** (cola de mensajes fallidos) | Mensajes que **fallaron** tras varios reintentos | No es confirmación — es destino de error |

#### Relación con store-and-forward y outbox

| Capa | Rol del ACK |
|---|---|
| **Outbox local** (dispositivo) | El conductor ve «pendiente de sync» hasta recibir ACK del backend AWS |
| **Outbox backend** (DynamoDB) | El puente hacia Azure puede reintentar; el móvil ya recibió ACK de AWS |
| **Service Bus** (PLT-03) | Cada consumidor ACK al procesar; si falla, DLQ o retry |

### Por qué C4 y no solo un diagrama de nube

Un diagrama de infraestructura muestra *dónde* corre cada servicio. C4 muestra *por qué* existe cada pieza y *cómo* colaboran en el negocio. Para RutaExpress — multinube, event-driven, con legados — C4 evita que el comité vea “tres nubes” sin entender el flujo orden → entrega.

---

## 2. Nivel 1 — Diagrama de Contexto

### 2.1 Descripción

El **sistema en alcance** es la **Plataforma Logística MVP RutaExpress** (hub central Azure). Todo lo demás es actor o sistema externo.

![C4 Nivel 1 Contexto MVP](diagramas_c4/imagenes/mvp_c4_n1_contexto.png)

#### Cómo leer este diagrama (Nivel 1 — Contexto)

Este diagrama responde: **¿quién interactúa con el MVP y qué sistemas externos se simulan?** No muestra contenedores ni nubes; solo el **perímetro**.

| Paso | Qué mirar | Significado |
|:---:|---|---|
| 1 | Caja central **Plataforma Logística MVP** | Todo lo desplegado en Azure + AWS + GCP del prototipo (detalle en Nivel 2). |
| 2 | Flecha **HTTPS API** (Cliente → MVP) | **Vía principal de alta de órdenes:** `POST /api/v1/orders` vía **Azure API Management (APP-01)** → **Orquestador de Pedidos (APP-02)**. En la misma puerta, `GET mock-portal` consulta tracking (solo lectura). |
| 3 | Flecha **HTTPS móvil** (Conductor → MVP) | **App de Conductores (APP-15)** habla REST con el **backend móvil en AWS** (entregas, excepciones, evidencias). |
| 4 | Flecha **HTTPS monitoreo** (Operaciones → MVP) | Soporte revisa DLQ, replay y dashboards; no es flujo transaccional. |
| 5 | Flechas hacia **WMS / ERP** (**HTTPS mock sync**) | El hub **llama** APIs simuladas en **Azure API Management (APP-01)** como si fueran **WMS Principal (On Premises) (APP-06)** y **ERP Financiero (On Premises) (APP-25)** on premises. Respuesta síncrona en la Saga. |
| 6 | Flecha hacia **Portal** (**HTTPS GET lectura**) | Solo **consulta** de estado de pedido vía `mock-portal`; lectura CQRS, sin alta de órdenes. |
| 7 | Flecha hacia **TMS** (**Eventos async**) | El mock **TMS (Transportation Management) (APP-11)** **no recibe** `POST /orders` ni crea órdenes. Solo **consume eventos** de despacho/manifiesto desde el **Bus de Eventos Central (PLT-03)** cuando la orden **ya existe** (tras reserva en Flujo A o entrega en Flujo B). La alta sigue siendo el paso 2 (Cliente → APIM → OMS). |

**Qué NO muestra este nivel:** Azure SQL, Event Hubs, DynamoDB, BigQuery. Eso aparece en el Nivel 2.

### 2.2 Elementos

| Elemento | Tipo | Descripción |
|---|---|---|
| Cliente B2B / Retail | Persona | **Alta de órdenes:** `POST /api/v1/orders` vía **Azure API Management (APP-01)**. **Consulta tracking:** `mock-portal` en **Azure API Management (APP-01)** (simula **Portal B2B (Trazabilidad) (APP-18)**; solo lectura CQRS) |
| Conductor | Persona | Ejecuta entregas con **App de Conductores (APP-15)** (simulada en MVP) |
| Operaciones / Soporte | Persona | Monitorea DLQ, replay, tracking |
| Plataforma Logística MVP | **Sistema** | Azure hub + AWS móvil + GCP analítica |
| WMS Principal (On Premises) (APP-06) / WMS Satélite (On Premises local) (APP-07) (mock) | Sistema externo | Simula **WMS Principal (On Premises) (APP-06)** y **WMS Satélite (On Premises local) (APP-07)** |
| ERP Financiero (On Premises) (APP-25) (mock) | Sistema externo | Simula ERP Financiero (On Premises) (APP-25) |
| Portal B2B (Trazabilidad) (APP-18) / CRM de Atención al Cliente (APP-20) (mock) | Sistema externo | `mock-portal` en **Azure API Management (APP-01)**: **solo consulta** tracking (CQRS); no alta de órdenes en MVP |
| TMS (Transportation Management) (APP-11) (mock) | Sistema externo | Simula **TMS (Transportation Management) (APP-11)**. **No** es entrada de órdenes: suscriptor **eventos async** (despacho/manifiesto) vía **Service Bus (PLT-03)**; la orden se crea solo por `POST /api/v1/orders` (paso 2 arriba). |

### 2.3 Mensaje para exposición

> “El MVP no reemplaza todavía el WMS Principal (On Premises) (APP-06) real ni el ERP Financiero (On Premises) (APP-25); los simula con contratos API. El valor de la demo es probar OMS centralizado / Orquestador de Pedidos (APP-02), Bus de Eventos Central (PLT-03), última milla offline y trazabilidad entre tres nubes.”

---

## 3. Nivel 2 — Diagrama de Contenedores

### 3.1 Descripción

Zoom dentro de la **Plataforma Logística MVP**: cada caja del diagrama muestra **servicio cloud + nombre oficial + identificador** (regla §1, punto 5). Los componentes internos de software (nivel 3) heredan el ID del contenedor padre.

![C4 Nivel 2 Contenedores MVP](diagramas_c4/imagenes/mvp_c4_n2_contenedores.png)

#### Cómo leer este diagrama (Nivel 2 — Contenedores)

El Nivel 2 muestra **cinco caminos** principales más los **legados simulados** como cajas **SaaS externas** (cluster «Legados simulados»). El **Flujo C (consulta tracking, escenario E8)** es la flecha **Azure API Management (APP-01) → BigQuery** — **no** pasa por **AKS (Orquestador de Pedidos (APP-02))** ni por **Azure SQL**.

#### ¿Dónde van los mocks? Nivel 1 vs Nivel 2 vs Nivel 3

En el MVP los mocks **no** son sistemas on premises reales ni SaaS desplegados aparte: son **rutas OpenAPI y políticas dentro de Azure API Management (APP-01)** (WMS, ERP, portal) o un **consumidor** sobre **Service Bus** (TMS). En C4 se dibujan en **distintos niveles** según el zoom:

| Nivel C4 | Qué muestra de los mocks | Ejemplo en la figura |
|---|---|---|
| **Nivel 1 — Contexto** | Vista **negocio**: legados como sistemas **externos** al MVP | Flechas MVP → mock WMS / ERP / Portal / TMS |
| **Nivel 2 — Contenedores** | Vista **integración**: mismos legados como cajas **SaaS externas** + tipo de flecha (HTTPS mock sync, HTTPS GET lectura, eventos async) | Cluster «Legados simulados»; OMS → APIM → mock-wms; Service Bus → mock-tms |
| **Nivel 3 — Componentes** | Vista **implementación**: adaptador concreto dentro de un contenedor | **WMS Adapter** en diagrama OMS (APP-02); consumidor TMS en diagrama PLT-03 |

> **Implementación física:** `mock-wms`, `mock-erp` y `mock-portal` son endpoints en **APP-01**; `mock-tms` es suscriptor de cola en **PLT-03**. Las cajas externas del Nivel 2 representan el **contrato** que simulan (APP-06, APP-25, APP-18, APP-11), no un despliegue aparte.

| Camino | Flechas en el diagrama | Flujo §3.3 | Escenario demo |
|---|---|---|---|
| **Alta de orden** | Cliente → APIM → AKS (Orquestador) → SQL / Event Hubs | Flujo A | E1–E3 |
| **Saga → legado WMS** | AKS (Orquestador) → APIM → **mock-wms** (SaaS externo APP-06) | Flujo A pasos 7–9 | E3, E4 |
| **Valorización ERP** | AKS (Orquestador) → APIM → **mock-erp** (SaaS externo APP-25) | Opcional demo | — |
| **Entrega offline** | Conductor → ALB → ECS → DynamoDB / S3 → puente → Event Hubs | Flujo B | E6–E7 |
| **Despacho TMS** | Service Bus → **mock-tms** (SaaS externo APP-11) | Flujo B paso 8 | — |
| **Consulta tracking (CQRS)** | Cliente → APIM → **BigQuery** + APIM → mock-portal (APP-18) | **Flujo C** | **E8** |
| **Escritura analítica (alimenta C)** | Event Hubs → Cloud Run → BigQuery | Flujos A + B (eventos previos) | — |
| **DLQ y replay (E5)** | Schema Validator → DLQ (§4.1 N3); Operaciones → Replay Controller (§4.1 N3); Operaciones → Azure Monitor (N2) | **Flujo D** | **E5** |

> **CQRS** (*Command Query Responsibility Segregation* — separar escritura y lectura): las **órdenes se escriben** en **Azure SQL** vía **Orquestador de Pedidos (APP-02)**; el **tracking se lee** desde **BigQuery** vía `mock-portal` en **Azure API Management (APP-01)**. Cloud Run proyecta eventos del bus hacia BigQuery; el cliente **no** interroga el OMS transaccional.

> **DLQ y replay (Flujo D):** en **N2** no se dibuja el camino interno «mensaje inválido → DLQ» — ocurre **dentro** del contenedor **Bus de Eventos Central (PLT-03)**. El zoom está en **§4.1** (DLQ Manager, Replay Controller). En **N2** sí aparece **Operaciones → Azure Monitor** (consulta métricas/DLQ); el **replay** disparado por operaciones se ve en **§4.1** (flecha Operaciones → Replay Controller).

> **Convención de lectura:** cada caja = **servicio cloud** · **nombre oficial** · **ID** (`APP` / `MS` / `PLT`) · flecha = tipo de integración (HTTPS API, HTTPS GET lectura, HTTPS móvil, eventos async). Catálogo detallado → §3.2 y flujos → §3.3.

#### ¿Cómo saber qué cajas tienen cosas **dentro** (Nivel 3)?

En C4 **no todas** las cajas del Nivel 2 son iguales. Hay **tres tipos**:

| Tipo en el diagrama N2 | Qué es | ¿Tiene zoom Nivel 3 en este MVP? | Cómo reconocerlo |
|---|---|:---:|---|
| **Contenedor de aplicación** | Ejecuta **lógica de negocio** desplegable (código, APIs, workers) | **Sí** — si hay diagrama en §4 | Nombre de **aplicación**, **microservicio** o **plataforma** con responsabilidad de proceso (no solo almacenar datos) |
| **Contenedor sin N3 dedicado** | Ejecuta lógica, pero en el MVP se **simplifica como mock** | **§4.5–§4.6** (texto) | Aparece en N2; columna «Nivel 3» apunta a vista mock |
| **Servicio de datos o infraestructura** | Almacén, cola administrada, balanceador, caché, secretos | **No** | Nombre del **proveedor** (Azure SQL, DynamoDB, Redis, ALB, Key Vault…) — **persistencia o red**, no código de dominio |

**Regla práctica:** si la caja es **donde corre tu código** (pods en AKS, tareas en ECS Fargate, funciones del bus) → **puede** tener Nivel 3. Si la caja es **donde se guarda o enruta** (SQL, S3, Event Hubs como servicio administrado) → en este proyecto **se queda en N2**; no abrimos componentes internos del producto de nube.

**Contenedores con zoom Nivel 3 completo (§4.1–§4.4 — PNG):**

| Caja en N2 | Contenedor lógico | ID | Diagrama N3 | Qué hay dentro (resumen) |
|---|---|---|---|---|
| **AKS — Orquestador** | **Orquestador de Pedidos (APP-02)** | APP-02 | **§4.2 Vista B** (PNG) | Order API, Saga, Dedup, Outbox, WMS Adapter… |
| **AKS — Inventario** | **Microservicio Inventario y Reservas (MS-INI01-02)** | MS-INI01-02 | **§4.4 Vista D** (PNG) | Reserve API, dominio reserva, outbox, conciliación… |
| **ECS Fargate** (+ ALB) | Backend móvil última milla | soporta APP-15 | **§4.3 Vista C** (PNG) | Delivery Handler, Outbox backend, Evidence, puente a Azure… |
| **Event Hubs + Service Bus** (+ workers) | **Bus de Eventos Central (PLT-03)** | PLT-03 | **§4.1 Vista A** (PNG) | Ingestion, Schema Validator, DLQ, Replay… |

**Contenedores simplificados en el MVP — zoom en texto (§4.5–§4.6) o dentro de otro N3:**

| Caja en N2 | ¿Merece zoom en TO BE? | Decisión en el MVP | Observación **mock / simplificación** |
|---|---|---|---|
| **Azure API Management (APP-01)** | **Sí** — gobierno API, políticas, enrutamiento y simulación de legados | **§4.5 Vista E** (texto) | **No** se despliegan **WMS Principal (APP-06)**, **ERP (APP-25)** ni **Portal B2B (APP-18)** reales: los **mocks son rutas OpenAPI + políticas XML** dentro del mismo **APP-01** (sin microservicio aparte ni VPN on premises). Facilita la demo sin migrar legado. |
| **Cloud Run** (proyector CQRS) | **Sí** — en producción habría proyector con reglas, dedup y varias tablas | **§4.6 Vista F** (texto) | **Proyector mínimo mock:** un solo handler que mapea eventos del bus → filas en **BigQuery** para `mock-portal`. Sin dominio analítico completo; basta para demostrar **CQRS** (escritura en Azure SQL, lectura en BigQuery). |

> **Regla para el comité:** si una caja del N2 **simula** un sistema legado o **proyecta lectura** sin ser el core transaccional, en el MVP se documenta con **vista mock en texto** (§4.5–§4.6) en lugar de un PNG de dominio DDD — el esfuerzo de implementación se concentra en **APP-02**, **MS-INI01-02**, **PLT-03** y backend móvil (§4.1–§4.4). El **Retry Worker** del backend móvil **no** es caja aparte en N2: vive **dentro del mismo task ECS Fargate** (§4.3).

**Cajas que no son contenedores de aplicación (solo infraestructura en N2):**

Azure SQL, Redis, DynamoDB, S3, BigQuery, SQS, EventBridge, Pub/Sub, Key Vault, Azure Monitor / CloudWatch / Cloud Logging, y las cajas **SaaS externas** del cluster «Legados simulados» (contrato simulado, no código interno del MVP).

> **Un AKS, dos contenedores:** en el cluster **AKS** corren **dos** workloads distintos — **Orquestador de Pedidos (APP-02)** y **Microservicio Inventario y Reservas (MS-INI01-02)** — por eso hay **dos cajas** en N2 con el mismo servicio cloud «AKS» pero IDs diferentes. Cada uno tiene su propio Nivel 3: §4.2 (APP-02) y §4.4 (MS-INI01-02).

### 3.2 Catálogo — servicio cloud → contenedor → qué es → para qué sirve

| Servicio en el diagrama | Nube | Contenedor / aplicación que corre ahí | Nivel 3 (§4) | Qué es el servicio cloud (resumen) | Para qué sirve en el MVP |
|---|---|---|---|---|---|
| **Azure API Management** | Azure | **Azure API Management (APP-01)** + mocks legados | **§4.5** (mock) | **API Gateway** PaaS de Azure: publica APIs REST, aplica OAuth/JWT, cuotas y políticas XML, enruta a backends y puede **simular respuestas** sin microservicio aparte. | Puerta de entrada única: OAuth, cuotas, `POST /api/v1/orders`, `GET mock-portal`, endpoints `mock-wms` / `mock-erp` / `mock-tms`. **Legados simulados en políticas APIM**, no sistemas aparte. |
| **AKS — Orquestador** | Azure | **Orquestador de Pedidos (APP-02)** | **§4.2** | **Azure Kubernetes Service**: plataforma administrada que ejecuta y orquesta **contenedores Docker** (despliegue, escalado, red interna, health checks). | Aplicación del catálogo (evoluciona a OMS): orden, idempotencia, Saga. |
| **AKS — Inventario** | Azure | **Microservicio Inventario y Reservas (MS-INI01-02)** | **§4.4** | Mismo servicio **AKS** (cluster compartido); aquí corre un **segundo contenedor** de negocio, aislado del Orquestador. | Microservicio de **INI-01**; ID **MS-INI01-02** sin **APP-XX**. Reserva, liberación y eventos de stock. |
| **Azure SQL** | Azure | Repositorio transaccional (**APP-02** + **MS-INI01-02**) | — | Base de datos **relacional administrada** (SQL Server en la nube): transacciones ACID, backups automáticos, réplicas y alta disponibilidad. | Fuente de verdad: órdenes, reservas, tabla **outbox**, historial de estados. |
| **Azure Cache for Redis** | Azure | Caché del **Orquestador de Pedidos (APP-02)** | — | Caché **en memoria** administrada compatible con Redis: lecturas de baja latencia, TTL y estructuras clave-valor sin golpear la BD. | Ventana de deduplicación, catálogos SLA, lecturas rápidas sin golpear SQL. |
| **Event Hubs** | Azure | **Bus de Eventos Central (PLT-03)** — stream | **§4.1** | **Streaming de eventos** de alto volumen: ingesta masiva en tiempo real, particiones y retención; los consumidores leen el flujo. | Ingesta de eventos canónicos (`OrderCreated`, `DeliveryCompleted`, …) en alto volumen. |
| **Service Bus** | Azure | **Bus de Eventos Central (PLT-03)** — colas/DLQ | **§4.1** | **Mensajería empresarial** administrada (colas, topics, suscripciones): entrega garantizada, reintentos, **DLQ** y desacoplamiento productor–consumidor. | Entrega por consumidor, reintentos, DLQ, replay auditado. |
| **Key Vault** | Azure | **Plataforma de Identidad y Accesos (IAM) (PLT-02)** (secretos) | — | Almacén seguro de **secretos, claves y certificados**; acceso por identidades gestionadas, rotación y auditoría — sin credenciales en código. | Claves API, connection strings del puente AWS→Azure; nada en código. |
| **Application Load Balancer** | AWS | Entrada HTTPS del backend móvil | — | Balanceador de carga **L7** de AWS: termina TLS, distribuye tráfico HTTP/HTTPS entre targets y ejecuta health checks. | Balanceo TLS hacia **ECS Fargate** (soporte **App de Conductores (APP-15)**). |
| **ECS Fargate** | AWS | Backend móvil última milla (API + handlers + Retry Worker) | **§4.3** | Ejecución **serverless de contenedores** en AWS: defines imagen, CPU y memoria; ECS orquesta tasks sin administrar servidores. | API REST de entrega, excepciones tipificadas, orquestación de evidencias y **reintento SQS en el mismo task**. |
| **DynamoDB** | AWS | Outbox backend + Ack Tracker | — | Base de datos **NoSQL** administrada (clave-valor/documento): escalado automático, baja latencia y consistencia configurable. | Cola **en AWS** tras sincronizar el móvil; reintentos hacia Azure si el puente falla. |
| **Amazon S3** | AWS | **Almacenamiento Evidencias (S3) (APP-16)** | — | **Almacenamiento de objetos** administrado: archivos (fotos, PDFs), alta durabilidad, versionado y cifrado en reposo. | Fotos, firmas, manifiesto; hash SHA-256 + cifrado KMS. |
| **Amazon SQS** | AWS | Buffer del puente móvil | — | **Cola de mensajes** administrada: buffer asíncrono entre componentes, absorbe picos y entrega at-least-once. | Desacopla picos de **App de Conductores (APP-15)** del hub Azure. |
| **EventBridge** | AWS | Publicador hacia Azure | — | **Bus de eventos** serverless de AWS: enruta eventos entre servicios AWS, reglas por patrón y destinos externos (incl. integración cross-cloud). | Enruta eventos móviles al **Event Hubs** (integración multinube). |
| **Pub/Sub** | GCP | Mensajería analítica | — | Mensajería **asíncrona administrada** de GCP: topics y suscripciones, entrega escalable en modo push o pull. | Entrada de eventos replicados hacia el consumidor GCP. |
| **Cloud Run** | GCP | Proyector CQRS | **§4.6** (mock) | Plataforma **serverless** para contenedores HTTP: escala a cero, pago por invocación; ideal para handlers ligeros sin cluster. | Handler mínimo: eventos → filas BigQuery para `mock-portal`. **No** es el motor analítico de producción. |
| **BigQuery** | GCP | Almacén de consultas CQRS | — | **Almacén de datos analítico** serverless: consultas SQL sobre datasets masivos, separado del transaccional (patrón CQRS lectura). | Tablas de lectura para `mock-portal` — sin consultar SQL transaccional. |
| **Azure Monitor** / **CloudWatch** / **Cloud Logging** | Multinube | **Plataforma de Observabilidad Unificada (PLT-01)** (parcial) | — | Servicios de **observabilidad** de cada nube: métricas, logs, alertas y (parcialmente) trazas distribuidas de apps e infraestructura. | Trazas/métricas con **correlation-id** end-to-end. |
| **mock-wms** (caja SaaS externa) | Simulado en **APP-01** | **WMS Principal (On Premises) (APP-06)** | — | **No es un servicio cloud**: contrato **simulado** en APIM que imita un WMS on premises (respuestas HTTP configurables). | Saga confirma reserva — **HTTPS mock sync** desde OMS vía APIM (Flujo A, E3–E4). |
| **mock-erp** (caja SaaS externa) | Simulado en **APP-01** | **ERP Financiero (On Premises) (APP-25)** | — | **No es un servicio cloud**: contrato **simulado** en APIM que imita un ERP on premises. | Valorización async — **HTTPS mock sync** (demo opcional). |
| **mock-portal** (caja SaaS externa) | Simulado en **APP-01** + lectura **BigQuery** | **Portal B2B (Trazabilidad) (APP-18)** | — | **No es un servicio cloud**: endpoint **simulado** en APIM; los datos de lectura vienen de **BigQuery** (CQRS). | Tracking **HTTPS GET lectura** — CQRS (Flujo C, E8). |
| **mock-tms** (caja SaaS externa) | Consumidor en **PLT-03** | **TMS (Transportation Management) (APP-11)** | — (consumidor en §4.1) | **No es un servicio cloud**: **consumidor simulado** en Service Bus que imita un TMS externo suscrito a eventos de despacho. | Recibe despacho — **eventos async** desde Service Bus (Flujo B). |

### 3.3 Ejemplos de flujo (cómo se usa el Nivel 2 en la demo)

Cada ejemplo recorre **servicios del diagrama** en orden, incluidas las cajas **SaaS externas** del cluster «Legados simulados».

---

#### Flujo A — Alta de orden y reserva (iniciativa **INI-01**, escenarios E1–E3)

**Actor:** Cliente B2B con Postman. Recorre el dominio **Orquestador de Pedidos (APP-02)** y el microservicio **Microservicio Inventario y Reservas (MS-INI01-02)** (ambos en AKS; solo **Orquestador de Pedidos (APP-02)** tiene ID de catálogo APP-XX).

```text
1. Cliente
      │  HTTPS API
      ▼
2. Azure API Management          ← APP-01: valida token, rate limit, enruta POST /api/v1/orders
      │  REST interno
      ▼
3. AKS (Orquestador)             ← APP-02: dedup + idempotency-key + persiste orden
      ├──────────────► Azure SQL  ← fila orden + fila outbox (misma transacción)
      ├──────────────► Azure Cache for Redis  ← marca hash logístico en ventana temporal
      │
      │  worker lee outbox
      ▼
4. Event Hubs                    ← PLT-03: publica OrderValidated
      ▼
5. Service Bus                   ← entrega OrderValidated a cola de MS-INI01-02 (eventos async)
      │  eventos async
      ▼
6. AKS (Inventario)              ← MS-INI01-02: Reserve Handler consume cola, reserva stock, SQL + outbox
      ├──────────────► Azure SQL
      └──────────────► Event Hubs  ← InventoryReserved

7. AKS (Orquestador)             ← APP-02 Saga Orchestrator: tras reserva OK, confirma en WMS simulado
      │  HTTPS mock sync
      ▼
8. Azure API Management (APP-01) ← enruta a política mock-wms
      │  mock-wms
      ▼
9. mock-wms (SaaS externo)       ← simula WMS Principal (APP-06); respuesta 200 / 503 / timeout (E3–E4)
```

**Qué demuestra:** orden no duplicada (Redis + idempotencia), reserva consistente (SQL), eventos desacoplados (Event Hubs → Service Bus → **MS-INI01-02**), confirmación WMS **síncrona en la Saga** (pasos 7–9). La compensación `ReleaseInventory` (mock-wms 503) va por **HTTPS interno** OMS → MS-INI01-02.

> **Flechas en N2 (ambas explícitas en el PNG):**
> - `Service Bus → AKS Inventario` — reserva async (pasos 5–6).
> - `AKS Orquestador → APIM → mock-wms` — **HTTPS mock sync** de la Saga (pasos 7–9); **no** sale del Inventario, sale del **Orquestador de Pedidos (APP-02)**.

---

#### Flujo B — Entrega offline y evidencia (iniciativa **INI-03**, escenarios E6–E7)

**Actor:** Conductor sin red 4G en zona de entrega; luego recupera conectividad hacia AWS (no necesariamente hacia Azure). Materializa las aplicaciones **App de Conductores (APP-15)** y **Almacenamiento Evidencias (S3) (APP-16)**.

> **Aclaración importante:** «Sin red» **no** significa escribir directo en DynamoDB ni en S3. Sin conectividad, todo queda en el **dispositivo** (outbox local cifrado). DynamoDB y S3 solo intervienen cuando la aplicación **ya puede** hablar con el backend AWS (ALB → ECS Fargate). «Sin red al hub» se refiere a que el **puente AWS → Azure** puede fallar aunque AWS haya recibido la entrega.

**Fase 1 — Sin conectividad (solo dispositivo)**

```text
1. App de Conductores (APP-15)
      │  captura firma, foto, GPS, timestamp
      ▼
2. Outbox local cifrado (dispositivo)   ← SQLite / almacenamiento local (INI-03 RF-02)
      │  evento + evidencia quedan PENDING en el teléfono
      ▼
3. UI confirma al conductor              ← puede cerrar la app; datos persisten localmente
```

**Fase 2 — Recupera red hacia AWS (sincronización store-and-forward)**

```text
4. App de Conductores (APP-15)
      │  HTTPS móvil (lote ordenado de eventos pendientes)
      ▼
5. Application Load Balancer → ECS Fargate   ← POST /deliveries/{id}/complete (+ evidencias)
      ├──────────────► DynamoDB              ← outbox **del backend**: evento PENDING hacia Azure
      └──────────────► Amazon S3             ← **Almacenamiento Evidencias (S3) (APP-16)**: foto/firma + hash
      │
      │  backend responde ACK al móvil
      ▼
6. App de Conductores (APP-15)             ← borra copia local **solo** tras confirmación (INI-03 RF-04)
```

**Fase 3 — Puente hacia Azure (puede fallar aunque Fase 2 haya terminado)**

```text
7. Amazon SQS → EventBridge                  ← buffer + enrutamiento
      │  eventos async (puente multinube)
      ▼
8. Event Hubs (Azure)                        ← DeliveryCompleted entra al PLT-03
      ├──────────────► Service Bus           ← mock TMS (APP-11), otros consumidores
      └──────────────► Cloud Run → BigQuery  ← actualiza proyección CQRS
```

**Qué demuestra:** sin red el conductor **no pierde** la entrega (outbox **local** cifrado); al reconectar con AWS, el backend persiste en **DynamoDB** y **S3** y confirma al móvil; el hub Azure se entera **después** vía puente, sin que **App de Conductores (APP-15)** hable directo con Event Hubs.

| Capa | Dónde vive | Cuándo se usa |
|---|---|---|
| **Outbox local (dispositivo)** | Teléfono del conductor, cifrado | Sin conectividad — RF-02, RF-03 |
| **Outbox backend (DynamoDB)** | AWS, tras recibir el lote del móvil | Red hacia AWS OK, puente a Azure pendiente o en retry |
| **Evidencias (S3)** | AWS | Cuando el móvil sube el lote a ECS (no en modo 100 % offline) |
| **Puente (SQS → EventBridge → Event Hubs)** | AWS → Azure | Cuando hay conectividad multinube hacia el hub |

---

#### Flujo C — Consulta de tracking (CQRS, escenario E8)

**Actor:** Cliente B2B consulta estado del pedido.

```text
1. Cliente
      │  HTTPS GET lectura
      ▼
2. Azure API Management          ← mock-portal (simula Portal B2B Trazabilidad APP-18)
      │  consulta SQL analítico (no transaccional)
      ▼
3. BigQuery                      ← fila proyectada por Cloud Run desde eventos previos
```

**Qué demuestra:** la lectura **no** interroga **Azure SQL** ni bloquea **AKS (Orquestador)**. El estado visible al cliente viene de la **proyección** alimentada por **Flujo A** y **Flujo B**.

---

#### Flujo D — Mensaje inválido y recuperación (iniciativa **INI-02**, escenario E5)

Valida patrones de resiliencia del **Bus de Eventos Central (PLT-03)** (plataforma, no aplicación de negocio aislada).

```text
1. AKS (Orquestador o Inventario) publica evento mal formado
      ▼
2. Event Hubs → Service Bus          ← visible en N2 (misma caja PLT-03)
      ▼
3. Schema Validator → DLQ Manager    ← DENTRO de PLT-03 — zoom §4.1 N3 (no flecha aparte en N2)
      │  mensaje a cola de fallidos con payload y causa
      ▼
4. Operaciones / Soporte
      ├─ HTTPS monitoreo ──► Azure Monitor (PLT-01)   ← flecha en N2: consulta DLQ / métricas
      └─ HTTPS monitoreo ──► Replay Controller (PLT-03)  ← flecha en §4.1 N3: replay auditado
            ▼
5. Replay Controller → Event Router  ← reprocesa tras corregir contrato (§4.1)
```

| Paso | ¿Dónde se ve en C4? | Qué mirar |
|---|---|---|
| 1–2 | **N2** | Publicación normal OMS/Inventario → Event Hubs → Service Bus |
| 3 (DLQ) | **N3 §4.1** | Schema Validator rechaza → DLQ Manager (Service Bus DLQ) |
| 4 (consulta) | **N1 y N2** | Operaciones → MVP / Azure Monitor — **HTTPS monitoreo** |
| 4–5 (replay) | **N3 §4.1** | Operaciones → Replay Controller → Router |

**Qué demuestra:** resiliencia del **Bus de Eventos Central (PLT-03)** — no se pierden mensajes en campaña (caso Cyber Days). El **DLQ no es un contenedor aparte en N2**: es componente interno del bus (§4.1).

---

### 3.4 Mapa rápido flechas del diagrama

| Flecha en el diagrama | Significado |
|---|---|
| Cliente → **Azure API Management** | **HTTPS API** — una sola puerta (**APP-01**): `POST` órdenes hacia AKS; `GET mock-portal` consulta **BigQuery** (CQRS, E8) |
| **Azure API Management** → **BigQuery** | `mock-portal` en APP-01 consulta la **proyección CQRS** (Flujo C / E8) |
| **AKS (Orquestador)** → **Azure API Management** → **mock-wms** | **HTTPS mock sync** — Saga confirma reserva con **WMS Principal (APP-06)** simulado |
| **AKS (Orquestador)** → **Azure API Management** → **mock-erp** | **HTTPS mock sync** — valorización **ERP Financiero (APP-25)** simulado |
| **Azure API Management** → **mock-portal** (SaaS externo) | Simula contrato **Portal B2B (Trazabilidad) (APP-18)**; datos desde BigQuery |
| **Service Bus** → **AKS (Inventario)** | **Eventos async** — cola **MS-INI01-02** recibe `OrderValidated` (Flujo A pasos 5–6) |
| **Service Bus** → **mock-tms** (SaaS externo) | **Eventos async** — despacho / manifiesto **TMS (APP-11)** simulado |
| **AKS (Orquestador)** → **AKS (Inventario)** | **HTTPS interno** — solo `ReleaseInventory` (compensación Saga si mock-wms falla) |
| Conductor → **ALB** → **ECS Fargate** | HTTPS móvil — entregas y evidencias |
| **AKS** ↔ **Azure SQL** | Lectura/escritura transaccional + outbox |
| **AKS** → **Event Hubs** | Publicación de eventos tras commit |
| **Event Hubs** → **Service Bus** | Enrutamiento a colas por consumidor |
| **ECS Fargate** → **SQS** → **EventBridge** → **Event Hubs** | Puente multinube AWS→Azure |
| **Event Hubs** → **Cloud Run** → **BigQuery** | Proyección **CQRS** (escritura analítica — alimenta el Flujo C) |
| **Operaciones** → **Azure Monitor (PLT-01)** | **HTTPS monitoreo** — consulta DLQ, métricas, alertas (Flujo D paso 4) |
| **Schema Validator → DLQ** (dentro PLT-03) | Solo en **§4.1 N3** — mensaje inválido a cola de fallidos (Flujo D paso 3) |
| **Operaciones → Replay Controller** (dentro PLT-03) | Solo en **§4.1 N3** — replay auditado tras corregir contrato (Flujo D pasos 4–5) |

### 3.5 Catálogo de contenedores (referencia C4)

> Detalle por **contenedor lógico** (nombre de negocio + ID). Los contenedores con **APP-XX** son aplicaciones del portafolio; **MS-INI01-02** es microservicio de **INI-01** sin ID APP-XX; **PLT-03** es plataforma. Ver §0.1.

| Contenedor | Nube | Tecnología | Responsabilidad |
|---|---|---|---|
| Azure API Management (APP-01) y Mocks | Azure | API Management | Entrada única, OAuth, rate limit; mocks **WMS Principal (On Premises) (APP-06)**, **ERP Financiero (On Premises) (APP-25)**, **Portal B2B (Trazabilidad) (APP-18)**, **TMS (Transportation Management) (APP-11)** |
| Orquestador de Pedidos (APP-02) — OMS centralizado | Azure | AKS + .NET/Node | Evolución **Orquestador de Pedidos (APP-02)**: orden, idempotencia, dedup, estado canónico |
| Microservicio Inventario y Reservas (MS-INI01-02) | Azure | AKS | Disponibilidad, reserva, liberación, conciliación — microservicio **INI-01** con ID **MS-INI01-02** (sin **APP-XX**; distinto de **Control de Inventario (APP-08)**) |
| Repositorio transaccional | Azure | Azure SQL | Órdenes, inventario, outbox, historial estados |
| Bus de Eventos Central (PLT-03) | Azure | Event Hubs + Service Bus | Ingesta, streaming, colas, DLQ, replay |
| Caché operativa | Azure | Redis | SLA, catálogos, ventana deduplicación |
| Backend móvil | AWS | ECS Fargate | Store-and-forward, sync, API entrega, retry SQS (mismo task) |
| Estado móvil / outbox backend | AWS | DynamoDB | Eventos recibidos del móvil pendientes de puente a Azure; registro de acks |
| Evidencias | AWS | S3 + KMS | Fotos, firmas, hash SHA-256 — **Almacenamiento Evidencias (S3) (APP-16)** |
| Puente móvil | AWS | SQS + EventBridge | Buffer hacia Azure Event Hubs |
| Consumidor analítico | GCP | Cloud Run | Proyección eventos a BigQuery |
| Almacén consultas | GCP | BigQuery | Modelo lectura CQRS tracking/SLA |
| Mensajería analítica | GCP | Pub/Sub | Entrada eventos desde puente |
| Observabilidad | Multinube | OpenTelemetry + Monitor/CloudWatch/Logging | Correlation ID end-to-end |
| Identidad y secretos | Azure/AWS/GCP | Entra ID, Key Vault, IAM, Secret Manager | **Plataforma de Identidad y Accesos (IAM) (PLT-02)** federado |

### 3.6 Vista resumen (una línea)

```text
Cliente → Azure API Management → AKS (Orquestador) → Azure SQL / Event Hubs → Service Bus
         │                              │
         │                              └── HTTPS mock sync → APIM → mock-wms (APP-06) / mock-erp (APP-25)
                                      ↓
                    AKS (Inventario) ←┘
Conductor → [outbox local] → ALB → ECS Fargate → DynamoDB / S3 → SQS → EventBridge → Event Hubs
Service Bus → mock-tms (APP-11)
Event Hubs → Cloud Run → BigQuery ← Azure API Management (GET mock-portal, E8 CQRS) → mock-portal (APP-18)
```

---

## 4. Nivel 3 — Diagramas de Componentes (detalle tipo cuadro)

En el nivel 3 hacemos **zoom en un contenedor**. Presentamos **cuatro vistas con PNG** (workloads transaccionales del MVP — §4.1–§4.4) y **dos vistas en texto** para componentes **simplificados como mock** en el MVP (§4.5–§4.6), con el estilo de **arquitectura física por zonas**.

---

### 4.0 Guía detallada — cómo leer los diagramas de Nivel 3

Esta sección es la **guía maestra** del Nivel 3 para el comité. Incluye **seis explicaciones detalladas** — una por diagrama — en **§4.0.1 a §4.0.6**. Las secciones **§4.1 a §4.6** conservan tablas técnicas y referencia formal; **empiece por §4.0** para entender cada PNG antes del detalle.

Cada vista profundiza **un solo contenedor** del Nivel 2; las cajas **fuera del recuadro en foco** son **vecinos** (otros contenedores o actores), no componentes internos.

#### ¿Qué es el Nivel 3 en este MVP?

| Concepto | Significado en el paquete Hito 3 |
|---|---|
| **Un diagrama N3** | Zoom **dentro** de un contenedor N2 (un workload desplegable) |
| **Caja «CONTENEDOR EN FOCO»** | Donde vive el **código** del dominio — APIs, handlers, repositorios, outbox |
| **Cajas externas (arriba/abajo/lados)** | Contenedores **vecinos** con los que se integra — APIM, Event Hubs, OMS, SQL, conductor |
| **Zonas internas** | Agrupación lógica (API, Dominio DDD, Aplicación, Infraestructura…) — no son servicios cloud distintos |
| **PNG vs texto** | PNG = dominio transaccional completo; texto = mock o proyector mínimo (§4.5–§4.6) |

#### Catálogo de las seis vistas

| Vista | Contenedor en foco | ID | Formato | Iniciativa | Flujo §3.3 |
|---|---|---|---|---|---|
| **§4.1 A** | **Bus de Eventos Central (PLT-03)** | PLT-03 | PNG | INI-02 | A, B, D |
| **§4.2 B** | **Orquestador de Pedidos (APP-02)** | APP-02 | PNG | INI-01 | A |
| **§4.3 C** | Backend móvil última milla | soporta APP-15 | PNG | INI-03 | B |
| **§4.4 D** | **Microservicio Inventario y Reservas (MS-INI01-02)** | MS-INI01-02 | PNG | INI-01 | A |
| **§4.5 E** | **Azure API Management (APP-01)** + mocks | APP-01 | Texto | INI-02 | A, C |
| **§4.6 F** | Proyector CQRS | Cloud Run GCP | Texto | INI-02 / CQRS | C |

**Archivos PNG** (carpeta `diagramas_c4/imagenes/`):

| PNG | Vista |
|---|---|
| `mvp_c4_n3_plt03_componentes.png` | §4.1 — Bus |
| `mvp_c4_n3_oms_componentes.png` | §4.2 — OMS |
| `mvp_c4_n3_mobile_componentes.png` | §4.3 — Móvil |
| `mvp_c4_n3_inventario_componentes.png` | §4.4 — Inventario |

#### Convenciones visuales (todas las figuras N3)

1. **Tres líneas por caja:** (1) servicio cloud del proveedor; (2) nombre oficial; (3) ID `APP` / `MS` / `PLT` o rol.
2. **Cluster «CONTENEDOR EN FOCO»:** borde grueso en el PNG — solo ahí hay componentes de software del dominio.
3. **Flechas entrantes** desde fuera = integración con vecinos; **flechas internas** = llamadas entre componentes del mismo pod/task.
4. **Tipos de flecha** (misma regla que §1.1):
   - **HTTPS API / HTTPS mock sync / HTTPS móvil / HTTPS monitoreo** — síncrono, espera respuesta.
   - **Eventos async** — publicación o consumo vía **Bus de Eventos Central (PLT-03)** (Event Hubs / Service Bus).
5. **Un AKS, dos contenedores:** §4.2 (APP-02) y §4.4 (MS-INI01-02) son **diagramas separados** del mismo cluster Azure AKS.

#### Cómo se relacionan entre sí (mapa de vecinos)

```text
                    ┌── APP-01 (§4.5) ── mock-wms / mock-portal
                    │
Cliente B2B ────────┤
                    │
                    ▼
              ┌─────────────┐     HTTPS interno          ┌──────────────────┐
              │  APP-02     │ ─── ReleaseInventory ────► │  MS-INI01-02     │
              │  (§4.2)     │                            │  (§4.4)          │
              └──────┬──────┘                            └────────┬─────────┘
                     │ publica / Saga                            │ publica / consume
                     ▼                                             ▼
              ┌─────────────────────────────────────────────────────────────┐
              │           PLT-03 Bus de Eventos Central (§4.1)               │
              │  Event Hubs ◄──► Service Bus ◄──► DLQ / Replay               │
              └──────┬──────────────────────┬──────────────────┬────────────┘
                     │                      │                  │
         cola inventario              mock-tms          puente AWS / GCP
                     │                      │                  │
                     ▼                      ▼                  ▼
              MS-INI01-02 (§4.4)      APP-11 simulado   §4.3 móvil ──► §4.6 BQ
```

**Lectura clave:** la reserva de stock **happy path** no va APP-02 → MS-INI01-02 por HTTPS; va **PLT-03 (Service Bus) → MS-INI01-02** (§4.1 + §4.4). El HTTPS OMS → Inventario es **solo** `ReleaseInventory` (compensación).

#### Recorrido por flujo de demo (qué diagrama abrir primero)

| Si el comité pregunta… | Diagrama | Guía detallada |
|---|---|---|
| ¿Cómo entra la orden y no se duplica? | **§4.2 OMS** | **§4.0.2** |
| ¿Cómo se reserva inventario? | **§4.4 + §4.1** | **§4.0.4** y **§4.0.1** |
| ¿Cómo confirma el WMS sin on premises? | **§4.2 + §4.5** | **§4.0.2** y **§4.0.5** |
| ¿Cómo funciona el bus y el DLQ? | **§4.1 Bus** | **§4.0.1** |
| ¿Cómo entrega offline el conductor? | **§4.3 Móvil** | **§4.0.3** |
| ¿Cómo consulto tracking sin golpear SQL? | **§4.6 + §4.5** | **§4.0.6** y **§4.0.5** |

---

#### 4.0.1 Diagrama N3 — **Bus de Eventos Central (PLT-03)**

**Archivo:** `mvp_c4_n3_plt03_componentes.png` · **Vista formal:** [§4.1](#41-vista-a--contenedor-bus-de-eventos-central-plt-03-en-azure) · **Iniciativa:** INI-02 · **Flujos:** A, B, D · **¿Se implementa?** **Sí** — Event Hubs + Service Bus + workers en AKS.

![Guía N3 — Bus PLT-03](diagramas_c4/imagenes/mvp_c4_n3_plt03_componentes.png)

**Qué es este diagrama**  
Zoom **dentro** de la plataforma **Bus de Eventos Central (PLT-03)**. En N2 solo ves dos cajas («Event Hubs» y «Service Bus»); aquí se abre el **código** que valida, enruta, reintenta y entrega mensajes.

**Cajas FUERA del recuadro (vecinos — no son parte del bus)**

| Vecino | Posición típica en el PNG | Rol |
|---|---|---|
| **Orquestador de Pedidos (APP-02)** | Arriba — productor | Publica `OrderValidated`, `ReservationConfirmed`, etc. |
| **Microservicio Inventario y Reservas (MS-INI01-02)** | Arriba — productor y consumidor | Publica `InventoryReserved`; **consume** cola `OrderValidated` |
| **Backend móvil AWS** | Arriba — productor | Publica `DeliveryCompleted` tras el puente SQS→EventBridge |
| Adaptador CSV / mocks | Arriba — productor opcional | Eventos normalizados de legado simulado |
| **mock TMS (APP-11)** | Abajo — consumidor | Recibe despacho por cola Service Bus |
| **Proyector GCP (Cloud Run)** | Abajo — consumidor | Lee stream Event Hubs → BigQuery |
| **Azure Monitor (PLT-01)** | Abajo — observabilidad | Auditoría de eventos y DLQ |
| **Operaciones / Soporte** | Lateral — actor | Dispara **replay auditado** al Replay Controller |

**Recorrido del diagrama — leer en este orden**

1. **Productores → Event Ingestion API** (flecha «publica»): varios sistemas envían eventos **sin conocer** quién consume — patrón EDA.
2. **Schema Validator**: si el JSON no cumple contrato **AsyncAPI**, el mensaje **no** sigue al stream — va a DLQ (Flujo D, escenario E5).
3. **Event Router + Ordering Guard**: enruta por dominio/SLA y mantiene **orden por agregado** (misma `order_id` en la misma partición) — crítico para entregas móviles fuera de secuencia.
4. **Event Hubs** (stream): copia canónica de alto volumen — alimenta analítica y replay.
5. **Retry Scheduler → Service Bus** (colas): entrega **por consumidor** con reintentos y **ACK**; aquí sale la flecha **cola MS-INI01-02** hacia inventario (Flujo A pasos 5–6).
6. **DLQ Manager**: mensajes que agotan reintentos — **no se pierden** (caso Cyber Days 240k mensajes).
7. **Replay Controller**: **Operaciones** lo activa por **HTTPS monitoreo**; reprocesa desde DLQ con auditoría (Flujo D).
8. **Backpressure Controller**: si mock **WMS Principal (APP-06)** está degradado, **ralentiza** ingesta para no tumbar el OMS.

**Zonas internas del recuadro**

| Zona en el PNG | Qué mirar | Para qué sirve |
|---|---|---|
| Entrada y validación | Ingestion API, Schema Validator | Puerta única de eventos al hub |
| Núcleo EDA | Router, Ordering Guard | Enrutamiento y secuencia |
| Resiliencia | Retry, DLQ, Replay, Backpressure | INI-02 — patrón **Resiliencia** del MVP |
| Persistencia | Event Hubs, Service Bus, Registro auditoría | Stream + colas + trazabilidad |

**Mensaje para el comité:** el bus **complementa** las APIs síncronas (Saga→mock-wms); **no las reemplaza**. Desacopla inventario, TMS, móvil y GCP.

**Enlace N2:** la flecha `Service Bus → AKS Inventario` y `Service Bus → mock-tms` del diagrama de contenedores **nacen aquí**, en los dispatchers de salida.

---

#### 4.0.2 Diagrama N3 — **Orquestador de Pedidos (APP-02)**

**Archivo:** `mvp_c4_n3_oms_componentes.png` · **Vista formal:** [§4.2](#42-vista-b--contenedor-oms-centralizado--orquestador-de-pedidos-app-02--dominio-orden-en-azure-aks) · **Iniciativa:** INI-01 · **Flujo:** A · **¿Se implementa?** **Sí** — workload en AKS (aplicación del catálogo).

![Guía N3 — OMS APP-02](diagramas_c4/imagenes/mvp_c4_n3_oms_componentes.png)

**Qué es este diagrama**  
Zoom **dentro** del contenedor **Orquestador de Pedidos (APP-02)** — dominio **Orden** (OMS centralizado). Es el **corazón transaccional** del MVP en Azure: alta de órdenes, deduplicación, Saga y publicación de eventos.

**Cajas FUERA del recuadro**

| Vecino | Rol en el diagrama |
|---|---|
| **Azure API Management (APP-01)** | Entrada `POST /api/v1/orders` y consultas Query API |
| **Azure SQL** | Persistencia de órdenes y tabla **outbox** |
| **Event Hubs (PLT-03)** | Destino de eventos publicados tras commit SQL |
| **mock WMS (APP-06)** | Destino **HTTPS mock sync** de la Saga |
| **Microservicio Inventario (MS-INI01-02)** | Solo **ReleaseInventory** por HTTPS (compensación) |

**Recorrido del diagrama — leer en este orden**

1. **APIM → Order API** (`HTTPS API`): llega la orden del cliente B2B con `Idempotency-Key`.
2. **Correlation Middleware**: propaga `correlation_id` para trazas end-to-end (PLT-01).
3. **Create Order Handler → Dedup Engine + Idempotency Guard**: evita los **32.000 duplicados** del caso AS IS (hash logístico + clave de idempotencia).
4. **Order Aggregate + State Machine → Order Repository → SQL**: estado canónico `CREATED` → `VALIDATED` → …
5. **Outbox Table → Event Publisher → Event Hubs**: patrón **outbox** — el evento `OrderValidated` solo se publica si el commit SQL fue exitoso (§1.2).
6. **Saga Orchestrator → WMS Adapter → mock-wms** (`HTTPS mock sync`): paso **síncrono** obligatorio — confirmar reserva en WMS simulado (Flujo A pasos 7–9). Si responde 503 → compensación.
7. **Saga → Inventory Client → MS-INI01-02** (`HTTPS interno`, **solo** `ReleaseInventory`): **no** es la reserva happy path; la reserva va por **Service Bus** (§4.0.1 / §4.0.4).
8. **Query API → Repository**: lecturas operativas ligeras — **distinto** del `mock-portal` CQRS en BigQuery.

**Zonas internas**

| Zona | Componentes clave | Patrón MVP |
|---|---|---|
| Capa API | Order API, Query API | API REST INI-02 |
| Dominio DDD | Order Aggregate, Dedup, Idempotency | **DDD** |
| Aplicación | Create Handler, **Saga Orchestrator** | **Saga** |
| Infraestructura | Repository, Outbox, Event Publisher | **Outbox** + **EDA** |
| Integración | WMS Adapter, Inventory Client | Solo donde Saga exige sync |
| Resiliencia | Circuit Breaker | Hacia mock-wms degradado (E4) |

**Mensaje para el comité:** aquí viven **idempotencia, dedup y Saga** — INI-01. Una orden entra una sola vez y la Saga coordina pasos **sin** una transacción distribuida única.

**Enlace N2:** caja **AKS — Orquestador**; flechas hacia SQL, Redis, Event Hubs, APIM (mock-wms).

---

#### 4.0.3 Diagrama N3 — **Backend Móvil Última Milla (AWS)**

**Archivo:** `mvp_c4_n3_mobile_componentes.png` · **Vista formal:** [§4.3](#43-vista-c--contenedor-backend-móvil-última-milla-en-aws) · **Iniciativa:** INI-03 · **Flujo:** B · **¿Se implementa?** **Sí** — un servicio **ECS Fargate** en AWS (soporta **App de Conductores (APP-15)**).

![Guía N3 — Backend móvil](diagramas_c4/imagenes/mvp_c4_n3_mobile_componentes.png)

**Qué es este diagrama**  
Zoom **dentro** del **backend móvil en AWS**. La **App de Conductores (APP-15)** no publica eventos directo a Azure: habla **HTTPS móvil** con este backend, y el backend **traduce** a eventos y evidencias.

**Decisión MVP:** un solo **task ECS Fargate** — Delivery Handler, Evidence, **Retry Worker** en el mismo despliegue (sin Lambda aparte).

**Cajas FUERA del recuadro**

| Vecino | Rol |
|---|---|
| **App de Conductores (APP-15)** | Actor conductor — dispositivo móvil |
| **Outbox local cifrado** (SQLite en teléfono) | Fase offline — **no** es AWS; es el dispositivo |
| **Amazon S3 (APP-16)** | Evidencias (foto, firma) |
| **DynamoDB** | Outbox **del backend** + Ack Tracker |
| **SQS + EventBridge** | Buffer y publicador del puente a Azure |
| **Event Hubs (PLT-03)** | Destino final en el hub Azure |
| **CloudWatch (PLT-01)** | Trazas del backend |

**Recorrido del diagrama — tres fases**

**Fase offline (solo dispositivo — arriba del recuadro)**  
1. Conductor captura entrega **sin red** → **outbox local cifrado** en el teléfono (INI-03 RF-02).  
2. La UI confirma al conductor; los datos **persisten en el móvil**.

**Fase sync hacia AWS (entra al recuadro)**  
3. Con red → **ALB → Delivery API** (`HTTPS móvil`, lote store-and-forward).  
4. **Delivery Handler** valida excepciones con **Exception Taxonomy Validator** (lista cerrada, no texto libre).  
5. Escribe en **Outbox DynamoDB** (estado PENDING hacia Azure).  
6. **Evidence Orchestrator → S3 + Hash Verifier SHA-256**: integridad de evidencias (caso 1.200 firmas perdidas).  
7. **Delivery API → móvil (ACK)**: el teléfono **borra** la copia local solo tras ACK del backend (INI-03 RF-04) — ver **Ack Tracker**.

**Fase puente a Azure (sale del recuadro)**  
8. **SQS Outbox Relay → Retry Worker** (mismo task ECS, polling con jitter) → **EventBridge → Event Hubs**.  
9. Si el puente falla, el Retry Worker reintenta sin perder el evento en DynamoDB.

**Zonas internas**

| Zona | Qué demuestra al comité |
|---|---|
| Canal | ALB + Delivery API — única entrada HTTPS del móvil |
| Dominio entrega | Handlers de negocio INI-03 |
| Evidencias | S3 + hash — **Almacenamiento Evidencias (APP-16)** |
| Integración Azure | SQS Relay + EventBridge — multinube async |
| Resiliencia | Retry Worker en el mismo ECS + Ack Tracker |

**Mensaje para el comité:** «Sin red, todo en el teléfono; con red, AWS confirma al conductor; Azure se entera **después** por el puente.»

**Enlace N2:** caja **ECS Fargate** + ALB; flechas a DynamoDB, S3, SQS, Event Hubs.

---

#### 4.0.4 Diagrama N3 — **Microservicio Inventario y Reservas (MS-INI01-02)**

**Archivo:** `mvp_c4_n3_inventario_componentes.png` · **Vista formal:** [§4.4](#44-vista-d--contenedor-microservicio-inventario-y-reservas-ms-ini01-02-en-azure-aks) · **Iniciativa:** INI-01 · **Flujo:** A · **¿Se implementa?** **Sí** — segundo workload en el mismo AKS que APP-02 (ID **MS-INI01-02**, **no** APP-XX).

![Guía N3 — Inventario MS-INI01-02](diagramas_c4/imagenes/mvp_c4_n3_inventario_componentes.png)

**Qué es este diagrama**  
Zoom **dentro** del microservicio de **dominio Inventario** — reservas, liberaciones, conciliación. **No** es **Control de Inventario (APP-08)** legado ni **WMS Principal (APP-06)**.

**Cajas FUERA del recuadro**

| Vecino | Rol |
|---|---|
| **Service Bus (PLT-03)** | Entrega `OrderValidated` → **Reserve Handler** (happy path) |
| **Orquestador de Pedidos (APP-02)** | Llama **Release API** solo para compensación |
| **Azure SQL** | Tablas `inventory_position`, `inventory_reservation`, outbox |
| **Event Hubs (PLT-03)** | Publica `InventoryReserved` / `InventoryInsufficient` |
| Eventos WMS (mock) | Entrada a Movement Handler (F-INV-02) |

**Recorrido del diagrama — leer en este orden**

1. **Service Bus → Reserve Handler** (`eventos async`): trigger principal de reserva — Flujo A pasos 5–6.  
2. **Idempotency Guard + Inventory Aggregate + Reservation Policy**: reglas RF-06 a RF-09; no reservar sin disponibilidad.  
3. **Position Repository + Reservation Repository → SQL** con **Optimistic Lock**: control de versión en picos Cyber Days.  
4. **Outbox → Event Publisher → Event Hubs**: `InventoryReserved` o rechazo — misma transacción SQL (outbox).  
5. **Release API ← APP-02** (`HTTPS interno`): `ReleaseInventory` si mock-wms falla en la Saga.  
6. **Movement Handler**: movimientos auditables (F-INV-02).  
7. **Reconciliation Handler + Conflict Rules**: conciliación WMS local vs canónico (F-INV-03); **Backpressure Gate** si WMS degradado.

**Zonas internas**

| Zona | Componentes |
|---|---|
| API | Reserve API, Release API, Availability Query API |
| Dominio DDD | Inventory Aggregate, Reservation Policy, Conflict Rules |
| Aplicación | Reserve / Release / Movement / Reconciliation Handlers |
| Infraestructura | Repositories, Outbox, Event Publisher |
| Resiliencia | Idempotency, Optimistic Lock, Backpressure |

**Mensaje para el comité:** inventario es un **microservicio hermano** del OMS en el mismo cluster AKS, pero con **ID propio MS-INI01-02**. La reserva **entra por el bus**, no por HTTPS desde el OMS.

**Enlace N2:** caja **AKS — Inventario**; flecha `Service Bus → Inventario` + SQL + Event Hubs.

---

#### 4.0.5 Vista N3 — **Azure API Management (APP-01) + mocks**

**Formato:** texto (sin PNG) · **Vista formal:** [§4.5](#45-vista-e--contenedor-azure-api-management-app-01--gateway-y-mocks-de-legado) · **Iniciativa:** INI-02 · **Flujos:** A, C · **¿Se implementa?** **Sí** — gateway real + **mocks** OpenAPI/políticas XML (no legados on premises).

**Qué es esta vista**  
Zoom **dentro** de **Azure API Management (APP-01)**. En el MVP **no** se despliegan WMS, ERP ni portal reales: las rutas `mock-wms`, `mock-erp`, `mock-portal` son **políticas dentro del mismo APP-01**.

**Estructura lógica (leer como diagrama mental)**

```text
                    ┌─ Global policies (JWT, rate limit, correlation-id)
Cliente B2B ────────┤
                    ├─ POST /api/v1/orders ──────────► AKS Orquestador (APP-02)     [HTTPS API]
                    ├─ mock-wms  ◄── Saga APP-02 ────► política 200/503/timeout    [HTTPS mock sync]
                    ├─ mock-erp  ◄── opcional ───────► 202 Accepted               [HTTPS mock sync]
                    └─ mock-portal GET tracking ─────► consulta BigQuery          [HTTPS GET lectura]
```

**Recorrido por ruta**

| Ruta | Quién llama | Qué demuestra |
|---|---|---|
| `POST /api/v1/orders` | Cliente B2B | Única entrada de **escritura** de órdenes (Flujo A paso 2) |
| `mock-wms` | Saga APP-02 vía APIM | Confirmación WMS simulada — E3/E4 circuit breaker |
| `mock-erp` | OMS (opcional) | Valorización async |
| `mock-portal` | Cliente B2B | Tracking CQRS desde BigQuery — Flujo C, E8 |

**Zonas internas (configuración, no pods)**

| Zona | Contenido |
|---|---|
| Entrada global | OAuth/JWT, cuotas, CORS |
| Backend real | Enrutamiento a AKS APP-02 |
| Mocks síncronos | Políticas return-xml / circuit breaker |
| Mock lectura | `mock-portal` → BigQuery |
| IaC | OpenAPI en `apis/mock/` + Terraform (doc `04` §5) |

**Mensaje para el comité:** APP-01 es **puerta única** y **simulador de legados** a la vez — sin VPN al CD en la demo.

**Enlace N2:** caja **Azure API Management**; cluster «Legados simulados» representa los **contratos** que mock-wms/erp/portal simulan.

---

#### 4.0.6 Vista N3 — **Proyector CQRS (Cloud Run, GCP)**

**Formato:** texto (sin PNG) · **Vista formal:** [§4.6](#46-vista-f--contenedor-proyector-cqrs-en-cloud-run-gcp) · **Iniciativa:** INI-02 / CQRS · **Flujo:** C · **¿Se implementa?** **Sí** — handler mínimo en Cloud Run (proyector **simplificado** para el MVP).

**Qué es esta vista**  
Zoom **dentro** del consumidor **GCP** que alimenta **BigQuery** para lecturas. Separa **escritura** (Azure SQL vía OMS) de **consulta** (BigQuery vía `mock-portal`).

**Recorrido lógico**

1. **Event Hubs (PLT-03)** entrega eventos (`OrderCreated`, `DeliveryCompleted`, …) al **Event Subscriber** en Cloud Run.  
2. **Schema mapper** (validación ligera): traduce JSON → fila de proyección.  
3. **BigQuery writer**: `INSERT` / merge idempotente por `order_id` en `tracking_projection`.  
4. **Azure API Management (APP-01)** `mock-portal` hace `GET /mock/portal/v1/tracking/{id}` sobre BigQuery — el cliente **no** interroga el OMS.

**Componentes internos (MVP mínimo)**

| Componente | Rol | ¿Complejo en MVP? |
|---|---|:---:|
| Event Subscriber | Lee lotes del bus | No — handler único |
| Projection mapper | Mapping fijo evento→fila | Sí — simplificado a propósito |
| BigQuery writer | Persiste proyección | No — tabla real en sandbox |

**Mensaje para el comité:** demuestra **CQRS** sin motor analítico completo — basta para escenario **E8** (consulta tracking).

**Enlace N2:** caja **Cloud Run** + **BigQuery**; flecha APIM → BigQuery en Flujo C.

---

#### Qué **no** tiene diagrama N3 propio (y por qué)

| Caja N2 | Motivo |
|---|---|
| Azure SQL, Redis, DynamoDB, S3, BigQuery | Persistencia administrada del proveedor — sin código de dominio propio |
| ALB, Key Vault, Pub/Sub | Infraestructura de red o mensajería pura |
| Azure Monitor (PLT-01) | Observabilidad transversal — actor Operaciones en N1/N2 |

#### Orden sugerido para presentar al comité (10 min — Nivel 3)

1. **§4.0.1–§4.0.2** (2 min) — Bus + OMS: «cómo entra la orden y sale el evento».  
2. **§4.0.4 + §4.0.1** (2 min) — Inventario: «reserva por cola, no por HTTPS».  
3. **§4.0.3** (2 min) — Móvil: «offline primero, puente después».  
4. **§4.0.1** (2 min) — DLQ/replay si preguntan resiliencia (Flujo D).  
5. **§4.0.5 + §4.0.6** (2 min) — Mocks y CQRS si preguntan legado o portal.

---

### 4.1 Vista A — Contenedor: **Bus de Eventos Central (PLT-03)** en Azure

> **Guía de lectura paso a paso:** §4.0.1

**Contenedor en foco:** Bus de Eventos Central (PLT-03) (Event Hubs + Service Bus + workers en AKS).

![C4 N3 Bus de Eventos Central (PLT-03) Componentes](diagramas_c4/imagenes/mvp_c4_n3_plt03_componentes.png)

#### Cómo leer este diagrama (Nivel 3 — Bus de Eventos Central)

Zoom **dentro de un solo contenedor**: el **Bus de Eventos Central (PLT-03)**. Las cajas de arriba y abajo son **contenedores externos** (productores y consumidores).

| Flujo | De → A | Tipo | Qué demuestra |
|---|---|---|---|
| 1 | **Orquestador de Pedidos (APP-02)** / **Microservicio Inventario y Reservas (MS-INI01-02)** / Backend móvil → Ingestion API | Eventos async (entrada) | Varios productores publican al mismo bus sin conocer consumidores. |
| 2 | Ingestion → Schema Validator | Validación interna | Rechaza mensajes fuera de contrato AsyncAPI (INI-02). |
| 3 | Router → Ordering Guard → Event Hubs | Eventos async (stream) | Stream canónico con partición por agregado (orden, entrega). |
| 4 | Router → Retry → Service Bus | Eventos async (colas) | Entrega por consumidor con reintento y DLQ. |
| 5 | DLQ → Replay Controller → Router | Comando interno | Recuperación auditada tras fallos (caso Cyber Days). **Operaciones** dispara replay vía **HTTPS monitoreo** (Flujo D). |
| 6 | Service Bus → **Microservicio Inventario y Reservas (MS-INI01-02)** | Eventos async (salida) | Cola dedicada: `OrderValidated` → Reserve Handler (Flujo A pasos 5–6). |
| 7 | Service Bus → mock **TMS (Transportation Management) (APP-11)** | Eventos async (salida) | **TMS (Transportation Management) (APP-11)** recibe despachos y actualiza manifiesto simulado. |
| 8 | Event Hubs → Proyector GCP | Eventos async (salida) | Alimenta BigQuery para CQRS. |

**Mensaje para el comité:** el bus **no reemplaza** las APIs síncronas de la Saga (confirmación WMS); **complementa** desacoplando notificaciones, tracking analítico y última milla.

#### Zonas del cuadro

| Zona | Componentes | Función |
|---|---|---|
| **Entrada** | Event Ingestion API, Schema Validator | Recibir y validar contratos AsyncAPI, correlation ID, idempotency key |
| **Núcleo EDA** | Event Router, Ordering Guard, Partition Manager | Enrutar por dominio/SLA; secuencia por agregado (orden, entrega) |
| **Resiliencia** | Retry Scheduler, DLQ Manager, Replay Controller, Backpressure Controller | Patrones INI-02: reintento, cola fallidos, replay auditado, protección mock de WMS Principal (On Premises) (APP-06) |
| **Persistencia eventos** | Event Hubs (stream), Service Bus (colas), Registro de auditoría (SQL/Storage) | Trazabilidad e historial de intercambio (ADR-016) |
| **Salida** | Subscription Dispatchers | Entrega a Microservicio Inventario y Reservas (MS-INI01-02), mock de TMS (Transportation Management) (APP-11), puente AWS, GCP |

#### Por qué cada componente interno

| Componente | Por qué existe | Si se quitara… |
|---|---|---|
| Schema Validator | INI-02 RF-04: eventos fuera de contrato rompieron tracking en AS IS | Datos corruptos en consumidores |
| Ordering Guard | Eventos móviles llegan fuera de orden (caso **App de Conductores (APP-15)**) | Estados de pedido incoherentes |
| DLQ Manager | 240k mensajes en cola Cyber Days sin remediación | Pérdida silenciosa de eventos |
| Replay Controller | Auditoría y recuperación controlada | Reprocesos manuales peligrosos |
| Backpressure Controller | mock de WMS Principal (On Premises) (APP-06) degradado no debe tumbar OMS centralizado / Orquestador de Pedidos (APP-02) | Efecto dominó en campaña |

---

### 4.2 Vista B — Contenedor: **OMS centralizado / Orquestador de Pedidos (APP-02) + Dominio Orden** en Azure AKS

> **Guía de lectura paso a paso:** §4.0.2

**Contenedor en foco:** OMS centralizado / Orquestador de Pedidos (APP-02) (evolución **Orquestador de Pedidos (APP-02)**).

![C4 N3 OMS centralizado / Orquestador de Pedidos (APP-02) Componentes](diagramas_c4/imagenes/mvp_c4_n3_oms_componentes.png)

#### Cómo leer este diagrama (Nivel 3 — OMS)

Zoom dentro del **Orquestador de Pedidos (APP-02)** en AKS. **Azure API Management (APP-01)** queda **fuera** como entrada; **Microservicio Inventario y Reservas (MS-INI01-02)** y Event Hubs como **vecinos**.

| Flujo | De → A | Tipo | Qué demuestra |
|---|---|---|---|
| 1 | **Azure API Management (APP-01)** → Order API | HTTPS API | `POST /api/v1/orders` entra al dominio orden. |
| 2 | Create Handler → Dedup / Idempotency | Lógica interna | Caso 32.000 duplicados: hash + `Idempotency-Key`. |
| 3 | Aggregate → Repository → SQL | Persistencia | Estado canónico `CREATED` → `VALIDATED` → … |
| 4 | Outbox → Event Publisher → Event Hubs | Eventos async | Publicación confiable: evento solo si commit SQL OK. |
| 5 | Saga → WMS Adapter → mock-wms | HTTPS mock sync | Paso síncrono obligatorio de la Saga (confirmar reserva en WMS simulado). |
| 6 | Saga → Inventory Client → **Microservicio Inventario y Reservas (MS-INI01-02)** | HTTPS interno | **Solo compensación:** `ReleaseInventory` si mock-wms falla (E3). La reserva **happy path** va por Service Bus → MS-INI01-02 (Flujo A). |
| 7 | Query API → Repository | HTTPS lectura ligera | Consultas operativas sin pasar por BigQuery (distinto del mock-portal CQRS). |

**Mensaje para el comité:** aquí viven **idempotencia, dedup y Saga** — el corazón de INI-01.

#### Zonas del cuadro

| Zona | Componentes | Función |
|---|---|---|
| **API** | Order API, Query API (CQRS lectura ligera) | REST desde Azure API Management (APP-01); consultas sin cargar escritura |
| **Dominio (DDD)** | Order Aggregate, Order State Machine, Dedup Engine, Idempotency Guard | Reglas RF-01 a RF-05 INI-01 |
| **Aplicación** | Create Order Handler, Transition Status Handler, Saga Orchestrator | Casos de uso y coordinación Saga |
| **Infraestructura** | Order Repository, Outbox Publisher, Event Publisher | Persistencia + publicación confiable |
| **Integración** | WMS Adapter (mock), Inventory Client | Llamadas sincrónicas solo donde Saga lo exige |
| **Transversal** | Correlation Middleware, Circuit Breaker (Polly) | OBS-01, resiliencia hacia mocks |

#### Por qué cada componente interno

| Componente | Por qué existe |
|---|---|
| Order Aggregate | Raíz DDD; invariantes de orden (SKU, dirección, SLA) |
| Dedup Engine | Caso 32.000 duplicados; hash + ventana temporal |
| Idempotency Guard | Reintentos de clientes API no duplican órdenes |
| Outbox Publisher | Garantiza que SQL y evento no divergen (patrón Outbox) |
| Saga Orchestrator | Reserva inventario y confirmación WMS Principal (On Premises) (APP-06) no son una sola TX |
| Query API | CQRS: consultas frecuentes sin bloquear escritura |

---

### 4.3 Vista C — Contenedor: **Backend Móvil Última Milla** en AWS

> **Guía de lectura paso a paso:** §4.0.3

**Contenedor en foco:** Backend móvil (soporte **App de Conductores (APP-15)**).

> **Decisión MVP:** un solo servicio **ECS Fargate**. Todos los componentes internos (Delivery Handler, Evidence, **Retry Worker**) corren en el **mismo task**. El **Retry Worker** hace **polling de SQS con jitter** y publica al puente EventBridge → Event Hubs — cumple INI-03 (reintento del puente) sin desplegar **Lambda** aparte.

![C4 N3 Mobile Componentes](diagramas_c4/imagenes/mvp_c4_n3_mobile_componentes.png)

#### Cómo leer este diagrama (Nivel 3 — Backend móvil)

Zoom dentro del **backend móvil en AWS** (soporte a **App de Conductores (APP-15)**). **Bus de Eventos Central (PLT-03)** (Event Hubs) aparece como **destino** del puente.

| Flujo | De → A | Tipo | Qué demuestra |
|---|---|---|---|
| 0 | Conductor captura entrega sin red | Solo dispositivo | Firma/foto/GPS en **outbox local cifrado** (INI-03 RF-02); UI confirma al conductor. |
| 1 | **App de Conductores (APP-15)** → ALB → Delivery API | HTTPS móvil | Al recuperar red: envía lote store-and-forward (INI-03 RF-03). |
| 2 | Delivery Handler → Outbox (DynamoDB) | Escritura en AWS | Backend persiste evento; queda PENDING si el **puente a Azure** aún no publicó. |
| 3 | Evidence → S3 + Hash Verifier | HTTPS / SDK | Evidencia con integridad (caso 1.200 firmas perdidas). |
| 4 | Outbox → SQS Relay → EventBridge → Event Hubs | Eventos async | Sincronización al hub Azure cuando hay conectividad multinube. |
| 5 | Delivery API → **App de Conductores (APP-15)** (ACK) | HTTPS móvil | El móvil borra copia local **solo** tras confirmación del backend (INI-03 RF-04). |
| 6 | Retry Worker (mismo task ECS) → SQS | Reintento interno | Polling con jitter ante picos o throttling del puente a Azure. |

**Mensaje para el comité:** **App de Conductores (APP-15)** **no habla directo** con Event Hubs; usa REST al backend AWS, y el backend **traduce** a eventos — por eso en Nivel 1 la flecha del conductor dice **HTTPS móvil**, no “eventos”.

#### Zonas del cuadro

| Zona | Componentes | Función |
|---|---|---|
| **Canal** | Mobile API (ALB + Fargate) | HTTPS desde **App de Conductores (APP-15)** |
| **Offline (dispositivo)** | Local Sync Agent, outbox cifrado en teléfono, Encryption Service | Store-and-forward ADR-006 — RF-02: sin red, todo queda en el móvil |
| **Dominio entrega** | Delivery Handler, Exception Taxonomy Validator, Evidence Orchestrator | INI-03 RF-01, RF-06, RF-07 |
| **Evidencias** | S3 Upload Service, Hash Verifier, Manifest Writer | SHA-256, KMS, **Almacenamiento Evidencias (S3) (APP-16)** |
| **Integración** | SQS Outbox Relay, EventBridge Publisher | Puente asíncrono hacia Azure |
| **Resiliencia** | Retry Worker (mismo task ECS), Ack Tracker | Acks por evento; polling SQS con jitter y reintento del puente a Azure |
| **Observabilidad** | OTel Collector sidecar | Trazas a X-Ray / federación |

#### Por qué cada componente interno

| Componente | Por qué existe |
|---|---|
| Outbox Table (DynamoDB) | Outbox **del backend** en AWS: recibe el lote del móvil y reintenta el puente a Azure si falla |
| Ack Tracker (DynamoDB) | Registra qué eventos ya confirmó el backend al móvil (INI-03 RF-04) |
| Exception Taxonomy Validator | Texto libre impedía **ML / Optimización de Rutas (GCP) (APP-24)** y conciliación (F5) |
| Hash Verifier | Evidencias corruptas generaron disputas financieras |
| SQS Outbox Relay | Desacopla pico móvil del hub Azure |
| Retry Worker (mismo task ECS) | INI-03: polling SQS con jitter y reintento del puente; un solo despliegue Fargate |

---

### 4.4 Vista D — Contenedor: **Microservicio Inventario y Reservas (MS-INI01-02)** en Azure AKS

> **Guía de lectura paso a paso:** §4.0.4

**Contenedor en foco:** **Microservicio Inventario y Reservas (MS-INI01-02)** — workload en **AKS**, dominio Inventario de **INI-01**.

![C4 N3 Microservicio Inventario y Reservas (MS-INI01-02) Componentes](diagramas_c4/imagenes/mvp_c4_n3_inventario_componentes.png)

#### Dónde aparece MS-INI01-02 en los otros niveles

| Nivel | Cómo se ve |
|---|---|
| **N2** | Caja **AKS — Inventario** (MS-INI01-02) → SQL, Event Hubs |
| **N3 OMS (§4.2)** | Caja **externa**: *Inventory Client* del OMS llama a este microservicio (HTTPS interno) |
| **N3 Bus (§4.1)** | **Productor** de eventos (`InventoryReserved`, etc.) hacia **PLT-03** |
| **Flujo A (§3.3)** | Pasos 5–6: Service Bus entrega comando → AKS Inventario reserva → publica evento |

#### Cómo leer este contenedor (Nivel 3 — Inventario)

Zoom **dentro de MS-INI01-02**. **Orquestador de Pedidos (APP-02)** y **Bus de Eventos Central (PLT-03)** quedan **fuera** como vecinos.

| Flujo | De → A | Tipo | Qué demuestra |
|---|---|---|---|
| 1 | **Service Bus** → Reserve Handler | Eventos async | `OrderValidated` desde cola PLT-03 (Flujo A pasos 5–6). |
| 1b | **Orquestador de Pedidos (APP-02)** → Release API | HTTPS interno | `ReleaseInventory` — compensación Saga si mock-wms falla. |
| 2 | Reserve Handler → Availability Service | Lógica dominio | Consulta posiciones por SKU, almacén, lote (F-INV-01). |
| 3 | Reserve Handler → Reservation Repository → **Azure SQL** | Persistencia | Tablas `inventory_position`, `inventory_reservation`; control optimista de versión. |
| 4 | Reserve Handler → Outbox → Event Publisher → **Event Hubs** | Eventos async | `InventoryReserved` o `InventoryInsufficient` — patrón outbox (§1.2). |
| 5 | Evento WMS / movimiento → Movement Handler | Eventos async (entrada) | Registro auditable de movimientos (F-INV-02). |
| 6 | Reconciler → Conflict Repository | Lógica dominio | Conciliación WMS local vs canónico (F-INV-03); backpressure si WMS degradado. |
| 7 | Fallo stock o WMS → **Orquestador de Pedidos (APP-02)** | HTTPS / evento compensación | `ReleaseInventory` si Saga falla en mock-wms (Flujo A, E3). |

**Mensaje para el comité:** inventario **no** es **Control de Inventario (APP-08)** legado ni **WMS Principal (APP-06)** — es el **dominio de reservas** nuevo de INI-01, desplegado como microservicio hermano del OMS en el mismo **AKS**.

#### Zonas del cuadro (componentes internos)

| Zona | Componentes | Función |
|---|---|---|
| **API** | Reserve API, Release API, Availability Query API | Contratos hacia **Orquestador de Pedidos (APP-02)** y consultas de disponibilidad |
| **Dominio (DDD)** | Inventory Aggregate, Reservation Policy, Conflict Rules | Reglas RF-06 a RF-09 INI-01; cantidades, lotes, estados de stock |
| **Aplicación** | Reserve Handler, Release Handler, Movement Handler, Reconciliation Handler | Casos de uso F-INV-01, F-INV-02, F-INV-03 |
| **Infraestructura** | Reservation Repository, Position Repository, Outbox Table, Event Publisher | Persistencia en **Azure SQL** compartida + publicación fiable a **PLT-03** |
| **Integración** | WMS Event Adapter (futuro / mock en MVP), ERP Valuation Client (opcional) | En MVP la confirmación física va por Saga del OMS → mock-wms; inventario reserva stock lógico |
| **Resiliencia** | Idempotency Guard, Optimistic Lock, Backpressure Gate | Picos Cyber Days; WMS on premises degradado |

#### Por qué cada componente interno

| Componente | Por qué existe |
|---|---|
| Availability Service | RF-06: no reservar sin consultar disponibilidad real por SKU/almacén/lote |
| Reservation Repository | Fuente de verdad de reservas (`inventory_reservation`) separada del dominio Orden |
| Outbox Table | Misma transacción SQL + evento `InventoryReserved` sin perder mensajes (§1.2) |
| Reconciliation Handler | RF-09/RF-12: inventario fragmentado entre WMS y ERP en el caso AS IS |
| Backpressure Gate | Protege mock/real **WMS Principal (APP-06)** cuando está caído 6 h (Cyber Days) |

#### Modelo de datos (MVP)

Tablas principales en **Azure SQL** (compartidas con **Orquestador de Pedidos (APP-02)** en el mismo cluster, esquemas separados):

| Tabla | Propósito |
|---|---|
| `inventory_position` | Stock por SKU, almacén, ubicación, lote y estado (`available_qty`, `reserved_qty`, `blocked_qty`, versión optimista) |
| `inventory_reservation` | Reservas ligadas a `order_id`, cantidad, SLA, `correlation_id` |
| `inventory_conflict` | Diferencias WMS local vs canónico; estado y regla de resolución |
| `inventory_event_log` | Movimientos auditables (F-INV-02) |
| `outbox` | Cola local SQL: `InventoryReserved`, `InventoryInsufficient`, compensaciones |

Funcionalidades del microservicio en el MVP:

| Código | Funcionalidad | Entrada | Salida |
|---|---|---|---|
| F-INV-01 | Consultar disponibilidad y reservar | `ReserveInventoryCommand` | `InventoryReserved` o `InventoryInsufficient` |
| F-INV-02 | Registrar movimientos auditables | Evento WMS/OMS | Movimiento persistido + evento canónico |
| F-INV-03 | Conciliar conflictos | Snapshot WMS local/central | `InventoryConflictResolved` o bloqueo operativo |

#### Relación con Orquestador de Pedidos (APP-02) — mismo AKS, dos contenedores

```text
AKS (cluster)
├── Pod(s) Orquestador de Pedidos (APP-02)     ← §4.2
└── Pod(s) Microservicio Inventario (MS-INI01-02)  ← §4.4
         ▲                              ▲
         │ Service Bus (reserva)        │ HTTPS interno (solo ReleaseInventory)
         └──────── PLT-03 §4.1 ─────────┘ Inventory Client desde APP-02 §4.2
```

---

### 4.5 Vista E — Contenedor: **Azure API Management (APP-01)** — gateway y **mocks de legado**

> **Guía de lectura paso a paso:** §4.0.5

**Contenedor en foco:** **Azure API Management (APP-01)** — aplicación del catálogo INI-02; en el MVP concentra **entrada real** y **simulación de legados**.

> **Decisión MVP:** los sistemas **WMS Principal (On Premises) (APP-06)**, **ERP Financiero (On Premises) (APP-25)**, **Portal B2B (Trazabilidad) (APP-18)** y parte del contrato **TMS (Transportation Management) (APP-11)** **no se despliegan**. Se **implementan como mocks** (OpenAPI importado + políticas XML en el mismo **APP-01**) para demostrar contratos y resiliencia **sin VPN ni on premises** en la demo académica.

#### Cómo leer este contenedor (Nivel 3 — APP-01)

Zoom **dentro de APP-01**. **Orquestador de Pedidos (APP-02)** en AKS y **BigQuery** quedan **fuera** como backends enrutados.

| Flujo | De → A | Tipo | Qué demuestra |
|---|---|---|---|
| 1 | Cliente B2B → Global policies → `POST /api/v1/orders` | HTTPS API | OAuth/JWT, rate limit, `Idempotency-Key` hacia **APP-02**. |
| 2 | **Orquestador de Pedidos (APP-02)** → `mock-wms` | HTTPS mock sync | Saga confirma reserva; política devuelve 200 / 503 / timeout (E4). |
| 3 | **Orquestador de Pedidos (APP-02)** → `mock-erp` | HTTPS mock sync | Valorización async (202 Accepted) — demo opcional. |
| 4 | Cliente → `mock-portal` → **BigQuery** | HTTPS GET lectura | **CQRS:** portal mock lee proyección; **no** escribe en SQL (Flujo C, E8). |
| 5 | **Service Bus** → consumidor `mock-tms` | Eventos async | Manifiesto simulado — **no** es ruta HTTP de APP-01; se documenta en §4.1. |

#### Zonas del cuadro (componentes internos — configuración APIM)

| Zona | Componentes | Función en el MVP |
|---|---|---|
| **Entrada global** | JWT validate, Rate limit, CORS, Correlation-ID | Gobierno API-first INI-02 en un solo punto |
| **Backend real** | Route `POST /api/v1/orders` → AKS **APP-02** | Única escritura transaccional de órdenes |
| **Mocks síncronos** | `mock-wms`, `mock-erp` (políticas return/mock + circuit breaker) | Sustituyen legados on premises en la Saga |
| **Mock lectura** | `mock-portal` + policy/set-header hacia consulta BigQuery | Sustituye **Portal B2B (APP-18)** solo para tracking |
| **Operación** | OpenAPI en repo `apis/mock/` + Terraform `azurerm_api_management_api` | IaC versionado — ver `04_IaC_Costos_Despliegue.md` §5 |

**Mensaje para el comité:** **APP-01 sí tiene zoom N3**, pero el contenido interno son **políticas y rutas mock**, no un dominio DDD con pods. Por eso va en **texto** (§4.5) y no en un PNG de microservicio.

---

### 4.6 Vista F — Contenedor: **Proyector CQRS** en **Cloud Run** (GCP)

> **Guía de lectura paso a paso:** §4.0.6

**Contenedor en foco:** servicio en **Cloud Run** que consume eventos del **Bus de Eventos Central (PLT-03)** y escribe la **proyección de lectura** en **BigQuery**.

> **Decisión MVP:** en producción el proyector tendría varios handlers, deduplicación analítica y tablas de agregados. En el MVP se implementa como **proyector mínimo mock**: **un handler** que traduce `OrderCreated`, `DeliveryCompleted`, etc. → filas en tablas `tracking_projection` / `sla_projection` en **BigQuery**. Basta para que `mock-portal` en **APP-01** responda `GET /mock/portal/v1/tracking/{id}` sin consultar **Azure SQL**.

#### Cómo leer este contenedor (Nivel 3 — Cloud Run)

| Flujo | De → A | Tipo | Qué demuestra |
|---|---|---|---|
| 1 | **Event Hubs** (vía puente o suscripción) → Event Subscriber | Eventos async | Mismo bus que alimenta TMS mock y backend móvil. |
| 2 | Subscriber → Schema mapper | Validación ligera | Rechaza payload fuera de contrato (sin replicar PLT-03 completo). |
| 3 | Mapper → BigQuery Insert | Escritura analítica | **CQRS:** separa lectura de la escritura transaccional en Azure. |
| 4 | **Azure API Management (APP-01)** `mock-portal` → **BigQuery** | HTTPS GET lectura | Cliente consulta tracking desde proyección (Flujo C). |

#### Componentes internos (MVP simplificado)

| Componente | Rol | ¿Mock? |
|---|---|:---:|
| HTTP/Event trigger | Arranque Cloud Run (min instances = 0) | No — servicio real en GCP |
| Event Subscriber | Lee lote de eventos | Sí — lógica mínima, sin cola propia |
| Projection mapper | JSON evento → fila BQ | Sí — mapping fijo en código, sin motor de reglas |
| BigQuery writer | `INSERT` / merge idempotente por `order_id` | No — tabla real en sandbox BQ |

**Mensaje para el comité:** **Cloud Run sí merece zoom conceptual**, pero en el MVP es **deliberadamente simple** para no duplicar la complejidad del bus (§4.1) ni del OMS (§4.2).

---

## 5. Tabla resumen — servicio por servicio (las tres nubes)

| Servicio cloud | Nivel C4 | Contenedor | Justificación de negocio |
|---|---|---|---|
| Azure API Management (APP-01) | 2–3 | API Gateway + mocks | Entrada única; legados **simulados** en APIM (§4.5) |
| AKS | 2–3 | **Orquestador de Pedidos (APP-02)**, **Microservicio Inventario y Reservas (MS-INI01-02)**, workers **Bus de Eventos Central (PLT-03)** | Cluster AKS: aplicación **Orquestador de Pedidos (APP-02)** + microservicio **Microservicio Inventario y Reservas (MS-INI01-02)** (este último sin ID APP-XX) |
| Azure SQL | 2–3 | Repositorio transaccional | Saga, outbox, estados fuertes |
| Event Hubs | 2–3 | Bus de Eventos Central (PLT-03) | Hub eventos campaña 180k |
| Service Bus | 2–3 | Bus de Eventos Central (PLT-03) | DLQ y colas por consumidor |
| Redis | 2–3 | OMS centralizado / Orquestador de Pedidos (APP-02) | Dedup/SLA en memoria |
| ECS Fargate | 2–3 | Backend móvil | Siempre activo para conductores |
| DynamoDB | 2–3 | Backend móvil | Outbox backend y acks tras sincronización desde el móvil |
| S3 + KMS | 2–3 | Evidencias | Costo/escala evidencias |
| SQS/EventBridge | 2–3 | Puente AWS | Integración asíncrona multinube |
| Cloud Run | 2–3 | Consumidor GCP (proyector mock) | CQRS lectura; handler mínimo eventos → BigQuery (§4.6) |
| BigQuery | 2 | CQRS lectura | Portal tracking sin golpear OMS centralizado / Orquestador de Pedidos (APP-02) |
| Pub/Sub | 2 | Mensajería GCP | Patrón nativo GCP |
| Terraform | Transversal | Plataforma IaC (PLT-04) | 100% IaC exigido |

---

## 6. Cómo presentar C4 al comité (guion 5 minutos)

1. **Nivel 1 (1 min):** “Estos son los actores y los mocks; el MVP es la caja central.”
2. **Nivel 2 (2 min):** Mostrar el diagrama con **nombres de servicio cloud**; explicar con **Flujo A** (orden), **Flujo B** (offline) o **Flujo C** (tracking E8 — flecha APIM → BigQuery) de §3.3 — “Azure gobierna, AWS entrega, GCP consulta”.
3. **Nivel 3 (3 min):** Leer **§4.0** (guía de las seis vistas); luego mostrar PNG según pregunta; si preguntan por **mocks o CQRS**:
   - ¿Integración? → Bus de Eventos Central (PLT-03) (DLQ, replay) — §4.1; Flujo D escenario E5.
   - ¿Órdenes duplicadas? → Orquestador de Pedidos (APP-02) (dedup, idempotencia, Saga) — §4.2.
   - ¿Reservas e inventario? → Microservicio Inventario y Reservas (MS-INI01-02) — §4.4.
   - ¿Firmas perdidas? → Backend móvil (outbox, S3, hash) — §4.3.
   - ¿Mocks WMS/portal sin on premises? → **Azure API Management (APP-01)** — §4.5.
   - ¿Tracking sin golpear SQL? → Proyector **Cloud Run** mock + `mock-portal` — §4.6.

---

## 7. Diagramas Mermaid (editable en repo)

### Nivel 1 — Contexto

```mermaid
C4Context
    title Nivel 1 - Contexto MVP RutaExpress
    Person(cliente, "Cliente B2B", "Actor / Persona")
    Person(conductor, "App de Conductores (APP-15)", "Dispositivo movil")
    Person(ops, "Operaciones / Soporte", "Actor / Persona")
    System(mvp, "Plataforma Logistica MVP", "Azure hub + AWS + GCP")
    System_Ext(wms, "mock WMS Principal (On Premises)", "APP-06 / APP-07")
    System_Ext(erp, "mock ERP Financiero (On Premises)", "APP-25")
    System_Ext(portal, "mock Portal B2B (Trazabilidad)", "APP-18 / APP-20")
    System_Ext(tms, "mock TMS (Transportation Management)", "APP-11")
    Rel(cliente, mvp, "HTTPS API: POST orden, GET tracking")
    Rel(conductor, mvp, "HTTPS movil: entrega / evidencias")
    Rel(ops, mvp, "HTTPS monitoreo: DLQ / metricas")
    Rel(mvp, wms, "HTTPS mock sync: confirmar reserva")
    Rel(mvp, erp, "HTTPS mock sync: valorizacion")
    Rel(mvp, portal, "HTTPS GET lectura: mock-portal CQRS")
    Rel(mvp, tms, "Eventos async: despacho / manifiesto")
```

### Nivel 2 — Contenedores (servicio cloud + nombre + ID)

```mermaid
flowchart LR
    CLI["Cliente B2B<br/>Actor<br/>Persona"]
    OPS["Operaciones / Soporte<br/>Actor<br/>Persona"]
    subgraph Azure["Azure"]
        APIM["Azure API Management<br/>Azure API Management<br/>APP-01"]
        OMS["AKS<br/>Orquestador de Pedidos<br/>APP-02"]
        INV["AKS<br/>Microservicio Inventario y Reservas<br/>MS-INI01-02"]
        SQL[("Azure SQL<br/>Repositorio transaccional<br/>APP-02 + MS-INI01-02")]
        EH["Event Hubs<br/>Bus de Eventos Central<br/>PLT-03"]
        SB["Service Bus<br/>Bus de Eventos Central<br/>PLT-03"]
        REDIS["Azure Cache for Redis<br/>Cache operativa OMS<br/>APP-02"]
        MON["Azure Monitor<br/>Plataforma Observabilidad<br/>PLT-01"]
    end
    subgraph AWS["AWS"]
        ALB["Application Load Balancer<br/>Entrada backend movil<br/>soporta APP-15"]
        ECS["ECS Fargate<br/>Backend movil ultima milla<br/>soporta APP-15"]
        DDB[("DynamoDB<br/>Outbox backend + Ack Tracker<br/>backend APP-15")]
        S3[("Amazon S3<br/>Almacenamiento Evidencias<br/>APP-16")]
        SQS["Amazon SQS<br/>Buffer puente movil<br/>hacia PLT-03"]
        EB["EventBridge<br/>Publicador puente AWS<br/>hacia PLT-03"]
    end
    subgraph GCP["GCP"]
        CR["Cloud Run<br/>Proyector CQRS<br/>lectura tracking"]
        BQ[("BigQuery<br/>Almacen consultas CQRS<br/>mock-portal APP-18")]
        PS["Pub/Sub<br/>Mensajeria analitica<br/>GCP"]
    end
    subgraph EXT["Legados simulados (SaaS externo)"]
        MWMS["mock-wms en APIM<br/>WMS Principal (On Premises)<br/>APP-06"]
        MERP["mock-erp en APIM<br/>ERP Financiero (On Premises)<br/>APP-25"]
        MPORT["mock-portal en APIM<br/>Portal B2B (Trazabilidad)<br/>APP-18"]
        MTMS["mock-tms consumidor<br/>TMS (Transportation Mgmt)<br/>APP-11"]
    end
    CLI -->|HTTPS API: POST orden / GET tracking E8| APIM --> OMS --> SQL
    APIM -->|mock-portal CQRS| BQ
    APIM -->|simula contrato| MPORT
    OMS -->|HTTPS mock sync| APIM
    APIM -->|mock-wms| MWMS
    APIM -->|mock-erp| MERP
    OMS --> REDIS
    OMS --> EH --> SB
    SB -->|eventos async: cola MS-INI01-02| INV
    SB -->|eventos async| MTMS
    INV --> SQL
    INV --> EH
    ALB --> ECS --> DDB
    ECS --> S3
    ECS --> SQS --> EB --> EH
    EH --> CR --> BQ
    PS --> CR
    OPS -->|HTTPS monitoreo: DLQ / metricas| MON
    OMS --> MON
```

> **Nota:** Las figuras PNG exportables usan la misma convención de tres líneas por caja. Regenerar: `python diagramas_c4/generar_diagramas_mvp_c4.py`. **DLQ y Replay Controller** — zoom interno en §4.1 N3 (Flujo D); no son cajas separadas en N2.

---

*Continúa en [`04_IaC_Costos_Despliegue.md`](04_IaC_Costos_Despliegue.md) para Terraform y FinOps.*
