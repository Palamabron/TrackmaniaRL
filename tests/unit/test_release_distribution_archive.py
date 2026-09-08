from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from scripts import check_distribution


def test_wheel_validation_accepts_windows_text_line_endings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    source = Path("trackmaniarl") / "module.py"
    source.parent.mkdir()
    source.write_bytes(b"value = 'built'\r\n")
    archive = tmp_path / "package.whl"
    with zipfile.ZipFile(archive, "w") as package:
        package.writestr("trackmaniarl/module.py", source.read_bytes())
    with zipfile.ZipFile(archive) as package:
        check_distribution._validate_wheel_checkout_files(package, archive)
