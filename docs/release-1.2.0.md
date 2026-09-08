# Release 1.2.0 preparation

Status: local preparation only; no commit, push, merge, tag or publication.

The later [public-library release review](reviews/1.2.0-release-review.md)
supersedes the readiness assessment below. Its current-tree checks pass, but
reachable-history privacy findings and the transitive dependency advisory need
an explicit publication disposition. The older counts below are historical
preparation evidence, not the latest gate results.

## Changes and migration

The own-map starter no longer assumes the TMRL test map or a 37-second target.
Benchmarking supports optional time targets, complete-attempt reporting, unique
output directories, a recording context and an append-only trial timeline.
See [README](../README.md) for installation, geometry, demonstration, training,
resume and benchmark commands; [recording](recording.md) for publication media.

Map-specific V108 action wrappers now live in repository-only
`experiments/sub37/`, outside the wheel. Their runner requires explicit config
and checkpoint arguments. There are no old import aliases. Graph/recovery
components remain opt-in experiments in the library because current models and
recovery training use them. No local checkpoint or training recording was deleted.

Training checkpoints must use schema 2.0 and columnar-v2 replay. Schema 1.0,
columnar-v1 loading and private CLI helper re-exports were removed. The historical
V107I checkpoint already uses the supported format and was loaded successfully;
its weights did not need conversion. Never load untrusted Torch checkpoints.

The reward reference now follows the implementation. Architecture, supported
features, troubleshooting, benchmark provenance and telemetry limitations have
dedicated documentation. The 36.976667 s result remains a map-specific replay
wrapper result, not a newly trained or universal policy.

## Validation on the preparation host

- Regression suite: 638 passed, 1 skipped (19.72 seconds).
- Ruff checks and formatting: passed.
- Mypy: passed for 251 source files.
- Dependency lock check: passed.
- Wheel and source archive built; distribution-content validator passed.
- Wheel installed into a separate target; outside-checkout working-directory
  smoke check verified the installed import path, version, starter generation and
  configuration parsing. This reused existing dependencies, not a fresh download
  and installation of the entire GPU stack.
- Existing V108 recording was inspected to identify all 30 consecutive attempts;
  full-series and best-attempt publication exports were created locally. The
  README GIF is attempt 29. Telemetry reports 36.560 s; the game overlay is 36.568 s.

Reproduce code checks from the repository root:

```powershell
uv sync --group dev
uv run ruff check .
uv run ruff format --check .
uv run mypy trackmaniarl
uv run pytest -o addopts='' tests -q --basetemp=artifacts/release-1.2.0/pytest-verification
uv lock --check
uv build --out-dir artifacts/release-1.2.0/dist
uv run python scripts/check_distribution.py --dist-dir artifacts/release-1.2.0/dist --tag v1.2.0
```

## Remaining limitations

The requested approximate halving of tests has **not** been achieved: the suite
went from 676 collected cases to 639 after removing redundant checks and adding
public-workflow/recording coverage. Line-coverage overlap alone was not used to
delete numerical, failure-handling or data-integrity assertions. Further reduction
requires a separate behavior-level review; these counts must not be presented as
a 50% reduction.

No new live-game validation of the new recording command or own-map training was
performed during this release preparation. Recorder lifecycle/error handling is
tested with a mocked process. Installation on a clean Windows machine, real
FFmpeg window capture and an end-to-end user-map smoke run remain release checks.
Existing benchmark video exports do not substitute for those checks.

The full benchmark contains 458 skipped producer frames. Read the
[evaluation limitations](library-architecture.md#dropped-telemetry-frames-and-evaluation-validity)
before comparing machines, policies or a strict zero-drop series. No slow attempt
was excluded to obtain the reported mean, and no future sub-37 mean is guaranteed.
