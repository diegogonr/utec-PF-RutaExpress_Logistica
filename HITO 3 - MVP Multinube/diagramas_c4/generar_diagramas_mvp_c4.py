#!/usr/bin/env python3
"""
Genera diagramas C4 del MVP Hito 3 con la librería diagrams (mingrammer).
Requiere: pip install diagrams graphviz + Graphviz instalado en el SO.

Convencion de etiquetas en cada caja (3 lineas):
  1. Nombre del servicio cloud (proveedor)
  2. Nombre oficial (aplicacion / microservicio / plataforma)
  3. Identificador (APP-XX, MS-INIxx-yy, PLT-XX) o rol si es infraestructura pura

Salida: diagramas_c4/imagenes/*.png

Uso:
  python generar_diagramas_mvp_c4.py
  python generar_diagramas_mvp_c4.py --only n3-oms
"""

from __future__ import annotations

import argparse
from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import ECS
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import Eventbridge, SQS
from diagrams.aws.management import Cloudwatch
from diagrams.aws.network import ALB
from diagrams.aws.security import KMS
from diagrams.aws.storage import S3
from diagrams.azure.analytics import EventHubs, LogAnalyticsWorkspaces
from diagrams.azure.compute import AKS, FunctionApps
from diagrams.azure.database import CacheForRedis, SQLManagedInstances
from diagrams.azure.security import KeyVaults
from diagrams.azure.integration import APIManagement, ServiceBus
from diagrams.azure.storage import StorageAccounts
from diagrams.gcp.analytics import BigQuery
from diagrams.gcp.compute import Run
from diagrams.gcp.operations import Logging
from diagrams.generic.blank import Blank as BlankNode
from diagrams.generic.database import SQL
from diagrams.generic.device import Mobile
from diagrams.onprem.client import Client, User, Users
from diagrams.onprem.container import Docker
from diagrams.saas import Saas

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "imagenes"

GRAPH_ATTR = {
    "fontsize": "16",
    "fontname": "Segoe UI",
    "bgcolor": "white",
    "pad": "0.6",
    "nodesep": "1.0",
    "ranksep": "1.3",
    "dpi": "200",
    "compound": "true",
    "splines": "spline",
    "overlap": "false",
    "newrank": "true",
}

# N3: flechas rectas/ortogonales y menos espacio muerto entre cajas.
N3_GRAPH_ATTR = {
    **GRAPH_ATTR,
    "splines": "ortho",
    "nodesep": "0.40",
    "ranksep": "0.55",
    "pad": "0.35",
}

NODE_ATTR = {"fontsize": "10", "fontname": "Segoe UI"}

EDGE_ATTR = {
    "fontsize": "7",
    "fontname": "Segoe UI",
}


def el(text: str = "", **attrs) -> Edge:
    """Etiqueta mínima junto a la flecha. Sin texto cuando la relación es obvia."""
    if text:
        attrs = {"label": text, **attrs}
    return Edge(**attrs)


def lbl(servicio: str, nombre: str, identificador: str) -> str:
    """Etiqueta estandar: servicio cloud + nombre oficial + ID o rol."""
    return f"{servicio}\n{nombre}\n{identificador}"


def wrap_text(text: str, width: int = 22) -> str:
    """Parte una frase en varias líneas para que quepa en la caja azul."""
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join(current + [word])
        if len(candidate) <= width:
            current.append(word)
            continue
        if current:
            lines.append(" ".join(current))
        current = [word]
    if current:
        lines.append(" ".join(current))
    return "\n".join(lines) if lines else text


def n3_lbl(nombre: str, responsabilidad: str) -> str:
    """Etiqueta de componente N3 con salto de línea en nombre y responsabilidad."""
    return (
        f"Componente N3\n"
        f"{wrap_text(nombre, 20)}\n"
        f"{wrap_text(responsabilidad, 20)}"
    )


def Blank(label: str) -> BlankNode:
    """Caja C4 para un componente lógico; no representa un pod ni un servicio cloud."""
    return BlankNode(
        label,
        shape="box",
        style="rounded,filled",
        fillcolor="#FFFFFF",
        color="#0B5EA8",
        fontcolor="#0A2540",
        fontsize="11",
        width="2.55",
        height="1.45",
        fixedsize="true",
        margin="0.12,0.10",
        labelloc="c",
        penwidth="2.0",
        image="",
    )


def _ensure_out() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def n1_contexto() -> None:
    _ensure_out()
    with Diagram(
        "C4 N1 - Contexto MVP RutaExpress",
        filename=str(OUT_DIR / "mvp_c4_n1_contexto_v4"),
        show=False,
        direction="TB",
        graph_attr={**GRAPH_ATTR, "splines": "ortho"},
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        cliente = User(lbl("Actor externo", "Cliente B2B", "Persona"))
        conductor = User(lbl("Actor externo", "Conductor", "Persona"))
        ops = Users(lbl("Actor externo", "Operaciones / Soporte", "Persona"))

        with Cluster("Sistema en alcance"):
            mvp = Saas(
                lbl(
                    "Plataforma multinube",
                    "Plataforma Logistica MVP",
                    "Azure hub + AWS + GCP",
                )
            )

        wms = Saas(
            lbl(
                "mock legado (APIM)",
                "WMS Principal (On Premises)",
                "APP-06 / APP-07",
            )
        )
        erp = Saas(
            lbl(
                "mock legado (APIM)",
                "ERP Financiero (On Premises)",
                "APP-25",
            )
        )
        portal = Saas(
            lbl(
                "mock-portal (APIM)",
                "Portal B2B (Trazabilidad)",
                "APP-18 / APP-20",
            )
        )
        tms = Saas(
            lbl(
                "mock TMS (APIM)",
                "TMS (Transportation Management)",
                "APP-11",
            )
        )

        cliente >> el("orden y tracking") >> mvp
        conductor >> el("entrega y evidencias") >> mvp
        ops >> el("operación") >> mvp
        mvp >> el("confirmar reserva") >> wms
        mvp >> el("valorización") >> erp
        mvp >> el("lectura CQRS") >> portal
        mvp >> el("AMQP · despacho") >> tms


def n2_contenedores() -> None:
    _ensure_out()
    with Diagram(
        "C4 N2 - Contenedores MVP Hub central Azure",
        filename=str(OUT_DIR / "mvp_c4_n2_contenedores_v20"),
        show=False,
        direction="LR",
        graph_attr={
            **GRAPH_ATTR,
            "splines": "ortho",
            "nodesep": "0.8",
            "ranksep": "1.1",
        },
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        cliente = User(lbl("Actor externo", "Cliente B2B", "Persona"))
        conductor = User(lbl("Actor externo", "Conductor", "Persona"))
        ops = Users(lbl("Actor externo", "Operaciones / Soporte", "Persona"))
        frontend = Client(
            lbl("Navegador", "Frontend Web del MVP", "aplicación de página única")
        )

        with Cluster("Azure - Hub operativo"):
            apim = APIManagement(
                lbl(
                    "Azure API Management",
                    "Azure API Management",
                    "APP-01",
                )
            )
            with Cluster("Cluster AKS compartido"):
                aks = AKS(
                    lbl(
                        "Azure Kubernetes Service",
                        "Plataforma de ejecución",
                        "cluster AKS compartido",
                    )
                )
                bff = Docker(
                    lbl(
                        "Kubernetes Deployment",
                        "BFF del MVP",
                        "adapta frontend y APIs",
                    )
                )
                oms = Docker(
                    lbl(
                        "Kubernetes Deployment",
                        "OMS — APP-02",
                        "Saga · Inventario HTTP · WMS vía APIM",
                    )
                )
                inv = Docker(
                    lbl(
                        "Kubernetes Deployment",
                        "Inventario — MS-INI01-02",
                        "reservas y liberaciones",
                    )
                )
                bus_workers = Docker(
                    lbl(
                        "Kubernetes Deployment",
                        "bus-workers — PLT-03",
                        "consulta outbox SQL → Event Hubs",
                    )
                )
            sql = SQLManagedInstances(
                lbl(
                    "Azure SQL",
                    "Órdenes, inventario y outbox",
                    "OMS/Inv escriben · bus-workers lee",
                )
            )
            eh = EventHubs(
                lbl(
                    "Event Hubs",
                    "Bus de Eventos Central",
                    "PLT-03",
                )
            )
            sb = ServiceBus(
                lbl(
                    "Service Bus",
                    "q-inventory + DLQ (demo E5)",
                    "PLT-03 · parcial",
                )
            )
            redis = CacheForRedis(
                lbl(
                    "Azure Cache for Redis",
                    "Cache operativa OMS",
                    "APP-02",
                )
            )
            kv = KeyVaults(
                lbl(
                    "Key Vault",
                    "Plataforma Identidad y Accesos",
                    "PLT-02",
                )
            )
            aws_azure_adapter = FunctionApps(
                lbl(
                    "Azure Function",
                    "Adaptador AWS→Azure",
                    "normaliza y publica en Event Hubs · OBJETIVO",
                )
            )
            mon = LogAnalyticsWorkspaces(
                lbl(
                    "Azure Monitor",
                    "Observabilidad Azure",
                    "PLT-01",
                )
            )

        with Cluster("AWS - Ultima milla"):
            alb = ALB(
                lbl(
                    "Application Load Balancer",
                    "Entrada Backend móvil",
                    "APP-15",
                )
            )
            mob = ECS(
                lbl(
                    "ECS Fargate",
                    "Backend móvil — APP-15",
                    "código mobile-api",
                )
            )
            retry_worker = Docker(
                lbl(
                    "Contenedor en tarea ECS Fargate",
                    "retry-worker",
                    "puente SQS → EventBridge · OBJETIVO",
                )
            )
            ddb = Dynamodb(
                lbl(
                    "DynamoDB",
                    "Outbox backend + Ack Tracker",
                    "backend APP-15",
                )
            )
            s3 = S3(
                lbl(
                    "Amazon S3",
                    "Almacenamiento Evidencias",
                    "APP-16",
                )
            )
            sqs = SQS(
                lbl(
                    "Amazon SQS",
                    "Buffer puente movil",
                    "hacia PLT-03",
                )
            )
            eb = Eventbridge(
                lbl(
                    "EventBridge",
                    "Publicador puente AWS",
                    "hacia PLT-03",
                )
            )
            cw = Cloudwatch(
                lbl(
                    "CloudWatch",
                    "Observabilidad AWS",
                    "PLT-01",
                )
            )

        with Cluster("GCP - Analitica CQRS"):
            run = Run(
                lbl(
                    "Cloud Run",
                    "Proyector CQRS",
                    "lectura tracking",
                )
            )
            tracking_api = Run(
                lbl(
                    "Cloud Run",
                    "Tracking Query API",
                    "consulta cliente — objetivo",
                )
            )
            bq = BigQuery(
                lbl(
                    "BigQuery",
                    "Almacen consultas CQRS",
                    "mock-portal APP-18",
                )
            )
            glog = Logging(
                lbl(
                    "Cloud Logging",
                    "Observabilidad GCP",
                    "PLT-01",
                )
            )

        with Cluster("Legados simulados (SaaS externo)"):
            mock_wms = Saas(
                lbl(
                    "APIM mock-wms",
                    "WMS Principal (On Premises)",
                    "APP-06",
                )
            )
            mock_erp = Saas(
                lbl(
                    "Ruta APIM mock-erp",
                    "ERP Financiero (On Premises)",
                    "APP-25",
                )
            )
            mock_portal = Saas(
                lbl(
                    "Ruta APIM mock-portal",
                    "Portal B2B (Trazabilidad)",
                    "APP-18",
                )
            )
            mock_tms = Saas(
                lbl(
                    "Consumidor mock-tms",
                    "TMS (Transportation Mgmt)",
                    "APP-11",
                )
            )

        cliente >> el() >> frontend
        conductor >> el() >> frontend
        ops >> el() >> frontend
        frontend >> el("HTTPS") >> bff
        bff >> el() >> apim
        bff >> el() >> sb
        apim >> el("orden") >> oms
        oms >> el() >> sql
        inv >> el() >> sql
        oms >> el() >> redis
        oms >> el() >> inv
        bus_workers >> el() >> sql
        bus_workers >> el("AMQP") >> eh
        sb >> el(style="dashed") >> inv
        sb >> el(style="dashed") >> mock_tms
        # WMS vía APIM: sin etiqueta flotante; el mock ya dice APIM mock-wms
        oms >> el() >> apim
        apim >> el() >> mock_wms
        apim >> el() >> mock_erp
        apim >> el() >> mock_portal
        apim >> el(style="dashed") >> tracking_api
        tracking_api >> el(style="dashed") >> bq
        bff >> el() >> alb
        alb >> el() >> mob
        mob >> el() >> ddb
        mob >> el() >> s3
        mob >> el(style="dashed") >> sqs
        sqs >> el(style="dashed") >> retry_worker
        retry_worker >> el(style="dashed") >> eb
        eb >> el(style="dashed") >> aws_azure_adapter
        aws_azure_adapter >> el(style="dashed") >> eh
        eh >> el(style="dashed") >> run
        run >> el(style="dashed") >> bq
        oms >> el() >> mon
        mob >> el() >> cw
        run >> el() >> glog
        apim >> el() >> kv
        oms >> el() >> kv


def n3_plt03() -> None:
    """Nivel 3: componentes de bus-workers; PaaS y actores quedan fuera."""
    _ensure_out()
    with Diagram(
        "C4 N3 - bus-workers (PLT-03) y servicios administrados",
        filename=str(OUT_DIR / "mvp_c4_n3_plt03_componentes"),
        show=False,
        direction="TB",
        graph_attr=N3_GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        ops = Users(lbl("Actor externo", "Operaciones / Soporte", "Persona"))

        with Cluster("Azure"):
            with Cluster("Workloads vecinos en AKS"):
                bff = Docker(
                    lbl(
                        "Kubernetes Deployment",
                        "BFF del MVP",
                        "incluye demo DLQ E5",
                    )
                )
                oms = Docker(
                    lbl(
                        "Kubernetes Deployment",
                        "OMS — APP-02",
                        "escribe outbox → SQL",
                    )
                )
                inv = Docker(
                    lbl(
                        "Kubernetes Deployment",
                        "Inventario — MS-INI01-02",
                        "escribe outbox → SQL",
                    )
                )

            with Cluster("CONTENEDOR EN FOCO: Deployment bus-workers en AKS"):
                with Cluster("Implementado en el MVP"):
                    poller = Blank(n3_lbl("Outbox Poller", "Lee pendientes desde SQL"))
                    publisher = Blank(
                        n3_lbl("Event Hubs Publisher", "Publica el evento canónico")
                    )
                with Cluster("Diseño objetivo — no cableado en MVP"):
                    validator = Blank(
                        n3_lbl("Schema Validator", "Valida contrato y versión")
                    )
                    dispatcher = Blank(
                        n3_lbl("Service Bus Dispatcher", "Enruta eventos hacia colas")
                    )
                    replay = Blank(
                        n3_lbl("Replay Controller", "Reprocesa eventos auditados")
                    )
                    bp = Blank(
                        n3_lbl(
                            "Backpressure Controller",
                            "Regula concurrencia del consumidor",
                        )
                    )

            with Cluster("Servicios administrados (fuera de AKS)"):
                sql = SQLManagedInstances(
                    lbl(
                        "Azure SQL",
                        "Tablas outbox",
                        "OMS/Inventario escriben · poller lee",
                    )
                )
                eh = EventHubs(lbl("Event Hubs", "Stream canónico", "PLT-03"))
                sb = ServiceBus(
                    lbl("Service Bus", "q-inventory + DLQ (demo E5)", "PLT-03 · parcial")
                )
                audit = StorageAccounts(
                    lbl("Azure Storage", "Registro auditoría eventos", "PLT-03")
                )
                obs = LogAnalyticsWorkspaces(
                    lbl("Azure Monitor", "Observabilidad Azure", "PLT-01")
                )
                tms = Saas(
                    lbl(
                        "Consumidor mock",
                        "TMS (Transportation Management)",
                        "APP-11",
                    )
                )

        with Cluster("AWS"):
            mobile = ECS(
                lbl(
                    "ECS Fargate task",
                    "Backend móvil — APP-15",
                    "código mobile-api",
                )
            )

        with Cluster("GCP"):
            gcp = Run(lbl("Cloud Run", "Proyector CQRS", "objetivo / parcial"))

        poller >> el() >> sql
        poller >> el() >> publisher
        publisher >> el("AMQP") >> eh
        oms >> el() >> sql
        inv >> el() >> sql
        mobile >> el(style="dashed") >> eh
        eh >> el(style="dashed") >> validator
        validator >> el(style="dashed") >> dispatcher
        dispatcher >> el(style="dashed") >> sb
        ops >> el("HTTPS") >> bff
        bff >> el() >> sb
        sb >> el(style="dashed") >> inv
        sb >> el(style="dashed") >> tms
        sb >> el(style="dashed") >> bp
        bp >> el(style="dashed") >> dispatcher
        ops >> el(style="dashed") >> replay
        replay >> el(style="dashed") >> sb
        validator >> el(style="dashed") >> audit
        audit >> el() >> obs
        eh >> el(style="dashed") >> gcp


def n3_oms() -> None:
    """Nivel 3: componentes del contenedor Orquestador de Pedidos (APP-02) en AKS."""
    _ensure_out()
    with Diagram(
        "C4 N3 - Componentes Orquestador de Pedidos (APP-02)",
        filename=str(OUT_DIR / "mvp_c4_n3_oms_componentes"),
        show=False,
        direction="TB",
        graph_attr={
            **N3_GRAPH_ATTR,
            "nodesep": "0.35",
            "ranksep": "0.45",
            "pad": "0.25",
        },
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        cliente = User(lbl("Actor externo", "Cliente B2B", "Persona"))
        ops = Users(lbl("Actor externo", "Operaciones / Soporte", "Persona"))
        frontend = Client(
            lbl("Navegador", "Frontend Web del MVP", "aplicación de página única")
        )

        with Cluster("Azure"):
            with Cluster("Gateway y entrada"):
                bff = Docker(
                    lbl("Kubernetes Deployment", "BFF del MVP", "Node.js con Express")
                )
                apim = APIManagement(
                    lbl("Azure API Management", "API Gateway", "APP-01")
                )
                wms = Saas(lbl("APIM mock-wms", "WMS Principal", "APP-06"))

            with Cluster("CONTENEDOR EN FOCO: Deployment OMS en AKS"):
                with Cluster("Capa API"):
                    order_api = Blank(
                        n3_lbl("Order API", "Entrada REST para crear órdenes")
                    )
                    query_api = Blank(
                        n3_lbl("Query API", "Consulta operativa de órdenes")
                    )
                with Cluster("Resiliencia"):
                    corr = Blank(
                        n3_lbl("Correlation Middleware", "Propaga la trazabilidad")
                    )
                    cb = Blank(n3_lbl("Circuit Breaker", "Aísla fallos del WMS"))
                with Cluster("Aplicación"):
                    create = Blank(
                        n3_lbl(
                            "Create Order Handler",
                            "Ejecuta el caso de uso crear orden",
                        )
                    )
                    saga = Blank(
                        n3_lbl(
                            "Saga Orchestrator",
                            "Coordina pasos y compensaciones",
                        )
                    )
                with Cluster("Dominio DDD"):
                    agg = Blank(
                        n3_lbl("Order Aggregate", "Reglas e invariantes de orden")
                    )
                    sm = Blank(
                        n3_lbl("State Machine", "Controla transiciones de estado")
                    )
                    dedup = Blank(
                        n3_lbl("Dedup Engine", "Detecta órdenes duplicadas")
                    )
                    idem = Blank(
                        n3_lbl("Idempotency Guard", "Controla reintentos seguros")
                    )
                with Cluster("Integración"):
                    inv_client = Blank(
                        n3_lbl("Inventory Client", "Invoca Inventario por HTTP")
                    )
                with Cluster("Infraestructura"):
                    repo = Blank(
                        n3_lbl("Order Repository", "Persiste órdenes en SQL")
                    )
                    outbox = Blank(
                        n3_lbl("Outbox Repository", "Registra eventos pendientes")
                    )
                    pub = Blank(
                        n3_lbl("Event Publisher", "Entrega eventos al publicador")
                    )

            with Cluster("Vecinos y PaaS"):
                inv_svc = Docker(
                    lbl(
                        "Kubernetes Deployment",
                        "Inventario y Reservas",
                        "MS-INI01-02",
                    )
                )
                sql = SQLManagedInstances(
                    lbl("Azure SQL", "Base de datos órdenes", "APP-02")
                )
                eh = EventHubs(lbl("Event Hubs", "Stream canónico", "PLT-03"))

        cliente >> el("orden") >> frontend
        ops >> el("consulta") >> frontend
        frontend >> el("HTTPS") >> bff
        bff >> el() >> apim
        apim >> el("orden") >> order_api
        # Mock WMS: el nodo ya dice APIM mock-wms (sin etiqueta de flecha flotante)
        apim >> el() >> wms
        order_api >> el() >> corr
        corr >> el() >> create
        create >> el() >> agg
        create >> el() >> dedup >> idem
        agg >> el() >> sm >> repo
        repo >> el() >> sql
        create >> el() >> outbox
        outbox >> el() >> sql
        outbox >> el() >> pub
        pub >> el("AMQP") >> eh
        create >> el() >> saga
        saga >> el() >> cb
        cb >> el() >> apim
        saga >> el() >> inv_client
        inv_client >> el("reserva") >> inv_svc
        bff >> el() >> query_api
        query_api >> el() >> repo


def n3_mobile() -> None:
    """Nivel 3: componentes backend movil AWS (ultima milla)."""
    _ensure_out()
    with Diagram(
        "C4 N3 - Componentes Backend Movil Ultima Milla",
        filename=str(OUT_DIR / "mvp_c4_n3_mobile_componentes"),
        show=False,
        direction="TB",
        graph_attr=N3_GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        persona = User(lbl("Actor externo", "Conductor", "Persona"))
        app = Mobile(lbl("Aplicación web móvil", "App de Conductores", "APP-15"))
        local_outbox = SQL(lbl("SQLite cifrado", "Outbox local dispositivo", "APP-15"))
        bff = Docker(
            lbl("Kubernetes Deployment", "BFF del MVP", "Node.js con Express")
        )

        with Cluster("AWS"):
            with Cluster("ECS Service sobre Fargate · CONTENEDOR EN FOCO: mobile-api"):
                with Cluster("Canal"):
                    api = Blank(
                        n3_lbl("Delivery API", "Recibe entregas y evidencias")
                    )
                with Cluster("Dominio entrega"):
                    delivery = Blank(
                        n3_lbl(
                            "Delivery Handler",
                            "Coordina el caso de entrega",
                        )
                    )
                    tax = Blank(
                        n3_lbl(
                            "Exception Taxonomy Validator",
                            "Valida códigos de novedad",
                        )
                    )
                    evid = Blank(
                        n3_lbl(
                            "Evidence Orchestrator",
                            "Coordina metadatos y archivo",
                        )
                    )
                    hashv = Blank(
                        n3_lbl(
                            "Hash Verifier SHA-256",
                            "Verifica integridad de evidencia",
                        )
                    )
                with Cluster("Persistencia e integración"):
                    relay = Blank(
                        n3_lbl(
                            "Outbox Relay",
                            "Reenvía pendientes desde DynamoDB",
                        )
                    )
                retry = Docker(
                    lbl(
                        "Contenedor en tarea ECS Fargate",
                        "retry-worker",
                        "puente SQS → EventBridge · OBJETIVO",
                    )
                )

            with Cluster("Servicios administrados (fuera de ECS)"):
                alb = ALB(
                    lbl("Application Load Balancer", "Entrada mobile-api", "AWS")
                )
                outbox = Dynamodb(
                    lbl("DynamoDB", "Outbox + Ack Tracker", "backend APP-15")
                )
                upload = S3(
                    lbl("Amazon S3", "Almacenamiento Evidencias", "APP-16")
                )
                kms = KMS(lbl("AWS KMS", "Cifrado evidencias", "APP-16"))
                sqs = SQS(
                    lbl("Amazon SQS", "Buffer puente + DLQ", "hacia PLT-03")
                )
                eb = Eventbridge(
                    lbl("EventBridge", "Publicador puente", "placeholder MVP")
                )
                cw = Cloudwatch(lbl("CloudWatch", "Observabilidad AWS", "PLT-01"))

        with Cluster("Azure"):
            with Cluster("Puente de ingreso objetivo"):
                adapter = FunctionApps(
                    lbl(
                        "Azure Function",
                        "Adaptador AWS→Azure",
                        "normaliza el evento · OBJETIVO",
                    )
                )
                eh = EventHubs(
                    lbl("Azure Event Hubs", "Bus de Eventos Central", "PLT-03")
                )

        persona >> el("entrega") >> app
        app >> el("offline") >> local_outbox
        app >> el("HTTPS") >> bff
        bff >> el() >> alb
        alb >> el() >> api
        api >> el() >> delivery
        delivery >> el() >> tax
        delivery >> el() >> evid >> hashv
        delivery >> el() >> outbox
        evid >> el() >> upload
        upload >> el("SSE-KMS") >> kms
        relay >> el(style="dashed") >> outbox
        relay >> el(style="dashed") >> sqs
        sqs >> el("consume", style="dashed") >> retry
        retry >> el(style="dashed") >> eb
        eb >> el(style="dashed") >> adapter
        adapter >> el("AMQP", style="dashed") >> eh
        api >> el() >> cw


def n3_inventario() -> None:
    """Nivel 3: componentes del contenedor Microservicio Inventario y Reservas (MS-INI01-02) en AKS."""
    _ensure_out()
    with Diagram(
        "C4 N3 - Componentes Microservicio Inventario y Reservas (MS-INI01-02)",
        filename=str(OUT_DIR / "mvp_c4_n3_inventario_componentes"),
        show=False,
        direction="TB",
        graph_attr=N3_GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        with Cluster("Azure"):
            with Cluster("Vecinos externos"):
                oms = Docker(
                    lbl("Kubernetes Deployment", "Orquestador de Pedidos", "APP-02")
                )
                eh = EventHubs(lbl("Event Hubs", "Stream canónico", "PLT-03"))
                sb = ServiceBus(
                    lbl("Service Bus", "Cola inventario", "PLT-03 · OBJETIVO")
                )
                sql = SQLManagedInstances(
                    lbl("Azure SQL", "Base de datos inventario", "MS-INI01-02")
                )

            with Cluster("CONTENEDOR EN FOCO: Deployment Inventario en AKS"):
                with Cluster("Capa API"):
                    reserve_api = Blank(
                        n3_lbl("Reserve API", "Recibe solicitudes de reserva")
                    )
                    release_api = Blank(
                        n3_lbl("Release API", "Recibe solicitudes de liberación")
                    )
                    avail_api = Blank(
                        n3_lbl(
                            "Availability Query API",
                            "Consulta disponibilidad operativa",
                        )
                    )
                with Cluster("Dominio DDD"):
                    agg = Blank(
                        n3_lbl(
                            "Inventory Aggregate",
                            "Mantiene invariantes de inventario",
                        )
                    )
                    policy = Blank(
                        n3_lbl("Reservation Policy", "Aplica reglas de reserva")
                    )
                with Cluster("Aplicación"):
                    reserve = Blank(
                        n3_lbl("Reserve Handler", "Ejecuta el caso de reserva")
                    )
                    release = Blank(
                        n3_lbl("Release Handler", "Ejecuta la liberación")
                    )
                with Cluster("Infraestructura"):
                    res_repo = Blank(
                        n3_lbl("Reservation Repository", "Persiste reservas en SQL")
                    )
                    pos_repo = Blank(
                        n3_lbl(
                            "Position Repository",
                            "Consulta posiciones de stock",
                        )
                    )
                    outbox = Blank(
                        n3_lbl("Outbox Repository", "Registra eventos pendientes")
                    )
                    pub = Blank(
                        n3_lbl(
                            "Event Publisher",
                            "Publica resultados de inventario",
                        )
                    )
                with Cluster("Resiliencia"):
                    idem = Blank(
                        n3_lbl("Idempotency Guard", "Controla reintentos seguros")
                    )
                    opt_lock = Blank(
                        n3_lbl(
                            "Optimistic Lock",
                            "Evita conflictos concurrentes",
                        )
                    )
                    queue_consumer = Blank(
                        n3_lbl(
                            "Queue Consumer",
                            "Consume comandos desde Service Bus",
                        )
                    )
                    bp = Blank(
                        n3_lbl(
                            "Backpressure Controller",
                            "Regula concurrencia del consumidor",
                        )
                    )

        oms >> el("reserva") >> reserve_api
        oms >> el("liberación") >> release_api
        sb >> el(style="dashed") >> queue_consumer
        queue_consumer >> el(style="dashed") >> bp
        bp >> el(style="dashed") >> reserve
        reserve_api >> el() >> reserve
        release_api >> el() >> release
        reserve >> el() >> idem >> agg >> policy
        reserve >> el() >> pos_repo
        reserve >> el() >> res_repo
        reserve >> el() >> opt_lock >> pos_repo
        release >> el() >> res_repo
        reserve >> el() >> outbox
        release >> el() >> outbox
        pos_repo >> el() >> sql
        res_repo >> el() >> sql
        outbox >> el() >> sql
        outbox >> el() >> pub
        pub >> el("AMQP") >> eh
        avail_api >> el() >> pos_repo


JOBS = {
    "n1": n1_contexto,
    "n2": n2_contenedores,
    "n3-plt03": n3_plt03,
    "n3-oms": n3_oms,
    "n3-mobile": n3_mobile,
    "n3-inventario": n3_inventario,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera diagramas C4 MVP Hito 3")
    parser.add_argument(
        "--only",
        choices=list(JOBS.keys()),
        help="Generar solo un diagrama",
    )
    args = parser.parse_args()
    targets = [args.only] if args.only else list(JOBS.keys())
    for key in targets:
        print(f"Generando {key}...")
        JOBS[key]()
        print(f"  OK -> {OUT_DIR}")
    print("Listo.")


if __name__ == "__main__":
    main()
