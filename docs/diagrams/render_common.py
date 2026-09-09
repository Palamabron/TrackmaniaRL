from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast

# Color communicates role, while card surfaces remain neutral.
PALETTE = {
    "blue": ("#285cc4", "#eff4fc"),
    "green": ("#087d74", "#edf7f5"),
    "orange": ("#9b681f", "#fbf5e9"),
    "purple": ("#285cc4", "#eff4fc"),
    "red": ("#a64646", "#fcf0ef"),
    "slate": ("#536579", "#f3f5f7"),
    "cyan": ("#087d74", "#edf7f5"),
}


@dataclass(frozen=True, slots=True)
class Bounds:
    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True, slots=True)
class TextLayout:
    x: float
    y: float
    width: float
    size: int
    color: str
    align: str


FONT_WIDTHS = json.loads(Path(__file__).with_name("arial-widths.json").read_text(encoding="utf-8"))


def text_width(label: str, size: int) -> float:
    """Arial advance widths in ems, with a 6% allowance for font substitution."""
    return sum(FONT_WIDTHS.get(char, 1.0) for char in label) * size * 1.06


def wrap(label: str, width: float, size: int) -> str:
    lines: list[str] = []
    for paragraph in label.split("\n"):
        line = ""
        for word in paragraph.split():
            candidate = f"{line} {word}" if line else word
            if line and text_width(candidate, size) > width:
                lines.append(line)
                line = ""
            # Identifiers can be wider than a card even without any spaces.
            if line:
                line += " "
            for char in word:
                if line and text_width(line + char, size) > width:
                    lines.append(line)
                    line = ""
                line += char
        lines.append(line)
    return "\n".join(lines)


def node_content_layouts(node: dict[str, Any]) -> list[tuple[str, str, TextLayout]]:
    """Lay out headings, optional formulae and descriptions inside a node."""
    width = node["w"] * 0.65 if node.get("shape") == "diamond" else node["w"] - 40
    title = wrap(node["label"], width, 20)
    detail = wrap(node.get("detail", ""), width, 18)
    formula = node.get("formula")
    formula_plain = node.get("formula_plain", formula or "")
    formula_size = node.get("formula_size", 22)
    formula_height = formula_size * 1.6 if formula else 0
    title_height = len(title.split("\n")) * 25
    detail_height = 8 + len(detail.split("\n")) * 22.5 if detail else 0
    formula_gap = 10 if formula else 0
    height = title_height + formula_gap + formula_height + detail_height
    if node.get("shape") == "diamond":
        fits = width / node["w"] + height / node["h"] <= 0.94
    else:
        fits = height + 32 <= node["h"]
    if not fits:
        raise ValueError(f"Text does not fit node {node['id']!r}; enlarge it or shorten the label")
    top = node["y"] + (node["h"] - height) / 2
    left = node["x"] + (node["w"] - width) / 2
    align = "center" if node.get("shape") == "diamond" else "left"
    layouts = [("title", title, TextLayout(left, top, width, 20, "#152b43", align))]
    cursor = top + title_height
    if formula:
        cursor += formula_gap
        layouts.append(
            (
                "formula",
                formula_plain,
                TextLayout(left, cursor, width, formula_size, "#152b43", align),
            )
        )
        cursor += formula_height
    if detail:
        layouts.append(
            ("detail", detail, TextLayout(left, cursor + 8, width, 18, "#536579", align))
        )
    return layouts


def node_text_layouts(node: dict[str, Any]) -> list[tuple[str, TextLayout]]:
    """Compatibility view containing the editable text representation."""
    return [(label, layout) for _, label, layout in node_content_layouts(node)]


def edge_points(edge: dict[str, Any], nodes: dict[str, dict[str, Any]]) -> list[list[float]]:
    if points := edge.get("points"):
        return cast(list[list[float]], points)
    source = nodes[edge["from"]]
    target = nodes[edge["to"]]
    return [
        [source["x"] + source["w"], source["y"] + source["h"] / 2],
        [target["x"], target["y"] + target["h"] / 2],
    ]


def edge_label_position(points: list[list[float]]) -> tuple[float, float]:
    start_x, start_y = points[0]
    end_x, end_y = points[-1]
    if start_y == end_y:
        return ((start_x + end_x) / 2, start_y - 18)
    if start_x == end_x:
        return (start_x + 100, (start_y + end_y) / 2)
    point = points[len(points) // 2]
    return (point[0], point[1])
