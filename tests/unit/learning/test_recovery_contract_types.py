from typing import Any

import pytest

from trackmaniarl.trackmania.imitation_learning import RecoveryContract


@pytest.mark.parametrize(
    ("name", "value"),
    [
        ("map_uid", 17),
        ("geometry_sha256", 17),
        ("action_repeat_frames", True),
        ("action_repeat_frames", 1.5),
        ("decision_interval_ms", True),
        ("decision_interval_ms", "50"),
    ],
)
def test_recovery_contract_rejects_invalid_field_types(name: str, value: Any) -> None:
    fields = {
        "map_uid": "map",
        "geometry_sha256": "a" * 64,
        "action_repeat_frames": 1,
        "decision_interval_ms": None,
        "control_alignment": "frame_start",
    }
    fields[name] = value
    with pytest.raises(ValueError, match="recovery"):
        RecoveryContract(**fields)
