# Camera vision and PPO

This guide applies to TrackmaniaRL 1.2.4 with RunSpec 2.0.

PPO is a supported local on-policy algorithm. The Trackmania project template
generates `run-ppo.yaml` (telemetry) and `run-ppo-vision.yaml` (camera), alongside
the default IQN/lidar `run.yaml`. Configure the map UID, map file and geometry in
the selected file using the usual Trackmania setup instructions.

```powershell
uv run trackmaniarl init my-agent --template trackmania
cd my-agent
uv add "trackmaniarl[trackmania,distributed,vision]"
uv run trackmaniarl validate run-ppo-vision.yaml
uv run trackmaniarl train run-ppo-vision.yaml
uv run trackmaniarl resume run-ppo-vision.yaml artifacts/RUN/checkpoints/CHECKPOINT.pt
uv run trackmaniarl benchmark run-ppo-vision.yaml artifacts/RUN/checkpoints/CHECKPOINT.pt
```

`validate` uses synthetic images and performs a learner update plus a checkpoint
round trip without opening the game or capturing the desktop. For telemetry PPO,
use `run-ppo.yaml`. It does not need the vision extra.

## Image observations

`trackmaniarl.trackmania.vision:VisionFeaturePipeline` accepts RGB `uint8` arrays
with shape `(height, width, 3)`. It resizes with bilinear antialiasing, optionally
converts to grayscale, scales to `[0, 1]`, and concatenates consecutive frames on
the channel axis. Defaults are four grayscale 84x84 frames, giving `(4, 84, 84)`
float32 observations. On reset it repeats the first frame. Replay stores completed
stacks. Sampling a batch does not advance the frame history.

Configure the feature pipeline through `kwargs.config`:

```yaml
config: {width: 84, height: 84, grayscale: true, frame_stack: 4}
```

Match the model factory's `kwargs.channels` to `frame_stack` for grayscale or
`3 * frame_stack` for RGB. The bundled PPO config disables running observation
normalization because image features already have a fixed range.

`trackmaniarl.trackmania.vision_models:VisionPpoModelFactory` supplies independent
CNN encoders for a bounded Gaussian actor and state-value critic. Actions are
`[accelerator, brake, steer]` with bounds `[0, 0, -1]` to `[1, 1, 1]`.
`VisionSensorEncoder` also implements the existing composite value encoder
contract: use it with `CompositeValueModelFactory` and scalar Q, QR, IQN or FQF
heads. Match `output_dim` to the temporal core's `input_dim`.

## Live frame source

`trackmaniarl.trackmania.vision_environment:VisionEnvironmentFactory` wraps the
Openplanet environment. Its `kwargs.config` is the standard Trackmania environment
configuration. `kwargs.capture` selects a desktop rectangle in pixels:

```yaml
capture: {left: 0, top: 0, width: 1280, height: 720}
```

Set this rectangle to the game viewport and keep it visible and unobstructed.
Capture uses the optional [MSS backend](https://python-mss.readthedocs.io/v10.2.0/examples.html),
including conversion from BGRA to RGB. Windows and Linux/X11 desktop capture
depend on the host display. Headless/Wayland capture is not provided by this wrapper.
The feature pipeline and models can also consume RGB frames from a custom environment
without installing MSS. `VisionEnvironment` accepts a `FrameSource` implementation
with `capture()` and `close()` for alternative camera sources.

Each reset/step obtains telemetry and then captures a fresh image. The policy
observes images. Telemetry still drives rewards, progress, finish detection and
controls. Camera and telemetry are not synchronized atomically. The environment
reports `vision/capture_ms` per observation. Keep camera, crop and display settings
consistent between training and evaluation. Telemetry-only demonstration files
cannot train this vision policy because they do not contain image observations.

## PPO lifecycle and resource limits

Use `OnPolicySequenceSampler`, `n_step: 1`, and a replay capacity at least as large
as `training.sequence_length`. PPO collects a fixed number of fresh transitions,
updates for the configured epochs, and starts another rollout. Rollouts may cross
episode boundaries. GAE stops at episode ends and bootstraps time-limit truncations.
`total_transitions` must be divisible by `sequence_length`. Distributed actor/learner
commands remain off-policy only.

The vision template keeps 2048 transitions. Float32 image stacks consume much more
memory than telemetry: two `(4,84,84)` observations per transition require roughly
441 MiB at this capacity, before learner tensors and overhead. Adjust rollout size,
capacity, minibatch size and image size together for the host's RAM/VRAM.

Checkpoints restore model, optimizer, normalizers, learning-rate progress, scaler
and RNG. Resume restarts the live environment and clears image history at an episode
boundary. It cannot restore the running game's exact visual state. Automated tests
exercise synthetic image rollouts and checkpoint continuation, not racing performance.

## How a PPO update works

The actor CNN turns the image stack into a feature vector. The Gaussian head
predicts an action mean and learns a state-independent standard deviation. During
training it samples a latent action, applies `tanh`, and rescales each coordinate
to the accelerator, brake and steering bounds. Evaluation uses the mean instead
of sampling. A separate CNN and value head estimate the future discounted return.

Collection saves the latent action, its behavior-policy log probability and the
value estimate before any optimization. PPO uses those saved values to compare
the updated policy against the policy that actually drove the rollout.

The one-step value error is `reward + bootstrap_discount * next_value - value`.
GAE accumulates these errors backward, decaying them by the discount and
`gae_lambda`. An episode end stops that recursion. A true termination also removes
the next-value bootstrap, while truncation keeps it. Returns are advantages plus
the saved values. Advantages are normalized over the rollout before optimization.

For each minibatch, the probability ratio is
`exp(new_log_probability - behavior_log_probability)`. The policy objective clips
that ratio to `1 ± clip_epsilon`, limiting the incentive for a large change from
the behavior policy. The value objective trains predicted returns and clips the
change from saved values. An entropy bonus encourages exploration, and gradient
clipping limits update size. `target_kl` can stop further epochs when average KL
exceeds the configured threshold. This implementation checks it after each epoch.

Observation-normalizer statistics stay fixed during the rollout's update and are
updated afterward for the next policy snapshot. Reward normalization estimates a
scale from discounted returns and resets its running return at episode boundaries.
The optimizer's learning rate decays linearly with processed transitions. All these
states are saved so continuation uses the same learning schedule.

Monitor `loss/policy`, `loss/value`, `state/entropy`, `state/approx_kl`,
`state/clip_fraction`, `state/early_stop` and `state/learning_rate` alongside finish
rate and progress. Low training loss alone does not establish successful driving.
