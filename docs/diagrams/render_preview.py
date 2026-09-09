from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass, replace
from functools import lru_cache
from io import StringIO
from typing import Any

from matplotlib import rc_context
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure

from docs.diagrams.render_common import (
    PALETTE,
    TextLayout,
    edge_label_position,
    edge_points,
    node_content_layouts,
    text_width,
    wrap,
)

HTML_STYLE = (
    "body{margin:0;background:#e2e8f0;font-family:system-ui}main{padding:24px}"
    ".canvas{max-width:1000px;margin:auto;background:white;border:1px solid #dce3ea;"
    "border-radius:12px;overflow:hidden}"
    "svg{display:block;width:100%;height:auto}button{position:fixed;right:24px;bottom:24px;"
    "padding:12px 18px;border:0;border-radius:9px;background:#1864ab;color:white;"
    "font-weight:700;cursor:pointer}"
)


@dataclass(frozen=True, slots=True)
class PreviewDocument:
    spec: dict[str, Any]
    svg: str
    scene: dict[str, Any]
    stem: str


def _svg_text(label: str, layout: TextLayout) -> str:
    anchor = {"middle": "middle", "start": "start"}[layout.align]
    text_x = layout.x + layout.width / 2 if layout.align == "middle" else layout.x
    lines = wrap(label, layout.width, layout.size).split("\n")
    spans = "".join(
        f'<tspan x="{text_x}" dy="{0 if index == 0 else layout.size * 1.25}">'
        f"{html.escape(line)}</tspan>"
        for index, line in enumerate(lines)
    )
    return (
        f'<text x="{text_x}" y="{layout.y}" text-anchor="{anchor}" '
        f'font-family="Arial,Helvetica,sans-serif" font-size="{layout.size}" '
        f'fill="{layout.color}">{spans}</text>'
    )


def render_svg(spec: dict[str, Any]) -> str:
    nodes = {node["id"]: node for node in spec["nodes"]}
    parts = _svg_header(spec)
    for zone in spec["zones"]:
        parts.extend(_svg_zone(zone))
    for edge in spec["edges"]:
        parts.extend(_svg_edge(edge, nodes))
    for node in spec["nodes"]:
        parts.extend(_svg_node(node))
    for note in spec.get("notes", []):
        parts.extend(_svg_note(note))
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def _svg_header(spec: dict[str, Any]) -> list[str]:
    title = TextLayout(40, 91, spec["width"] - 80, 34, "#152b43", "start")
    subtitle = TextLayout(40, 131, spec["width"] - 80, 18, "#536579", "start")
    return [
        (
            '<svg xmlns="http://www.w3.org/2000/svg" '
            'xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{spec["width"]}" '
            f'height="{spec["height"]}" viewBox="0 0 {spec["width"]} {spec["height"]}">'
        ),
        (
            '<defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="8" '
            'refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" '
            'fill="context-stroke"/></marker><filter id="shadow" x="-20%" y="-20%" '
            'width="140%" height="140%"><feDropShadow dx="0" dy="2" stdDeviation="3" '
            'flood-opacity=".14"/></filter></defs>'
        ),
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        _svg_text(
            spec.get("eyebrow", "TRACKMANIARL / SYSTEM GUIDE"),
            TextLayout(40, 37, spec["width"] - 80, 18, "#087d74", "start"),
        ),
        '<path d="M40,52 H960" stroke="#dce3ea" stroke-width="1"/>',
        _svg_text(spec["title"], title).replace("<text ", '<text font-weight="600" ', 1),
        _svg_text(spec["subtitle"], subtitle),
    ]


def _svg_zone(zone: dict[str, Any]) -> list[str]:
    stroke = PALETTE[zone["color"]][0]
    layout = TextLayout(zone["x"] + 24, zone["y"] + 38, zone["w"] - 48, 18, stroke, "start")
    return [
        (
            f'<rect x="{zone["x"]}" y="{zone["y"]}" width="{zone["w"]}" '
            f'height="{zone["h"]}" rx="10" fill="#f3f5f7" '
            'stroke="none"/>'
        ),
        _svg_text(zone["label"], layout).replace("<text ", '<text font-weight="600" ', 1),
    ]


def _svg_edge(edge: dict[str, Any], nodes: dict[str, dict[str, Any]]) -> list[str]:
    points = edge_points(edge, nodes)
    stroke = PALETTE[edge.get("color", "slate")][0]
    dash = ' stroke-dasharray="8 7"' if edge.get("style") == "dashed" else ""
    joined = " ".join(f"{x},{y}" for x, y in points)
    parts = [
        f'<g data-edge="{html.escape(edge["id"])}">',
        f'<polyline points="{joined}" fill="none" stroke="{stroke}" '
        f'stroke-width="1.75"{dash} marker-end="url(#arrow)"/>',
    ]
    if label := edge.get("label"):
        label_x, label_y = edge.get("label_at", edge_label_position(points))
        label_width = min(176, text_width(label, 18))
        label_height = len(wrap(label, 176, 18).split("\n")) * 22.5
        parts.append(
            f'<rect x="{label_x - label_width / 2 - 5}" y="{label_y - 24}" '
            f'width="{label_width + 10}" '
            f'height="{label_height + 6}" rx="5" fill="#ffffff" fill-opacity=".92"/>'
        )
        layout = TextLayout(label_x - 88, label_y - 5, 176, 18, stroke, "middle")
        parts.append(_svg_text(label, layout))
    return [*parts, "</g>"]


@lru_cache(maxsize=64)
def _math_svg(latex: str, layout: TextLayout, prefix: str) -> tuple[str, str]:
    """Render LaTeX math as deterministic SVG paths."""
    figure = Figure(figsize=(8, 1), dpi=72)
    FigureCanvasSVG(figure)
    figure.text(
        0,
        0.5,
        f"${latex}$",
        fontsize=layout.size,
        color=layout.color,
        va="center",
    )
    output = StringIO()
    with rc_context({"svg.fonttype": "path", "svg.hashsalt": "trackmaniarl-diagrams"}):
        figure.savefig(
            output,
            format="svg",
            transparent=True,
            bbox_inches="tight",
            pad_inches=0,
            metadata={"Date": None},
        )
    source = output.getvalue()
    view_box = re.search(r'viewBox="([^"]+)"', source)
    if view_box is None:
        raise ValueError("Rendered formula has no SVG viewBox")
    body = source[source.index(">", source.index("<svg")) + 1 : source.rindex("</svg>")]
    body = re.sub(r"<metadata>.*?</metadata>", "", body, flags=re.DOTALL)
    body = "\n".join(line.rstrip() for line in body.splitlines())
    ids = set(re.findall(r'id="([^"]+)"', body))
    for element_id in sorted(ids, key=len, reverse=True):
        safe_id = f"{prefix}-{element_id}"
        body = body.replace(f'id="{element_id}"', f'id="{safe_id}"')
        body = body.replace(f'#{element_id}"', f'#{safe_id}"')
    return view_box.group(1), body


def _svg_formula(latex: str, layout: TextLayout, item_id: str) -> str:
    view_box, body = _math_svg(latex, layout, item_id)
    return (
        f'<svg data-formula="{html.escape(item_id)}" x="{layout.x}" y="{layout.y}" '
        f'width="{layout.width}" height="{layout.size * 1.6}" viewBox="{view_box}" '
        f'preserveAspectRatio="xMinYMid meet">{body}</svg>'
    )


def _svg_node_text(node: dict[str, Any]) -> list[str]:
    parts = []
    for kind, label, layout in node_content_layouts(node):
        if kind == "formula":
            parts.append(_svg_formula(node["formula"], layout, f"{node['id']}-formula"))
            continue
        svg_layout = replace(
            layout,
            y=layout.y + layout.size,
            align="middle" if layout.align == "center" else "start",
        )
        text = _svg_text(label, svg_layout)
        if kind == "title":
            text = text.replace("<text ", '<text font-weight="600" ', 1)
        parts.append(text)
    return parts


def _svg_node(node: dict[str, Any]) -> list[str]:
    stroke, fill = PALETTE[node["color"]]
    return [
        f'<g data-node="{html.escape(node["id"])}">',
        _svg_node_shape(node, stroke, fill),
        (
            f'<path d="M{node["x"] + 20},{node["y"] + 1} h32" stroke="{stroke}" stroke-width="3"/>'
            if node.get("shape") != "diamond"
            else ""
        ),
        *_svg_node_text(node),
        "</g>",
    ]


def _svg_node_shape(node: dict[str, Any], stroke: str, fill: str) -> str:
    if node.get("shape") == "diamond":
        points = " ".join(
            (
                f"{node['x'] + node['w'] / 2},{node['y']}",
                f"{node['x'] + node['w']},{node['y'] + node['h'] / 2}",
                f"{node['x'] + node['w'] / 2},{node['y'] + node['h']}",
                f"{node['x']},{node['y'] + node['h'] / 2}",
            )
        )
        return f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>'
    return (
        f'<rect x="{node["x"]}" y="{node["y"]}" width="{node["w"]}" '
        f'height="{node["h"]}" rx="8" fill="#ffffff" stroke="#cdd7e2" '
        'stroke-width="1.5"/>'
    )


def _svg_note(note: dict[str, Any]) -> list[str]:
    fill = PALETTE[note.get("color", "slate")][1]
    layout = TextLayout(note["x"] + 20, note["y"] + 34, note["w"] - 40, 18, "#1f2937", "start")
    return [
        f'<g data-note="{html.escape(note["id"])}">',
        (
            f'<rect x="{note["x"]}" y="{note["y"]}" width="{note["w"]}" '
            f'height="{note["h"]}" rx="8" fill="{fill}" stroke="none" '
            'stroke-width="1.5"/>'
        ),
        _svg_text(note["text"], layout).replace("<tspan ", '<tspan font-weight="600" ', 1),
        "</g>",
    ]


def _download_script(stem: str) -> str:
    return (
        "document.getElementById('download').onclick=()=>{"
        "const data=JSON.parse(document.getElementById('scene').textContent);"
        "const a=document.createElement('a');"
        "a.href=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],"
        "{type:'application/json'}));"
        f"a.download='{stem}.excalidraw';a.click();}};"
    )


def render_html(preview: PreviewDocument) -> str:
    # Script contents are raw text: HTML entities would corrupt JSON.parse.
    # Escape '<' as JSON instead, so labels cannot close the script element.
    encoded = json.dumps(preview.scene, ensure_ascii=False).replace("<", "\\u003c")
    script = _download_script(preview.stem)
    return "\n".join(
        (
            "<!doctype html>",
            '<html lang="en"><head><meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width,initial-scale=1">',
            f"<title>{html.escape(preview.spec['title'])}</title>"
            f"<style>{HTML_STYLE}</style></head>",
            f'<body><main><div class="canvas">{preview.svg}</div></main>',
            '<button id="download">Download editable diagram</button>',
            f'<script id="scene" type="application/json">{encoded}</script>',
            f"<script>{script}</script></body></html>",
        )
    )
