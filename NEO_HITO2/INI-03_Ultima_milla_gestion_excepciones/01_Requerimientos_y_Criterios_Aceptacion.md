# Requerimientos Funcionales / No Funcionales y Criterios de Aceptacion
## RutaExpress Fulfillment & Transporte - Hito 2

> **Fuente:** `requerimientos.md` y `criterios_aceptacion_gherkin.md`.
> **Iniciativa:** **INI-03** - Modernizacion de ultima milla y gestion de excepciones.
> **Convencion:** nombres oficiales de aplicaciones y plataformas del Hito 1 cuando aplican.
> **Nota de alcance:** este consolidado no incluye bloques Gherkin completos de historias de usuario. Los escenarios completos permanecen en `criterios_aceptacion_gherkin.md` y `historias_gherkin/`.

---

## 1. Proposito

Definir los requerimientos para fortalecer App de Conductores (APP-15) con operacion offline-first, almacenamiento local cifrado, sincronizacion store-and-forward y gestion estandarizada de excepciones entre TMS (Transportation Management) (APP-11), CRM de Atencion al Cliente (APP-20), Portal B2B (Trazabilidad) (APP-18) y Almacenamiento Evidencias (S3) (APP-16).

---

## 2. Alineamiento con casuistica y lineamientos

| Fuente | Elemento considerado | Implicancia para los requerimientos |
|---|---|---|
| Caso 6a - Fase 4 | App de conductores en AWS usa DynamoDB, envia ubicacion cada 2 minutos y almacena evidencias en S3 | Se requieren tracking periodico, persistencia offline y evidencia con integridad |
| Caso 6a - Fase 4 | 44,000 eventos de tracking diarios, mas de 130,000 en campana, 8% con retraso mayor a 20 minutos | Los RNF deben medir retraso de sincronizacion y observabilidad de eventos pendientes |
| Caso 6a - Fase 4 | Reinstalacion o cambio de equipo puede perder evidencias; 1,200 entregas quedaron sin firma | Se agregan controles de retencion, confirmacion backend y recuperacion operativa ante cambio de equipo |
| Caso 6a - Fase 5 | 12.5% entregas fallidas, 8,500 paquetes diarios, 34% por direccion o ausencia, reintentos de USD 1.20 a USD 2.80 | La taxonomia y automatizacion de reintentos/devoluciones deben reducir fallas prevenibles |
| Caso 6b - Riesgo 3 | Texto libre, categorias distintas y cambios manuales sin causa estructurada | Las excepciones deben ser canonicas y trazables entre app, TMS, CRM y portal |
| Enunciado Hito 2 | Requisitos y criterios de aceptacion para futuras alternativas de solucion multinube | El documento prepara criterios para diseno con integracion, seguridad, observabilidad y resiliencia |

---

## 3. Alcance funcional

- Operacion offline-first para conductores.
- Persistencia local cifrada de eventos, evidencias y excepciones.
- Sincronizacion automatica con confirmacion backend.
- Reintentos automaticos sin perdida de firma, foto, GPS ni timestamp.
- Taxonomia unica de excepciones para app, TMS, CRM y portal.
- Automatizacion de reintentos, devoluciones, reasignaciones y escalamiento.

---

## 4. Requerimientos funcionales y no funcionales

| ID | Tipo | Descripcion | Criterio de aceptacion |
| --- | --- | --- | --- |
| RF-01 | Funcional | App de Conductores (APP-15) debe permitir operar entregas asignadas sin conectividad movil. | El conductor puede visualizar ruta, paquetes, destinatario y registrar eventos offline. |
| RF-02 | Funcional | La app debe almacenar localmente y de forma cifrada eventos, firma, foto, GPS, timestamp y excepciones. | Los datos capturados offline permanecen disponibles tras cierre/reapertura de la app. |
| RF-03 | Funcional | La app debe sincronizar datos mediante patron store-and-forward. | Al recuperar conectividad, los eventos pendientes se envian automaticamente en orden logico o con secuencia controlada. |
| RF-04 | Funcional | El backend debe confirmar recepcion y persistencia de cada evento o evidencia. | La app no elimina datos locales hasta recibir confirmacion backend. |
| RF-05 | Funcional | La app debe reintentar automaticamente envios fallidos. | Un error temporal no obliga al conductor a recapturar evidencia ni genera perdida de informacion. |
| RF-06 | Funcional | El sistema debe aplicar una taxonomia unica de excepciones. | App, TMS, CRM y portal usan los mismos codigos y descripciones oficiales. |
| RF-07 | Funcional | El conductor debe seleccionar un motivo de excepcion obligatorio cuando una entrega no se completa. | No se puede cerrar una entrega fallida con texto libre sin clasificacion canonica. |
| RF-08 | Funcional | El sistema debe automatizar acciones segun tipo de excepcion. | Una excepcion de ausencia, direccion incorrecta o rechazo genera reintento, devolucion, reasignacion o escalamiento segun regla configurada. |
| RF-09 | Funcional | Portal B2B (Trazabilidad) (APP-18) y CRM de Atencion al Cliente (APP-20) deben visualizar el mismo estado y motivo de excepcion. | Cliente y agente ven estado consistente con el evento confirmado por backend. |
| RF-10 | Funcional | Almacenamiento Evidencias (S3) (APP-16) debe conservar evidencias con hash de integridad y referencia a la orden/entrega. | Toda evidencia puede verificarse contra su hash y correlation ID. |
| RF-11 | Funcional | La app debe preservar evidencias pendientes ante cierre de sesion, reinicio de equipo, reinstalacion controlada o cambio de dispositivo gestionado. | Ninguna evidencia confirmada localmente queda sin sincronizar o sin registro de recuperacion/remediacion. |
| RF-12 | Funcional | La app debe registrar y sincronizar eventos de ubicacion cada 2 minutos cuando exista conectividad, y encolar eventos cuando opere offline. | TMS y portal reciben eventos con secuencia, timestamp original y estado de sincronizacion. |
| RF-13 | Funcional | El sistema debe permitir acciones preventivas de excepcion por direccion o ausencia. | Cuando se detecta riesgo de direccion/ausencia, se genera tarea de contacto, ajuste de ventana o validacion antes del siguiente intento. |
| RNF-01 | No funcional | La app debe funcionar offline durante una jornada de ruta definida por operacion, con minimo 8 horas de captura. | Pruebas de campo validan captura y consulta sin conectividad durante la jornada objetivo. |
| RNF-02 | No funcional | El almacenamiento local debe estar cifrado. | Revision tecnica evidencia cifrado local y proteccion de datos sensibles. |
| RNF-03 | No funcional | Sincronizacion con garantia de no perdida funcional de datos. | Eventos y evidencias capturados offline se sincronizan o quedan pendientes con causa visible. |
| RNF-04 | No funcional | Tiempo de sincronizacion menor a 5 minutos para backlog normal al recuperar conectividad. | Pruebas de campo validan sincronizacion p95 menor a 5 minutos y reduccion de eventos con retraso mayor a 20 minutos. |
| RNF-05 | No funcional | Usabilidad para operacion en ruta. | El conductor puede registrar entrega o excepcion en menos de 5 pasos operativos. |
| RNF-06 | No funcional | Observabilidad de eventos offline y reintentos. | Operacion puede ver pendientes, fallidos, confirmados y DLQ por conductor/ruta. |
| RNF-07 | No funcional | Integridad de evidencias. | Toda firma/foto/GPS tiene hash, timestamp, usuario/dispositivo y correlation ID. |
| RNF-08 | No funcional | Compatibilidad con dispositivos definidos por la operacion. | La solucion funciona en las versiones Android/iOS y modelos homologados. |
| RNF-09 | No funcional | Capacidad para picos de tracking en campana. | El backend procesa mas de 130,000 eventos diarios de tracking sin perdida y con alertas por retraso. |

---

## 5. Historias de usuario

| ID | Sector | Como | Quiero | Para | RF asociado |
| --- | --- | --- | --- | --- | --- |
| HU-INI03-RF01 | Logistica | conductor | que App de Conductores (APP-15) permita operar entregas asignadas sin conectividad movil | continuar la ruta aun en zonas con mala senal | RF-01 |
| HU-INI03-RF02 | Logistica | responsable de seguridad movil | que la app almacene localmente y de forma cifrada eventos, firma, foto, GPS, timestamp y excepciones | proteger evidencias y datos personales | RF-02 |
| HU-INI03-RF03 | Logistica | operador de ultima milla | que la app sincronice datos mediante patron store-and-forward | enviar eventos pendientes en orden logico al recuperar conectividad | RF-03 |
| HU-INI03-RF04 | Logistica | conductor | que el backend confirme recepcion y persistencia de cada evento o evidencia | que la app elimine datos locales solo cuando sea seguro | RF-04 |
| HU-INI03-RF05 | Logistica | conductor | que la app reintente automaticamente envios fallidos | no recapturar evidencias ni perder informacion por errores temporales | RF-05 |
| HU-INI03-RF06 | Logistica | responsable de atencion y transporte | una taxonomia unica de excepciones | que app, TMS, CRM y portal usen los mismos codigos y descripciones | RF-06 |
| HU-INI03-RF07 | Logistica | supervisor de ruta | que el conductor seleccione un motivo obligatorio cuando una entrega no se completa | evitar texto libre no clasificable | RF-07 |
| HU-INI03-RF08 | Logistica | planner de ultima milla | automatizar acciones segun tipo de excepcion | generar reintentos, devoluciones, reasignaciones o escalamiento sin gestion manual innecesaria | RF-08 |
| HU-INI03-RF09 | Logistica | agente de atencion y cliente B2B | que Portal B2B (APP-18) y CRM (APP-20) visualicen el mismo estado y motivo de excepcion | evitar respuestas contradictorias | RF-09 |
| HU-INI03-RF10 | Logistica | responsable de liquidacion | que Almacenamiento Evidencias (S3) (APP-16) conserve evidencias con hash de integridad y referencia a orden/entrega | demostrar cumplimiento y resolver observaciones | RF-10 |
| HU-INI03-RF11 | Logistica | supervisor de conductores | preservar evidencias pendientes ante cierre de sesion, reinicio, reinstalacion controlada o cambio de dispositivo gestionado | evitar entregas sin firma o foto | RF-11 |
| HU-INI03-RF12 | Logistica | supervisor de transporte | que la app registre y sincronice ubicacion cada 2 minutos con timestamp original | mejorar tracking confiable y trazabilidad de ruta | RF-12 |
| HU-INI03-RF13 | Logistica | equipo de atencion preventiva | generar acciones preventivas por direccion o ausencia | reducir fallas antes del siguiente intento de entrega | RF-13 |

---

## 6. Matriz de escenarios de aceptacion sin Gherkin

| Codigo | Historia | Tipo | Escenario |
| --- | --- | --- | --- |
| ESC-INI03-RF01-P01 | HU-INI03-RF01 | positivo | Consultar ruta descargada sin conexion |
| ESC-INI03-RF01-N01 | HU-INI03-RF01 | negativo | Bloquear ruta no descargada |
| ESC-INI03-RF02-P01 | HU-INI03-RF02 | positivo | Preservar evidencia tras reinicio de app |
| ESC-INI03-RF02-N01 | HU-INI03-RF02 | negativo | Impedir acceso local sin sesion valida |
| ESC-INI03-RF03-P01 | HU-INI03-RF03 | positivo | Sincronizar eventos pendientes al recuperar red |
| ESC-INI03-RF03-N01 | HU-INI03-RF03 | negativo | Retener evento fuera de secuencia |
| ESC-INI03-RF04-P01 | HU-INI03-RF04 | positivo | Liberar evidencia tras confirmacion backend |
| ESC-INI03-RF04-N01 | HU-INI03-RF04 | negativo | Conservar evidencia sin ACK |
| ESC-INI03-RF05-P01 | HU-INI03-RF05 | positivo | Reintentar envio tras error temporal |
| ESC-INI03-RF05-N01 | HU-INI03-RF05 | negativo | Enviar a remediacion tras reintentos agotados |
| ESC-INI03-RF06-P01 | HU-INI03-RF06 | positivo | Registrar excepcion con codigo canonico |
| ESC-INI03-RF06-N01 | HU-INI03-RF06 | negativo | Rechazar codigo no vigente |
| ESC-INI03-RF07-P01 | HU-INI03-RF07 | positivo | Cerrar entrega fallida con motivo canonico |
| ESC-INI03-RF07-N01 | HU-INI03-RF07 | negativo | Bloquear cierre sin motivo |
| ESC-INI03-RF08-P01 | HU-INI03-RF08 | positivo | Crear reintento por destinatario ausente |
| ESC-INI03-RF08-N01 | HU-INI03-RF08 | negativo | Escalar excepcion sin regla automatica |
| ESC-INI03-RF09-P01 | HU-INI03-RF09 | positivo | Actualizar portal y CRM con la misma excepcion |
| ESC-INI03-RF09-N01 | HU-INI03-RF09 | negativo | No mostrar excepcion no confirmada |
| ESC-INI03-RF10-P01 | HU-INI03-RF10 | positivo | Guardar evidencia con hash valido |
| ESC-INI03-RF10-N01 | HU-INI03-RF10 | negativo | Bloquear evidencia corrupta |
| ESC-INI03-RF11-P01 | HU-INI03-RF11 | positivo | Bloquear cambio de dispositivo con pendientes |
| ESC-INI03-RF11-N01 | HU-INI03-RF11 | negativo | Registrar remediacion si evidencia no puede recuperarse |
| ESC-INI03-RF12-P01 | HU-INI03-RF12 | positivo | Enviar ubicacion periodica con conectividad |
| ESC-INI03-RF12-N01 | HU-INI03-RF12 | negativo | Encolar ubicaciones durante perdida de red |
| ESC-INI03-RF13-P01 | HU-INI03-RF13 | positivo | Crear tarea preventiva por direccion riesgosa |
| ESC-INI03-RF13-N01 | HU-INI03-RF13 | negativo | No crear accion preventiva sin evidencia de riesgo |

---

## 7. Trazabilidad

| Iniciativa | Historias | RF | RNF | Escenarios referenciados |
| --- | --- | --- | --- | --- |
| INI-03 | 13 | 13 | 9 | 26 |

---

*Documento consolidado para el Proyecto Integrador Final - Arquitectura de Soluciones Multinube - UTEC.*
*Fecha: Julio 2026.*
