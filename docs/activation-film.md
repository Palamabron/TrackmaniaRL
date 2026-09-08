# Neural network in action

The finished local film is
`artifacts/activation-film/trackmaniarl-neural-flow-polished.mp4`.
It shows a newly recorded lap without the in-game ghost. Output is 1920 by 1080,
30 fps, H.264/yuv420p and 42.1 seconds long. The English titles are intended for
a general audience and the video has no audio. No training was performed.

The game overlay reports 36.658 s and that value appears in the outro. Telemetry
reports 36.650 s. Both clocks are retained in the evidence.

## New recording and selection

The user authorized fresh driving after the historical source audit found
insufficient inference data. Five attempts were recorded in
`take-03-no-ghost/source.mkv` after disabling the in-game ghost.
The renderer selected the fastest finished attempt after all five completed:

| Attempt | Telemetry finish, s | Skipped telemetry frames |
| --- | --- | --- |
| 1 | 40.820 | 266 |
| 2, selected | 36.650 | 17 |
| 3 | 36.750 | 6 |
| 4 | 36.760 | 16 |
| 5 | 36.860 | 8 |

The five-attempt telemetry mean is 37.568 s. This small series was collected for
a film and does not replace the earlier 30-attempt confirmation. The film makes
no claim that this is an all-time best. The implementation record identifies the
policy as V107I with the optional map-specific `neighbors` action filter. Those
project details are intentionally absent from the video.

The selected archive, `take-03-no-ghost/trial-02.npz`, contains 733 complete
observations, raw telemetry, selected actions, masked action values and the actual
outputs of 12 instrumented neural modules. Its SHA-256 is
`1f81fa2c0bebd85f2e74c751e99bd3da8fda743f50be636ad17fc97e2cb527ed`.
The checkpoint hash is
`4d1973d931a20e4f5874cce1c535be84582658aa05817c46573bf2f2dfa1db01`.

Earlier `take-01` and `take-02` directories are technical iterations. Take 02 is
the complete first film series with the ghost enabled. Take 03 supersedes it.

## Repeat the export

From a source checkout with the local recording and archive present:

```powershell
uv run python -m experiments.activation_film.verify artifacts/activation-film/take-03-no-ghost --full-path
uv run --with imageio-ffmpeg --with opencv-python python -m experiments.activation_film.flow artifacts/activation-film/take-03-no-ghost artifacts/activation-film/neural-drive-new-export.mp4 --finish-time "36.658 s"
```

The enrichment command runs once and refuses to overwrite `path-tensors.npz`.
Skip it when the verified archive already exists. The renderer checks its hash and
requires verification of every decision. The renderer refuses an existing output path.
Dependencies are added to an isolated
uv overlay, not the library's required dependencies. Fonts use Bahnschrift on
Windows or DejaVu Sans on Linux. A JSON sidecar records hashes, selection,
timestamps, displayed channel IDs and normalization scales. Preview JPEGs are
written beside the output. Local recordings and archives are ignored by Git.

To record another fixed series on this same map, using the matching local config
and checkpoint, choose a new empty output directory:

```powershell
$Config = 'my-trackmania-agent/sub37-iqn-gnn-simba-v107j-s17-human-recovery.yaml'
$Checkpoint = 'my-trackmania-agent/artifacts/sub37-iqn-gnn-simba-v107i-s17-incident-gated-recovery/checkpoints/fastest-eval-policy-00000348-at-update-00000433.pt'
uv run --with imageio-ffmpeg python -m experiments.activation_film.capture --config "$Config" --checkpoint "$Checkpoint" --output artifacts/activation-film/new-take --trials 5
uv run python -m experiments.activation_film.verify artifacts/activation-film/new-take
```

Capture requires the visible Trackmania window on the matching map, Openplanet
telemetry and editor validation ready, and the configured controller backend.
It uses the existing experimental evaluator. It is a local publication tool for
this policy, not a generic capture command for every model architecture.

## Current layout and model routing

The film places the complete gameplay frame in a 1152 by 648 area on the left.
The right-hand 768-pixel panel is fully opaque. A compact heading sits above the
gameplay and telemetry, steering wheel and pedal indicators sit below it. The
source image is uniformly resized with no cropping, stretching or overlays.

Numbered sections and arrowheads show the processing order:

1. Road geometry feeds the GNN and an independent Conv1D adapter. The graph path
   pools 44 nodes into 128 features and projects them to 192 through an MLP.
   The Conv1D path contributes a scaled tanh correction to those 192 features.
   Car features go through another MLP, with a separate context MLP correction.
2. The two resulting 192-feature vectors are concatenated. SimBa appends its
   constant shift channel, normalizes, projects to 192 and normalizes again.
   Four residual MLP blocks then run in order from left to right.
3. The gated recovery MLP adds a correction before the IQN head. The head combines
   value and advantage streams over 32 evaluation quantiles into 78 action scores.
   The runtime action filter and selection produce the displayed controls.

The diagram abbreviates the input projection as `384 to 192`. Internally it has
385 inputs because of the constant shift channel. Inside each SimBa block, the
purple skip route bypasses expansion, ReLU and projection. The diamond merge symbol
represents learned elementwise interpolation followed by normalization, not a
plain unweighted addition. Functional activations between module hooks are not
all drawn. The diagram is a readable module overview with selected full tensors.

The visible GNN tensor is the output of its second message-passing step. Conv1D
shows the final dilated residual block's 64 by 44 tensor. Its internal activations
are nonzero, but its final 192-feature correction is exactly zero throughout this
lap, hence `Zero correction / after projection`. This is a zero-valued vector,
not a zero-dimensional layer. Context and motion plates show their module outputs.
The SimBa plates show 768 expansion values before ReLU and 192 block outputs after
mixing and normalization. The IQN plate shows 78 raw expected scores centered on
their median for color contrast. It does not show probabilities or the runtime mask.
Recovery status measures the actual added correction. Values below 1e-8 are
displayed as off.

The wheel rotates by commanded steer times 110 visual degrees. This is a readable
indicator of the normalized command, not a measured steering-wheel angle. Pedals
show commanded throttle and brake. A brake-tap sentinel is labelled `TAP` and shown
as active rather than being incorrectly clamped to zero. These are recorded agent
commands held until the next decision, with no smoothing or invented intermediate
controls. The replay-based action restriction remains documented in provenance
and intentionally has no project-specific caption in the film.

All 733 observations were reprocessed and all original recorded activations and
actions matched exactly. The new `path-tensors.npz` also contains the Conv1D
stages, fusion input, actual recovery correction, both IQN output streams and
their expected action scores. Its SHA-256 is
`cafaf60820da99a323cd9159d23104e7a3dd1d09ce90e0d58ddda7eeff88a507`.
The expected scores reconstructed with NumPy match available live scores within
float32 reduction rounding, with maximum absolute difference 0.000030517578125.
The exporter checks this with absolute and relative tolerances of 1e-5.

## Earlier tensor view

The earlier `tensors` exporter replaces equal-size representative neuron columns with tilted
activation plates. Every cell corresponds to a fixed real tensor element.

| Display | Actual tensor | Display layout |
| --- | --- | --- |
| Road graph input and two message-passing steps | 44 nodes by 128 channels each | 44 by 128, all elements |
| Pooled road representation | 128 | 8 by 16 |
| Motion representation | 192 | 12 by 16 |
| Expansion inside each of four residual blocks | 768 | 24 by 32 |
| Output of each residual block | 192 | 12 by 16 |
| Final encoder state | 192 | 6 by 32 |

The three GNN plates genuinely have the same dimensions. The residual expansion
plates have four times as many cells as their output plates, with the same cell
scale within that comparison. GNN cells use a smaller scale to fit all 5,632 values
per stage. Do not compare screen area across the graph and residual sections as
a common unit. Reshaping a vector into a rectangle is a display convention, not
a spatial structure learned by the model. Plate thickness is decorative.

Turquoise or blue denotes positive values, violet denotes negative values.
Brightness follows absolute activation with a fixed per-tensor 99th-percentile
scale over the selected lap. Values above that scale saturate. Nothing is animated
randomly or interpolated between observations. In particular, expansion tensors
are measured before ReLU, so negative values there are legitimate.

Lines are static routing guides, not learned weights or causal attribution.
The road and motion paths are parallel. The compact view omits the intermediate
road projection, fusion projection, adapter branches and quantile head. It is a
view of selected real internal tensors, not an exhaustive computational graph.
The final plate is the encoder state, not action probabilities. Control bars below
it decode the actual selected action, including the optional replay-based mask.

`internal-tensors.npz` was reconstructed offline from the original checkpoint and
all 733 exact recorded observations. Every original captured module output and
selected action was checked against the live archive. Maximum activation error
was 0.0. The additional tensors have SHA-256
`dc2e201af322576e720c7e135630a1e9297c2358c3b6ed438ded9b4c3a56844f`.
The original gameplay, sample timing, lap selection and finish text are unchanged.

The visual direction takes inspiration from the user's Welch Labs reference.
The suggested Blender pipeline was not treated as evidence about that video's
implementation. This exporter uses Pillow and OpenCV for orthographic plates and
restrained bloom, then FFmpeg for encoding. It adds no renderer to the library.

## Previous dot view

The earlier `render` exporter is retained for comparison. Its panel covers the
route from the track GNN to the discrete decision values.
It includes track features, motion features, fusion, the residual core and final
driving state. Smaller branches show context, track-shape and recovery adapters.
The capture also retains every residual block even though the compact film shows
only the last one.

Each main column displays 12 representative channels. Each smaller branch shows
7. Channels are selected once by mean absolute activation over the chosen lap,
so their identities do not jump between frames. Brightness and radius use actual
activation magnitude normalized by that module's 99th percentile. The complete
128-channel GNN output, 192-channel feature outputs and 78 decision values remain
in the archive. Available decision values are centered on their per-step median
for display. Actions removed by the runtime mask are drawn as inactive.

Lines are representative co-activity links between stage summaries. Their
brightness uses the geometric mean of the endpoint activation magnitudes.
They are explicitly not individual learned synapses or an attribution claim.
Control bars decode the selected discrete action into steering, throttle and
braking. The model has no separate drift output. Project-specific action IDs,
model versions, policy wrappers and benchmark labels are excluded from the film.

The gameplay fills the complete 16:9 frame under a translucent neural panel.
There are no letterbox margins or an inset video border. The full source view,
race clock, car, trajectory and finish remain visible. No slow motion or synthetic
gameplay frames are used. Intro and outro use short fades.

## Synchronization and validation

FFmpeg's gdigrab packet timestamps and Python decision timestamps use the same
host UTC clock. The first original packet timestamp is read from `ffmpeg.log`.
The renderer walks decoded presentation timestamps, not frame number divided
by nominal FPS. This matters because the source recording has missing frames.
The previous available activation sample is held until the next decision.

Visual checks at about 8, 25 and 36 seconds compared the game clock with the
telemetry panel. Observed differences were 0, 40 and 10 ms respectively.
Display latency, 30 fps sampling and telemetry cadence limit precision. This is
timestamp synchronization with visual checks, not a claim of zero-latency
rendering or millisecond-exact game/telemetry clock agreement.

The selected attempt had 17 skipped producer frames and a maximum decision clock
step of 70 ms. These are retained
without time correction. Frame loss does not authorize inventing intermediate
activations. The renderer holds the previous real activation until the next
recorded decision.

The initial verification recomputed 25 decisions spanning the selected lap from
their exact saved observations with the original checkpoint. All 12 activation
modules matched exactly, with maximum absolute error 0.0. All sampled actions
matched. The tensor enrichment subsequently repeated this check for all 733
decisions with the same zero-error result. All 733 recorded actions also match argmax of their saved masked action
values. Details are in `take-03-no-ghost/verification.json`. Ruff checks pass for the new
tools. These checks run offline and do not start another drive.
The final MP4 was decoded end to end with FFmpeg without errors. It contains
1,263 frames at 30 fps and has been visually checked at intro, mid-lap and finish.

## Historical source audit

The earlier best-lap MP4 remains available locally at
`artifacts/release-1.2.0/v108-neighbors-best.mp4`. The following audit explains
why that footage could not be used for an honest activation visualization.

## Available footage

The repository and local Videos, Documents and Downloads folders were searched,
along with the surrounding project directory. Relevant recordings are:

| Recording | Contents |
| --- | --- |
| `my-trackmania-agent/artifacts/v108-night-20260908-state-aware.mkv` | V108 state-conditioned screening and all 30 confirmation attempts |
| `my-trackmania-agent/artifacts/v108-night-20260908-screening.mkv` | Earlier V108 screening variants |
| `artifacts/release-1.2.0/v108-neighbors-all-30.mp4` | Existing export of the full confirmation |
| `artifacts/release-1.2.0/v108-neighbors-best.mp4` | Existing export of confirmation attempt 29 |
| Videos/Captures: `TrackmaniaRL-benchmark-20260906-v106b-v107c.mp4` | Earlier V106B and V107C comparison |
| Videos/Captures: `TrackmaniaRL-benchmark-20260906-v107c-continuation.mp4` | V107C continuation |

Attempt 29 is the best of the 30-trial confirmation, at 36.560 s by telemetry
and 36.568 s on the recorded game overlay. Its previously verified source window
is 2190.0 to 2228.7 seconds. The original video is 720p at 20 fps.
A 1080p/30 fps export would upscale and repeat source frames.

It must not be called the fastest attempt across all experiments. Earlier
`drive-neighbors` screening recorded 36.530 s in the state-aware recording.
That screening series finished 9 of 10 attempts. Its exact video boundaries
have not been verified by this audit.

See [the complete benchmark report](benchmarks/2026-09-08-v108-live.md)
for the controller variants and [recording provenance](recording.md).

## Why inference cannot currently be reconstructed

The frozen historical `policy-source.py` records only `physics[3]`, `physics[0]`,
`context[0]` and the selected action. Attempt 29 contains 731 decisions.
The actual model consumes 361 scalar inputs:

| Input | Shape |
| --- | --- |
| Physics | 60 |
| Track | 3 by 88 |
| Context | 29 |
| Recovery | 8 |

The additional neighbor trace preserves a subset of features only within the
wrapper's active section. Neither trace contains complete observations, hidden
activations or per-decision video timestamps. Evaluation JSON contains aggregate
diagnostics, not the missing observation stream.

The source V107I checkpoint exists and its SHA-256 matches the historical
experiment. Its replay contains 41,128 earlier observation rows. Only 2 of the
731 benchmark decisions even match a replay row's progress and speed exactly.
Matching those two features would still not establish an identical observation.
The checkpoint existed before these evaluation attempts and its replay cannot
serve as their observation recording.

The relevant native game replay found in Documents is a human 36.725 s lap from
April. Human demonstration NPZ files and stitched demonstrations also exist,
including faster times. They do not describe the filmed agent's trajectory.
Running the checkpoint on those inputs would produce real activations for a
different trajectory, which cannot be presented as the filmed decisions.

## Repeat the audit

From the repository root:

```powershell
$Run = 'my-trackmania-agent/artifacts/sub37-v108-benchmark-neighbors-20260907T234730538820'
$Checkpoint = 'my-trackmania-agent/artifacts/sub37-iqn-gnn-simba-v107i-s17-incident-gated-recovery/checkpoints/fastest-eval-policy-00000348-at-update-00000433.pt'
$Video = 'my-trackmania-agent/artifacts/v108-night-20260908-state-aware.mkv'
uv run python -m experiments.sub37.audit_activation_sources "$Run" "$Checkpoint" "$Video"
```

The completed local audit is `artifacts/activation-film/source-audit.json`.
Use `--output PATH` to save another audit. Existing output files are refused.
This command checks the checkpoint hash and reports the video hash, input shapes
and replay matches. It does not render a film or certify frame synchronization.

## Requirements established by the historical audit

To show actual neural activity, a new run needs a simultaneous video recording
and capture of model activations or complete inputs. Record each decision's race
clock and capture timestamps, the exact weights, chosen action and any action
mask. Hooks must observe the forward pass used to select the action. Logging
overhead and telemetry skips must be measured. Alignment should be verified
against several visible race-clock readings before rendering.

Alternatively, preserve the historical film and visualize its recorded telemetry
and actions with an explicit statement that neural activations were not recorded.
That would change the requested right-hand panel. Do not fill the missing inputs
with zeros, borrow nearby replay observations or animate random neurons.

The V107I model outputs discrete action values. A future presentation should
decode the selected action into controls and identify the optional map-specific
replay mask. It should not invent a separate drift output or portray the model
as a plain feedforward network without disclosing its graph and residual blocks.
