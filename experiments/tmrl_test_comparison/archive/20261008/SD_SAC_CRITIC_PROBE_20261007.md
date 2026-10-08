# SD-SAC: terminal gradients and disposable critic copies, 2026-10-07

## Decision

No terminal bootstrap/sign error was found. Corrected terminal stratification did
not materially improve calibration in this bounded experiment. Terminal-only
regression can fit recorded failure rewards, including episodes excluded from the
new fitting, but severely damages nonterminal values. Reject terminal-only training
and do not promote any tested variant to live/full training. The known driving
result remains **0/10 finishes**, full SD-SAC **BLOCKED**, automation **PAUSED**.

A separate, reproducible replay contract bug was repaired in editable source:
reading a zero-dimensional tensor column yielded a NumPy scalar and crashed
`torch.from_numpy`. Restoring its zero-dimensional array shape fixes read,
checkpoint restore and n-step materialization. The failed pilot stored ordinary
integer action indices, so this repair is **not its driving fix**. Frozen runtime,
saved checkpoint/replay and all learning settings remained untouched. A future
run using edited source needs a fresh run, never resume of the old checkpoint.

## Actual data path and gradient checks

The frozen runtime materialized 5257 saved transitions:110 training terminals,
4096 training nonterminals,27 held terminals and1024 held nonterminals. Reward,
terminated/truncated flags, action, step and observation were compared with saved
columns, and one-step discount checked against0 for termination or gamma0.995.
The actual production `_critic_targets` returned exactly the stored reward on all
137 terminals. Terminal endpoints use replay next-observation overrides; a unit
fixture checks this endpoint independently of the following episode.

The actual production clipped loss was differentiated with respect to both
critics' selected terminal values. No gradient pointed away from the reward;
273/274 gradients matched ordinary squared-error gradients. Clipping blocked just
1/274 (0.365%). This checkpoint does not support mass clipping or reversed-gradient
explanations. It does not exclude other optimization or data-coverage issues.

Source inspection shows the collector pairs the current prepared observation and
chosen action with the same environment step's reward/flags and next observation.
Replay terminal info retains behavior entropy, not raw reward-component/telemetry
traces: this audit cannot independently reconstruct physical action acceptance or
prove all original game-step timestamps were aligned. No game/UI was used.

## Controlled copy experiment

The SHA-verified CP33866 copy and original have SHA
`a243b4f50d210d882860b74e4626ff42b369c3f1c2fd78a25fe81068d05906d7`.
Fingerprint recomputation from frozen281332d9 matches
`1f4d26134a9c90b701d2cc1a3a447c30ac0ef053d447833a4a8a8048b2a81989`.
Whole complete episodes were split with seed17421,110 fitting and27 held episodes,
with no overlap. These episodes **were used by original training**; they are held
out only from this new optimization, not an unseen driving/generalization test.

Each variant started from the same saved critics and an independent deep copy of
saved critic Adam state. Actor, alpha0.01 and target critics stayed frozen; models
ran in eval mode. Critic LR0.0003, batch128,64 steps per copy, sampling seeds17/29:
**384 disposable optimizer steps**, zero runtime learner updates. No candidate
weights/checkpoints were saved. CPU one thread/idle priority,224.406s within a
600s cap. Immutable models and both checkpoint SHAs were checked afterward.

Empirical terminal mass was110/109215=0.10072%. A fixed random4096-row nonterminal
subset reduced CPU cost, while the empirical class mass was retained. Sampling
was with replacement, not production's without-replacement sampler. Corrected
stratification drew terminals with probability12.5%, weighted terminal rows p/q
and nonterminal rows(1-p)/(1-q), taking arithmetic mean without self-normalization.
This preserves the expected mixed loss on the selected class-conditional pools;
it intentionally does not give terminals greater expected objective weight.

Errors below average absolute error across both critics, on fixed frozen Bellman
targets for nonterminals and known rewards for terminals. Lower nonterminal error
is self-consistency with the saved target critic, **not independently correct Q**.

| Variant | Sampling seed | Terminal draws | Fit terminal MAE | Held terminal MAE | Held nonterminal MAE |
|---|---:|---:|---:|---:|---:|
| Baseline | — | — |3.3232|3.3102|0.1210|
| Empirical uniform |17|15|3.2121|3.2172|0.1430|
| Empirical uniform |29|6|3.3832|3.3660|0.1323|
| Stratified, corrected |17|1038|3.3144|3.2859|0.1323|
| Stratified, corrected |29|1046|3.3358|3.3348|0.1279|
| Terminal-only MSE capacity control |17|8192|0.1023|0.2463|11.8800|
| Terminal-only MSE capacity control |29|8192|0.1075|0.2500|11.9412|

Terminal-only MSE intentionally removes clipping and ignores nonterminals. It is
a capacity control, not an isolated sampling change. It shows the network can fit
terminal rewards; its approximately98-fold nonterminal residual increase rules
out accepting that fitted copy as a repair. Corrected oversampling substantially
increased exposure but did not consistently improve held terminal MAE. This short
probe cannot reject every longer online sampling scheme: anchors/targets were
frozen instead of production's target updates(tau0.005), and the nonterminal pool
was a subset. Two sampling seeds are not three independently trained live seeds.

## Stochastic versus greedy behavior

The final saved actor still has broad entropy (~3.14 nats), yet all138 saved
first-episode observations pick the same greedy action21 (gas1,brake0,steer-0.5).
Its mean best-action probability is13.39%; the next action is only0.128 percentage
points behind. Stochastic collection can choose many alternatives while greedy
inference repeats the maximum. Broad entropy or critic agreement therefore does
not guarantee a usable deterministic driver. This explains a mechanism for the
gap, not its full cause; saved starts are not actual evaluation control traces.

Known terminal miscalibration and the large capacity-control tradeoff make a
joint terminal/nonterminal calibration objective the next hypothesis to test on
copies, with explicit nonterminal-drift limits. The current evidence does not
select a coefficient or justify changing shared reward/model/GNN, disabling the
alpha floor, replacing the driving gate with stochastic success, or another actor
objective change. No new live test/full training was launched or prepared as a
qualified variant.

## Validation and preserved failures

87 relevant replay/materialization/sampling/SD-SAC/audit tests passed; Ruff and
mypy(two changed source files) passed. Post-probe verifier confirms all51 prior
owned identities closed, mutex free and1260 immutable pins valid. Historical STOP
files, checkpoints and journals are preserved; automation remains PAUSED.

First execution failed fingerprint validation **before optimization** because both
editable and frozen experiment namespace roots were on PYTHONPATH. It was fixed
by restricting runtime imports to frozen sources and loading the adjacent helper
without adding an editable package root. No fingerprint override, source edit or
live resume occurred. Both the failed log/initial JSON and successful result are
preserved. The exact executed helper is archived with its SHA; published helper
then received import/provenance/saved-option generalization, without rerunning
optimization or substituting results.

Evidence: `evidence/sd-critic-probe07/`; full originals under
`H:/Studia/inzynierskie/inzynierkav2/AITrackmania/artifacts/tmrl-test-comparison/sd-critic-probe07`.
