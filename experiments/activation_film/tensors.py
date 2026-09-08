"""Render verified internal tensors over the original recorded lap."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, ClassVar

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from experiments.activation_film import render as film
from experiments.sub37.audit_activation_sources import digest


class TensorComposition(film.Composition):
    """Every visible cell represents one fixed tensor element, never a random particle."""

    tensors: ClassVar[dict[str, np.ndarray]] = {}

    def __init__(self, manifest: dict[str, Any], best: dict[str, Any], data: Any) -> None:
        super().__init__(manifest, best, data)
        # Keep every tensor legible even when the road behind it is bright white.
        ramp = np.linspace(210, 252, 760).astype(np.uint8)
        self.panel_mask = Image.fromarray(np.tile(ramp, (film.H, 1)))
        self.values = {key: np.asarray(data[key]) for key in data.files}
        self.values.update(self.tensors)
        self.values["pooled"] = self.values["encoder.track_conv.0"]
        self.values["motion"] = self.values["encoder.physics_proj"]
        self.values["state"] = self.values["encoder"]
        self.scales = {
            key: max(float(np.percentile(np.abs(value), 99)), 1e-6)
            for key, value in self.values.items()
            if key.startswith("encoder.") or key in ("pooled", "motion", "state")
        }
        self.selected = {}
        self.cached_row = -1
        self.cached_network = None

    def plate(  # noqa: PLR0913
        self,
        layer: Image.Image,
        row: int,
        key: str,
        xy: tuple[int, int],
        shape: tuple[int, int],
        cell: float,
        color: tuple[int, int, int],
    ) -> None:
        values = self.values[key][row].reshape(shape)
        normalized = np.clip(values / self.scales[key], -1, 1)
        magnitude = np.abs(normalized)
        positive = np.asarray(color)
        negative = np.asarray((155, 114, 225))
        tone = np.where(normalized[..., None] >= 0, positive, negative)
        rgb = 12 + tone * (magnitude[..., None] ** 0.72) * 0.88
        rgb += 30 * magnitude[..., None] ** 4
        texture = np.clip(rgb, 0, 255).astype(np.uint8)
        # Nearest-neighbor preserves separate cells, including the 44 x 128 GNN.
        width, height = round(shape[1] * cell), round(shape[0] * cell)
        texture = cv2.resize(texture, (width, height), interpolation=cv2.INTER_NEAREST)
        if cell >= 2:
            texture[np.arange(height) % max(2, round(cell)) == 0] //= 2
            texture[:, np.arange(width) % max(2, round(cell)) == 0] //= 2
        # Orthographic tilted plate with a solid side face, no fake tensor depth.
        shift = int(width * 0.24) + 2
        matrix = np.array([[1, 0.48, 1], [-0.24, 1, shift]], dtype=np.float32)
        out_size = (width + int(height * 0.48) + 3, height + shift + 3)
        rgba = np.dstack((texture, np.full((height, width), 255, np.uint8)))
        warped = cv2.warpAffine(rgba, matrix, out_size, flags=cv2.INTER_NEAREST)
        x, y = xy
        corners = [
            (x + 1, y + shift),
            (x + width + 1, y + 2),
            (x + width + height * 0.48, y + height + 2),
            (x + height * 0.48, y + height + shift),
        ]
        draw = ImageDraw.Draw(layer)
        draw.polygon(
            [
                corners[0],
                corners[3],
                (corners[3][0], corners[3][1] + 7),
                (corners[0][0], corners[0][1] + 7),
            ],
            fill=(24, 38, 57, 255),
        )
        layer.alpha_composite(Image.fromarray(warped), (x, y))
        draw.line([*corners, corners[0]], fill=(*color, 130), width=1)

    def network(self, overlay: Image.Image, row: int) -> None:
        if row == self.cached_row:
            overlay.alpha_composite(self.cached_network)
            return
        layer = Image.new("RGBA", overlay.size)
        draw = ImageDraw.Draw(layer)
        label = film.write
        label(draw, (1220, 198), "READING THE ROAD", 18, film.AQUA)
        for i, suffix in enumerate(("node_in", "norms.0", "norms.1")):
            x = 1220 + i * 222
            self.plate(
                layer, row, f"encoder.track_conv.0.{suffix}", (x, 260), (44, 128), 1.45, film.AQUA
            )
            label(draw, (x, 399), "44 x 128", 16, film.MUTED)
            if i < 2:
                draw.line((x + 218, 324, x + 221, 324), fill=(*film.AQUA, 160), width=2)
        # Track and motion are parallel inputs, not successive neural layers.
        self.plate(layer, row, "pooled", (1270, 454), (8, 16), 4, film.AQUA)
        self.plate(layer, row, "motion", (1460, 454), (12, 16), 4, film.CYAN)
        label(draw, (1265, 530), "ROAD 128", 16, film.MUTED)
        label(draw, (1460, 530), "MOTION 192", 16, film.MUTED)
        draw.line((1760, 425, 1760, 434, 1320, 434, 1320, 443), fill=(*film.AQUA, 80), width=1)
        draw.line((1320, 550, 1320, 575, 1580, 575), fill=(*film.AQUA, 100), width=1)
        draw.line((1500, 550, 1500, 575), fill=(*film.CYAN, 100), width=1)
        label(draw, (1220, 596), "SHAPING THE DECISION", 18, film.CYAN)
        for i in range(4):
            x = 1220 + i * 166
            key = f"encoder.backbone.blocks.{i}"
            # Both are genuine module outputs. Expansion is before ReLU.
            self.plate(layer, row, key + ".expand", (x, 652), (24, 32), 3.4, film.CYAN)
            self.plate(layer, row, key, (x + 24, 803), (12, 16), 3.4, film.AQUA)
            label(draw, (x + 25, 765), "768", 16, film.MUTED)
            label(draw, (x + 32, 864), "192", 16, film.MUTED)
            draw.line((x + 61, 782, x + 61, 798), fill=(*film.CYAN, 150), width=2)
            # Residual bypass is a topology guide, not a claimed attribution.
            draw.line(
                (x + 143, 652, x + 153, 652, x + 153, 840, x + 99, 840),
                fill=(*film.AQUA, 80),
                width=1,
            )
            if i < 3:
                draw.line(
                    (x + 104, 856, x + 164, 856, x + 164, 639, x + 227, 639),
                    fill=(*film.CYAN, 65),
                    width=1,
                )
        label(draw, (1220, 922), "DRIVING SIGNAL", 18, film.AQUA)
        self.plate(layer, row, "state", (1600, 894), (6, 32), 3, film.AQUA)
        # One restrained bloom pass keeps actual bright elements sharp.
        crop = layer.crop((1190, 180, 1920, 977))
        glow = crop.filter(ImageFilter.GaussianBlur(5))
        glow.putalpha(glow.getchannel("A").point(lambda value: int(value * 0.28)))
        result = Image.new("RGBA", overlay.size)
        result.alpha_composite(glow, (1190, 180))
        result.alpha_composite(layer)
        overlay.alpha_composite(result)
        self.cached_row, self.cached_network = row, result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--finish-time", default=None)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    evidence = json.loads((args.capture / "internal-tensors.json").read_text())
    _, best, data = film.choose_trial(args.capture)
    archive = args.capture / "internal-tensors.npz"
    if (
        digest(archive) != evidence["tensor_sha256"]
        or best["capture_sha256"] != evidence["capture_sha256"]
    ):
        raise ValueError("Internal tensor provenance mismatch")
    if evidence["sampled_decisions"] != list(range(len(data["action"]))):
        raise ValueError("Every decision must be verified before tensor export")
    with np.load(archive, allow_pickle=False) as tensors:
        TensorComposition.tensors = {key: tensors[key] for key in tensors.files}
    film.Composition = TensorComposition
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report = film.render(args)
    report.update(
        {
            "internal_tensor_sha256": evidence["tensor_sha256"],
            "tensor_shapes": evidence["tensor_shapes"],
            "visual_abstraction": (
                "All elements of selected tensors, fixed row-major layouts. "
                "Plate thickness is decorative. Lines indicate topology, not attribution."
            ),
        }
    )
    args.output.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
