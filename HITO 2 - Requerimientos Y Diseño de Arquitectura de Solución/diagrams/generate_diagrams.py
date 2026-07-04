#!/usr/bin/env python3
"""
Genera diagramas C4 del Hito 2 con la librería diagrams (mingrammer).
Salida: ../diagramas/*.png

Uso:
  python generate_diagrams.py
  python generate_diagrams.py --only alt-a-containers
"""

from __future__ import annotations

import argparse
from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.analytics import KinesisDataStreams
from diagrams.aws.compute import Fargate
from diagrams.aws.integration import Eventbridge, SQS
from diagrams.aws.management import Cloudwatch
from diagrams.aws.storage import S3
from diagrams.azure.analytics import EventHubs, LogAnalyticsWorkspaces
from diagrams.azure.compute import AKS, FunctionApps
from diagrams.azure.database import CacheForRedis, SQLManagedInstances
from diagrams.azure.identity import ActiveDirectory
from diagrams.azure.integration import APIManagement
from diagrams.azure.storage import StorageAccounts
from diagrams.azure.web import AppServices
from diagrams.gcp.analytics import Pubsub
from diagrams.gcp.compute import Run
from diagrams.gcp.operations import Logging
from diagrams.generic.device import Mobile
from diagrams.onprem.client import User, Users
from diagrams.onprem.compute import Server
from diagrams.onprem.database import PostgreSQL
from diagrams.saas import Saas

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR.parent / "diagramas"

GRAPH_ATTR = {
    "fontsize": "18",
    "fontname": "Segoe UI",
    "bgcolor": "white",
    "pad": "0.6",
    "nodesep": "0.9",
    "ranksep": "1.4",
    "dpi": "220",
    "compound": "true",
}

NODE_ATTR = {
    "fontsize": "14",
    "fontname": "Segoe UI",
}


def _diagram(name: str, direction: str = "TB") -> Diagram:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    return Diagram(
        name,
        filename=str(OUT_DIR / name),
        show=False,
        direction=direction,
        outformat="png",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
    )


def alt_a_context() -> None:
    with _diagram("alt-a-c4-context", "TB"):
        cliente = User("Cliente B2B\n(órdenes / trazabilidad)")
        conductor = User("Conductor\n(entregas / evidencias)")
        supervisor = User("Supervisor almacén\n(picking / campañas)")

        with Cluster("RutaExpress TO BE — Alternativa A"):
            plataforma = AKS(
                "Plataforma Logística RutaExpress\nHub central PLT-03 en Azure"
            )

        with Cluster("Cloud SaaS (EEUU)"):
            saas = Saas("Portal B2B (APP-18)\nCRM (APP-20)\nNotificaciones (APP-21)")

        with Cluster("On Premises (Lima)"):
            erp = Server("ERP Financiero\n(APP-25)")

        cliente >> Edge(label="HTTPS / API", color="#2563eb") >> plataforma
        conductor >> Edge(label="App móvil 4G", color="#2563eb") >> plataforma
        supervisor >> Edge(label="Wi-Fi / WMS UI", color="#2563eb") >> plataforma
        plataforma >> Edge(label="Webhooks / API", color="#7c3aed") >> saas
        plataforma >> Edge(label="VPN site-to-site", color="#64748b") >> erp


def alt_a_containers() -> None:
    with _diagram("alt-a-c4-containers", "LR"):
        cliente = Users("Clientes B2B")
        conductor = User("Conductor")

        with Cluster("Cloud MS Azure (EEUU)"):
            api_gw = APIManagement("API Management\n(APP-01)\nOAuth · WAF")
            orq = AKS("Orquestador Pedidos\n(APP-02)\n.NET")
            wms = AKS("WMS Cloud\n.NET · inventario único")
            tms = AKS("TMS (APP-11)\nRutas / manifiestos")
            bus = EventHubs("Bus Eventos Central\n(PLT-03)\nEvent Hubs Standard")
            connector = FunctionApps("Conector AWS→Azure\nKinesis → Event Hubs")
            obs = LogAnalyticsWorkspaces("PLT-01\nMonitor + App Insights\n+ Log Analytics")
            iam = ActiveDirectory("Entra ID (PLT-02)\n+ Key Vault")
            sql = SQLManagedInstances("Azure SQL MI\nInventario WMS")

        with Cluster("Cloud AWS (EEUU)"):
            app15 = Fargate("Backend App Conductores\n(APP-15)\nECS Fargate")
            kinesis = KinesisDataStreams("Kinesis Data Streams\nIngesta campo")
            s3 = S3("Evidencias (APP-16)\nS3 Object Lock")
            cw = Cloudwatch("CloudWatch\nMétricas AWS")

        with Cluster("Cloud SaaS (EEUU)"):
            portal = Saas("Portal B2B Trazabilidad\n(APP-18)")

        cliente >> Edge(color="#2563eb") >> api_gw
        api_gw >> Edge(label="REST") >> orq
        orq >> Edge(label="pub/sub") >> bus
        wms >> Edge(label="pub/sub") >> bus
        tms >> Edge(label="subscribe") >> bus
        wms >> Edge(label="TCP/TLS") >> sql
        conductor >> Edge(label="HTTPS/4G") >> app15
        app15 >> Edge(label="PutRecords") >> kinesis
        app15 >> Edge(label="PUT") >> s3
        kinesis >> Edge(label="stream") >> connector
        connector >> Edge(label="forward", color="#dc2626") >> bus
        bus >> Edge(label="webhook") >> portal
        iam >> Edge(label="OAuth/MFA", style="dashed") >> api_gw
        obs >> Edge(label="metrics", style="dashed") >> bus
        cw >> Edge(style="dashed") >> app15


def alt_a_components_wms_bus() -> None:
    with _diagram("alt-a-c4-components-wms-bus", "TB"):
        with Cluster("WMS Cloud — Azure AKS (INI-02)"):
            reserva = AppServices("Servicio Reserva\nidempotente")
            picking = AppServices("Servicio Picking\nolas / confirmación")
            reconciliador = AppServices("Reconciliador CD\nmodo degradado")
            publisher = AppServices("Publicador Eventos\n.NET")

        with Cluster("PLT-03 — Azure Event Hubs (INI-01)"):
            topic_inv = EventHubs("inventory-events\nmovimientos stock")
            topic_ord = EventHubs("order-status\nestados canónicos")
            replay = FunctionApps("Servicio Replay\nauditoría orderId")
            schema = StorageAccounts("Esquemas canónicos\nBlob Storage + Function")

        orq = AKS("Orquestador\n(APP-02)")
        tms = AKS("TMS (APP-11)")

        orq >> Edge(label="gRPC/REST") >> reserva
        reserva >> Edge(label="domain events") >> publisher
        picking >> Edge(label="PickingConfirmed") >> publisher
        reconciliador >> Edge(label="ReconciliationCompleted") >> publisher
        reconciliador >> Edge(label="reconcile") >> reserva
        publisher >> Edge(color="#0078d4") >> topic_inv
        publisher >> Edge(color="#0078d4") >> topic_ord
        schema >> Edge(label="valida", style="dashed") >> topic_ord
        topic_ord >> Edge(label="subscribe") >> tms
        replay >> Edge(label="replay read", style="dashed") >> topic_ord


def alt_a_components_app15() -> None:
    with _diagram("alt-a-c4-components-app15", "LR"):
        with Cluster("App Conductores — Mobile (INI-03)"):
            ui = Mobile("UI Entrega\nFlutter/RN")
            offline = PostgreSQL("SQLite AES-256\ncola offline")
            taxonomy = AppServices("Taxonomía\nexcepciones")

        with Cluster("Backend AWS — ECS Fargate"):
            api = Fargate("API Entrega\nREST sync")
            sync = Fargate("Sync Atómico\nidempotencia")
            kin_prod = KinesisDataStreams("Productor\nKinesis SDK")

        s3 = S3("APP-16 S3\nevidencias")
        kinesis = KinesisDataStreams("Kinesis\nData Streams")
        connector = FunctionApps("Conector\nAWS→Azure")
        bus = EventHubs("PLT-03\nEvent Hubs")

        ui >> Edge(label="guarda") >> offline
        ui >> Edge(label="valida") >> taxonomy
        ui >> Edge(label="sync online") >> api
        api >> Edge(label="batch") >> sync
        sync >> Edge(label="PUT atómico") >> s3
        sync >> Edge(label="emit") >> kin_prod
        kin_prod >> Edge(label="PutRecord") >> kinesis
        kinesis >> Edge(label="stream") >> connector
        connector >> Edge(label="forward", color="#dc2626") >> bus


def alt_b_context() -> None:
    with _diagram("alt-b-c4-context", "TB"):
        cliente = User("Cliente B2B")
        conductor = User("Conductor")
        supervisor = User("Supervisor almacén")

        with Cluster("RutaExpress TO BE — Alternativa B"):
            plataforma = AKS(
                "Plataforma Logística Federada\nMalla Event Hubs + EventBridge + Pub/Sub"
            )

        with Cluster("Cloud SaaS (EEUU)"):
            saas = Saas("Portal B2B · CRM · Notificaciones")

        with Cluster("On Premises (Lima)"):
            erp = Server("ERP Financiero (APP-25)")

        cliente >> Edge(color="#2563eb") >> plataforma
        conductor >> Edge(color="#2563eb") >> plataforma
        supervisor >> Edge(color="#2563eb") >> plataforma
        plataforma >> Edge(color="#7c3aed") >> saas
        plataforma >> Edge(color="#64748b") >> erp


def alt_b_containers() -> None:
    with _diagram("alt-b-c4-containers", "LR"):
        cliente = Users("Clientes B2B")
        conductor = User("Conductor")

        with Cluster("Cloud MS Azure (EEUU)"):
            api_gw = APIManagement("API Management\n(APP-01)")
            orq = AKS("Orquestador (APP-02)")
            wms = AKS("WMS Cloud\nAKS + SQL MI")
            tms = AKS("TMS (APP-11)")
            bus_az = EventHubs("PLT-03-AZ\nEvent Hubs Standard")
            router = AKS("Enrutador Multinube\nAKS + Functions")
            schema = StorageAccounts("Esquemas\nBlob + Function")
            iam = ActiveDirectory("Entra ID (PLT-02)\n+ IAM AWS/GCP")

        with Cluster("Cloud AWS (EEUU)"):
            bus_aws = Eventbridge("PLT-03-AWS\nEventBridge")
            app15 = Fargate("APP-15\nECS + Kinesis")
            s3 = S3("APP-16 S3")

        with Cluster("Cloud GCP (EEUU)"):
            bus_gcp = Pubsub("PLT-03-GCP\nPub/Sub")
            ml = Run("APP-24\nCloud Run ML")

        with Cluster("PLT-01 — Observabilidad nativa"):
            obs_az = LogAnalyticsWorkspaces("Azure Monitor\n+ App Insights")
            obs_aws = Cloudwatch("Amazon CloudWatch")
            obs_gcp = Logging("GCP Cloud Logging")

        with Cluster("Cloud SaaS (EEUU)"):
            portal = Saas("Portal B2B (APP-18)")

        cliente >> api_gw >> orq >> bus_az
        wms >> bus_az
        tms >> Edge(label="subscribe") >> bus_az
        conductor >> app15 >> bus_aws
        app15 >> s3
        bus_az >> Edge(color="#0078d4") >> router
        bus_aws >> Edge(color="#ff9900") >> router
        schema >> Edge(label="valida", style="dashed") >> router
        router >> Edge(color="#4285f4") >> bus_gcp >> ml
        router >> Edge(label="webhook") >> portal
        obs_az >> Edge(style="dashed") >> router
        obs_aws >> Edge(style="dashed") >> app15
        obs_gcp >> Edge(style="dashed") >> ml


def alt_b_components_router() -> None:
    with _diagram("alt-b-c4-components-router", "TB"):
        bus_az = EventHubs("Azure Event Hubs\nPLT-03-AZ")
        bus_aws = Eventbridge("Amazon EventBridge\nPLT-03-AWS")
        bus_gcp = Pubsub("Google Pub/Sub\nPLT-03-GCP")
        schema = StorageAccounts("Esquemas\nBlob + Function")

        with Cluster("Enrutador de Eventos — AKS + Functions"):
            ingress_az = FunctionApps("Adaptador\nEvent Hubs")
            ingress_aws = FunctionApps("Adaptador\nEventBridge")
            translator = AppServices("Traductor Canónico\n.NET v1")
            dedup = CacheForRedis("Deduplicador\nAzure Redis Cache")
            egress_gcp = FunctionApps("Publicador\nPub/Sub")
            egress_portal = AppServices("Dispatcher\nwebhooks APP-18")
            dlq = SQS("Dead Letter Queue\nSQS + Storage Queue")

        bus_az >> ingress_az >> translator
        bus_aws >> ingress_aws >> translator
        schema >> Edge(label="validate", style="dashed") >> translator
        translator >> dedup
        dedup >> egress_gcp >> bus_gcp
        dedup >> egress_portal
        translator >> Edge(label="on failure", color="#dc2626") >> dlq


def alt_b_components_wms() -> None:
    with _diagram("alt-b-c4-components-wms", "LR"):
        with Cluster("WMS Cloud — Azure AKS"):
            reserva = AppServices("Servicio Reserva")
            picking = AppServices("Servicio Picking")
            reconciliador = AppServices("Reconciliador CD")
            local_pub = EventHubs("Publicador\nsolo bus_az")

        bus_az = EventHubs("PLT-03-AZ\nEvent Hubs Standard")
        router = AKS("Enrutador\nMultinube")
        tms = AKS("TMS (APP-11)")

        reserva >> local_pub
        picking >> local_pub
        reconciliador >> local_pub
        local_pub >> bus_az >> router >> tms


def alt_b_components_app15() -> None:
    with _diagram("alt-b-c4-components-app15", "LR"):
        with Cluster("App Conductores — Mobile (INI-03)"):
            ui = Mobile("UI Entrega\nFlutter/RN")
            offline = PostgreSQL("SQLite AES-256\ncola offline")
            taxonomy = AppServices("Taxonomía\nexcepciones")

        with Cluster("Backend AWS — ECS Fargate"):
            api = Fargate("API Entrega\nREST sync")
            sync = Fargate("Sync Atómico\nidempotencia")
            kin_prod = KinesisDataStreams("Productor\nKinesis SDK")

        s3 = S3("APP-16 S3\nevidencias")
        kinesis = KinesisDataStreams("Kinesis\nData Streams")
        rule = Eventbridge("Regla nativa\nKinesis → EventBridge")
        bus_aws = Eventbridge("PLT-03-AWS\nEventBridge")
        router = FunctionApps("Adaptador\nEnrutador Azure")

        ui >> Edge(label="guarda") >> offline
        ui >> Edge(label="valida") >> taxonomy
        ui >> Edge(label="sync online") >> api
        api >> Edge(label="batch") >> sync
        sync >> Edge(label="PUT atómico") >> s3
        sync >> Edge(label="emit") >> kin_prod
        kin_prod >> Edge(label="PutRecord") >> kinesis
        kinesis >> Edge(label="stream") >> rule
        rule >> Edge(label="PutEvents") >> bus_aws
        bus_aws >> Edge(label="forward", color="#ff9900") >> router


DIAGRAMS = {
    "alt-a-context": alt_a_context,
    "alt-a-containers": alt_a_containers,
    "alt-a-components-wms-bus": alt_a_components_wms_bus,
    "alt-a-components-app15": alt_a_components_app15,
    "alt-b-context": alt_b_context,
    "alt-b-containers": alt_b_containers,
    "alt-b-components-router": alt_b_components_router,
    "alt-b-components-wms": alt_b_components_wms,
    "alt-b-components-app15": alt_b_components_app15,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera diagramas C4 Hito 2 (diagrams/mingrammer)")
    parser.add_argument(
        "--only",
        choices=list(DIAGRAMS.keys()),
        help="Generar un solo diagrama",
    )
    args = parser.parse_args()

    targets = [args.only] if args.only else list(DIAGRAMS.keys())
    print(f"Salida: {OUT_DIR}")
    for key in targets:
        print(f"  -> {key}.png")
        DIAGRAMS[key]()

    print("Listo.")


if __name__ == "__main__":
    main()
