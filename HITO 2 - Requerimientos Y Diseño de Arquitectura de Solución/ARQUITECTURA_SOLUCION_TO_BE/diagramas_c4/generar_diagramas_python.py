#!/usr/bin/env python3
"""
Genera diagramas de arquitectura con la libreria diagrams (mingrammer)
para los 3 primeros niveles del C4 Model:

- Nivel 1: Contexto, un unico sistema en alcance.
- Nivel 2: Contenedores, aplicaciones/data stores dentro del sistema.
- Nivel 3: Componentes, un unico contenedor en foco.

Salida:
  imagenes_python_graphviz/*.png   → solo Alternativa B
  alternativa_A_*.png           → Alternativa A (en diagramas_c4/)

Uso:
  python generar_diagramas_python.py
  python generar_diagramas_python.py --only alternativa-b-n2
"""

from __future__ import annotations

import argparse
from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import Fargate
from diagrams.aws.integration import SQS
from diagrams.aws.storage import S3
from diagrams.azure.analytics import EventHubs, LogAnalyticsWorkspaces
from diagrams.azure.compute import AKS, FunctionApps
from diagrams.azure.database import CacheForRedis, SQLManagedInstances
from diagrams.azure.identity import ActiveDirectory
from diagrams.azure.integration import APIManagement, ServiceBus
from diagrams.onprem.container import Docker
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
# Preferir cwd al generar (evita corrupción de Unicode en __file__ bajo Windows/PowerShell)
OUT_DIR = (Path.cwd() / "imagenes_python_graphviz").resolve()
if not (Path.cwd() / "generar_diagramas_python.py").exists():
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


def _repo_root() -> Path:
    here = Path(__file__).resolve().parent
    for cand in [here, *here.parents]:
        if (cand / "sync_diagramas_alternativa_A.py").is_file() and (cand / "Implementacion").is_dir():
            return cand
    return Path(__file__).resolve().parents[3]


def _sync_alternativa_a_images() -> None:
    """Alternativa A usa las PNG canónicas en diagramas_c4/alternativa_A_*.png."""
    import runpy

    script = _repo_root() / "sync_diagramas_alternativa_A.py"
    runpy.run_path(str(script), run_name="__main__")


def _diagram(name: str, direction: str = "TB") -> Diagram:
    """Render en imagenes_python_graphviz (Modelo B y utilidades)."""
    import shutil

    here = Path(__file__).resolve().parent
    ascii_out = _repo_root() / "_c4_gen_tmp"
    ascii_out.mkdir(parents=True, exist_ok=True)
    final_out = here / "imagenes_python_graphviz"
    final_out.mkdir(parents=True, exist_ok=True)
    tmp_file = ascii_out / name

    class _CopyOnExit(Diagram):
        def __exit__(self, *args):
            result = super().__exit__(*args)
            for src in ascii_out.glob(f"{name}.*"):
                try:
                    shutil.copy2(src, final_out / src.name)
                except OSError:
                    shutil.copy2(src, ascii_out / f"OK_{src.name}")
            return result

    return _CopyOnExit(
        name,
        filename=str(tmp_file),
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
    """PNG oficial en diagramas_c4/alternativa_A_*.png."""
    _sync_alternativa_a_images()


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
            "Alt B: orquestacion +\nmonolito modular"
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
    """PNG oficial en diagramas_c4/alternativa_A_*.png."""
    _sync_alternativa_a_images()



def alternativa_b_n2_contenedores() -> None:
    """C4 Contenedores: monolito modular + orquestador; eventos solo como notificacion."""
    with _diagram("alternativa_B_n2_contenedores", "LR"):
        cliente = Users("Cliente B2B")
        app = Mobile("App Conductores\nAPP-15")
        ops = User("Operacion / Soporte")

        with Cluster("Sistema en alcance: Plataforma Logistica RutaExpress TO BE"):
            with Cluster("Azure"):
                apim = APIManagement("Gateway y Gobierno API\nAzure API Management (APP-01)")
                core = AKS("Nucleo Logistico Modular\nAPP-02 OMS + Inventario")
                orch = FunctionApps("Orquestador de Procesos\nDurable Functions")
                sql = SQLManagedInstances("Repositorio transaccional\nAzure SQL")
                notif = EventHubs("Canal notificaciones\nService Bus topics")
                acl = AKS("Adaptadores ACL\nWMS / TMS / ERP")
                az_obs = LogAnalyticsWorkspaces("Observabilidad\nPlataforma de Observabilidad Unificada (PLT-01)")
                az_iam = ActiveDirectory("Identidad y secretos\nEntra ID + Key Vault")

            with Cluster("AWS"):
                mobile_backend = Fargate("Backend movil\nECS/Lambda")
                mobile_db = PostgreSQL("DynamoDB logico\nsync movil")
                s3 = S3("Repositorio evidencias\nS3 + KMS APP-16")

            with Cluster("GCP"):
                pubsub = Pubsub("Canal analitico\nPub/Sub")
                optimizer = Run("Optimizador dinamico\nCloud Run/GKE")
                streaming = Run("Procesamiento analitico\nDataflow")
                bigquery = StorageAccounts("Repositorio analitico\nBigQuery")
                ml = Run("Prediccion riesgo\nVertex AI")

        with Cluster("Sistemas externos"):
            wms = Server("WMS Principal (On Premises) (APP-06) APP-06 / APP-07")
            erp = Server("ERP Financiero (On Premises) (APP-25) APP-25")
            tms = Server("TMS (Transportation Management) (APP-11) APP-11")
            portal = Saas("Portal B2B / CRM")
            legacy = StorageAccounts("Canales legados")

        cliente >> apim >> core
        app >> mobile_backend
        ops >> az_obs
        core >> sql
        core >> orch
        orch >> core
        orch >> acl
        acl >> wms
        acl >> erp
        acl >> tms
        core >> notif
        orch >> notif
        notif >> portal
        notif >> mobile_backend
        notif >> pubsub
        mobile_backend >> mobile_db
        mobile_backend >> s3
        mobile_backend >> _edge("confirmacion API", EDGE_ORANGE, minlen=2) >> apim
        pubsub >> optimizer
        pubsub >> streaming >> bigquery >> ml
        optimizer >> acl
        legacy >> apim
        az_iam >> _edge(style="dashed", minlen=1, constraint=False) >> apim
        az_iam >> _edge(style="dashed", minlen=1, constraint=False) >> core
        az_obs >> _edge(style="dashed", minlen=1, constraint=False) >> core
        az_obs >> _edge(style="dashed", minlen=1, constraint=False) >> orch
        az_obs >> _edge(style="dashed", minlen=1, constraint=False) >> mobile_backend


def alternativa_a_n3_componentes() -> None:
    """PNG oficial en diagramas_c4/alternativa_A_*.png."""
    _sync_alternativa_a_images()



def alternativa_b_n3_componentes() -> None:
    """C4 Componentes: zoom al Nucleo Logistico Modular (APP-02)."""
    with _diagram("alternativa_B_n3_componentes", "TB"):
        with Cluster("Contenedores colaboradores"):
            apim = APIManagement("Gateway API\nAzure API Management (APP-01)")
            orch_rt = FunctionApps("Runtime Orquestador\nDurable Functions")
            mobile = Fargate("Backend movil\nAWS")
            legacy = StorageAccounts("Adaptadores legados")

        with Cluster("Contenedor en foco: Nucleo Logistico Modular APP-02"):
            facade = AppServices("Command API Facade")
            valid = FunctionApps("Validation and Dedup")
            order = AKS("Order Lifecycle Module")
            inv = AKS("Inventory and Reservation")
            comp = FunctionApps("Compensation Manager")
            acl = AppServices("External ACL Gateway")
            notif = EventHubs("Notification Publisher")
            audit = StorageAccounts("Audit Store")

        with Cluster("Sistemas / contenedores de salida"):
            wms = Server("WMS APP-06 / APP-07")
            erp = Server("ERP APP-25")
            tms = AKS("Adaptador TMS APP-11")
            portal = Saas("Portal B2B / CRM")
            obs = LogAnalyticsWorkspaces("Observabilidad\nPlataforma de Observabilidad Unificada (PLT-01)")
            iam = ActiveDirectory("Identidad / secretos\nPlataforma de Identidad y Accesos (IAM) (PLT-02)")

        apim >> _edge("CreateOrder") >> facade
        mobile >> _edge("DeliveryConfirmed") >> facade
        legacy >> _edge("BulkOrder") >> facade
        facade >> valid >> order >> inv
        facade >> orch_rt
        orch_rt >> order
        orch_rt >> inv
        orch_rt >> comp
        comp >> inv
        comp >> order
        inv >> acl
        order >> acl
        acl >> wms
        acl >> erp
        acl >> tms
        order >> notif
        inv >> notif
        comp >> notif
        notif >> portal
        notif >> mobile
        valid >> audit
        order >> audit
        inv >> audit
        audit >> obs
        iam >> _edge(style="dashed", minlen=1, constraint=False) >> facade
        iam >> _edge(style="dashed", minlen=1, constraint=False) >> acl


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

    alt_a = [k for k in targets if k.startswith("alternativa-a-")]
    alt_rest = [k for k in targets if not k.startswith("alternativa-a-")]
    if alt_a:
        print("Alternativa A -> diagramas_c4/alternativa_A_*.png")
        _sync_alternativa_a_images()
    if alt_rest:
        print(f"Salida: {OUT_DIR}")
        for key in alt_rest:
            print(f"  -> {key}.png")
            DIAGRAMS[key]()

    print("Listo.")


if __name__ == "__main__":
    main()
