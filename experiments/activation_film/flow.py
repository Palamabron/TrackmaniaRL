"""Export an opaque, ordered model view beside the intact recorded gameplay."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw

from experiments.activation_film import render as film
from experiments.activation_film.tensors import TensorComposition
from experiments.sub37.audit_activation_sources import digest

BG = (9, 14, 25)
CARD = (17, 25, 40)
LINE = (47, 67, 87)
SOFT = (133, 154, 177)
TEAL = (67, 224, 196)
BLUE = (110, 180, 255)
PURPLE = (179, 143, 246)


def arrow(draw: Any, points: list[tuple[int, int]], color: tuple = TEAL) -> None:
    draw.line(points, fill=color, width=2, joint="curve")
    x, y = points[-1]
    px, py = points[-2]
    angle = math.atan2(y - py, x - px)
    tips = [(x, y)]
    for offset in (-0.5, 0.5):
        tips.append((x - 7 * math.cos(angle + offset), y - 7 * math.sin(angle + offset)))
    draw.polygon(tips, fill=color)


def box(draw: Any, bounds: tuple[int, int, int, int]) -> None:
    draw.rounded_rectangle(bounds, radius=12, fill=CARD, outline=LINE, width=1)


def merge(draw: Any, center: tuple[int, int], symbol: str = "+") -> None:
    x, y = center
    if symbol == "mix":
        draw.polygon(
            [(x, y - 10), (x + 10, y), (x, y + 10), (x - 10, y)], fill=BG, outline=TEAL, width=2
        )
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=TEAL)
    else:
        draw.ellipse((x - 10, y - 10, x + 10, y + 10), fill=BG, outline=TEAL, width=2)
        draw.line((x - 4, y, x + 4, y), fill=TEAL, width=2)
        draw.line((x, y - 4, x, y + 4), fill=TEAL, width=2)


class FlowComposition(TensorComposition):
    def __init__(self, manifest: dict[str, Any], best: dict[str, Any], data: Any) -> None:
        super().__init__(manifest, best, data)
        self.values["road_input"] = self.values["observation/track"].reshape(-1, 264)
        self.values["car_input"] = self.values["observation/physics"]
        self.values["context_input"] = self.values["observation/context"]
        self.values["raw_q_centered"] = self.values["raw_q"] - np.median(
            self.values["raw_q"], axis=1, keepdims=True
        )
        for key in (
            "fusion",
            "road_input",
            "car_input",
            "context_input",
            "raw_q_centered",
            "recovery_correction",
        ):
            self.scales[key] = max(float(np.percentile(np.abs(self.values[key]), 99)), 1e-6)

    def features(self, layer: Image.Image, row: int) -> None:
        draw = ImageDraw.Draw(layer)
        text = film.write
        text(draw, (1180, 100), "01   INPUTS", 18, SOFT)
        for bounds, title in (
            ((1180, 133, 1528, 184), "ROAD GEOMETRY  /  264"),
            ((1546, 133, 1707, 184), "CAR  /  60"),
            ((1725, 133, 1896, 184), "CONTEXT  /  29"),
        ):
            box(draw, bounds)
            text(draw, (bounds[0] + 13, 150), title, 16, TEAL)
        # One road input forks into the graph and the ordered Conv1D adapter.
        arrow(draw, [(1354, 184), (1354, 198), (1262, 198), (1262, 218)])
        arrow(draw, [(1354, 198), (1445, 198), (1445, 218)], PURPLE)
        arrow(draw, [(1626, 184), (1626, 218)], BLUE)
        arrow(draw, [(1810, 184), (1810, 218)], BLUE)
        for left, right, title, subtitle in (
            (1180, 1345, "GNN", "44 nodes x 128"),
            (1363, 1528, "Conv1D", "64 x 44"),
            (1546, 1707, "MLP", "60 to 192"),
            (1725, 1896, "MLP", "29 to 192"),
        ):
            box(draw, (left, 218, right, 427))
            text(draw, (left + 13, 232), title, 22, TEAL if title == "GNN" else BLUE)
            text(draw, (left + 13, 265), subtitle, 16, SOFT)
        self.plate(layer, row, "encoder.track_conv.0.norms.1", (1191, 300), (44, 128), 0.95, TEAL)
        self.plate(
            layer, row, "encoder.spatial_adapter.blocks.3", (1387, 291), (64, 44), 1.15, PURPLE
        )
        self.plate(layer, row, "motion", (1574, 301), (12, 16), 4.2, BLUE)
        self.plate(layer, row, "encoder.context_adapter", (1760, 301), (12, 16), 4.2, BLUE)
        text(draw, (1193, 386), "Pool + MLP", 16, SOFT)
        spatial_zero = not np.any(self.values["encoder.spatial_adapter"][row])
        text(draw, (1376, 385), "Zero correction" if spatial_zero else "Adds correction", 16, SOFT)
        text(draw, (1376, 405), "after projection", 16, SOFT)
        text(draw, (1560, 386), "Motion", 16, SOFT)
        text(draw, (1739, 386), "Correction", 16, SOFT)
        arrow(draw, [(1262, 427), (1262, 449), (1344, 449)])
        arrow(draw, [(1445, 427), (1445, 449), (1364, 449)], PURPLE)
        merge(draw, (1354, 449))
        arrow(draw, [(1626, 427), (1626, 449), (1708, 449)], BLUE)
        arrow(draw, [(1810, 427), (1810, 449), (1728, 449)], BLUE)
        merge(draw, (1718, 449))
        arrow(draw, [(1354, 459), (1354, 489), (1446, 489)])
        arrow(draw, [(1718, 459), (1718, 489), (1660, 489)], BLUE)
        box(draw, (1446, 467, 1660, 513))
        text(draw, (1460, 480), "CONCAT  192 + 192", 16, film.WHITE)
        arrow(draw, [(1553, 513), (1553, 528)])
        box(draw, (1360, 528, 1746, 563))
        text(draw, (1373, 536), "Normalize + project 384 to 192", 18, SOFT)

    def simba(self, layer: Image.Image, row: int) -> None:
        draw = ImageDraw.Draw(layer)
        text = film.write
        text(draw, (1180, 583), "02   SimBa", 22, TEAL)
        text(draw, (1320, 588), "4 residual MLP blocks", 16, SOFT)
        arrow(draw, [(1553, 563), (1553, 574), (1167, 574), (1167, 620), (1259, 620)])
        for i in range(4):
            x = 1180 + 183 * i
            key = f"encoder.backbone.blocks.{i}"
            box(draw, (x, 633, x + 165, 862))
            text(draw, (x + 12, 646), f"BLOCK {i + 1}", 16, SOFT)
            arrow(draw, [(x + 79, 620), (x + 79, 680)])
            # The arrow forks before the MLP and rejoins at the learned residual mix.
            arrow(draw, [(x + 79, 620), (x + 154, 620), (x + 154, 801), (x + 89, 801)], PURPLE)
            text(draw, (x + 109, 680), "skip", 16, PURPLE)
            self.plate(layer, row, key + ".expand", (x + 11, 689), (24, 32), 2.15, BLUE)
            text(draw, (x + 12, 762), "768", 16, SOFT)
            text(draw, (x + 60, 762), "ReLU", 16, SOFT)
            arrow(draw, [(x + 79, 785), (x + 79, 791)], BLUE)
            merge(draw, (x + 79, 801), "mix")
            arrow(draw, [(x + 79, 811), (x + 79, 820)])
            self.plate(layer, row, key, (x + 14, 820), (8, 24), 2.3, TEAL)
            text(draw, (x + 104, 830), "192", 16, SOFT)
            if i < 3:
                arrow(
                    draw,
                    [(x + 79, 862), (x + 79, 878), (x + 174, 878), (x + 174, 620), (x + 262, 620)],
                )
        text(
            draw,
            (1180, 889),
            "Each block: expand, ReLU, project. Diamond: mix + normalize.",
            16,
            SOFT,
        )

    def decision(self, layer: Image.Image, row: int) -> None:
        draw = ImageDraw.Draw(layer)
        text = film.write
        arrow(draw, [(1808, 862), (1808, 918), (1588, 918)])
        text(draw, (1180, 930), "03   ACTION SELECTION", 18, SOFT)
        recovery = float(np.max(np.abs(self.values["recovery_correction"][row])))
        box(draw, (1180, 958, 1420, 1051))
        text(draw, (1193, 972), "RECOVERY 8 > MLP", 16, SOFT)
        text(draw, (1193, 1002), f"Correction: {'active' if recovery > 1e-8 else 'off'}", 18, SOFT)
        arrow(draw, [(1420, 983), (1437, 983), (1437, 918), (1568, 918)], PURPLE)
        arrow(draw, [(1578, 928), (1578, 950)])
        merge(draw, (1578, 918))
        box(draw, (1462, 950, 1694, 1051))
        text(draw, (1475, 962), "IQN head", 22, TEAL)
        text(draw, (1475, 993), "32 quantiles > 78 scores", 16, SOFT)
        self.plate(layer, row, "raw_q_centered", (1479, 1020), (3, 26), 2.3, TEAL)
        arrow(draw, [(1694, 996), (1725, 996)])
        box(draw, (1725, 956, 1896, 1035))
        text(draw, (1740, 969), "CHOOSE", 20, TEAL)
        text(draw, (1740, 999), "Steer / pedals", 16, SOFT)
        arrow(draw, [(1810, 1035), (1810, 1068), (1135, 1068), (1135, 839), (1090, 839)])

    def network(self, overlay: Image.Image, row: int) -> None:
        if row != self.cached_row:
            layer = Image.new("RGBA", overlay.size)
            self.features(layer, row)
            self.simba(layer, row)
            self.decision(layer, row)
            self.cached_row, self.cached_network = row, layer
        overlay.alpha_composite(self.cached_network)

    def controls(self, overlay: Image.Image, row: int) -> None:
        draw = ImageDraw.Draw(overlay)
        gas, brake, steer = self.manifest["action_table"][int(self.data["action"][row])]
        text = film.write
        text(draw, (674, 811), "AGENT CONTROLS", 18, SOFT)
        center = (750, 949)
        draw.ellipse((687, 886, 813, 1012), outline=(58, 78, 96), width=10)
        rotation = math.radians(steer * 110)
        for base_angle in (0, math.pi, math.pi / 2):
            angle = rotation + base_angle
            end = (center[0] + 53 * math.cos(angle), center[1] + 53 * math.sin(angle))
            draw.line([center, end], fill=TEAL, width=8)
        marker = (center[0] + 59 * math.sin(rotation), center[1] - 59 * math.cos(rotation))
        draw.ellipse((marker[0] - 5, marker[1] - 5, marker[0] + 5, marker[1] + 5), fill=film.WHITE)
        draw.ellipse((734, 933, 766, 965), fill=CARD, outline=TEAL, width=2)
        text(draw, (700, 1040), f"STEER {steer:+.2f}", 16, SOFT)
        for x, title, value, color in (
            (887, "THROTTLE", gas, TEAL),
            (1025, "BRAKE", abs(brake), (246, 127, 137)),
        ):
            active = float(np.clip(value, 0, 1))
            text(draw, (x - 17, 859), title, 16, SOFT)
            draw.line((x + 21, 1012, x + 21, 1030), fill=LINE, width=8)
            polygon = [(x, 900), (x + 43, 891), (x + 51, 1006), (x + 2, 1013)]
            tone = tuple(int(24 + channel * active * 0.66) for channel in color)
            draw.polygon(polygon, fill=tone, outline=color if active else LINE, width=2)
            for y in range(918, 995, 15):
                draw.line((x + 10, y, x + 38, y - 5), fill=BG, width=3)
            value_text = "TAP" if title == "BRAKE" and brake < 0 else f"{active:.0%}"
            text(draw, (x + 1, 1040), value_text, 16, color if active else SOFT)

    def live_frame(self, gameplay: Any, row: int) -> Image.Image:
        base = Image.new("RGBA", (film.W, film.H), (*BG, 255))
        rgb = cv2.cvtColor(gameplay, cv2.COLOR_BGR2RGB)
        shot = Image.fromarray(rgb).resize((1152, 648), Image.Resampling.LANCZOS)
        base.paste(shot, (0, 126))
        overlay = Image.new("RGBA", base.size)
        draw = ImageDraw.Draw(overlay)
        text = film.write
        draw.rectangle((1152, 0, 1920, 1080), fill=(*BG, 255))
        draw.line((1152, 0, 1152, 1080), fill=LINE, width=2)
        text(draw, (34, 27), "TRACKMANIA", 38, film.WHITE)
        text(draw, (36, 79), "An AI behind the wheel", 22, SOFT)
        draw.ellipse((984, 50, 996, 62), fill=TEAL)
        text(draw, (1010, 43), "AI DRIVING", 18, TEAL)
        text(draw, (1180, 28), "Inside the network", 30, film.WHITE)
        text(draw, (1180, 69), "Live activations  /  follow the arrows", 16, SOFT)
        text(draw, (36, 811), "SPEED", 18, SOFT)
        text(draw, (33, 845), f"{self.data['speed_kmh'][row]:.0f}", 76, film.WHITE)
        text(draw, (188, 893), "km/h", 22, SOFT)
        text(draw, (340, 811), "LAP TIME", 18, SOFT)
        text(draw, (336, 866), f"{self.data['race_ms'][row] / 1000:05.2f}", 48, film.WHITE)
        progress = float(np.clip(self.data["progress"][row], 0, 1))
        text(draw, (36, 977), "TRACK PROGRESS", 16, SOFT)
        text(draw, (490, 977), f"{progress:.0%}", 16, TEAL)
        draw.rounded_rectangle((36, 1019, 560, 1025), radius=3, fill=LINE)
        draw.rounded_rectangle(
            (36, 1019, 36 + max(2, round(524 * progress)), 1025), radius=3, fill=TEAL
        )
        draw.line((617, 811, 617, 1058), fill=LINE, width=1)
        self.network(overlay, row)
        self.controls(overlay, row)
        return Image.alpha_composite(base, overlay).convert("RGB")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--finish-time")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    manifest, best, data = film.choose_trial(args.capture)
    archive = args.capture / "path-tensors.npz"
    evidence = json.loads(archive.with_suffix(".json").read_text())
    if (
        digest(archive) != evidence["tensor_sha256"]
        or evidence["capture_sha256"] != best["capture_sha256"]
        or evidence["checkpoint_sha256"] != manifest["checkpoint_sha256"]
        or evidence["sampled_decisions"] != list(range(len(data["action"])))
    ):
        raise ValueError("Full-path tensor provenance mismatch")
    with np.load(archive, allow_pickle=False) as tensors:
        FlowComposition.tensors = {key: tensors[key] for key in tensors.files}
    if any(
        not np.isfinite(value).all() or len(value) != len(data["action"])
        for value in FlowComposition.tensors.values()
    ):
        raise ValueError("Full-path tensors contain invalid samples")
    available = np.isfinite(data["q"])
    np.testing.assert_allclose(
        data["q"][available],
        FlowComposition.tensors["raw_q"][available],
        atol=1e-5,
        rtol=1e-5,
    )
    film.Composition = FlowComposition
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report = film.render(args)
    report.update(
        {
            "path_tensor_sha256": evidence["tensor_sha256"],
            "layout": "Opaque 768px network panel, complete 1152x648 gameplay, wheel and pedals",
            "visual_abstraction": (
                "Selected full tensors and labelled module routes. "
                "IQN scores centered for display. "
                "Wheel angle is a visual mapping of the commanded steer. "
                "Brake TAP is a command, not continuous measured pedal pressure."
            ),
        }
    )
    args.output.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
