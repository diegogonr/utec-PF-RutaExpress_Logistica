#!/usr/bin/env python3
"""
Genera PNGs C4 con Python + Pillow reutilizando las especificaciones del
generador SVG.

Este script existe para ambientes donde no estan instalados Graphviz ni la
libreria diagrams, pero si esta disponible Pillow.
"""

from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from generar_diagramas_python_svg import COLORS, OUT_DIR, SOURCE_MARKDOWNS, DiagramSpec, specs


PNG_NAMES = {
    "alternativa-a-n1": "alternativa_A_n1_contexto.png",
    "alternativa-a-n2": "alternativa_A_n2_contenedores.png",
    "alternativa-a-n3": "alternativa_A_n3_componentes.png",
    "alternativa-b-n1": "alternativa_B_n1_contexto.png",
    "alternativa-b-n2": "alternativa_B_n2_contenedores.png",
    "alternativa-b-n3": "alternativa_B_n3_componentes.png",
}


def _font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


FONT_TITLE = _font(26, True)
FONT_SUBTITLE = _font(15)
FONT_LANE = _font(16, True)
FONT_NODE = _font(14)
FONT_EDGE = _font(12)


def _wrap(label: str, width: int = 25) -> list[str]:
    lines: list[str] = []
    for part in label.split("\n"):
        words = part.split()
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if len(candidate) > width and current:
                lines.append(current)
                current = word
            else:
                current = candidate
        if current:
            lines.append(current)
    return lines[:5]


def _center_text(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], lines: list[str]) -> None:
    x1, y1, x2, y2 = box
    line_height = 17
    total_h = len(lines) * line_height
    y = y1 + ((y2 - y1) - total_h) // 2 + 2
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=FONT_NODE)
        text_w = bbox[2] - bbox[0]
        draw.text((x1 + ((x2 - x1) - text_w) // 2, y), line, font=FONT_NODE, fill="#0f172a")
        y += line_height


def _overlaps(a: tuple[int, int, int, int], b: tuple[int, int, int, int]) -> bool:
    return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])


def _draw_edge_label(
    draw: ImageDraw.ImageDraw,
    center: tuple[int, int],
    label: str,
    used_rects: list[tuple[int, int, int, int]],
    image_size: tuple[int, int],
) -> None:
    if not label:
        return

    label = label[:24]
    bbox = draw.textbbox((0, 0), label, font=FONT_EDGE)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pad_x = 7
    pad_y = 4
    cx, cy = center
    max_w, max_h = image_size

    candidates: list[tuple[int, int, int, int]] = []
    for step in range(0, 9):
        for sign in (1, -1):
            y = cy + sign * step * 18
            rect = (
                cx - tw // 2 - pad_x,
                y - th // 2 - pad_y,
                cx + tw // 2 + pad_x,
                y + th // 2 + pad_y,
            )
            if rect[0] < 6 or rect[1] < 6 or rect[2] > max_w - 6 or rect[3] > max_h - 6:
                continue
            candidates.append(rect)

    rect = candidates[-1] if candidates else (cx - tw // 2 - pad_x, cy - th // 2 - pad_y, cx + tw // 2 + pad_x, cy + th // 2 + pad_y)
    for candidate in candidates:
        if not any(_overlaps(candidate, used) for used in used_rects):
            rect = candidate
            break

    used_rects.append(rect)
    x1, y1, x2, y2 = rect
    draw.rounded_rectangle(rect, radius=6, fill="#ffffff", outline="#cbd5e1")
    draw.text((x1 + pad_x, y1 + pad_y - 1), label, font=FONT_EDGE, fill="#334155")


def _draw_arrowhead(draw: ImageDraw.ImageDraw, previous: tuple[int, int], end: tuple[int, int]) -> None:
    px, py = previous
    ex, ey = end
    angle = math.atan2(ey - py, ex - px)
    arrow_len = 12
    arrow_angle = math.pi / 7
    p1 = (
        ex - arrow_len * math.cos(angle - arrow_angle),
        ey - arrow_len * math.sin(angle - arrow_angle),
    )
    p2 = (
        ex - arrow_len * math.cos(angle + arrow_angle),
        ey - arrow_len * math.sin(angle + arrow_angle),
    )
    draw.polygon([(ex, ey), p1, p2], fill="#475569")


def _polyline_arrow(
    draw: ImageDraw.ImageDraw,
    points: list[tuple[int, int]],
    label: str,
    label_pos: tuple[int, int],
    used_label_rects: list[tuple[int, int, int, int]],
    image_size: tuple[int, int],
) -> None:
    draw.line(points, fill="#475569", width=2, joint="curve")
    _draw_arrowhead(draw, points[-2], points[-1])
    _draw_edge_label(draw, label_pos, label, used_label_rects, image_size)


def render_png(spec: DiagramSpec) -> None:
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

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    draw.text((margin, 34), spec.title, font=FONT_TITLE, fill="#0f172a")
    draw.text((margin, 70), spec.subtitle, font=FONT_SUBTITLE, fill="#475569")
    draw.text((margin, 96), f"Fuente: {SOURCE_MARKDOWNS[spec.key].name}", font=FONT_EDGE, fill="#64748b")

    node_pos: dict[str, tuple[int, int, int, int]] = {}
    node_lane: dict[str, int] = {}
    lane_boxes: list[tuple[int, int, int, int]] = []
    for lane_index, lane in enumerate(spec.lanes):
        x = margin + lane_index * (lane_width + lane_gap)
        lane_boxes.append((x, lanes_y, x + lane_width, lanes_y + lane_height))
        fill, stroke = COLORS.get(lane.kind, COLORS["external"])
        draw.rounded_rectangle((x, lanes_y, x + lane_width, lanes_y + lane_height), radius=18, fill=fill, outline=stroke, width=2)
        draw.text((x + 18, lanes_y + 18), lane.title, font=FONT_LANE, fill=stroke)
        for node_index, (node_id, label) in enumerate(lane.nodes):
            nx = x + (lane_width - node_width) // 2
            ny = lanes_y + 58 + node_index * (node_height + node_gap)
            node_box = (nx, ny, nx + node_width, ny + node_height)
            node_pos[node_id] = node_box
            node_lane[node_id] = lane_index
            draw.rounded_rectangle(node_box, radius=12, fill=fill, outline=stroke, width=2)
            _center_text(draw, node_box, _wrap(label))

    used_label_rects: list[tuple[int, int, int, int]] = []
    adjacent_gap_counts: dict[tuple[int, int], int] = {}
    same_lane_counts: dict[int, int] = {}
    long_edge_count = 0

    for source, target, label in spec.edges:
        sx1, sy1, sx2, sy2 = node_pos[source]
        tx1, ty1, tx2, ty2 = node_pos[target]
        source_lane = node_lane[source]
        target_lane = node_lane[target]
        source_mid_y = (sy1 + sy2) // 2
        target_mid_y = (ty1 + ty2) // 2
        lane_diff = target_lane - source_lane

        if source_lane == target_lane:
            lane_x1, _lane_y1, lane_x2, _lane_y2 = lane_boxes[source_lane]
            rail_count = same_lane_counts.get(source_lane, 0)
            same_lane_counts[source_lane] = rail_count + 1
            rail_x = lane_x2 - 18 - (rail_count % 3) * 18
            rail_x = max(rail_x, sx2 + 12)
            points = [
                (sx2, source_mid_y),
                (rail_x, source_mid_y),
                (rail_x, target_mid_y),
                (tx2, target_mid_y),
            ]
            _polyline_arrow(
                draw,
                points,
                label,
                (rail_x, (source_mid_y + target_mid_y) // 2),
                used_label_rects,
                image.size,
            )
            continue

        if abs(lane_diff) == 1:
            left_lane = min(source_lane, target_lane)
            gap_key = (left_lane, left_lane + 1)
            gap_count = adjacent_gap_counts.get(gap_key, 0)
            adjacent_gap_counts[gap_key] = gap_count + 1
            left_lane_right = lane_boxes[left_lane][2]
            right_lane_left = lane_boxes[left_lane + 1][0]
            channel_offsets = [0, -28, 28, -56, 56, -84, 84]
            channel_x = (left_lane_right + right_lane_left) // 2 + channel_offsets[gap_count % len(channel_offsets)]

            if lane_diff > 0:
                start = (sx2, source_mid_y)
                end = (tx1, target_mid_y)
            else:
                start = (sx1, source_mid_y)
                end = (tx2, target_mid_y)
            points = [start, (channel_x, source_mid_y), (channel_x, target_mid_y), end]
            _polyline_arrow(
                draw,
                points,
                label,
                (channel_x, (source_mid_y + target_mid_y) // 2),
                used_label_rects,
                image.size,
            )
            continue

        route_y = lanes_y + lane_height + 28 + long_edge_count * 26
        long_edge_count += 1
        if lane_diff > 0:
            start = (sx2, source_mid_y)
            end = (tx1, target_mid_y)
        else:
            start = (sx1, source_mid_y)
            end = (tx2, target_mid_y)
        points = [start, (start[0], route_y), (end[0], route_y), end]
        _polyline_arrow(
            draw,
            points,
            label,
            ((start[0] + end[0]) // 2, route_y),
            used_label_rects,
            image.size,
        )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    image.save(OUT_DIR / PNG_NAMES[spec.key])


def _lane_index(spec: DiagramSpec, node_id: str) -> int:
    for index, lane in enumerate(spec.lanes):
        if any(candidate_id == node_id for candidate_id, _label in lane.nodes):
            return index
    raise KeyError(node_id)


def main() -> None:
    all_specs = specs()
    parser = argparse.ArgumentParser(description="Genera PNG C4 RutaExpress con Python + Pillow")
    parser.add_argument("--only", choices=list(all_specs.keys()), help="Generar un solo diagrama")
    args = parser.parse_args()

    targets = [args.only] if args.only else list(all_specs.keys())
    print(f"Salida: {OUT_DIR}")
    for key in targets:
        print(f"  -> {PNG_NAMES[key]}")
        render_png(all_specs[key])
    print("Listo.")


if __name__ == "__main__":
    main()
