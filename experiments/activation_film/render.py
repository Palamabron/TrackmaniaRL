"""Render the fastest finished attempt as a concise neural driving film."""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
from pathlib import Path
from typing import Any

import cv2
import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from experiments.sub37.audit_activation_sources import digest

W, H, FPS = 1920, 1080, 30
INTRO, OUTRO = 1.6, 2.6
WHITE = (244, 248, 255)
MUTED = (166, 180, 204)
INK = (7, 10, 24)
AQUA = (31, 232, 214)
CYAN = (61, 178, 255)
VIOLET = (144, 98, 255)
PINK = (255, 72, 164)
STAGE_SPECS = (
    ("TRACK GNN", "encoder.track_conv.0", AQUA),
    ("TRACK", "encoder.track_conv", CYAN),
    ("MOTION", "encoder.physics_proj", (88, 142, 255)),
    ("FUSION", "encoder.backbone.input_projection", VIOLET),
    ("CORE", "encoder.backbone.blocks.3", (203, 83, 255)),
    ("STATE", "encoder", PINK),
    ("DECISION", "q", (255, 131, 89)),
)
SATELLITES = (
    ("CONTEXT", "encoder.context_adapter", (75, 202, 255)),
    ("TRACK SHAPE", "encoder.spatial_adapter", (112, 126, 255)),
    ("RECOVERY", "encoder.recovery_adapter", (246, 83, 172)),
)


def font(size: int) -> Any:
    for path in (
        "C:/Windows/Fonts/bahnschrift.ttf",
        "C:/Windows/Fonts/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    raise FileNotFoundError("Bahnschrift or DejaVu Sans is required")


FONTS = {size: font(size) for size in (16, 18, 20, 22, 26, 30, 38, 48, 76, 104)}


def write(  # noqa: PLR0913
    draw: Any, xy: tuple[int, int], value: str, size: int, fill: tuple = WHITE
) -> None:
    draw.text(xy, value, font=FONTS[size], fill=fill)


def source_epoch(log: str) -> float:
    match = re.search(r"demuxer -> .*?pkt_pts_time:([0-9.]+)", log)
    if match is None:
        raise ValueError("Original packet timestamp is missing")
    return float(match[1])


def choose_trial(directory: Path) -> tuple[dict[str, Any], dict[str, Any], Any]:
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
    trials = [
        json.loads(line)
        for line in (directory / "trials.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    if len(trials) != manifest["planned_trials"]:
        raise ValueError("The planned recording series is incomplete")
    finished = [item for item in trials if item["finished"] and item["finish_time_s"]]
    if not finished:
        raise ValueError("The recorded series contains no finished lap")
    best = min(finished, key=lambda item: item["finish_time_s"])
    archive = directory / best["capture"]
    if digest(archive) != best["capture_sha256"]:
        raise ValueError("Activation archive hash mismatch")
    data = np.load(archive, allow_pickle=False)
    utc = data["utc"]
    if len(utc) != best["steps"] or not np.all(np.diff(utc) > 0):
        raise ValueError("Decision timestamps are incomplete or nonmonotonic")
    required = {spec[1] for spec in (*STAGE_SPECS, *SATELLITES)}
    if not required.issubset(data.files):
        raise ValueError("Capture predates the full network visualization")
    if any(not np.isfinite(data[name]).all() for name in required - {"q"}):
        raise ValueError("Captured neural activations contain nonfinite values")
    if not np.all(np.isfinite(data["q"]).any(axis=1)):
        raise ValueError("A decision has no finite output value")
    return manifest, best, data


def fit_gameplay(frame: Any) -> Image.Image:
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb).resize((W, H), Image.Resampling.LANCZOS)


def gradient_mask(width: int, height: int) -> Image.Image:
    values = np.zeros((height, width), dtype=np.uint8)
    for x in range(width):
        values[:, x] = int(245 * min(1.0, max(0.0, (x - 40) / 230)))
    return Image.fromarray(values, mode="L")


class Composition:
    def __init__(self, manifest: dict[str, Any], best: dict[str, Any], data: Any) -> None:
        self.manifest = manifest
        self.best = best
        self.data = data
        self.selected: dict[str, np.ndarray] = {}
        self.scales: dict[str, float] = {}
        satellite_names = {item[1] for item in SATELLITES}
        for _, name, _ in (*STAGE_SPECS, *SATELLITES):
            values = np.asarray(data[name])
            finite = np.where(np.isfinite(values), values, np.nan)
            if name == "q":
                finite = finite - np.nanmedian(finite, axis=1, keepdims=True)
            score = np.nanmean(np.abs(finite), axis=0)
            count = 7 if name in satellite_names else 12
            indices = np.argsort(np.nan_to_num(score, nan=-1.0))[-count:]
            self.selected[name] = np.sort(indices)
            chosen = finite[:, self.selected[name]]
            self.scales[name] = max(float(np.nanpercentile(np.abs(chosen), 99)), 1e-6)
        self.panel_mask = gradient_mask(760, H)

    def normalized(self, name: str, row: int) -> np.ndarray:
        values = np.asarray(self.data[name][row, self.selected[name]], dtype=np.float64)
        if name == "q":
            finite = values[np.isfinite(values)]
            values = values - (float(np.median(finite)) if finite.size else 0.0)
        values = np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0)
        return np.clip(values / self.scales[name], -1.0, 1.0)

    @staticmethod
    def node_positions(  # noqa: PLR0913
        x: int, center_y: int, count: int, spacing: int = 31
    ) -> list[tuple[int, int]]:
        first = center_y - (count - 1) * spacing // 2
        return [(x, first + index * spacing) for index in range(count)]

    @staticmethod
    def draw_glow_node(  # noqa: PLR0913
        base: Image.Image,
        position: tuple[int, int],
        value: float,
        color: tuple[int, int, int],
    ) -> None:
        x, y = position
        magnitude = min(1.0, abs(value))
        tone = color if value >= 0 else PINK
        draw = ImageDraw.Draw(base)
        radius = 5 + 5 * magnitude
        for multiplier, opacity in ((2.5, 18), (1.8, 30), (1.35, 48)):
            outer = radius * multiplier
            draw.ellipse(
                (x - outer, y - outer, x + outer, y + outer),
                fill=(*tone, int(opacity * (0.4 + 0.6 * magnitude))),
            )
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            fill=(*tone, int(120 + 135 * magnitude)),
            outline=(*WHITE, 90),
            width=1,
        )

    def network(self, overlay: Image.Image, row: int) -> None:
        draw = ImageDraw.Draw(overlay)
        positions: list[list[tuple[int, int]]] = []
        values: list[np.ndarray] = []
        for index, (label, name, color) in enumerate(STAGE_SPECS):
            x = 1260 + index * 96
            group = self.node_positions(x, 470, len(self.selected[name]))
            positions.append(group)
            current = self.normalized(name, row)
            values.append(current)
            box = draw.textbbox((0, 0), label, font=FONTS[16])
            write(draw, (x - (box[2] - box[0]) // 2, 242), label, 16, color)
        for layer in range(len(positions) - 1):
            source, target = positions[layer], positions[layer + 1]
            for index, start in enumerate(source):
                for offset in (-2, 0, 2):
                    end_index = min(len(target) - 1, max(0, index + offset))
                    strength = math.sqrt(
                        abs(float(values[layer][index] * values[layer + 1][end_index]))
                    )
                    color = STAGE_SPECS[layer + 1][2]
                    draw.line(
                        (*start, *target[end_index]),
                        fill=(*color, int(12 + 75 * strength)),
                        width=1,
                    )
        for group, current, spec in zip(positions, values, STAGE_SPECS, strict=True):
            for point, value in zip(group, current, strict=True):
                self.draw_glow_node(overlay, point, float(value), spec[2])
        for satellite_index, (label, name, color) in enumerate(SATELLITES):
            current = self.normalized(name, row)
            start_x = 1235 + satellite_index * 225
            group = [(start_x + index * 22, 845) for index in range(len(current))]
            write(draw, (start_x, 790), label, 16, color)
            for point, value in zip(group, current, strict=True):
                self.draw_glow_node(overlay, point, float(value), color)
            destination = positions[5 if name == "encoder.recovery_adapter" else 3]
            for index, point in enumerate(group):
                target = destination[round(index * (len(destination) - 1) / max(1, len(group) - 1))]
                draw.line(
                    (*point, *target),
                    fill=(*color, int(15 + 55 * abs(float(current[index])))),
                    width=1,
                )

    def controls(self, overlay: Image.Image, row: int) -> None:
        draw = ImageDraw.Draw(overlay)
        action = int(self.data["action"][row])
        gas, brake, steer = self.manifest["action_table"][action]
        write(draw, (1215, 988), "STEER", 16, MUTED)
        write(draw, (1485, 988), "THROTTLE", 16, MUTED)
        write(draw, (1730, 988), "BRAKE", 16, MUTED)
        center = 1370
        draw.rounded_rectangle((1270, 1026, 1470, 1037), radius=5, fill=(42, 52, 78, 210))
        steering_x = center + int(steer * 95)
        draw.rounded_rectangle(
            (min(center, steering_x), 1026, max(center, steering_x), 1037),
            radius=5,
            fill=(*AQUA, 255),
        )
        draw.ellipse((steering_x - 7, 1021, steering_x + 7, 1042), fill=(*WHITE, 255))
        for x, value, color in ((1535, gas, AQUA), (1775, max(0.0, brake), PINK)):
            draw.rounded_rectangle((x, 1026, x + 120, 1037), radius=5, fill=(42, 52, 78, 210))
            draw.rounded_rectangle(
                (x, 1026, x + max(2, int(120 * value)), 1037),
                radius=5,
                fill=(*color, 255),
            )

    def live_frame(self, gameplay: Any, row: int) -> Image.Image:
        base = fit_gameplay(gameplay).convert("RGBA")
        panel = Image.new("RGBA", (760, H), (*INK, 238))
        base.paste(panel, (1160, 0), self.panel_mask)
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        draw.rounded_rectangle(
            (42, 38, 256, 90), radius=25, fill=(5, 15, 29, 205), outline=(*AQUA, 150)
        )
        draw.ellipse((62, 57, 76, 71), fill=(*AQUA, 255))
        write(draw, (91, 52), "AI IS DRIVING", 20)
        draw.rounded_rectangle((42, 892, 890, 1038), radius=24, fill=(5, 10, 24, 195))
        speed = float(self.data["speed_kmh"][row])
        race_time = float(self.data["race_ms"][row]) / 1000
        progress = float(self.data["progress"][row])
        fields = (
            (70, "SPEED", f"{speed:03.0f} km/h"),
            (334, "TIME", f"{race_time:05.2f}"),
            (598, "TRACK", f"{progress * 100:04.1f}%"),
        )
        for x, label, value in fields:
            write(draw, (x, 920), label, 16, MUTED)
            write(draw, (x, 950), value, 38)
        draw.rounded_rectangle((70, 1012, 850, 1020), radius=4, fill=(42, 52, 78, 210))
        draw.rounded_rectangle(
            (70, 1012, 70 + max(2, int(780 * min(1.0, progress))), 1020),
            radius=4,
            fill=(*AQUA, 255),
        )
        write(draw, (1215, 46), "LIVE NEURAL ACTIVITY", 22, AQUA)
        write(draw, (1215, 82), "From perception to steering", 30)
        write(draw, (1215, 130), "Brightness follows the real signal", 18, MUTED)
        self.network(overlay, row)
        self.controls(overlay, row)
        return Image.alpha_composite(base, overlay).convert("RGB")

    @staticmethod
    def title_card(gameplay: Any, *, closing: bool, display_time: str) -> Image.Image:
        base = fit_gameplay(gameplay).filter(ImageFilter.GaussianBlur(12)).convert("RGBA")
        base = Image.alpha_composite(
            base, Image.new("RGBA", base.size, (*INK, 202 if closing else 218))
        )
        draw = ImageDraw.Draw(base)
        if closing:
            write(draw, (110, 310), "LAP COMPLETE", 22, AQUA)
            write(draw, (110, 352), display_time, 104)
            write(draw, (110, 495), "Driven by a neural network", 30)
        else:
            write(draw, (110, 320), "WATCH AN AI DRIVE", 22, AQUA)
            write(draw, (110, 366), "Trackmania", 104)
            write(draw, (110, 510), "through a neural network", 38)
        draw.rounded_rectangle((110, 615, 560, 623), radius=4, fill=(*VIOLET, 255))
        return base.convert("RGB")


def render(args: argparse.Namespace) -> dict[str, Any]:
    manifest, best, data = choose_trial(args.capture)
    epoch = source_epoch((args.capture / "ffmpeg.log").read_text(encoding="utf-8"))
    start = float(data["utc"][0] - epoch) - 0.15
    end = float(data["utc"][-1] - epoch) + 1.15
    video = cv2.VideoCapture(str(args.capture / "source.mkv"))
    duration = video.get(cv2.CAP_PROP_FRAME_COUNT) / video.get(cv2.CAP_PROP_FPS)
    if not 0 <= start < end <= duration:
        raise ValueError("The selected lap falls outside the source video")
    composition = Composition(manifest, best, data)
    display_time = args.finish_time or f"{best['finish_time_s']:.3f} s"
    command = [
        imageio_ffmpeg.get_ffmpeg_exe(),
        "-v",
        "error",
        "-n",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{W}x{H}",
        "-r",
        str(FPS),
        "-i",
        "pipe:0",
        "-an",
        "-c:v",
        "libx264",
        "-threads",
        "4",
        "-preset",
        "fast",
        "-crf",
        "18",
        "-pix_fmt",
        "yuv420p",
        "-movflags",
        "+faststart",
        str(args.output),
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    total = math.ceil((INTRO + end - start + OUTRO) * FPS)
    ok, upcoming = video.read()
    if not ok:
        raise RuntimeError("Cannot decode the first source frame")
    upcoming_pts = video.get(cv2.CAP_PROP_POS_MSEC) / 1000
    gameplay = upcoming
    try:
        for number in range(total):
            elapsed = number / FPS
            source_time = start + min(max(elapsed - INTRO, 0), end - start)
            while upcoming is not None and upcoming_pts <= source_time:
                gameplay = upcoming
                ok, upcoming = video.read()
                if ok:
                    upcoming_pts = video.get(cv2.CAP_PROP_POS_MSEC) / 1000
                else:
                    upcoming = None
            row = int(
                np.clip(
                    np.searchsorted(data["utc"], epoch + source_time, side="right") - 1,
                    0,
                    len(data["utc"]) - 1,
                )
            )
            live = composition.live_frame(gameplay, row)
            if elapsed < INTRO:
                card = composition.title_card(gameplay, closing=False, display_time=display_time)
                frame = Image.blend(live, card, min(1.0, (INTRO - elapsed) / 0.25))
            elif elapsed >= INTRO + end - start:
                card = composition.title_card(gameplay, closing=True, display_time=display_time)
                opacity = min(1.0, (elapsed - INTRO - end + start) / 0.25)
                frame = Image.blend(live, card, opacity)
            else:
                frame = live
            if number in (0, int((INTRO + 8) * FPS), int((INTRO + 25) * FPS), total - 1):
                frame.save(args.output.with_name(f"{args.output.stem}-preview-{number:04}.jpg"))
            process.stdin.write(frame.tobytes())
            if number % 300 == 0:
                print(f"Rendered {number}/{total} frames", flush=True)
        process.stdin.close()
        if process.wait() != 0:
            raise RuntimeError("Video encoder failed")
    finally:
        video.release()
        if process.poll() is None:
            process.kill()
            process.wait()
    return {
        "selected_attempt": best["trial_index"] + 1,
        "telemetry_finish_time_s": best["finish_time_s"],
        "display_time": display_time,
        "source_start_s": start,
        "source_end_s": end,
        "source_sha256": digest(args.capture / "source.mkv"),
        "activation_sha256": best["capture_sha256"],
        "checkpoint_sha256": manifest["checkpoint_sha256"],
        "displayed_channels": {
            name: indices.tolist() for name, indices in composition.selected.items()
        },
        "activation_scales": composition.scales,
        "frames": total,
        "fps": FPS,
        "output_sha256": digest(args.output),
        "alignment": "Original packet timestamps mapped to decision UTC, previous activation held",
        "visual_abstraction": "Representative real channels and co-activity links",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument(
        "--finish-time", help="Verified in-game finish text, for example '36.722 s'"
    )
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    report = render(args)
    args.output.with_suffix(".json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
