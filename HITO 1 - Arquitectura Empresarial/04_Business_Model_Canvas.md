# Business Model Canvas
## RutaExpress Fulfillment & Transporte

> **Para el comité de arquitectura** — Contexto **de negocio** del canvas: propuesta de valor, segmentos, canales y costos. **Mensaje clave:** el ingreso depende de SLA y trazabilidad; los canales digitales (**APP-01**, **APP-03**, **APP-15**, **APP-18**, **APP-19**) y la plataforma multinube son recursos clave — la arquitectura debe protegerlos.

---

## 1. Propósito

Documentar el modelo de negocio de RutaExpress en formato Business Model Canvas, vinculando actividades logísticas con los sistemas del portafolio (**APP-01** … **APP-26**).

---

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                              BUSINESS MODEL CANVAS - RUTAEXPRESS                                         │
├─────────────────────┬──────────────────────┬──────────────────────┬──────────────────────────────────────┤
│   8. SOCIOS CLAVE   │  7. ACTIVIDADES CLAVE │  1. PROPUESTA DE VALOR│     3. CANALES                      │
│                     │                      │                      │                                      │
│ • Transportistas    │ • Recepción y         │ Operador logístico   │ • API de integración                 │
│   tercerizados      │   validación de       │ integral con         │   para marketplaces                  │
│   (1,400 unidades   │   órdenes de clientes │ cobertura nacional,  │ • Portal B2B (carga CSV/Excel)       │
│   en campaña)       │ • Gestión de almacén  │ velocidad de         │   para clientes                      │
│ • Proveedores cloud │   y picking           │ entrega, trazabilidad│   medianos                           │
│   (AWS, Azure, GCP) │ • Optimización de     │ en tiempo real y     │ • App móvil para                     │
│ • Proveedores WMS   │   rutas y transporte  │ capacidad de         │   conductores                        │
│   y TMS             │ • Gestión de última   │ absorber picos de    │ • Portal de tracking                 │
│ • Clientes de       │   milla y excepciones │ hasta 180,000        │   para destinatarios                 │
│   combustible       │ • Logística inversa   │ entregas/día.        │ • Integración EDI                    │
│ • Empresas de       │   y devoluciones      │                      │   y archivos CSV                     │
│   tecnología móvil  │ • Facturación y       │ • Almacenamiento y   │   (clientes legacy)                  │
│ • Proveedor de      │   liquidación         │   preparación de     │ • Centro de atención                 │
│   pasarela de pagos │ • Analítica y mejora  │   pedidos (fulfil.)  │   B2B y B2C                          │
│ • Reguladores y     │   continua de rutas   │ • Entrega última     │                                      │
│   municipalidades   │                       │   milla en ventanas  │                                      │
│                     ├──────────────────────┤   horarias precisas  ├──────────────────────────────────────┤
│                     │  6. RECURSOS CLAVE   │ • Entregas           │  4. RELACIÓN CON CLIENTES             │
│                     │                      │   refrigeradas y     │                                      │
│                     │ • 14 centros de       │   especializadas     │ • SLA contractuales con              │
│                     │   distribución        │ • Trazabilidad       │   penalidades y bonif.               │
│                     │ • 2,700 vehículos     │   confiable desde    │ • Portal B2B (trazabilidad)          │
│                     │   propios             │   origen hasta       │   en tiempo real                     │
│                     │ • 9,500 colaboradores │   destino            │ • Reportes automatizados             │
│                     │ • WMS, TMS, app de    │ • Logística inversa  │   para clientes grandes              │
│                     │   conductores         │   y gestión de       │ • Atención personalizada             │
│                     │ • Plataforma          │   devoluciones       │   para cuentas clave                 │
│                     │   multinube           │ • Penalidades y      │ • Comunicación proactiva             │
│                     │   (AWS+Azure+GCP)     │   bonificaciones     │   al destinatario final              │
│                     │ • Red de cobertura    │   por cumplimiento   │   (SMS, email, WhatsApp)             │
│                     │   urbana validada     │   de SLA             │ • Mesa B2B para                      │
│                     │ • Datos históricos    │                      │   integraciones técnicas             │
│                     │   de rutas y tráfico  │                      │                                      │
├─────────────────────┴──────────────────────┴──────────────────────┴──────────────────────────────────────┤
│                          2. SEGMENTOS DE CLIENTES                                                        │
│                                                                                                          │
│  • Marketplaces y e-commerce (alto volumen, integración API, SLA exigente)                              │
│  • Cadenas de retail y tiendas por departamento                                                          │
│  • Empresas farmacéuticas y de salud (cadena de frío, custodia, regulación)                             │
│  • Supermercados y consumo masivo (frecuencia alta, bajo margen)                                         │
│  • Marcas de venta directa (DTC) que externalizan su fulfillment                                         │
│  • Fabricantes con distribución nacional                                                                 │
├──────────────────────────────────────────────────┬───────────────────────────────────────────────────────┤
│              9. ESTRUCTURA DE COSTOS             │              5. FUENTES DE INGRESO                   │
│                                                  │                                                      │
│ • Flota propia (mantenimiento, combustible,       │ • Tarifa por almacenamiento (m² / pallet / día)     │
│   seguros, GPS)                                  │ • Tarifa por picking y packing por ítem/pedido       │
│ • Mano de obra (conductores, pickers,            │ • Tarifa por entrega (por zona, tipo, volumen)       │
│   supervisores, TI: ~9,500 personas)             │ • Recargo por entrega express y ventana horaria      │
│ • Infraestructura cloud (AWS, Azure, GCP)        │ • Tarifa por logística inversa / devolución          │
│ • Licencias WMS, TMS, CRM, portales SaaS         │ • Tarifa por entregas refrigeradas y especiales      │
│ • Transportistas tercerizados (campaña)          │ • Bonificaciones por cumplimiento de SLA             │
│ • Reintentos de entrega (USD 1.20-2.80/intento)  │ • Penalidades cobradas por SLA a transportistas      │
│ • Penalidades pagadas a clientes (USD 1.1M       │ • Servicios premium de visibilidad y analítica       │
│   solo en Cyber Days)                            │   para clientes grandes                              │
│ • Centros de distribución (alquiler, utilities)  │ • Contratos por volumen mínimo garantizado           │
│ • Tecnología móvil y dispositivos handhelds      │                                                      │
└──────────────────────────────────────────────────┴───────────────────────────────────────────────────────┘
```

---

## Análisis de los 9 Bloques

### 1. Propuesta de Valor
RutaExpress entrega a sus clientes la capacidad de tercerizar su operación logística completa con garantías de velocidad, cobertura, trazabilidad y manejo de excepciones. Su diferencial es la capacidad de absorber picos (3x volumen normal), la red de 14 centros de distribución, la cobertura en zonas urbanas complejas y los servicios especializados (frío, farmacéutico, alto valor). La propuesta se sostiene en la promesa de cumplimiento de SLA con evidencia digital.

### 2. Segmentos de Clientes
Clientes B2B de alto volumen que no quieren o no pueden construir su propia operación logística. El segmento principal son los marketplaces y el e-commerce, que representan el mayor volumen pero también las exigencias más altas de trazabilidad, integración API y penalidades.

### 3. Canales
Multicanal para integración: **APP-01** Azure API Management para grandes clientes, **APP-03** Portal B2B (Carga CSV/Excel) para medianos, **APP-04** Bucket S3 Legado (archivos) para legacy. **APP-15** App de Conductores es el canal de ejecución en campo. **APP-18** Portal B2B (Trazabilidad) y **APP-19** Portal Tracking Destinatarios son los canales de visibilidad para clientes empresariales y destinatarios finales, respectivamente.

### 4. Relación con Clientes
Relaciones contractuales de largo plazo con SLA y penalidades. La visibilidad en tiempo real y la comunicación proactiva son habilitadores de fidelización y diferenciación.

### 5. Fuentes de Ingreso
Modelo de tarificación por actividad logística. Los ingresos variables dependen del cumplimiento de SLA. Las penalidades pagadas a clientes son un costo que erosiona directamente el ingreso.

### 6. Recursos Clave
La red física (centros, flota, personal) combinada con la plataforma tecnológica multinube y los datos históricos de rutas y comportamiento de entregas son los recursos más valiosos y difíciles de replicar.

### 7. Actividades Clave
El ciclo completo: recepción → almacén → transporte → entrega → excepciones → liquidación. La optimización de rutas y la gestión de excepciones son las actividades con mayor impacto en el cumplimiento de SLA y en los costos.

### 8. Socios Clave
Los transportistas tercerizados son estratégicos en campaña. Los proveedores cloud son habilitadores de la plataforma tecnológica. La dependencia de múltiples proveedores cloud reduce el lock-in pero aumenta la complejidad de integración.

### 9. Estructura de Costos
Modelo intensivo en mano de obra y flota. Los reintentos de entrega y las penalidades son costos evitables que la arquitectura TO BE debe eliminar. La infraestructura cloud es un costo variable que debe optimizarse con auto-scaling.

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
