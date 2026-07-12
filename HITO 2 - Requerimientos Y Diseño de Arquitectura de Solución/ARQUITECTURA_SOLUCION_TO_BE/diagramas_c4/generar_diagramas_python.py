#!/usr/bin/env python3
"""
Genera diagramas de arquitectura con la libreria diagrams (mingrammer)
para los 3 primeros niveles del C4 Model:

- Nivel 1: Contexto, un unico sistema en alcance.
- Nivel 2: Contenedores, aplicaciones/data stores dentro del sistema.
- Nivel 3: Componentes, un unico contenedor en foco.

Salida:
  imagenes_python_graphviz/*.png

Uso:
  python generar_diagramas_python.py
  python generar_diagramas_python.py --only alternativa-a-n1
"""

from __future__ import annotations

import argparse
from pathlib import Path

from diagrams import Cluster, Diagram, Edge
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
OUT_DIR = BASE_DIR / "imagenes_python_graphviz"

SOURCE_MARKDOWNS = {
    "alternativa-a-n1": BASE_DIR / "alternativa_A_n1_contexto.md",
    "alternativa-a-n2": BASE_DIR / "alternativa_A_n2_contenedores.md",
    "alternativa-a-n3": BASE_DIR / "alternativa_A_n3_componentes.md",
    "alternativa-b-n1": BASE_DIR / "alternativa_B_n1_contexto.md",
    "alternativa-b-n2": BASE_DIR / "alternativa_B_n2_contenedores.md",
    "alternativa-b-n3": BASE_DIR / "alternativa_B_n3_componentes.md",
}

GRAPH_ATTR = {
    "fontsize": "18",
    "fontname": "Segoe UI",
    "bgcolor": "white",
    "pad": "0.75",
    "nodesep": "1.05",
    "ranksep": "1.55",
    "dpi": "220",
    "compound": "true",
    "splines": "ortho",
    "overlap": "false",
    "outputorder": "edgesfirst",
    "forcelabels": "true",
}

NODE_ATTR = {
    "fontsize": "13",
    "fontname": "Segoe UI",
}

EDGE_BLUE = "#2563eb"
EDGE_PURPLE = "#7c3aed"
EDGE_GRAY = "#64748b"
EDGE_ORANGE = "#f97316"
EDGE_RED = "#dc2626"

EDGE_ATTR = {
    "fontname": "Segoe UI",
    "fontsize": "10",
    "labelfontsize": "10",
    "arrowsize": "0.75",
    "penwidth": "1.7",
}


def _validate_sources(targets: list[str]) -> None:
    missing = [str(SOURCE_MARKDOWNS[key]) for key in targets if not SOURCE_MARKDOWNS[key].exists()]
    if missing:
        raise FileNotFoundError("No se encontraron fuentes Markdown: " + ", ".join(missing))


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


def _edge(
    label: str = "",
    color: str = EDGE_GRAY,
    style: str = "solid",
    minlen: int = 2,
    constraint: bool = True,
) -> Edge:
    attrs = dict(EDGE_ATTR)
    attrs["minlen"] = str(minlen)
    attrs["constraint"] = "true" if constraint else "false"
    if label:
        # xlabel deja que Graphviz ubique el texto fuera del trazo ortogonal.
        attrs["xlabel"] = label
    return Edge(color=color, style=style, **attrs)


def alternativa_a_n1_contexto() -> None:
    """C4 Contexto: un unico sistema central, personas y sistemas externos."""
    with _diagram("alternativa_A_n1_contexto", "TB"):
        with Cluster("Personas"):
            cliente = Users("Cliente B2B / Retail\nordenes y trazabilidad")
            conductor = User("Conductor\nentregas y evidencias")
            operador = User("Operacion RutaExpress\nSLA y excepciones")
            finanzas = User("Finanzas\nconciliacion")

        sistema = Server(
            "Plataforma Logistica\nRutaExpress TO BE\n"
            "Alt A: gobierno e integracion centralizados"
        )

        with Cluster("Sistemas externos"):
            wms = Server("WMS Principal (On Premises) (APP-06) APP-06 / APP-07")
            tms = Server("TMS (Transportation Management) (APP-11) APP-11")
            erp = Server("ERP Financiero (On Premises) (APP-25) APP-25")
            portal = Saas("Portal B2B / CRM")
            legados = StorageAccounts("Clientes SaaS\ncanales legados")
            mapas = Saas("Trafico / mapas")

        cliente >> _edge("crea ordenes / consulta", EDGE_BLUE) >> sistema
        conductor >> _edge("entregas / tracking", EDGE_BLUE) >> sistema
        operador >> _edge("gestion operativa", EDGE_PURPLE) >> sistema
        finanzas >> _edge("soportes liquidacion", EDGE_GRAY) >> sistema

        sistema >> _edge("inventario") >> wms
        sistema >> _edge("despacho / rutas") >> tms
        sistema >> _edge("valorizacion") >> erp
        sistema >> _edge("trazabilidad") >> portal
        legados >> _edge("ordenes / archivos") >> sistema
        sistema >> _edge("ETA / trafico") >> mapas


def alternativa_b_n1_contexto() -> None:
    """C4 Contexto: un unico sistema central, personas y sistemas externos."""
    with _diagram("alternativa_B_n1_contexto", "TB"):
        with Cluster("Personas"):
            cliente = Users("Cliente B2B / Retail\nordenes y trazabilidad")
            conductor = User("Conductor\nentregas y evidencias")
            operador = User("Operacion RutaExpress\nSLA y excepciones")
            finanzas = User("Finanzas\nconciliacion")

        sistema = Server(
            "Plataforma Logistica\nRutaExpress TO BE\n"
            "Alt B: eventos y ultima milla priorizados"
        )

        with Cluster("Sistemas externos"):
            wms = Server("WMS Principal (On Premises) (APP-06) APP-06 / APP-07")
            tms = Server("TMS (Transportation Management) (APP-11) APP-11")
            erp = Server("ERP Financiero (On Premises) (APP-25) APP-25")
            portal = Saas("Portal B2B / CRM")
            legados = StorageAccounts("Clientes SaaS\ncanales legados")
            mapas = Saas("Trafico / mapas")

        cliente >> _edge("crea ordenes / consulta", EDGE_BLUE) >> sistema
        conductor >> _edge("entregas / tracking", EDGE_BLUE) >> sistema
        operador >> _edge("gestion operativa", EDGE_PURPLE) >> sistema
        finanzas >> _edge("soportes liquidacion", EDGE_GRAY) >> sistema

        sistema >> _edge("inventario") >> wms
        sistema >> _edge("despacho / rutas") >> tms
        sistema >> _edge("valorizacion") >> erp
        sistema >> _edge("trazabilidad") >> portal
        legados >> _edge("ordenes / archivos") >> sistema
        sistema >> _edge("ETA / trafico") >> mapas


def alternativa_a_n2_contenedores() -> None:
    """C4 Contenedores: aplicaciones y data stores dentro del sistema en alcance."""
    with _diagram("alternativa_A_n2_contenedores", "LR"):
        cliente = Users("Cliente B2B")
        app = Mobile("App Conductores\nAPP-15")
        ops = User("Operacion / Soporte")

        with Cluster("Sistema en alcance: Plataforma Logistica RutaExpress TO BE"):
            with Cluster("Azure"):
                apim = APIManagement("Gateway y Gobierno API\nAzure API Management (APP-01)")
                oms = AKS("OMS centralizado\nAPP-02 sobre AKS")
                inv = AKS("Inventario y Reservas\nAKS")
                sql = SQLManagedInstances("Repositorio transaccional\nAzure SQL")
                bus = EventHubs("Bus de Eventos Central\nBus de Eventos Central (PLT-03) Event Hubs")
                colas = EventHubs("Colas, DLQ y Replay\nAzure Service Bus")
                tms_adapter = AKS("Adaptador TMS (Transportation Management) (APP-11)\nAPP-11")
                obs = LogAnalyticsWorkspaces("Observabilidad unificada\nPlataforma de Observabilidad Unificada (PLT-01)")
                iam = ActiveDirectory("Identidad y secretos\nPlataforma de Identidad y Accesos (IAM) (PLT-02)")

            with Cluster("AWS"):
                mobile_backend = Fargate("Backend movil\nECS/Lambda")
                mobile_db = PostgreSQL("DynamoDB logico\nsync movil")
                s3 = S3("Repositorio evidencias\nS3 + KMS APP-16")
                aws_buffer = SQS("Buffer movil\nSQS/EventBridge")

            with Cluster("GCP"):
                pubsub = Pubsub("Canal analitico\nPub/Sub")
                optimizer = Run("Optimizador dinamico\nCloud Run/GKE")
                streaming = Run("Procesamiento analitico\nDataflow")
                bigquery = StorageAccounts("Repositorio analitico\nBigQuery")
                ml = Run("Prediccion riesgo\nVertex AI")

        with Cluster("Sistemas externos"):
            wms = Server("WMS Principal (On Premises) (APP-06) APP-06 / APP-07")
            erp = Server("ERP Financiero (On Premises) (APP-25) APP-25")
            portal = Saas("Portal B2B / CRM")
            legacy = StorageAccounts("Canales legados")

        cliente >> apim >> oms
        app >> mobile_backend
        ops >> obs
        oms >> sql
        oms >> inv
        inv >> sql
        oms >> bus
        inv >> bus
        bus >> colas
        colas >> tms_adapter
        colas >> mobile_backend
        mobile_backend >> mobile_db
        mobile_backend >> s3
        mobile_backend >> aws_buffer
        aws_buffer >> _edge("bridge", EDGE_ORANGE, minlen=3) >> bus
        bus >> pubsub
        pubsub >> optimizer
        pubsub >> streaming >> bigquery >> ml
        optimizer >> tms_adapter
        inv >> wms
        inv >> erp
        colas >> portal
        legacy >> colas
        iam >> _edge(style="dashed", minlen=1, constraint=False) >> apim
        iam >> _edge(style="dashed", minlen=1, constraint=False) >> oms
        obs >> _edge(style="dashed", minlen=1, constraint=False) >> bus
        obs >> _edge(style="dashed", minlen=1, constraint=False) >> mobile_backend
        obs >> _edge(style="dashed", minlen=1, constraint=False) >> optimizer


def alternativa_b_n2_contenedores() -> None:
    """C4 Contenedores: aplicaciones y data stores dentro del sistema en alcance."""
    with _diagram("alternativa_B_n2_contenedores", "LR"):
        cliente = Users("Cliente B2B")
        app = Mobile("App Conductores\nAPP-15")
        ops = User("Operacion / Soporte")

        with Cluster("Sistema en alcance: Plataforma Logistica RutaExpress TO BE"):
            with Cluster("Azure"):
                apim = APIManagement("Gateway y Gobierno API\nAzure API Management (APP-01)")
                oms = AKS("OMS centralizado / Orquestador de Pedidos (APP-02) e Inventario\nAPP-02 sobre AKS")
                sql = SQLManagedInstances("Repositorio transaccional\nAzure SQL")
                tms_adapter = AKS("Adaptador TMS (Transportation Management) (APP-11)\nAPP-11")
                az_obs = LogAnalyticsWorkspaces("Telemetria Azure")
                az_iam = ActiveDirectory("Identidad y secretos\nEntra ID + Key Vault")

            with Cluster("AWS"):
                event_hub = Eventbridge("Hub principal eventos\nEventBridge Bus de Eventos Central (PLT-03)")
                queues = SQS("Colas, DLQ y Replay\nSQS + workers")
                adapters = Fargate("Adaptadores y validadores\nLambda/ECS")
                mobile_backend = Fargate("Backend movil\nECS/Lambda")
                mobile_db = PostgreSQL("DynamoDB logico\nsync movil")
                s3 = S3("Repositorio evidencias\nS3 + KMS APP-16")
                aws_obs = Cloudwatch("Telemetria AWS\nCloudWatch/X-Ray")
                aws_iam = StorageAccounts("Secretos y roles\nSecrets Manager/IAM")

            with Cluster("GCP"):
                pubsub = Pubsub("Canal analitico\nPub/Sub")
                optimizer = Run("Optimizador dinamico\nCloud Run/GKE")
                streaming = Run("Procesamiento analitico\nDataflow")
                bigquery = StorageAccounts("Repositorio analitico\nBigQuery")
                ml = Run("Prediccion riesgo\nVertex AI")

        with Cluster("Sistemas externos"):
            wms = Server("WMS Principal (On Premises) (APP-06) APP-06 / APP-07")
            erp = Server("ERP Financiero (On Premises) (APP-25) APP-25")
            portal = Saas("Portal B2B / CRM")
            legacy = StorageAccounts("Canales legados")

        cliente >> apim >> oms
        app >> mobile_backend
        ops >> az_obs
        ops >> aws_obs
        oms >> sql
        oms >> _edge("bridge Azure-AWS", EDGE_ORANGE, minlen=3) >> event_hub
        oms >> wms
        oms >> erp
        event_hub >> queues >> adapters
        adapters >> tms_adapter
        adapters >> portal
        adapters >> legacy
        mobile_backend >> mobile_db
        mobile_backend >> s3
        mobile_backend >> event_hub
        event_hub >> pubsub
        pubsub >> optimizer
        pubsub >> streaming >> bigquery >> ml
        optimizer >> tms_adapter
        az_iam >> _edge(style="dashed", minlen=1, constraint=False) >> apim
        az_iam >> _edge(style="dashed", minlen=1, constraint=False) >> oms
        aws_iam >> _edge(style="dashed", minlen=1, constraint=False) >> mobile_backend
        aws_iam >> _edge(style="dashed", minlen=1, constraint=False) >> event_hub


def alternativa_a_n3_componentes() -> None:
    """C4 Componentes: zoom a un solo contenedor, Bus de Eventos Central (PLT-03) en Azure."""
    with _diagram("alternativa_A_n3_componentes", "TB"):
        with Cluster("Contenedores productores"):
            oms = AKS("OMS centralizado\nAPP-02")
            inv = AKS("Inventario y Reservas")
            mobile = Fargate("Backend movil\nAWS")
            legacy = StorageAccounts("Adaptadores legados")

        with Cluster("Contenedor en foco: Bus de Eventos Central (PLT-03)"):
            ingestion = AppServices("Event Ingestion API")
            schema = FunctionApps("Schema Validator")
            router = EventHubs("Event Router")
            ordering = CacheForRedis("Ordering Guard")
            retry = FunctionApps("Retry Scheduler")
            dlq = StorageAccounts("DLQ Manager")
            replay = FunctionApps("Replay Controller")
            backpressure = AppServices("Backpressure Controller")
            audit = StorageAccounts("Audit / Event Store")

        with Cluster("Contenedores consumidores"):
            tms = AKS("Adaptador TMS (Transportation Management) (APP-11)\nAPP-11")
            portal = Saas("Portal B2B / CRM")
            optimizer = Run("Optimizador dinamico\nGCP")
            obs = LogAnalyticsWorkspaces("Observabilidad\nPlataforma de Observabilidad Unificada (PLT-01)")
            iam = ActiveDirectory("Identidad / secretos\nPlataforma de Identidad y Accesos (IAM) (PLT-02)")

        oms >> _edge("OrderEvents") >> ingestion
        inv >> _edge("InventoryEvents") >> ingestion
        mobile >> _edge("Tracking/Evidence") >> ingestion
        legacy >> _edge("LegacyNormalized") >> ingestion
        ingestion >> schema >> router >> ordering >> retry
        retry >> tms
        retry >> portal
        retry >> optimizer
        router >> dlq >> replay >> router
        backpressure >> _edge(style="dashed", minlen=1, constraint=False) >> router
        schema >> audit
        router >> audit
        dlq >> audit
        audit >> obs
        iam >> _edge(style="dashed", minlen=1, constraint=False) >> ingestion
        iam >> _edge(style="dashed", minlen=1, constraint=False) >> replay


def alternativa_b_n3_componentes() -> None:
    """C4 Componentes: zoom a un solo contenedor, Bus de Eventos Central (PLT-03) en AWS."""
    with _diagram("alternativa_B_n3_componentes", "TB"):
        with Cluster("Contenedores productores"):
            apim = APIManagement("Gateway API\nAzure")
            oms = AKS("OMS centralizado / Orquestador de Pedidos (APP-02) e Inventario\nAzure AKS")
            mobile = Fargate("Backend movil\nAWS")
            legacy = StorageAccounts("Adaptadores legados")

        with Cluster("Contenedor en foco: Hub principal de eventos Bus de Eventos Central (PLT-03)"):
            ingestion = Eventbridge("Event Ingestion")
            schema = FunctionApps("Schema Lambda")
            rules = Eventbridge("EventBridge Rules")
            queues = SQS("SQS Queues")
            ordering = CacheForRedis("Ordering Guard")
            retry = Fargate("Retry Worker")
            dlq = SQS("DLQ Processor")
            replay = Fargate("Replay Worker")
            throttle = AppServices("Backpressure Controller")
            audit = StorageAccounts("Audit / Event Store")

        with Cluster("Contenedores consumidores"):
            tms = AKS("Adaptador TMS (Transportation Management) (APP-11)\nAPP-11")
            portal = Saas("Portal B2B / CRM")
            optimizer = Run("Optimizador dinamico\nGCP")
            obs = Cloudwatch("Observabilidad federada")
            iam = StorageAccounts("IAM / Secrets Manager")

        apim >> _edge("contratos") >> oms
        oms >> _edge("Order/Inventory") >> ingestion
        mobile >> _edge("Tracking/Evidence") >> ingestion
        legacy >> _edge("LegacyNormalized") >> ingestion
        ingestion >> schema >> rules >> queues >> ordering >> retry
        retry >> tms
        retry >> portal
        retry >> optimizer
        queues >> dlq >> replay >> rules
        throttle >> _edge(style="dashed", minlen=1, constraint=False) >> rules
        schema >> audit
        rules >> audit
        dlq >> audit
        audit >> obs
        iam >> _edge(style="dashed", minlen=1, constraint=False) >> ingestion
        iam >> _edge(style="dashed", minlen=1, constraint=False) >> replay


DIAGRAMS = {
    "alternativa-a-n1": alternativa_a_n1_contexto,
    "alternativa-a-n2": alternativa_a_n2_contenedores,
    "alternativa-a-n3": alternativa_a_n3_componentes,
    "alternativa-b-n1": alternativa_b_n1_contexto,
    "alternativa-b-n2": alternativa_b_n2_contenedores,
    "alternativa-b-n3": alternativa_b_n3_componentes,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera diagramas C4 RutaExpress con diagrams")
    parser.add_argument("--only", choices=list(DIAGRAMS.keys()), help="Generar un solo diagrama")
    args = parser.parse_args()

    targets = [args.only] if args.only else list(DIAGRAMS.keys())
    _validate_sources(targets)

    print(f"Salida: {OUT_DIR}")
    for key in targets:
        print(f"  -> {key}.png")
        DIAGRAMS[key]()

    print("Listo.")


if __name__ == "__main__":
    main()
