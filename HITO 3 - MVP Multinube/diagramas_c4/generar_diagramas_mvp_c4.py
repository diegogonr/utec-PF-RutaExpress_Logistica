#!/usr/bin/env python3
"""
Genera diagramas C4 del MVP Hito 3 con la libreria diagrams (mingrammer).
Requiere: pip install diagrams graphviz  +  Graphviz instalado en el SO.

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
from diagrams.gcp.analytics import BigQuery, PubSub
from diagrams.gcp.compute import Run
from diagrams.gcp.operations import Logging
from diagrams.generic.blank import Blank
from diagrams.generic.device import Mobile
from diagrams.onprem.client import User, Users
from diagrams.onprem.database import PostgreSQL
from diagrams.saas import Saas

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "imagenes"

GRAPH_ATTR = {
    "fontsize": "16",
    "fontname": "Segoe UI",
    "bgcolor": "white",
    "pad": "0.6",
    "nodesep": "0.9",
    "ranksep": "1.2",
    "dpi": "200",
    "compound": "true",
    "splines": "ortho",
}

NODE_ATTR = {"fontsize": "10", "fontname": "Segoe UI"}


def lbl(servicio: str, nombre: str, identificador: str) -> str:
    """Etiqueta estandar: servicio cloud + nombre oficial + ID o rol."""
    return f"{servicio}\n{nombre}\n{identificador}"


def _ensure_out() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def n1_contexto() -> None:
    _ensure_out()
    with Diagram(
        "C4 N1 - Contexto MVP RutaExpress",
        filename=str(OUT_DIR / "mvp_c4_n1_contexto"),
        show=False,
        direction="TB",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
    ):
        cliente = User(lbl("Actor", "Cliente B2B", "Persona"))
        conductor = Mobile(
            lbl(
                "Dispositivo movil",
                "App de Conductores",
                "APP-15",
            )
        )
        ops = Users(lbl("Actor", "Operaciones / Soporte", "Persona"))

        with Cluster("Sistema en alcance"):
            mvp = Blank(
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

        cliente >> Edge(label="HTTPS API\nPOST orden / GET tracking") >> mvp
        conductor >> Edge(label="HTTPS movil\nentrega / evidencias") >> mvp
        ops >> Edge(label="HTTPS monitoreo\nDLQ / dashboards") >> mvp
        mvp >> Edge(label="HTTPS mock sync\nconfirmar reserva") >> wms
        mvp >> Edge(label="HTTPS mock sync\nvalorizacion") >> erp
        mvp >> Edge(label="HTTPS GET lectura\nmock-portal CQRS") >> portal
        mvp >> Edge(label="Eventos async\ndespacho / manifiesto") >> tms


def n2_contenedores() -> None:
    _ensure_out()
    with Diagram(
        "C4 N2 - Contenedores MVP Hub central Azure",
        filename=str(OUT_DIR / "mvp_c4_n2_contenedores"),
        show=False,
        direction="LR",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
    ):
        cliente = User(lbl("Actor", "Cliente B2B", "Persona"))
        conductor = Mobile(
            lbl(
                "Dispositivo movil",
                "App de Conductores",
                "APP-15",
            )
        )
        ops = Users(lbl("Actor", "Operaciones / Soporte", "Persona"))

        with Cluster("Azure - Hub operativo"):
            apim = APIManagement(
                lbl(
                    "Azure API Management",
                    "Azure API Management",
                    "APP-01",
                )
            )
            oms = AKS(
                lbl(
                    "AKS",
                    "Orquestador de Pedidos",
                    "APP-02",
                )
            )
            inv = AKS(
                lbl(
                    "AKS",
                    "Microservicio Inventario y Reservas",
                    "MS-INI01-02",
                )
            )
            sql = SQLManagedInstances(
                lbl(
                    "Azure SQL",
                    "Repositorio transaccional",
                    "APP-02 + MS-INI01-02",
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
                    "Bus de Eventos Central",
                    "PLT-03",
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

        with Cluster("GCP - Analitica CQRS"):
            run = Run(
                lbl(
                    "Cloud Run",
                    "Proyector CQRS",
                    "lectura tracking",
                )
            )
            ps = PubSub(
                lbl(
                    "Pub/Sub",
                    "Mensajeria analitica",
                    "GCP",
                )
            )
            bq = BigQuery(
                lbl(
                    "BigQuery",
                    "Almacen consultas CQRS",
                    "mock-portal APP-18",
                )
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

        with Cluster("Legados simulados (SaaS externo)"):
            mock_wms = Saas(
                lbl(
                    "Ruta APIM mock-wms",
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

        cliente >> Edge(label="HTTPS API\nPOST orden / GET tracking") >> apim >> Edge(label="REST interno") >> oms >> sql
        apim >> Edge(label="mock-portal\nconsulta BigQuery") >> bq
        apim >> Edge(label="mock-portal\nsimula contrato") >> mock_portal
        oms >> Edge(label="HTTPS mock sync\nSaga confirmacion") >> apim
        apim >> Edge(label="mock-wms") >> mock_wms
        apim >> Edge(label="mock-erp") >> mock_erp
        oms >> redis
        oms >> Edge(label="eventos async") >> eh >> sb
        inv >> sql
        inv >> Edge(label="eventos async") >> eh
        sb >> Edge(label="eventos async\ncola MS-INI01-02") >> inv
        sb >> Edge(label="eventos async\nmock-tms") >> mock_tms
        conductor >> Edge(label="HTTPS movil") >> alb >> mob >> ddb
        mob >> s3
        mob >> Edge(label="outbox relay +\nretry worker (mismo task)") >> sqs >> eb >> Edge(label="puente multinube") >> eh
        eh >> Edge(label="eventos async") >> run >> bq
        ps >> run
        oms >> mon
        mob >> cw
        run >> glog
        kv >> apim
        ops >> Edge(label="HTTPS monitoreo\nDLQ / metricas") >> mon


def n3_plt03() -> None:
    """Nivel 3: componentes internos del contenedor Bus de Eventos Central (PLT-03)."""
    _ensure_out()
    with Diagram(
        "C4 N3 - Componentes Bus de Eventos Central (PLT-03)",
        filename=str(OUT_DIR / "mvp_c4_n3_plt03_componentes"),
        show=False,
        direction="TB",
        graph_attr={**GRAPH_ATTR, "ranksep": "1.0"},
        node_attr=NODE_ATTR,
    ):
        with Cluster("Productores (contenedores externos)"):
            oms = AKS(
                lbl(
                    "AKS",
                    "Orquestador de Pedidos",
                    "APP-02",
                )
            )
            inv = AKS(
                lbl(
                    "AKS",
                    "Microservicio Inventario y Reservas",
                    "MS-INI01-02",
                )
            )
            mobile = ECS(
                lbl(
                    "ECS Fargate",
                    "Backend movil ultima milla",
                    "soporta APP-15",
                )
            )
            legado = Saas(
                lbl(
                    "mock legado (APIM)",
                    "Adaptador CSV normalizado",
                    "APP-01 mocks",
                )
            )

        with Cluster("CONTENEDOR EN FOCO: Bus de Eventos Central (PLT-03)"):
            with Cluster("Entrada y validacion"):
                ingest = FunctionApps(
                    lbl("Azure Functions", "Event Ingestion API", "PLT-03")
                )
                schema = FunctionApps(
                    lbl("Azure Functions", "Schema Validator", "PLT-03")
                )
            with Cluster("Nucleo EDA"):
                router = FunctionApps(
                    lbl("Azure Functions", "Event Router", "PLT-03")
                )
                ordering = FunctionApps(
                    lbl("Azure Functions", "Ordering Guard", "PLT-03")
                )
            with Cluster("Resiliencia"):
                retry = FunctionApps(
                    lbl("Azure Functions", "Retry Scheduler", "PLT-03")
                )
                dlq = ServiceBus(
                    lbl("Service Bus", "DLQ Manager", "PLT-03")
                )
                replay = FunctionApps(
                    lbl("Azure Functions", "Replay Controller", "PLT-03")
                )
                bp = FunctionApps(
                    lbl("Azure Functions", "Backpressure Controller", "PLT-03")
                )
            with Cluster("Persistencia"):
                eh = EventHubs(
                    lbl("Event Hubs", "Stream canonico", "PLT-03")
                )
                sb = ServiceBus(
                    lbl("Service Bus", "Colas por consumidor", "PLT-03")
                )
                audit = StorageAccounts(
                    lbl("Azure Storage", "Registro auditoria eventos", "PLT-03")
                )

        with Cluster("Consumidores (contenedores externos)"):
            tms = Saas(
                lbl(
                    "mock TMS (APIM)",
                    "TMS (Transportation Management)",
                    "APP-11",
                )
            )
            gcp = Run(
                lbl(
                    "Cloud Run",
                    "Proyector CQRS",
                    "BigQuery / APP-18",
                )
            )
            obs = LogAnalyticsWorkspaces(
                lbl(
                    "Azure Monitor",
                    "Plataforma Observabilidad Unificada",
                    "PLT-01",
                )
            )
            ops = Users(
                lbl(
                    "Actor",
                    "Operaciones / Soporte",
                    "Persona",
                )
            )

        oms >> Edge(label="publica") >> ingest
        inv >> Edge(label="publica") >> ingest
        mobile >> Edge(label="publica") >> ingest
        legado >> Edge(label="publica") >> ingest
        ingest >> schema >> router >> ordering
        ordering >> Edge(label="stream") >> eh
        ordering >> Edge(label="colas") >> retry >> sb
        router >> dlq >> replay >> router
        bp >> router
        schema >> audit
        dlq >> audit
        sb >> Edge(label="eventos async\ncola inventario") >> inv
        sb >> Edge(label="eventos async") >> tms
        eh >> Edge(label="eventos async") >> gcp
        audit >> obs
        ops >> Edge(label="HTTPS monitoreo\nreplay auditado") >> replay


def n3_oms() -> None:
    """Nivel 3: componentes del contenedor Orquestador de Pedidos (APP-02) en AKS."""
    _ensure_out()
    with Diagram(
        "C4 N3 - Componentes Orquestador de Pedidos (APP-02)",
        filename=str(OUT_DIR / "mvp_c4_n3_oms_componentes"),
        show=False,
        direction="TB",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
    ):
        apim = APIManagement(
            lbl(
                "Azure API Management",
                "Azure API Management",
                "APP-01",
            )
        )

        with Cluster("CONTENEDOR EN FOCO: Orquestador de Pedidos (APP-02) — AKS"):
            with Cluster("Capa API"):
                order_api = FunctionApps(
                    lbl("AKS pod", "Order API", "APP-02")
                )
                query_api = FunctionApps(
                    lbl("AKS pod", "Query API", "APP-02")
                )
            with Cluster("Dominio DDD"):
                agg = FunctionApps(
                    lbl("AKS pod", "Order Aggregate", "APP-02")
                )
                sm = FunctionApps(
                    lbl("AKS pod", "State Machine", "APP-02")
                )
                dedup = FunctionApps(
                    lbl("AKS pod", "Dedup Engine", "APP-02")
                )
                idem = FunctionApps(
                    lbl("AKS pod", "Idempotency Guard", "APP-02")
                )
            with Cluster("Aplicacion"):
                create = FunctionApps(
                    lbl("AKS pod", "Create Order Handler", "APP-02")
                )
                saga = FunctionApps(
                    lbl("AKS pod", "Saga Orchestrator", "APP-02")
                )
            with Cluster("Infraestructura"):
                repo = SQLManagedInstances(
                    lbl("Azure SQL", "Order Repository", "APP-02")
                )
                outbox = PostgreSQL(
                    lbl("Azure SQL", "Outbox Table", "APP-02")
                )
                pub = EventHubs(
                    lbl("Event Hubs", "Event Publisher", "PLT-03")
                )
            with Cluster("Integracion"):
                wms = Saas(
                    lbl(
                        "mock WMS (APIM)",
                        "WMS Principal (On Premises)",
                        "APP-06",
                    )
                )
                inv_client = FunctionApps(
                    lbl("AKS pod", "Inventory Client", "APP-02")
                )
            with Cluster("Resiliencia"):
                cb = FunctionApps(
                    lbl("AKS pod", "Circuit Breaker", "APP-02")
                )
                corr = FunctionApps(
                    lbl("AKS pod", "Correlation Middleware", "APP-02")
                )

        inv_svc = AKS(
            lbl(
                "AKS",
                "Microservicio Inventario y Reservas",
                "MS-INI01-02",
            )
        )
        eh = EventHubs(
            lbl(
                "Event Hubs",
                "Bus de Eventos Central",
                "PLT-03",
            )
        )

        apim >> Edge(label="HTTPS API") >> order_api >> corr >> create >> agg
        create >> dedup >> idem
        agg >> sm >> repo
        create >> outbox >> pub >> Edge(label="eventos async") >> eh
        saga >> Edge(label="HTTPS mock sync") >> wms
        saga >> Edge(label="HTTPS interno\nReleaseInventory") >> inv_client >> inv_svc
        wms >> cb
        apim >> Edge(label="HTTPS GET lectura") >> query_api >> repo


def n3_mobile() -> None:
    """Nivel 3: componentes backend movil AWS (ultima milla)."""
    _ensure_out()
    with Diagram(
        "C4 N3 - Componentes Backend Movil Ultima Milla",
        filename=str(OUT_DIR / "mvp_c4_n3_mobile_componentes"),
        show=False,
        direction="TB",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
    ):
        conductor = Mobile(
            lbl(
                "Dispositivo movil",
                "App de Conductores",
                "APP-15",
            )
        )
        local_outbox = Dynamodb(
            lbl(
                "SQLite local cifrado",
                "Outbox local dispositivo",
                "APP-15 offline",
            )
        )

        with Cluster("CONTENEDOR EN FOCO: Backend Movil AWS"):
            with Cluster("Canal"):
                alb = ALB(
                    lbl(
                        "Application Load Balancer",
                        "Mobile API",
                        "soporta APP-15",
                    )
                )
                api = ECS(
                    lbl(
                        "ECS Fargate",
                        "Delivery API",
                        "soporta APP-15",
                    )
                )
            with Cluster("Persistencia backend AWS"):
                outbox = Dynamodb(
                    lbl(
                        "DynamoDB",
                        "Outbox backend",
                        "backend APP-15",
                    )
                )
                ack = Dynamodb(
                    lbl(
                        "DynamoDB",
                        "Ack Tracker",
                        "backend APP-15",
                    )
                )
            with Cluster("Dominio entrega"):
                delivery = ECS(
                    lbl("ECS Fargate", "Delivery Handler", "backend APP-15")
                )
                tax = ECS(
                    lbl("ECS Fargate", "Exception Taxonomy Validator", "backend APP-15")
                )
                evid = ECS(
                    lbl("ECS Fargate", "Evidence Orchestrator", "backend APP-15")
                )
            with Cluster("Evidencias"):
                upload = S3(
                    lbl(
                        "Amazon S3",
                        "Almacenamiento Evidencias",
                        "APP-16",
                    )
                )
                hashv = ECS(
                    lbl("ECS Fargate", "Hash Verifier SHA-256", "APP-16")
                )
                manifest = S3(
                    lbl("Amazon S3", "Manifest auditoria", "APP-16")
                )
                kms = KMS(
                    lbl("AWS KMS", "Cifrado evidencias", "APP-16")
                )
            with Cluster("Integracion Azure"):
                relay = SQS(
                    lbl("Amazon SQS", "Outbox Relay", "hacia PLT-03")
                )
                eb = Eventbridge(
                    lbl("EventBridge", "Publisher puente", "hacia PLT-03")
                )
            with Cluster("Resiliencia"):
                retry = ECS(
                    lbl("ECS Fargate", "Retry Worker (mismo task)", "backend APP-15")
                )
            with Cluster("Observabilidad"):
                cw = Cloudwatch(
                    lbl(
                        "CloudWatch",
                        "Plataforma Observabilidad Unificada",
                        "PLT-01",
                    )
                )

        eh = EventHubs(
            lbl(
                "Event Hubs",
                "Bus de Eventos Central",
                "PLT-03",
            )
        )

        conductor >> Edge(label="offline: captura") >> local_outbox
        conductor >> Edge(label="HTTPS movil: sync") >> alb >> api >> delivery
        api >> tax
        delivery >> outbox
        delivery >> evid >> upload >> hashv >> manifest
        upload >> kms
        outbox >> relay >> retry >> Edge(label="eventos async") >> eb >> eh
        api >> ack >> outbox
        api >> cw


def n3_inventario() -> None:
    """Nivel 3: componentes del contenedor Microservicio Inventario y Reservas (MS-INI01-02) en AKS."""
    _ensure_out()
    with Diagram(
        "C4 N3 - Componentes Microservicio Inventario y Reservas (MS-INI01-02)",
        filename=str(OUT_DIR / "mvp_c4_n3_inventario_componentes"),
        show=False,
        direction="TB",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
    ):
        oms = AKS(
            lbl(
                "AKS",
                "Orquestador de Pedidos",
                "APP-02",
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
                "Bus de Eventos Central",
                "PLT-03",
            )
        )

        with Cluster(
            "CONTENEDOR EN FOCO: Microservicio Inventario y Reservas (MS-INI01-02) — AKS"
        ):
            with Cluster("Capa API"):
                reserve_api = FunctionApps(
                    lbl("AKS pod", "Reserve API", "MS-INI01-02")
                )
                release_api = FunctionApps(
                    lbl("AKS pod", "Release API", "MS-INI01-02")
                )
                avail_api = FunctionApps(
                    lbl("AKS pod", "Availability Query API", "MS-INI01-02")
                )
            with Cluster("Dominio DDD"):
                agg = FunctionApps(
                    lbl("AKS pod", "Inventory Aggregate", "MS-INI01-02")
                )
                policy = FunctionApps(
                    lbl("AKS pod", "Reservation Policy", "MS-INI01-02")
                )
                conflict = FunctionApps(
                    lbl("AKS pod", "Conflict Rules", "MS-INI01-02")
                )
            with Cluster("Aplicacion"):
                reserve = FunctionApps(
                    lbl("AKS pod", "Reserve Handler", "MS-INI01-02")
                )
                release = FunctionApps(
                    lbl("AKS pod", "Release Handler", "MS-INI01-02")
                )
                movement = FunctionApps(
                    lbl("AKS pod", "Movement Handler", "MS-INI01-02")
                )
                reconcile = FunctionApps(
                    lbl("AKS pod", "Reconciliation Handler", "MS-INI01-02")
                )
            with Cluster("Infraestructura"):
                res_repo = SQLManagedInstances(
                    lbl("Azure SQL", "Reservation Repository", "MS-INI01-02")
                )
                pos_repo = SQLManagedInstances(
                    lbl("Azure SQL", "Position Repository", "MS-INI01-02")
                )
                outbox = PostgreSQL(
                    lbl("Azure SQL", "Outbox Table", "MS-INI01-02")
                )
                pub = EventHubs(
                    lbl("Event Hubs", "Event Publisher", "PLT-03")
                )
            with Cluster("Integracion"):
                wms_evt = Saas(
                    lbl(
                        "eventos WMS (mock)",
                        "WMS Principal (On Premises)",
                        "APP-06",
                    )
                )
            with Cluster("Resiliencia"):
                idem = FunctionApps(
                    lbl("AKS pod", "Idempotency Guard", "MS-INI01-02")
                )
                opt_lock = FunctionApps(
                    lbl("AKS pod", "Optimistic Lock", "MS-INI01-02")
                )
                backpressure = FunctionApps(
                    lbl("AKS pod", "Backpressure Gate", "MS-INI01-02")
                )

        oms >> Edge(label="HTTPS interno\nReleaseInventory") >> release_api
        sb >> Edge(label="eventos async\nOrderValidated") >> reserve
        reserve >> idem >> agg >> policy
        reserve >> pos_repo >> res_repo
        reserve >> opt_lock >> pos_repo
        reserve >> outbox >> pub >> Edge(label="eventos async") >> eh
        avail_api >> pos_repo
        wms_evt >> movement >> pos_repo
        movement >> outbox
        wms_evt >> backpressure >> reconcile >> conflict
        release >> res_repo >> outbox
        release_api >> release


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
