# CP33866: initial-state Q landscape and joint calibration probe

## Decision

**None of the four tested weights is viable under the required nonterminal drift guard.**
All weights reduce held-episode terminal error with positive family-adjusted paired
bootstrap intervals, but every weight fails the <=0.145 nonterminal MAE guard in
both sampling seeds. This is a strong calibration tradeoff in the tested frozen
landscape, not evidence that the critic simply cannot fit terminal rewards.
It does not prove architectural insufficiency or rule out smaller weights, different
optimization schedules or moving targets. No such extra tests were run.

**Identity:** the requested immutable SHA identifies CP33866 from
`tmrl-sd-sac-actorfit-s17` / sd-fit07d, not the stopped sd-af07 checkpoint.
Both the original file and diagnostic copy matched
`a243b4f50d210d882860b74e4626ff42b369c3f1c2fd78a25fe81068d05906d7` before/after.
The requested SHA took precedence over the inconsistent parent label.

## Stage 1: zero updates, 138 saved episode-first observations

All 78 discrete actions were enumerated independently for Q1, Q2 and the
production SD-SAC average(0.5*Q1+0.5*Q2). Actor greedy action21 appears on all138
starts; all three critic rankings instead choose action71 on all138 starts.
Action21 is gas1/brake0/steer-0.5. In the frozen action table, action71 is
gas1/timed10ms-brake-tap/steer+5/6. These are encoded controls, not tested driving
quality. Similar start observations do not measure representation diversity
across the track.

| Critic | maxQ-minQ mean | Median | Min | Max |
|---|---:|---:|---:|---:|
|Q1|0.19211699|0.19213009|0.19202709|0.19218445|
|Q2|0.19520355|0.19521523|0.19512463|0.19523525|
|Average Q|0.19366029|0.19367218|0.19357586|0.19370842|

| Critic | Top-1 distribution | Action21 rank /78 | Percentile | Mean Q(action21) | Mean max Q | Mean regret |
|---|---|---:|---:|---:|---:|---:|
|Q1|71:138/138|11|87.0130|10.1896526|10.2258699|0.0362174|
|Q2|71:138/138|5|94.8052|10.2560746|10.2852517|0.0291771|
|Average Q|71:138/138|8|90.9091|10.2228637|10.2555608|0.0326971|

Ranks and percentiles are identical across the138 starts for each critic.
Rank1 is best. Percentile runs from0(worst) to100(best), based on the other77
actions, with exact ties assigned mid-percentile. No action21 ties for best occur.
JSON preserves each state's full78-action values, actual argmax, action21 value,
rank, percentile and regret. The critic average ranks21 eighth: reasonably high
but never best. This is a learned ranking discrepancy, not independent action truth.

## Stage 2: exactly384 disposable optimizer steps

The existing selected transition IDs were loaded unchanged from the previous
probe JSON:110 fit terminals/4096 fit nonterminals/27 held terminals/1024 held
nonterminals,5257 total. Fit/held episodes do not overlap. These episodes were
already used by original live training; held means excluded only from these new
copy updates. The27 held terminal transitions belong to27 distinct episodes.

Each lambda/seed pair received48 steps(4 weights*2 seeds*48=384), starting from
the same saved critics and a separate deep copy of saved critic Adam state.
Only copied Q1/Q2 parameters received gradients. Actor, alpha0.01 and target
critics stayed frozen. Candidate weights were discarded, never saved/resumed.
Critic LR0.0003;128 fit nonterminals plus128 fit terminals sampled with replacement
per step. Seeds17/29 produce matched sampling streams across lambda values.

The implemented requested objective uses **unclipped MSE**, with each class
separately averaged and both critics' squared errors summed:

`L = mean_nonterminal(sum_critics((Q-y_frozen)^2)) + lambda * mean_terminal(sum_critics((Q-r)^2))`

Nonterminal targets use the actual frozen runtime Bellman target function, gamma
0.995/current saved actor/saved target critics. All137 terminal targets equal
the recorded reward exactly. There is no empirical terminal-frequency correction;
lambda is an explicit objective weight. This differs from production clipped
SD-SAC and from the earlier importance-corrected stratification probe.

| lambda | Sampling seed | Fit terminal MAE | Held terminal MAE | Held nonterminal MAE | Guard |
|---|---:|---:|---:|---:|---|
|Baseline|—|3.323240|3.310210|0.121032|Reference|
|0.1|17|1.716415|2.199863|0.352545|REJECT|
|0.1|29|1.721087|2.286801|0.366395|REJECT|
|1|17|0.408005|1.067552|0.865697|REJECT|
|1|29|0.486569|1.361400|0.777365|REJECT|
|5|17|0.231089|1.030206|1.435648|REJECT|
|5|29|0.204472|1.145136|1.403639|REJECT|
|10|17|0.221015|1.304657|2.449186|REJECT|
|10|29|0.174994|1.190988|1.571659|REJECT|

The guard requires both `MAE <=0.145` and `MAE <=1.2*measured baseline`
in **each seed**, so a good terminal score cannot rescue a violating weight.
The smallest weight raises held nonterminal MAE to0.3525/0.3664, approximately
+191%/+203%, already far beyond the allowed+20%.

### Paired terminal-error uncertainty

For each held episode, average absolute error across the two critics, then
average each episode's baseline-minus-after reduction across the two sampling
seeds. Resample the27 episode clusters, not54 independent seed/episode pairs.
20,000 paired bootstrap draws(seed17422) yield two-sided98.75% intervals per
weight(Bonferroni nominal95% family coverage for four comparisons).

| lambda | Mean held terminal MAE reduction | Family-adjusted interval | Positive lower bound | Both seeds pass drift |
|---|---:|---|---|---|
|0.1|1.066878|[0.790236, 1.302930]|Yes|No|
|1|2.095734|[1.648950, 2.479802]|Yes|No|
|5|2.222539|[1.564910, 2.786079]|Yes|No|
|10|2.062387|[1.199326, 2.656228]|Yes|No|

Terminal improvements are statistically distinguishable from zero under this
conditional, approximate bootstrap; **none is jointly acceptable**. Only27
episodes/two sampling streams and one checkpoint were tested. This is not
independent training-seed evidence or a population driving-success claim.

## Capacity/interference interpretation

The prior terminal-only control fitted terminal MAE to~0.10 and held terminal
MAE to~0.25, while badly damaging nonterminals. This joint probe also fits
fit-terminal MAE as low as0.175, but preserves neither the required nonterminal
accuracy nor equally strong held-terminal calibration. Together these support
objective/representation interference as the observed bottleneck for this short
probe, rather than simple inability to fit known terminal rewards.

Important limit: the guard protects agreement with **learned frozen Bellman
targets**, not independently correct future returns. A drift violation is a
rejection under the requested test, not proof that true driving values worsened.
Likewise, preserving those targets would not establish critic correctness.
The fixed-target schedule, finite budget and objective weights do not establish
an unavoidable capacity limit. Neither replacing the actor with action71 nor
promoting any calibrated copy to live training is justified by this diagnosis.

## Integrity, execution and reproducibility

The numerical probe finished in355.704s within its900s cap.
CPU only, one numerical/intra-op thread and one inter-op thread, idle priority.
A sampled OS-thread receipt records one CPU-active worker thread and three idle
library threads; the venv launcher used no sampled CPU. All observed probe
PID/creation-time identities are now closed. Original/copy checkpoint hashes,
config and prior-data inputs, baseline model/target digests and original Adam
state digest were unchanged afterward. No controller, learner, training run,
Trackmania launch, game eval, resume, networking or remote publication occurred.
Automation remainsPAUSED. No training configuration or algorithm was changed.

Frozen runtime commit281332d99fdb8bc1edb70d590260731699ab40bf; fingerprint
`1f4d26134a9c90b701d2cc1a3a447c30ac0ef053d447833a4a8a8048b2a81989`
matches the checkpoint.58 relevant unit checks passed, including4 new rank,
class-normalization, paired-bootstrap and Adam-digest tests; Ruff/mypy passed.
The4 new tests also passed under explicit CPU-one-thread/idle settings.

Run the standalone script as a file, with only the frozen runtime on PYTHONPATH
(adding the editable experiments package to runtime imports changes the pinned
component-source fingerprint):

```powershell
$base = "H:/Studia/inzynierskie/inzynierkav2/AITrackmania/artifacts/tmrl-test-comparison"
$editable = "C:/Users/szulc/.codex/worktrees/tmrl-training-fixes/AITrackmania"
$frozen = "C:/Users/szulc/.codex/worktrees/tmrl-sd-sac-actorfit-runtime/AITrackmania"
$env:PYTHONPATH = $frozen
Set-Location $frozen
& "H:/Studia/inzynierskie/inzynierkav2/AITrackmania/.venv/Scripts/python.exe" `
  "$editable/experiments/tmrl_test_comparison/probe_sd_sac_joint_calibration.py" `
  --config "$base/sd-fit07d/sd-sac.yaml" `
  --checkpoint "$base/sd-fit07-final-audit/cp33866.pt" `
  --original-checkpoint "$base/tmrl-sd-sac-actorfit-s17/checkpoints/distributed-update-00033866.pt" `
  --prior-probe "$base/sd-critic-probe07/probe02.json" `
  --starts "$base/sd-fit07-final-audit/start-policy-audit.json" `
  --output "$base/sd-joint-calibration07/reproduction.json"
```

JSON/report/evidence are preserved under `evidence/sd-joint-calibration07/`.
Full diagnostic originals remain under the BASE/sd-joint-calibration07 directory.
The standalone script is `probe_sd_sac_joint_calibration.py` in this harness.
