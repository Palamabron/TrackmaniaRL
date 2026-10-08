# SD-SAC — experimental: raport i prompt dla Fable 5.1

Decyzja człowieka, 8 października 2026: zachować SD-SAC jako **experimental**,
wyłączyć go ze standardowej kampanii na kilku komputerach i zakończyć automatyczne
szukanie poprawek. To przekazanie diagnozy, nie polecenie uruchomienia kolejnej próby.
Scheduler `trackmania-nocne-piloty-i-gotowo-trening-w` jest **PAUSED**; zachowuje
częstotliwość 15 minut na wypadek późniejszego świadomego wznowienia.

Najważniejszy wynik: ostatni kompletny pilot miał **0/10 met**, poprzedni **2/10**.
Nie znaleziono poprawki, która jednocześnie spełniłaby dotychczasowe warunki
offline i poprawiła rzeczywistą jazdę. Nie jest to dowód, że SD-SAC jako metoda
jest bezwartościowy. Dotyczy tej implementacji, konfiguracji i budżetu.

Poniższy prompt można przekazać Fable 5.1 razem z repozytorium i dowodami.
Nazwa modelu pochodzi od użytkownika; raport nie zakłada jego dostawcy, API ani
dostępności i nie uruchamia innego agenta. Nie trzeba przekazywać prywatnego `.env`.

## Gotowy prompt

You are investigating an experimental SD-SAC-inspired implementation in
TrackmaniaRL. Read this entire handoff before proposing a repair. Your objective
is to identify one plausible, falsifiable cause of the observed failure, review
the implementation against its intended objective, and produce the smallest
well-controlled correction or an honest conclusion that the evidence is
insufficient. Do not keep tuning arbitrary coefficients or repeat closed probes.

The human has removed SD-SAC from the standard multi-computer, multi-week
training campaign. Keep it experimental and excluded. This handoff authorizes
read-only diagnosis and a concrete repair proposal; it does **not** restore the
old autonomous training authorization, authorize a game/controller/model update,
restart an automation, modify shared reward/model/GNN/observations, or launch a
new pilot/full run. Obtain explicit scope for a dependent experiment after making
the proposal reviewable. Do not ask for permission to perform read-only analysis.

### 1. Repository and immutable evidence

Windows/PowerShell, Python 3.12. User timezone Europe/Warsaw; dates in the evidence
are UTC unless explicitly qualified. Diagnose the actual local implementation,
not a generic SAC implementation. Inspect the source and evidence before drawing
conclusions. If using papers, verify primary sources and distinguish canonical
SD-SAC from experimental additions.

Local paths:

| Purpose | Absolute path |
| --- | --- |
| Only editable source checkout | `C:/Users/szulc/.codex/worktrees/tmrl-training-fixes/AITrackmania` |
| Dirty main checkout — do not edit sources | `H:/Studia/inzynierskie/inzynierkav2/AITrackmania` |
| Runtime frozen for the last two pilots — NEVER edit/pull | `C:/Users/szulc/.codex/worktrees/tmrl-sd-sac-projection-runtime/AITrackmania` |
| Frozen runtime commit | `9821c23eabfacc989869a71e7b97e99ce006deca` |
| Python environment | `H:/Studia/inzynierskie/inzynierkav2/AITrackmania/.venv/Scripts/python.exe` |
| Artifact BASE | `H:/Studia/inzynierskie/inzynierkav2/AITrackmania/artifacts/tmrl-test-comparison` |

The diagnosis was published atomically to `origin/codex/tmrl-training-fixes` and
`origin/codex/tmrl-algorithm-runs`, most recently at `be6a161e` before retirement.
The retirement/campaign commit follows it. Use the checkout's actual current
commit for new work; do not assume `be6a161e` remains HEAD. Source edits, including
documentation inside Python, change the package fingerprint: old checkpoints
must be read with their original frozen runtime, never with an override.

Portable evidence is committed under
`experiments/tmrl_test_comparison/evidence/sd-projlr08-final/`,
`evidence/sd-proj08-final/`, and `evidence/sd-fit07-final/`.
Large original checkpoints, replay and event logs remain local under BASE; they
are intentionally absent from Git. Without those files, do not claim to have
reproduced model/replay diagnostics. Request their specific non-secret artifacts
if needed; never invent missing causal telemetry.

Entry points:

- `SD_SAC_REPAIR_DECISIONS.md`: closed decisions and the final calibration trace.
- `SD_SAC_OBSERVABILITY_PROPOSAL.md`: prepared, unimplemented causal-clock proposal.
- `archive/20261008/`: historical READINESS/HANDOFF/TUNING/NIGHT_QUEUE and audit logs;
  all historical ACTIVE/RUNNING/NEXT instructions are superseded by retirement.
- BASE `sd-projlr08-audit/`: original diagnostics and verification receipts.
- BASE `sd-sac-retired-20261008/`: retirement/integrity inventory and old queue pointers.

Do not blindly follow `diagnosis.json`'s early "both critics no throttle"
description as a statement about their **mean**: the later target-calibration
audit corrects that distinction.

### 2. Actual implementation and experiment contract

Relevant implementation paths, relative to the editable or frozen source root:

- `trackmaniarl/algorithms/stable_discrete_soft_actor_critic.py`
- `trackmaniarl/algorithms/sac_config.py`, `sac_support.py`, `sd_sac_objectives.py`
- `trackmaniarl/models/sensor_actor_critic.py`, `models/backbones.py`
- `trackmaniarl/experiments/graph_iqn_v5.py` and the encoders it composes
- `trackmaniarl/trackmania/reward_step.py`, `reward_config.py`
- `trackmaniarl/distributed/` coordinator, replay/checkpoint and actor policies
- `trackmaniarl/core/fingerprint.py`, replay transition/n-step handling
- `experiments/tmrl_test_comparison/generate.py`, `components.py`
- `tests/unit/learning/test_sd_sac_*.py`, comparison/preflight/launcher tests.

The class is SD-SAC-inspired, not a claim of faithful reproduction of every
paper detail. It uses a categorical actor over 78 actions; disjoint actor/Q1/Q2
parameters and encoder copies; two all-action critics; double-average soft
targets; clipped critic regression; entropy anchoring; learned temperature;
and Polyak target networks. Examine the saved options and frozen source for the
precise actor objective, entropy reference, detach boundaries and loss weights.

Latest runtime configuration:

| Setting | Value |
| --- | --- |
| Map UID | `oqIJ5rQDRrNwLPTh9H2p_W4tLof` |
| Pipeline / encoder | V5 telemetry/context/physics/recovery/track; incident-gated GNN + Simba V6 |
| Actions | 78 discrete gas/brake-mode/steer combinations, including timed-brake taps |
| Actor objective | `soft_q_forward_kl` — explicitly experimental |
| Actor learning rate | `0.0009` in last failed pilot; `0.0001` in predecessor |
| Critic / entropy learning rates | `0.0003` / `0.0003` |
| Alpha initialization / minimum | `0.2` / `0.01` |
| Target entropy | `0.8` **raw nats**, not `0.8 * log(78)` in these final pilots |
| Entropy penalty beta | `0.0005`, behavior-entropy anchor |
| Extra terminal loss coefficient | `0` |
| Q clipping epsilon / Polyak tau | `0.5` / `0.005` |
| Discount / n-step | `0.995` / `1` |
| Batch / warmup / UTD | `256` / `10000` / `0.25` |
| Replay | Uniform; capacity 1000000; original replay immutable |
| Weight projection | Stored hyperspherical actor/Q1/Q2 weights projected after Adam, before Polyak |
| Interaction / race deadline | 50 ms decisions; intentional 150 s penalized terminal |
| Pilot target | 145408 total transitions, fresh initialization, no resume |

The final fast-actor pilot changed only actor LR relative to the projected
predecessor. The runs have different replay populations; their result difference
is not a controlled paired causal estimate.

### 3. Actual game outcomes and checkpoint identities

| Attempt | Actual outcome | Final checkpoint SHA256 |
| --- | --- | --- |
| `sd-projlr08`: `tmrl-sd-sac-projected-fastactor-s17`, CP33856 | 0/10 finishes; mean progress 1.060849%; 145424 transitions / 33856 updates, credit0 | `f2b0d4aa942606c1b6c0c058942d7e4e0f816a909ea17733635bf38ab0d40f53` |
| `sd-proj08`: `tmrl-sd-sac-projected-s17`, CP33866 | 2/10 finishes; mean progress51.558708%; median finished87.675s; 145466 / 33866, credit0.5 | `333522bce19b998118da2ca3acde864c17e092f2d821f82d54d861d16256e8dc` |
| Earlier actor-fit pilot CP33866 | 0/10; mean progress5.770238%; 145464 / 33866 | `a243b4f50d210d882860b74e4626ff42b369c3f1c2fd78a25fe81068d05906d7` |
| Earlier best complete slow pilot CP33852 | 3/10; still failed qualification | `90705fda277c26536c2c7d08a7e501d2b2dc751c92e457935befcdf6e2827fa6` |

Checkpoint locations:

- BASE `/tmrl-sd-sac-projected-fastactor-s17/checkpoints/distributed-update-00033856.pt`
- BASE `/tmrl-sd-sac-projected-s17/checkpoints/distributed-update-00033866.pt`
- BASE `/sd-fit07-final-audit/cp33866.pt`: verified immutable actor-fit copy.
- BASE `/sd-c07/a/slow-complete/checkpoints/distributed-update-00033852.pt`.

Last pilot fingerprint:
`c022d63558596fe1a341d616f4d83681b2d9435ad90d966ea645cd6fe2cc0fb7`.
Its normal closure verified all43 owned PID+creation-time identities closed,
mutex free,1883 immutable pins unchanged; predecessor1865 pins. Actual checkpoint
hash, finite state, full budget, accounted updates and drained credit passed.
The last run closed2026-10-08 04:50:06UTC. Ten trials had correct UID,
1446 timing measurements, max50ms, no controller/telemetry errors; skipped
frames2906/max6 were reported. Thus the quality failure is not being excused
by an incomplete run or a silently invalid final evaluation. No process is
supposed to remain active. Never use a historical PID as current ownership.

### 4. Frozen-Q actor diagnostics: what they establish

Current saved starts: actor chooses action8, no throttle + timed brake;
Q1 ranks56, Q2 ranks62, also no throttle. **Mean Q**, however, ranks action35
with gas1 on all131 saved starts. Mean gas probability mass0.56028 and best-gas
advantage+0.002131; min Q mass0.50999, advantage-0.001755. A min-Q substitution
is not supported as a start fix. Actor entropy4.25073 is close to log78.

Mixed-row forward-KL fitting on disposable projected actor copies with saved
Adam,64 steps, paired seeds17/29:

- LR.0009 improves held agreement23.24%→76.95/77.15%, forward KL.37559→.08744/.08687,
  and mean-Q greedy regret.00861→.0005356/.0005184; **start agreement stays0**.
- Canonical SAC with saved Adam performs worse, but saved moments were trained
  on forward KL, so that alone does not establish SAC inferiority.
- Fresh-Adam matched controls largely remove SAC's deficit in reverse KL;
  SAC.07828/.07276 versus forward.07556/.07422; neither fixes starts.
- Start-only fitting104 fit starts/27 held starts achieves100% held agreement
  in both seeds, action35. Actor can fit these targets; no capacity bottleneck
  has been established. General reverse KL worsens.471377→.71689.
- Mixtures with start fractions.01/.1/.25 pass general guards but all have0
  held start agreement. Standalone greedy-margin penalties also fail starts.
- Start fraction.25 plus margin.1 fits all starts, but general greedy regret
  .00082685/.00091310 fails the predeclared20% protection versus controls.
- A value-gap-aware margin fails general regret and/or held starts.
- Sharp target alpha.001 fixes starts and improves greedy regret, but fails
  distribution KL guards. Inverse-logit.1 compensation gives nearly uniform
  distributions and fails KL; it does not rescue calibration.
- Two-stage sharp64→ordinary64 fits starts and passes old64-step comparisons,
  but fails the matched ordinary128-step KL comparison. No promotion.
- Centered-logit score regression improves its own MSE but fails starts and
  general KL/regret, including matched fresh-Adam controls.
- Intermediate ordinary fitting reaches start agreement100% at48 steps and
  reverses to0 at64. Selecting the attractive intermediate checkpoint after
  observing this trace is not independent validation or a runtime repair.

Mixed diagnostics use ordinary fit2048/held512 and start104/27 from the same
whole-episode split. Some initial fit/held samples contain only3/1 starts;
expected12 start draws over64x128 diagnostic samples is **not** a reconstruction
of actual runtime sampling.131 starts have9 exact decoded observation hashes.
Do not infer actual training undersampling from that diagnostic alone.

Raw/tangent actor gradients are globally aligned; initial saved-Adam or
first-moment-reset directions do not explain the eventual finite behavior.
Finite copies are demonstrations of fitting against frozen approximate Q,
not proof of critic correctness or improved driving. Worsened held actions
are moving nonterminal states, not just reset states:62/71 worsened rows;
41/51 transitions56→35 add gas across17/18 episodes.

### 5. Critic calibration and finite drift

Current terminal MAE≈5.5292 versus predecessor≈2.0858, on different replay
populations; nonterminal Bellman MAE≈.06185. Recorded soft behavior-return proxy
MAE≈3.869 is **off-policy behavior**, not ground truth for the current policy.
That return audit already exists; do not repeat it as a new discovery.

Terminal clipping blocks a selected branch in only1/130 rows per critic (.77%)
in the final snapshot and0% of sampled nonterminals. It is not evidence of
pervasive blocked terminal gradients. Terminal target=immediate reward,
bootstrap0; mean-minus-min nonterminal target gap.01718 and entropy bootstrap
.03785 do not identify true values.

Projected disposable critic/saved-Adam calibration, frozen actor/targets/alpha,
whole-episode holdout, lambda0/.01/.1/1,seeds17/29,48 steps each:

- Initial held terminal MAE5.016299; held nonterminal MAE.07138495.
- Fixed relative20% nonterminal guard≤.08566194.
- Lambda0 final nonterminal MAE.070387/.074598; terminal4.993965/5.013276.
- Lambda.01 terminal4.550828/4.597501 improves, but nonterminal
  .113856/.115229 fails in **both seeds**. Higher weights fail more severely.
- Episode-paired, family-adjusted terminal gains do not waive nonterminal drift.

Zero-update parameter gradient audit on the exact same partition:
105/25 fit/held terminals,1024/1024 nonterminals; no-progress56/13,
slow-progress30/7,time-limit19/5. Terminal MSE tangent cosine with fit/held
nonterminal clipped loss+.391678/+.666113; held reason cosines+.490299,
+.710553,+.171710. There are negative individual-parameter dot products, but
no initial global conflict. Terminal MSE gradient norm22.71267 versus
nonterminal MSE.21923; account for normalization/frequency and Adam before
interpreting scale.

Non-mutating saved/fresh/zero-first-moment Adam algebra, baseline and previously
tested terminal weight.01 with reason decomposition: **all15 initial directions
locally improve held clipped loss/MSE/MAE**. Eight float64 scalar Adam controls
passed, no model optimizer steps. This does not justify resetting Adam.

Final trajectory control,192 copied steps total,212.36s, fixed300s cap:
lambda0/.01 × seeds17/29 ×48 steps; trace0/1/4/8/16/32/48. All four final MAE
endpoints reproduce prior results **exactly**, maximum error0. Both weighted
seeds first fail the sampled MAE guard at step8 (onset is bracketed4→8, not
proven to occur exactly8). At48 held nonterminal MSE.095405/.090436 versus
initial.033756; fit MSE.080726/.059229 versus initial.027232. Actual held
clipped loss also worsens. Thus this is a finite tradeoff affecting fit and
held states, not merely MAE/MSE disagreement or ordinary train-only overfit.
No specific optimizer/clipping bug was established. Close generic weight/LR/
reset grids unless a new concrete mechanism makes one counterfactual decisive.

Evidence files: `projected-calibration*.json`, `critic-gradient-conflict*.json`,
`critic-adam-directions*.json`, `calibration-trajectory*.json`.
All original model/target/**all** optimizer states and actual checkpoint SHA
were unchanged; copied processes closed. Never claim an exact process identity
was captured when a short foreground audit finished before identity capture.

### 6. Representation, termination and causal history

- Feature/head geometry reconstructs linear outputs and satisfies Cauchy
  bounds. Terminal rewards lie within the observed feature-norm envelope for
  both critics on both checkpoints. No demonstrated output-range limitation.
- Low effective feature rank already exists in the predecessor. Different
  populations and normalization scales prevent a causal collapse claim.
- Hashing **all**145424/145466 decoded current replay observations finds
  **zero exact terminal/nonterminal aliases** in either checkpoint.
  Nearest-neighbor distances are descriptive, not a classifier or label-bug proof.
- Replay info deliberately retains only `_trackmaniarl_behavior_entropy`.
  Terminal reasons are joined from original events by exact episode and step:
  all130 terminals match endpoint steps=row step+1, previous links pass.
- Reasons:69no_progress/37slow_progress/24time_limit. Q1/Q2 terminal MAE:
  4.2454/4.2379,4.6690/4.6947,10.5076/10.5670 respectively. Timeouts are18.46%
  of rows and35.18% of absolute mean-Q terminal error. This is association,
  not proof of failure cause.
- V5 omits explicit absolute race clock, reward no-progress age and reward
  rolling-progress window. Frame advance and incident memory are different
  quantities. Missing explicit inputs alone do not establish nonidentifiability.
- Actual frozen V5, synthetic identical-motion clock histories0→50ms versus
  149900→149950ms: every context/physics/recovery/track branch is exactly
  identical, max error0. This proves clock-shift information loss in that
  controlled input; it is not a saved replay alias or proof of failed-driving cause.
- The configured150s race deadline is an **intentional penalized terminal**.
  Collection/telemetry interruptions are separate truncations. Three focused
  tests pass: penalized race terminal, zero terminal bootstrap, truncation
  bootstrap. Automatically relabeling timeouts as truncations changes the task.

**Do not feed post-action endpoint logs into current observations.** Causal
pre-action progress counters were not preserved in replay. A logged endpoint
reason/elapsed window is not the state available before its action. Do not guess
or rewrite old replay to make it appear causal.

An unimplemented, scoped hypothesis is normalized remaining-race-clock input to
an SD-SAC-only adapter. Compare with an **identical constant-clock adapter**,
same parameter count/initialization, to distinguish information from capacity.
Actor and both online/target critics get the same causal current/next clock;
clock_t comes from telemetry for s_t before a_t, clock_next from next telemetry.
Reset correctly, represent missing-clock validity, freeze normalization against
the150s deadline, test finite/bounds and no future leakage. Keep reward,
termination, shared features/GNN and optimizer settings fixed. Use a new runtime,
config/fingerprint and fresh collection if verified causal clocks are absent.
No old replay rewrite or fingerprint override. This requires explicit scope
authorization and is not currently implemented or scheduled.

Later progress-history proposals would need a read-only causal snapshot after
previous scoring/before next action: `_step-_last_progress_step`,
`_window_progress_m`, window age/fill. Aggregates do not fully specify future
deque expiration; do not claim full Markov sufficiency. Do not combine this
intervention with the clock in the first discriminating experiment.

### 7. Investigation strategy and deliverables

1. Verify current retirement status, source and checkpoint availability. Read
   existing source/tests/results together; classify facts, hypotheses and missing
   evidence. Consolidate complementary read-only measurements into one load.
2. Audit actual objective equations, target construction, probabilities/actions,
   entropy/alpha units, saved optimizer/options, projection/Polyak order and
   terminal/truncation semantics. Do not assume a paper formula equals this
   configured experimental objective. Review action35/56 values against actual
   physics only with appropriate causal evidence.
3. Rank at most three concrete mechanisms by evidence and experiment cost.
   Explicitly say which closed hypotheses stay closed and why. Avoid another
   catalog of unrelated audits or broad coefficient sweeps.
4. For the leading mechanism, specify one matched control, fixed seeds/rows/
   targets, a predeclared budget, meaningful held metrics, rejection/stop rule,
   and the precise decision a result would change. A local derivative cannot
   establish finite-step behavior; a frozen-Q fit cannot establish good driving.
5. Produce a minimal proposed patch and relevant regression checks if it fits
   newly authorized scope. Shared reward/model/GNN/feature changes require their
   own reviewed proposal; this handoff does not silently permit them. Preserve
   old source/checkpoints/replay/logs/STOP and the main training campaign.
6. Only a later explicitly authorized, fresh bounded pilot can test driving.
   Preserve the old gate≥8/10 finishes, complete≥145408 transitions, finite/
   matching fingerprint and actual SHA, accounted/drained updates,10 complete
   correct-UID trials, timing≤100ms, no errors, reported skips and full closure.
   Passing it does not automatically put SD-SAC back in the standard campaign
   or authorize full/multi-week training.

Return: (a) short diagnosis with evidence paths; (b) exact causal claims and
limitations; (c) prioritized mechanism and single discriminating experiment;
(d) concrete patch/proposal and test results; (e) expected benefit/risk and
explicit required scope; (f) whether to abandon the branch if rejected.
Do not call a CPU success a driving repair, claim completion from issued commands,
or continue probing indefinitely without a decision.

### 8. Execution safeguards, if a future experiment is authorized

Offline CPU idle/single-thread, disposable copies, no controller. Load original
checkpoints with the appropriate FROZEN cwd/PYTHONPATH, `PYTHONNOUSERSITE=1`,
`PYTHONDONTWRITEBYTECODE=1`; offline-only `CUDA_VISIBLE_DEVICES=-1` and W&B disabled
must never leak into a real CUDA training process. Never print `.env` or secrets.
New outputs and proof paths, no overwriting old receipts. Verify actual CP SHA,
model/target/all optimizer hashes, original replay and immutable pins before/after.

Any new/touched STOP or direct human STOP wins; never automatically exempt/pin
it. No second controller: `Global\TrackmaniaRL.ComparisonController`. No UI
automation during learner/eval. Game must be ready, foreground and desktop
unlocked, correct UID; no security/signature/locked-desktop bypass or blind retry.
`Start-Process` must be Hidden. Capture PID+creation time for actual owned
processes, including descendants observed after launcher exit. Never kill a
bare reused PID or unrelated process. Close and preserve before moving on.

Former bounded SD pilot contract, for a separately authorized new attempt:
fresh unique queue/run/plan and predecessor/source/helper/asset/STOP pins,
validate-only before launch; max14400s from **actual** start, train targetTOTAL
145408/max11400s then10greedy/max2100s; SAVE=start+13800,HARD=start+14400,
independent guard/stage watchdog. No restart/extend/resume-on-changed-code or
fingerprint override. No owned controller/learner after HARD. Preserve closure,
actual finalSHA/finite/fingerprint/complete/accounted/drained state, mutex and
immutable pins. Historical used launchers must never be launched again.

Publish approved source changes only from the editable checkout, atomically to
both named branches. Never edit/pull the frozen runtime, change main's dirty
sources, unpause the retired automation, or alter the standard campaign to
accommodate an unqualified experimental variant.

## Koniec promptu

Status przekazania: diagnoza zachowana, naprawa niepotwierdzona, eksperyment
z zegarem nieuruchomiony. W nowej kampanii Borys otrzymuje **continuous SAC**,
nie alias `discrete-sac`/`dsac`/`sd-sac`. Zwykłe launchery odrzucają te aliasy.
Kontynuacja SD-SAC wymaga osobnej, świadomej decyzji człowieka.
