# ADM - Fase F: Migration Planning
## RutaExpress Fulfillment & Transporte

> **Para el comité de arquitectura** — **Plan de migración 36 meses** para las **6 iniciativas** aprobadas en ADM E. **Mensaje clave:** iniciar en mes 1 con Observabilidad/Seguridad/Gobierno (INI-05) e Integración API-First/Event-Driven (INI-02); ejecutar Modernización de última milla (INI-03) como quick win; y desplegar el OMS centralizado / Orquestador de Pedidos (APP-02) + inventario (INI-01), rutas dinámicas (INI-04) y liquidación automatizada (INI-06) sobre la plataforma de eventos y trazabilidad.

---

## 1. Propósito

Definir el plan de migración desde el estado AS IS hacia el TO BE, con estimaciones de tiempo, costo, prioridades, dependencias, hitos y riesgos. El plan mantiene consistencia con el catálogo de aplicaciones del Hito 1: no se crean nuevos IDs de aplicación y el OMS centralizado / Orquestador de Pedidos (APP-02) se implementa como evolución funcional de Orquestador de Pedidos (APP-02).

---

## 2. Iniciativas Priorizadas

### Criterios de priorización

| Criterio | Peso |
|---|---|
| Impacto en penalidades, ingresos retenidos o costo operativo | 30% |
| Reducción de riesgo operativo y de integridad de datos | 25% |
| Habilitación de otras iniciativas | 20% |
| Velocidad de entrega de valor | 15% |
| Complejidad y riesgo de implementación | 10% |

### Ranking recomendado

| Prioridad | Iniciativa | Tipo | Motivo |
|---|---|---|---|
| 1 | INI-05 Observabilidad, seguridad y gobierno multinube | Fundacional | Da trazabilidad, IAM, secretos, IaC y gobierno para todo el programa |
| 2 | INI-02 Integración API-First y Event-Driven | Fundacional | Habilita contratos, eventos, colas, reintentos y desacoplamiento |
| 3 | INI-03 Modernización de última milla y gestión de excepciones | Quick win operativo | Reduce pérdida de evidencias y normaliza excepciones temprano |
| 4 | INI-01 Gestión unificada de órdenes e inventario end-to-end | Transformación core | Centraliza órdenes, inventario, reservas, idempotencia y reconciliación |
| 5 | INI-04 Optimización dinámica de rutas y despacho | Optimización operativa | Usa eventos, excepciones y datos limpios para reducir costo por entrega |
| 6 | INI-06 Conciliación financiera y liquidación automatizada | Alto impacto financiero | Monetiza la trazabilidad end-to-end y reduce dependencia de Excel |

---

## 3. Fichas de iniciativas con estimación

### INI-01: Gestión unificada de órdenes e inventario end-to-end

**Prioridad:** 4 (Transformación core)
**Duración:** 12 meses
**Equipo:** 1 arquitecto senior + 1 product owner logístico + 5 ingenieros backend + 1 DBA + 1 DevOps + 1 analista funcional WMS Principal (On Premises) (APP-06)/ERP
**Alcance:**

- Evolucionar Orquestador de Pedidos (APP-02) hacia capacidad OMS centralizado / Orquestador de Pedidos (APP-02) centralizada.
- Integrar validación, deduplicación, idempotencia y estado canónico de orden.
- Implementar vista unificada de inventario por SKU, almacén, ubicación, lote y estado.
- Migrar progresivamente WMS Principal (On Premises) (APP-06) y WMS Satélite (On Premises local) (APP-07) hacia WMS Cloud.
- Absorber la función de Control de Inventario (APP-08) dentro de WMS Cloud.
- Integrar reservas, liberaciones y movimientos con TMS (Transportation Management) (APP-11) y ERP Financiero (On Premises) (APP-25).
- Reconciliar conflictos de inventario al reconectar almacenes locales.

| Componente de costo | Estimación | Total |
|---|---|---|
| Azure AKS + Azure SQL / SQL Managed Instance | USD 4,000/mes | USD 48,000 |
| Equipo desarrollo y arquitectura | USD 42,000/mes | USD 504,000 |
| Migración de datos, pruebas de inventario y reconciliación | One-time | USD 45,000 |
| Capacitación de operación y almacenes | One-time | USD 20,000 |
| Contingencia técnica | One-time | USD 33,000 |
| **TOTAL INI-01** | | **USD 650,000** |

**Beneficios que aporta:**

- Órdenes válidas antes de reservar inventario.
- Inventario único y reconciliado entre almacenes.
- Reducción de duplicados, ajustes manuales y conflictos de stock.
- Base operacional para rutas, última milla y liquidación automática.

**ROI esperado:** evita incidentes de pedidos duplicados, reduce ajustes de inventario y disminuye el riesgo de penalidades por indisponibilidad de WMS Principal (On Premises) (APP-06) en campañas.

---

### INI-02: Integración API-First y Event-Driven

**Prioridad:** 2 (Fundacional)
**Duración:** 8 meses
**Equipo:** 2 arquitectos + 4 ingenieros backend/integración + 1 DevOps
**Alcance:**

- Implementar Bus de Eventos Central (PLT-03) con **Azure Event Hubs + Azure Service Bus** como hub principal en Azure y conectores hacia AWS y GCP.
- Fortalecer Azure API Management (APP-01) como capa de gobierno API-first.
- Definir contratos de APIs, eventos y modelos de datos.
- Migrar progresivamente integraciones punto a punto entre OMS centralizado / Orquestador de Pedidos (APP-02), WMS Principal (On Premises) (APP-06), TMS (Transportation Management) (APP-11), App de Conductores (APP-15), ERP Financiero (On Premises) (APP-25), Portal B2B (Trazabilidad) (APP-18) y Plataforma de Analítica (GCP batch) (APP-22).
- Incorporar colas, reintentos, priorización, backpressure y dead-letter queues.
- Habilitar event replay y auditoría.

| Componente de costo | Estimación | Total |
|---|---|---|
| Azure Event Hubs / Service Bus / conectores cloud | USD 1,200/mes | USD 9,600 |
| Capacidad AKS/API adicional | USD 1,200/mes | USD 9,600 |
| Equipo desarrollo e integración | USD 30,000/mes | USD 240,000 |
| Diseño de contratos, pruebas y gobierno | One-time | USD 5,400 |
| **TOTAL INI-02** | | **USD 264,600** |

**Beneficios que aporta:**

- Desacopla sistemas críticos.
- Evita pérdida de mensajes y reprocesos manuales.
- Permite estados canónicos y trazabilidad entre sistemas.
- Habilita INI-01, INI-03, INI-04 e INI-06.

**ROI esperado:** reducción de incidentes de integración y menor costo de cambio en flujos core.

---

### INI-03: Modernización de última milla y gestión de excepciones

**Prioridad:** 3 (Quick win operativo)
**Duración:** 5 meses
**Equipo:** 1 arquitecto + 3 ingenieros mobile/backend + 1 QA + 1 analista de operación última milla
**Alcance:**

- Rediseñar App de Conductores (APP-15) con almacenamiento local cifrado y operación offline-first.
- Implementar sincronización store-and-forward, confirmación backend y reintentos automáticos.
- Garantizar persistencia de firma, foto, GPS, timestamp y motivo de excepción.
- Añadir hash de integridad para evidencias en Almacenamiento Evidencias (S3) (APP-16).
- Definir taxonomía única de excepciones para App de Conductores (APP-15), TMS (Transportation Management) (APP-11), CRM de Atención al Cliente (APP-20) y Portal B2B (Trazabilidad) (APP-18).
- Automatizar reintentos, devoluciones, reasignaciones y escalamiento.

| Componente de costo | Estimación | Total |
|---|---|---|
| Backend AWS / sincronización | USD 1,000/mes | USD 5,000 |
| Mensajería/eventos última milla | USD 500/mes | USD 2,500 |
| Equipo desarrollo y QA | USD 22,000/mes | USD 110,000 |
| MDM, pruebas de campo y seguridad local | One-time | USD 17,500 |
| **TOTAL INI-03** | | **USD 135,000** |

**Beneficios que aporta:**

- Reduce pérdida de evidencias.
- Mejora soporte a reclamos y liquidación.
- Normaliza datos para ML / Optimización de Rutas (GCP) (APP-24).
- Reduce reintentos manuales y disputas de custodia.

**ROI esperado:** evita retenciones por evidencias faltantes y reduce costos de reintento en última milla.

---

### INI-04: Optimización dinámica de rutas y despacho

**Prioridad:** 5 (Optimización operativa)
**Duración:** 7 meses
**Equipo:** 1 arquitecto + 2 ingenieros ML + 2 ingenieros backend + 1 DevOps
**Alcance:**

- Evolucionar Optimizador de Rutas (GCP batch) (APP-12) hacia optimización dinámica en GCP.
- Integrar tráfico, capacidad vehicular, ventanas horarias, cadena de frío, seguridad y SLA.
- Integrar el optimizador con TMS (Transportation Management) (APP-11) mediante APIs y eventos.
- Automatizar asignación de vehículos, conductores y paquetes.
- Registrar cambios manuales de rutas con usuario, motivo, timestamp e impacto.
- Alimentar ML / Optimización de Rutas (GCP) (APP-24) con excepciones normalizadas.

| Componente de costo | Estimación | Total |
|---|---|---|
| GCP GKE / procesamiento dinámico | USD 1,500/mes | USD 10,500 |
| Datos de tráfico, mapas y Pub/Sub | USD 2,000/mes | USD 14,000 |
| Equipo desarrollo y ML | USD 30,000/mes | USD 210,000 |
| Datos históricos, entrenamiento y pruebas piloto | One-time | USD 20,500 |
| **TOTAL INI-04** | | **USD 255,000** |

**Beneficios que aporta:**

- Reduce rutas inviables y correcciones manuales.
- Mejora cumplimiento de ventanas de entrega.
- Optimiza uso de flota, conductores y capacidad.
- Reduce costo por entrega.

**ROI esperado:** meta de hasta 15% de reducción en costo por entrega, equivalente a USD 2M+ anuales sobre el volumen actual.

---

### INI-05: Observabilidad, seguridad y gobierno multinube

**Prioridad:** 1 (Fundacional transversal)
**Duración:** 6 meses
**Equipo:** 1 arquitecto de seguridad + 2 DevSecOps + 1 SRE + 1 analista FinOps
**Alcance:**

- Implementar Plataforma de Observabilidad Unificada (PLT-01) con métricas, logs y trazas de Azure, AWS, GCP, SaaS y on premises.
- Definir correlation ID end-to-end para pedidos, inventario, rutas, entregas, evidencias, colas y liquidación.
- Crear tableros y alertas para colas, pedidos, inventario, rutas, entregas y SLA.
- Completar Plataforma de Identidad y Accesos (IAM) (PLT-02) con identidad federada, mínimo privilegio, MFA, secretos centralizados y políticas en Azure API Management (APP-01).
- Implementar Plataforma IaC (PLT-04) con Terraform y pipelines.
- Aplicar cifrado, auditoría y gobierno FinOps.

| Componente de costo | Estimación | Total |
|---|---|---|
| Observabilidad nativa cloud y exportaciones | USD 1,000/mes | USD 6,000 |
| IAM, Key Vault/secretos, WAF y hardening | USD 1,700/mes | USD 10,200 |
| Equipo DevSecOps/SRE/FinOps | USD 20,000/mes | USD 120,000 |
| Repos IaC, pipelines y tableros FinOps | One-time | USD 8,800 |
| **TOTAL INI-05** | | **USD 145,000** |

**Beneficios que aporta:**

- Visibilidad end-to-end.
- Menor tiempo de detección y recuperación.
- Seguridad homogénea en multinube.
- Infraestructura reproducible y auditable.
- Control de costos cloud en campañas.

**ROI esperado:** reducción de riesgo operativo, menor tiempo de indisponibilidad y base de gobierno para todas las iniciativas.

---

### INI-06: Conciliación financiera y liquidación automatizada

**Prioridad:** 6 (Alto impacto financiero)
**Duración:** 7 meses
**Equipo:** 1 arquitecto + 3 ingenieros backend + 1 analista de negocio financiero + 1 QA + soporte ERP Financiero (On Premises) (APP-25)
**Alcance:**

- Implementar motor de liquidación en Azure AKS + Azure SQL.
- Integrar OMS centralizado / Orquestador de Pedidos (APP-02), WMS Cloud, TMS (Transportation Management) (APP-11), tracking, evidencias, Portal B2B (Trazabilidad) (APP-18) y ERP Financiero (On Premises) (APP-25).
- Conciliar órdenes, estados, evidencias, SLA, tarifas y penalidades.
- Automatizar bonificaciones, penalidades y notas de crédito.
- Reemplazar el uso operativo de Sistema de Liquidación (Excel) (APP-26).
- Exponer tablero/portal de conciliación para clientes B2B.

| Componente de costo | Estimación | Total |
|---|---|---|
| Azure AKS + Azure SQL | USD 1,200/mes | USD 8,400 |
| Equipo desarrollo y QA | USD 28,000/mes | USD 196,000 |
| Integración ERP Financiero (On Premises) (APP-25) y validación financiera | One-time | USD 40,000 |
| Pruebas de reglas, evidencias y portal | One-time | USD 15,600 |
| **TOTAL INI-06** | | **USD 260,000** |

**Beneficios que aporta:**

- Conciliación en menos de 1 día.
- Reducción de facturas observadas y notas de crédito manuales.
- Liberación de caja retenida por disputas.
- Auditoría financiera con trazabilidad de evidencias y SLA.

**ROI esperado:** recuperación de USD 2.4M retenidos por un solo cliente y reducción de facturas observadas de 7% a menos de 1.5%.

---

## 4. Resumen de costos por iniciativa

| Iniciativa | Duración | Costo estimado | Prioridad |
|---|---|---|---|
| INI-05 Observabilidad, seguridad y gobierno multinube | 6 meses | USD 145,000 | 1 |
| INI-02 Integración API-First y Event-Driven | 8 meses | USD 264,600 | 2 |
| INI-03 Modernización de última milla y gestión de excepciones | 5 meses | USD 135,000 | 3 |
| INI-01 Gestión unificada de órdenes e inventario end-to-end | 12 meses | USD 650,000 | 4 |
| INI-04 Optimización dinámica de rutas y despacho | 7 meses | USD 255,000 | 5 |
| INI-06 Conciliación financiera y liquidación automatizada | 7 meses | USD 260,000 | 6 |
| **TOTAL TRANSFORMACIÓN** | **36 meses** | **USD 1,709,600** | |

**Nota:** costos operativos recurrentes de infraestructura cloud no incluidos en el estimado de proyecto; se incorporan al presupuesto operativo de TI y al gobierno FinOps de INI-05.

---

## 5. Roadmap de implementación

```text
MES:       1    2    3    4    5    6    7    8    9    10   11   12
INI-05   [========================]                                      Observabilidad/IAM/IaC base
INI-02   [================================]                              APIs, eventos, contratos, colas
INI-03        [====================]                                      Última milla y excepciones
INI-01             [==============================================]      OMS centralizado / Orquestador de Pedidos (APP-02) + inventario + WMS Cloud piloto
INI-04                            [============================]         Rutas dinámicas
INI-06                                 [============================]    Motor liquidación

MES:       13   14   15   16   17   18   19   20   21   22   23   24
INI-01   [========]                                                       Despliegue WMS Cloud total y estabilización
INI-04   [====]                                                           Ajustes de optimización y ML
INI-06   [====]                                                           Cierre financiero y portal B2B
          [============================]                                  Transición 2: expansión, hardening y adopción

MES:       25   26   27   28   29   30   31   32   33   34   35   36
          [============================================]                  TO BE completo: optimización continua, FinOps,
                                                                          auditoría, DR y mejora de KPIs
```

### Hitos del roadmap

| Hito | Mes | Descripción | KPI esperado |
|---|---|---|---|
| H1 | Mes 2 | Correlation ID y tableros base de Plataforma de Observabilidad Unificada (PLT-01) | Trazabilidad inicial de pedidos y colas |
| H2 | Mes 4 | Bus de Eventos Central (PLT-03) piloto entre Orquestador de Pedidos (APP-02), WMS Principal (On Premises) (APP-06) y TMS (Transportation Management) (APP-11) | Integración desacoplada para flujo crítico |
| H3 | Mes 5 | App de Conductores (APP-15) offline-first y taxonomía de excepciones en producción piloto | 0 pérdida funcional de evidencias piloto |
| H4 | Mes 6 | Gobierno API-first, IAM base, secretos y pipelines IaC operativos | APIs críticas con políticas y despliegues reproducibles |
| H5 | Mes 8 | OMS centralizado / Orquestador de Pedidos (APP-02) MVP sobre Orquestador de Pedidos (APP-02) con validación, deduplicación e idempotencia | Defectos de órdenes <3% |
| H6 | Mes 10 | Motor de liquidación piloto con ERP Financiero (On Premises) (APP-25) y evidencias | Conciliación piloto <3 días |
| H7 | Mes 12 | Rutas dinámicas piloto integradas con TMS (Transportation Management) (APP-11) | Reducción de cambios manuales no trazados |
| H8 | Mes 14 | WMS Cloud estabilizado y vista unificada de inventario | Ajustes de inventario <0.5% |
| H9 | Mes 18 | Liquidación automatizada en operación estándar | Conciliación <1 día |
| H10 | Mes 24 | Transición 2 completa | 93% cumplimiento de promesa y 99.5% disponibilidad |
| H11 | Mes 36 | TO BE completo | 94% cumplimiento, 99.9% disponibilidad y 98% tracking confiable |

---

## 6. Análisis de dependencias

```text
INI-05 Observabilidad/Seguridad/Gobierno -> Todas las iniciativas
INI-02 API-First/Event-Driven -> INI-01, INI-03, INI-04, INI-06
INI-03 Última milla/Excepciones -> INI-04, INI-06
INI-01 OMS centralizado / Orquestador de Pedidos (APP-02)/Inventario -> INI-04, INI-06
INI-04 Rutas dinámicas -> Mejora continua de INI-03 e INI-06
INI-06 Liquidación automatizada -> Depende de estados, evidencias y SLA confiables
```

| Dependencia | Motivo | Mitigación |
|---|---|---|
| INI-01 depende de INI-02 | OMS centralizado / Orquestador de Pedidos (APP-02) e inventario requieren contratos, eventos y backpressure | Empezar INI-02 en mes 1 y entregar piloto en mes 4 |
| INI-03 depende parcialmente de INI-02 | Store-and-forward debe publicar eventos confiables | Usar adaptadores temporales hasta que Bus de Eventos Central (PLT-03) esté completo |
| INI-04 depende de INI-03 | Rutas dinámicas necesitan excepciones normalizadas | Habilitar taxonomía mínima antes del piloto de rutas |
| INI-06 depende de INI-01/INI-03 | Liquidación requiere órdenes, inventario, tracking y evidencias confiables | Piloto financiero con subconjunto de clientes y rutas |
| Todas dependen de INI-05 | Seguridad, trazabilidad y despliegues deben ser gobernados | Entregar baseline de observabilidad/IAM/IaC en primeros 6 meses |

---

## 7. Gestión de riesgos del plan de migración

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| OMS centralizado / Orquestador de Pedidos (APP-02) se interpreta como aplicación nueva y no como evolución de Orquestador de Pedidos (APP-02) | Media | Medio | Alinear decisión de arquitectura al inicio; si se crea app separada, actualizar `06`, `08` y `09` antes del diseño detallado |
| Migración WMS Cloud se extiende más de lo previsto | Media | Alto | Mantener WMS Principal (On Premises) (APP-06) en modo puente, con APIs/eventos y migración por centros |
| Contratos de eventos no son adoptados por todos los equipos | Media | Alto | Comité de gobierno API/eventos, versionamiento y pruebas de contrato obligatorias |
| Resistencia operativa en almacenes y última milla | Alta | Alto | Pilotos por centro/ruta, capacitación y soporte en campo |
| Costos cloud superiores al estimado | Media | Medio | Presupuesto FinOps, etiquetas obligatorias, alertas de gasto y revisión mensual |
| Datos históricos incompletos para rutas y liquidación | Media | Medio | Reglas de calidad de datos, reconciliación y ventanas de estabilización |

---

## 8. Beneficios esperados y ROI

| Beneficio | Valor anual estimado |
|---|---|
| Evitar penalidades en campañas por indisponibilidad WMS Principal (On Premises) (APP-06) | USD 1,100,000+ |
| Reducción de entregas fallidas y reintentos | USD 1,580,000 |
| Recuperación de disputas de liquidación | USD 2,400,000 |
| Reducción de costo por entrega por rutas dinámicas | USD 2,000,000+ |
| Reducción de errores por órdenes duplicadas/defectuosas | USD 300,000+ |
| **Beneficio total estimado año 1 post-TO BE** | **USD 7,380,000+** |
| **Inversión total transformación** | **USD 1,709,600** |
| **ROI estimado** | **~4.3x** |

---

## 9. Verificación de consistencia con aplicaciones

| Documento | Resultado de verificación | Acción requerida |
|---|---|---|
| `06_Mapa_Portafolio_Aplicaciones.md` | Las iniciativas usan aplicaciones y plataformas ya catalogadas: Orquestador de Pedidos (APP-02), Validador de Pedidos (APP-05), WMS Principal (On Premises) (APP-06), WMS Satélite (On Premises local) (APP-07), Control de Inventario (APP-08), TMS (Transportation Management) (APP-11), Optimizador de Rutas (GCP batch) (APP-12), App de Conductores (APP-15), Almacenamiento Evidencias (S3) (APP-16), Portal B2B (Trazabilidad) (APP-18), CRM de Atención al Cliente (APP-20), ERP Financiero (On Premises) (APP-25), Sistema de Liquidación (Excel) (APP-26), Plataforma de Observabilidad Unificada (PLT-01), Plataforma de Identidad y Accesos (IAM) (PLT-02), Bus de Eventos Central (PLT-03) y Plataforma IaC (PLT-04). Se explicita que Orquestador de Pedidos (APP-02) evoluciona a OMS centralizado en TO BE | Actualizado |
| `08_Mapeo_Aplicaciones_Tecnologia.md` | El documento es AS IS; las nuevas capacidades son TO BE y no obligan a alterar el stack AS IS | No requiere cambios |
| `09_ADM_Fases_CadenasValor_B_C_D_ASIS_TOBE.md` | La disposición TO BE contempla WMS Cloud, Servicio de Validación, Optimizador de Rutas en Tiempo Real, **Bus de Eventos Central (PLT-03)** (Azure Event Hubs + Service Bus), Servicio de Liquidación y plataformas PLT. Orquestador de Pedidos (APP-02) evoluciona a OMS centralizado; no se crea Event Store separado en AWS | Actualizado |

**Nota de arquitectura:** la línea base aprobada es que "OMS centralizado" sea la evolución TO BE de Orquestador de Pedidos (APP-02). Si el comité solicita tratarlo como aplicación separada, los cambios necesarios serían:

| Cambio potencial | Documento afectado | Detalle |
|---|---|---|
| Crear nuevo ID APP para OMS centralizado / Orquestador de Pedidos (APP-02) | `06_Mapa_Portafolio_Aplicaciones.md` | Agregar aplicación TO BE en capa core y ajustar resumen del portafolio |
| Definir stack del OMS centralizado / Orquestador de Pedidos (APP-02) | `08_Mapeo_Aplicaciones_Tecnologia.md` | Agregar fila TO BE o sección complementaria si se decide documentar tecnologías objetivo |
| Ajustar matriz de disposición | `09_ADM_Fases_CadenasValor_B_C_D_ASIS_TOBE.md` | Cambiar Orquestador de Pedidos (APP-02) de MODIFICAR a reemplazo parcial o integración con nuevo OMS centralizado / Orquestador de Pedidos (APP-02) |

No se recomienda este cambio para el Hito 1 porque el alcance funcional puede cubrirse con Orquestador de Pedidos (APP-02) evolucionado, manteniendo el catálogo estable.

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
