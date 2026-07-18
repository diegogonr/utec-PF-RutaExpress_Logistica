#!/usr/bin/env python3
"""
Genera diagramas C4 de la Alternativa B (Hito 2) con la libreria diagrams (mingrammer).
Estilo alineado a HITO 3 (generar_diagramas_mvp_c4.py) y a la reparticion N3 de Alternativa A.

Alternativa B = Orquestacion + Monolito Modular
  N1 Contexto
  N2 Contenedores
  N3 x4 (paralelo a A):
    - orquestador / notificaciones  (~ PLT-03 en A)
    - modulo OMS del nucleo         (~ OMS en A)
    - modulo Inventario del nucleo  (~ Inventario en A)
    - backend movil AWS             (~ mobile en A)

Convencion de etiquetas en cada caja (3 lineas):
  1. Nombre del servicio cloud (proveedor)
  2. Nombre oficial (aplicacion / modulo / plataforma)
  3. Identificador (APP-XX, PLT-XX) o rol

Requiere: pip install diagrams graphviz  +  Graphviz (dot) en el PATH del SO.

Salida: diagramas_c4/imagenes_alternativa_B/*.png

Uso:
  python generar_diagramas_alternativa_B_c4.py
  python generar_diagramas_alternativa_B_c4.py --only n3-oms
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
from diagrams.azure.analytics import LogAnalyticsWorkspaces
from diagrams.azure.compute import AKS, FunctionApps
from diagrams.azure.database import SQLManagedInstances
from diagrams.azure.integration import APIManagement, ServiceBus
from diagrams.azure.security import KeyVaults
from diagrams.azure.storage import StorageAccounts
from diagrams.gcp.analytics import BigQuery
from diagrams.gcp.compute import Run
from diagrams.gcp.operations import Logging
from diagrams.generic.blank import Blank as BlankNode
from diagrams.generic.device import Mobile
from diagrams.k8s.compute import Deploy as Docker
from diagrams.onprem.client import Client, User, Users
from diagrams.onprem.database import PostgreSQL as SQL
from diagrams.saas import Saas

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "imagenes_alternativa_B"

GRAPH_ATTR = {
    "fontsize": "16",
    "fontname": "Segoe UI",
    "bgcolor": "white",
    "pad": "0.6",
    "nodesep": "1.0",
    "ranksep": "1.3",
    "dpi": "200",
    "compound": "true",
    "splines": "ortho",
    "overlap": "false",
    "newrank": "true",
}

N3_GRAPH_ATTR = {
    **GRAPH_ATTR,
    "splines": "ortho",
    "nodesep": "0.40",
    "ranksep": "0.55",
    "pad": "0.35",
}

NODE_ATTR = {"fontsize": "10", "fontname": "Segoe UI"}
EDGE_ATTR = {"fontsize": "7", "fontname": "Segoe UI"}


def el(text: str = "", **attrs) -> Edge:
    if text:
        attrs = {"label": text, **attrs}
    return Edge(**attrs)


def lbl(servicio: str, nombre: str, identificador: str) -> str:
    return f"{servicio}\n{nombre}\n{identificador}"


def wrap_text(text: str, width: int = 22) -> str:
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
    return (
        f"Componente N3\n"
        f"{wrap_text(nombre, 20)}\n"
        f"{wrap_text(responsabilidad, 20)}"
    )


def Blank(label: str) -> BlankNode:
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
        "C4 N1 - Contexto Alternativa B (Orquestacion + Monolito Modular)",
        filename=str(OUT_DIR / "alternativa_B_c4_n1_contexto"),
        show=False,
        direction="TB",
        graph_attr={**GRAPH_ATTR, "splines": "ortho"},
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        cliente = User(lbl("Actor", "Cliente B2B", "Persona"))
        conductor = Mobile(lbl("Dispositivo movil", "App de Conductores", "APP-15"))
        ops = Users(lbl("Actor", "Operaciones / Soporte", "Persona"))
        finanzas = Users(lbl("Actor", "Finanzas", "Persona"))

        with Cluster("Sistema en alcance"):
            plataforma = Blank(
                lbl(
                    "Plataforma multinube",
                    "Plataforma Logistica TO BE",
                    "Orquestacion + monolito modular",
                )
            )

        wms = Saas(lbl("On Premises", "WMS Principal / Satelite", "APP-06 / APP-07"))
        erp = Saas(lbl("On Premises", "ERP Financiero", "APP-25"))
        portal = Saas(lbl("SaaS", "Portal B2B / CRM", "APP-18 / APP-20"))
        tms = Saas(lbl("Azure / SaaS", "TMS Transportation Management", "APP-11"))

        cliente >> el("HTTPS API\nPOST orden / GET tracking") >> plataforma
        conductor >> el("HTTPS movil\nentrega / evidencias") >> plataforma
        ops >> el("HTTPS monitoreo\nSLA / excepciones") >> plataforma
        finanzas >> el("HTTPS consulta\nevidencias / estados") >> plataforma
        plataforma >> el("HTTPS sync\nreserva / picking") >> wms
        plataforma >> el("HTTPS sync\nvalorizacion") >> erp
        plataforma >> el("HTTPS / notificacion\ntrazabilidad") >> portal
        plataforma >> el("HTTPS / notificacion\ndespacho") >> tms


def n2_contenedores() -> None:
    """C4 N2: nucleo modular + orquestador; notificaciones selectivas (no PLT-03)."""
    _ensure_out()
    with Diagram(
        "C4 N2 - Contenedores Alternativa B (Orquestacion + Monolito Modular)",
        filename=str(OUT_DIR / "alternativa_B_c4_n2_contenedores"),
        show=False,
        direction="LR",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
    ):
        cliente = User(lbl("Actor", "Cliente B2B", "Persona"))
        conductor = Mobile(
            lbl("Dispositivo movil", "App de Conductores", "APP-15")
        )
        ops = Users(lbl("Actor", "Operaciones / Soporte", "Persona"))

        with Cluster("Azure - Core orquestado"):
            apim = APIManagement(
                lbl("Azure API Management", "Gateway y Gobierno API", "APP-01")
            )
            core = AKS(
                lbl(
                    "AKS",
                    "Nucleo Logistico Modular",
                    "APP-02 OMS + Inventario",
                )
            )
            orch = FunctionApps(
                lbl(
                    "Durable Functions",
                    "Orquestador de Procesos",
                    "Saga orden-reserva",
                )
            )
            sql = SQLManagedInstances(
                lbl(
                    "Azure SQL",
                    "Repositorio transaccional",
                    "APP-02 nucleo",
                )
            )
            notif = ServiceBus(
                lbl(
                    "Service Bus topics",
                    "Canal de notificaciones",
                    "fan-out informativo",
                )
            )
            kv = KeyVaults(
                lbl("Key Vault", "Identidad y secretos", "PLT-02")
            )

        with Cluster("AWS - Ultima milla"):
            alb = ALB(
                lbl(
                    "Application Load Balancer",
                    "Entrada backend movil",
                    "soporta APP-15",
                )
            )
            mob = ECS(
                lbl(
                    "ECS Fargate",
                    "Backend movil ultima milla",
                    "soporta APP-15",
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
            kms = KMS(lbl("AWS KMS", "Cifrado evidencias", "APP-16"))

        with Cluster("GCP - Analitica"):
            run = Run(
                lbl("Cloud Run", "Optimizador / proyector", "rutas / CQRS")
            )
            bq = BigQuery(
                lbl("BigQuery", "Almacen analitico", "consultas / tableros")
            )

        with Cluster("Observabilidad"):
            mon = LogAnalyticsWorkspaces(
                lbl(
                    "Azure Monitor",
                    "Plataforma Observabilidad Unificada",
                    "PLT-01",
                )
            )
            cw = Cloudwatch(
                lbl(
                    "CloudWatch",
                    "Plataforma Observabilidad Unificada",
                    "PLT-01",
                )
            )
            glog = Logging(
                lbl(
                    "Cloud Logging",
                    "Plataforma Observabilidad Unificada",
                    "PLT-01",
                )
            )

        with Cluster("Legados / externos"):
            mock_wms = Saas(
                lbl("ACL / API", "WMS Principal (On Premises)", "APP-06")
            )
            mock_erp = Saas(
                lbl("ACL / API", "ERP Financiero (On Premises)", "APP-25")
            )
            mock_portal = Saas(
                lbl("Notificacion / API", "Portal B2B / CRM", "APP-18 / APP-20")
            )
            mock_tms = Saas(
                lbl("Notificacion / API", "TMS Transportation Mgmt", "APP-11")
            )

        cliente >> Edge(label="HTTPS API\nPOST orden") >> apim
        apim >> Edge(label="REST comando\nidempotente") >> core
        core >> sql
        core >> Edge(label="dispara saga") >> orch
        orch >> Edge(label="pasos / compensaciones") >> core
        orch >> Edge(label="HTTPS sync\nACL + circuit breaker") >> mock_wms
        orch >> Edge(label="HTTPS sync\nvalorizacion") >> mock_erp
        orch >> Edge(label="notificacion\nresultado saga") >> notif
        notif >> mock_portal
        notif >> Edge(label="fan-out") >> mock_tms
        notif >> Edge(label="fan-out analitico") >> run >> bq

        conductor >> Edge(label="HTTPS movil") >> alb >> mob >> ddb
        mob >> s3 >> kms
        mob >> Edge(label="confirmacion API\nidempotente") >> apim

        apim >> Edge(label="obtiene secretos") >> kv
        core >> Edge(label="obtiene secretos") >> kv
        core >> mon
        orch >> mon
        mob >> cw
        run >> glog
        ops >> Edge(label="HTTPS monitoreo\nworkflows / SLA") >> mon


def n3_orquestador() -> None:
    """N3 paralelo a PLT-03 de A: Durable Functions + canal de notificaciones."""
    _ensure_out()
    with Diagram(
        "C4 N3 - Orquestador Durable Functions y notificaciones (Alternativa B)",
        filename=str(OUT_DIR / "alternativa_B_c4_n3_orquestador_componentes"),
        show=False,
        direction="TB",
        graph_attr=N3_GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        ops = Users(lbl("Actor externo", "Operaciones / Soporte", "Persona"))

        with Cluster("Azure"):
            with Cluster("Workloads vecinos en AKS"):
                core = Docker(
                    lbl(
                        "Kubernetes Deployment",
                        "Nucleo Logistico Modular",
                        "APP-02 OMS + Inventario",
                    )
                )
                apim = APIManagement(
                    lbl("Azure API Management", "Gateway y Gobierno API", "APP-01")
                )

            with Cluster("CONTENEDOR EN FOCO: Orquestador Durable Functions"):
                with Cluster("Runtime de saga"):
                    starter = Blank(n3_lbl("Saga Starter", "Recibe disparo desde el nucleo"))
                    orch = Blank(
                        n3_lbl("Process Orchestrator", "Coordina pasos y compensaciones")
                    )
                    timer = Blank(n3_lbl("Timeout / Retry Policy", "Controla esperas y reintentos"))
                    comp = Blank(
                        n3_lbl("Compensation Activities", "Revierte efectos de negocio")
                    )
                with Cluster("Actividades externas"):
                    wms_act = Blank(n3_lbl("WMS Activity", "Llama WMS via ACL/APIM"))
                    erp_act = Blank(n3_lbl("ERP Activity", "Llama ERP via ACL/APIM"))
                    notify_act = Blank(
                        n3_lbl("Notify Activity", "Emite resultado de saga")
                    )

            with Cluster("Canal de notificaciones (sin PLT-03 completo)"):
                outbox = SQLManagedInstances(
                    lbl("Azure SQL", "Notification Outbox", "post-commit del nucleo")
                )
                sb = ServiceBus(
                    lbl("Service Bus topics", "Canal de notificaciones", "fan-out informativo")
                )
                audit = StorageAccounts(
                    lbl("Azure Storage", "Audit Store workflows", "correlation ID")
                )
                obs = LogAnalyticsWorkspaces(
                    lbl("Azure Monitor", "Observabilidad Azure", "PLT-01")
                )

            with Cluster("Externos"):
                wms = Saas(lbl("ACL / API", "WMS Principal", "APP-06"))
                erp = Saas(lbl("ACL / API", "ERP Financiero", "APP-25"))
                portal = Saas(lbl("Notificacion", "Portal B2B / CRM", "APP-18 / APP-20"))
                tms = Saas(lbl("Notificacion", "TMS", "APP-11"))

        with Cluster("GCP"):
            run = Run(lbl("Cloud Run", "Proyector / analitica", "consume notificacion"))

        core >> el("dispara") >> starter >> orch
        orch >> el() >> timer
        orch >> el() >> wms_act >> el("HTTPS") >> apim >> wms
        orch >> el() >> erp_act >> el("HTTPS") >> apim >> erp
        orch >> el("compensa") >> comp >> core
        orch >> el() >> notify_act
        core >> el() >> outbox
        outbox >> el("relay") >> sb
        notify_act >> el() >> sb
        sb >> el("fan-out") >> portal
        sb >> el("fan-out") >> tms
        sb >> el("fan-out") >> run
        orch >> el() >> audit >> obs
        ops >> el("consulta workflow") >> orch


def n3_oms() -> None:
    """N3 paralelo a OMS de A: modulo Order Lifecycle dentro del nucleo modular."""
    _ensure_out()
    with Diagram(
        "C4 N3 - Modulo OMS del Nucleo Logistico Modular (APP-02)",
        filename=str(OUT_DIR / "alternativa_B_c4_n3_oms_componentes"),
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
            lbl("Navegador", "Frontend / Portal", "consulta operativa")
        )

        with Cluster("Azure"):
            with Cluster("Gateway y vecinos"):
                apim = APIManagement(
                    lbl("Azure API Management", "API Gateway", "APP-01")
                )
                orch = FunctionApps(
                    lbl("Durable Functions", "Orquestador de Procesos", "Saga runtime")
                )
                inv_mod = Docker(
                    lbl(
                        "Modulo interno AKS",
                        "Inventory and Reservation",
                        "mismo deploy APP-02",
                    )
                )
                wms = Saas(lbl("APIM / ACL", "WMS Principal", "APP-06"))

            with Cluster("CONTENEDOR EN FOCO: Modulo OMS dentro del Nucleo Modular"):
                with Cluster("Capa API"):
                    facade = Blank(n3_lbl("Command API Facade", "Entrada REST de ordenes"))
                    query = Blank(n3_lbl("Query API", "Consulta operativa de ordenes"))
                with Cluster("Seguridad y resiliencia"):
                    authz = Blank(n3_lbl("AuthZ / Claims", "Autorizacion por token/roles"))
                    corr = Blank(n3_lbl("Correlation Middleware", "Propaga trazabilidad"))
                    cb = Blank(n3_lbl("Circuit Breaker", "Aisla fallos de legados"))
                with Cluster("Aplicacion"):
                    create = Blank(
                        n3_lbl("Create Order Handler", "Caso de uso crear orden")
                    )
                    saga_hook = Blank(
                        n3_lbl("Saga Trigger", "Dispara Durable Functions")
                    )
                with Cluster("Dominio DDD"):
                    order = Blank(n3_lbl("Order Lifecycle Module", "Estado canonico orden"))
                    dedup = Blank(n3_lbl("Validation and Dedup", "Detecta duplicados"))
                    idem = Blank(n3_lbl("Idempotency Guard", "Reintentos seguros"))
                with Cluster("Infraestructura"):
                    uow = Blank(n3_lbl("Unit of Work", "TX local Azure SQL"))
                    repo = Blank(n3_lbl("Order Repository", "Persiste ordenes"))
                    outbox = Blank(
                        n3_lbl("Notification Outbox", "Fan-out post-commit")
                    )

            with Cluster("PaaS"):
                sql = SQLManagedInstances(
                    lbl("Azure SQL", "BD nucleo compartida", "APP-02")
                )
                sb = ServiceBus(
                    lbl("Service Bus topics", "Canal de notificaciones", "fan-out")
                )

        cliente >> el("orden") >> frontend
        ops >> el("consulta") >> frontend
        frontend >> el("HTTPS") >> apim
        apim >> el("orden") >> facade
        facade >> el() >> authz >> corr >> create
        create >> el() >> dedup >> idem
        create >> el() >> uow
        uow >> order >> repo >> sql
        uow >> outbox >> sql
        outbox >> el("relay") >> sb
        create >> el() >> saga_hook >> orch
        create >> el("reserva in-proc") >> inv_mod
        orch >> el("pasos saga") >> cb >> apim >> wms
        frontend >> el() >> query >> repo


def n3_inventario() -> None:
    """N3 paralelo a Inventario de A: modulo Inventory dentro del mismo nucleo."""
    _ensure_out()
    with Diagram(
        "C4 N3 - Modulo Inventario del Nucleo Logistico Modular (APP-02)",
        filename=str(OUT_DIR / "alternativa_B_c4_n3_inventario_componentes"),
        show=False,
        direction="TB",
        graph_attr=N3_GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        with Cluster("Azure"):
            with Cluster("Vecinos del mismo deploy / externos"):
                oms_mod = Docker(
                    lbl(
                        "Modulo interno AKS",
                        "Order Lifecycle Module",
                        "mismo deploy APP-02",
                    )
                )
                orch = FunctionApps(
                    lbl("Durable Functions", "Orquestador de Procesos", "Saga runtime")
                )
                sql = SQLManagedInstances(
                    lbl("Azure SQL", "BD nucleo compartida", "APP-02")
                )
                sb = ServiceBus(
                    lbl("Service Bus topics", "Canal de notificaciones", "fan-out")
                )
                wms = Saas(lbl("ACL / API", "WMS Principal", "APP-06"))

            with Cluster("CONTENEDOR EN FOCO: Modulo Inventario dentro del Nucleo Modular"):
                with Cluster("Capa API interna"):
                    reserve = Blank(n3_lbl("Reserve API", "Reserva stock (in-proc/HTTP)"))
                    release = Blank(n3_lbl("Release API", "Libera reserva"))
                    avail = Blank(n3_lbl("Availability Query", "Consulta disponibilidad"))
                with Cluster("Dominio"):
                    inv = Blank(
                        n3_lbl("Inventory Aggregate", "Reglas de stock y reserva")
                    )
                    policy = Blank(
                        n3_lbl("Reservation Policy", "Politicas de asignacion")
                    )
                    idem = Blank(n3_lbl("Idempotency Guard", "Evita doble reserva"))
                with Cluster("Aplicacion"):
                    reserve_h = Blank(
                        n3_lbl("Reserve Handler", "Caso de uso reservar")
                    )
                    release_h = Blank(
                        n3_lbl("Release Handler", "Caso de uso liberar")
                    )
                    comp = Blank(
                        n3_lbl("Compensation Hook", "Compensa ante fallo de saga")
                    )
                with Cluster("Integracion e infra"):
                    acl = Blank(n3_lbl("WMS ACL Adapter", "Sync/adaptacion a WMS"))
                    cb = Blank(n3_lbl("Circuit Breaker", "Protege llamadas WMS"))
                    repo = Blank(n3_lbl("Inventory Repository", "Persiste stock/reservas"))
                    outbox = Blank(
                        n3_lbl("Notification Outbox", "Eventos informativos stock")
                    )

        oms_mod >> el("reserva") >> reserve >> reserve_h
        reserve_h >> el() >> idem >> inv >> policy
        reserve_h >> el() >> repo >> sql
        reserve_h >> el() >> outbox >> sql
        outbox >> el("relay") >> sb
        orch >> el("compensa") >> comp >> release_h >> release
        release_h >> inv
        inv >> acl >> cb >> el("HTTPS") >> wms
        avail >> repo


def n3_mobile() -> None:
    """N3 paralelo a mobile de A: backend AWS; en B confirma al nucleo por API."""
    _ensure_out()
    with Diagram(
        "C4 N3 - Componentes Backend Movil Ultima Milla (Alternativa B)",
        filename=str(OUT_DIR / "alternativa_B_c4_n3_mobile_componentes"),
        show=False,
        direction="TB",
        graph_attr=N3_GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR,
    ):
        persona = User(lbl("Actor externo", "Conductor", "Persona"))
        app = Mobile(lbl("Aplicacion web movil", "App de Conductores", "APP-15"))
        local_outbox = SQL(lbl("SQLite cifrado", "Outbox local dispositivo", "APP-15"))

        with Cluster("AWS"):
            with Cluster("ECS Service sobre Fargate · CONTENEDOR EN FOCO: mobile-api"):
                with Cluster("Canal"):
                    api = Blank(n3_lbl("Delivery API", "Recibe entregas y evidencias"))
                with Cluster("Dominio entrega"):
                    delivery = Blank(
                        n3_lbl("Delivery Handler", "Coordina el caso de entrega")
                    )
                    tax = Blank(
                        n3_lbl(
                            "Exception Taxonomy Validator",
                            "Valida codigos de novedad",
                        )
                    )
                    evid = Blank(
                        n3_lbl(
                            "Evidence Orchestrator",
                            "Coordina metadatos y archivo",
                        )
                    )
                    hashv = Blank(
                        n3_lbl("Hash Verifier SHA-256", "Verifica integridad")
                    )
                with Cluster("Persistencia e integracion"):
                    relay = Blank(
                        n3_lbl("Outbox Relay", "Reenvia pendientes desde DynamoDB")
                    )
                    confirm = Blank(
                        n3_lbl(
                            "Nucleo Confirm Client",
                            "Confirma entrega al nucleo Azure",
                        )
                    )
                retry = Docker(
                    lbl(
                        "Contenedor en tarea ECS Fargate",
                        "retry-worker",
                        "reintentos store-and-forward",
                    )
                )

            with Cluster("Servicios administrados (fuera de ECS)"):
                alb = ALB(lbl("Application Load Balancer", "Entrada mobile-api", "AWS"))
                outbox = Dynamodb(
                    lbl("DynamoDB", "Outbox + Ack Tracker", "backend APP-15")
                )
                upload = S3(lbl("Amazon S3", "Almacenamiento Evidencias", "APP-16"))
                kms = KMS(lbl("AWS KMS", "Cifrado evidencias", "APP-16"))
                sqs = SQS(lbl("Amazon SQS", "Buffer reintentos + DLQ", "sync movil"))
                eb = Eventbridge(
                    lbl("EventBridge", "Opcional fan-out AWS", "no hub PLT-03")
                )
                cw = Cloudwatch(lbl("CloudWatch", "Observabilidad AWS", "PLT-01"))

        with Cluster("Azure"):
            apim = APIManagement(
                lbl("Azure API Management", "Gateway", "APP-01")
            )
            core = Docker(
                lbl(
                    "Kubernetes Deployment",
                    "Nucleo Logistico Modular",
                    "APP-02",
                )
            )

        persona >> el("entrega") >> app
        app >> el("offline") >> local_outbox
        app >> el("HTTPS") >> alb >> api
        api >> el() >> delivery
        delivery >> el() >> tax
        delivery >> el() >> evid >> hashv
        delivery >> el() >> outbox
        evid >> el() >> upload
        upload >> el("SSE-KMS") >> kms
        relay >> el(style="dashed") >> outbox
        relay >> el(style="dashed") >> sqs
        sqs >> el("consume", style="dashed") >> retry
        retry >> el(style="dashed") >> confirm
        delivery >> el() >> confirm
        confirm >> el("HTTPS\nidempotente") >> apim >> core
        retry >> el(style="dashed") >> eb
        api >> el() >> cw


JOBS = {
    "n1": n1_contexto,
    "n2": n2_contenedores,
    "n3-orquestador": n3_orquestador,
    "n3-oms": n3_oms,
    "n3-inventario": n3_inventario,
    "n3-mobile": n3_mobile,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera diagramas C4 Alternativa B (estilo Hito 3 / paralelo a A)"
    )
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
