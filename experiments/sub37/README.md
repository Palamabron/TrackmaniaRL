# Sub-37 result on the TMRL test track

This folder exists only to reproduce the 36.976667 s mean reported for the TMRL
test track. It is not part of the installed library and is not a general solution
for driving other maps.

The successful `neighbors` variant wraps the existing V107I policy. Between 54%
and 90% track progress it compares the current observation with complete laps in
the checkpoint's replay. It selects the 15 closest replay states from this same
map and masks actions that did not occur in those states. The original network
then chooses the highest-valued action left by the mask. The wrapper falls back to
the original policy when the car is outside that section, nearly stopped, or too
far from every reference state.

The replay is fixed before evaluation and the wrapper does not train or change any
model weights. Its progress range, feature scaling, distance threshold, action
layout, and reference laps were chosen for this map. Using the same code on a
different map is not expected to work.

The folder also keeps the variants that failed during screening. The normal
`trackmaniarl benchmark` command does not load any of them.

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

These modules replace the old `scripts.sub37_experiments` and
`trackmaniarl.experiments.sub37_*` paths. No compatibility aliases remain.
