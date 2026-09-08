from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from trackmaniarl.trackmania import recording


class _Process:
    returncode: int | None = None
    finalized = False

    def poll(self) -> int | None:
        return self.returncode

    def communicate(self, command: str, timeout: int) -> None:
        assert command == "q\n"
        assert timeout == 20
        self.finalized = True
        self.returncode = 0


def test_recorder_finalizes_when_evaluation_fails(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    process = _Process()
    monkeypatch.setattr(recording, "recording_command", lambda _: ["ffmpeg"])
    monkeypatch.setattr(recording, "_launch", lambda *_: process)
    monkeypatch.setattr(recording, "sleep", lambda _: None)
    with (
        pytest.raises(ValueError, match="evaluation failed"),
        recording.record_window(recording.RecordingOptions(tmp_path / "all.mkv")),
    ):
        raise ValueError("evaluation failed")
    assert process.finalized
    assert (tmp_path / "all.recording.json").is_file()


def test_recorder_never_overwrites_existing_media(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    output = tmp_path / "all.mkv"
    output.write_bytes(b"original")
    monkeypatch.setattr(recording, "recording_command", lambda _: ["ffmpeg"])

    def unexpected_launch(*_: Any) -> None:
        pytest.fail("Recorder must not start for an existing file")

    monkeypatch.setattr(recording, "_launch", unexpected_launch)
    with (
        pytest.raises(FileExistsError),
        recording.record_window(recording.RecordingOptions(output)),
    ):
        pytest.fail("Evaluation must not start after a recording setup failure")
    assert output.read_bytes() == b"original"
