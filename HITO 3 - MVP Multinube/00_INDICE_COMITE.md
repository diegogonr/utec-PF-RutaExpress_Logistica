# Hito 3 — MVP Multinube RutaExpress
## Índice para el Comité de Arquitectura

> **Carpeta única de lectura.** Este Hito 3 consolida Hito 1 (arquitectura empresarial) y Hito 2 (diseño TO BE — hub central Azure) y define **qué se implementará** en el prototipo/MVP. **Aún no hay código desplegado**; este paquete es la documentación de diseño de implementación aprobable por comité.

> **Regla de oro — nomenclatura:** en todo el paquete Hito 3 cada identificador va **siempre** con su **nombre oficial** (catálogo APP/PLT → `HITO 1 - .../06_Mapa_Portafolio_Aplicaciones.md`).

## Tipos de identificadores (leer antes del dossier)

En este proyecto conviven **cuatro familias de ID** de negocio/arquitectura, más una quinta capa de **servicios en la nube** del proveedor. No son intercambiables. Se evitan abreviaturas informales («apps», «ML» suelto); se usan nombres oficiales completos. **Términos técnicos:** siglas y palabras en inglés van con significado breve entre paréntesis la primera vez en cada documento (p. ej. **ACK** — acuse de recibo).

| Prefijo | Qué es | Ejemplo en el MVP | ¿Es una aplicación del portafolio? |
|---|---|---|---|
| **INI-XX** | **Iniciativa** de transformación del roadmap Hito 1 (bloque de capacidades de negocio, 36 meses). Agrupa cambios sobre varias aplicaciones, plataformas y microservicios. | **INI-01** órdenes e inventario; **INI-02** integración API/eventos; **INI-03** última milla | **No** — una iniciativa **no** es una aplicación |
| **APP-XX** | **Aplicación** del catálogo empresarial (26 aplicaciones: APP-01 … APP-26). Unidad reconocida por negocio y gobierno de TI. | **Orquestador de Pedidos (APP-02)**, **App de Conductores (APP-15)** | **Sí** |
| **PLT-XX** | **Plataforma** transversal habilitadora (observabilidad, identidad, bus de eventos, infraestructura como código). | **Bus de Eventos Central (PLT-03)** | Es plataforma, no aplicación de negocio |
| **MS-INIxx-yy** | **Microservicio** de una iniciativa. El prefijo **MS** abrevia solo el tipo *microservicio* en el ID; el nombre completo es obligatorio en el texto. **INI01** = iniciativa origen; **02** = segundo componente principal de esa iniciativa (el primero es el dominio Orden en **Orquestador de Pedidos (APP-02)**). | **Microservicio Inventario y Reservas (MS-INI01-02)** | **No** — tiene ID **MS-INI01-02**, no **APP-XX** |

### Diferencias entre aplicación, microservicio, plataforma y servicio en la nube

| Concepto | Qué representa | ¿Se despliega? | Relación con los demás |
|---|---|---|---|
| **Aplicación (APP-XX)** | Capacidad de negocio del portafolio Hito 1 (qué hace RutaExpress para el usuario o la operación). | Sí — como uno o más **contenedores** (workloads) en AKS, ECS, SaaS, etc. | Una aplicación **puede** implementarse con uno o varios microservicios, pero conserva **un solo ID APP**. Ej.: **Orquestador de Pedidos (APP-02)** corre en AKS. |
| **Microservicio (MS-INIxx-yy)** | Unidad técnica **acotada por dominio** (un bounded context), desplegable de forma independiente. Nace de una **iniciativa** cuando no existe APP en el catálogo. | Sí — típicamente un contenedor en **AKS** o **ECS Fargate**. | **No** agrupa varias aplicaciones APP dentro. **No** es un catálogo de APP-XX. Usa **servicios en la nube** (Azure SQL, Event Hubs, DynamoDB) como dependencias. |
| **Plataforma (PLT-XX)** | Capacidad compartida por muchas aplicaciones (bus, identidad, observabilidad). | Sí — como servicios administrados multinube. | Las aplicaciones y microservicios **publican/consumen** la plataforma; no la contienen. |
| **Servicio en la nube** | Recurso del proveedor (Azure, AWS, GCP): **AKS**, **Azure SQL**, **Event Hubs**, **Amazon S3**, **BigQuery**. | Lo provisiona Terraform (Plataforma IaC (PLT-04)). | Es **infraestructura** donde corren aplicaciones y microservicios; **no** es una aplicación del portafolio ni un microservicio de negocio. |

**¿De qué se compone un microservicio?** Un microservicio —por ejemplo **Microservicio Inventario y Reservas (MS-INI01-02)**— es **una** unidad desplegable (imagen de contenedor en **AKS**), con **componentes internos** de software (API, repositorio, publicador de eventos — nivel 3 C4). Se apoya en **servicios en la nube** (Azure SQL, **Bus de Eventos Central (PLT-03)** vía Event Hubs). **No** está formado por varias aplicaciones APP-XX; convive con **Orquestador de Pedidos (APP-02)** como otro workload en el mismo cluster, pero cada uno con responsabilidad de dominio distinta.

Dentro de **INI-01** el MVP despliega dos piezas de dominio: **Orquestador de Pedidos (APP-02)** (aplicación del catálogo que evoluciona a OMS centralizado) y **Microservicio Inventario y Reservas (MS-INI01-02)** (microservicio nuevo en AKS). No confundir **MS-INI01-02** con **Control de Inventario (APP-08)** (legado en deprecación) ni con **WMS Principal (On Premises) (APP-06)** (sistema de almacén on premises).

---

## Lectura recomendada (35–45 minutos)

| Orden | Documento | Para qué sirve | Tiempo |
|:---:|---|---|:---:|
| 1 | **Este índice** | Orientación y mensajes clave | 3 min |
| 2 | [`01_Resumen_Empresa_RutaExpress.md`](01_Resumen_Empresa_RutaExpress.md) | **Contexto de negocio** — quién es RutaExpress, dolores, cadena de valor | 5 min |
| 3 | [`02_Dossier_MVP_Alternativa_A.md`](02_Dossier_MVP_Alternativa_A.md) | Alcance MVP, patrones, mocks, decisiones | 15 min |
| 4 | [`03_C4_Model_MVP.md`](03_C4_Model_MVP.md) | **Documento central C4** — taxonomía (§0.1), glosarios (§1.1–§1.3), niveles 1–3; **guía detallada N3 en §4.0** | 15 min |
| 5 | [`04_IaC_Costos_Despliegue.md`](04_IaC_Costos_Despliegue.md) | Terraform multinube, pipeline, costos mensuales por nube | 8 min |

**Diagramas exportables:** carpeta [`diagramas_c4/imagenes/`](diagramas_c4/imagenes/) — generar con `python diagramas_c4/generar_diagramas_mvp_c4.py`. Nivel 3 (cuatro workloads): `mvp_c4_n3_plt03_componentes.png`, `mvp_c4_n3_oms_componentes.png`, `mvp_c4_n3_inventario_componentes.png`, `mvp_c4_n3_mobile_componentes.png` — detalle en [`03_C4_Model_MVP.md`](03_C4_Model_MVP.md) §4.1–§4.4.

---

## Mensaje ejecutivo (elevator pitch)

RutaExpress opera logística multinube fragmentada: **26 aplicaciones**, integraciones punto a punto, WMS Principal (On Premises) (APP-06) / WMS Satélite (On Premises local) (APP-07) frágil y última milla offline con pérdida de evidencias. Los Hitos 1 y 2 definieron el **TO BE** con **hub central en Azure** (Azure API Management (APP-01), OMS centralizado / Orquestador de Pedidos (APP-02), Bus de Eventos Central (PLT-03)), **AWS para última milla** y **GCP para analítica/rutas**.

El **MVP del Hito 3** demostrará el flujo crítico **orden → reserva → evento → entrega offline → evidencia**, en **tres nubes**, con **IaC completo (Terraform)**, **APIs mock** para **WMS Principal (On Premises) (APP-06)**, **ERP Financiero (On Premises) (APP-25)** y portales, y **seis patrones** de arquitectura: Microservicios, DDD, EDA, CQRS, Saga y Resiliencia.

---

## Cumplimiento del enunciado (Hito 3)

| Requisito académico | Cómo se cumple en este MVP |
|---|---|
| Basado en diseño TO BE del Hito 2 | Hub central Azure — ver `02_Alternativa_A.md` |
| Mínimo 2 nubes | **3 nubes:** Azure + AWS + GCP |
| Mínimo 3 patrones | **6 patrones:** Microservicios, DDD, EDA, CQRS, Saga, Resiliencia |
| Despliegue 100% IaC | Terraform modular por nube — ver doc `04` |
| Costos estimados por nube/mes | Tabla FinOps en doc `04` |
| API mock para integraciones | Azure API Management (APP-01) + mocks — ver doc `02` §4.3 y §2.1 |

---

## Decisiones que el comité valida con este paquete

1. **Hub central Azure** como base arquitectónica del MVP.
2. **Orquestador de Pedidos (APP-02) evoluciona a OMS centralizado** (mismo ID APP-02).
3. **Bus de Eventos Central (PLT-03)** = Azure Event Hubs + Azure Service Bus.
4. **Microservicio Inventario y Reservas (MS-INI01-02)** — microservicio de la iniciativa **INI-01** (prefijo **MS** = microservicio; ID **MS-INI01-02**, no **APP-XX**). Gestiona reservas y disponibilidad en AKS. **No** es **Control de Inventario (APP-08)** ni una aplicación nueva del catálogo.
5. **Alcance MVP acotado** a las iniciativas **INI-01**, **INI-02** e **INI-03** (programas de transformación, no aplicaciones). **INI-04** (optimización de rutas y **ML / Optimización de Rutas (GCP) (APP-24)**), **INI-05** (observabilidad plena) e **INI-06** (liquidación) quedan fuera o parciales en la primera versión del prototipo.
6. **Sistemas on premises y SaaS** se simulan con mocks en v1 del MVP.

---

## Trazabilidad a entregables previos

| Origen | Ubicación en el repositorio |
|---|---|
| Hito 1 — Arquitectura empresarial | `HITO 1 - Arquitectura Empresarial/` (docs 01–11) |
| Hito 2 — Requerimientos INI-01/02/03 | `HITO 2 - Requerimientos Y Diseño de Arquitectura de Solución/INI-*` |
| Hito 2 — Arquitectura TO BE y ADR | `HITO 2 - .../ARQUITECTURA_SOLUCION_TO_BE/` |
| Caso de negocio | `Caso 6a` y `Caso 6b` en raíz del repo |

---

*RutaExpress Fulfillment & Transporte — Proyecto Integrador Final UTEC — Arquitectura de Soluciones Multinube*
