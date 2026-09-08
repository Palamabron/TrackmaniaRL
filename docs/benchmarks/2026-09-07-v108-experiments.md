# V108: experiments targeting a raw benchmark mean below 37 seconds

Status: prepared and tested offline on 2026-09-07. **No V108 live lap has been
measured. The sub-37 mean is not yet achieved or demonstrated.** Trackmania was
closed while preparing this package.

The existing policy can drive approximately 36.7–36.9 seconds, but occasional
large losses dominate the mean. Earlier live interventions did not solve this:
the narrow action projection finished 10/10 with mean 39.032 seconds, including
a 56.600-second lap whose main loss started around 80% progress. Open-loop action
replay subsequently finished only 1/8 attempts. These failed experiments are not
used as positive evidence for V108.

V108 preserves feedback from the current observation. It tests inference changes
before spending another night on training. No checkpoint weights, reward,
Openplanet physics, timer, or benchmark trial selection are changed.

## Implemented candidates

| Variant | Change | Purpose |
| --- | --- | --- |
| `baseline` | Original neutral 32-quantile decisions | Same-session control |
| `dense` | Neutral integration with 128 quantiles | Check numerical action-ranking sensitivity |
| `cvar75` | 128 quantiles; lower 75% of predicted return at 54–90% progress | Reduce decisions relying on optimistic outcomes |
| `cvar50` | As above, lower 50% | Stronger risk sensitivity |
| `envelope` | Highest-Q allowed action at 54–90% progress | Suppress action branches absent from reference trajectories |
| `envelope-cvar75` | Envelope plus lower 75%, using 32 quantiles | Combined intervention, original behavior outside the window |

Risk-sensitive action selection is supported by the
[IQN research](https://proceedings.mlr.press/v80/dabney18a.html). Whether its learned
return distribution captures these particular collisions remains unverified.
Lower-tail return optimization is a hypothesis for improving mean race time;
it is not mathematically identical to minimizing that mean.

The envelope comes exclusively from this checkpoint's online replay. It excludes
human demonstrations and requires contiguous, terminated, non-truncated episodes
of 700–750 steps with final observed progress above 99%. This step-count rule is
a reference-selection proxy, **not a measured sub-37 finish-time label**. It finds
20 episodes. Allowed actions are grouped in 0.5%-progress bins, unioned with both
neighbors. No benchmark result updates this envelope. If no finite allowed Q
value exists, the original values remain available. The mask is specific to
this map, observation layout and 78-action encoding; it is not a safety guarantee
for arbitrary off-line states.

## Offline evidence

Each online episode was sampled every 20 observations. The model uses an identity
temporal core, so this sampling does not omit recurrent state. The same observations
were supplied to every variant. Counts below are changes from the original policy:

| Variant | Reference states (743) | Other online states (487) |
| --- | ---: | ---: |
| baseline | 0 | 0 |
| dense | 15 | 11 |
| cvar75 | 20 | 22 |
| cvar50 | 28 | 41 |
| envelope | 0 | 135 |
| envelope-cvar75 | 13 | 137 |

The zero reference disagreement for the envelope is in-sample. An additional
leave-one-episode-out check built the envelope without each held-out reference
episode: 17/5005 recorded actions in the intervention window were excluded
(0.34%). This measures action coverage, not closed-loop stability or lap time.
The other-online group contains complete longer episodes; its action changes
can be beneficial or harmful. There is no simulator-based proof of improvement.

Offline output is under
`my-trackmania-agent/artifacts/sub37-v108-offline-baseline-20260907T212905133500/`.
The runner also prints its output directory for each new invocation. Unit checks
cover lower-tail preference, highest-Q selection within the envelope, window
boundaries, empty-mask fallback, and exclusion of demo/incomplete episodes.

## Tomorrow: live protocol

Open the existing test map in Trackmania, with the plugin connected and the car
ready to restart. Run commands from the repository root, one at a time. Start
window recording before live measurement if a video is desired; this runner
does not start a recorder. Recording settings must be the same across candidates.
If the game returns to the finish/menu screen between commands, return to the
track before launching the next command.

```powershell
Set-Location '%PROJECT_ROOT%/'
uv run python -m scripts.sub37_experiments benchmark --variant baseline --trials 10
uv run python -m scripts.sub37_experiments benchmark --variant envelope --trials 10
uv run python -m scripts.sub37_experiments benchmark --variant cvar75 --trials 10
uv run python -m scripts.sub37_experiments benchmark --variant dense --trials 10
uv run python -m scripts.sub37_experiments benchmark --variant cvar50 --trials 10
uv run python -m scripts.sub37_experiments benchmark --variant envelope-cvar75 --trials 10
```

Each command resolves the existing config and source checkpoint automatically;
it does not depend on PowerShell `$Config`/`$Checkpoint` variables. The optional
`--config` and `--checkpoint` overrides must point to compatible V5/78-action
artifacts. Every invocation gets a distinct directory and saves its intervention,
checkpoint SHA-256, envelope, complete evaluation, action trace and `results.md`.
Logging is local and does not require W&B credentials.

A failed performance gate exits nonzero but keeps its results. A telemetry or
controller error requires fixing the runtime before the next candidate. Every
candidate must finish all attempts; **no slow or telemetry-skipped lap is dropped**.
Acceptance requires mean and median strictly below 37 seconds, all finishes,
zero telemetry/controller errors and valid race-clock steps no larger than 100 ms.
Raw telemetry skip counts remain visible. A ten-lap pass is a screening result.

Select the lowest-mean candidate among those completing all ten healthy attempts,
freeze it, and run a fresh 30-lap confirmation. For example, **only if `envelope`
wins the screen**:

```powershell
uv run python -m scripts.sub37_experiments benchmark --variant envelope --trials 30
```

Success means 30/30 and raw mean below 37 seconds in that fresh confirmation.
Keep a failed confirmation too; do not repeatedly rerun until a favorable batch
appears. A confirmed sample mean is still not a guarantee about every future batch.

## If all candidates fail

The saved action/progress/speed/lateral-offset traces and evaluation progress bins
will locate the first loss of time. Use those states to design targeted correction
data and retraining. The existing human recovery archives need a separate causal
input-label audit before further fine-tuning. A new vision/attention architecture
would need new training and a matched comparison; these inference experiments
can establish whether action selection alone is sufficient first.

Offline screening can be repeated without the game:

```powershell
uv run python -m scripts.sub37_experiments offline
uv run pytest tests/unit/experiments/test_sub37_policy.py -q
```
