# MS-INI02-01 - Gobierno de APIs y Contratos

## Identificacion

- Iniciativa: INI-02 Integracion API-First y Event-Driven.
- Componente TO BE: capacidad de gobierno sobre Azure API Management o gateway equivalente de la alternativa cloud.
- Fuentes: `01_Requerimientos_y_Criterios_Aceptacion.md` e historias `HU-INI02-RF01`, `HU-INI02-RF02`, `HU-INI02-RF10` y `HU-INI02-RF12`.
- Alcance: contratos API/eventos, seguridad, cuotas, rate limiting, tableros de salud y convivencia transicional con integraciones punto a punto.

## Responsabilidades

- Registrar y publicar contratos API y eventos canonicos.
- Aplicar seguridad, cuotas, rate limiting y politicas por consumidor.
- Versionar contratos y evitar cambios incompatibles sin version nueva.
- Exponer estado operativo de APIs, errores y latencias.
- Encapsular adaptadores transicionales para CSV, S3, SaaS o canales legados.

## Modelo de datos

```sql
CREATE TABLE api_contract (
  contract_id UUID PRIMARY KEY,
  api_name VARCHAR(80) NOT NULL,
  version VARCHAR(20) NOT NULL,
  owner_domain VARCHAR(60) NOT NULL,
  openapi_uri VARCHAR(300) NOT NULL,
  lifecycle_status VARCHAR(30) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL
);

CREATE TABLE event_contract (
  event_contract_id UUID PRIMARY KEY,
  event_type VARCHAR(100) NOT NULL,
  schema_version VARCHAR(20) NOT NULL,
  producer VARCHAR(80) NOT NULL,
  schema_uri VARCHAR(300) NOT NULL,
  compatibility_mode VARCHAR(30) NOT NULL,
  lifecycle_status VARCHAR(30) NOT NULL,
  created_at TIMESTAMP NOT NULL
);

CREATE TABLE consumer_policy (
  consumer_id VARCHAR(80) NOT NULL,
  contract_id UUID NOT NULL REFERENCES api_contract(contract_id),
  plan_name VARCHAR(40) NOT NULL,
  requests_per_minute INTEGER NOT NULL,
  burst_limit INTEGER NOT NULL,
  auth_scope VARCHAR(120) NOT NULL,
  PRIMARY KEY (consumer_id, contract_id)
);

CREATE TABLE integration_adapter (
  adapter_id UUID PRIMARY KEY,
  source_system VARCHAR(80) NOT NULL,
  target_contract VARCHAR(120) NOT NULL,
  adapter_type VARCHAR(30) NOT NULL,
  status VARCHAR(30) NOT NULL,
  retirement_target_date DATE
);
```

## Funcionalidades

| Codigo | Funcionalidad | Contrato entrada | Contrato salida | Trazabilidad | Lineamientos |
|---|---|---|---|---|---|
| F-API-01 | Registrar contratos API y eventos | Definicion OpenAPI/AsyncAPI, owner, version, productor/consumidor | Contrato publicado, version activa y reglas de compatibilidad | `HU-INI02-RF01`, `ESC-INI02-RF01-P01`, `ESC-INI02-RF01-N01` | ARQ-05, INT-01, INT-03, INT-04 |
| F-API-02 | Aplicar seguridad, cuotas y rate limiting | Token OAuth/OIDC, consumidor, contrato y plan | Solicitud permitida o rechazada con codigo gobernado | `HU-INI02-RF02`, `ESC-INI02-RF02-P01`, `ESC-INI02-RF02-N01` | SEG-03, SEG-04, SEG-08, ESC-05 |
| F-API-03 | Publicar salud y convivencia transicional | Metricas de gateway, adaptador, latencia y errores | Tablero de salud, alertas y plan de retiro de punto a punto | `HU-INI02-RF10`, `HU-INI02-RF12` | INT-11, OBS-04, OBS-08, ARQ-09 |

## Algoritmos

### F-API-01 - Registro de contrato

```text
recibir definicion de contrato
validar owner, version, errores funcionales y correlationId
comparar contra version activa
si rompe compatibilidad:
  exigir version nueva y marcar contrato anterior como vigente
publicar contrato en catalogo
emitir ContractPublished al Bus de Eventos Central (PLT-03)
```

### F-API-02 - Politicas de consumo

```text
validar token federado y scopes
resolver consumidor y plan contratado
aplicar cuota por minuto y burst limit
si excede cuota:
  responder 429 con retry-after
  emitir metrica y alerta si supera umbral
enrutar hacia API de dominio con correlationId propagado
```

### F-API-03 - Salud y adaptadores

```text
capturar latencia, errores, volumen y saturacion por API/adaptador
agrupar metricas por dominio, consumidor y criticidad
si integracion legada falla:
  registrar evidencia de intercambio y cola de remediacion
si adaptador tiene reemplazo API/evento:
  actualizar plan de retiro y trazabilidad de migracion
```

## Consideraciones de calidad

- MVP: contratos OpenAPI/AsyncAPI mockeables y politicas basicas de cuota por cliente.
- Seguridad: WAF, OAuth/OIDC, scopes, validacion de payload y secreto en gestor central.
- Observabilidad: errores 4xx/5xx, latencia p95/p99, consumo por cliente, adaptadores legados y correlacion.
- Escalabilidad: cache de autorizacion, limites por cliente y proteccion de dominios internos.
