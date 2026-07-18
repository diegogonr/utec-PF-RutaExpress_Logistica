#!/usr/bin/env python3
"""
Genera diagramas C4 de la Alternativa B (Hito 2) con la libreria diagrams (mingrammer).
Estilo alineado a HITO 3: generar_diagramas_mvp_c4.py

Alternativa B = Orquestacion + Monolito Modular
  - Nucleo Logistico Modular (APP-02 OMS + Inventario) en AKS
  - Saga orquestada con Durable Functions
  - API-first sincrono; eventos solo como notificacion (sin PLT-03 completo)
  - AWS ultima milla / evidencias; GCP analitica

Convencion de etiquetas en cada caja (3 lineas):
  1. Nombre del servicio cloud (proveedor)
  2. Nombre oficial (aplicacion / modulo / plataforma)
  3. Identificador (APP-XX, PLT-XX) o rol

Requiere: pip install diagrams graphviz  +  Graphviz (dot) en el PATH del SO.

Salida: diagramas_c4/imagenes_alternativa_B/*.png

Uso:
  python generar_diagramas_alternativa_B_c4.py
  python generar_diagramas_alternativa_B_c4.py --only n2
"""

from __future__ import annotations

import argparse
from pathlib import Path

from diagrams import Cluster, Diagram, Edge
from diagrams.aws.compute import ECS
from diagrams.aws.database import Dynamodb
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
from diagrams.generic.blank import Blank
from diagrams.generic.device import Mobile
from diagrams.onprem.client import User, Users
from diagrams.saas import Saas

BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "imagenes_alternativa_B"

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
    """C4 N1: alcance funcional; el estilo orquestacion se detalla en N2."""
    _ensure_out()
    with Diagram(
        "C4 N1 - Contexto Alternativa B (Orquestacion + Monolito Modular)",
        filename=str(OUT_DIR / "alternativa_B_c4_n1_contexto"),
        show=False,
        direction="TB",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
    ):
        cliente = User(lbl("Actor", "Cliente B2B", "Persona"))
        conductor = Mobile(
            lbl("Dispositivo movil", "App de Conductores", "APP-15")
        )
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

        wms = Saas(
            lbl("On Premises", "WMS Principal / Satelite", "APP-06 / APP-07")
        )
        erp = Saas(
            lbl("On Premises", "ERP Financiero", "APP-25")
        )
        portal = Saas(
            lbl("SaaS", "Portal B2B / CRM", "APP-18 / APP-20")
        )
        tms = Saas(
            lbl("Azure / SaaS", "TMS Transportation Management", "APP-11")
        )

        cliente >> Edge(label="HTTPS API\nPOST orden / GET tracking") >> plataforma
        conductor >> Edge(label="HTTPS movil\nentrega / evidencias") >> plataforma
        ops >> Edge(label="HTTPS monitoreo\nSLA / excepciones") >> plataforma
        finanzas >> Edge(label="HTTPS consulta\nevidencias / estados") >> plataforma
        plataforma >> Edge(label="HTTPS sync\nreserva / picking") >> wms
        plataforma >> Edge(label="HTTPS sync\nvalorizacion") >> erp
        plataforma >> Edge(label="HTTPS / notificacion\ntrazabilidad") >> portal
        plataforma >> Edge(label="HTTPS / notificacion\ndespacho") >> tms


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
        core >> Edge(label="notificacion\nestado orden") >> notif
        orch >> Edge(label="notificacion\nresultado saga") >> notif
        notif >> Edge(label="fan-out") >> mock_portal
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


def n3_nucleo() -> None:
    """C4 N3: componentes del Nucleo Logistico Modular (contenedor en foco).

    Incluye capas de seguridad de aplicacion y limites transaccionales
    (Unit of Work local vs Saga orquestada hacia WMS/ERP).
    """
    _ensure_out()
    with Diagram(
        "C4 N3 - Componentes Nucleo Logistico Modular (APP-02)",
        filename=str(OUT_DIR / "alternativa_B_c4_n3_nucleo_componentes"),
        show=False,
        direction="TB",
        graph_attr={**GRAPH_ATTR, "ranksep": "1.0", "nodesep": "0.75"},
        node_attr=NODE_ATTR,
    ):
        with Cluster("Colaboradores (contenedores externos)"):
            apim = APIManagement(
                lbl("Azure API Management", "Gateway y Gobierno API", "APP-01")
            )
            orch = FunctionApps(
                lbl(
                    "Durable Functions",
                    "Orquestador de Procesos",
                    "Saga runtime",
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
                lbl("Canal legado", "CSV / Excel / S3 historico", "transicional")
            )
            kv = KeyVaults(
                lbl("Key Vault", "Identidad y secretos", "PLT-02")
            )

        with Cluster("CONTENEDOR EN FOCO: Nucleo Logistico Modular (APP-02) — AKS"):
            with Cluster("Capa API"):
                facade = AKS(
                    lbl("AKS pod", "Command API Facade", "APP-02")
                )
                query = AKS(
                    lbl("AKS pod", "Query API", "APP-02")
                )
            with Cluster("Seguridad de aplicacion"):
                authz = AKS(
                    lbl("AKS pod", "AuthZ / Claims Middleware", "APP-02")
                )
                secrets = AKS(
                    lbl("AKS pod", "Secrets Client", "APP-02 → PLT-02")
                )
                corr = AKS(
                    lbl("AKS pod", "Correlation Middleware", "APP-02")
                )
            with Cluster("Dominio DDD"):
                valid = AKS(
                    lbl("AKS pod", "Validation and Dedup", "APP-02")
                )
                order = AKS(
                    lbl("AKS pod", "Order Lifecycle Module", "APP-02")
                )
                inv = AKS(
                    lbl("AKS pod", "Inventory and Reservation", "APP-02")
                )
                idem = AKS(
                    lbl("AKS pod", "Idempotency Guard", "APP-02")
                )
            with Cluster("Aplicacion"):
                create = AKS(
                    lbl("AKS pod", "Create Order Handler", "APP-02")
                )
                comp = AKS(
                    lbl("AKS pod", "Compensation Manager", "APP-02")
                )
            with Cluster("Integracion"):
                acl = AKS(
                    lbl("AKS pod", "External ACL Gateway", "APP-02")
                )
                cb = AKS(
                    lbl("AKS pod", "Circuit Breaker / Throttle", "APP-02")
                )
                notif_pub = AKS(
                    lbl("AKS pod", "Notification Publisher", "APP-02")
                )
            with Cluster("Infraestructura transaccional"):
                uow = AKS(
                    lbl(
                        "AKS pod",
                        "Unit of Work / TX Boundary",
                        "TX local Azure SQL",
                    )
                )
                repo = SQLManagedInstances(
                    lbl("Azure SQL", "Order + Inventory Repository", "APP-02")
                )
                outbox = SQLManagedInstances(
                    lbl(
                        "Azure SQL",
                        "Notification Outbox",
                        "post-commit fan-out",
                    )
                )
                audit = StorageAccounts(
                    lbl("Azure Storage", "Audit Store", "correlation ID")
                )

        with Cluster("Sistemas / contenedores de salida"):
            wms = Saas(
                lbl("ACL / API", "WMS Principal (On Premises)", "APP-06")
            )
            erp = Saas(
                lbl("ACL / API", "ERP Financiero (On Premises)", "APP-25")
            )
            tms = Saas(
                lbl("Notificacion / API", "TMS Transportation Mgmt", "APP-11")
            )
            portal = Saas(
                lbl("Notificacion / API", "Portal B2B / CRM", "APP-18 / APP-20")
            )
            notif = ServiceBus(
                lbl(
                    "Service Bus topics",
                    "Canal de notificaciones",
                    "fan-out informativo",
                )
            )
            obs = LogAnalyticsWorkspaces(
                lbl(
                    "Azure Monitor",
                    "Plataforma Observabilidad Unificada",
                    "PLT-01",
                )
            )
            ops = Users(lbl("Actor", "Operaciones / Soporte", "Persona"))

        # Entrada
        apim >> Edge(label="HTTPS API\nPOST /orders") >> facade
        mobile >> Edge(label="HTTPS API\nDeliveryConfirmed") >> facade
        legado >> Edge(label="BulkOrder") >> facade

        # Seguridad de aplicacion (pipeline de entrada)
        facade >> authz >> corr >> create
        secrets >> Edge(label="lee secretos") >> kv
        acl >> secrets

        # Dominio dentro de TX local
        create >> valid >> idem
        create >> Edge(label="TX local\ncommit/rollback") >> uow
        uow >> order
        uow >> inv
        uow >> repo
        uow >> Edge(label="escribe outbox\nmisma TX") >> outbox

        # Saga orquestada: fuera de la TX local
        facade >> Edge(label="dispara") >> orch
        orch >> Edge(label="pasos saga\nfuera de TX local") >> order
        orch >> Edge(label="pasos saga\nfuera de TX local") >> inv
        orch >> Edge(label="compensa") >> comp
        comp >> inv
        comp >> order

        # Integracion externa (no participa de TX local)
        inv >> acl >> cb
        order >> acl
        cb >> Edge(label="HTTPS sync") >> wms
        cb >> Edge(label="HTTPS sync") >> erp

        # Notificaciones post-commit
        outbox >> Edge(label="relay post-commit") >> notif_pub >> notif
        notif >> portal
        notif >> tms

        # Auditoria y lectura
        corr >> audit
        order >> audit
        audit >> obs
        ops >> Edge(label="HTTPS GET\nestado orden") >> query >> repo


JOBS = {
    "n1": n1_contexto,
    "n2": n2_contenedores,
    "n3-nucleo": n3_nucleo,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera diagramas C4 Alternativa B (orquestacion + monolito modular)"
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
