HITO 1:

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
Vista del inventario completo de aplicaciones
●
Clasificadas por dominio, capacidad o unidad de negocio
●
Permite identificar redundancias, obsolescencia y riesgos

7.Arq. Tec. - Mapa de Infraestructura


8.Arq. Tec. - Mapeo Aplicaciones Tecnología

9. Arq. Neg. - Cadenas Valor
Un Value Stream es la secuencia end-to-end de etapas que una organización ejecuta para entregar valor a un clienteo stakeholder, desde la necesidad inicial hasta el resultado final.
Es el modelo del “cómofluye el valor” a través del negocio.

10. ADM - Fase B, C y D (AS IS y TO BE) con cadena de valor

    Arq Negocio 
    Arq  datos
    Arq aplicaciones
    Arq Tecnologia


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