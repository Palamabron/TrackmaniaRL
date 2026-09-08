"""Optional FFmpeg window recording; FFmpeg is an external executable."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import sleep
from typing import TextIO

_INPUT_OPTIONS = (
    "-hide_banner",
    "-loglevel",
    "warning",
    "-n",
    "-f",
    "gdigrab",
    "-framerate",
    "20",
    "-i",
)
_OUTPUT_OPTIONS = (
    "-an",
    "-c:v",
    "libx264",
    "-preset",
    "ultrafast",
    "-crf",
    "23",
    "-pix_fmt",
    "yuv420p",
)


@dataclass(frozen=True, slots=True)
class RecordingOptions:
    output: Path
    window_title: str = "Trackmania"
    ffmpeg: str = "ffmpeg"


def recording_command(options: RecordingOptions) -> list[str]:
    if sys.platform != "win32":
        raise RuntimeError("Window recording currently supports Windows; use OBS on other hosts")
    executable = shutil.which(options.ffmpeg)
    if executable is None:
        raise FileNotFoundError("FFmpeg not found: install it or pass --ffmpeg PATH")
    if options.output.suffix.lower() != ".mkv":
        raise ValueError("Record to .mkv so an interrupted recording remains recoverable")
    if not options.window_title.strip():
        raise ValueError("recording window title must not be empty")
    return [
        executable,
        *_INPUT_OPTIONS,
        f"title={options.window_title}",
        *_OUTPUT_OPTIONS,
        str(options.output),
    ]


def _write_metadata(options: RecordingOptions, command: list[str]) -> None:
    options.output.parent.mkdir(parents=True, exist_ok=True)
    if options.output.exists():
        raise FileExistsError(f"Refusing to overwrite recording: {options.output}")
    payload = {
        "started_utc": datetime.now(UTC).isoformat(),
        "command": command,
        "audio": False,
        "clock": "video wall time; lap times use game telemetry",
    }
    with options.output.with_suffix(".recording.json").open("x", encoding="utf-8") as file:
        json.dump(payload, file)


def _launch(command: list[str], log: TextIO) -> subprocess.Popen[str]:
    return subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=log,
        text=True,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )


@contextmanager
def _recorder(options: RecordingOptions) -> Iterator[subprocess.Popen[str]]:
    command = recording_command(options)
    _write_metadata(options, command)
    with options.output.with_suffix(".ffmpeg.log").open("x", encoding="utf-8") as log:
        process = _launch(command, log)
        try:
            sleep(0.5)
            if process.poll() is not None:
                raise RuntimeError(f"Window recording failed; inspect {log.name}")
            yield process
        finally:
            _finish_recording(process, options.output)


def _finish_recording(process: subprocess.Popen[str], output: Path) -> None:
    if process.poll() is None:
        try:
            process.communicate("q\n", timeout=20)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            raise RuntimeError(f"Recorder did not finalize; inspect {output}") from None
    if process.returncode != 0:
        log = output.with_suffix(".ffmpeg.log")
        raise RuntimeError(f"Recorder failed with exit {process.returncode}; see {log}")


@contextmanager
def record_window(options: RecordingOptions | None) -> Iterator[None]:
    """Record every trial, including failures; finalize the container on exceptions too."""
    if options is None:
        yield
    else:
        with _recorder(options):
            yield
