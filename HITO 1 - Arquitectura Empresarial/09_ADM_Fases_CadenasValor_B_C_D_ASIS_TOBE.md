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

**Guion de exposición (AS IS):** En recepción entran órdenes por varios canales sin la misma validación. Azure API Management (APP-01) expone APIs; el Orquestador (APP-02) y el Validador (APP-05) procesan en Azure AKS; clientes medianos usan el Portal B2B de Carga (APP-03) o el bucket S3 legado (APP-04); todo reserva inventario en el WMS Principal (APP-06). No hay bus de eventos ni backpressure: cuando el WMS se degrada la cola crece, y la deduplicación ya falló con treinta y dos mil pedidos duplicados.

#### Aplicaciones en esta fase
| App | Rol | Plataforma | Problema |
|---|---|---|---|
| Azure API Management (APP-01) | Gateway de APIs para clientes externos | Azure (PaaS) | Sin políticas de backpressure ni rate limiting por cliente |
| Orquestador de Pedidos (APP-02) | Recibe y procesa todas las órdenes | Azure AKS | Sin backpressure ante degradación WMS; cola ilimitada |
| Validador de Pedidos (APP-05) | Valida SKU, dirección y duplicados | Azure AKS | Falla deduplicación cuando cambia ID externo del cliente |
| APP-03 Portal B2B (Carga CSV/Excel) | Carga CSV/Excel para clientes medianos | SaaS externo | Sin validación automática; canal legado |
| Bucket S3 Legado (archivos) (APP-04) | Recepción de archivos histórica | AWS S3 | Deuda técnica; sin validación ni monitoreo |
| APP-06 WMS Principal (On Premises) | Confirma reserva de inventario al recibir orden | On Premises / SQL Server | Se satura bajo alta carga; bloqueo de tablas |

### Arquitectura Tecnológica

#### Infraestructura
| Componente | Tecnología | Plataforma | Problema |
|---|---|---|---|
| Gateway de APIs | Azure API Management | Azure PaaS | Sin circuit breaker ni throttling por cliente |
| APP-02 Orquestador de Pedidos | AKS (Kubernetes) | Azure | Sin HPA, sin KEDA; no escala en campaña |
| APP-06 WMS Principal (On Premises) | SQL Server | On Premises | Sin HA, sin auto-scaling; degradación en Cyber Days |
| Canal archivos | S3 bucket | AWS | Integración no monitoreada; sin SLA |
| Red/Conectividad | WAN privada | On Premises ↔ Azure | Sin redundancia hacia el WMS |

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

**Guion de exposición (AS IS):** En preparación el WMS Principal (APP-06) y los satélites locales (APP-07) guían picking e inventario on premises; los pickers operan con App Handhelds (APP-10) en dispositivos del almacén enlazados por Wi-Fi interno; IoT Core (APP-09) monitorea cámaras frías sin alertar al WMS; el ERP Financiero (APP-25) conserva inventario valorizado desactualizado. La sincronización horaria entre almacenes generó cuatro mil novecientos movimientos en conflicto en el caso.

#### Aplicaciones en esta fase
| App | Rol | Plataforma | Problema |
|---|---|---|---|
| APP-06 WMS Principal (On Premises) | Gestiona el inventario y guía el picking | On Premises / SQL Server | Bloqueo de tablas bajo alta carga |
| APP-07 WMS Satélite (On Premises local) | WMS local para almacenes pequeños | On Premises local | Sincronización horaria; conflictos al reconectar |
| App Handhelds (APP-10) | Guía al picker en el almacén | On Premises (dispositivo móvil) | Sin modo offline; depende de red Wi-Fi interna del almacén (infra — ver *Red almacenes*) |
| IoT Core (sensores temperatura) (APP-09) | Monitorea temperatura de cámaras refrigeradas | AWS IoT Core | Funciona bien; alertas no integradas con WMS |
| APP-25 ERP Financiero (On Premises) | Conserva inventario valorizado | On Premises | No actualizado en tiempo real; solo fin de mes |

### Arquitectura Tecnológica

#### Infraestructura
| Componente | Tecnología | Plataforma | Problema |
|---|---|---|---|
| APP-06 WMS Principal (On Premises) | SQL Server | On Premises | Sin HA ni replica hot-standby |
| APP-07 WMS Satélite (On Premises local) | BD local (tipo no especificado) | On Premises local | Sync horaria; sin reconciliación automática |
| Red almacenes (conectividad APP-10 ↔ WMS) | Wi-Fi interno | Infraestructura on premises · 14 CD | Sin failover; cortes registrados de 74 min |
| APP-09 IoT Core (sensores temperatura) | AWS IoT Core | AWS | Funciona; sin integración de alertas al **APP-06** WMS |

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

**Guion de exposición (AS IS):** En despacho el TMS (APP-11) consolida rutas y manifiestos en Azure; el Optimizador de Rutas (APP-12) corre en batch en GCP con tráfico desactualizado; transportistas terceros consultan el Portal Transportistas (APP-13); los manifiestos siguen en papel con el Sistema de Impresión (APP-14); la App de Conductores (APP-15) recibe rutas incompletas cuando el WMS respondió lento. El diecisiete por ciento de rutas se corrige a mano.

#### Aplicaciones en esta fase
| App | Rol | Plataforma | Problema |
|---|---|---|---|
| TMS (APP-11) | Gestiona rutas, manifiestos y transportistas | Azure | Recibe datos incompletos del WMS |
| Optimizador de Rutas (APP-12) | Genera rutas optimizadas con datos de tráfico | GCP (batch) | Solo batch; datos de tráfico llegan tarde |
| Portal Transportistas Tercerizados (APP-13) | Acceso de terceros a manifiestos | Azure | Sin alertas en tiempo real |
| Sistema Impresión Manifiestos (APP-14) | Imprime manifiestos físicos en cada centro | On Premises | Deuda técnica; papel sin trazabilidad |
| APP-15 App de Conductores | Recibe ruta y manifiesto en campo | AWS / DynamoDB | Recibe manifiestos parciales cuando WMS es lento |

### Arquitectura Tecnológica

#### Infraestructura
| Componente | Tecnología | Plataforma | Problema |
|---|---|---|---|
| TMS | Azure (tecnología interna no especificada) | Azure | Integración directa con WMS; sin eventos |
| APP-12 Optimizador de Rutas | GCP batch (stack no especificado) | GCP | Sin streaming; datos de tráfico desactualizados |
| Conectividad Azure ↔ GCP | Internet público | Multinube | Sin SLA de latencia; latencia variable |

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

**Guion de exposición (AS IS):** En entrega la App de Conductores (APP-15) navega, registra tracking en DynamoDB y captura evidencias en S3 (APP-16); los portales SaaS de Trazabilidad (APP-18) y Tracking Destinatarios (APP-19) muestran estados inconsistentes; la Pasarela de Pago Contra Entrega (APP-17) funciona sin observaciones críticas; el TMS (APP-11) actualiza con retraso. El offline frágil costó mil doscientas entregas sin firma en un incidente documentado.

#### Aplicaciones en esta fase
| App | Rol | Plataforma | Problema |
|---|---|---|---|
| APP-15 App de Conductores | Navegación, registro de entrega y evidencias | AWS / DynamoDB | Offline frágil; evidencias perdibles; motivos texto libre |
| Almacenamiento Evidencias (S3) (APP-16) | Almacena fotos y firmas de entrega | AWS S3 | Sin hash de integridad; evidencias sin garantía de completitud |
| DynamoDB (parte de APP-15) | Eventos de tracking y sincronización offline | AWS DynamoDB | Eventos pueden llegar fuera de orden al sincronizar |
| APP-18 Portal B2B (Trazabilidad) | Visibilidad de estados para clientes B2B | SaaS externo | Muestra estados con retraso y a veces inconsistentes |
| Portal Tracking Destinatarios (APP-19) | Seguimiento para destinatarios finales | SaaS externo | Datos de fuentes distintas a APP-18; inconsistencia percibida |
| Pasarela de Pago Contra Entrega (APP-17) | Procesa pagos contra entrega en campo | SaaS externo | Sin problemas reportados en el caso |
| TMS (APP-11) | Actualiza estados en Azure al recibir eventos | Azure | Recibe eventos con retraso |

### Arquitectura Tecnológica

#### Infraestructura
| Componente | Tecnología | Plataforma | Problema |
|---|---|---|---|
| APP-15 App de Conductores (backend) | AWS (servicio específico no indicado) | AWS | Sin mecanismo de retry robusto ante reinstalación |
| DynamoDB | AWS DynamoDB | AWS | No garantiza orden de eventos offline |
| Almacenamiento Evidencias (S3) (APP-16) | AWS S3 | AWS | Sin hash de integridad por archivo |
| Conectividad campo | Internet móvil 4G | Operadoras | Zonas con mala señal → offline no controlado |

---

## F5 — GESTIÓN DE EXCEPCIONES

### Arquitectura de Negocio

#### Puntos de Dolor
- La tasa de entrega fallida es 12.5% (8,500 paquetes diarios). El 34% de las fallas se relaciona con dirección o ausencia — problemas prevenibles antes de salir a ruta.
- Los motivos de excepción no están normalizados: cada conductor puede escribir texto libre o seleccionar categorías distintas para el mismo problema. Esto impide que el algoritmo de rutas en GCP aprenda correctamente.
- El CRM de atención usa una taxonomía diferente a la app y al TMS. Los reclamos no se correlacionan automáticamente con las excepciones.
- Cada reintento cuesta entre USD 1.20 y USD 2.80 según zona.

#### Roles
| Rol | Participación |
|---|---|
| Conductor | Registra la excepción y el motivo |
| Destinatario | Comunica imposibilidad de recibir |
| Atención al cliente | Gestiona el reclamo y decide acción |
| Cliente empresarial | Aprueba o rechaza reintentos |
| Planner | Reprograma reintento en TMS |
| Almacén | Recibe devoluciones |
| Finanzas | Evalúa costo del reintento o penalidad |

### Arquitectura de Datos

#### Entidades de Datos
| Entidad | Descripción | Problema AS IS |
|---|---|---|
| Excepción | Motivo de fallo, tipo, intento, conductor | Motivos no normalizados; texto libre permitido |
| Motivo de fallo | Categoría de la excepción | Taxonomía diferente en app, TMS y CRM |
| Reintento | Nuevo intento planificado con fecha y ventana | Sin validación previa de dirección o contacto |
| Devolución | Pedido que regresa al almacén | Se registra en WMS al llegar, sin trazabilidad intermedia |
| Reclamo | Registro en CRM del cliente o destinatario | Taxonomía desconectada del evento original |

### Arquitectura de Aplicaciones

**Guion de exposición (AS IS):** En excepciones la App de Conductores (APP-15) registra fallas con motivos en texto libre; el TMS (APP-11) planifica reintentos; el CRM de Atención (APP-20) usa otra taxonomía; el Portal B2B de Trazabilidad (APP-18) notifica tarde; las devoluciones llegan manualmente al WMS Principal (APP-06); el ML de Optimización de Rutas (APP-24) en GCP no aprende porque los motivos no están normalizados.

#### Aplicaciones en esta fase
| App | Rol | Plataforma | Problema |
|---|---|---|---|
| APP-15 App de Conductores | Registra excepción con motivo y evidencia | AWS | Permite texto libre; motivos no comparables |
| TMS (APP-11) | Visualiza excepciones y planifica reintentos | Azure | Recibe categorías inconsistentes de la app |
| CRM de Atención al Cliente (APP-20) | Abre reclamos y gestiona contacto con cliente | SaaS externo | Taxonomía diferente a app y TMS |
| APP-18 Portal B2B (Trazabilidad) | Notifica excepción al cliente B2B | SaaS externo | Notificación con retraso |
| APP-06 WMS Principal (On Premises) | Recibe devolución cuando el pedido vuelve | On Premises | Sin integración automática desde la excepción |
| ML / Optimización de Rutas (APP-24) | Aprende de histórico de rutas y excepciones | GCP | Motivos no normalizados impiden aprendizaje (Caso 6b R3) |

### Arquitectura Tecnológica

#### Infraestructura
| Componente | Tecnología | Plataforma | Problema |
|---|---|---|---|
| App backend excepciones | AWS | AWS | Sin validación de obligatoriedad de campos |
| CRM | SaaS externo | Nube proveedor | Sin integración con Event Store |
| TMS | Azure | Azure | Sin correlación automática excepción ↔ reclamo |

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

**Guion de exposición (AS IS):** En liquidación el ERP Financiero (APP-25) factura con datos desactualizados; el Sistema de Liquidación en Excel (APP-26) calcula penalidades a mano; la Plataforma de Analítica (APP-22) y los Dashboards Operativos (APP-23) consolidan en batch semanal en GCP; las evidencias en S3 (APP-16) no integran con finanzas; el Portal B2B de Trazabilidad (APP-18) no coincide con el ERP. De ahí conciliaciones de hasta veintitrés días y el siete por ciento de facturas observadas.

#### Aplicaciones en esta fase
| App | Rol | Plataforma | Problema |
|---|---|---|---|
| APP-25 ERP Financiero (On Premises) | Facturación y liquidación principal | On Premises | Factura desde reportes mensuales; sin tiempo real |
| Sistema de Liquidación (APP-26) | Cálculo de penalidades con reglas especiales | Excel local | Manual, propenso a errores, conciliación 23 días |
| Plataforma de Analítica (APP-22) | Consolida datos de todas las nubes | GCP (batch semanal) | Solo semanal; no sirve para conciliación operativa |
| Dashboards Operativos (APP-23) | Reportes para clientes y operaciones | GCP | Datos de la semana anterior |
| Almacenamiento Evidencias (S3) (APP-16) | Sustento de entrega para liquidación | AWS S3 | No integrado directamente con ERP Financiero (On Premises) |
| APP-18 Portal B2B (Trazabilidad) | Reportes de estado para cliente B2B | SaaS externo | Estados inconsistentes con ERP Financiero (On Premises) |

### Arquitectura Tecnológica

#### Infraestructura
| Componente | Tecnología | Plataforma | Problema |
|---|---|---|---|
| ERP | On Premises (tecnología no especificada) | On Premises | Sin APIs hacia sistemas cloud |
| Excel liquidación | Microsoft Excel local | PC usuario | Sin control de versiones ni auditoría |
| APP-22 Plataforma de Analítica (GCP) | GCP batch semanal | GCP | Sin streaming; incapaz de soportar conciliación diaria |
| Conectividad ERP ↔ Cloud | Sin integración en tiempo real | On Premises | Datos fluyen por archivos o reportes manuales |

---

# TO BE

> En *Arquitectura de Aplicaciones* de cada fase, el párrafo **Guion de exposición** resume qué se crea, modifica o elimina respecto al AS IS.

> **Convención (prompt Hito 1):** toda aplicación del AS IS de cada fase debe tener disposición explícita en el TO BE: **NUEVO**, **MODIFICAR**, **CONSERVAR** o **ELIMINAR**. Nomenclatura oficial: ver catálogo APP-01 a APP-26 en `06_Mapa_Portafolio_Aplicaciones.md`. Mapeo con Caso 6a/6b: portal SaaS → APP-03 (carga) + APP-18 (trazabilidad); WMS on premises del caso → APP-06; WMS local → APP-07.

---

## F1 — RECEPCIÓN DE ÓRDENES

### Arquitectura de Negocio

#### Objetivos
- Validar el 100% de órdenes en el momento del ingreso: dirección geo-validada, SKU existente, deduplicación por hash de contenido (no solo por ID externo).
- Implementar backpressure por cliente y prioridad por SLA para proteger el WMS en campaña.
- Eliminar el canal de archivos CSV/S3; migrar clientes medianos al Portal B2B (Carga CSV/Excel) con validación automática.
- Reducir defectos de ingreso de 6% a menos de 1%.

#### Roles
| Rol | Cambio TO BE |
|---|---|
| Cliente empresarial | Solo canal API o Portal B2B (Carga CSV/Excel) con validación en tiempo real |
| Mesa B2B | Se enfoca en onboarding; las excepciones de datos se resuelven antes del ingreso |
| Planeamiento | Recibe órdenes ya validadas y priorizadas por SLA |
| Sistema (automatizado) | Valida, deduplica y enruta sin intervención humana |

### Arquitectura de Datos

#### Entidades de Datos (cambios)
| Entidad | Cambio TO BE |
|---|---|
| Orden | ID interno + hash de contenido como clave idempotente; estado canónico desde el ingreso |
| Destinatario | Dirección geo-validada obligatoria antes de aceptar la orden |
| Estado del pedido | Modelo canónico: recibido → validado → reservado → pickeado → despachado → en ruta → entregado / fallido / devuelto → liquidado |

### Arquitectura de Aplicaciones

**Guion de exposición (TO BE):** En recepción validamos al ingreso: nuevo Servicio de Validación de Órdenes y Bus de Eventos (PLT-03) desacoplan el Orquestador (APP-02) del WMS (APP-06); fortalecemos Azure API Management (APP-01) con rate limiting y backpressure; eliminamos Validador (APP-05), bucket S3 (APP-04) y migramos el portal de carga (APP-03) a un canal unificado con validación automática.

#### NUEVO
| App | Descripción | Plataforma propuesta |
|---|---|---|
| Servicio de Validación de Órdenes | Valida dirección, SKU, SLA y deduplica por hash en tiempo real | Azure AKS |
| PLT-03 Bus de Eventos | Desacopla **APP-02** Orquestador de **APP-06** WMS; aplica backpressure | Azure Event Hubs |
| Servicio de Notificación (SMS/Email) (pre-entrega) | Confirma ventana horaria con destinatario antes de procesar | AWS SNS o SaaS |

#### MODIFICAR
| App | Cambio | Plataforma |
|---|---|---|
| Azure API Management (APP-01) | Agregar políticas de rate limiting, backpressure y OAuth 2.0 por cliente | Azure |
| Orquestador de Pedidos (APP-02) | Agregar circuit breaker, backpressure y prioridad por SLA; publicar a Event Hub | Azure AKS |
| APP-06 WMS Principal (On Premises) | Se mantiene en F1; recibe reservas vía Event Hub con backpressure (sin migración hasta F2) | On Premises |

#### ELIMINAR
| App | Motivo |
|---|---|
| Validador de Pedidos (APP-05) | Reemplazado por Servicio de Validación de Órdenes |
| Bucket S3 Legado (archivos) (APP-04) | Canal de archivos a deprecar; clientes migran a API o Portal B2B (Carga CSV/Excel) |
| APP-03 Portal B2B (Carga CSV/Excel) | Reemplazar por Portal B2B unificado con validación automática integrada |

### Arquitectura Tecnológica

#### Infraestructura (nueva o modificada)
| Componente | Tecnología TO BE | Cambio respecto AS IS |
|---|---|---|
| Bus de mensajes | Azure Event Hubs o Apache Kafka | NUEVO — no existía |
| APP-02 Orquestador de Pedidos | AKS + KEDA (auto-scaling por eventos) | MODIFICAR — agregar HPA y KEDA |
| API Management | Azure API Management con WAF y políticas avanzadas | MODIFICAR — agregar reglas de seguridad |
| APP-06 WMS Principal (On Premises) | Integración vía Event Hub; sin migración de plataforma en F1 | CONSERVAR — protegido con backpressure |

---

## F2 — PREPARACIÓN DE PEDIDOS

### Arquitectura de Negocio

#### Objetivos
- WMS Cloud con auto-scaling para absorber picos de hasta 3x sin degradación.
- Sincronización de inventario en tiempo real entre WMS Cloud y sistemas downstream (TMS, Portal B2B de Trazabilidad, ERP).
- Modo degradado automático con reconciliación al reconectar (eliminar conflictos manuales).
- Reducir ajustes de inventario de 2.8% a menos de 0.5%.

#### Roles
| Rol | Cambio TO BE |
|---|---|
| Picker | Guiado por handheld con datos de inventario en tiempo real |
| Sistema WMS Cloud | Publica movimientos a Event Hub automáticamente |
| Supervisor de frío | Recibe alertas automáticas del IoT si la temperatura sale de rango |
| ERP | Recibe actualizaciones de inventario vía API en tiempo real |

### Arquitectura de Datos

#### Entidades de Datos (cambios)
| Entidad | Cambio TO BE |
|---|---|
| Inventario | Single Source of Truth en WMS Cloud; replicado vía eventos |
| Movimiento de inventario | Publicado como evento en tiempo real al Event Hub con usuario, timestamp y motivo |
| Temperatura | Alertas integradas con WMS Cloud para bloquear despacho fuera de rango |

### Arquitectura de Aplicaciones

**Guion de exposición (TO BE):** En preparación reemplazamos WMS Principal (APP-06) y Satélite (APP-07) por WMS Cloud en Azure con auto-scaling y reconciliación automática; las App Handhelds (APP-10) ganan modo offline y red con backup 4G; IoT Core (APP-09) alerta al WMS Cloud; el ERP Financiero (APP-25) recibe inventario valorizado en tiempo real vía eventos.

#### NUEVO
| App | Descripción | Plataforma propuesta |
|---|---|---|
| WMS Cloud | Reemplaza APP-06 y APP-07; auto-scaling, HA multi-zona y modo degradado local | Azure (misma nube que TMS) |
| Servicio de Reconciliación | Detecta y resuelve conflictos de inventario automáticamente al reconectar | Azure AKS |

#### MODIFICAR
| App | Cambio | Plataforma |
|---|---|---|
| App Handhelds (APP-10) | Modo offline con sincronización segura al reconectar; red almacenes con failover 4G | On Premises (dispositivo móvil) |
| IoT Core (sensores temperatura) (APP-09) | Integrar alertas de temperatura con WMS Cloud para bloqueo automático de despacho | AWS IoT Core |
| APP-25 ERP Financiero (On Premises) | Integrar inventario valorizado en tiempo real vía API desde WMS Cloud y Event Hub | On Premises |

#### ELIMINAR
| App | Motivo |
|---|---|
| APP-06 WMS Principal (On Premises) | Reemplazado por WMS Cloud — migración progresiva por fases |
| APP-07 WMS Satélite (On Premises local) | Reemplazado por WMS Cloud con modo degradado local |

### Arquitectura Tecnológica

#### Infraestructura (nueva o modificada)
| Componente | Tecnología TO BE | Cambio respecto AS IS |
|---|---|---|
| WMS Cloud | Cloud (Azure, contenedores con auto-scaling) | NUEVO — reemplaza WMS Principal (APP-06) y WMS Satélite (APP-07) |
| Red almacenes | SD-WAN con failover 4G | MODIFICAR — agregar redundancia |
| Sincronización inventario | Event Hub (tiempo real) | NUEVO — reemplaza batch horario |

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
| TMS | Cierra manifiesto solo cuando WMS Cloud confirma todos los paquetes |
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

**Guion de exposición (TO BE):** En despacho el Optimizador pasa a tiempo real en GCP; el manifiesto digital reemplaza la impresión en papel (APP-14); el TMS (APP-11), la App de Conductores (APP-15) y el Portal Transportistas (APP-13) reciben manifiestos cerrados solo cuando WMS Cloud confirma todos los paquetes; se elimina el Optimizador batch (APP-12) anterior.

#### NUEVO
| App | Descripción | Plataforma propuesta |
|---|---|---|
| APP-12 Optimizador de Rutas RT | Optimizador en tiempo real con datos de tráfico live | GCP (GKE + Cloud Pub/Sub) |
| Manifiesto Digital | Cierre digital de manifiesto con confirmación WMS Cloud | Azure AKS (parte del TMS) |

#### MODIFICAR
| App | Cambio | Plataforma |
|---|---|---|
| TMS (APP-11) | Integrar con Event Hub para recibir confirmaciones de WMS Cloud en tiempo real | Azure |
| APP-15 App de Conductores | Recibir manifiesto digital completo; actualizable durante la jornada | AWS |
| Portal Transportistas Tercerizados (APP-13) | Acceso a manifiestos digitales en tiempo real; alertas ante cambios de ruta | Azure |

#### ELIMINAR
| App | Motivo |
|---|---|
| Sistema Impresión Manifiestos (APP-14) | Reemplazado por manifiesto digital en app |
| Optimizador de Rutas (APP-12) | Reemplazado por Optimizador de Rutas RT |

### Arquitectura Tecnológica

#### Infraestructura (nueva o modificada)
| Componente | Tecnología TO BE | Cambio respecto AS IS |
|---|---|---|
| APP-12 Optimizador de Rutas | GKE + Cloud Pub/Sub (GCP) | MODIFICAR — de batch a tiempo real |
| Conectividad Azure ↔ GCP | Azure ExpressRoute + Google Interconnect | NUEVO — reemplaza internet público |
| TMS | Azure AKS (modernizado con Event Hub) | MODIFICAR — agregar integración por eventos |

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
| Estado del pedido | Único estado canónico visible en todos los sistemas (Portal B2B de Trazabilidad, TMS, app, CRM) |

### Arquitectura de Aplicaciones

**Guion de exposición (TO BE):** En entrega creamos un Event Store de tracking como fuente canónica; rediseñamos la App de Conductores (APP-15) con offline robusto y motivos normalizados; S3 (APP-16) exige integridad; portales (APP-18, APP-19) y notificaciones (APP-21) leen el mismo estado; el TMS (APP-11) sincroniza en tiempo real; la Pasarela de Pago (APP-17) se conserva.

#### NUEVO
| App | Descripción | Plataforma propuesta |
|---|---|---|
| Event Store de Tracking | Ordena y valida eventos; fuente única de verdad del estado del pedido | AWS Kinesis + DynamoDB |

#### MODIFICAR
| App | Cambio | Plataforma |
|---|---|---|
| APP-15 App de Conductores | Rediseño de módulo offline: SQLite cifrado, retry robusto, evidencias atómicas, motivos normalizados obligatorios | AWS |
| Almacenamiento Evidencias (S3) (APP-16) | Agregar hash de integridad y política de retención por regulación | AWS S3 |
| APP-18 Portal B2B (Trazabilidad) | Conectar al Event Store canónico para mostrar estado real | SaaS / API |
| Portal Tracking Destinatarios (APP-19) | Conectar al Event Store; alinear estados con APP-18 y App de Conductores | SaaS / API |
| Servicio de Notificación (SMS/Email) — APP-21 | Ampliar para confirmación de ventana horaria y alertas proactivas al destinatario | SaaS / AWS SNS |
| TMS (APP-11) | Consumir y publicar estados desde Event Store; sincronización en tiempo real con app y portales | Azure |
| DynamoDB (parte de APP-15) | Pasa a réplica operacional; Event Store (Kinesis) es la fuente canónica de eventos | AWS DynamoDB |

#### CONSERVAR
| App | Motivo |
|---|---|
| Pasarela de Pago Contra Entrega (APP-17) | Sin cambios en F4; integración estable según el caso; sigue procesando pagos contra entrega | SaaS externo |

#### ELIMINAR
| App | Motivo |
|---|---|
| — | No hay aplicaciones a eliminar en esta fase |

### Arquitectura Tecnológica

#### Infraestructura (nueva o modificada)
| Componente | Tecnología TO BE | Cambio respecto AS IS |
|---|---|---|
| Streaming de eventos | AWS Kinesis Data Streams | NUEVO — reemplaza DynamoDB aislado |
| Almacenamiento Evidencias (S3) (APP-16) | AWS S3 + cifrado AES-256 + Object Lock | MODIFICAR — agregar integridad |
| App backend | AWS ECS Fargate (sin gestión de servidores) | MODIFICAR — escala automáticamente |
| MDM dispositivos | MDM (⚠️ herramienta a evaluar en HITO 2) | NUEVO — gestión de dispositivos de conductores |

---

## F5 — GESTIÓN DE EXCEPCIONES

### Arquitectura de Negocio

#### Objetivos
- Taxonomía de motivos normalizada y obligatoria en app, TMS y CRM (misma clasificación).
- Validar dirección y confirmar disponibilidad del destinatario antes de salir a ruta, reduciendo el 34% de fallas prevenibles.
- Alimentar el optimizador de rutas en GCP con datos de excepciones limpios y consistentes.
- Automatizar la decisión de reintento vs. devolución según reglas contractuales.

#### Roles
| Rol | Cambio TO BE |
|---|---|
| Conductor | Selecciona motivo de taxonomía controlada; no puede usar texto libre como motivo principal |
| Atención | Misma taxonomía que app y TMS; correlación automática excepción ↔ reclamo |
| Sistema | Propone acción (reintento / devolución) basado en reglas y ML |

### Arquitectura de Datos

#### Entidades de Datos (cambios)
| Entidad | Cambio TO BE |
|---|---|
| Motivo de excepción | Taxonomía canónica compartida por app, TMS y CRM |
| Excepción | Publicada como evento al Event Store; correlacionada automáticamente con reclamo |
| Reintento | Planificado con pre-validación de dirección y contacto |

### Arquitectura de Aplicaciones

**Guion de exposición (TO BE):** En excepciones un nuevo Servicio de Excepciones unifica la taxonomía; la App de Conductores (APP-15), el CRM (APP-20), el TMS (APP-11) y el Portal B2B de Trazabilidad (APP-18) comparten la misma clasificación; WMS Cloud recibe devoluciones por eventos; el ML de Optimización de Rutas (APP-24) reentrena con datos limpios del Event Store.

#### NUEVO
| App | Descripción | Plataforma propuesta |
|---|---|---|
| Servicio de Excepciones | Gestiona taxonomía canónica, reglas de decisión y correlación con reclamos | Azure AKS |

#### MODIFICAR
| App | Cambio | Plataforma |
|---|---|---|
| APP-15 App de Conductores | Taxonomía normalizada obligatoria; campos obligatorios por tipo de excepción | AWS |
| CRM de Atención al Cliente (APP-20) | Adoptar misma taxonomía canónica; integrar con Event Store | SaaS externo |
| TMS (APP-11) | Recibir excepciones estandarizadas; automatizar decisión reintento / devolución | Azure |
| APP-18 Portal B2B (Trazabilidad) | Notificaciones de excepción en tiempo real vía Event Store; estados alineados con TMS y app | SaaS externo |
| WMS Cloud | Recibir devoluciones automáticamente desde Servicio de Excepciones vía Event Hub (reemplaza APP-06/APP-07 desde F2) | Azure |
| ML / Optimización de Rutas (APP-24) | Reentrenar con taxonomía canónica de excepciones; alimentado por Event Store | GCP |

#### ELIMINAR
| App | Motivo |
|---|---|
| — | No hay aplicaciones a eliminar en esta fase |

### Arquitectura Tecnológica

#### Infraestructura (nueva o modificada)
| Componente | Tecnología TO BE | Cambio respecto AS IS |
|---|---|---|
| Servicio de excepciones | Azure AKS | NUEVO |
| ML predicción | GCP (tecnología a definir en HITO 2) | NUEVO — requiere datos limpios de excepciones |
| Integración CRM ↔ Event Store | API / webhooks desde Event Hub | NUEVO |

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

**Guion de exposición (TO BE):** En liquidación el Servicio de Liquidación reemplaza Excel (APP-26) y concilia automáticamente WMS Cloud, TMS, App y ERP; el ERP Financiero (APP-25), analítica streaming (APP-22), dashboards (APP-23), evidencias S3 (APP-16) y Portal B2B de Trazabilidad (APP-18) se alinean a la misma fuente; un portal de conciliación permite al cliente validar en tiempo real.

#### NUEVO
| App | Descripción | Plataforma propuesta |
|---|---|---|
| Servicio de Liquidación | Concilia automáticamente WMS + TMS + App + ERP; calcula penalidades | Azure AKS + Azure SQL |
| Portal de Conciliación para Clientes | Permite al cliente ver el estado de su liquidación en tiempo real | Azure (Web) |
| APP-22 Analítica en Streaming | Consolida datos operativos en tiempo real | GCP (BigQuery + Dataflow streaming) |

#### MODIFICAR
| App | Cambio | Plataforma |
|---|---|---|
| APP-25 ERP Financiero (On Premises) | Agregar API de integración en tiempo real con el Servicio de Liquidación | On Premises (transitorio) |
| Dashboards Operativos (APP-23) | Conectar a BigQuery streaming para reportes en tiempo real | GCP |
| Almacenamiento Evidencias (S3) (APP-16) | Exponer evidencias vía API al Servicio de Liquidación; hash de integridad obligatorio | AWS S3 |
| APP-18 Portal B2B (Trazabilidad) | Reportes de liquidación alineados con Event Store, ERP y evidencias S3 | SaaS externo |

#### ELIMINAR
| App | Motivo |
|---|---|
| Sistema de Liquidación (Excel) — APP-26 | Reemplazado por el Servicio de Liquidación automatizado |
| Plataforma de Analítica (GCP batch) — APP-22 | Reemplazada por analítica en streaming |

### Arquitectura Tecnológica

#### Infraestructura (nueva o modificada)
| Componente | Tecnología TO BE | Cambio respecto AS IS |
|---|---|---|
| APP-22 Plataforma de Analítica | GCP BigQuery + Dataflow streaming | MODIFICAR — de batch semanal a streaming |
| Servicio de liquidación | Azure AKS + Azure SQL | NUEVO |
| Integración ERP | API REST desde ERP hacia Azure | NUEVO — reemplaza archivos y reportes manuales |
| Conectividad AWS ↔ Azure | AWS Direct Connect + Azure ExpressRoute | NUEVO — reemplaza internet público |

---

## Matriz de disposición AS IS → TO BE (por fase)

Toda aplicación del AS IS debe aparecer en exactamente una disposición. Nombres según catálogo oficial (`06_Mapa_Portafolio_Aplicaciones.md`).

| Fase | App (AS IS) | Disposición TO BE | Detalle |
|---|---|---|---|
| **F1** | APP-01 Azure API Management | MODIFICAR | Rate limiting, OAuth 2.0, backpressure |
| **F1** | APP-02 Orquestador de Pedidos | MODIFICAR | Circuit breaker, Event Hub, prioridad SLA |
| **F1** | APP-03 Portal B2B (Carga CSV/Excel) | ELIMINAR | → Portal B2B unificado |
| **F1** | APP-04 Bucket S3 Legado (archivos) | ELIMINAR | Canal CSV/S3 deprecado |
| **F1** | APP-05 Validador de Pedidos | ELIMINAR | → Servicio de Validación de Órdenes |
| **F1** | APP-06 WMS Principal (On Premises) | MODIFICAR | Se conserva en F1; integración vía Event Hub |
| **F1** | *(nuevo)* Servicio de Validación de Órdenes | NUEVO | Reemplaza APP-05 |
| **F1** | PLT-03 Bus de Eventos | NUEVO | Desacopla **APP-02** y **APP-06** |
| **F2** | APP-06 WMS Principal (On Premises) | ELIMINAR | → WMS Cloud |
| **F2** | APP-07 WMS Satélite (On Premises local) | ELIMINAR | → WMS Cloud (modo degradado local) |
| **F2** | APP-09 IoT Core (sensores temperatura) | MODIFICAR | Alertas integradas con WMS Cloud |
| **F2** | APP-10 App Handhelds (picking) | MODIFICAR | Modo offline + sync segura |
| **F2** | APP-25 ERP Financiero (On Premises) | MODIFICAR | Inventario valorizado en tiempo real vía API |
| **F2** | *(nuevo)* WMS Cloud | NUEVO | Reemplaza APP-06 y APP-07 |
| **F2** | *(nuevo)* Servicio de Reconciliación | NUEVO | Conflictos de inventario automáticos |
| **F3** | APP-11 TMS | MODIFICAR | Event Hub + confirmaciones WMS Cloud |
| **F3** | APP-12 Optimizador de Rutas (GCP batch) | ELIMINAR | → Optimizador de Rutas RT |
| **F3** | APP-13 Portal Transportistas Tercerizados | MODIFICAR | Manifiestos digitales + alertas RT |
| **F3** | APP-14 Sistema Impresión Manifiestos | ELIMINAR | → Manifiesto Digital |
| **F3** | APP-15 App de Conductores | MODIFICAR | Manifiesto digital completo |
| **F3** | *(nuevo)* Optimizador de Rutas RT | NUEVO | Reemplaza APP-12 |
| **F3** | *(nuevo)* Manifiesto Digital | NUEVO | Reemplaza APP-14 |
| **F4** | APP-11 TMS | MODIFICAR | Estados desde Event Store |
| **F4** | APP-15 App de Conductores | MODIFICAR | Offline robusto, evidencias atómicas |
| **F4** | APP-16 Almacenamiento Evidencias (S3) | MODIFICAR | Hash de integridad, retención |
| **F4** | APP-17 Pasarela de Pago Contra Entrega | CONSERVAR | Sin cambios en esta fase |
| **F4** | APP-18 Portal B2B (Trazabilidad) | MODIFICAR | Conectado al Event Store canónico |
| **F4** | APP-19 Portal Tracking Destinatarios | MODIFICAR | Estados alineados con Event Store |
| **F4** | APP-21 Servicio de Notificación (SMS/Email) | MODIFICAR | Alertas proactivas al destinatario |
| **F4** | DynamoDB (parte de APP-15) | MODIFICAR | Réplica; Kinesis es fuente canónica |
| **F4** | *(nuevo)* Event Store de Tracking | NUEVO | Ordena y valida eventos |
| **F5** | APP-11 TMS | MODIFICAR | Excepciones estandarizadas, reintento automático |
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
| F2 | **APP-06** WMS sin auto-scaling ni HA | 6h caído Cyber Days; USD 1.1M penalidades | Tecnología |
| F2 | Sync horaria **APP-07** ↔ **APP-06** | 4,900 movimientos en conflicto | Datos |
| F2 | Inventario no disponible en tiempo real | 2.8% ajustes diarios; cancelaciones en alta rotación | Datos |
| F3 | **APP-12** Optimizador batch sin tráfico RT | 380 rutas inviables; 24,000 entregas fuera de ventana | Aplicaciones |
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
