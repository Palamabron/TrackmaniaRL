# Troubleshooting

Start with `trackmaniarl validate run.yaml`, then `trackmaniarl track check
--config run.yaml` with the car ready on the intended map. Run `smoke` before a
long training job. Keep the error message, resolved configuration and local logs.

| Symptom | Check and remedy |
| --- | --- |
| No telemetry / connection refused | Confirm the managed plugin is enabled, the game is running and TCP 9000/9001 match the config. Do not run duplicate loose and managed plugins. Check local firewall rules. |
| Protocol or frame-width mismatch | The library expects session protocol 2 and exactly 33 telemetry fields. Check plugin version/source; do not pad or truncate packets. |
| Menu opens and car does not move | Return to editor validation, reset the car and verify that restart controls reset the race clock. School Mode does not permit normal online play. Use the documented finish-confirmation setting for editor validation. |
| Plugin in wrong mode | Enable Openplanet School Mode and use editor validation. Verify the managed plugin in Plugin Manager, not just a copied script. |
| Map UID/hash mismatch | Load the intended local map, rebuild geometry for that exact file and update environment, features and evaluation UID together. The generated geometry is only a placeholder. |
| Skipped telemetry frames | Producer skips and long race-clock steps are different metrics. Reduce competing CPU work, rendering load and recording resolution; check decision cadence and controller timing. Compare fresh complete series. Never remove the slow/skipped attempts to improve the mean. |
| Benchmark gate fails despite finishes | Inspect all trials and configured targets. `--reject-telemetry-skips` rejects the complete series on any skip. Targets are strict for lap time; the maximum step-clock bound is inclusive. |
| No finishes | Inspect failure reasons and progress bins. Verify geometry order, finish extension/gate, speed units and maximum episode duration. Allow time to recover from collisions; check repeated brake actions and demo cadence before changing the model. |
| GPU unused | Check the installed Torch build and learner execution device. CPU-bound game collection can keep a working GPU lightly loaded. See the performance guide before raising update frequency. |
| CUDA unavailable / CPU-only host | Choose the appropriate official Torch wheel before syncing a generated project; its default source is CUDA 12.8. `device: cpu` cannot repair a missing library/driver dependency. |
| Missing W&B credentials | Use the default local JSONL logger, or install/configure the optional W&B integration deliberately. |
| Recorder fails / black recording | Install FFmpeg, check window title, keep Trackmania visible and unminimized. Inspect the `.ffmpeg.log`; recording failure makes the command fail. Run a short recording check before a 30-trial capture. |
| Resume rejects the checkpoint | Check schema 2.0, model architecture, immutable configuration and journal identity. Use a full training checkpoint for exact resume. Warm-start a new run if intentionally changing architecture, with an explicit compatible transfer. |

The library cannot guarantee that a map is learnable with the default reward or
that a model reaches a particular time. Compare finish rate, complete attempt
distribution, training/evaluation policy mode and telemetry before attributing
poor performance to hardware or architecture.
