from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

import pytest

from tests.integration.runtime.core_runtime_support import runtime_spec
from trackmaniarl.core.runtime import resolve_run
from trackmaniarl.core.spec import ComponentSpec


class TrackingLogger:
    instances: ClassVar[list[TrackingLogger]] = []

    def __init__(self, **kwargs: Any) -> None:
        self.closed = 0
        self.instances.append(self)

    def log(self, *args: Any, **kwargs: Any) -> None:
        pass

    def close(self) -> None:
        self.closed += 1


@pytest.mark.parametrize("failure", ["additional_logger", "checkpoint_codec", "contract", None])
def test_resolution_closes_loggers_on_failure_only(tmp_path: Path, failure: str | None) -> None:
    TrackingLogger.instances.clear()
    spec = runtime_spec(tmp_path)
    logger = ComponentSpec(class_path=f"{__name__}:TrackingLogger")
    invalid = ComponentSpec(class_path="trackmaniarl.core.runtime:MissingComponent")
    updates: dict[str, Any] = {"logger": logger, "additional_loggers": (logger,)}
    if failure == "additional_logger":
        updates["additional_loggers"] = (logger, invalid)
    elif failure == "checkpoint_codec":
        updates["checkpoint_codec"] = invalid
    elif failure == "contract":
        updates["checkpoint_codec"] = ComponentSpec(class_path="builtins:object")
    spec = spec.model_copy(update={"components": spec.components.model_copy(update=updates)})
    if failure is None:
        run = resolve_run(spec)
        assert all(logger.closed == 0 for logger in TrackingLogger.instances)
        run.logger.close()
    else:
        with pytest.raises((TypeError, ValueError), match=r"MissingComponent|CheckpointCodec"):
            resolve_run(spec)
    assert len(TrackingLogger.instances) == 2
    assert all(logger.closed == 1 for logger in TrackingLogger.instances)
