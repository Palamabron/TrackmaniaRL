# Record and publish a benchmark

On Windows, install FFmpeg separately and keep Trackmania visible and unminimized.
The recorder targets that window, excludes audio and runs for the entire
benchmark, including resets, slow trials and failures:

```powershell
trackmaniarl benchmark run.yaml artifacts/YOUR_RUN/checkpoints/YOUR_CHECKPOINT.pt --trials 30 --min-finish-rate 1 --record recordings/benchmark.mkv
```

Use `--ffmpeg PATH` when FFmpeg is not on PATH and `--window-title TITLE` when
the window has another title. Existing output files are never overwritten.
The `.recording.json` sidecar stores launch time and encoding arguments;
`.ffmpeg.log` records capture errors. `evaluation-timeline.jsonl` stores UTC
trial boundaries and completed results even if a later attempt fails.
Recorder launch time and trial timestamps help editing, but inspect the video
before publishing: startup latency is not an exact frame synchronization signal.

Recording consumes CPU and storage and may change telemetry quality. Declare
recording settings before collecting the series, report skips and long clock
steps and do not selectively repeat unsuccessful attempts. The default game
recorder is Windows-only; use an external recorder for other display setups.
Local recordings are ignored by Git and never included in Python wheels.

## September 2026 publication assets

The original `v108-night-20260908-state-aware.mkv` lasts 38:06.05 at 1280×720.
Visual restart matching identifies the 30 sequential confirmation attempts;
the first starts near 18:23 and the final finish near 37:47. The publication
window is **1102.0–2270.0 seconds**, with no internal cuts. This excludes earlier
candidate screening but preserves every confirmation attempt and its waits.
The best attempt is number **29**, window **2190.0–2228.7 seconds**.

The original recording SHA-256 is
`5ca18480ed6a26868f65558989bd28d5fa4e7aaffeff63e49a8e007db32dbe3a`.
Re-export from repository root with this original source:

```powershell
$Source = 'my-trackmania-agent/artifacts/v108-night-20260908-state-aware.mkv'
$Digest = '5ca18480ed6a26868f65558989bd28d5fa4e7aaffeff63e49a8e007db32dbe3a'
uv run python -m experiments.sub37.export_media "$Source" artifacts/publication/full-30.mp4 --source-sha256 "$Digest" --mode full
uv run python -m experiments.sub37.export_media "$Source" artifacts/publication/best.mp4 --source-sha256 "$Digest" --mode best
uv run python -m experiments.sub37.export_media "$Source" artifacts/publication/best.gif --source-sha256 "$Digest" --mode gif
```

Output is H.264/yuv420p MP4 for YouTube and a 384-pixel-wide 8 fps GIF at original
speed. The current publication files are local under `artifacts/release-1.2.0/`;
the selected GIF is versioned at `docs/assets/v108-neighbors-best.gif`.
The raw benchmark uses a telemetry-clock reading of **36.560 s** for the best
trial; the recorded game finish overlay shows **36.568 s**. Both are disclosed;
the overlay is not altered to match the telemetry. The original clock-based
statistics remain unchanged and are not represented as millisecond-exact UI times.

Suggested YouTube title: **TrackmaniaRL — all 30 attempts, V107I + map-specific
neighbors (36.977 s telemetry mean)**.

Description should link the full report and state: unchanged V107I weights,
map-specific replay action support, all 30 attempts included, 30/30 finishes,
36.976667 s telemetry mean, 41.370 s worst, 458 skipped producer frames,
and no claim of generalization or zero-drop timing. The shorter best-lap clip
illustrates the best attempt only; it is not evidence for the mean by itself.
