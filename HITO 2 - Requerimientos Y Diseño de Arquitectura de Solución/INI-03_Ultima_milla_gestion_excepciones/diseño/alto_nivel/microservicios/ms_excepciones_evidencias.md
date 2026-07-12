# MS-INI03-02 - Excepciones, Evidencias y Acciones

## Identificacion

- Iniciativa: INI-03 Modernizacion de ultima milla y gestion de excepciones.
- Componente TO BE: servicio de dominio para excepciones y evidencias integrado con TMS (APP-11), App de Conductores (APP-15), Almacenamiento Evidencias (S3) (APP-16), CRM y Portal B2B.
- Fuentes: `01_Requerimientos_y_Criterios_Aceptacion.md` e historias `HU-INI03-RF06` a `HU-INI03-RF10` y `HU-INI03-RF13`.
- Alcance: taxonomia unica, motivos obligatorios, automatizacion de acciones, estado consistente en portal/CRM, hash de evidencias y acciones preventivas.

## Responsabilidades

- Administrar taxonomia unica de excepciones para app, TMS, CRM y portal.
- Exigir motivo obligatorio y evidencia cuando una entrega falla.
- Automatizar reintentos, devoluciones, reasignaciones y escalamiento.
- Publicar estados consistentes hacia portal y CRM.
- Validar hash e integridad de evidencias almacenadas en S3.
- Ejecutar acciones preventivas cuando exista riesgo de excepcion por direccion, ausencia, clima, trafico o SLA.

## Modelo de datos

```sql
CREATE TABLE exception_taxonomy (
  exception_code VARCHAR(40) PRIMARY KEY,
  description VARCHAR(200) NOT NULL,
  category VARCHAR(60) NOT NULL,
  requires_evidence BOOLEAN NOT NULL,
  default_action VARCHAR(60) NOT NULL,
  severity VARCHAR(20) NOT NULL,
  active BOOLEAN NOT NULL
);

CREATE TABLE exception_case (
  exception_case_id UUID PRIMARY KEY,
  delivery_id VARCHAR(100) NOT NULL,
  route_id VARCHAR(80) NOT NULL,
  exception_code VARCHAR(40) NOT NULL REFERENCES exception_taxonomy(exception_code),
  reason_detail VARCHAR(500) NOT NULL,
  status VARCHAR(30) NOT NULL,
  assigned_team VARCHAR(80),
  correlation_id VARCHAR(100) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  resolved_at TIMESTAMP NULL
);

CREATE TABLE exception_action (
  action_id UUID PRIMARY KEY,
  exception_case_id UUID NOT NULL REFERENCES exception_case(exception_case_id),
  action_type VARCHAR(60) NOT NULL,
  action_status VARCHAR(30) NOT NULL,
  scheduled_at TIMESTAMP,
  executed_at TIMESTAMP,
  result_detail VARCHAR(500)
);

CREATE TABLE evidence_manifest (
  evidence_id UUID PRIMARY KEY,
  delivery_id VARCHAR(100) NOT NULL,
  storage_uri VARCHAR(300) NOT NULL,
  evidence_type VARCHAR(40) NOT NULL,
  sha256_hash CHAR(64) NOT NULL,
  capture_timestamp TIMESTAMP NOT NULL,
  upload_status VARCHAR(30) NOT NULL,
  correlation_id VARCHAR(100) NOT NULL
);

CREATE TABLE risk_signal (
  risk_signal_id UUID PRIMARY KEY,
  delivery_id VARCHAR(100) NOT NULL,
  risk_type VARCHAR(60) NOT NULL,
  risk_score NUMERIC(5,2) NOT NULL,
  recommended_action VARCHAR(80) NOT NULL,
  created_at TIMESTAMP NOT NULL
);
```

## Funcionalidades

| Codigo | Funcionalidad | Contrato entrada | Contrato salida | Trazabilidad | Lineamientos |
|---|---|---|---|---|---|
| F-EXC-01 | Taxonomia y motivo obligatorio | Entrega fallida, codigo de excepcion, motivo, evidencia y correlationId | Excepcion aceptada, rechazada o pendiente de evidencia | `HU-INI03-RF06`, `HU-INI03-RF07`, `ESC-INI03-RF07-N01` | ARQ-03, INT-03, SEG-07 |
| F-EXC-02 | Automatizar acciones | Caso de excepcion, reglas por SLA, zona, cliente y severidad | Reintento, devolucion, reasignacion o escalamiento | `HU-INI03-RF08`, `HU-INI03-RF13`, `ESC-INI03-RF08-P01` | ARQ-01, ESC-09, OBS-08 |
| F-EXC-03 | Evidencias y estado consistente | Evidencia, hash, estado de entrega y evento de portal/CRM | Manifest validado, estado publicado y alerta si hay inconsistencia | `HU-INI03-RF09`, `HU-INI03-RF10`, `ESC-INI03-RF10-N01` | SEG-10, INT-10, OBS-07 |

## Algoritmos

### F-EXC-01 - Registro de excepcion

```text
recibir evento DeliveryFailed o comando desde app
validar exception_code contra taxonomia activa
si motivo obligatorio falta:
  rechazar evento funcional y no cambiar estado de entrega
si requiere evidencia y no existe manifest:
  dejar caso pendiente de evidencia
crear exception_case y publicar LastMileExceptionRaised
```

### F-EXC-02 - Accion automatizada

```text
clasificar excepcion por categoria, severidad, SLA y cliente
consultar reglas de accion y riesgo preventivo
si direccion incorrecta:
  escalar a CRM y solicitar confirmacion
si ausencia destinatario:
  programar reintento o ventana alternativa
si cadena de frio o seguridad esta comprometida:
  escalar inmediatamente a supervisor
publicar accion hacia TMS y portal
```

### F-EXC-03 - Integridad de evidencia

```text
recibir evidencia desde app o backend movil
calcular sha256 y comparar con manifest enviado
si hash no coincide:
  marcar evidencia corrupta y crear excepcion tecnica
si hash coincide:
  registrar storage_uri, tipo y timestamp de captura
publicar EvidenceAccepted y actualizar portal/CRM
```

## Consideraciones de calidad

- Resiliencia: eventos idempotentes, DLQ para evidencias corruptas y reintentos de publicacion.
- Seguridad: hash de integridad, control de acceso a S3, retencion y auditoria.
- Observabilidad: entregas fallidas, causas, evidencias pendientes, acciones vencidas y SLA comprometido.
- Escalabilidad: reglas evaluadas de forma asincrona y prioridad por SLA/cliente.
