# Recorded V106B versus V107C benchmark (2026-09-06)

## Decision

V107C improves the long-tail behaviour over V106B under the same recorded conditions, but it does
not reach the project objective of a mean completed lap below 37 seconds. Keep V106B as the release
baseline and treat V107C as evidence that bounded context features help tail risk, not as a promoted
checkpoint.

## Compared policies

- V106B baseline: `best-eval-policy-00199840-at-update-00200029.pt`
- V107C candidate: `distributed-update-00015000.pt`
- Map UID: `oqIJ5rQDRrNwLPTh9H2p_W4tLof`
- Control and map: identical 20 Hz school-mode editor validation
- Capture: Trackmania window, 1920x1080 at 30 FPS, NVIDIA NVENC

## Valid 30-trial results

| Metric | V106B | V107C update 15000 | Change |
|---|---:|---:|---:|
| Finished | 30/30 | 30/30 | equal |
| Mean completed | 38.544 s | 37.842 s | -0.702 s |
| Median completed | 36.910 s | 36.830 s | -0.080 s |
| Best | 36.610 s | 36.650 s | +0.040 s |
| P95 (nearest-rank) | 46.830 s | 42.090 s | -4.740 s |
| Below 37 s | 19/30 | 23/30 | +4 |
| Below 38 s | 23/30 | 23/30 | equal |
| At least 40 s | 7/30 | 6/30 | -1 |

The typical lap changes only slightly. The useful V107C signal is the lower mean and substantially
lower P95. Six laps at or above 40 seconds remain, so the residual adapter does not solve the rare
slow-line failure mode.

V106B times in seconds:

```text
37.980, 36.610, 36.740, 36.630, 36.780, 37.080, 36.890, 36.940, 42.240, 42.330,
36.830, 36.930, 36.790, 36.950, 36.900, 36.730, 36.730, 47.910, 37.020, 36.830,
41.890, 36.830, 37.060, 36.690, 36.910, 36.910, 36.670, 45.580, 46.830, 41.110
```

V107C valid times in seconds:

```text
42.090, 36.930, 36.860, 36.720, 36.880, 41.570, 39.680, 36.810, 36.770, 36.760,
36.810, 41.180, 36.860, 36.690, 36.780, 36.890, 36.650, 36.920, 36.980, 40.950,
36.810, 36.670, 40.110, 36.700, 43.350, 36.690, 36.780, 36.720, 36.850, 36.800
```

## Run provenance

- V106B 30-trial W&B run: `doqwzzf1`
- V107C first invocation: `ic7bgbj3`
- V107C clean 15-trial continuation: `dhwsc0ux`

The first V107C invocation began while Trackmania was still on the post-validation replay screen.
Its trials 0-14 are telemetry timeouts with zero progress and are a procedure failure, not policy
DNFs. After the editor-validation state was restored, trials 15-29 completed normally and form the
first valid 15-trial block above. The clean continuation was started only after `track check`
reported `ready=true`; all of its 15 trials completed and form the second block.

## Video evidence

- `%USERPROFILE%\Videos\Captures\TrackmaniaRL-benchmark-20260906-v106b-v107c.mp4`
  - 35:18, approximately 2.81 GB
  - contains V106B, the visible invalid transition/replay interval, and the first valid V107C block
- `%USERPROFILE%\Videos\Captures\TrackmaniaRL-benchmark-20260906-v107c-continuation.mp4`
  - 10:27, approximately 564 MB
  - contains the clean second V107C block

Both files were finalized normally and are deliberately stored outside the repository.

## Slow-lap video diagnosis

Frame-aligned comparisons of a nominal V107C lap and the three slow laps in the clean continuation
show that the tail is created by isolated wall contacts, not by uniformly slower driving:

- the 40.950 s lap diverges at approximately 24.5 s, hits the right wall and drops from roughly
  260 km/h to roughly 120 km/h;
- the 40.110 s lap contacts the inside wall in the final section at approximately 30 s;
- the 43.350 s lap reaches the right wall at approximately 31 s and remains in contact through
  approximately 35 s, with speed falling to roughly 50--100 km/h.

The nominal and slow trajectories remain close before those events. The useful learning target is
therefore the entry action roughly 0.5--1.0 seconds before contact, plus recovery after contact.

## Rejected inference-only stabilization

Two ten-trial screens used the unchanged V107C update-15000 weights and changed only
`switch_q_margin` from zero:

| Margin | Finished | Mean completed | Median completed | Slow outcomes | W&B |
|---:|---:|---:|---:|---|---|
| 0.020 | 9/10 | 38.937 s | 36.960 s | 42.510, 42.340, 43.600 s; one DNF | `5ot3a76k` |
| 0.005 | 10/10 | 39.100 s | 36.850 s | 48.170, 41.960, 43.310 s | `hbf9jijr` |

Both settings are rejected. Even the smaller margin prevents timely corrective switches and makes
the tail worse. V107C remains configured with `switch_q_margin: 0.0`.

## V107D credit-assignment screen

`sub37-iqn-gnn-simba-v107d-s17-nstep20-tail-credit.yaml` changes one learning mechanism: the
n-step return increases from 5 to 20 decisions, or from 0.25 to 1.0 seconds at 20 Hz. It preserves
the Fable-derived reward, V3 bounded adapter, optimizer, exploration and inference behavior. This
places the wall-contact slowdown inside the target horizon of the pre-contact entry actions.

The 200k-transition screen warm-started from the V107C update-15000 checkpoint. Validation, Ruff
and the 12 focused V3 tests passed. Live run `tedopdkz` completed 200,014 transitions and 45,012
updates. Its deterministic 10-trial evaluations were:

| Policy / update | Mean | Median | Best | Below 37 s | Below 40 s |
|---:|---:|---:|---:|---:|---:|
| 1 / 120 | 40.32 s | 37.46 s | 36.70 s | 50% | 60% |
| 4,886 / 5,070 | 38.20 s | 36.91 s | 36.63 s | 60% | 80% |
| 9,777 / 9,991 | 38.76 s | 37.02 s | 36.65 s | 40% | 60% |
| 14,659 / 14,843 | 38.62 s | 36.87 s | 36.67 s | 70% | 80% |
| 19,580 / 19,775 | 39.29 s | 36.78 s | 36.72 s | 80% | 80% |
| 24,452 / 24,635 | 40.30 s | 36.87 s | 36.74 s | 60% | 60% |
| 29,243 / 29,430 | 42.04 s | 39.05 s | 36.28 s | 40% | 50% |
| 34,392 / 34,628 | 37.66 s | 36.84 s | 36.70 s | 60% | 80% |
| 39,551 / 39,736 | 37.68 s | 36.89 s | 36.72 s | 70% | 90% |

V107D is rejected as a promotion candidate: its best mean (37.66 s) remains above the objective and
the tail remains present. It does show that the longer return can improve a 10-trial mean relative to
its own 40.32 s baseline, but it does not beat the recorded 30-trial V107C result reliably enough.
The fastest V107D policy is explicitly unsuitable despite a 36.28 s single lap: its same-batch mean
is 42.04 s. Promotion still requires a fresh 30-trial benchmark with 30/30 finishes and mean below
37 seconds; exploratory training laps are not promotion evidence.

## Next experiment

V107E implements the targeted-supervision experiment. It adds demonstration progress metadata and
a cross-entropy objective that is active only at 58--70% and 78--94% track progress. These ranges
cover the lead-in to the approximately 24.5 s wall contact and the complete 30--35 s final-section
failure region. The V106B policy, value head and temporal path remain frozen; only the V3 context
adapter can change and its correction remains bounded to 0.02 per latent dimension.

The offline gate imported 16,798 transitions from 23 human laps between 36.035 and 36.995 seconds,
warm-started from V107C update 15,000 and completed 500 updates in 48.6 seconds. W&B run `kj4es4xq`
produced `distributed-update-00000500.pt`. All 50 focused V3, objective, replay and demonstration
tests pass, as does Ruff. Against all demonstrations, exact-action agreement changed from 23.294%
to 23.366% and steering-bin agreement from 30.99% to 31.15%. The intended 70--90% tail region
improved while most non-target bins were effectively unchanged; this is a safety gate, not evidence
of faster closed-loop laps.

The next required gate is a short online screen from the offline checkpoint. Do not extend V107C
training unchanged, add an inference switch margin or repeat V107D n-step 20. The official TMRL
competition ranks the mean of ten runs and penalizes crashes, so a fast single lap is diagnostic but
not the selection metric. Promotion still requires a fresh recorded 30-trial run with 30/30 finishes
and mean below 37 seconds.

## V107E online screen

The short online screen ran as W&B run `gxh1t2vh` from the gated offline checkpoint and completed
100,006 transitions, 20,001 updates and 120 training episodes. The final training finish rate was
96.67%. All four deterministic evaluations finished 10/10 trials:

| Policy / update | Mean | Median | Best | Below 37 s | Below 40 s |
|---:|---:|---:|---:|---:|---:|
| 1 / 61 | 37.336 s | 36.865 s | 36.68 s | 90% | 90% |
| 4,854 / 5,072 | 38.673 s | 37.095 s | 36.74 s | 40% | 80% |
| 10,179 / 10,439 | 41.803 s | 37.715 s | 36.63 s | 50% | 60% |
| 15,646 / 15,858 | 43.352 s | 41.610 s | 36.93 s | 10% | 20% |

V107E is rejected as a promotion candidate. The initial policy is the best by mean and has nine
sub-37-second laps, but its 37.336-second mean misses the target because of one slow tail outcome.
Further online updates progressively worsen both the mean and the tail. The 36.63-second fastest
lap at update 10,439 is not a viable selection result because its same-batch mean is 41.803 seconds.
No checkpoint satisfies the required 10/10 and mean-below-37 gate, so a recorded 30-trial promotion
benchmark was not run and no production checkpoint was replaced.

## Next experiment: V107F

V107F preserves the complete best V107E policy and freezes its existing context adapter. It adds a
separate zero-initialized spatial residual adapter over the 44 ordered boundary stations. Four
direction-sensitive Conv1D blocks with dilations 1, 2, 4 and 8 retain station order and combine near
and farther geometry before near/mean/max pooling. The spatial correction is hard-bounded to 0.02
per latent dimension.

The actual V107E best-eval checkpoint loaded 63 shared tensors into V107F; all 28 missing tensors
belong exclusively to the new spatial adapter. Before training, the V3 and V4 encoder outputs are
bit-identical (`max_abs_diff=0.0`). Only the spatial adapter is trainable. The overnight screen uses
500 offline updates followed by 300,000 online transitions, evaluations every 25 episodes and a
lower `3e-6` learning rate. A 30-trial recorded benchmark remains conditional on a 10/10 eval whose
mean is below 37 seconds.

## V107F overnight result

V107F completed 300,004 online transitions, 70,501 updates and 371 training episodes after its
500-update offline gate. There were no runtime, telemetry or controller errors; training finish rate
was 98.65%. Its fourteen deterministic 10-trial evaluations all showed the same failure mode: the
nominal line remained near 36.7--37.0 seconds, but rare slow tails prevented a qualifying mean.

| Policy / update | Finished | Mean | Median | Best | Below 37 s |
|---:|---:|---:|---:|---:|---:|
| 500 / 650 | 9/10 | 41.392 s | 41.560 s | 36.79 s | 30% |
| 5,299 / 5,601 | 10/10 | 38.806 s | 36.910 s | 36.73 s | 60% |
| 15,453 / 15,641 | 10/10 | 37.547 s | 36.950 s | 36.68 s | 60% |
| 30,652 / 30,842 | 10/10 | 39.271 s | 37.005 s | 36.60 s | 50% |
| 50,701 / 50,886 | 10/10 | 37.507 s | 37.030 s | 36.77 s | 40% |
| 66,255 / 66,440 | 10/10 | 39.316 s | 36.930 s | 36.74 s | 60% |

The best V107F mean, 37.507 seconds, remains above both the target and V107E's 37.336-second
screen. The fastest 36.60-second lap at update 30,842 is explicitly rejected because the other
trials in the same evaluation include 42.44, 45.98 and 41.98 seconds. V107F therefore does not
justify a recorded 30-trial benchmark or promotion. The ordered spatial adapter by itself has not
removed the rare recovery failure mode; the next experiment should address contact/recovery signals
or time-correlated telemetry, rather than extend this run.

W&B: `054n2n95`.

## V107G/V107H recovery-memory screen

V107G adds eight causal recovery indicators (decision-interval error, instantaneous and forward
speed loss, progress advance, clearance loss, edge approach, retained-speed deficit and a
0.75-second decaying incident memory) plus a 0.8-second residual GRU with 0.4-second burn-in. Both
new paths are hard-bounded to 0.02 and initially produce exactly zero. The real V107E checkpoint
loaded 63 shared tensors and its output remained bit-identical before adaptation
(`max_abs_diff=0.0`). Only the recovery adapter and temporal core are trainable. Ruff and the full
suite pass (`534 passed, 1 skipped`).

The V107G offline gate is rejected. It imported 16,798 transitions from 23 corrected human laps and
completed 1,000 sequence updates, but its first three online laps were 42.48, 38.10 and 44.74
seconds (mean 41.77 seconds). This shows that adapting recurrent memory only on clean expert
trajectories changes the nominal line before the model has observed the failure states it must
recover from. The run was stopped before spending the configured 100,000 online transitions. W&B:
`ujuk8k6d`.

V107H tests the same architecture without offline adaptation. It starts from the exact zero-gated
V107E policy, imports demonstrations only into replay and delays updates until real online recovery
sequences are available. The screen is limited to 50,000 transitions with earlier ten-episode
evaluations. Exploratory baseline laps already demonstrate the known bimodal behavior: 36.58 and
37.04-second finishes coexist with much slower laps and DNFs. Those exploratory laps are not the
selection metric; promotion remains conditional on a deterministic 10/10 mean below 37 seconds.

V107H completed its 50,032-transition screen and is rejected. The exact-start evaluation at update
65 finished 10/10 with mean/median/best `38.902 / 36.965 / 36.630` seconds. At update 1,257 the
online recovery adapter briefly reduced the mean to `37.490` seconds (10/10, median `37.030`, best
`36.840`, 3/10 below 37 seconds), but this policy was not retained as a checkpoint. Continued
learning then collapsed: update 3,970 finished 9/10 with a `57.160`-second completed-lap mean, and
update 6,539 finished only 5/10 with a `57.878`-second mean and `50.280`-second best. The run itself
ended normally at update 7,508; this was learning instability, not an infrastructure failure.

The result rejects an always-active recurrent residual trained by unrestricted online TD updates.
Although only the new recovery modules were trainable, their global residual gate could alter the
nominal racing line in every state. Prioritized slow/failure sequences and target-network refreshes
then amplified those changes. A successor should keep the proven base policy immutable and make
the recovery correction state-conditional and exactly zero outside a sustained, independently
detected incident. Random exploration should not be used in the promotion screen; recovery data
should instead come from explicit perturbation-and-correction collection. W&B: `ngsj0h5v`.

## V107I incident-gated recovery result

V107I removes the unstable recurrent branch and keeps the V107E-derived base policy immutable. Its
bounded recovery adapter is multiplied by a conservative gate that requires both a sustained
incident memory and retained-speed loss. Outside a detected incident its correction is exactly zero.

The best ten-trial evaluation candidate, policy 348 at update 433, finished 9/10 trials. Its nine
completed laps had mean/median/best `36.824 / 36.830 / 36.620` seconds. This is encouraging nominal
pace but not a qualifying result because one trial did not finish. W&B: `mnhje6t7`.

A subsequent 30-trial benchmark of the exact fastest checkpoint finished 29/30. Among the 29
completed laps, mean/median/best were `38.782 / 36.940 / 36.620` seconds; 16 were below 37 seconds
and eight were at least 40 seconds. The single DNF reached roughly 80.4% progress. The complete
times were:

```text
42.420, 36.650, 36.840, 47.390, 36.680, 36.620, 48.760, 36.830, 37.030, 36.800,
37.120, 37.080, 37.010, 36.640, 36.640, 36.940, 36.710, 41.020, 36.680, DNF,
36.810, 42.050, 36.780, 41.160, 46.940, 36.780, 36.950, 37.060, 41.360, 36.930
```

W&B: `a8ekowuh`. Checkpoint:
`fastest-eval-policy-00000348-at-update-00000433.pt`, SHA-256
`4D1973D931A20E4F5874CCE1C535BE84582658AA05817C46573BF2F2DFA1DB01`.

V107I is therefore retained as the V107J source, not promoted. The evidence narrows the problem:
the source usually drives a competitive 36.6--37.1-second line, but occasional contact and weak
recovery create the heavy tail. Extending ordinary online TD learning would again expose the base
line to an objective that already destabilized V107H.

## V107J targeted human recovery phase

V107J implements perturbation-and-correction data collection. Its default 36-episode design covers
three progress windows from 55% to 83%, three severity windows from 50 to 200 ms and both planned
steering directions twice. The V107I checkpoint drives to the seeded target, receives one
full-gas/full-steer impulse, releases the virtual controller and asks a human to recover. On a bend,
the applied direction opposes the policy's current steering to maximize a meaningful deviation and
the actual control is archived. Only completed, continuous laps are kept; timer resets and
kinematically implausible teleport/respawn jumps are rejected. The full pre-incident and reaction
history is stored so V5's causal memory can be reconstructed, but expert labels begin only with the
first clear physical input after virtual input is observably neutral.

The separate `recovery-finetune` phase validates map, geometry, the exact architecture and
source-checkpoint provenance. It requires at least 24 usable episodes, six held-out episodes, 500
active-gate labels and 15 such labels per episode. The recorder reconstructs the applied impulse
from telemetry and rejects a missing, wrong-direction or too-short perturbation. Fine-tuning bins
the actual progress, actual duration and actual direction, requires every progress-by-severity
cell, and makes a deterministic episode-held-out split with balanced marginals. Complete episodes
are sampled uniformly and later reaction frames receive less weight. Only the bounded recovery
adapter is updated. The unchanged update-zero adapter is also a validation candidate; a trained
candidate must improve held-out action accuracy while changing 5--20% of the source policy's
recovery actions. Its output is an explicitly non-resumable `policy_only` checkpoint so selected
weights cannot be paired with optimizer state from a later update.

The official TMRL competition document ranks the mean of ten runs and applies a special penalty to
proper crashes. The project's `crashed` telemetry flag also covers recoverable wall contact, so it
must not be reused as that official reset penalty. For this experiment the conservative promotion
gate is instead 10/10 finishes, completed-lap mean strictly below 37 seconds and median strictly
below 37 seconds. The fastest checkpoint remains separate so a sub-36 lap is retained as diagnostic
evidence. See the [TMRL competition rules](https://github.com/trackmania-rl/tmrl/blob/master/readme/competition.md).

Collection cannot run unattended because the expert segment is deliberately human-controlled.
The default target is 36 valid recoveries covering 55--83% progress, 50--200 ms severity and both
planned steering directions. Expert labels begin at the first clear physical input after virtual
control is neutral; restarts and teleport-like discontinuities are rejected. Then run the supervised
phase and a recorded ten-trial screen. A
passing candidate must then repeat the result over 30 fresh recorded trials before promotion. Do
not start a multi-hour online training run until this bounded experiment has been evaluated.

## V107I telemetry timing diagnosis

The apparent telemetry-frame loss in the V107I benchmark is not evidence that the actor CPU or GPU
is too slow. The client intentionally drains queued render-rate packets and acts on the newest one.
Slow laps were brake-tap heavy: controller-apply time and the reported skipped-frame fraction had a
correlation of `0.999993`, consistent with the synchronous 10 ms brake pulse allowing extra render
packets to queue. Fast and slow laps used almost the same controller-apply plus telemetry-wait time
(about 41.27 ms versus 41.15 ms), and the maximum observed race-clock step was only 60 ms against a
50 ms target interval.

Raw skipped packets are therefore retained as a diagnostic and are not an acceptance gate. The
meaningful hardware/runtime guard is the physical race-step p99/max latency; V107J rejects a
benchmark if any trial lacks a positive measurement or if the configured maximum exceeds 100 ms.
This catches a genuine two-tick stall without changing 20 Hz control, replaying stale observations
or introducing a timer race into the 10 ms brake action. On the measured i9-13900K/RTX 4090 host,
actor inference and control timing have ample headroom; the heavy tail remains a driving/recovery
problem.
