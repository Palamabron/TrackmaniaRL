# TrackmaniaRL

A Python library for training reinforcement-learning agents on your own Trackmania
2020 maps. Prepare map geometry, record or reuse demonstrations, train locally or
with remote actors, resume checkpoints, and benchmark every attempt with telemetry
diagnostics. No pretrained model, private assets or W&B account is required.

This source tree targets **1.2.0**, Python **3.12**, RunSpec **2.0** and training
checkpoint schema **2.0**. Trackmania runs on Windows; offline training and remote
learners can run on other supported PyTorch platforms. This is beta software.

## Install and create your project

With Python 3.12 and [uv](https://docs.astral.sh/uv/) installed:

```powershell
uv tool install "trackmaniarl==1.2.0"
trackmaniarl init my-agent --template trackmania
cd my-agent
uv sync
uv run trackmaniarl validate run.yaml
```

Before 1.2.0 is published, install the prepared wheel with
`uv tool install path/to/trackmaniarl-1.2.0-py3-none-any.whl`, or run
`uv sync --group dev` and `uv run trackmaniarl init my-agent --template trackmania`
from this checkout. Generated projects contain a synthetic geometry placeholder
so validation can run without the game. **Replace it before driving.**

The generated Trackmania project declares the distributed dependencies and pins
the vetted virtual-gamepad fork. Its installer may provision ViGEmBus on Windows.
For an existing project, install `trackmaniarl[trackmania,distributed]` and follow
the [controller setup](readme/trackmania.md); the public extra does not install the
Git-pinned gamepad dependency. Choose a PyTorch build matching your GPU; generated
projects select CUDA 12.8 on Windows/Linux. CPU users must change that source
before syncing. W&B is optional (`wandb` extra plus an explicit logger).

## Prepare your own map

You need Trackmania 2020, Openplanet in School Mode, and the managed
**TrackmaniaRL Connect / SAC_GetData** plugin with the expected telemetry and
session protocol. The repository includes its 2.4.0 reference source. Install and
check the signed plugin through Plugin Manager; see the
[environment setup](readme/trackmania.md) and
[plugin guide](trackmaniarl/project/openplanet/README.md).

Load your map in the editor's validation mode, with the car ready to drive.
School Mode disables ordinary online play. Telemetry uses localhost TCP **9000**;
session readiness and map identity use **9001**. Do not expose them publicly.

```powershell
uv run trackmaniarl track check
uv run trackmaniarl track record-boundary left assets/my-map-left.npy
uv run trackmaniarl track record-boundary right assets/my-map-right.npy
uv run trackmaniarl track build-geometry assets/my-map.geometry.npz --left assets/my-map-left.npy --right assets/my-map-right.npy --map-uid YOUR_MAP_UID --map-path maps/my-map.Map.Gbx
```

Drive each boundary from start to finish in the same direction. Copy your map to
`maps/my-map.Map.Gbx`. Replace `REPLACE_WITH_YOUR_MAP_UID` in all three places
in `run.yaml` with the UID reported by `track check`. The generated configuration
is also available as [a complete example](examples/own-map.yaml).
Map selection is manual; the library verifies the loaded map rather than loading
arbitrary maps through an undocumented game API.

## Train, reuse demonstrations and resume

```powershell
uv run trackmaniarl validate run.yaml
uv run trackmaniarl track check --config run.yaml
uv run trackmaniarl smoke run.yaml --transitions 100
uv run trackmaniarl train run.yaml
```

The default model is a lidar encoder and dueling IQN with 78 control actions.
Training is asynchronous: an actor drives while a learner updates replay.
Use a fresh run ID when changing immutable configuration.

Optional human demonstrations can seed the same training path:

```powershell
uv run trackmaniarl track record-demo demonstrations --config run.yaml --count 5
uv run trackmaniarl train run.yaml --demo demonstrations
uv run trackmaniarl resume run.yaml artifacts/YOUR_RUN/checkpoints/YOUR_CHECKPOINT.pt
```

Use the actual checkpoint path produced by your run. Exact resume restores
training state; `train --model-initialization-checkpoint PATH` starts a new run
from compatible weights. A policy-only checkpoint cannot resume an optimizer.
Demo recording intentionally filters training data; benchmark attempts are
never filtered to improve reported times. See [demonstrations and recovery](readme/imitation-learning.md)
and [checkpoint migration](readme/migration-2.0.md).

## Benchmark and record evaluation

With the matching map ready:

```powershell
uv run trackmaniarl benchmark run.yaml artifacts/YOUR_RUN/checkpoints/YOUR_CHECKPOINT.pt --trials 30 --min-finish-rate 1
uv run trackmaniarl benchmark run.yaml artifacts/YOUR_RUN/checkpoints/YOUR_CHECKPOINT.pt --trials 30 --min-finish-rate 1 --record recordings/benchmark.mkv
```

Recording requires FFmpeg on PATH (or `--ffmpeg PATH`) and a visible Windows
window titled `Trackmania` (or `--window-title TITLE`). It records the full
evaluation without audio and closes the recording on completion or error.
See [recording and publication](docs/recording.md).

Each benchmark has a fresh output directory, a complete `evaluation.json` and
an append-only trial timeline. Finish times come from the game telemetry clock,
not video duration. A DNF remains an attempt; mean/median finish time is
conditional on finishing and must always be accompanied by finish rate.
Optional `--target-mean`, `--target-median`, `--max-step-race-time-ms` and
`--reject-telemetry-skips` define acceptance gates. A failed gate retains the
evidence and returns a failing exit status. No gate discards a slow trial.

## Recorded result — one map, experimental controller

| Policy | Finishes | Mean | Median | Best | Worst |
| --- | --- | --- | --- | --- | --- |
| V107I checkpoint, ordinary policy (screening) | 10/10 | 38.061 s | — | 36.630 s | 42.430 s |
| V107I + optional `neighbors` (fresh confirmation) | 30/30 | 36.976667 s | 36.835 s | 36.560 s | 41.370 s |

The confirmation used a **map-specific replay-based action filter**, with unchanged
V107I weights. It is not a universal pretrained model or ordinary checkpoint
evaluation. The 10-trial baseline is a smaller screening series, not a matched
30-trial comparison. All 30 confirmation attempts count, including 41.370 s.
There were 458 skipped producer frames; this was not a zero-drop benchmark.
The mean has only a 0.023333 s margin below 37 s and does not guarantee repetition.

[Full report and all times](docs/benchmarks/2026-09-08-v108-live.md) ·
[Optional source reproduction](experiments/sub37/README.md)

![Trial 29 of 30, V107I plus map-specific neighbors](docs/assets/v108-neighbors-best.gif)

*Trial 29 from the complete 8 September confirmation. Benchmark telemetry reports
36.560 s; the in-game finish overlay reads 36.568 s. Full-lap excerpt at normal
speed; unchanged network weights plus the optional map-specific wrapper.*

## Documentation and supported surface

| Topic | Guide |
| --- | --- |
| Model, observations, actions and public API | [Library architecture](docs/library-architecture.md), [SDK](readme/sdk.md) |
| Configuration and component contracts | [Configuration reference](readme/configuration.md) |
| Every reward term, units and tuning | [Reward function](docs/reward-function.md) |
| Replay, n-step returns and temporal models | [Replay and sequences](readme/replay-and-sequences.md) |
| Algorithms and limitations | [Algorithm support matrix](readme/algorithms.md) |
| Demonstrations, BC, DAgger and recovery | [Imitation learning](readme/imitation-learning.md) |
| Process boundaries and distributed training | [Runtime architecture](readme/architecture.md) |
| Metrics and performance | [Observability](readme/observability.md), [Performance](readme/performance.md) |
| Connection, menus, telemetry, GPU/CPU | [Troubleshooting](docs/troubleshooting.md) |
| Optional and repository-only experiments | [Support status](docs/support-status.md) |
| Development, tests and releases | [Development](readme/development.md), [Contributing](CONTRIBUTING.md), [Changelog](CHANGELOG.md) |

PPO uses the local on-policy Trainer API, not the asynchronous actor/learner CLI.
Graph recovery encoders, trajectory optimisation and orchestration strategies are
opt-in experiments; their tests establish contracts, not general performance.
There is no supported camera-vision training pipeline in the starter project.
Configs import Python objects: run only trusted configurations and checkpoints.

## Development

```powershell
uv sync --group dev
uv run ruff check .
uv run mypy trackmaniarl
uv run pytest -o addopts='' tests
uv build
uv run python scripts/check_distribution.py
```

TrackmaniaRL originated from TMRL; see [NOTICE](NOTICE) and [MIT license](LICENSE).
It is not affiliated with Ubisoft, Nadeo or the TMRL maintainers.
See the [security policy](SECURITY.md) for trust boundaries.
