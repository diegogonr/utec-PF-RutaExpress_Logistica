#!/usr/bin/env python3
"""
Genera diagramas C4 en SVG usando solo Python estandar.

La salida sigue la semantica oficial de C4:

- Nivel 1 Contexto: un unico sistema en alcance, personas y sistemas externos.
- Nivel 2 Contenedores: aplicaciones/data stores dentro del sistema en alcance.
- Nivel 3 Componentes: zoom a un unico contenedor en foco.

Salida:
  imagenes_python/*.svg
"""

from __future__ import annotations

import argparse
import html
from dataclasses import dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
OUT_DIR = BASE_DIR / "imagenes_python"

SOURCE_MARKDOWNS = {
    "alternativa-a-n1": BASE_DIR / "alternativa_A_n1_contexto.md",
    "alternativa-a-n2": BASE_DIR / "alternativa_A_n2_contenedores.md",
    "alternativa-a-n3": BASE_DIR / "alternativa_A_n3_componentes.md",
    "alternativa-b-n1": BASE_DIR / "alternativa_B_n1_contexto.md",
    "alternativa-b-n2": BASE_DIR / "alternativa_B_n2_contenedores.md",
    "alternativa-b-n3": BASE_DIR / "alternativa_B_n3_componentes.md",
}

COLORS = {
    "actor": ("#f0fdf4", "#16a34a"),
    "system": ("#f8fafc", "#0f172a"),
    "azure": ("#e0f2fe", "#0284c7"),
    "aws": ("#fff7ed", "#ea580c"),
    "gcp": ("#eef2ff", "#4f46e5"),
    "external": ("#f8fafc", "#64748b"),
    "focus": ("#f5f3ff", "#7c3aed"),
}


@dataclass(frozen=True)
class Lane:
    title: str
    kind: str
    nodes: list[tuple[str, str]]


@dataclass(frozen=True)
class DiagramSpec:
    key: str
    title: str
    subtitle: str
    lanes: list[Lane]
    edges: list[tuple[str, str, str]]


def _validate_sources(targets: list[str]) -> None:
    missing = [str(SOURCE_MARKDOWNS[key]) for key in targets if not SOURCE_MARKDOWNS[key].exists()]
    if missing:
        raise FileNotFoundError("No se encontraron fuentes Markdown: " + ", ".join(missing))


def _split_label(label: str) -> list[str]:
    lines: list[str] = []
    for part in label.split("\n"):
        part = part.strip()
        if len(part) <= 28:
            lines.append(part)
            continue
        words = part.split()
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if len(candidate) > 28 and current:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
    return lines[:5]


def _text(x: int, y: int, value: str, size: int = 13, weight: str = "400", color: str = "#0f172a") -> str:
    return (
        f'<text x="{x}" y="{y}" font-family="Segoe UI, Arial, sans-serif" '
        f'font-size="{size}" font-weight="{weight}" fill="{color}">{html.escape(value)}</text>'
    )


def _centered_text(x: int, y: int, width: int, lines: list[str], size: int = 13) -> str:
    start_y = y - (len(lines) - 1) * 8
    parts = []
    for index, line in enumerate(lines):
        parts.append(
            f'<text x="{x + width / 2:.0f}" y="{start_y + index * 17}" '
            'text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" '
            f'font-size="{size}" fill="#0f172a">{html.escape(line)}</text>'
        )
    return "\n".join(parts)


def _node(x: int, y: int, width: int, height: int, label: str, kind: str) -> str:
    fill, stroke = COLORS.get(kind, COLORS["external"])
    lines = _split_label(label)
    return f"""
<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="2"/>
{_centered_text(x, y + height // 2 + 5, width, lines)}
"""


def _overlaps(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def _edge_label_svg(
    center: tuple[int, int],
    label: str,
    used_rects: list[tuple[int, int, int, int]],
    image_size: tuple[int, int],
) -> str:
    if not label:
        return ""

    label = label[:24]
    text_width = max(78, min(184, len(label) * 6 + 22))
    text_height = 22
    cx, cy = center
    max_w, max_h = image_size
    candidates: list[tuple[int, int, int, int]] = []

    for step in range(0, 9):
        for sign in (1, -1):
            y = cy + sign * step * 18
            rect = (
                cx - text_width // 2,
                y - text_height // 2,
                cx + text_width // 2,
                y + text_height // 2,
            )
            if rect[0] < 6 or rect[1] < 6 or rect[2] > max_w - 6 or rect[3] > max_h - 6:
                continue
            candidates.append(rect)

    fallback = (
        cx - text_width // 2,
        cy - text_height // 2,
        cx + text_width // 2,
        cy + text_height // 2,
    )
    rect = candidates[-1] if candidates else fallback
    for candidate in candidates:
        if not any(_overlaps(candidate, used) for used in used_rects):
            rect = candidate
            break

    used_rects.append(rect)
    x1, y1, x2, y2 = rect
    return (
        f'<rect x="{x1}" y="{y1}" width="{x2 - x1}" height="{y2 - y1}" rx="6" '
        'fill="white" stroke="#cbd5e1"/>'
        f'<text x="{(x1 + x2) // 2}" y="{y1 + 15}" text-anchor="middle" '
        'font-family="Segoe UI, Arial, sans-serif" font-size="10" fill="#334155">'
        f"{html.escape(label)}</text>"
    )


def _routed_arrow(
    points: list[tuple[int, int]],
    label: str,
    label_pos: tuple[int, int],
    used_label_rects: list[tuple[int, int, int, int]],
    image_size: tuple[int, int],
) -> str:
    path_parts = [f"M {points[0][0]} {points[0][1]}"]
    path_parts.extend(f"L {x} {y}" for x, y in points[1:])
    label_svg = _edge_label_svg(label_pos, label, used_label_rects, image_size)
    return f"""
<path d="{' '.join(path_parts)}" fill="none" stroke="#475569" stroke-width="2" marker-end="url(#arrow)"/>
{label_svg}
"""


def render(spec: DiagramSpec) -> None:
    lane_width = 300
    lane_gap = 160
    node_width = 242
    node_height = 78
    node_gap = 24
    margin = 42
    lanes_y = 146
    max_nodes = max(len(lane.nodes) for lane in spec.lanes)
    long_edges = [
        edge for edge in spec.edges
        if abs(_lane_index(spec, edge[0]) - _lane_index(spec, edge[1])) > 1
    ]
    bottom_route_band = 46 + max(0, len(long_edges) - 1) * 26
    lane_height = 72 + max_nodes * (node_height + node_gap)
    height = lanes_y + lane_height + bottom_route_band + margin
    width = margin * 2 + len(spec.lanes) * lane_width + (len(spec.lanes) - 1) * lane_gap

    node_pos: dict[str, tuple[int, int, int, int]] = {}
    node_lane: dict[str, int] = {}
    lane_boxes: list[tuple[int, int, int, int]] = []
    body: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        """
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L9,3 z" fill="#475569"/>
  </marker>
  <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
    <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#94a3b8" flood-opacity="0.25"/>
  </filter>
</defs>
""",
        '<rect x="0" y="0" width="100%" height="100%" fill="white"/>',
        _text(margin, 38, spec.title, 22, "700"),
        _text(margin, 66, spec.subtitle, 13, "400", "#475569"),
        _text(margin, 88, f"Fuente: {SOURCE_MARKDOWNS[spec.key].name}", 11, "400", "#64748b"),
    ]

    for lane_index, lane in enumerate(spec.lanes):
        x = margin + lane_index * (lane_width + lane_gap)
        lane_boxes.append((x, lanes_y, x + lane_width, lanes_y + lane_height))
        fill, stroke = COLORS.get(lane.kind, COLORS["external"])
        body.append(
            f'<g filter="url(#shadow)"><rect x="{x}" y="{lanes_y}" width="{lane_width}" height="{lane_height}" '
            f'rx="14" fill="{fill}" stroke="{stroke}" stroke-width="2" opacity="0.72"/></g>'
        )
        body.append(_text(x + 16, lanes_y + 30, lane.title, 14, "700", stroke))
        for node_index, (node_id, label) in enumerate(lane.nodes):
            nx = x + (lane_width - node_width) // 2
            ny = lanes_y + 52 + node_index * (node_height + node_gap)
            node_pos[node_id] = (nx, ny, node_width, node_height)
            node_lane[node_id] = lane_index
            body.append(_node(nx, ny, node_width, node_height, label, lane.kind))

    used_label_rects: list[tuple[int, int, int, int]] = []
    adjacent_gap_counts: dict[tuple[int, int], int] = {}
    same_lane_counts: dict[int, int] = {}
    long_edge_count = 0

    for source, target, label in spec.edges:
        sx, sy, sw, sh = node_pos[source]
        tx, ty, tw, th = node_pos[target]
        source_lane = node_lane[source]
        target_lane = node_lane[target]
        source_mid_y = sy + sh // 2
        target_mid_y = ty + th // 2
        lane_diff = target_lane - source_lane

        if source_lane == target_lane:
            _lane_x1, _lane_y1, lane_x2, _lane_y2 = lane_boxes[source_lane]
            rail_count = same_lane_counts.get(source_lane, 0)
            same_lane_counts[source_lane] = rail_count + 1
            rail_x = lane_x2 - 18 - (rail_count % 3) * 18
            rail_x = max(rail_x, sx + sw + 12)
            points = [
                (sx + sw, source_mid_y),
                (rail_x, source_mid_y),
                (rail_x, target_mid_y),
                (tx + tw, target_mid_y),
            ]
            body.append(
                _routed_arrow(
                    points,
                    label,
                    (rail_x, (source_mid_y + target_mid_y) // 2),
                    used_label_rects,
                    (width, height),
                )
            )
            continue

        if abs(lane_diff) == 1:
            left_lane = min(source_lane, target_lane)
            gap_key = (left_lane, left_lane + 1)
            gap_count = adjacent_gap_counts.get(gap_key, 0)
            adjacent_gap_counts[gap_key] = gap_count + 1
            left_lane_right = lane_boxes[left_lane][2]
            right_lane_left = lane_boxes[left_lane + 1][0]
            channel_offsets = [0, -24, 24, -48, 48, -68, 68]
            channel_x = (
                (left_lane_right + right_lane_left) // 2
                + channel_offsets[gap_count % len(channel_offsets)]
            )

            if lane_diff > 0:
                start = (sx + sw, source_mid_y)
                end = (tx, target_mid_y)
            else:
                start = (sx, source_mid_y)
                end = (tx + tw, target_mid_y)
            points = [start, (channel_x, source_mid_y), (channel_x, target_mid_y), end]
            body.append(
                _routed_arrow(
                    points,
                    label,
                    (channel_x, (source_mid_y + target_mid_y) // 2),
                    used_label_rects,
                    (width, height),
                )
            )
            continue

        route_y = lanes_y + lane_height + 28 + long_edge_count * 26
        long_edge_count += 1
        if lane_diff > 0:
            start = (sx + sw, source_mid_y)
            end = (tx, target_mid_y)
        else:
            start = (sx, source_mid_y)
            end = (tx + tw, target_mid_y)
        points = [start, (start[0], route_y), (end[0], route_y), end]
        body.append(
            _routed_arrow(
                points,
                label,
                ((start[0] + end[0]) // 2, route_y),
                used_label_rects,
                (width, height),
            )
        )

    body.append("</svg>")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / f"{spec.key.replace('-', '_')}.svg").write_text("\n".join(body), encoding="utf-8")


def _lane_index(spec: DiagramSpec, node_id: str) -> int:
    for index, lane in enumerate(spec.lanes):
        if any(candidate_id == node_id for candidate_id, _label in lane.nodes):
            return index
    raise KeyError(node_id)


def specs() -> dict[str, DiagramSpec]:
    return {
        "alternativa-a-n1": DiagramSpec(
            "alternativa-a-n1",
            "Alternativa A - C4 Nivel 1 Contexto",
            "Un unico sistema en alcance; detalle tecnologico en Nivel 2.",
            [
                Lane("Personas", "actor", [
                    ("cliente", "Cliente B2B / Retail\nordenes y trazabilidad"),
                    ("conductor", "Conductor\nentregas y evidencias"),
                    ("operador", "Operacion RutaExpress\nSLA y excepciones"),
                    ("finanzas", "Finanzas\nconciliacion"),
                ]),
                Lane("Sistema en alcance", "system", [
                    ("sistema", "Plataforma Logistica\nRutaExpress TO BE\nAlt A: gobierno e\nintegracion centralizados"),
                ]),
                Lane("Sistemas externos", "external", [
                    ("wms", "WMS Principal (On Premises) (APP-06) APP-06 / APP-07"),
                    ("tms", "TMS (Transportation Management) (APP-11) APP-11"),
                    ("erp", "ERP Financiero (On Premises) (APP-25) APP-25"),
                    ("portal", "Portal B2B / CRM"),
                    ("legados", "Clientes SaaS y legados"),
                    ("mapas", "Servicios mapas / trafico"),
                ]),
            ],
            [
                ("cliente", "sistema", "ordenes"),
                ("conductor", "sistema", "entregas"),
                ("operador", "sistema", "gestion"),
                ("finanzas", "sistema", "conciliacion"),
                ("sistema", "wms", "inventario"),
                ("sistema", "tms", "rutas"),
                ("sistema", "erp", "finanzas"),
                ("sistema", "portal", "trazabilidad"),
                ("legados", "sistema", "archivos/API"),
                ("sistema", "mapas", "trafico"),
            ],
        ),
        "alternativa-b-n1": DiagramSpec(
            "alternativa-b-n1",
            "Alternativa B - C4 Nivel 1 Contexto",
            "Un unico sistema en alcance; detalle tecnologico en Nivel 2.",
            [
                Lane("Personas", "actor", [
                    ("cliente", "Cliente B2B / Retail\nordenes y trazabilidad"),
                    ("conductor", "Conductor\nentregas y evidencias"),
                    ("operador", "Operacion RutaExpress\nSLA y excepciones"),
                    ("finanzas", "Finanzas\nconciliacion"),
                ]),
                Lane("Sistema en alcance", "system", [
                    ("sistema", "Plataforma Logistica\nRutaExpress TO BE\nAlt B: orquestacion +\nmonolito modular"),
                ]),
                Lane("Sistemas externos", "external", [
                    ("wms", "WMS Principal (On Premises) (APP-06) APP-06 / APP-07"),
                    ("tms", "TMS (Transportation Management) (APP-11) APP-11"),
                    ("erp", "ERP Financiero (On Premises) (APP-25) APP-25"),
                    ("portal", "Portal B2B / CRM"),
                    ("legados", "Clientes SaaS y legados"),
                    ("mapas", "Servicios mapas / trafico"),
                ]),
            ],
            [
                ("cliente", "sistema", "ordenes"),
                ("conductor", "sistema", "entregas"),
                ("operador", "sistema", "gestion"),
                ("finanzas", "sistema", "conciliacion"),
                ("sistema", "wms", "inventario"),
                ("sistema", "tms", "rutas"),
                ("sistema", "erp", "finanzas"),
                ("sistema", "portal", "trazabilidad"),
                ("legados", "sistema", "archivos/API"),
                ("sistema", "mapas", "trafico"),
            ],
        ),
        "alternativa-a-n2": DiagramSpec(
            "alternativa-a-n2",
            "Alternativa A - C4 Nivel 2 Contenedores",
            "Aplicaciones y data stores dentro del sistema en alcance.",
            [
                Lane("Personas/canales", "actor", [
                    ("b2b", "Cliente B2B / Portal"),
                    ("app", "App Conductores\nAPP-15"),
                    ("ops", "Operacion / Soporte"),
                ]),
                Lane("Azure", "azure", [
                    ("apim", "Gateway y Gobierno API\nAzure API Management (APP-01)"),
                    ("oms", "OMS centralizado\nAPP-02 sobre AKS"),
                    ("inv", "Inventario y Reservas\nAKS"),
                    ("sql", "Repositorio transaccional\nAzure SQL"),
                    ("bus", "Bus Eventos Central\nBus de Eventos Central (PLT-03) Event Hubs"),
                    ("colas", "Colas, DLQ y Replay\nAzure Service Bus"),
                    ("obs", "Observabilidad\nPlataforma de Observabilidad Unificada (PLT-01)"),
                ]),
                Lane("AWS", "aws", [
                    ("backend", "Backend movil\nECS/Lambda"),
                    ("syncdb", "Repositorio sync movil\nDynamoDB"),
                    ("s3", "Repositorio evidencias\nS3 + KMS"),
                    ("awsbuffer", "Buffer movil\nSQS/EventBridge"),
                ]),
                Lane("GCP", "gcp", [
                    ("pubsub", "Canal analitico\nPub/Sub"),
                    ("opt", "Optimizador dinamico\nCloud Run/GKE"),
                    ("dwh", "Repositorio analitico\nBigQuery"),
                    ("ml", "Prediccion riesgo\nVertex AI"),
                ]),
                Lane("Externos", "external", [
                    ("wms", "WMS Principal (On Premises) (APP-06) APP-06 / APP-07"),
                    ("erp", "ERP Financiero (On Premises) (APP-25) APP-25"),
                    ("portal", "Portal B2B / CRM"),
                    ("legacy", "Canales legados"),
                ]),
            ],
            [
                ("b2b", "apim", "API"),
                ("apim", "oms", "REST"),
                ("oms", "inv", "reserva"),
                ("oms", "sql", "estado"),
                ("inv", "sql", "stock"),
                ("oms", "bus", "events"),
                ("inv", "bus", "events"),
                ("bus", "colas", "colas"),
                ("app", "backend", "mobile"),
                ("backend", "syncdb", "estado"),
                ("backend", "s3", "evidencia"),
                ("backend", "awsbuffer", "buffer"),
                ("awsbuffer", "bus", "bridge"),
                ("bus", "pubsub", "bridge"),
                ("pubsub", "opt", "eventos"),
                ("opt", "dwh", "features"),
                ("dwh", "ml", "modelo"),
                ("inv", "wms", "WMS Principal (On Premises) (APP-06)"),
                ("inv", "erp", "ERP Financiero (On Premises) (APP-25)"),
                ("colas", "portal", "estado"),
                ("legacy", "colas", "adaptador"),
                ("ops", "obs", "dashboards"),
            ],
        ),
        "alternativa-b-n2": DiagramSpec(
            "alternativa-b-n2",
            "Alternativa B - C4 Nivel 2 Contenedores",
            "Monolito modular + orquestador; notificaciones selectivas.",
            [
                Lane("Personas/canales", "actor", [
                    ("b2b", "Cliente B2B / Portal"),
                    ("app", "App Conductores\nAPP-15"),
                    ("ops", "Operacion / Soporte"),
                ]),
                Lane("Azure", "azure", [
                    ("apim", "Gateway y Gobierno API\nAzure API Management (APP-01)"),
                    ("core", "Nucleo Logistico Modular\nAPP-02 OMS + Inventario"),
                    ("orch", "Orquestador de Procesos\nDurable Functions"),
                    ("sql", "Repositorio transaccional\nAzure SQL"),
                    ("notif", "Canal notificaciones\nService Bus topics"),
                    ("acl", "Adaptadores ACL\nWMS / TMS / ERP"),
                    ("azobs", "Observabilidad\nPlataforma de Observabilidad Unificada (PLT-01)"),
                ]),
                Lane("AWS", "aws", [
                    ("backend", "Backend movil\nECS/Lambda"),
                    ("syncdb", "Repositorio sync movil\nDynamoDB"),
                    ("s3", "Repositorio evidencias\nS3 + KMS"),
                ]),
                Lane("GCP", "gcp", [
                    ("pubsub", "Canal analitico\nPub/Sub"),
                    ("opt", "Optimizador dinamico\nCloud Run/GKE"),
                    ("dwh", "Repositorio analitico\nBigQuery"),
                    ("ml", "Prediccion riesgo\nVertex AI"),
                ]),
                Lane("Externos", "external", [
                    ("wms", "WMS Principal (On Premises) (APP-06) APP-06 / APP-07"),
                    ("erp", "ERP Financiero (On Premises) (APP-25) APP-25"),
                    ("tms", "TMS (Transportation Management) (APP-11) APP-11"),
                    ("portal", "Portal B2B / CRM"),
                    ("legacy", "Canales legados"),
                ]),
            ],
            [
                ("b2b", "apim", "API"),
                ("apim", "core", "REST"),
                ("core", "sql", "estado"),
                ("core", "orch", "saga"),
                ("orch", "acl", "pasos"),
                ("acl", "wms", "WMS"),
                ("acl", "erp", "ERP"),
                ("acl", "tms", "TMS"),
                ("core", "notif", "notify"),
                ("notif", "portal", "estado"),
                ("notif", "backend", "estado"),
                ("notif", "pubsub", "bridge"),
                ("app", "backend", "mobile"),
                ("backend", "syncdb", "estado"),
                ("backend", "s3", "evidencia"),
                ("backend", "apim", "ack API"),
                ("pubsub", "opt", "eventos"),
                ("opt", "dwh", "features"),
                ("dwh", "ml", "modelo"),
                ("legacy", "apim", "adaptador"),
                ("ops", "azobs", "dashboards"),
            ],
        ),
        "alternativa-a-n3": DiagramSpec(
            "alternativa-a-n3",
            "Alternativa A - C4 Nivel 3 Componentes",
            "Zoom a un unico contenedor: Bus de Eventos Central (PLT-03) en Azure.",
            [
                Lane("Productores", "external", [
                    ("oms", "OMS centralizado\nAPP-02"),
                    ("inv", "Inventario y Reservas"),
                    ("mobile", "Backend movil AWS"),
                    ("legacy", "Adaptadores legados"),
                ]),
                Lane("Contenedor en foco", "focus", [
                    ("ingest", "Event Ingestion API"),
                    ("schema", "Schema Validator"),
                    ("router", "Event Router"),
                    ("ordering", "Ordering Guard"),
                    ("retry", "Retry Scheduler"),
                    ("dlq", "DLQ Manager"),
                    ("replay", "Replay Controller"),
                    ("backpressure", "Backpressure Controller"),
                    ("audit", "Audit / Event Store"),
                ]),
                Lane("Consumidores", "external", [
                    ("tms", "Adaptador TMS (Transportation Management) (APP-11)\nAPP-11"),
                    ("portal", "Portal B2B / CRM"),
                    ("optimizer", "Optimizador GCP"),
                    ("obs", "Observabilidad\nPlataforma de Observabilidad Unificada (PLT-01)"),
                    ("iam", "Identidad y secretos\nPlataforma de Identidad y Accesos (IAM) (PLT-02)"),
                ]),
            ],
            [
                ("oms", "ingest", "OrderEvents"),
                ("inv", "ingest", "Inventory"),
                ("mobile", "ingest", "Tracking"),
                ("legacy", "ingest", "Legacy"),
                ("ingest", "schema", "valida"),
                ("schema", "router", "valido"),
                ("router", "ordering", "secuencia"),
                ("ordering", "retry", "entrega"),
                ("retry", "tms", "eventos"),
                ("retry", "portal", "estado"),
                ("retry", "optimizer", "analitica"),
                ("router", "dlq", "fallo"),
                ("dlq", "replay", "replay"),
                ("replay", "router", "reinyecta"),
                ("backpressure", "router", "control"),
                ("audit", "obs", "metricas"),
                ("iam", "ingest", "auth"),
            ],
        ),
        "alternativa-b-n3": DiagramSpec(
            "alternativa-b-n3",
            "Alternativa B - C4 Nivel 3 Componentes",
            "Zoom a un unico contenedor: Nucleo Logistico Modular APP-02.",
            [
                Lane("Colaboradores", "external", [
                    ("apim", "Gateway API Azure"),
                    ("orch", "Runtime Orquestador\nDurable Functions"),
                    ("mobile", "Backend movil AWS"),
                    ("legacy", "Adaptadores legados"),
                ]),
                Lane("Contenedor en foco", "focus", [
                    ("facade", "Command API Facade"),
                    ("valid", "Validation and Dedup"),
                    ("order", "Order Lifecycle"),
                    ("inv", "Inventory Reservation"),
                    ("comp", "Compensation Manager"),
                    ("acl", "External ACL Gateway"),
                    ("notif", "Notification Publisher"),
                    ("audit", "Audit Store"),
                ]),
                Lane("Salida", "external", [
                    ("wms", "WMS APP-06/07"),
                    ("erp", "ERP APP-25"),
                    ("tms", "Adaptador TMS APP-11"),
                    ("portal", "Portal B2B / CRM"),
                    ("obs", "Observabilidad PLT-01"),
                ]),
            ],
            [
                ("apim", "facade", "CreateOrder"),
                ("mobile", "facade", "DeliveryAck"),
                ("legacy", "facade", "BulkOrder"),
                ("facade", "valid", "valida"),
                ("valid", "order", "estado"),
                ("order", "inv", "reserva"),
                ("facade", "orch", "saga"),
                ("orch", "comp", "compensa"),
                ("inv", "acl", "WMS/ERP"),
                ("acl", "wms", "integracion"),
                ("acl", "erp", "integracion"),
                ("acl", "tms", "despacho"),
                ("order", "notif", "notify"),
                ("notif", "portal", "estado"),
                ("audit", "obs", "metricas"),
            ],
        ),
    }


def main() -> None:
    all_specs = specs()
    parser = argparse.ArgumentParser(description="Genera SVG C4 RutaExpress con Python estandar")
    parser.add_argument("--only", choices=list(all_specs.keys()), help="Generar un solo diagrama")
    args = parser.parse_args()

    targets = [args.only] if args.only else list(all_specs.keys())
    _validate_sources(targets)

    print(f"Salida: {OUT_DIR}")
    for key in targets:
        print(f"  -> {key.replace('-', '_')}.svg")
        render(all_specs[key])
    print("Listo.")


if __name__ == "__main__":
    main()
