## Hito 1 Documentos


-Analiza los documentos caso 6a y caso 6b que refieren al mismo caso
-Crea una carpeta para el desarrollo del hito 1 donde debe incluir documentos:

Business Model Canvas, Modelo Conceptual de Datos, Mapa Portafolio de Aplicaciones, Mapa de Infraestructura, Mapeo de Aplicaciones con Tecnología, ADM - Preliminary, ADM - A. Architecture Vision, ADM - Requirements Management, AS IS y TO BE con cadena de valor (ADM - B. Business Architecture, C. Information Systems Architecture y D. Technology Architecture), ADM - E. Opportunities and Solutions, ADM - F. Migration Planning

1.  ADM - Preliminary     
    Ejemplo:
    Modelo de Gobierno de Arquitectura:
    ● Comité de Arquitectura (Semanal) con
    asistencia del Gerente de Arquitectura,
    Arquitectos Empresariales, Arquitectos de
    Dominio y Jefe de Arquitectura de
    Solución con acta por escrito con
    acuerdos.
    ● Todas las iniciativas de la empresa se
    revisan en este comité. Se asigna a un
    Arquitecto Empresarial por cada iniciativa.
    ● Se usará Togaf (ADM) para la Arquitectura
    Empresarial.
    ● El Arquitecto Empresarial elaborará un
    documento en word (en base a plantilla)
    donde documentará todas las fases del
    ADM incluyendo la Situación Actual AS IS y
    la Situación Futura TO BE. Se almacenará
    en carpetas compartidas del Sharepoint
    de Arquitectura.
    ● Se usará draw.io para los diagramas de
    arquitectura (carpetas compartidas).

    Ejemplo:
    Principios o Lineamientos de Arquitectura:
    ● Principios de Arq. Negocio:
    ○ Digital-first
    ○ Experiencia centrada en cliente
    ○ Cumplimiento regulatorio
    prioritario
    ● Principios de Arq. Datos:
    ○ Single source of truth (Única
    fuente de verdad)
    ○ Estándar Arquitectura Medallion
    para Data lakehouse
    ● Principios de Arq. Aplicaciones:
    ○ Api-Fist: Integración vía APIs
    ○ Evitar soluciones punto a punto
    ○ Preferencia SaaS cuando sea
    viable
    ● Principios de Arq. Tecnológica:
    ○ Cloud-First (Nube pública): En vez
    de On-Premises
    ○ IaC: Infraestructura como código
    ○ Seguridad desde la fase de diseño
    (Security by design)

2. ADM - A. Architecture Vision

🏦 Ejemplo aplicado - Aseguradora
    Situación: La aseguradora tarda 48 horas en emitir pólizas.
    Drivers
    ● Competencia insurtech
    ● Mala experiencia digital
    Objetivo: Emitir pólizas en menos de 5 minutos.
    Alcance
    ● Productos vehiculares
    ● Canal digital
    KPI
    ● Tiempo emisión
    ● % emisión automática
    Aquí todavía no diseñamos aplicaciones ni tecnología.
    Solo alineamos dirección y justificamos el cambio.

3. ADM - Requirements Management

Gestión de Requisitos:
● Capturar requisitos. Pueden venir de:
○ Estrategia
○ Regulación
○ Stakeholders
○ Auditoría
○ Proyectos
○ Cambios externos
● Clasificar requisitos:
○ Funcionales
○ No Funcionales
● Trazabilidad de requisitos en todas las fases del ADM.

4. Arq. Neg. - Business Model Canvas

Business Model Canvas, es un marco visual que describe cómo un negocio crea, entrega y captura valoren una sola página, mediante 9 bloques:
1.
Propuesta de valor
2.
Segmentos de clientes
3.
Canales
4.
Relación con clientes
5.
Fuentes de ingreso
6.
Recursos clave
7.
Actividades clave
8.
Socios clave
9.
Estructura de costos

5. Arq. Dat. - Modelo Conceptual Datos

¿Cuáles son las entidadesprincipales y cómo se relacionan?

6. Arq. Apl. - Mapa Portafolio Aplicaciones
    Vista del inventario completo de aplicaciones clasificadas por CAPA ARQUITECTÓNICA:
    · Transversal (Seguridad, Observabilidad, IaC, Bus de Eventos)
    · Canales (portales, apps de campo)
    · Integración (API Gateway, mensajería, conectores)
    · Core (sistemas operacionales centrales)
    · Data (analítica, ML, eventos, IoT)
    · Soporte (back-office, operaciones internas)
    · CRM / Atención al Cliente
    · ERP / Finanzas
    Permite identificar redundancias, obsolescencia y riesgos por capa.
    IMPORTANTE: distinguir datos confirmados en el caso (✅) de suposiciones técnicas (⚠️).

7.Arq. Tec. - Mapa de Infraestructura


8.Arq. Tec. - Mapeo Aplicaciones Tecnología

9. Arq. Neg. - Cadenas Valor
Un Value Stream es la secuencia end-to-end de etapas que una organización ejecuta para entregar valor a un clienteo stakeholder, desde la necesidad inicial hasta el resultado final.
Es el modelo del “cómofluye el valor” a través del negocio.

10. ADM - Fase B, C y D (AS IS y TO BE) con cadena de valor

    ESTRUCTURA DEL DOCUMENTO:

    Value Stream (cadena de valor) al inicio: F1 Recepción → F2 Preparación → F3 Despacho → F4 Entrega → F5 Excepciones → F6 Liquidación

    Por cada fase del Value Stream, documentar AS IS y TO BE:

    AS IS (por fase):
      - Arq. Negocio:
          · Puntos de dolor
          · Roles
      - Arq. Datos:
          · Entidades de datos de la fase
      - Arq. Aplicaciones:
          · Aplicaciones involucradas en la fase
      - Arq. Tecnológica:
          · Infraestructura que soporta la fase

    TO BE (por fase):
      - Arq. Negocio:
          · Objetivos
          · Roles (cambios)
      - Arq. Datos:
          · Entidades de datos (cambios)
      - Arq. Aplicaciones — separado en tres secciones:
          · NUEVO: aplicaciones nuevas a crear
          · MODIFICAR: aplicaciones existentes a cambiar
          · ELIMINAR: aplicaciones a deprecar
      - Arq. Tecnológica:
          · Infraestructura (misma o nueva)

    Al final del documento:
      - GAPS / BRECHAS AS IS → TO BE
          · Por fase (Negocio, Datos, Aplicaciones, Tecnología)
          · Transversales (aplican a todas las fases)


11. ADM - E. Opportunities and Solutions
    Consolidar los gaps o brechas para ir del AS IS al TO BE (Negocio,
    Datos, Aplicaciones, Tecnología)
    ● Agrupar gaps en iniciativas o proyectos
    ● Identificar Arquitecturas de Transición
    A veces no puedes pasar directo del AS-IS a TO-BE. Necesitas
    estados intermedios. Ejemplo:
    AS-IS: Core Monolítico (On-Premises)
    Transición 1: APIs con BD centralizada sobre monolito
    (On-Premises)
    Transición 2: Microservicios cada uno con su BD desacoplados
    con contenedores docker y kubernetes (On-Premises)
    TO-BE: Migración a nube pública

12. ADM - F. Migration Planning

Para cada iniciativa o proyecto estimar el tiempo y costo en base
al alcance (Transiciones o TO BE).
● Priorizar iniciativas en base al valor que generan al negocio.
● Elaborar un roadmap o cronograma de implementación
considerando dependencias entre iniciativas.

---

## PPT Hito 1 — Notebook LM (RutaExpress)

**Cuándo usar:** presentación ejecutiva del Hito 1 ante comité de arquitectura o evaluación UTEC. El detalle técnico va en documentos y diagramas draw.io; la PPT es narrativa de alto nivel.

### Fuentes a cargar en Notebook LM

Subir como fuentes (prioridad):

1. `Caso 6a - Ruta Express_Logistica.md` y `Caso 6b - Ruta Express_Logistica - Anexo.md`
2. Carpeta `HITO 1 - Arquitectura Empresarial/` — los 11 documentos (`01` … `11`)
3. Opcional: capturas PNG de `HITO 1 - Arquitectura Empresarial/diagramas/infra-as-is.png` e `infra-to-be.png`

### Prompt para Notebook LM

```
Genera una presentación (15–18 diapositivas) para exponer el HITO 1 — Arquitectura Empresarial de RutaExpress Fulfillment & Transporte, usando SOLO la información de las fuentes cargadas.

AUDIENCIA: comité de arquitectura y docentes UTEC. Tono ejecutivo, claro, en español. Duración objetivo: 20–25 minutos.

REGLAS DE CONTENIDO:
- Nivel ALTO: mensajes clave, problemas de negocio, decisiones arquitectónicas y roadmap. NO listar las 26 APP ni tablas completas en las diapositivas.
- Usar nomenclatura oficial: nombre de aplicación + (APP-XX) o plataforma + (PLT-XX) la primera vez por diapositiva. Ejemplo: Azure API Management (APP-01), Bus de Eventos Central (PLT-03).
- Distinguir: Plataforma (dónde corre) vs Origen (Custom / COTS / SaaS externo) vs conectividad (ej. Wi-Fi interno del almacén — no es plataforma).
- Separar AS IS y TO BE de forma explícita. Resaltar brechas críticas: integración P2P sin PLT-03, WMS on premises (APP-06/APP-07), offline frágil App de Conductores (APP-15), liquidación en Excel (APP-26), identidad parcial PLT-02.
- Incluir 1–2 datos del caso por slide cuando refuerce el argumento (Cyber Days 6h WMS caído, 32.000 pedidos duplicados, 1.200 firmas perdidas, conciliación 23 días / USD 2.4M).
- NO inventar tecnologías, vendors ni cifras que no estén en las fuentes. Marcar suposiciones con ⚠️ si las mencionas.

ESTRUCTURA SUGERIDA DE DIAPOSITIVAS:

1. Portada — Hito 1 · RutaExpress · Arquitectura Empresarial TOGAF ADM
2. Contexto del caso — operador logístico multinube, 14 CD, 68k entregas/día, fragmentación tecnológica
3. Drivers y visión — doc 02: por qué transformar (objetivos estratégicos en 3–4 bullets)
4. Gobierno y principios — doc 01: comité, TOGAF, API-First, Cloud-First, event-driven
5. Cadena de valor — F1 Recepción → F2 Preparación → F3 Despacho → F4 Entrega → F5 Excepciones → F6 Liquidación (diagrama simple)
6. AS IS — síntesis del dolor transversal (multinube sin estrategia, datos inconsistentes, campañas frágiles)
7. [DIAGRAMA draw.io] Mapa portafolio AS IS por capas — placeholder; ver doc 06 §2
8. [DIAGRAMA draw.io] Infraestructura AS IS multinube — placeholder; ver doc 07 / infra-as-is
9. Portafolio en cifras — 26 APP, PLT-02 parcial, 3 brechas PLT, 3 candidatas a deprecar (🗑️ APP-04, APP-14, APP-26)
10. AS IS por fases (tabla resumen 6 filas) — una línea de dolor + apps protagonistas por F1–F6 (doc 09 guiones AS IS)
11. TO BE — visión objetivo: validación al ingreso, WMS Cloud, bus de eventos, tracking canónico, liquidación automática
12. [DIAGRAMA draw.io] Mapa portafolio / apps TO BE por capa — placeholder; doc 06 §4
13. [DIAGRAMA draw.io] Infraestructura TO BE — placeholder; doc 07 / infra-to-be (PLT-03, PLT-01, PLT-02 completo)
14. TO BE por fases — highlights NUEVO / MODIFICAR / ELIMINAR (1 bullet por fase, doc 09 guiones TO BE)
15. Gaps transversales — tabla compacta Negocio · Datos · Apps · Tecnología (doc 09 cierre)
16. Iniciativas y arquitecturas de transición — doc 10 (agrupación de gaps en proyectos)
17. Roadmap 36 meses — doc 11: fases, dependencias, inversión (solo hitos, no detalle de costos línea a línea)
18. Cierre — decisiones que el comité debe tomar + próximos pasos Hito 2

DIAPOSITIVAS CON DIAGRAMA (draw.io):
En las slides marcadas [DIAGRAMA draw.io], el contenido debe ser:
- Título de la vista arquitectónica
- 3 bullets de qué debe mostrar el diagrama
- Nota al pie: "Insertar diagrama desde draw.io — ver carpeta SharePoint / repo Proyecto"
NO generar el diagrama en la PPT; dejar espacio visual y texto guía.

Diagramas recomendados para draw.io (crear o exportar desde el repo):

| # | Diagrama | Fuente documento | Uso en PPT |
|---|----------|------------------|------------|
| D1 | Cadena de valor F1–F6 | 09 (inicio) | Slide 5 |
| D2 | Mapa portafolio AS IS por capas | 06 §2 | Slide 7 |
| D3 | Infraestructura AS IS (On Prem + Azure + AWS + GCP + SaaS) | 07, diagrams/infra-as-is | Slide 8 |
| D4 | Mapa portafolio TO BE por capas | 06 §4 | Slide 12 |
| D5 | Infraestructura TO BE con PLT-03 bus central | 07, diagrams/infra-to-be | Slide 13 |
| D6 | Modelo conceptual de datos (entidades core) | 05 | Opcional anexo |
| D7 | Business Model Canvas | 04 | Opcional slide contexto negocio |
| D8 | Arquitectura de transición (estados intermedios) | 10 | Slide 16 |
| D9 | Roadmap / Gantt iniciativas 36 meses | 11 | Slide 17 |

NOTAS DEL PRESENTADOR:
- Al final de cada slide AS IS/TO BE por fase, añadir nota breve basada en los "Guion de exposición" del doc 09 (Arquitectura de Aplicaciones).
- Slide 7: aclarar PLT-02 vs APP-01 (identidad parcial vs gateway — dos roles, misma app desplegada).
- Slide 10 F2: App Handhelds (APP-10) on premises; Wi-Fi interno = conectividad, no plataforma.

FORMATO DE SALIDA:
- Título de diapositiva
- 3–5 bullets máximo por slide
- Notas del presentador (2–4 frases)
- Indicar [INSERTAR DIAGRAMA D#] donde corresponda
```

### Checklist post-generación (PowerPoint / Google Slides)

- [ ] Reemplazar placeholders con diagramas exportados desde draw.io (PNG/SVG, letra legible)
- [ ] Revisar que IDs APP/PLT coincidan con `06_Mapa_Portafolio_Aplicaciones.md`
- [ ] No duplicar tablas del doc 09 en la PPT — en vivo se abre el markdown o draw.io si preguntan detalle
- [ ] Ensayo con guiones de doc 06 (mapa portafolio) y doc 09 (por fase)


## Hito 2 Documentos Requerimientos Y Diseño de Arquitectura de Solución

Tome como mínimo 3 iniciativas del "ADM - F. Migration Planning" y elabore los Requerimientos Funcionales / No Funcionales y sus criterios de aceptación

1. los requerimientoes  deben tener el siguiente formato
Enunciar requerimientos
Historias de Usuario (Scrum)
Ejemplos:
Estructura:
Como[rol]Quiero[funcionalidad]Para[beneficio]
Sector
Requerimiento Funcional
Requerimiento No Funcional
Seguros
Comocliente
Quieroemitir una póliza vehicular en línea
Paraobtener cobertura inmediata
ComoclienteQuieroque la emisión de la póliza sea menor a 5 minutosParatener cobertura inmediata
Banca
Comocliente
Quierotransferir dinero a otro banco
Parapagar mis obligaciones
Comocliente
Quieroque mis transferencias estén protegidas con autenticación multifactor
Paraevitar fraudes


2. Los Criterios deben tener el siguiente formato
 Enunciar CriteriosAceptación
Gherkin(BDD -Behavior-DrivenDevelopment)
Definen cuándo el requerimiento está bien implementado
Gherkin(BDD-Behavior-DrivenDevelopment)
Estructura:
Given(Dado)When(Cuando)Then(Entonces)
EJEMPLOS: 
-Escenarios Positivos
Scenario: Emisión exitosa de póliza vehicular
Givenque el cliente ingresa datos personales válidos
Andingresa datos válidos del vehículo
Andselecciona datos válidos de la póliza
Andacepta los términos y condiciones
Andacepta la política de tratamiento de datos
Andel riesgo de la solicitud es aceptable
Whenconfirma la emisión de la póliza
Thenel sistema debe calcular la prima
Anddebe generar el número de póliza
And debe registrar la póliza con estado "Emitida“
Anddeberegistrar los documentos de cobro
And debe mostrar el mensaje "Póliza emitida correctamente"
Anddebe enviar la póliza al correo del cliente

-Escenarios Negativos
Scenario: Rechazo por datos obligatorios incompletos
Givenque el cliente ingresa información incompleta
Andfalta al menos un campo obligatorio del cliente o del vehículo o de la póliza
Whenconfirma la emisión de la póliza
Thenel sistema no debe emitir la póliza
And debe mostrar los campos obligatorios faltantes
And debe mostrar el mensaje "Complete los campos obligatorios para continuar"



3. En base a los requerimientos y criterios de aceptación elabore dos alternativas de solución TO BE y para cada una presente un Diagrama de Arquitectura de Solución en C4 Model hasta nivel 3 (Contexto, Contenedores, Componentes) con íconos de AWS, Azure o GCP aplicando Lineamientos de Arquitectura (Ejemplo: Integración, Seguridad, Observabilidad, etc.) y Patrones de Arquitectura. Indique todas las Decisiones de diseño (Architectural Decision Records (ADR))tomadas. Presente un cuadro comparativo de ambas alternativas y sus recomendaciones.

NOTAS ADICIONALES: No se usarán servicios de tercero como telemetry ni datadog, ni algun otro serviico de tercero, siempre proioprizar los servicios de alguna de las 3 nubes aws, gcp o azure. Además, los servicios usados no deben ser muy caros, deben ser de nivel intermedio. recuerda que tampoco debes dar opciones para que yo elija tu debes elegir en base a todo el HITO1