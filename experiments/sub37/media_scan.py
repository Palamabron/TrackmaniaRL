"""Locate visually matching restart intervals in the original V108 recording.

This is an aid for manual media verification, not lap-time measurement.
Uses a user-selected reference frame and never chooses attempts by performance.
"""

from __future__ import annotations

import argparse
import json
import subprocess

import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video")
    parser.add_argument("--ffmpeg", required=True)
    parser.add_argument("--reference", type=float, required=True)
    parser.add_argument("--start", type=float, default=1080)
    parser.add_argument("--duration", type=float, default=1200)
    args = parser.parse_args()
    common = [args.ffmpeg, "-v", "error", "-ss"]
    frame = subprocess.check_output(
        [
            *common,
            str(args.reference),
            "-i",
            args.video,
            "-frames:v",
            "1",
            "-vf",
            "scale=80:45",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ]
    )
    raw = subprocess.check_output(
        [
            *common,
            str(args.start),
            "-i",
            args.video,
            "-t",
            str(args.duration),
            "-vf",
            "fps=4,scale=80:45",
            "-f",
            "rawvideo",
            "-pix_fmt",
            "rgb24",
            "-",
        ]
    )
    reference = np.frombuffer(frame, np.uint8).reshape(45, 80, 3).astype(float)
    frames = np.frombuffer(raw, np.uint8).reshape(-1, 45, 80, 3).astype(float)
    errors = ((frames[:, :29] - reference[:29]) ** 2).mean(axis=(1, 2, 3))
    indices = np.flatnonzero(errors < 2500)
    groups = np.split(indices, np.flatnonzero(np.diff(indices) > 1) + 1)
    intervals = [
        {
            "start_s": args.start + float(group[0]) / 4,
            "end_s": args.start + float(group[-1]) / 4,
            "min_mse": float(errors[group].min()),
        }
        for group in groups
        if len(group) >= 2
    ]
    print(json.dumps(intervals, indent=2))


if __name__ == "__main__":
    main()
