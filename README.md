# TrackmaniaRL

![TrackmaniaRL logo](https://raw.githubusercontent.com/Palamabron/TrackmaniaRL/v1.2.9/docs/assets/trackmaniarl-logo.png)

TrackmaniaRL is a Python library for training reinforcement-learning agents on
custom Trackmania 2020 maps. It covers map geometry, demonstrations, asynchronous
training, checkpoint resume and repeatable evaluation.

The Python package and game integration support Windows and desktop Linux. On Linux,
Trackmania runs through Proton and is not officially supported by Ubisoft Nadeo, so
the game setup is experimental. WSL is not a supported game host.
Version 1.2.9 requires Python 3.12 and uses RunSpec 2.0 and checkpoint schema 2.0.

## Installation

Install [uv](https://docs.astral.sh/uv/), then create a project:

```powershell
uv tool install "trackmaniarl==1.2.9"
trackmaniarl init my-agent --template trackmania
cd my-agent
uv sync
```

To install a locally built wheel instead:

```powershell
uv tool install path\to\trackmaniarl-1.2.9-py3-none-any.whl
```

To work from this repository, run `uv sync --group dev` and prefix commands with
`uv run`.

For a game-free installation check, generate the small SDK starter instead:

```powershell
trackmaniarl init sdk-check --template starter
cd sdk-check
uv sync
uv run trackmaniarl inspect-config run.yaml
uv run trackmaniarl validate run.yaml
```

Validation executes trusted component code and a synthetic update. It does not
drive the game or establish driving performance. CPU execution is sufficient for
this check. Live neural inference and training benefit from an NVIDIA GPU with
a compatible PyTorch build. See [platform and performance guidance](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/readme/performance.md).

## Neural inference in motion

![Full drive alongside road, car and context branches, residual blocks, action values and changing steering and pedal controls](https://raw.githubusercontent.com/Palamabron/TrackmaniaRL/v1.2.9/docs/assets/trackmaniarl-neural-flow.gif)

This full drive shows a selected evaluation lap from the contributor's strongest
checkpoint for this map. The contributor reports approximately 12 wall-clock hours
of training before the recording; capturing and rendering the film did not update
its weights. The panel is an architecture showcase: it follows map-relative road
geometry, a 60-value car/physics vector and 29 engineered driving-context values
through the model to action scores and selected controls. The changing activation
colours show real tensor values, but they are not feature attribution and individual
cells are not intended to explain a decision by themselves. This selected lap uses
the map-specific `neighbors` action filter. It is neither an unassisted-policy
benchmark nor evidence of generalization. See [the model and recording explanation](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/docs/activation-film.md)
for provenance, the five-attempt film series and [GIF reproduction](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/docs/neural-flow-media.md).

## Game setup

You need:

- Trackmania 2020 on Windows, or on desktop Linux through Steam and Proton
- Openplanet in School Mode
- the **TrackmaniaRL Connect / SAC_GetData** plugin
- your map open in the editor's validation mode, with the car at the start.

The plugin uses TCP ports 9000 (telemetry) and 9001 (session and map status) on
localhost. The setup guide explains plugin installation and controller setup:
[Trackmania setup](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/readme/trackmania.md).

On Linux, install Trackmania with Steam/Proton, run the Openplanet installer in
Trackmania's Proton prefix and grant your user access to `/dev/uinput`. The setup
guide includes the complete Linux procedure and a virtual-gamepad smoke test.

Check the connection before recording data or training:

```powershell
uv run trackmaniarl track check
```

## Configure a map

Record both track boundaries from start to finish, then build the geometry file:

```powershell
uv run trackmaniarl track record-boundary left assets/my-map-left.npy
uv run trackmaniarl track record-boundary right assets/my-map-right.npy
uv run trackmaniarl track build-geometry assets/my-map.geometry.npz `
  --left assets/my-map-left.npy `
  --right assets/my-map-right.npy `
  --map-uid YOUR_MAP_UID `
  --map-path maps/my-map.Map.Gbx
```

Copy the map to `maps/`, then replace `REPLACE_WITH_YOUR_MAP_UID` in `run.yaml`
with the UID printed by `track check`. See [examples/own-map.yaml](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/examples/own-map.yaml)
for a complete configuration. TrackmaniaRL verifies the open map but does not
select it for you.

## Train and resume

Validate the configuration and run a short smoke test before a full training run:

```powershell
uv run trackmaniarl validate run.yaml
uv run trackmaniarl track check --config run.yaml
uv run trackmaniarl smoke run.yaml --transitions 100
uv run trackmaniarl train run.yaml
```

The starter project uses a lidar encoder, a dueling IQN policy and 78 discrete
control actions. An actor drives while the learner trains from replay.

For continuous off-policy control, use the generated `run-sac.yaml`,
`run-redq.yaml` or `run-tqc.yaml`. `run-discrete-sac.yaml` provides a categorical
actor-critic with the 78-action table. All four include first-party telemetry models.

Every RL family supports camera observations. The template also generates
`run-q-vision.yaml`, `run-qr-vision.yaml`, `run-iqn-vision.yaml`,
`run-fqf-vision.yaml`, `run-sac-vision.yaml`, `run-redq-vision.yaml`,
`run-tqc-vision.yaml` and `run-discrete-sac-vision.yaml`.
For supervised learning from aligned RGB demonstrations, use `run-bc-vision.yaml`
and the [camera BC guide](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/readme/vision-bc.md).

For local on-policy PPO, use the generated `run-ppo.yaml` (telemetry) or
`run-ppo-vision.yaml` (camera images). Configure the map in the chosen file.
The [vision and PPO guide](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/readme/vision.md) explains camera setup, CNN input,
fresh rollouts and the PPO update cycle.

Demonstrations are optional:

```powershell
uv run trackmaniarl track record-demo demonstrations --config run.yaml --count 5
uv run trackmaniarl train run.yaml --demo demonstrations
```

Resume the full training state from a checkpoint:

```powershell
uv run trackmaniarl resume run.yaml artifacts/RUN/checkpoints/CHECKPOINT.pt
```

To start a new run with compatible weights, use
`train --model-initialization-checkpoint CHECKPOINT.pt`. A policy-only checkpoint
does not contain optimizer or replay state and cannot be used for an exact resume.

## Evaluate a checkpoint

Run every trial and keep the complete result:

```powershell
uv run trackmaniarl benchmark run.yaml artifacts/RUN/checkpoints/CHECKPOINT.pt `
  --trials 30 --min-finish-rate 1
```

Add `--record recordings/benchmark.mkv` to record the Trackmania window. Recording
requires FFmpeg. Use `--ffmpeg PATH` or `--window-title TITLE` when the defaults do
not match your system.

Each benchmark writes `evaluation.json` and an append-only trial timeline. A DNF
still counts as an attempt. Mean and median times cover finished attempts, so report
them together with the finish rate. Telemetry drops are recorded because they can
delay observations and control decisions. `--reject-telemetry-skips` rejects the
whole evaluation. It never removes individual slow attempts.

More detail: [evaluation architecture](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/docs/library-architecture.md#checkpoints-and-evaluation),
[recording](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/docs/recording.md) and [troubleshooting](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/docs/troubleshooting.md).

## Documentation

Start with the [1.2.9 reading guide](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/readme/README.md) for how the components fit
together and the setup-to-evaluation workflow.

- [Configuration](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/readme/configuration.md)
- [Algorithms and supported combinations](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/readme/algorithms.md)
- [Camera vision and PPO](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/readme/vision.md)
- [Metrics and observability](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/readme/observability.md)
- [Platforms and performance](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/readme/performance.md)
- [Model, observations, actions and evaluation](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/docs/library-architecture.md)
- [Neural activation film and repeatable export](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/docs/activation-film.md)
- [Reward function](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/docs/reward-function.md)
- [Demonstrations and recovery](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/readme/imitation-learning.md)
- [Replay and sequences](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/readme/replay-and-sequences.md)
- [Distributed runtime](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/readme/architecture.md)
- [Supported features and contracts](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/docs/support-status.md)
- [Troubleshooting](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/docs/troubleshooting.md)
- [Python API](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/readme/sdk.md)

PPO is a supported local on-policy training path, with telemetry and camera-image
models. `init --template trackmania` also generates `run-ppo.yaml` and
`run-ppo-vision.yaml`. See [camera vision and PPO](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/readme/vision.md) for setup.
Graph-based recovery supports incident-gated adapter training. Configuration files
and PyTorch checkpoints can execute Python. Only use files you trust.

## Development

```powershell
uv sync --group dev
uv run ruff format --check .
uv run ruff check .
uv run mypy --strict trackmaniarl
uv run pytest
uv build
uv run python scripts/check_distribution.py
```

TrackmaniaRL is released under the [MIT license](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/LICENSE). It originated from TMRL.
Attribution is in [NOTICE](https://github.com/Palamabron/TrackmaniaRL/blob/v1.2.9/NOTICE). It is not affiliated with Ubisoft or Nadeo.
