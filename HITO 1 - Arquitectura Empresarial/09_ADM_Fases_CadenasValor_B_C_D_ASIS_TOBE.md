# ADM - Fases B, C y D: AS IS y TO BE con Cadena de Valor
## RutaExpress Fulfillment & Transporte

> **Para el comité de arquitectura** — Documento **más operativo** del Hito 1: AS IS y TO BE por fase de cadena de valor (F1–F6), con arquitectura de negocio, datos, apps y tecnología. **Mensaje clave:** cada fila indica qué **APP** se conserva, modifica o reemplaza y cuándo entra **PLT-03**; usar junto con `06` (catálogo) y `11` (roadmap).

---

# VALUE STREAM: Entrega de Pedido Logístico

```
  CLIENTE ENVÍA ORDEN                                              CLIENTE RECIBE PAGO
        │                                                                   ▲
        ▼                                                                   │
 ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
 │     F1     │  │     F2     │  │     F3     │  │     F4     │  │     F6     │
 │ RECEPCIÓN  │─►│PREPARACIÓN │─►│ DESPACHO   │─►│  ENTREGA   │─►│LIQUIDACIÓN │
 │ DE ÓRDENES │  │ DE PEDIDOS │  │ DE PEDIDOS │  │ DEL PEDIDO │  │Y DEVOLUC.  │
 └────────────┘  └────────────┘  └────────────┘  └─────┬──────┘  └────────────┘
                                                         │
                                                  ┌──────▼──────┐
                                                  │     F5      │
                                                  │  GESTIÓN DE │
                                                  │ EXCEPCIONES │
                                                  └─────────────┘
```

Fuente: Caso 6a — las 6 fases de la cadena de valor están explícitamente descritas en el documento.

---

# AS IS

> En *Arquitectura de Aplicaciones* de cada fase, el párrafo **Guion de exposición** resume el landscape actual para leer en voz alta (nombre oficial + identificador entre paréntesis).
>
> **Plataformas de infraestructura:** nomenclatura unificada con [`07_Mapa_Infraestructura.md`](07_Mapa_Infraestructura.md) §2.2 — **On Premises (Lima)**, **Cloud MS Azure (EEUU)**, **Cloud AWS (EEUU)**, **Cloud GCP (EEUU)**, **Cloud SaaS - Software as a Service (EEUU)**. Cada bloque *Infraestructura* incluye un resumen de plataformas activas en esa fase.

---

## F1 — RECEPCIÓN DE ÓRDENES

### Arquitectura de Negocio

#### Puntos de Dolor
- El 6% de órdenes ingresa con defectos (direcciones incompletas, SKUs inexistentes, pedidos duplicados) y no se detectan en el ingreso — explotan más adelante en la cadena.
- Un cliente envió dos veces 32,000 pedidos por reintento de API. La deduplicación falló porque cambió el identificador externo. Se generaron rutas fantasma y se consumieron horas de operación.
- No hay backpressure entre el orquestador y el WMS. Cuando el WMS se degrada, la cola crece sin control.
- Clientes medianos siguen enviando archivos CSV/Excel, canal sin validación automática.

#### Roles
| Rol | Participación |
|---|---|
| Cliente empresarial | Envía órdenes por API, Portal B2B (Carga CSV/Excel) o archivo |
| Integración TI (cliente) | Gestiona la conexión API del cliente |
| Mesa B2B | Soporte a clientes con problemas de integración |
| Planeamiento | Recibe y prioriza órdenes según SLA |
| Almacén | Recibe confirmación de órdenes para preparar |
| Atención al cliente | Gestiona excepciones tempranas de datos |

### Arquitectura de Datos

#### Entidades de Datos
| Entidad | Descripción | Problema AS IS |
|---|---|---|
| Orden | ID interno + ID externo cliente, canal, SLA, ventana | ID externo no es clave única confiable |
| Línea de pedido | SKU, cantidad, lote, tipo de servicio | SKUs no validados contra catálogo |
| SKU | Referencia de producto con atributos logísticos | Catálogo no centralizado |
| Destinatario | Nombre, dirección, teléfono, contacto | Direcciones no geo-validadas |
| Promesa / SLA | Fecha compromiso, ventana horaria, prioridad | No se verifica disponibilidad antes de aceptar |
| Canal | API / Portal B2B (Carga CSV/Excel) / CSV / S3 | Múltiples canales sin normalización |

### Arquitectura de Aplicaciones

**Guion de exposición (AS IS):** En recepción entran órdenes por varios canales sin la misma validación. Azure API Management (APP-01) expone APIs; Orquestador de Pedidos (APP-02) y Validador de Pedidos (APP-05) procesan en Cloud MS Azure (EEUU); clientes medianos usan Portal B2B (Carga CSV/Excel) (APP-03) en Cloud SaaS - Software as a Service (EEUU) o Bucket S3 Legado (archivos) (APP-04) en Cloud AWS (EEUU); todo reserva inventario en WMS Principal (On Premises) (APP-06) en On Premises (Lima). No hay Bus de Eventos Central (PLT-03) ni backpressure: cuando WMS Principal (On Premises) (APP-06) se degrada la cola crece, y la deduplicación ya falló con treinta y dos mil pedidos duplicados.

#### Aplicaciones en esta fase
| App | Rol | Plataforma | Problema |
|---|---|---|---|
| Azure API Management (APP-01) | Gateway de APIs para clientes externos | Cloud MS Azure (EEUU) | Sin políticas de backpressure ni rate limiting por cliente |
| Orquestador de Pedidos (APP-02) | Recibe y procesa todas las órdenes | Cloud MS Azure (EEUU) | Sin backpressure ante degradación WMS; cola ilimitada |
| Validador de Pedidos (APP-05) | Valida SKU, dirección y duplicados | Cloud MS Azure (EEUU) | Falla deduplicación cuando cambia ID externo del cliente |
| APP-03 Portal B2B (Carga CSV/Excel) | Carga CSV/Excel para clientes medianos | Cloud SaaS - Software as a Service (EEUU) | Sin validación automática; canal legado |
| Bucket S3 Legado (archivos) (APP-04) | Recepción de archivos histórica | Cloud AWS (EEUU) | Deuda técnica; sin validación ni monitoreo |
| APP-06 WMS Principal (On Premises) | Confirma reserva de inventario al recibir orden | On Premises (Lima) | Se satura bajo alta carga; bloqueo de tablas |

### Arquitectura Tecnológica

#### Infraestructura

**Plataformas (resumen):** Cloud MS Azure (EEUU) · On Premises (Lima) · Cloud AWS (EEUU) · Cloud SaaS - Software as a Service (EEUU)

| Componente | Tecnología | Plataforma | Problema |
|---|---|---|---|
| Gateway de APIs | Azure API Management | Cloud MS Azure (EEUU) | Sin circuit breaker ni throttling por cliente |
| APP-02 Orquestador de Pedidos | AKS (Kubernetes) | Cloud MS Azure (EEUU) | Sin HPA, sin KEDA; no escala en campaña |
| APP-06 WMS Principal (On Premises) | SQL Server | On Premises (Lima) | Sin HA, sin auto-scaling; degradación en Cyber Days |
| Canal archivos | S3 bucket | Cloud AWS (EEUU) | Integración no monitoreada; sin SLA |
| Red/Conectividad | WAN privada | On Premises (Lima) · Cloud MS Azure (EEUU) | Sin redundancia hacia el WMS |

---

## F2 — PREPARACIÓN DE PEDIDOS

### Arquitectura de Negocio

#### Puntos de Dolor
- El WMS se degrada bajo alta carga bloqueando tablas de inventario (Cyber Days: 6 horas caído).
- Los WMS Satélite (On Premises local) de almacenes pequeños sincronizan cada hora. En 74 minutos de desconexión se acumularon 4,900 movimientos en conflicto que retrasaron 18,000 pedidos.
- El inventario físico se mueve más rápido que las sincronizaciones: 2.8% de movimientos genera ajustes por diferencia, daño o conteo tardío.
- El ERP conserva inventario valorizado pero no siempre actualizado en tiempo real.

#### Roles
| Rol | Participación |
|---|---|
| Jefe de almacén | Supervisa la preparación del pedido |
| Picker | Ejecuta el picking guiado por handheld |
| Verificador | Confirma el pedido antes de cerrar |
| Control de calidad | Revisa productos especiales o dañados |
| Supervisor de frío | Controla temperatura en cámaras refrigeradas |
| Inventario | Gestiona ajustes y diferencias |

### Arquitectura de Datos

#### Entidades de Datos
| Entidad | Descripción | Problema AS IS |
|---|---|---|
| Inventario | Stock por SKU, ubicación, lote, vencimiento | Múltiples fuentes de verdad (**APP-06**, **APP-07**, **APP-25** ERP) |
| Movimiento de inventario | Entrada, salida, picking, ajuste, devolución | 2.8% genera ajuste; no siempre auditable |
| Ubicación de almacén | Pasillo, nivel, posición, tipo | Desincronización entre **APP-06** y **APP-07** |
| Ola de picking | Agrupación de líneas para un picker | Se genera con inventario potencialmente desactualizado |
| SKU (atributos logísticos) | Temperatura requerida, custodia, lote, vencimiento | No centralizado; discrepancias entre sistemas |
| Excepción de preparación | Daño, faltante, vencimiento, ubicación incorrecta | No siempre registrada con datos estructurados |

### Arquitectura de Aplicaciones

**Guion de exposición (AS IS):** En preparación el WMS Principal (APP-06) y los satélites locales (APP-07) guían picking e inventario en On Premises (Lima); Control de Inventario (APP-08) no refleja stock en tiempo real frente a esos WMS; los pickers operan con App Handhelds (APP-10) enlazados por Wi-Fi interno; IoT Core (APP-09) en Cloud AWS (EEUU) monitorea cámaras frías sin alertar al WMS; el ERP Financiero (APP-25) conserva inventario valorizado desactualizado. La sincronización horaria entre almacenes generó cuatro mil novecientos movimientos en conflicto en el caso.

#### Aplicaciones en esta fase
| App | Rol | Plataforma | Problema |
|---|---|---|---|
| Control de Inventario (APP-08) | Complemento de inventario on premises | On Premises (Lima) | Stock no reflejado en tiempo real vs WMS Principal (APP-06) / WMS Satélite (APP-07) |
| APP-06 WMS Principal (On Premises) | Gestiona el inventario y guía el picking | On Premises (Lima) | Bloqueo de tablas bajo alta carga |
| APP-07 WMS Satélite (On Premises local) | WMS local para almacenes pequeños | On Premises (Lima) | Sincronización horaria; conflictos al reconectar |
| App Handhelds (APP-10) | Guía al picker en el almacén | On Premises (Lima) | Sin modo offline; depende de red Wi-Fi interna del almacén (infra — ver *Red almacenes*) |
| IoT Core (sensores temperatura) (APP-09) | Monitorea temperatura de cámaras refrigeradas | Cloud AWS (EEUU) | Funciona bien; alertas no integradas con WMS |
| APP-25 ERP Financiero (On Premises) | Conserva inventario valorizado | On Premises (Lima) | No actualizado en tiempo real; solo fin de mes |

### Arquitectura Tecnológica

#### Infraestructura

**Plataformas (resumen):** On Premises (Lima) · Cloud AWS (EEUU)

| Componente | Tecnología | Plataforma | Problema |
|---|---|---|---|
| APP-06 WMS Principal (On Premises) | SQL Server | On Premises (Lima) | Sin HA ni replica hot-standby |
| APP-07 WMS Satélite (On Premises local) | BD local (tipo no especificado) | On Premises (Lima) | Sync horaria; sin reconciliación automática |
| Red almacenes (conectividad APP-10 ↔ WMS) | Wi-Fi interno | On Premises (Lima) | Sin failover; cortes registrados de 74 min |
| APP-09 IoT Core (sensores temperatura) | AWS IoT Core | Cloud AWS (EEUU) | Funciona; sin integración de alertas a WMS Principal (On Premises) (APP-06) |

---

## F3 — DESPACHO DE PEDIDOS

### Arquitectura de Negocio

#### Puntos de Dolor
- El optimizador de rutas usa datos de tráfico con retraso porque corre en batch. En una jornada de lluvia generó 380 rutas inviables; planners corrigieron a mano y 24,000 entregas llegaron fuera de ventana.
- El 17% de rutas se modifica manualmente después de generarse, sin registrar causa estructurada.
- Las rutas se generan sin esperar confirmación completa del WMS; algunos manifiestos salen con paquetes faltantes.
- Los manifiestos se imprimen físicamente en cada centro; canal paper es deuda técnica.

#### Roles
| Rol | Participación |
|---|---|
| Planner de transporte | Revisa y cierra rutas generadas |
| Supervisor de despacho | Coordina salida de vehículos |
| Transportista | Recibe manifiesto y confirma carga |
| Conductor | Recibe ruta en app móvil |
| Seguridad | Valida salida de vehículos |
| Cliente empresarial | Recibe confirmación de despacho |

### Arquitectura de Datos

#### Entidades de Datos
| Entidad | Descripción | Problema AS IS |
|---|---|---|
| Ruta | Secuencia de paradas, vehículo, conductor, ventana | 17% modificadas a mano sin causa documentada |
| Manifiesto | Lista de paquetes por ruta y vehículo | Se genera con datos incompletos del WMS |
| Vehículo | Placa, tipo, capacidad, disponibilidad | Datos de disponibilidad no siempre confiables |
| Conductor | Asignación a vehículo y zona | No siempre actualizado en tiempo real |
| Restricción de carga | Temperatura, zona, tipo de producto | No siempre aplicada automáticamente |
| Datos de tráfico | Condiciones viales en tiempo real | Llegan con retraso al optimizador batch |

### Arquitectura de Aplicaciones

**Guion de exposición (AS IS):** En despacho TMS (Transportation Management) (APP-11) consolida rutas y manifiestos en Cloud MS Azure (EEUU); Optimizador de Rutas (GCP batch) (APP-12) corre en batch en Cloud GCP (EEUU) con tráfico desactualizado; transportistas terceros consultan Portal Transportistas Tercerizados (APP-13); los manifiestos siguen en papel con Sistema Impresión Manifiestos (APP-14) en On Premises (Lima); App de Conductores (APP-15) en Cloud AWS (EEUU) recibe rutas incompletas cuando WMS Principal (On Premises) (APP-06) respondió lento. El diecisiete por ciento de rutas se corrige a mano.

#### Aplicaciones en esta fase
| App | Rol | Plataforma | Problema |
|---|---|---|---|
| TMS (Transportation Management) (APP-11) | Gestiona rutas, manifiestos y transportistas | Cloud MS Azure (EEUU) | Recibe datos incompletos del WMS |
| Optimizador de Rutas (APP-12) | Genera rutas optimizadas con datos de tráfico | Cloud GCP (EEUU) | Solo batch; datos de tráfico llegan tarde |
| Portal Transportistas Tercerizados (APP-13) | Acceso de terceros a manifiestos | Cloud MS Azure (EEUU) | Sin alertas en tiempo real |
| Sistema Impresión Manifiestos (APP-14) | Imprime manifiestos físicos en cada centro | On Premises (Lima) | Deuda técnica; papel sin trazabilidad |
| APP-15 App de Conductores | Recibe ruta y manifiesto en campo | Cloud AWS (EEUU) | Recibe manifiestos parciales cuando WMS es lento |

### Arquitectura Tecnológica

#### Infraestructura

**Plataformas (resumen):** Cloud MS Azure (EEUU) · Cloud GCP (EEUU)

| Componente | Tecnología | Plataforma | Problema |
|---|---|---|---|
| TMS (Transportation Management) (APP-11) | Azure (tecnología interna no especificada) | Cloud MS Azure (EEUU) | Integración directa con WMS Principal (On Premises) (APP-06); sin eventos |
| APP-12 Optimizador de Rutas | GCP batch (stack no especificado) | Cloud GCP (EEUU) | Sin streaming; datos de tráfico desactualizados |
| Conectividad Azure ↔ GCP | Internet público | Cloud MS Azure (EEUU) · Cloud GCP (EEUU) | Sin SLA de latencia; latencia variable |

---

## F4 — ENTREGA DEL PEDIDO

### Arquitectura de Negocio

#### Puntos de Dolor
- La app de conductores guarda eventos offline, pero si el conductor reinstala la app o cambia de equipo antes de sincronizar, se pierden firmas y fotos. Un incidente resultó en 1,200 entregas sin firma digital; el cliente retuvo el pago.
- El 8% de eventos de tracking llega con más de 20 minutos de retraso. Los clientes llaman preguntando por paquetes que ya fueron entregados.
- Los estados en el Portal B2B (Trazabilidad) son inconsistentes con la realidad porque los eventos offline se sincronizan fuera de orden.
- Picos de 130,000 eventos/día en campaña vs. 44,000 en día normal.

#### Roles
| Rol | Participación |
|---|---|
| Conductor | Ejecuta la entrega y registra evidencias |
| Destinatario | Recibe el pedido y firma |
| Supervisor de ruta | Monitorea el avance en tiempo real |
| Atención al cliente | Responde consultas de seguimiento |
| Cliente empresarial | Monitorea el estado de sus pedidos |
| Seguridad | Gestiona incidentes en campo |

### Arquitectura de Datos

#### Entidades de Datos
| Entidad | Descripción | Problema AS IS |
|---|---|---|
| Evento de tracking | Cambio de estado con timestamp, GPS, fuente | 8% con retraso >20 min; pueden llegar fuera de orden |
| Evidencia de entrega | Foto, firma digital, geolocalización, timestamp | Se pierden al reinstalar app o cambiar equipo |
| Intento de entrega | Número de intento, resultado, conductor | Sin trazabilidad completa entre intentos |
| Ubicación del conductor | GPS cada 2 minutos | Retraso cuando hay mala señal |
| Pago contra entrega | Monto, método, estado | Integrado con pasarela SaaS; sin incidentes reportados |

### Arquitectura de Aplicaciones

**Guion de exposición (AS IS):** En entrega App de Conductores (APP-15) en Cloud AWS (EEUU) navega, registra tracking en DynamoDB y captura evidencias en Almacenamiento Evidencias (S3) (APP-16); Portal B2B (Trazabilidad) (APP-18), Portal Tracking Destinatarios (APP-19) y Pasarela de Pago Contra Entrega (APP-17) operan en Cloud SaaS - Software as a Service (EEUU) con estados inconsistentes; TMS (Transportation Management) (APP-11) en Cloud MS Azure (EEUU) actualiza con retraso. El offline frágil costó mil doscientas entregas sin firma en un incidente documentado.

#### Aplicaciones en esta fase
| App | Rol | Plataforma | Problema |
|---|---|---|---|
| APP-15 App de Conductores | Navegación, registro de entrega y evidencias | Cloud AWS (EEUU) | Offline frágil; evidencias perdibles; motivos texto libre |
| Almacenamiento Evidencias (S3) (APP-16) | Almacena fotos y firmas de entrega | Cloud AWS (EEUU) | Sin hash de integridad; evidencias sin garantía de completitud |
| DynamoDB (parte de APP-15) | Eventos de tracking y sincronización offline | Cloud AWS (EEUU) | Eventos pueden llegar fuera de orden al sincronizar |
| APP-18 Portal B2B (Trazabilidad) | Visibilidad de estados para clientes B2B | Cloud SaaS - Software as a Service (EEUU) | Muestra estados con retraso y a veces inconsistentes |
| Portal Tracking Destinatarios (APP-19) | Seguimiento para destinatarios finales | Cloud SaaS - Software as a Service (EEUU) | Datos de fuentes distintas a APP-18; inconsistencia percibida |
| Pasarela de Pago Contra Entrega (APP-17) | Procesa pagos contra entrega en campo | Cloud SaaS - Software as a Service (EEUU) | Sin problemas reportados en el caso |
| TMS (Transportation Management) (APP-11) | Actualiza estados en Azure al recibir eventos | Cloud MS Azure (EEUU) | Recibe eventos con retraso |

### Arquitectura Tecnológica

#### Infraestructura

**Plataformas (resumen):** Cloud AWS (EEUU) · Cloud MS Azure (EEUU) · Cloud SaaS - Software as a Service (EEUU)

| Componente | Tecnología | Plataforma | Problema |
|---|---|---|---|
| APP-15 App de Conductores (backend) | AWS (servicio específico no indicado) | Cloud AWS (EEUU) | Sin mecanismo de retry robusto ante reinstalación |
| DynamoDB | Cloud AWS (EEUU) | Cloud AWS (EEUU) | No garantiza orden de eventos offline |
| Almacenamiento Evidencias (S3) (APP-16) | Cloud AWS (EEUU) | Cloud AWS (EEUU) | Sin hash de integridad por archivo |
| Conectividad campo | Internet móvil 4G | Cloud AWS (EEUU) | Zonas con mala señal → offline no controlado |

---

## F5 — GESTIÓN DE EXCEPCIONES

### Arquitectura de Negocio

#### Puntos de Dolor
- La tasa de entrega fallida es 12.5% (8,500 paquetes diarios). El 34% de las fallas se relaciona con dirección o ausencia — problemas prevenibles antes de salir a ruta.
- Los motivos de excepción no están normalizados: cada conductor puede escribir texto libre o seleccionar categorías distintas para el mismo problema. Esto impide que el algoritmo de rutas en GCP aprenda correctamente.
- CRM de Atención al Cliente (APP-20) usa una taxonomía diferente a App de Conductores (APP-15) y TMS (Transportation Management) (APP-11). Los reclamos no se correlacionan automáticamente con las excepciones.
- Cada reintento cuesta entre USD 1.20 y USD 2.80 según zona.

#### Roles
| Rol | Participación |
|---|---|
| Conductor | Registra la excepción y el motivo |
| Destinatario | Comunica imposibilidad de recibir |
| Atención al cliente | Gestiona el reclamo y decide acción |
| Cliente empresarial | Aprueba o rechaza reintentos |
| Planner | Reprograma reintento en TMS (Transportation Management) (APP-11) |
| Almacén | Recibe devoluciones |
| Finanzas | Evalúa costo del reintento o penalidad |

### Arquitectura de Datos

#### Entidades de Datos
| Entidad | Descripción | Problema AS IS |
|---|---|---|
| Excepción | Motivo de fallo, tipo, intento, conductor | Motivos no normalizados; texto libre permitido |
| Motivo de fallo | Categoría de la excepción | Taxonomía diferente en App de Conductores (APP-15), TMS (Transportation Management) (APP-11) y CRM de Atención al Cliente (APP-20) |
| Reintento | Nuevo intento planificado con fecha y ventana | Sin validación previa de dirección o contacto |
| Devolución | Pedido que regresa al almacén | Se registra en WMS al llegar, sin trazabilidad intermedia |
| Reclamo | Registro en CRM del cliente o destinatario | Taxonomía desconectada del evento original |

### Arquitectura de Aplicaciones

**Guion de exposición (AS IS):** En excepciones App de Conductores (APP-15) en Cloud AWS (EEUU) registra fallas con motivos en texto libre; TMS (Transportation Management) (APP-11) en Cloud MS Azure (EEUU) planifica reintentos; CRM de Atención al Cliente (APP-20) en Cloud SaaS - Software as a Service (EEUU) usa otra taxonomía; Portal B2B (Trazabilidad) (APP-18) notifica tarde; las devoluciones llegan manualmente a WMS Principal (On Premises) (APP-06); ML / Optimización de Rutas (GCP) (APP-24) en Cloud GCP (EEUU) no aprende porque los motivos no están normalizados.

#### Aplicaciones en esta fase
| App | Rol | Plataforma | Problema |
|---|---|---|---|
| APP-15 App de Conductores | Registra excepción con motivo y evidencia | Cloud AWS (EEUU) | Permite texto libre; motivos no comparables |
| TMS (Transportation Management) (APP-11) | Visualiza excepciones y planifica reintentos | Cloud MS Azure (EEUU) | Recibe categorías inconsistentes de la app |
| CRM de Atención al Cliente (APP-20) | Abre reclamos y gestiona contacto con cliente | Cloud SaaS - Software as a Service (EEUU) | Taxonomía diferente a app y TMS |
| APP-18 Portal B2B (Trazabilidad) | Notifica excepción al cliente B2B | Cloud SaaS - Software as a Service (EEUU) | Notificación con retraso |
| APP-06 WMS Principal (On Premises) | Recibe devolución cuando el pedido vuelve | On Premises (Lima) | Sin integración automática desde la excepción |
| ML / Optimización de Rutas (APP-24) | Aprende de histórico de rutas y excepciones | Cloud GCP (EEUU) | Motivos no normalizados impiden aprendizaje (Caso 6b R3) |

### Arquitectura Tecnológica

#### Infraestructura

**Plataformas (resumen):** Cloud AWS (EEUU) · Cloud MS Azure (EEUU) · Cloud SaaS - Software as a Service (EEUU)

| Componente | Tecnología | Plataforma | Problema |
|---|---|---|---|
| App backend excepciones | AWS | Cloud AWS (EEUU) | Sin validación de obligatoriedad de campos |
| CRM de Atención al Cliente (APP-20) | Cloud SaaS - Software as a Service (EEUU) | Cloud SaaS - Software as a Service (EEUU) | Sin integración con Event Store |
| TMS (Transportation Management) (APP-11) | Azure | Cloud MS Azure (EEUU) | Sin correlación automática excepción ↔ reclamo |

---

## F6 — LIQUIDACIÓN Y DEVOLUCIONES

### Arquitectura de Negocio

#### Puntos de Dolor
- La conciliación entre nubes y sistemas locales toma hasta 23 días. Una cadena retail retuvo USD 2.4M porque sus reportes mostraban menos entregas exitosas que RutaExpress. La conciliación involucró archivos de AWS, reportes del TMS, capturas del Portal B2B (Trazabilidad) y registros del WMS.
- El 7% de facturas queda observado por clientes por diferencias de estado, evidencia, tarifa o penalidad.
- Las notas de crédito por penalidades especiales se calculan con hojas Excel.
- Mensualmente se facturan más de 2 millones de servicios logísticos sin automatización.

#### Roles
| Rol | Participación |
|---|---|
| Finanzas | Factura y gestiona notas de crédito |
| Operaciones | Informa resultados de entrega |
| Cliente empresarial | Valida y aprueba la liquidación |
| Atención | Gestiona disputas y observaciones |
| Legal | Revisa penalidades contractuales |
| APP-22 Plataforma de Analítica | Consolida datos para informes |
| Almacén | Reporta devoluciones recibidas |

### Arquitectura de Datos

#### Entidades de Datos
| Entidad | Descripción | Problema AS IS |
|---|---|---|
| Liquidación | Resumen de servicios prestados por período | Se genera con datos de múltiples sistemas sin reconciliación automática |
| Factura | Documento de cobro con evidencia | 7% observada por diferencias entre sistemas |
| Penalidad / Bonificación | Cálculo según SLA contractual | Calculada manualmente en Excel para contratos especiales |
| Devolución | Pedidos que regresan al almacén | Estado en WMS; no siempre reflejado en Portal B2B (Trazabilidad) o ERP |
| Evidencia de entrega | Fotos, firmas, geolocalización usadas para sustentar la factura | Almacenadas en AWS S3; no siempre accesibles desde ERP |
| Reporte de cliente | Trazabilidad completa del pedido para el cliente | Generado semanalmente desde GCP con datos desactualizados |

### Arquitectura de Aplicaciones

**Guion de exposición (AS IS):** En liquidación ERP Financiero (On Premises) (APP-25) en On Premises (Lima) factura con datos desactualizados; Sistema de Liquidación (Excel) (APP-26) calcula penalidades a mano; Plataforma de Analítica (GCP batch) (APP-22) y Dashboards Operativos (APP-23) consolidan en batch semanal en Cloud GCP (EEUU); Almacenamiento Evidencias (S3) (APP-16) en Cloud AWS (EEUU) no integra con finanzas; Portal B2B (Trazabilidad) (APP-18) en Cloud SaaS - Software as a Service (EEUU) no coincide con ERP Financiero (On Premises) (APP-25). De ahí conciliaciones de hasta veintitrés días y el siete por ciento de facturas observadas.

#### Aplicaciones en esta fase
| App | Rol | Plataforma | Problema |
|---|---|---|---|
| APP-25 ERP Financiero (On Premises) | Facturación y liquidación principal | On Premises (Lima) | Factura desde reportes mensuales; sin tiempo real |
| Sistema de Liquidación (APP-26) | Cálculo de penalidades con reglas especiales | Excel local | Manual, propenso a errores, conciliación 23 días |
| Plataforma de Analítica (APP-22) | Consolida datos de todas las nubes | Cloud GCP (EEUU) | Solo semanal; no sirve para conciliación operativa |
| Dashboards Operativos (APP-23) | Reportes para clientes y operaciones | Cloud GCP (EEUU) | Datos de la semana anterior |
| Almacenamiento Evidencias (S3) (APP-16) | Sustento de entrega para liquidación | Cloud AWS (EEUU) | No integrado directamente con ERP Financiero (On Premises) |
| APP-18 Portal B2B (Trazabilidad) | Reportes de estado para cliente B2B | Cloud SaaS - Software as a Service (EEUU) | Estados inconsistentes con ERP Financiero (On Premises) |

### Arquitectura Tecnológica

#### Infraestructura

**Plataformas (resumen):** On Premises (Lima) · Cloud GCP (EEUU) · Cloud MS Azure (EEUU) · Cloud AWS (EEUU) · Cloud SaaS - Software as a Service (EEUU)

| Componente | Tecnología | Plataforma | Problema |
|---|---|---|---|
| ERP Financiero (On Premises) (APP-25) | On Premises (tecnología no especificada) | On Premises (Lima) | Sin APIs hacia sistemas cloud |
| Excel liquidación | Microsoft Excel local | On Premises (Lima) | Sin control de versiones ni auditoría |
| APP-22 Plataforma de Analítica (GCP) | GCP batch semanal | Cloud GCP (EEUU) | Sin streaming; incapaz de soportar conciliación diaria |
| Conectividad ERP ↔ Cloud | Sin integración en tiempo real | On Premises (Lima) · Cloud MS Azure (EEUU) · Cloud AWS (EEUU) | Datos fluyen por archivos o reportes manuales |

---

# TO BE

> En *Arquitectura de Aplicaciones* de cada fase, el párrafo **Guion de exposición** resume qué se crea, modifica o elimina respecto al AS IS.
>
> **Plataformas de infraestructura:** misma nomenclatura que AS IS y [`07_Mapa_Infraestructura.md`](07_Mapa_Infraestructura.md) §2.2.

> **Convención (prompt Hito 1):** toda aplicación del AS IS de cada fase debe tener disposición explícita en el TO BE: **NUEVO**, **MODIFICAR**, **CONSERVAR** o **ELIMINAR**. Nomenclatura oficial: ver catálogo APP-01 a APP-26 en `06_Mapa_Portafolio_Aplicaciones.md`. Mapeo con Caso 6a/6b: portal SaaS → APP-03 (carga) + APP-18 (trazabilidad); WMS on premises del caso → APP-06; WMS local → APP-07.

---

## F1 — RECEPCIÓN DE ÓRDENES

### Arquitectura de Negocio

#### Objetivos
- Validar el 100% de órdenes en el momento del ingreso: dirección geo-validada, SKU existente, deduplicación por hash de contenido (no solo por ID externo).
- Convertir Orquestador de Pedidos (APP-02) en un **OMS centralizado** para gobernar el ciclo de vida de la orden desde recepción hasta liquidación.
- Implementar backpressure por cliente y prioridad por SLA para proteger el WMS en campaña.
- Eliminar el canal de archivos CSV/S3; migrar clientes medianos al Portal B2B (Carga CSV/Excel) con validación automática.
- Reducir defectos de ingreso de 6% a menos de 1%.

#### Roles
| Rol | Cambio TO BE |
|---|---|
| Cliente empresarial | Solo canal API o Portal B2B (Carga CSV/Excel) con validación en tiempo real |
| Mesa B2B | Se enfoca en onboarding; las excepciones de datos se resuelven antes del ingreso |
| Planeamiento | Recibe órdenes ya validadas y priorizadas por SLA |
| OMS centralizado / Orquestador de Pedidos (APP-02) | Valida, deduplica, asegura idempotencia, gobierna el estado canónico y coordina reservas/liberaciones sin intervención humana |

### Arquitectura de Datos

#### Entidades de Datos (cambios)
| Entidad | Cambio TO BE |
|---|---|
| Orden | Gobernada por OMS centralizado / Orquestador de Pedidos (APP-02), con ID interno + hash de contenido como clave idempotente y estado canónico desde el ingreso |
| Destinatario | Dirección geo-validada obligatoria antes de aceptar la orden |
| Estado del pedido | Modelo canónico: recibido → validado → reservado → pickeado → despachado → en ruta → entregado / fallido / devuelto → liquidado |

### Arquitectura de Aplicaciones

**Guion de exposición (TO BE):** En recepción, Orquestador de Pedidos (APP-02) evoluciona a **OMS centralizado**: gobierna el ciclo de vida de la orden, mantiene el estado canónico, aplica idempotencia y coordina reservas/liberaciones con WMS Cloud, TMS y ERP. El nuevo Servicio de Validación de Órdenes y Bus de Eventos Central (PLT-03) desacoplan este OMS del WMS Principal (On Premises) (APP-06) durante la transición; fortalecemos Azure API Management (APP-01) con rate limiting y backpressure; eliminamos Validador de Pedidos (APP-05), Bucket S3 Legado (archivos) (APP-04) y migramos Portal B2B (Carga CSV/Excel) (APP-03) a un canal unificado con validación automática.

#### NUEVO
| App | Descripción | Plataforma propuesta |
|---|---|---|
| Servicio de Validación de Órdenes | Valida dirección, SKU, SLA y deduplica por hash en tiempo real | Cloud MS Azure (EEUU) |
| PLT-03 Bus de Eventos Central | Desacopla Orquestador de Pedidos (APP-02) de WMS Principal (On Premises) (APP-06); aplica backpressure | Cloud MS Azure (EEUU) |
| Servicio de Notificación (SMS/Email) (APP-21) (pre-entrega) | Confirma ventana horaria con destinatario antes de procesar | Cloud SaaS - Software as a Service (EEUU) |

#### MODIFICAR
| App | Cambio | Plataforma |
|---|---|---|
| Azure API Management (APP-01) | Agregar políticas de rate limiting, backpressure y OAuth 2.0 por cliente | Cloud MS Azure (EEUU) |
| Orquestador de Pedidos (APP-02) | Evolucionar a **OMS centralizado**: ciclo de vida de orden, estado canónico, idempotencia, deduplicación, reservas/liberaciones y publicación a Event Hub | Cloud MS Azure (EEUU) |
| APP-06 WMS Principal (On Premises) | Se mantiene en F1; recibe reservas vía Event Hub con backpressure (sin migración hasta F2) | On Premises (Lima) |

#### ELIMINAR
| App | Motivo |
|---|---|
| Validador de Pedidos (APP-05) | Reemplazado por Servicio de Validación de Órdenes |
| Bucket S3 Legado (archivos) (APP-04) | Canal de archivos a deprecar; clientes migran a API o Portal B2B (Carga CSV/Excel) |
| APP-03 Portal B2B (Carga CSV/Excel) | Reemplazar por Portal B2B unificado con validación automática integrada |

### Arquitectura Tecnológica

#### Infraestructura (nueva o modificada)

**Plataformas (resumen):** Cloud MS Azure (EEUU) · On Premises (Lima)

| Componente | Tecnología TO BE | Plataforma | Cambio respecto AS IS |
|---|---|---|---|
| Bus de mensajes | **Azure Event Hubs (PLT-03)** | Cloud MS Azure (EEUU) | NUEVO — no existía |
| APP-02 Orquestador de Pedidos / OMS centralizado | AKS + KEDA (auto-scaling por eventos) + store canónico de órdenes | Cloud MS Azure (EEUU) | MODIFICAR — evoluciona de orquestador técnico a OMS |
| API Management | Azure API Management con WAF y políticas avanzadas | Cloud MS Azure (EEUU) | MODIFICAR — agregar reglas de seguridad |
| APP-06 WMS Principal (On Premises) | Integración vía Event Hub; sin migración de plataforma en F1 | On Premises (Lima) | CONSERVAR — protegido con backpressure |

---

## F2 — PREPARACIÓN DE PEDIDOS

### Arquitectura de Negocio

#### Objetivos
- WMS Cloud con auto-scaling para absorber picos de hasta 3x sin degradación.
- Sincronización de inventario en tiempo real entre WMS Cloud y sistemas downstream (TMS (Transportation Management) (APP-11), Portal B2B (Trazabilidad) (APP-18), ERP Financiero (On Premises) (APP-25)).
- Modo degradado automático con reconciliación al reconectar (eliminar conflictos manuales).
- Reducir ajustes de inventario de 2.8% a menos de 0.5%.

#### Roles
| Rol | Cambio TO BE |
|---|---|
| Picker | Guiado por handheld con datos de inventario en tiempo real |
| Sistema WMS Cloud | Publica movimientos a Event Hub automáticamente |
| Supervisor de frío | Recibe alertas automáticas del IoT si la temperatura sale de rango |
| ERP Financiero (On Premises) (APP-25) | Recibe actualizaciones de inventario vía API en tiempo real |

### Arquitectura de Datos

#### Entidades de Datos (cambios)
| Entidad | Cambio TO BE |
|---|---|
| Inventario | Single Source of Truth en WMS Cloud; replicado vía eventos |
| Movimiento de inventario | Publicado como evento en tiempo real al Event Hub con usuario, timestamp y motivo |
| Temperatura | Alertas integradas con WMS Cloud para bloquear despacho fuera de rango |

### Arquitectura de Aplicaciones

**Guion de exposición (TO BE):** En preparación **WMS Cloud** (NUEVO) reemplaza WMS Principal (APP-06) y WMS Satélite (APP-07); **Control de Inventario (APP-08) se elimina** — no hay app TO BE homóloga, la capacidad queda en el inventario único de WMS Cloud; las App Handhelds (APP-10) ganan modo offline y red con backup 4G; IoT Core (APP-09) alerta al WMS Cloud; el ERP Financiero (APP-25) recibe inventario valorizado en tiempo real vía eventos.

#### NUEVO
| App | Descripción | Plataforma propuesta |
|---|---|---|
| WMS Cloud | Reemplaza APP-06 y APP-07; auto-scaling, HA multi-zona y modo degradado local | Cloud MS Azure (EEUU) |
| Servicio de Reconciliación | Detecta y resuelve conflictos de inventario automáticamente al reconectar | Cloud MS Azure (EEUU) |

#### MODIFICAR
| App | Cambio | Plataforma |
|---|---|---|
| App Handhelds (APP-10) | Modo offline con sincronización segura al reconectar; red almacenes con failover 4G | On Premises (Lima) |
| IoT Core (sensores temperatura) (APP-09) | Integrar alertas de temperatura con WMS Cloud para bloqueo automático de despacho | Cloud AWS (EEUU) |
| APP-25 ERP Financiero (On Premises) | Integrar inventario valorizado en tiempo real vía API desde WMS Cloud y Event Hub | On Premises (Lima) |

#### ELIMINAR
| App | Motivo |
|---|---|
| APP-06 WMS Principal (On Premises) | Reemplazado por WMS Cloud — migración progresiva por fases |
| APP-07 WMS Satélite (On Premises local) | Reemplazado por WMS Cloud con modo degradado local |
| Control de Inventario (APP-08) | Sin equivalente TO BE — capacidad absorbida por WMS Cloud |

### Arquitectura Tecnológica

#### Infraestructura (nueva o modificada)

**Plataformas (resumen):** Cloud MS Azure (EEUU) · On Premises (Lima)

| Componente | Tecnología TO BE | Plataforma | Cambio respecto AS IS |
|---|---|---|---|
| WMS Cloud | Cloud (Azure, contenedores con auto-scaling) | Cloud MS Azure (EEUU) | NUEVO — reemplaza WMS Principal (APP-06) y WMS Satélite (APP-07); APP-08 eliminado |
| Red almacenes | SD-WAN con failover 4G | On Premises (Lima) | MODIFICAR — agregar redundancia |
| Sincronización inventario | Event Hub (tiempo real) | Cloud MS Azure (EEUU) | NUEVO — reemplaza batch horario |

---

## F3 — DESPACHO DE PEDIDOS

### Arquitectura de Negocio

#### Objetivos
- Generar rutas en tiempo real con datos de tráfico actualizados, no en batch.
- Cerrar manifiestos solo con paquetes confirmados por WMS Cloud.
- Reducir rutas modificadas manualmente de 17% a menos de 5%, registrando causa estructurada.
- Eliminar manifiestos en papel.

#### Roles
| Rol | Cambio TO BE |
|---|---|
| Planner de transporte | Interviene solo en excepciones; el optimizador re-optimiza automáticamente |
| TMS (Transportation Management) (APP-11) | Cierra manifiesto solo cuando WMS Cloud confirma todos los paquetes |
| APP-12 Optimizador de Rutas | Corre en tiempo real en GCP; re-optimiza cada 30 min o ante evento crítico |
| Conductor | Recibe manifiesto digital completo y actualizado |

### Arquitectura de Datos

#### Entidades de Datos (cambios)
| Entidad | Cambio TO BE |
|---|---|
| Ruta | Generada en tiempo real; re-optimizable durante la jornada |
| Manifiesto | Digital; cerrado solo con confirmación completa de WMS Cloud |
| Modificación de ruta | Requiere motivo estructurado (clima / capacidad / tráfico / cliente / planificación) |
| Datos de tráfico | Consumidos en tiempo real desde API de tráfico vía Pub/Sub |

### Arquitectura de Aplicaciones

**Guion de exposición (TO BE):** En despacho Optimizador de Rutas en Tiempo Real reemplaza Optimizador de Rutas (GCP batch) (APP-12); el manifiesto digital reemplaza Sistema Impresión Manifiestos (APP-14); TMS (Transportation Management) (APP-11), App de Conductores (APP-15) y Portal Transportistas Tercerizados (APP-13) reciben manifiestos cerrados solo cuando WMS Cloud confirma todos los paquetes.

#### NUEVO
| App | Descripción | Plataforma propuesta |
|---|---|---|
| APP-12 Optimizador de Rutas RT | Optimizador en tiempo real con datos de tráfico live | Cloud GCP (EEUU) |
| Manifiesto Digital | Cierre digital de manifiesto con confirmación WMS Cloud | Cloud MS Azure (EEUU) |

#### MODIFICAR
| App | Cambio | Plataforma |
|---|---|---|
| TMS (Transportation Management) (APP-11) | Integrar con Event Hub para recibir confirmaciones de WMS Cloud en tiempo real | Cloud MS Azure (EEUU) |
| APP-15 App de Conductores | Recibir manifiesto digital completo; actualizable durante la jornada | Cloud AWS (EEUU) |
| Portal Transportistas Tercerizados (APP-13) | Acceso a manifiestos digitales en tiempo real; alertas ante cambios de ruta | Cloud MS Azure (EEUU) |

#### ELIMINAR
| App | Motivo |
|---|---|
| Sistema Impresión Manifiestos (APP-14) | Reemplazado por manifiesto digital en app |
| Optimizador de Rutas (APP-12) | Reemplazado por Optimizador de Rutas RT |

### Arquitectura Tecnológica

#### Infraestructura (nueva o modificada)

**Plataformas (resumen):** Cloud MS Azure (EEUU) · Cloud GCP (EEUU)

| Componente | Tecnología TO BE | Plataforma | Cambio respecto AS IS |
|---|---|---|---|
| APP-12 Optimizador de Rutas | GKE + Cloud Pub/Sub (GCP) | Cloud GCP (EEUU) | MODIFICAR — de batch a tiempo real |
| Conectividad Azure ↔ GCP | VPN site-to-site cifrada (Azure VPN Gateway) | Cloud MS Azure (EEUU) · Cloud GCP (EEUU) | NUEVO — reemplaza internet público sin cifrado garantizado |
| TMS (Transportation Management) (APP-11) | Azure AKS (modernizado con Event Hub) | Cloud MS Azure (EEUU) | MODIFICAR — agregar integración por eventos |

---

## F4 — ENTREGA DEL PEDIDO

### Arquitectura de Negocio

#### Objetivos
- Cero pérdidas de evidencias: la app cifra localmente y sube de forma atómica al reconectar, incluso tras reinstalación o cambio de dispositivo.
- Eventos de tracking en tiempo real (< 30 segundos end-to-end) para el 98% de pedidos.
- Pre-validar dirección y confirmar contacto con el destinatario antes de salir a ruta.
- Tracking visible con estados siempre consistentes entre Portal B2B (Trazabilidad), app y TMS.

#### Roles
| Rol | Cambio TO BE |
|---|---|
| Conductor | App con offline robusto; motivos de excepción normalizados y obligatorios |
| Destinatario | Recibe confirmación y puede gestionar ventana antes de la entrega |
| Supervisor de ruta | Dashboard en tiempo real con ubicación y estado de cada conductor |
| APP-18 Portal B2B (Trazabilidad) | Muestra estado real del pedido en tiempo real |

### Arquitectura de Datos

#### Entidades de Datos (cambios)
| Entidad | Cambio TO BE |
|---|---|
| Evento de tracking | Publicado a Kinesis en tiempo real; reordenado por Event Store antes de mostrarse |
| Evidencia de entrega | Cifrada localmente (AES-256); hash de integridad; subida atómica garantizada |
| Estado del pedido | Único estado canónico visible en todos los sistemas (Portal B2B (Trazabilidad) (APP-18), TMS (Transportation Management) (APP-11), App de Conductores (APP-15), CRM de Atención al Cliente (APP-20)) |

### Arquitectura de Aplicaciones

**Guion de exposición (TO BE):** En entrega creamos un Event Store de tracking como fuente canónica; rediseñamos App de Conductores (APP-15) con offline robusto y motivos normalizados; Almacenamiento Evidencias (S3) (APP-16) exige integridad; Portal B2B (Trazabilidad) (APP-18), Portal Tracking Destinatarios (APP-19) y Servicio de Notificación (SMS/Email) (APP-21) leen el mismo estado; TMS (Transportation Management) (APP-11) sincroniza en tiempo real; Pasarela de Pago Contra Entrega (APP-17) se conserva.

#### NUEVO
| App | Descripción | Plataforma propuesta |
|---|---|---|
| Event Store de Tracking | Ordena y valida eventos; fuente única de verdad del estado del pedido | Cloud AWS (EEUU) |

#### MODIFICAR
| App | Cambio | Plataforma |
|---|---|---|
| APP-15 App de Conductores | Rediseño de módulo offline: SQLite cifrado, retry robusto, evidencias atómicas, motivos normalizados obligatorios | Cloud AWS (EEUU) |
| Almacenamiento Evidencias (S3) (APP-16) | Agregar hash de integridad y política de retención por regulación | Cloud AWS (EEUU) |
| APP-18 Portal B2B (Trazabilidad) | Conectar al Event Store canónico para mostrar estado real | Cloud SaaS - Software as a Service (EEUU) |
| Portal Tracking Destinatarios (APP-19) | Conectar al Event Store; alinear estados con APP-18 y App de Conductores | Cloud SaaS - Software as a Service (EEUU) |
| Servicio de Notificación (SMS/Email) — APP-21 | Ampliar para confirmación de ventana horaria y alertas proactivas al destinatario | Cloud SaaS - Software as a Service (EEUU) |
| TMS (Transportation Management) (APP-11) | Consumir y publicar estados desde Event Store; sincronización en tiempo real con app y portales | Cloud MS Azure (EEUU) |
| DynamoDB (parte de APP-15) | Pasa a réplica operacional; Event Store (Kinesis) es la fuente canónica de eventos | Cloud AWS (EEUU) |

#### CONSERVAR
| App | Motivo |
|---|---|
| Pasarela de Pago Contra Entrega (APP-17) | Sin cambios en F4; integración estable según el caso; sigue procesando pagos contra entrega | Cloud SaaS - Software as a Service (EEUU) |

#### ELIMINAR
| App | Motivo |
|---|---|
| — | No hay aplicaciones a eliminar en esta fase |

### Arquitectura Tecnológica

#### Infraestructura (nueva o modificada)

**Plataformas (resumen):** Cloud AWS (EEUU) · Cloud SaaS - Software as a Service (EEUU)

| Componente | Tecnología TO BE | Plataforma | Cambio respecto AS IS |
|---|---|---|---|
| Streaming de eventos | AWS Kinesis Data Streams | Cloud AWS (EEUU) | NUEVO — reemplaza DynamoDB aislado |
| Almacenamiento Evidencias (S3) (APP-16) | AWS S3 + cifrado AES-256 + Object Lock | Cloud AWS (EEUU) | MODIFICAR — agregar integridad |
| App backend | AWS ECS Fargate (sin gestión de servidores) | Cloud AWS (EEUU) | MODIFICAR — escala automáticamente |
| MDM dispositivos | MDM (⚠️ herramienta a evaluar en HITO 2) | Cloud SaaS - Software as a Service (EEUU) | NUEVO — gestión de dispositivos de conductores |

---

## F5 — GESTIÓN DE EXCEPCIONES

### Arquitectura de Negocio

#### Objetivos
- Taxonomía de motivos normalizada y obligatoria en App de Conductores (APP-15), TMS (Transportation Management) (APP-11) y CRM de Atención al Cliente (APP-20) (misma clasificación).
- Validar dirección y confirmar disponibilidad del destinatario antes de salir a ruta, reduciendo el 34% de fallas prevenibles.
- Alimentar el optimizador de rutas en GCP con datos de excepciones limpios y consistentes.
- Automatizar la decisión de reintento vs. devolución según reglas contractuales.

#### Roles
| Rol | Cambio TO BE |
|---|---|
| Conductor | Selecciona motivo de taxonomía controlada; no puede usar texto libre como motivo principal |
| Atención | Misma taxonomía que App de Conductores (APP-15) y TMS (Transportation Management) (APP-11); correlación automática excepción ↔ reclamo |
| Sistema | Propone acción (reintento / devolución) basado en reglas y ML |

### Arquitectura de Datos

#### Entidades de Datos (cambios)
| Entidad | Cambio TO BE |
|---|---|
| Motivo de excepción | Taxonomía canónica compartida por App de Conductores (APP-15), TMS (Transportation Management) (APP-11) y CRM de Atención al Cliente (APP-20) |
| Excepción | Publicada como evento al Event Store; correlacionada automáticamente con reclamo |
| Reintento | Planificado con pre-validación de dirección y contacto |

### Arquitectura de Aplicaciones

**Guion de exposición (TO BE):** En excepciones un nuevo Servicio de Excepciones unifica la taxonomía; App de Conductores (APP-15), CRM de Atención al Cliente (APP-20), TMS (Transportation Management) (APP-11) y Portal B2B (Trazabilidad) (APP-18) comparten la misma clasificación; WMS Cloud recibe devoluciones por eventos; ML / Optimización de Rutas (GCP) (APP-24) reentrena con datos limpios del Event Store.

#### NUEVO
| App | Descripción | Plataforma propuesta |
|---|---|---|
| Servicio de Excepciones | Gestiona taxonomía canónica, reglas de decisión y correlación con reclamos | Cloud MS Azure (EEUU) |

#### MODIFICAR
| App | Cambio | Plataforma |
|---|---|---|
| APP-15 App de Conductores | Taxonomía normalizada obligatoria; campos obligatorios por tipo de excepción | Cloud AWS (EEUU) |
| CRM de Atención al Cliente (APP-20) | Adoptar misma taxonomía canónica; integrar con Event Store | Cloud SaaS - Software as a Service (EEUU) |
| TMS (Transportation Management) (APP-11) | Recibir excepciones estandarizadas; automatizar decisión reintento / devolución | Cloud MS Azure (EEUU) |
| APP-18 Portal B2B (Trazabilidad) | Notificaciones de excepción en tiempo real vía Event Store; estados alineados con TMS y app | Cloud SaaS - Software as a Service (EEUU) |
| WMS Cloud | Recibir devoluciones automáticamente desde Servicio de Excepciones vía Event Hub (reemplaza APP-06/APP-07 desde F2) | Cloud MS Azure (EEUU) |
| ML / Optimización de Rutas (APP-24) | Reentrenar con taxonomía canónica de excepciones; alimentado por Event Store | Cloud GCP (EEUU) |

#### ELIMINAR
| App | Motivo |
|---|---|
| — | No hay aplicaciones a eliminar en esta fase |

### Arquitectura Tecnológica

#### Infraestructura (nueva o modificada)

**Plataformas (resumen):** Cloud MS Azure (EEUU) · Cloud GCP (EEUU) · Cloud SaaS - Software as a Service (EEUU)

| Componente | Tecnología TO BE | Plataforma | Cambio respecto AS IS |
|---|---|---|---|
| Servicio de excepciones | Cloud MS Azure (EEUU) | Cloud MS Azure (EEUU) | NUEVO |
| ML predicción | GCP (tecnología a definir en HITO 2) | Cloud GCP (EEUU) | NUEVO — requiere datos limpios de excepciones |
| Integración CRM ↔ Event Store | API / webhooks desde Event Hub | Cloud SaaS - Software as a Service (EEUU) | NUEVO |

---

## F6 — LIQUIDACIÓN Y DEVOLUCIONES

### Arquitectura de Negocio

#### Objetivos
- Automatizar la conciliación: comparar datos de WMS, TMS, app y ERP en tiempo real sin intervención manual.
- Reducir conciliación de 23 días a menos de 1 día.
- Calcular penalidades y bonificaciones automáticamente según reglas contractuales.
- Reducir facturas observadas de 7% a menos de 1.5%.

#### Roles
| Rol | Cambio TO BE |
|---|---|
| Finanzas | Aprueba liquidaciones ya conciliadas automáticamente; no genera Excel |
| Cliente empresarial | Accede a portal de conciliación en tiempo real; reduce disputas |
| Sistema | Detecta diferencias automáticamente y genera alerta antes de emitir factura |

### Arquitectura de Datos

#### Entidades de Datos (cambios)
| Entidad | Cambio TO BE |
|---|---|
| Liquidación | Generada automáticamente desde Event Store canónico |
| Penalidad / Bonificación | Calculada por reglas de negocio en microservicio; no en Excel |
| Reporte de cliente | Generado en tiempo real desde la misma fuente que la factura |
| Evidencia | Accesible directamente desde el servicio de liquidación (S3 + hash) |

### Arquitectura de Aplicaciones

**Guion de exposición (TO BE):** En liquidación Servicio de Liquidación reemplaza Sistema de Liquidación (Excel) (APP-26) y concilia automáticamente WMS Cloud, TMS (Transportation Management) (APP-11), App de Conductores (APP-15) y ERP Financiero (On Premises) (APP-25); Plataforma de Analítica (GCP batch) (APP-22), Dashboards Operativos (APP-23), Almacenamiento Evidencias (S3) (APP-16) y Portal B2B (Trazabilidad) (APP-18) se alinean a la misma fuente; un portal de conciliación permite al cliente validar en tiempo real.

#### NUEVO
| App | Descripción | Plataforma propuesta |
|---|---|---|
| Servicio de Liquidación | Concilia automáticamente WMS + TMS + App + ERP; calcula penalidades | Cloud MS Azure (EEUU) |
| Portal de Conciliación para Clientes | Permite al cliente ver el estado de su liquidación en tiempo real | Cloud MS Azure (EEUU) |
| APP-22 Analítica en Streaming | Consolida datos operativos en tiempo real | Cloud GCP (EEUU) |

#### MODIFICAR
| App | Cambio | Plataforma |
|---|---|---|
| APP-25 ERP Financiero (On Premises) | Agregar API de integración en tiempo real con el Servicio de Liquidación | On Premises (Lima) |
| Dashboards Operativos (APP-23) | Conectar a BigQuery streaming para reportes en tiempo real | Cloud GCP (EEUU) |
| Almacenamiento Evidencias (S3) (APP-16) | Exponer evidencias vía API al Servicio de Liquidación; hash de integridad obligatorio | Cloud AWS (EEUU) |
| APP-18 Portal B2B (Trazabilidad) | Reportes de liquidación alineados con Event Store, ERP y evidencias S3 | Cloud SaaS - Software as a Service (EEUU) |

#### ELIMINAR
| App | Motivo |
|---|---|
| Sistema de Liquidación (Excel) — APP-26 | Reemplazado por el Servicio de Liquidación automatizado |
| Plataforma de Analítica (GCP batch) — APP-22 | Reemplazada por analítica en streaming |

### Arquitectura Tecnológica

#### Infraestructura (nueva o modificada)

**Plataformas (resumen):** Cloud GCP (EEUU) · Cloud MS Azure (EEUU) · On Premises (Lima) · Cloud AWS (EEUU) · Cloud SaaS - Software as a Service (EEUU)

| Componente | Tecnología TO BE | Plataforma | Cambio respecto AS IS |
|---|---|---|---|
| APP-22 Plataforma de Analítica | GCP BigQuery + Dataflow streaming | Cloud GCP (EEUU) | MODIFICAR — de batch semanal a streaming |
| Servicio de liquidación | Azure AKS + Azure SQL | Cloud MS Azure (EEUU) | NUEVO |
| Integración ERP | API REST desde ERP hacia Azure | On Premises (Lima) · Cloud MS Azure (EEUU) | NUEVO — reemplaza archivos y reportes manuales |
| Conectividad AWS ↔ Azure | VPN site-to-site cifrada (Azure VPN Gateway) | Cloud MS Azure (EEUU) · Cloud AWS (EEUU) | NUEVO — reemplaza internet público sin cifrado garantizado |

---

## Matriz de disposición AS IS → TO BE (por fase)

Toda aplicación del AS IS debe aparecer en exactamente una disposición. Nombres según catálogo oficial (`06_Mapa_Portafolio_Aplicaciones.md`).

| Fase | App (AS IS) | Disposición TO BE | Detalle |
|---|---|---|---|
| **F1** | APP-01 Azure API Management | MODIFICAR | Rate limiting, OAuth 2.0, backpressure |
| **F1** | APP-02 Orquestador de Pedidos | MODIFICAR | Evoluciona a **OMS centralizado / Orquestador de Pedidos**: estado canónico, idempotencia, deduplicación, reservas/liberaciones, Event Hub y prioridad SLA |
| **F1** | APP-03 Portal B2B (Carga CSV/Excel) | ELIMINAR | → Portal B2B unificado |
| **F1** | APP-04 Bucket S3 Legado (archivos) | ELIMINAR | Canal CSV/S3 deprecado |
| **F1** | APP-05 Validador de Pedidos | ELIMINAR | → Servicio de Validación de Órdenes |
| **F1** | APP-06 WMS Principal (On Premises) | MODIFICAR | Se conserva en F1; integración vía Event Hub |
| **F1** | *(nuevo)* Servicio de Validación de Órdenes | NUEVO | Reemplaza APP-05 |
| **F1** | PLT-03 Bus de Eventos | NUEVO | Desacopla **APP-02** y **APP-06** |
| **F2** | APP-08 Control de Inventario | ELIMINAR | Sin app TO BE — función absorbida por WMS Cloud |
| **F2** | APP-06 WMS Principal (On Premises) | ELIMINAR | → WMS Cloud |
| **F2** | APP-07 WMS Satélite (On Premises local) | ELIMINAR | → WMS Cloud (modo degradado local) |
| **F2** | APP-09 IoT Core (sensores temperatura) | MODIFICAR | Alertas integradas con WMS Cloud |
| **F2** | APP-10 App Handhelds (picking) | MODIFICAR | Modo offline + sync segura |
| **F2** | APP-25 ERP Financiero (On Premises) | MODIFICAR | Inventario valorizado en tiempo real vía API |
| **F2** | *(nuevo)* WMS Cloud | NUEVO | Reemplaza APP-06 y APP-07 |
| **F2** | *(nuevo)* Servicio de Reconciliación | NUEVO | Conflictos de inventario automáticos |
| **F3** | APP-11 TMS (Transportation Management) | MODIFICAR | Event Hub + confirmaciones WMS Cloud |
| **F3** | APP-12 Optimizador de Rutas (GCP batch) | ELIMINAR | → Optimizador de Rutas RT |
| **F3** | APP-13 Portal Transportistas Tercerizados | MODIFICAR | Manifiestos digitales + alertas en tiempo real |
| **F3** | APP-14 Sistema Impresión Manifiestos | ELIMINAR | → Manifiesto Digital |
| **F3** | APP-15 App de Conductores | MODIFICAR | Manifiesto digital completo |
| **F3** | *(nuevo)* Optimizador de Rutas RT | NUEVO | Reemplaza APP-12 |
| **F3** | *(nuevo)* Manifiesto Digital | NUEVO | Reemplaza APP-14 |
| **F4** | APP-11 TMS (Transportation Management) | MODIFICAR | Estados desde Event Store |
| **F4** | APP-15 App de Conductores | MODIFICAR | Offline robusto, evidencias atómicas |
| **F4** | APP-16 Almacenamiento Evidencias (S3) | MODIFICAR | Hash de integridad, retención |
| **F4** | APP-17 Pasarela de Pago Contra Entrega | CONSERVAR | Sin cambios en esta fase |
| **F4** | APP-18 Portal B2B (Trazabilidad) | MODIFICAR | Conectado al Event Store canónico |
| **F4** | APP-19 Portal Tracking Destinatarios | MODIFICAR | Estados alineados con Event Store |
| **F4** | APP-21 Servicio de Notificación (SMS/Email) | MODIFICAR | Alertas proactivas al destinatario |
| **F4** | DynamoDB (parte de APP-15) | MODIFICAR | Réplica; Kinesis es fuente canónica |
| **F4** | *(nuevo)* Event Store de Tracking | NUEVO | Ordena y valida eventos |
| **F5** | APP-11 TMS (Transportation Management) | MODIFICAR | Excepciones estandarizadas, reintento automático |
| **F5** | APP-15 App de Conductores | MODIFICAR | Taxonomía obligatoria de excepciones |
| **F5** | APP-18 Portal B2B (Trazabilidad) | MODIFICAR | Notificaciones de excepción en tiempo real |
| **F5** | APP-20 CRM de Atención al Cliente | MODIFICAR | Taxonomía canónica + Event Store |
| **F5** | APP-24 ML / Optimización de Rutas (GCP) | MODIFICAR | Reentrenar con datos limpios de excepciones |
| **F5** | WMS Cloud *(reemplaza APP-06/07 desde F2)* | MODIFICAR | Devoluciones automáticas vía Event Hub |
| **F5** | *(nuevo)* Servicio de Excepciones | NUEVO | Taxonomía y correlación reclamos |
| **F6** | APP-16 Almacenamiento Evidencias (S3) | MODIFICAR | API para Servicio de Liquidación |
| **F6** | APP-18 Portal B2B (Trazabilidad) | MODIFICAR | Reportes alineados con liquidación |
| **F6** | APP-22 Plataforma de Analítica (GCP batch) | ELIMINAR | → Analítica en Streaming |
| **F6** | APP-23 Dashboards Operativos | MODIFICAR | BigQuery streaming |
| **F6** | APP-25 ERP Financiero (On Premises) | MODIFICAR | API tiempo real con Servicio de Liquidación |
| **F6** | APP-26 Sistema de Liquidación (Excel) | ELIMINAR | → Servicio de Liquidación |
| **F6** | *(nuevo)* Servicio de Liquidación | NUEVO | Conciliación automática |
| **F6** | *(nuevo)* Portal de Conciliación para Clientes | NUEVO | Visibilidad al cliente B2B |

---

# GAPS / BRECHAS AS IS → TO BE

## Por Fase

| Fase | Brecha | Impacto | Tipo |
|---|---|---|---|
| F1 | Sin deduplicación robusta por hash de contenido | Incidente 32K pedidos duplicados | Aplicaciones |
| F1 | Sin backpressure en orquestador | Cola ilimitada ante degradación WMS | Tecnología |
| F1 | Canal de archivos CSV/S3 activo | Deuda técnica sin validación automática | Negocio |
| F2 | **APP-06** WMS Principal (On Premises) sin auto-scaling ni HA | 6h caído Cyber Days; USD 1.1M penalidades | Tecnología |
| F2 | Sync horaria **APP-07** ↔ **APP-06** | 4,900 movimientos en conflicto | Datos |
| F2 | Inventario no disponible en tiempo real | 2.8% ajustes diarios; cancelaciones en alta rotación | Datos |
| F3 | Optimizador de Rutas (GCP batch) (APP-12) sin tráfico en tiempo real | 380 rutas inviables; 24,000 entregas fuera de ventana | Aplicaciones |
| F3 | Rutas sin confirmación completa **APP-06** | Manifiestos con paquetes faltantes | Datos |
| F3 | Manifiestos físicos en papel | Sin trazabilidad digital; deuda técnica | Negocio |
| F4 | Offline frágil en **APP-15** | 1,200 firmas perdidas; USD 2.4M retenidos | Aplicaciones |
| F4 | Eventos de tracking sin orden garantizado | 8% con >20 min de retraso; estados inconsistentes | Datos |
| F4 | Sin hash de integridad en evidencias S3 | Evidencias cuestionadas en disputas | Tecnología |
| F5 | Taxonomía de excepciones no normalizada | Datos sucios para ML; reclamos no correlacionados | Datos |
| F5 | Sin validación previa de dirección/contacto | 34% fallas prevenibles; USD 1.20-2.80/reintento | Negocio |
| F6 | Liquidación manual en Excel | Conciliación 23 días; 7% facturas observadas | Aplicaciones |
| F6 | Analítica solo semanal | Sin visibilidad operativa; detecta problemas tarde | Tecnología |
| F6 | ERP sin integración en tiempo real | Facturación con datos del mes anterior | Integración |

## Transversal (aplica a todas las fases)

| Brecha | Descripción | Tipo |
|---|---|---|
| Sin bus de eventos central | Todas las integraciones son punto a punto y frágiles | Tecnología |
| Sin modelo canónico de estados | Estados distintos en **APP-06**, **APP-11**, **APP-15** y **APP-18** | Datos |
| Sin observabilidad unificada cross-cloud | Monitoreo aislado; sin visibilidad end-to-end | Tecnología |
| Sin IaC | Infraestructura aprovisionada manualmente | Tecnología |
| Sin seguridad Zero Trust | OAuth básico; datos personales en riesgo | Seguridad |
| Sin conexión privada entre nubes | Tráfico entre AWS, Azure y GCP por internet público | Tecnología |

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
