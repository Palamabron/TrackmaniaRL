# SD-SAC: actor plasticity, calibration controls and optimizer repair

Status: **offline repair implemented; fresh bounded candidate prepared, not launched**.
Known driving result remains **0/10 finishes** for actorfit. Full training on
17/29/43 remains **BLOCKED**; automation **PAUSED**. No game, controller, training
run, resume, network publication or saved candidate weights were created.

## Decision and concrete repair

The evidence does not establish critic architecture/capacity as the root cause
with100% certainty. The model already has three independently parameterized GNN/
Simba encoders: actor, Q1 and Q2. Terminal/nonterminal interference is observed
under the tested frozen targets, but those targets are learned self-consistency
anchors, not independently correct action values.

A specific optimizer inconsistency was found and repaired in editable SD-SAC:
`HypersphericalLinear.forward` normalizes effective weight rows, while Adam
updates their raw parameters. The value learner projects these rows after each
optimizer step; SD-SAC omitted that operation. Saved critic row norms reached
**4.20**, with several layer means around1.6–2.1 instead of1. Redundant radial
drift changes effective directional step sizes even though forward inference
normalizes the rows. This supports a conditioning repair, not a claim that it
explains all failed driving.

SD-SAC now projects online Q1/Q2 immediately after critic Adam, and the actor
immediately after actor Adam, before Polyak averaging. Ordinary MLP models are
unaffected. Hyperspherical models record `hyperspherical_projection: true` in
their optimizer contract; loading a checkpoint lacking that contract is rejected
before state restoration. A **fresh run** is required. No old checkpoint is
converted or resumed. Shared reward, architecture/GNN, actor objective, alpha,
replay and UTD settings are unchanged.

Projection on a disposable saved-model copy changed start-state inference by at
most3.82e-6. That verifies forward invariance within floating-point precision;
optimization trajectories intentionally change.

## Actor experiment: lowering alpha is not required to learn the ranking

All experiments used CPU, idle priority, one numerical/inter-op thread. The
checkpoint original and read-only copy both had SHA
`a243b4f50d210d882860b74e4626ff42b369c3f1c2fd78a25fe81068d05906d7`.
Its actual run is `tmrl-sd-sac-actorfit-s17`, frozen281332d9, despite the earlier
user label `sd-af07`. Frozen fingerprint was recomputed and matched.

Actor copies restored independent deep copies of saved actor Adam. Critics,
alpha and saved policies stayed frozen. Each copy fitted4206 fixed replay rows
(110 terminals+4096 nonterminals), with1051 rows from disjoint episodes excluded
from these copy updates. All episodes were seen in original training. Sampling
seeds17/29, batch128 with replacement,64 steps/copy. The behavior-entropy anchor
beta0.0005 remained active. This is actor regression to **learned Q**, not a
driving test or evidence that action71 is physically good.

| Actor copy objective | Alpha | Held agreement seed17 | Seed29 | Start agreement |
|---|---:|---:|---:|---:|
| Saved actor, zero updates |0.01|19.12%|19.12%|0%|
| Existing forward KL |0.01|84.59%|88.58%|100%|
| Forward KL, lower alpha |0.001|91.34%|92.39%|100%|
| Greedy distillation control |—|91.06%|92.10%|100%|
| Forward KL + per-step projection |0.01|**92.20%**|**93.53%**|100%|

Every fitted copy picked critic action71 on all138 saved starts. Projection
reduced held greedy Q regret from0.004510/0.003472 to0.002355/0.002272 at the
same alpha, LR, Adam initialization, rows and sampling seeds. The projection
control used128 additional disposable steps; initial actor grid used384.
Original actor/critic tensors, saved Adam and checkpoint SHAs were verified
unchanged afterward. No optimized weights were persisted.

At alpha0.01 the actual frozen-Q start target already assigns p71=0.5660 versus
p21=0.02152, ratio26.30, target entropy1.727. Thus alpha does not make those
actions equivalent. At alpha0.001 the target becomes almost a point mass; that
does not establish better driving. The existing actor objective is experimental
forward KL, where alpha sets the detached target distribution; it is not simply
a separate alpha*entropy term dominating that cross-entropy gradient.

For comparison, canonical SAC parameter-gradient norms on saved starts were
Q0.008742 and entropy0.008206, cosine−0.84756. Comparable, partially opposing
gradients are consistent with a tradeoff, not a zero learning signal. Actual
forward-KL gradient norm1.15398 dwarfed the behavior-anchor gradient0.000533.
Broad entropy alone did not prevent correct greedy ranking after fitting. These
are descriptive gradients at one saved checkpoint, not universal dynamics.

## Critic controls: no accepted terminal-weight repair

Same5257 rows and110fit/27held episode split as the joint calibration probe.
Frozen actor/target critics/alpha0.01, saved critic Adam deep copied each time,
48 steps/copy,128 nonterminals+128 terminals, separate class means:

`L = mean_N(sum_heads((Q-y_frozen)^2)) + lambda*mean_T(sum_heads((Q-r)^2))`.

The head-only control froze both existing encoders, cached their exact features
and optimized only their final linear layers using copied full Adam state.
It tests representation interference without introducing a new architecture.
These controls used the historical **unprojected** optimizer for comparability
with the earlier calibration grid; they do not validate the repaired critics.

| Lambda | Encoder | Seed | Fit terminal MAE | Held terminal MAE | Held nonterminal MAE | Guard |
|---:|---|---:|---:|---:|---:|---|
|Baseline|frozen|—|3.323240|3.310210|0.121032|—|
|0.003|trainable|17|3.224106|3.220163|0.128741|PASS|
|0.003|trainable|29|3.288476|3.302863|0.120633|PASS|
|0.01|trainable|17|3.007359|3.057513|0.148755|FAIL|
|0.01|trainable|29|3.074334|3.143041|0.138139|PASS|
|0.03|trainable|17|2.491679|2.697410|0.224220|FAIL|
|0.03|trainable|29|2.598788|2.823807|0.204796|FAIL|
|0.1|frozen/head only|17|2.993787|3.144217|0.161969|FAIL|
|0.1|frozen/head only|29|2.992999|3.127168|0.164481|FAIL|

Guard requires held nonterminal MAE<=min(0.145,1.2*measured baseline) in both
seeds. Lambda0.003 passed, but terminal reduction was only0.04870 with a paired
episode bootstrap98.75% interval[−0.00018,0.10618], including zero. Larger
weights and head-only optimization failed the drift guard. No variant combines
the specified evidence of terminal reduction with both-seed drift protection.
Four comparisons,27 held episodes,20k bootstrap samples, seeds averaged before
episode resampling; these intervals are conditional and exploratory, following
an earlier grid, not a globally corrected confirmatory search.384 disposable
critic steps,281.593s; no production terminal coefficient was changed.

The observation pipeline also omits explicit race time and the exact historical
progress-window/no-progress counters used by termination logic. This is a
partial-observability concern, not a proven cause from saved data. No hidden
future terminal label, invented input history or shared-feature change was
introduced. Bigger networks alone cannot recover information absent from an
observation. Generic n-step remains disallowed by the SD-SAC contract because
its intermediate entropy terms would be missing; no reward rescaling was made.

## Prepared configuration and verification

Candidate: `configs/diagnostic/sd-sac-projected-s17.yaml`, generated and scope
checked by `prepare_sd_sac_projection.py`. It preserves all actorfit learning,
reward, model, feature-pipeline, replay, UTD and evaluation settings. Only the
source optimizer repair and fresh output identity differ. Preparation receipt
is `evidence/sd-actor-plasticity07/projection-preparation.json`; it is a snapshot,
not launch authority or evidence of qualification. No run directory was created.

Before any launch: create a new frozen repaired runtime and bounded queue, pin
assets/source/STOP and exact owned process identities, verify mutex/preflight
and independent deadline guard. Never reuse the old queue or checkpoint/Adam
state. Required gate remains145408 complete/finite/accounted/drained plus>=8/10
finishes, correctUID, all timing<=100ms, no errors, skips reported, SHA/source
integrity and normal process closure. Full17/29/43 configurations have **not**
been promoted; no learned-Q fitting score replaces that gate.

176 relevant tests passed, including both actor objectives, projection before
target averaging, state round-trip, old-Adam rejection and candidate-scope
rejections. Ruff and mypy passed. Final verification rehashed1260 frozen/prior
pins with no failures, original/copy CP SHA unchanged, prior exact PID/ctime
identities closed, automationPAUSED. Edits are only in the editable worktree;
all frozen sources and historical helpers are unchanged. Changes remain local.

## Reproduction

Scripts accept explicit config/checkpoint/original-checkpoint/prior-probe/starts/
output arguments; the critic tradeoff script does not need starts. Run absolute
script filenames with cwd and PYTHONPATH restricted to the frozen actorfit
runtime. Each script sets CPU/disabled W&B, numerical thread limits and idle
priority before fitting. Use a new diagnostic output file; no training run is
created. For the actor projection control add `--projected-only`.

Outputs: `evidence/sd-actor-plasticity07/{probe.json,projected-probe.json,weight-radii.json}`
and `evidence/sd-calibration-tradeoff07/probe.json`. The first two initial probes
did not pin their executed source SHA before formatting/type-only cleanup;
their outputs are retained honestly. The later projected control records its
executed script SHA. Final runnable sources include only equivalent indexing/
typing/style cleanup since those executions. Original data/model/Adam pins were
verified in every fitting probe; no failed numerical experiment was discarded.
