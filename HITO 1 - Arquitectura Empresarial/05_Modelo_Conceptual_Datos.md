# Modelo Conceptual de Datos
## RutaExpress Fulfillment & Transporte

---

## 1. Propósito

Identificar las entidades principales de datos del negocio logístico de RutaExpress y las relaciones entre ellas. Este modelo es la base para definir la arquitectura de datos, el modelo canónico y la estrategia de Single Source of Truth.

---

## 2. Entidades Principales y Atributos Clave

### CLIENTE EMPRESARIAL
Empresa que contrata los servicios logísticos de RutaExpress.
- ID Cliente, Nombre, RUC, Sector, Canal de integración (API/Portal/CSV)
- SLA contractual, Tarifario, Reglas de penalidad
- Contacto técnico, Contacto comercial

### DESTINATARIO
Persona natural o empresa que recibe el pedido.
- ID Destinatario, Nombre, Teléfono, Email
- Dirección validada, Coordenadas GPS, Referencias
- Historial de entregas exitosas/fallidas

### ORDEN / PEDIDO
Solicitud de entrega de uno o más productos.
- ID Orden (interno), ID Externo cliente, Fecha/Hora recepción
- Estado (recibido/validado/reservado/pickeado/despachado/en ruta/entregado/fallido/devuelto/liquidado)
- Canal de entrada, Prioridad, SLA prometido, Ventana horaria
- Tipo de servicio (estándar/express/refrigerado/alto valor)

### LÍNEA DE PEDIDO
Detalle de cada producto dentro de una orden.
- ID Línea, ID Orden, SKU, Cantidad, Peso, Volumen
- Lote, Vencimiento (para farmacéuticos/alimentos)
- Requiere control de temperatura, Requiere custodia

### SKU (Producto)
Referencia de producto en el catálogo logístico.
- ID SKU, Código cliente, Descripción, Categoría
- Peso, Dimensiones, Temperatura requerida
- Es peligroso, Es refrigerado, Es alto valor

### CENTRO DE DISTRIBUCIÓN
Almacén desde donde se preparan y despachan pedidos.
- ID Centro, Nombre, Dirección, Capacidad total
- Zonas de almacenamiento, Temperatura (seco/frío)
- WMS asociado, Región de cobertura

### UBICACIÓN DE ALMACÉN
Posición física de un ítem dentro del centro de distribución.
- ID Ubicación, Centro, Pasillo, Nivel, Posición
- Tipo (picking/reserva/cuarentena), Capacidad

### INVENTARIO
Stock disponible de un SKU en una ubicación.
- ID Inventario, SKU, Ubicación, Centro
- Cantidad disponible, Cantidad reservada, Cantidad en tránsito
- Lote, Vencimiento, Fecha último movimiento

### MOVIMIENTO DE INVENTARIO
Registro de cada cambio en el inventario.
- ID Movimiento, Tipo (entrada/salida/ajuste/picking/devolución)
- SKU, Cantidad, Origen, Destino, Fecha/Hora
- Usuario, Motivo, ID Orden asociada

### OLA DE PICKING
Agrupación de líneas de pedido para ejecutar en el almacén.
- ID Ola, Centro, Fecha planificada, Estado
- Criterio de agrupación, Picker asignado
- Líneas incluidas, Tiempo estimado

### VEHÍCULO
Unidad de transporte propia o tercerizada.
- ID Vehículo, Placa, Tipo (furgón/camión/moto/refrigerado)
- Capacidad kg/m³, Propio o tercerizado
- Estado (disponible/en ruta/mantenimiento)
- Dispositivo GPS asociado

### CONDUCTOR
Persona que opera el vehículo en la ruta.
- ID Conductor, Nombre, DNI, Licencia
- Vehículo asignado, Zona de operación
- Dispositivo móvil, Estado (activo/inactivo)

### RUTA
Plan de entregas asignado a un vehículo y conductor.
- ID Ruta, Fecha, Centro de distribución origen
- Vehículo, Conductor, Estado (planificada/en curso/cerrada)
- Secuencia de paradas, Distancia estimada, Tiempo estimado
- Modificada manualmente (sí/no), Motivo de modificación

### PARADA / ENTREGA
Punto específico en la ruta donde se realiza una entrega.
- ID Parada, Ruta, Orden, Destinatario
- Secuencia, Dirección, Coordenadas
- Ventana horaria prometida, Estado
- Hora llegada real, Hora entrega real

### EVENTO DE TRACKING
Registro de cada cambio de estado en el ciclo de vida del pedido.
- ID Evento, ID Orden, Tipo de evento
- Timestamp, Fuente (app/TMS/WMS/portal)
- Latitud, Longitud, Usuario/Sistema
- Sincronizado (sí/no), En orden (sí/no)

### EVIDENCIA DE ENTREGA
Prueba digital de la entrega o intento.
- ID Evidencia, ID Parada, Tipo (foto/firma/código QR)
- URL almacenamiento (S3), Timestamp captura
- Hash de integridad, GPS captura, Sincronizado

### EXCEPCIÓN
Registro de una entrega fallida o incidencia.
- ID Excepción, ID Parada, Tipo normalizado
- Motivo (taxonomía controlada), Descripción adicional
- Requiere reintento, Requiere devolución
- Costo estimado del reintento

### INTENTO DE ENTREGA
Cada intento (exitoso o fallido) de entregar un pedido.
- ID Intento, Orden, Número de intento
- Fecha/Hora, Resultado (exitoso/fallido)
- Motivo de fallo, Conductor, Evidencias

### DEVOLUCIÓN
Pedido que regresa al centro de distribución.
- ID Devolución, Orden, Motivo
- Fecha inicio, Fecha llegada a almacén
- Estado (en tránsito/recibida/en proceso/finalizada)
- SKUs devueltos, Estado del producto

### LIQUIDACIÓN
Cierre económico de los servicios prestados a un cliente.
- ID Liquidación, Cliente, Período
- Total entregas exitosas, Total fallidas, Total devueltas
- Monto base, Penalidades aplicadas, Bonificaciones
- Estado (borrador/observada/aprobada/facturada)

### FACTURA
Documento de cobro por servicios logísticos.
- ID Factura, Liquidación, Cliente
- Fecha emisión, Monto total, Estado
- Referencia ERP, Observaciones cliente

### RECLAMO
Disputa del cliente sobre una liquidación o entrega.
- ID Reclamo, Cliente, Tipo (entrega/facturación/SLA)
- Monto en disputa, Estado, Fecha apertura
- Evidencias aportadas, Resolución

---

## 3. Diagrama de Relaciones (Notación Textual)

```
CLIENTE EMPRESARIAL
    ├── tiene muchos ──► ORDEN
    └── tiene muchos ──► LIQUIDACIÓN
                              └── genera ──► FACTURA

ORDEN
    ├── tiene muchas ──► LÍNEA DE PEDIDO
    │                         └── referencia ──► SKU
    ├── genera muchos ──► EVENTO DE TRACKING
    ├── tiene muchos ──► INTENTO DE ENTREGA
    │                         └── puede generar ──► EXCEPCIÓN
    │                         └── tiene muchas ──► EVIDENCIA DE ENTREGA
    ├── puede tener ──► DEVOLUCIÓN
    └── asignada a ──► PARADA (dentro de RUTA)

DESTINATARIO
    └── es destino de muchos ──► ORDEN

RUTA
    ├── asignada a ──► VEHÍCULO
    ├── asignada a ──► CONDUCTOR
    ├── parte de ──► CENTRO DE DISTRIBUCIÓN
    └── tiene muchas ──► PARADA

OLA DE PICKING
    ├── ejecutada en ──► CENTRO DE DISTRIBUCIÓN
    └── incluye muchas ──► LÍNEA DE PEDIDO

INVENTARIO
    ├── corresponde a ──► SKU
    ├── ubicado en ──► UBICACIÓN DE ALMACÉN
    │                         └── pertenece a ──► CENTRO DE DISTRIBUCIÓN
    └── cambia por ──► MOVIMIENTO DE INVENTARIO

LIQUIDACIÓN
    ├── pertenece a ──► CLIENTE EMPRESARIAL
    └── puede tener ──► RECLAMO
```

---

## 4. Dominios de Datos y Sistema Maestro (Single Source of Truth)

| Entidad | Sistema Maestro (AS IS) | Sistema Maestro (TO BE) |
|---|---|---|
| Orden / Pedido | Orquestador AKS (Azure) | Servicio de Gestión de Pedidos (Azure) |
| SKU / Producto | WMS Principal (On Premises) | Catálogo de Productos (API centralizada) |
| Inventario | WMS Principal (On Premises) | WMS Cloud + Event Store |
| Ruta | TMS (Azure) | TMS (Azure) |
| Evento de Tracking | DynamoDB (AWS) | Event Store unificado (AWS Kinesis) |
| Evidencia de Entrega | S3 (AWS) | S3 (AWS) - con hash de integridad |
| Excepción | App conductores + TMS | Servicio de Excepciones (normalizado) |
| Liquidación / Factura | ERP on premises | ERP on premises (integrado) |
| Cliente Empresarial | Portal B2B (Trazabilidad) | Portal B2B unificado + CRM |
| Destinatario | Distribuido (WMS+TMS+App) | Servicio de Destinatarios (centralizado) |

---

## 5. Modelo Canónico de Estados de Pedido

```
[RECIBIDO] → [VALIDADO] → [RESERVADO] → [PICKEADO] → [DESPACHADO] 
    → [EN RUTA] → [ENTREGADO]
                → [FALLIDO] → [REINTENTO] → [ENTREGADO]
                                          → [DEVUELTO]
                           → [DEVUELTO]
    → [LIQUIDADO]
```

Este modelo canónico debe ser adoptado por WMS, TMS, App de Conductores, Portales B2B (Carga CSV/Excel y Trazabilidad) y ERP. Las transiciones de estado solo pueden avanzar (no retroceder) salvo en el flujo de devolución.

---

## 6. Volúmenes de Datos Referencia

| Entidad | Volumen Diario (Normal) | Volumen Diario (Campaña) |
|---|---|---|
| Órdenes nuevas | 68,000 | 180,000 |
| Líneas de pedido | ~200,000 | ~540,000 |
| Movimientos de inventario | 210,000 | ~600,000 |
| Eventos de tracking | 44,000 | 130,000+ |
| Intentos de entrega | 68,000 | 180,000 |
| Excepciones | ~8,500 | ~22,500 |
| Rutas generadas | 2,700 | 4,100 |

---

*Documento elaborado en el marco del Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC*
*Fecha: Junio 2026*
