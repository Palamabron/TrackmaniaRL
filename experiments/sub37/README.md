# V108 single-map reproduction (not part of the installed library)

This folder preserves all candidate controllers from the 8 September 2026
experiment, including failed screens. Only `neighbors` passed the fresh 30-trial
confirmation. It restricts the checkpoint's Q-ranked actions to those supported
by 15 nearest replay states in a fixed progress window. Reference states are
frozen before evaluation. No model weights are trained by this runner.

The progress window, 78-action layout, feature scales and replay selection are
specific to the recorded experiment. They must not be assumed valid on other
maps. The default library CLI never imports this folder. General graph/recovery
components used by the checkpoint remain in `trackmaniarl.experiments`.

From a source checkout, supply explicit paths:

```powershell
uv run python -m experiments.sub37.runner benchmark --variant neighbors --trials 30 --config PATH_TO_MATCHING_CONFIG --checkpoint PATH_TO_V107I_CHECKPOINT
```

Required local assets: the V107I checkpoint with its original replay, the matching
map and geometry, and the V107J feature/model configuration. Hashes, normalized
configuration and all attempt times are in the
[benchmark report](../../docs/benchmarks/2026-09-08-v108-live.md). Private artifacts
are not included in a wheel or claimed to be publicly downloadable. Removing
their replay or changing their map invalidates this reproduction.

`media_scan` identifies restart candidates by visual similarity for manual review.
It does not measure lap times. `export_media` exports the verified original video
using fixed time windows, including all 30 attempts without internal edits.
See [recording documentation](../../docs/recording.md) for the exact commands.

Moving these modules replaces the old `scripts.sub37_experiments` and
`trackmaniarl.experiments.sub37_*` paths; no compatibility aliases remain.
