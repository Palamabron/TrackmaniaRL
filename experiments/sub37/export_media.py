"""Export the complete V108 confirmation and its best lap from verified source bytes."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path

# Seconds into the original 20 fps, 1280x720 state-aware recording.
# Includes all 30 complete attempts and inter-trial waits, with no internal cuts.
FULL_START = 1102.0
FULL_DURATION = 1168.0
BEST_START = 2190.0
BEST_DURATION = 38.7
RESTARTS = (
    1102.75,
    1141,
    1179.75,
    1218.5,
    1257,
    1295.75,
    1334.25,
    1373,
    1411.75,
    1450.5,
    1489,
    1527.75,
    1566.5,
    1605.25,
    1644,
    1682.75,
    1721.5,
    1760,
    1798.75,
    1837.25,
    1876,
    1914.75,
    1953.5,
    1992,
    2030.75,
    2069.5,
    2112.75,
    2151.25,
    2190.25,
    2228.75,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--ffmpeg", default="ffmpeg")
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--mode", choices=("full", "best", "gif", "contacts"), required=True)
    args = parser.parse_args()
    with args.source.open("rb") as file:
        digest = hashlib.file_digest(file, "sha256").hexdigest()
    if digest != args.source_sha256.lower():
        raise ValueError("Source recording hash mismatch; offsets require the original video")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if args.output.exists():
        raise FileExistsError(args.output)
    start = FULL_START if args.mode in {"full", "contacts"} else BEST_START
    duration = FULL_DURATION if args.mode in {"full", "contacts"} else BEST_DURATION
    command = [args.ffmpeg, "-v", "error", "-n", "-ss", str(start), "-i", str(args.source)]
    if args.mode == "contacts":
        times = [value - 0.4 for value in RESTARTS[1:]] + [2267.6]
        select = "+".join(f"eq(n,{round((value - start) * 20)})" for value in times)
        command += ["-vf", f"fps=20,select='{select}',scale=480:-1,tile=5x6", "-frames:v", "1"]
    elif args.mode == "gif":
        graph = (
            "fps=8,scale=384:-1:flags=lanczos,split[a][b];"
            "[a]palettegen=max_colors=48[p];[b][p]paletteuse=dither=bayer:bayer_scale=4"
        )
        command += ["-t", str(duration), "-filter_complex", graph, "-loop", "0"]
    else:
        command += [
            "-t",
            str(duration),
            "-an",
            "-c:v",
            "libx264",
            "-threads",
            "4",
            "-preset",
            "fast",
            "-crf",
            "20",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
        ]
    subprocess.run([*command, str(args.output)], check=True)


if __name__ == "__main__":
    main()
