# ADM - Requirements Management
## RutaExpress Fulfillment & Transporte

> **Para el comité de arquitectura** — Catálogo de requisitos agrupados en **épicas Jira**. Cada RF/RNF sigue formato *Como … quiero … para …*. **Mensaje clave:** las épicas cubren la cadena Recepción → Almacén → Transporte → Última milla → Liquidación; en fases C y D cada historia se vincula a APP/PLT del diseño TO BE.

---

## 1. Propósito

Capturar, clasificar y mantener trazabilidad de todos los requisitos que guían las fases del ADM de RutaExpress. La gestión es transversal (fases A–F) y garantiza que los requisitos se satisfacen en el diseño de arquitectura.

---

## 2. Fuentes de Requisitos

| Fuente | Descripción |
|---|---|
| Estrategia del negocio | Objetivos del directorio: cumplimiento de promesa 94%, visibilidad 98%, disponibilidad 99,9% |
| Riesgos tecnológicos | Disponibilidad, integridad de datos y operación móvil |
| Stakeholders | Gerentes de almacén, transporte, finanzas, TI, atención al cliente |
| Incidentes operativos | Cyber Days: 240K pedidos en cola, USD 1,1M en penalidades, 19% entregas tardías |
| Clientes empresariales | SLA contractuales, APIs, reportes de trazabilidad, facturación |
| Regulación | Ley 29733 — Protección de Datos Personales (Perú) |
| Auditoría | Conciliación USD 2,4M retenidos; evidencias de entrega disputadas |

---

## 3. Convención del catálogo

| Elemento | Regla |
|---|---|
| **Épica** | Agrupa RF y RNF de un dominio de negocio; se registra en **Jira** como Epic |
| **RF-X.Y** | Requisito funcional de la épica X |
| **RNF-X.Y** | Requisito no funcional de la épica X |
| **Formato** | Tres líneas: *Como [rol], quiero [capacidad], para [beneficio]* |
| **Trazabilidad ADM** | Ver §5 — en qué fase TOGAF se validan las épicas |

---

## 4. Catálogo por Épicas

### Epica 1 — Gestión confiable de órdenes e inventario

*Recepción, validación, reserva de inventario y sincronización entre centros de distribución.*

#### Requisitos Funcionales

**RF-1.1 Unificación de estados**

Como sistema logístico,  
quiero mantener un modelo unificado de estados para todas las etapas del pedido,  
para garantizar información consistente entre los diferentes sistemas.

**RF-1.2 Validar órdenes de ingreso**

Como sistema de gestión de órdenes,  
quiero validar dirección, SKU, SLA, ventana, prioridad e idempotencia por cliente/canal/orden,  
para evitar que información inválida ingrese al flujo logístico.

**RF-1.3 Deduplicación idempotente**

Como responsable de integraciones B2B,  
quiero rechazar órdenes duplicadas usando ID externo del cliente y hash de contenido,  
para evitar incidentes masivos como los 32.000 pedidos duplicados.

**RF-1.4 Procesamiento multicanal con prioridad SLA**

Como operador de recepción,  
quiero procesar órdenes en tiempo real desde API, portal B2B y archivos con prioridad por SLA contractual,  
para cumplir promesas de entrega en campañas de alto volumen.

**RF-1.5 Sincronización de inventario en tiempo real**

Como supervisor de almacén,  
quiero que el inventario se actualice en tiempo real entre el WMS central, los almacenes satélite y los sistemas downstream,  
para eliminar ajustes manuales y el 2,8% de movimientos con discrepancia.

**RF-1.6 Modo degradado con reconciliación**

Como operador de almacén,  
quiero continuar operando en modo degradado cuando falle la conectividad y reconciliar automáticamente al reconectar,  
para no perder movimientos ni generar conflictos manuales.

**RF-1.7 Trazabilidad de movimientos de inventario**

Como auditor interno,  
quiero que cada movimiento de inventario registre usuario, timestamp y motivo,  
para investigar diferencias y cumplir auditorías.

**RF-1.8 Control de cadena de frío**

Como supervisor de productos farmacéuticos,  
quiero bloquear el despacho cuando la temperatura de cámara salga de rango,  
para cumplir condiciones de almacenamiento y evitar mermas.

**RF-1.9 Absorción de picos de recepción**

Como gerente de operaciones,  
quiero recibir hasta 180.000 órdenes por día sin degradación del flujo de recepción,  
para sostener Cyber Days y campañas estacionales.

#### Requisitos No Funcionales

**RNF-1.1 Consistencia de datos**

Como responsable de datos,  
quiero que cada cambio de estado incluya identificador de correlación, fecha, sistema de origen y número de versión,  
para detectar duplicados, mensajes fuera de orden e inconsistencias entre plataformas.

**RNF-1.2 Convergencia entre sistemas**

Como arquitecto de datos,  
quiero garantizar consistencia eventual con convergencia en menos de 60 segundos entre WMS, TMS y portales B2B,  
para que clientes y operación vean el mismo estado del pedido.

**RNF-1.3 Alerta de inconsistencias**

Como equipo de operaciones,  
quiero recibir alertas automáticas cuando los estados difieran entre almacén, transporte y portal de trazabilidad,  
para corregir desalineaciones antes de que lleguen al cliente.

**RNF-1.4 Resiliencia ante saturación del WMS**

Como arquitecto de solución,  
quiero circuit breakers y backpressure por cliente y prioridad SLA entre orquestador y WMS,  
para evitar colas descontroladas y fallos en cascada en campaña.

**RNF-1.5 Rendimiento de validación de órdenes**

Como cliente integrado por API,  
quiero recibir respuesta de validación y aceptación en menos de 2 segundos (p95),  
para integrar mi e-commerce sin fricción en picos de demanda.

**RNF-1.6 Throughput de recepción en campaña**

Como plataforma de recepción,  
quiero procesar hasta 500 órdenes por minuto en pico,  
para absorber Cyber Days sin rechazar pedidos válidos.

---

### Epica 2 — Transporte y optimización de rutas

*Planificación, manifiestos, restricciones operativas y corrección auditada de rutas.*

#### Requisitos Funcionales

**RF-2.1 Generación automática de rutas**

Como planner de transporte,  
quiero generar rutas con datos de tráfico y flota en tiempo real,  
para reducir el 17% de rutas que hoy se corrigen manualmente.

**RF-2.2 Manifiesto completo antes del despacho**

Como supervisor de despacho,  
quiero que el manifiesto incluya solo paquetes confirmados por el WMS,  
para evitar salir a ruta con entregas faltantes o inconsistentes.

**RF-2.3 Auditoría de cambios manuales de ruta**

Como gerente de transporte,  
quiero registrar motivo estructurado, aprobador y timestamp en toda modificación manual de ruta,  
para analizar desvíos y mejorar la planificación.

**RF-2.4 Restricciones operativas de flota**

Como TMS,  
quiero aplicar restricciones de vehículo, zona, capacidad y tipo de carga al asignar rutas,  
para cumplir reglas operativas y de seguridad.

#### Requisitos No Funcionales

**RNF-2.1 Tiempo de optimización de rutas**

Como planner,  
quiero obtener una ruta optimizada para un lote de hasta 2.700 vehículos en menos de 5 minutos,  
para reaccionar antes del inicio de la jornada o ante un evento crítico.

**RNF-2.2 Disponibilidad del TMS**

Como COO,  
quiero que el TMS tenga RTO menor a 15 minutos y forme parte del objetivo de 99,9% de disponibilidad en campaña,  
para no detener despachos en temporadas críticas.

---

### Epica 3 — Última milla y experiencia del destinatario

*App de conductores, evidencias de entrega, excepciones normalizadas y tracking en campo.*

#### Requisitos Funcionales

**RF-3.1 Operación offline resiliente**

Como conductor,  
quiero registrar entregas y excepciones sin conexión y sincronizar de forma segura al reconectar,  
para no perder evidencias aunque cambie de equipo o reinstale la aplicación.

**RF-3.2 Evidencias de entrega inviolables**

Como responsable de custodia,  
quiero que foto, firma, geolocalización y timestamp se cifren localmente y suban de forma atómica,  
para evitar disputas por entregas sin prueba (caso: 1.200 firmas perdidas).

**RF-3.3 Taxonomía obligatoria de excepciones**

Como analista de operaciones,  
quiero que el motivo principal de falla de entrega sea una categoría normalizada y obligatoria,  
para aprender de las excepciones y reducir el 34% de fallas prevenibles.

**RF-3.4 Publicación periódica de ubicación**

Como destinatario y cliente B2B,  
quiero ver la ubicación del reparto actualizada al menos cada 2 minutos,  
para planificar la recepción y reducir ausencias en ventana horaria.

**RF-3.5 Comunicación proactiva pre-entrega**

Como destinatario,  
quiero recibir confirmación de ventana horaria antes de que el camión salga a ruta,  
para reducir entregas fallidas por ausencia o dirección incorrecta.

#### Requisitos No Funcionales

**RNF-3.1 Latencia de eventos de tracking**

Como portal de trazabilidad,  
quiero publicar eventos de tracking con latencia end-to-end menor a 30 segundos,  
para ofrecer visibilidad casi en tiempo real.

**RNF-3.2 Seguridad de la app móvil**

Como CISO,  
quiero cifrado local, gestión de dispositivos (MDM) y autenticación segura en la app de conductores,  
para proteger datos personales y evidencias en campo.

**RNF-3.3 Disponibilidad de última milla**

Como gerente de operaciones,  
quiero que la app de conductores y el portal de tracking destinatarios contribuyan al objetivo de 99,9% en campaña,  
para no interrumpir la jornada de entrega.

---

### Epica 4 — Trazabilidad, eventos e integración

*Bus de eventos, modelo canónico, orden de mensajes y visibilidad operativa transversal.*

#### Requisitos Funcionales

**RF-4.1 Publicación de eventos del ciclo de vida**

Como arquitecto de integración,  
quiero que todos los eventos del ciclo de vida del pedido se publiquen en un bus central,  
para desacoplar sistemas y eliminar integraciones frágiles punto a punto.

**RF-4.2 Catálogo canónico de estados**

Como responsable de trazabilidad,  
quiero un catálogo único de estados (recibido, validado, reservado, pickeado, despachado, en ruta, entregado, fallido, devuelto, liquidado),  
para que todos los consumidores hablen el mismo lenguaje de negocio.

**RF-4.3 Reordenamiento de eventos fuera de secuencia**

Como consumidor de eventos,  
quiero detectar y reordenar mensajes llegados fuera de orden antes de actualizar el estado visible,  
para corregir escenarios offline y reconexiones móviles.

**RF-4.4 Propagación en tiempo real a consumidores**

Como cliente empresarial,  
quiero que el estado del pedido se propague en tiempo real a almacén, transporte y portal B2B de trazabilidad,  
para ver la misma información que usa la operación interna.

#### Requisitos No Funcionales

**RNF-4.1 Trazas distribuidas end-to-end**

Como equipo SRE,  
quiero trazas distribuidas por pedido desde recepción hasta entrega o liquidación,  
para diagnosticar incidentes en minutos y no en días.

**RNF-4.2 Dashboards operativos en tiempo real**

Como supervisor de operaciones,  
quiero tableros con cola de pedidos, rutas en curso, tracking y excepciones actualizados en vivo,  
para actuar antes de que un retraso se convierta en penalidad.

**RNF-4.3 Alertas ante degradación de servicios críticos**

Como responsable de disponibilidad,  
quiero alertas automáticas cuando WMS, TMS, app de conductores o portal de tracking se degraden,  
para activar runbooks antes de impacto masivo al cliente.

**RNF-4.4 Recuperación de datos operativos**

Como arquitecto de continuidad,  
quiero RPO menor a 5 minutos para datos de pedidos y tracking,  
para no perder trazabilidad ante una falla de infraestructura.

---

### Epica 5 — Liquidación, facturación y cumplimiento financiero

*Conciliación automatizada, reportes alineados a facturación y cálculo de penalidades.*

#### Requisitos Funcionales

**RF-5.1 Conciliación automatizada multifuente**

Como analista financiero,  
quiero conciliar automáticamente estados entre almacén, transporte, última milla y ERP,  
para reducir el tiempo de disputa de 23 días a menos de 1 día.

**RF-5.2 Reportes de trazabilidad alineados a facturación**

Como cliente empresarial,  
quiero reportes de trazabilidad generados en tiempo real con la misma fuente que la facturación,  
para evitar retenciones por diferencias de evidencia (caso USD 2,4M).

**RF-5.3 Cálculo automático de penalidades SLA**

Como área de finanzas,  
quiero calcular penalidades y bonificaciones por incumplimiento de SLA al cierre de cada ciclo de entrega,  
para eliminar hojas Excel y errores manuales en contratos especiales.

**RF-5.4 Detección de diferencias en cierre**

Como responsable de cuentas por cobrar,  
quiero alertas automáticas ante diferencias entre operación y facturación,  
para resolver observaciones antes del envío de factura al cliente.

#### Requisitos No Funcionales

**RNF-5.1 Integridad de datos de liquidación**

Como auditor externo,  
quiero que cada línea de liquidación sea trazable a eventos operativos con sello de tiempo e identificador de correlación,  
para sustentar conciliaciones y disputas comerciales.

---

### Epica 6 — Seguridad, privacidad y cumplimiento

*Autenticación, cifrado, enmascaramiento y auditoría de accesos — transversal a todas las épicas.*

#### Requisitos No Funcionales

**RNF-6.1 Autenticación y autorización de APIs**

Como administrador de seguridad,  
quiero OAuth 2.0 con scopes por cliente en todas las APIs expuestas,  
para controlar accesos B2B y reducir superficie de ataque.

**RNF-6.2 Cifrado de datos personales**

Como responsable de cumplimiento,  
quiero cifrado TLS 1.3 en tránsito y AES-256 en reposo para datos de destinatarios,  
para cumplir la Ley 29733 de Protección de Datos Personales.

**RNF-6.3 Enmascaramiento en ambientes no productivos**

Como equipo de QA,  
quiero datos personales enmascarados en desarrollo, prueba y capacitación,  
para evitar fugas de PII fuera de producción.

**RNF-6.4 Auditoría de accesos sensibles**

Como oficial de cumplimiento,  
quiero logs inmutables de acceso a firmas, fotos y datos personales,  
para investigar incidentes y responder a auditorías.

**RNF-6.5 Escalado automático en campaña**

Como plataforma cloud,  
quiero escalar automáticamente hasta 3× el volumen normal de carga,  
para mantener disponibilidad del 99,9% en Cyber Days sin intervención manual.

---

## 5. Trazabilidad por fase ADM

**¿Para qué sirve?** Indica **en qué fase del ADM de TOGAF** debe revisarse y validarse cada épica. No es un registro histórico: es la guía de **cuándo** el comité de arquitectura comprueba que los RF/RNF del §4 están cubiertos en los entregables de cada fase (visión → negocio → sistemas de información → tecnología → soluciones → migración).

| Fase ADM | Qué se valida con las épicas | Épicas prioritarias |
|---|---|---|
| **A — Architecture Vision** | Que los objetivos de negocio (doc `02`) justifiquen las épicas definidas | Todas (contexto) |
| **B — Business Architecture** | Procesos, roles y reglas de negocio alineados a RF de estados, excepciones y trazabilidad | Epica 1, 3, 4 |
| **C — Information Systems Architecture** | Que apps, datos e integraciones satisfagan los RF/RNF funcionales | Epicas 1–5 |
| **D — Technology Architecture** | Que infraestructura, disponibilidad, rendimiento y seguridad cumplan los RNF | Epicas 1, 2, 3, 4, 6 |
| **E — Opportunities & Solutions** | Que cada gap (doc `10`) cierre requisitos de alguna épica | Todas |
| **F — Migration Planning** | Que el roadmap (doc `11`) priorice épicas según valor y dependencias | Todas |

**Uso práctico:** al cerrar una fase ADM, el comité marca en Jira qué historias RF/RNF quedaron satisfechas en el entregable de esa fase antes de avanzar a la siguiente.

---

## 6. Gestión de cambios en requisitos

- Las **épicas** y sus RF/RNF se versionan en **Jira** (Epic → Story/Task).
- Todo cambio en fase C o D requiere análisis de impacto y aprobación del Comité de Arquitectura.
- Requisitos nuevos de fases E o F se incorporan a la épica correspondiente en Jira.
- Conflictos entre dominios se escalan al Comité de Arquitectura.

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
