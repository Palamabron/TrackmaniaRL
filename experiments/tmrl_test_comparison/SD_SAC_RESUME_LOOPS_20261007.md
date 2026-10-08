## 8 October 2026 05:12 UTC - projected terminal calibration rejected

Offline projected critic/saved-Adam copy probe completed all 384 steps in336.33s within600s cap. Both lambda0 baselines pass the held nonterminal drift guard. Every tested extra terminal weight(.01,.1,1) fails that guard in both seeds. At lambda.01,held terminal MAE improves from lambda0 4.994/5.013 to4.551/4.598,while held nonterminal MAE worsens to.113856/.115229 against the fixed limit.085662. Higher weights worsen nonterminal error further(.429/.434 and.913/1.159).

Whole-episode paired bootstrap with three-candidate family adjustment gives positive terminal-error reductions versus lambda0: .01 interval[.3456,.5213],.1[1.6123,2.2928],1[2.9242,4.7702]. Both-seed terminal gains also beat the initial baseline,but none qualifies because all nonzero weights fail the predeclared drift guard. This frozen-target reused-replay diagnostic does not establish driving quality; no terminal weighting promoted and no new pilot launched.

Final assertions confirm original checkpoint,models and saved Adam unchanged. Independent actual checkpoint SHA f2b0d4aa942606c1b6c0c058942d7e4e0f816a909ea17733635bf38ab0d40f53,all probe exactPID/ctime closed,immutable pins valid,no new/changed STOP. Evidence: evidence/sd-projlr08-final/projected-calibration.json and projected-calibration-verification.json. Full BLOCKED;automationACTIVE5min. Next scoped offline hypothesis: inspect actor objective gradients and compare projected forward-KL/canonical SAC copies against identical frozen mean-Q targets with episode-held rows and saved Adam. No runtime setting change justified yet.

## 8 October 2026 05:08 UTC - projected critic copy probe running

New standalone probe_sd_sac_projected_calibration.py is executing offline on CPU idle/single-thread against immutable CP33856 f2b0d4aa942606c1b6c0c058942d7e4e0f816a909ea17733635bf38ab0d40f53. Only independent q1/q2 and saved critic Adam copies receive updates; saved actor,target critics,alpha and Bellman targets remain frozen. Projection after each copied Adam step; no Polyak update. No game controller/runtime learner/new training run.

Fixed whole-episode fit/held split, all available eligible terminal rows plus1024 sampled nonterminals per split. Stratified128+128 sampling restores empirical fit terminal prevalence for the clipped Bellman baseline; extra terminal MSE lambda0/.01/.1/1,seeds17/29,48 steps each,384 total,600s copy-compute cap. Baseline held terminal MAE5.01630,held nonterminal0.071385; relative20% guard<=0.085662. Both completed lambda0 copies pass guard and leave terminal error near baseline. Nonzero-grid result pending; do not infer success or launch a candidate from partial output.

Three focused numerical tests pass (empirical class weighting,explicit terminal contribution,clipped-versus-extra gradient). Ruff and boundary-scoped mypy pass. Process receipts and incremental results: BASE/sd-projlr08-audit/projected-calibration-processes.json and projected-calibration.json. AutomationACTIVE5min; poll existing execsession37505 or inspect recorded exactPID/ctime,never start a duplicate. Candidate interpretation requires both seed guards,held-terminal paired comparison against lambda0 and initial baseline,and original checkpoint/model/Adam immutability. Full remains BLOCKED.

## 8 October 2026 05:01 UTC - mean/min and target-clipping audit

Completed zero-update CPU idle/single-thread inference on both immutable projected checkpoints. The current mean-Q actor target ranks action35 (gas1) first on all131 saved starts; Q1 and Q2 individually rank no-gas actions56/62 first. Therefore the preceding no-gas finding for the individual critics does not mean their averaged actor target also prefers no gas. Mean-Q gas mass56.03%,best-gas advantage0.00213; min-Q gas mass51.00%,best-gas advantage-0.00176. Predecessor mean-Q gas mass93.77%,advantage0.02486. These are different saved replay states,not a paired causal comparison. Switching actor targets to min-Q is not supported as a fix for this failed start behavior.

Terminal clipping blocks the selected loss branch for only1/130 samples per critic (0.77%) in the current checkpoint,versus0/181 and1/181 previously. Nonterminal blocked fractions0%. This checkpoint snapshot does not explain terminal MAE5.53 through pervasive clipped gradients and cannot reconstruct historical gradients. Terminal bootstrap and mean-minus-min target gap are exactly0; terminal targets match immediate rewards. Nonterminal mean-minus-min target gap0.01718 on1024 rows,entropy bootstrap0.03785. These counterfactual targets do not establish true Q values.

New runnable audit: audit_sd_sac_target_calibration.py. Ruff and boundary-scoped mypy pass; two real CPU inference executions pass fingerprint/SHA/model immutability checks. Terminal-zero-bootstrap,target-equals-reward,and mean>=min invariants pass. No optimizer/controller/training run created. Evidence: [current](evidence/sd-projlr08-final/target-calibration.json),[predecessor](evidence/sd-projlr08-final/predecessor-target-calibration.json).

Next diagnostic remains offline: test whether projected disposable critic+savedAdam copies can reduce episode-held terminal error while preserving fixed nonterminal Bellman targets under a relative20% drift guard; include an unmodified-loss baseline and paired seeds. Earlier unprojected checkpoint weighting probes failed the guard; do not promote terminal weighting or claim an architecture bottleneck. Only a positive,repeatable scoped result can justify a fresh pilot. Current sd-projlr08 remains closed;full BLOCKED;automationACTIVE5min. No new controller launched.

## 8 October 2026 04:55 UTC - fast actor pilot failed; offline diagnosis

sd-projlr08 completed normally at04:50:06 UTC. Real evaluation: **0/10 finishes, mean progress1.060849%**, versus predecessor2/10 and51.558708%. All other gate checks passed: ten complete correct-UID trials,1446 valid timing measurements,max50ms,no controller/telemetry errors; skipped frames2906,max6. Full training remains BLOCKED. No next pilot launched.

Normal guard closure at04:50:07 UTC,forced[]; external post-closure verification confirms all43 observed exactPID/ctime closed,mutex free,1883 immutable pins valid,no new/changed STOP. Final CP33856 SHA f2b0d4aa942606c1b6c0c058942d7e4e0f816a909ea17733635bf38ab0d40f53:145424 transitions,33856 updates,credit0,finite/accounted/drained/complete. Frozen9821c23e and prior checkpoints preserved.

Completed offline CPU idle/single-thread audits,zero runtime learner/controller updates:130 terminals MAE5.52922 (predecessor2.08577);944 analyzed nonterminals Bellman MAE0.06185 (predecessor0.08369). These are different saved replay samples,not a paired causal comparison. Critic pair greedy agreement on the sampled replay falls to5.20% from70.79%. On131 saved starts actor selects8,critic1 selects56,critic2/min selects62; all three are no-throttle timed-brake actions. Actor entropy4.25073; minQ margin0.06533; actor/minQ agreement0%. This is evidence against faster actor tracking as a sufficient repair,not proof of a capacity/architecture bottleneck.

Completed disposable saved-Adam actor probe64 steps per LR/seed,384 total,86.77s,checkpoint/model/Adam unchanged. Fixed averageQ held agreement23.24% initially; LR0.0001 gives25.00/25.00%,0.0003 gives25.20/24.61%,0.0009 gives76.95/77.15%. For0.0009 held KL0.37559->0.08744/0.08687 and regret0.00861->0.000536/0.000518,while saved-start top1 agreement remains0% for every variant. Frozen-Q fitting improvements did not establish useful driving. Next step: offline inspect critic target/value calibration and mean-versus-min actor target before selecting a justified fresh plan. No terminal-weighting promotion,shared reward/model/GNN changes,resume,or reused-queue restart.

Evidence: [closure](evidence/sd-projlr08-final/post-closure-verification.json),[critic](evidence/sd-projlr08-final/critic-audit.json),[starts](evidence/sd-projlr08-final/initial-landscape.json),[actor copies](evidence/sd-projlr08-final/actor-lr-probe.json). Automation ACTIVE every5min during offline diagnosis; earlier active-training states below are historical.

## Aktualizacja 2026-10-08 02:20UTC: nowy projected actor-LR pilot działa

sd-projlr08 wystartował02:18:45.468189UTC=04:18Warsaw, run tmrl-sd-sac-projected-fastactor-s17,W&Bryzo37yc. Aktor registered i świeży ingest205/0updates02:19:23UTC; warmup nie ocenia jazdy. SAVE06:08:45UTC/HARD06:18:45UTC,cap14400s,targetCAŁKOWITY145408/max11400+10greedy/max2100. Runner74772/guard8472/learner7632/actor66896 exactctimes w receipts. Preflight10ms/33fields/57reads/correctUID. Frozen projection runtime9821c23e unchanged;1883pins,fingerprintc022d63558596fe1a341d616f4d83681b2d9435ad90d966ea645cd6fe2cc0fb7.

Jedyna zmiana learning setting względem sd-proj08: actorLR.0001→.0009. Fresh odzera,noresume; reward/model/GNN/replay/UTD/alpha.01/beta.0005/criticLR/objective/projection bez zmian. Uzasadnienie: completed paired64step disposable savedAdam actorcopies,fixedaverageQ,CPUidle1thread. HeldKL .6118/.6125→.2123/.2094,regret .001408/.001304→.000575/.000330,agreement85.16/85.74%→89.26/88.87%; wszystkie LR variants poprawiły starts agreement0→100%. LR.0003 również poprawiał fitting; wybór.0009 bada szybsze tracking movingQ,nie izoluje prawdziwości Q i nie dowodzi poprawy jazdy. Saved model/Adam/CP unchanged; brak zapisania kopii policy.

27testówPASS:8nowychscope/window +19applicableguards; validate-only,Ruff i mypy z pominięciem zewnętrznych/importowanych boundariesPASS. Pierwsze wywołanie obejmowało legacy validate_plan oczekujący auth-path zamiast aktualnego prose-auth (27PASS/1FAIL),zachowano diagnostykę;łącznie5legacy actorLR/auth-plan przypadków nie stosuje się do nowego launchera. Nowe scope tests weryfikują dokładną zmianęactorLR,zakazreward/training/entropy/full/stale/reuse. Bez edycji starych helpers/frozen. MonitoringACTIVE5min do>=15min zdrowych learned checks,potemgodzinny tylko daleko odSAVE. Gate>=8/10 i pełne kontrole,fullBLOCKED; nigdyrestart/extend/nowySTOPoverride.

## Aktualizacja 2026-10-08: sd-proj08 zakończony, dalsza diagnoza offline

Świeży projected pilot zakończył się normalnie 02:07:37UTC; guard closure 02:07:38UTC, forced[]. Wszystkie zaobserwowane exactPID/ctime zamknięte, mutex wolny, 1865 immutable pins i poprzedni CP niezmienione. Final CP33866 SHA333522bce19b998118da2ca3acde864c17e092f2d821f82d54d861d16256e8dc:145466 transitions/33866 updates/credit0.5, finite/accounted/drained/complete.

Rzeczywista ocena FAIL2/10, średni postęp51.558708%, mediana dwóch met87.675s. Dziesięć kompletnych prób z prawidłowym UID,10404/10404 pomiarów timing valid,max50ms,bez błędów kontrolera/telemetrii; skips2262,max7. Wszystkie kontrole poza>=8finishes PASS. Lepszy wynik niż bezpośredni actorfit0/10 nie oznacza lepszej niezawodności od wcześniejszego slow3/10; pełne treningi nadal BLOCKED.

Offline CPU idle/single-thread,zero learner/controller updates:181 terminali MAE2.0858,978 analizowanych nonterminali Bellman MAE0.08369; behavior-return proxy ma ograniczenia off-policy. Na182 zapisanych startach oba krytyki wybierają akcję5,aktor akcję65 (agreement0%,regret minQ0.02737),entropia aktora3.9276 vs soft-target2.7918. Normy hyperspherical0.99999982–1.00000012: projekcja działa,nie dowodzi poprawności krytyka. Rozpoczęto bounded disposable actor+savedAdam LR probe64steps,seeds17/29,LR.0001/.0003/.0009 przy fixed averageQ/alpha.01/beta unchanged/projection. Wynik jeszcze nieznany; brak nowego pilota lub zmiany savedpolicy. Autoryzowana pętla pozostaje ACTIVE5min; kolejny świeży pilot wymaga konkretnego uzasadnienia,nowego planu/predecessor/pins/STOP,bez restartu sd-proj08.

## 8 October 2026 01:32 Warsaw — projection pilot running

Following the direct human go, sd-proj08 started at01:30:24 Warsaw on frozen9821c23e.
Actual preflight passed (10ms,33fields,57reads,correctUID); actor registered and
new ingest confirmed. Start verification:1149 transitions,0 updates (warmup),
1865 immutable pins valid, no new STOP/run failure. Monitoring ACTIVE every5min;
hourly cadence requires sustained verified health. SAVE05:20:24/HARD05:30:24
Warsaw; no extension/restart. Driving remains unqualified, full BLOCKED.
See [scheduled handoff](SD_SAC_SCHEDULE_20261008.md) and sd-proj08/start-verification.json.
Earlier PREPARED_NOT_LAUNCHED statements are historical preparation receipts.

## 8 October 2026 — pilots scheduled from 01:30 Warsaw

New direct human authorization resumes justified bounded SD-SAC tests and monitoring.
First queue sd-proj08 is PREPARED_NOT_LAUNCHED on frozen9821c23e, fresh projection
control; live game readiness and driving remain unverified. Existing heartbeat is
ACTIVE for01:30 and will switch to5-minute checks, then60-minute checks after three
healthy observations spanning15 minutes. Actual guard deadlines remain binding.
Full training remains BLOCKED; no automatic full launch. See
[scheduled pilot handoff](SD_SAC_SCHEDULE_20261008.md). Earlier PAUSED/offline-only
statements below describe historical scopes, superseded only by this authorization.

Offline optimizer repair 2026-10-07: SD-SAC now projects hyperspherical weights after
critic/actor Adam and before Polyak; old unprojected Adam contract cannot resume.
Saved raw row norms reached4.20. Fixed-Q actor copies at unchangedalpha.01 improved
held agreement84.59/88.58% to92.20/93.53% with projection, not proof of driving/Q truth.
Small terminal-weight/head-only controls selected no statistically supported repair
under the nonterminal drift guard. Fresh sd-sac-projected-s17.yaml PREPARED_NOT_LAUNCHED;
no new run/controller/game/network publication.176 tests/Ruff/mypy passed,1260pins
and original CP SHA unchanged, automationPAUSED, full17/29/43 BLOCKED; QR preserved.
See [SD_SAC_PROJECTION_REPAIR_20261007.md](SD_SAC_PROJECTION_REPAIR_20261007.md).

Offline joint-calibration follow-up 2026-10-07: SHA-pinned CP33866 actorfit,
138 starts/78 actions, both critics choose71 in138/138; actor21 ranks11/5/8
(Q1/Q2/average).384 disposable steps, lambda0.1/1/5/10, seeds17/29,48 each.
All held-terminal reductions have positive family-adjusted paired intervals,
but ALL weights violate held-nonterminal MAE<=0.145 in both seeds. No viable
joint calibration under this guard; capacity/interference conclusion conditional
on frozen targets/split/budget. No live run/resume/networking; immutable CP/model/
Adam unchanged, automationPAUSED/fullBLOCKED. Local offline deliverables only.
See [SD_SAC_JOINT_CALIBRATION_20261007.md](SD_SAC_JOINT_CALIBRATION_20261007.md).

Offline follow-up 2026-10-07: terminal materialization/targets/gradient sign checked;
137 exact terminal reward targets, only1/274 clipped gradients blocked.384 disposable
critic-copy optimizer steps, no runtime learner/controller. Corrected oversampling
showed no consistent held-episode terminal improvement; terminal-only MSE reduced
held terminal MAE3.3102 to0.2463/0.2500 but raised nonterminal residual0.1210 to
11.8800/11.9412, so it is rejected as a repair. Separate scalar-tensor replay-read
bug fixed with regression tests; ordinary saved action indices were unaffected.
87 tests/Ruff/mypy passed; original CP and frozen pins unchanged. No live launch,
no qualified learning-setting change; full BLOCKED/automation PAUSED/QR preserved.
See [SD_SAC_CRITIC_PROBE_20261007.md](SD_SAC_CRITIC_PROBE_20261007.md).

Final 2026-10-07 20:04UTC: sd-fit07d CLOSED / FAIL, automation PAUSED.
Real evaluation0/10 finishes, mean progress5.770238%, median0.599639%; nine
slow_progress failures and one51.66% time_limit. All ten correct-UID trials valid,
4477/4477 timing measurements/max50ms, no controller/telemetry errors; skips1248/max5.
FinalCP33866:145464 transitions/33866updates/credit0, finite/accounted/drained,
SHA a243b4f50d210d882860b74e4626ff42b369c3f1c2fd78a25fe81068d05906d7.
Normal closure/forced[], all51 exact identities closed/mutexfree/1260pins unchanged.
Final offline audit still finds terminal MAE3.3182 on137 states. No new live test or
full training; further live work requires a new direct human instruction. FullSD
BLOCKED; QR PASS preserved. Earlier ACTIVE sections below are historical snapshots.
[SD_SAC_ACTORFIT_RESULT_20261007.md](SD_SAC_ACTORFIT_RESULT_20261007.md).

Update 2026-10-07 19:46UTC: terminal MAE aggregation repaired in editable source;
50 regression/contract/stability tests, Ruff and mypy passed. Frozen sd-fit07d
continues unchanged; no new live test/full training. Read-only CP25000 audit finds
known terminal target miscalibration: mean Q+3.0702 vs reward-2.0465, MAE5.1168 on
all106 terminal failures. Off-policy return proxies do not establish action rankings
or driving readiness. Full remains BLOCKED pending actual evaluation. Actual actor/
checkpoint/frozen-runtime fingerprint1f4d2613… supersedes the differing historical
launch-confirmation snapshot; no override. Details/evidence:
[SD_SAC_CRITIC_AUDIT_20261007.md](SD_SAC_CRITIC_AUDIT_20261007.md).

Actor-fit actual start 2026-10-07 17:22:36.869341UTC (19:22 Warsaw): NEW sd-fit07d is RUNNING, fresh tmrl-sd-sac-actorfit-s17/W&B6d20j27j, frozen281332d99fdb8bc1edb70d590260731699ab40bf. Actualpreflight ready10ms/33fields/58reads/correctUID, learner83588 and actor71412 registered/collecting, initialupdates0 and freshingest confirmed. Objective-only experimentalforwardKL; noresume, unchangedreward/model/GNN/replay/UTD. Train145408/max11400s then10greedy/max2100s, whole14400s, SAVE21:12UTC/HARD21:22UTC (23:12/23:22Warsaw). ExactPIDctime inlive-ownedreceipt. AutomationACTIVE15min, newSTOPwins, noautonexttest/full. Warmup is not driving evidence; fullBLOCKED until>=8/10 plus all integrity/timing checks. Earlier sd-fit07 failedforeground/normalclosed; sd-fit07b/c preparationonly preserved. See sd-fit07d/launch-confirmation.json and actualstatus, not older snapshots.

> Prepared only after human STOP: new actor-fit candidate `configs/diagnostic/sd-sac-actorfit-s17.yaml` changes actor objective SAC→experimental forwardKL; all other learning/reward/model/GNN/replay/UTD settings remain as stopped alpha-floor. CPU actor-copy probe: heldout Q-argmax agreement13.28% SAC vs91.80% forwardKL after300steps; episode-first action0→57 for forwardKL. Frozen-Q fitting is not proof of driving or critic correctness. Added greedy-margin diagnostics and strict preparation/scope checks. See SD_SAC_ACTORFIT_PREPARATION_20261007.md. No launch, no checkpoint resume, no STOP exemptions; automationPAUSED/fullBLOCKED.

> Offline analysis after human STOP (2026-10-07): same 1024 replay observations across both saved models show current alpha-floor greedy gas-off66.89%, mean steer-0.970. All256 sampled episode-first observations choose action0 (gas0/brake0/steer-1); top probability only2.76%, so broad stochastic entropy masks an unfavorable greedy maximum. Actor feature std0.0385 does not support global representation collapse. Comparable-budget last30 training mean progress8.37% vs8.87%, median7.33% vs1.25%, finishes0/30 both; these are training episodes, not evaluation. Evidence: artifacts/tmrl-test-comparison/sd-af07-stopped-analysis-20261007/{analysis.json,RAPORT.md}. CPU inference only,0updates/noController/models and checkpoints unchanged. Improvement unproven, full BLOCKED, human STOP and automation PAUSED remain in force.

> Current state — 2026-10-07 14:01 Europe/Warsaw: HUMAN STOP / PAUSED. Direct instruction: "przerwij i tak na ten moment trening". sd-af07 closed normally at 12:00:26 UTC, forced processes [], all 19 observed exact PID/creation-time identities closed, controller mutex free. No evaluation or subsequent training launched. Full SD-SAC remains BLOCKED. Earlier ACTIVE sections below are historical snapshots.
>
> Preserved alpha-floor candidate CP25735: 114821/145408 transitions, 25735 updates, remaining update credit 470.25; finite, fingerprint matched and accounting valid, but budget incomplete and credit not drained. SHA256: 38279862c9c56417dc9804869c66f2bb8b06c894341ccaf01aecb8b198487938. Immutable source/helpers and four previous saved checkpoint hashes verified unchanged. Evidence: artifacts/tmrl-test-comparison/sd-af07/human-stop-verification.json and human-stop-checkpoint.json. New STOP preserved and automation PAUSED; do not launch until a new direct human instruction.
>
> Driving improvement remains unproven for this candidate: evaluation NEVER_LAUNCHED (not 0/10). Latest completed predecessor scored 3/10 finishes. Current training entropy metrics are not a driving qualification.

## 2026-10-07 12:13 Warsaw — completed slow pilot FAIL, fresh alpha-floor-only pilot ACTIVE

Completed exact continuation sd-c07:145408 transitions/33852 updates/credit0,
finite/accounted/drained, CP33852 SHA90705fda277c26536c2c7d08a7e501d2b2dc751c92e457935befcdf6e2827fa6.
Actual evaluation3/10 finishes, median143.22s, mean progress51.365148%.
Ten complete correct-UID trials, timing maxima60ms, no controller/telemetry errors,
skips9278/max5. All gate checks passed except>=8 finishes. This fails readiness.
Compared with the incomplete checkpoint's2/10 and57.836355% mean progress, extra
training did not establish a consistent improvement. No full training has started.
Normal closure10:09:35UTC, forced[], all41 observed exact PID/ctime identities
closed, mutex free, source/helper/original evidence and final checkpoint unchanged.

Offline temperature probe of this final checkpoint: savedalpha0.00027483, frozen-Q
target entropy0.0152 on1024 replay states; atalpha0.01 target entropy1.805.
No learner updates, saved-policy changes or game input. This suggests excessively
sharp targets as a testable mechanism; it does not prove critic correctness or
that a floor improves driving. Evidence BASE/sd-temp08/temperature-sensitivity.json.

Fresh bounded queue BASE/sd-af07 is ACTIVE, run tmrl-sd-sac-alphafloor02-s17,
W&B gdfg75cl. Same frozen70d3eb0a runtime, NEVER EDIT/PULL; fresh replay/zero initial
updates, no checkpoint resume. The only algorithm setting changed from actorslow is
entropy_coefficient_min0.01. ActorLR0.0001,critic/entropyLR0.0003,target0.8,beta0.0005,
SAC objective,alpha init0.2,terminalcoef0,qclip0.5,reward/model/GNN/replay/UTD unchanged.
Fingerprint e629a9f7d08deb923a19c14c4c53982a8e0b8ee761595cf3ac101eab42523d14.
27 plan/predecessor tests and validate-only passed. Actual preflight30ms/33fields/
54reads/correctUID. Runner82556,guard71832,learner76756,actor50956 exact identities
persisted in actual-launch-receipt.json and live-owned-identity-receipt.json.
ActualSTART10:11:53.139355UTC,SAVE14:01:53UTC/HARD14:11:53UTC (16:01/16:11Warsaw).
Cap14400s,train145408/max11400+10greedy/max2100; never extend or restart.
Historical STOP exceptions are inherited exactly, never automatically re-pinned.
New/changed STOP wins. No UI or second controller while learner/evaluation is active.
FullSD remains BLOCKED until actual gate and matching full configurations; QR PASS
29/30 median54.3s preserved. Older ACTIVE sections below are historical snapshots.

## 2026-10-07 11:55 Warsaw — slow training COMPLETE, ten-trial evaluation ACTIVE

The new human instruction reauthorizes SD-SAC repair/test loops and prioritizes SD-SAC
before other algorithms. Historical STOP files remain preserved with exact SHA/mtime
exemptions; a new or changed STOP always wins.

Actual saved-policy evaluation sd-e08 completed normally: **2/10 finishes**, median
149.24s, mean progress57.836355%. Ten complete correct-UID trials; timing, SHA and
controller/telemetry checks passed, skips reported. All observed owned identities
closed, mutex free, immutable pins unchanged. This is improved driving versus earlier
0/10 results, but it fails the>=8/10 gate and uses incomplete training.
Evidence: BASE/sd-e08/post-closure-verification.json and its evaluation artifact.

New bounded attempt BASE/sd-c07 completed training normally, run slow-complete,
W&B8dj5aeh9. Final145408 transitions/33852 updates/credit0, finite/accounted/drained.
CP33852 SHA90705fda277c26536c2c7d08a7e501d2b2dc751c92e457935befcdf6e2827fa6.
Checkpoint validation passed; the new ten-trial evaluation is now ACTIVE.
FULL restore confirmed140754 transitions/32256 updates, replay140754, credit432.5,
same frozen70d3eb0a source and fingerprint2be95ca917238a1fd5f90760e24c2763d899b3633784b5285acc1a914372b1bc.
Only run/artifact identity changed. Original checkpoint/journal remain byte-identical.
Total target remains145408 (4654 remaining); no target extension, replay reset or
changed-code/settings resume. Trainmax900s, then10greedy/max2100s, overallcap3600s.
ActualSTART09:47:33.022069UTC, SAVE10:42:33UTC/HARD10:47:33UTC (12:42/12:47Warsaw).
Preflight20ms/33fields/55reads/correctUID and19 completion/STOP/accounting tests passed.
Exact identities are persisted in sd-c07/live-owned-identity-receipt.json.
The separate alpha-floor-only candidate is PREPARED_NOT_LAUNCHED, not the active run.

Full SD-SAC remains BLOCKED pending complete/finite/accounted/drained checkpoint and
>=8/10 real finishes plus all identity/timing/error/skips checks. Existing full YAMLs
still use different defaults and must be aligned with the qualified candidate before
any three-seed start. QR PASS29/30 median54.3s is preserved. No other algorithm or
full training started. Earlier ACTIVE sections are historical snapshots.

## 2026-10-07 07:32 Warsaw — fresh actorslow pilot ACTIVE

Queue `queue-sd-sac-actorslow-20261007`, run `tmrl-sd-sac-actorslow-s17`, W&B olarxz70
API running. Fresh from zero using unchanged frozen refit70d3eb0a; no resume.
Only actorLR0.0009->0.0001; critic/entropyLR0.0003,target0.8,beta0.0005,SAC objective,
alpha init0.2/unbounded,terminalcoef0,qclip0.5,model/GNN/reward/replay/UTD unchanged.
Hypothesis: slower actor updates may prevent representation collapse. Offline evidence
is mixed: fresh fixed-Q copies100steps heldout agreement0.535/0.398 for LR0.0001/0.0009,
but forwardKL3.992/3.200 and entropy4.343/3.915. Both retain feature diversity.
This does not prove the cause, critic correctness or driving. Collapsed full-actor
copies remain poorly fitted after100steps; evidence BASE/sd-sac-refit-audit-20261007.
24 guard tests+validate-only passed; preparation10ms/33fields/60reads and actual
preflight10ms/33fields/55reads/correctUID. Runner56556,guard37024,learner63824,
actor64872 identities in actual-launch-receipt.json. ActualSTART05:31:45.606638UTC,
SAVE09:21:45.606638UTC/HARD09:31:45.606638UTC (11:21/11:31Warsaw),cap14400s.
Train145408/max11400+10greedy/max2100. UnderSAVE stayturn waits<=60s toclosure/HARD;
no owned learner/controller afterHARD. NewSTOP wins; never extend/restart/noUI.
Refit FAIL and all previous checkpoints/receipts remain preserved and verified.
FullSD BLOCKED until real>=8/10 plus all completion/identity/timing checks.
QR PASS29/30 median54.3s preserved. Authorized repair loops ACTIVE; no automatic full.
Older ACTIVE entries below are historical snapshots.

## 2026-10-07 07:22 Warsaw — refit COMPLETE, driving FAIL; offline diagnosis active

The fresh refit queue completed normally at05:22:14UTC; deadline closure forced[].
All27 exact owned PID/creation-time identities are closed and the shared mutex is free.
W&B aqsyvox9/6v7bhym0 API finished. Complete145433 transitions/33858 updates,
credit0.25, earned=accounted33858.25, drained and finite. CP33858 SHA
58f1c4db6bfc539988979a1d7a672b8ce4344538fc62ef4f5ebd4fb8faf993bc
and frozen source/helper/prior receipt pins verified unchanged, including prior CP33857.
Actual driving FAIL0/10; meanprogress4.787796%,
10 complete correctUID trials, timing maxima<=60ms, no controller/telemetry errors,
skips831/max6. FullSD remains BLOCKED; QR PASS29/30 median54.3s preserved.
The audit on exact frozen70d3 source is CPU-only, no controller or saved-policy changes.
Actor greedy action33 on1024/1024 replay states and128/128 starts, gas1/steer-1/6;
alpha0.001243, entropy0.2525 versus target0.8. Actor feature std0.000506 versus
critic feature std0.042807/0.041055; actor/Q agreement0.0957. This supports representation
collapse and poor actor fitting; it does not establish critic correctness. Independent
1000-step fixed-Q head fitting reaches only0.373 agreement at LR0.0009; full-actor
copy probes completed with limited recovery. Evidence: BASE/sd-sac-refit-audit-20261007.
No next game test has launched. Authorized repair/test/diagnosis loops remain ACTIVE;
never restart refit or extend its expired-as-completed attempt. Old ACTIVE entries below
are historical snapshots. New STOP wins. No changed-code resume or automatic full start.

## 2026-10-07 04:33 Warsaw — fresh refit pilot ACTIVE

Following the authorized repair loop, clipping5 was rejected: independent100-step
critic copies gave held-out nonterminal fixed-target MAE0.52267 with epsilon0.5
versus0.53640 with epsilon5; terminal MAE0.65203 versus0.65821. No saved policy changed.
A fresh bounded refit pilot now uses the earlier best-driving beta0.0005/target0.8
SAC objective with actorLR0.0009; the previous actorLR test was interrupted.
ForwardKL, separate entropyLR, alpha bounds and terminal auxiliary loss are explicitly
rolled back together. This does not isolate their individual effects or establish
critic correctness. Numerical/contracts/focus repairs remain; reward/model/GNN/replay/
UTD unchanged. No checkpoint resume. Exact new frozen source70d3eb0a, fingerprint
b9202ac959f155a529952b74b84d01b588e098156fbd75a841beaf27f04a1c85.
Queue `queue-sd-sac-refit-20261007`, run `tmrl-sd-sac-refit-s17`, W&Baqsyvox9 APIrunning.
Actual start02:32:54.190437UTC; SAVE06:22:54.190437UTC/HARD06:32:54.190437UTC
(08:22/08:32Warsaw), cap14400s,train145408/max11400+10greedy/max2100.
Runner30620,guard68232,learner36960,actor42340 exact identities in actual-launch-receipt.
24guard tests+18CPU learning tests+validate-only passed; actualpreflight10ms/33fields/
correctUID/57reads. Actor registered and collecting. These checks are not a driving gate.
Previous resume02 FAIL and all evidence preserved. New STOP wins; no UI/secondcontroller.
UnderSAVE remain in turn with waits<=60s untilclosure/HARD; never extend/restart.
FullSD BLOCKED,QR PASS preserved,monitorACTIVE for authorized bounded repair loops.


## 2026-10-07 04:20 Warsaw — resume02 COMPLETE, driving FAIL

This supersedes the ACTIVE snapshot below. Queue resume02 completed normally at
02:12:37 UTC; guard closure at 02:12:38 UTC has forced[]. Post-closure verification
confirmed all 31 exact owned PID/creation-time identities closed, controller mutex
free, 440 immutable pins unchanged, and training/evaluation W&B runs finished.
Checkpoint33857 SHA c3ebe43048f24bf709fb1993da432e308fb569ddc3f319c1ebb002c5c0b73502:
145430 transitions,33857 updates,credit0.5; finite, complete, drained and accounted.
Actual driving gate FAIL0/10, mean progress3.72697%; ten complete correct-map trials,
3626/3626 valid timing measurements,max60ms,p99=50ms,no controller/telemetry errors,
1728 skipped frames,max4. FullSD remains BLOCKED. QR PASS stays preserved.
Offline audit found greedy action28 (gas plus full brake) on128 saved start states,
actor/Q agreement7.62% on1024 replay states, alpha0.01, entropy3.279. Fixed-Q independent
actor-head fitting improves agreement but does not prove critic correctness or driving.
Recorded behavior soft-return proxy bias+8.981 on21220 complete-episode states is a
warning, not on-policy calibration. Independent critic clipping probe is diagnostic;
no saved weights changed and no new game test launched. Evidence:
`artifacts/tmrl-test-comparison/sd-sac-resume02-audit-20261007` and queue
`post-closure-verification.json`. Authorized repair loops and automation remain ACTIVE.
Never restart this completed queue or resume these weights on changed source.

# SD-SAC exact-source continuation and bounded repair loops — 2026-10-07

The latest direct human instruction authorizes sensible autonomous repair,
bounded-test and diagnosis loops until the SD-SAC driving gate and handoff are
complete. Full training never starts automatically. New or modified STOP wins.
Every attempt has a separate immutable plan and time limit; used queues never
restart and running attempts never gain extra time. Changed-code checkpoint
resume, replay reset and shared-reward changes remain forbidden.

## Actual continuation

Queue: H:/Studia/inzynierskie/inzynierkav2/AITrackmania/artifacts/tmrl-test-comparison/queue-sd-sac-comprehensive-resume02-20261007.
Run: tmrl-sd-sac-resume02-s17; config BASE/sd-r07/resume-sd-sac.yaml.
Frozen comprehensive runtime ab736f53b3b96f517be8c72dc85bdcefb50a0606 remains
unchanged. Full checkpoint fingerprint bb4a1819292e59a76cba405198cfd92ba05baee99a25bceabb6d339848cce652.
Initial checkpoint SHA bc68ab6231f3e2ff21235961f1337144690031bb7034acc143e261f8f8b5401d.
Original checkpoint and journal remain preserved in the old closed run.

Actual log confirms FULL state restored:23582 transitions,3272 updates;
replay23582 and credit123.5 continue, with new ingested rollouts and updates.
The total target remains145408, with121826 remaining at launch. Optimizers,
sampler, RNG, replay and durable journal are restored, with no reset.
The newer keyboard focus patch3cacbb57 is deliberately not substituted into
this checkpoint's source. Persistent foreground denial remains a possible
bounded failure; no security or focus-permission bypass is used.

START2026-10-06T23:48:20.701294UTC (7Oct01:48Warsaw).
SAVE2026-10-07T03:36:30.115902UTC (05:36Warsaw).
HARD2026-10-07T03:46:30.115902UTC (05:46Warsaw).
Effective cap14289.414608s, clamped to resume01's deadline without extension.
Train max11400s, then ten greedy trials max2100s. Under SAVE keep checking at
intervals <=60s until normal closure/HARD; no controller/learner survives HARD.

Actual-launch-receipt.json pins runner63992/ctime1791330490.7654765,
learner57576/1791330516.88723, actor49712/1791330516.8990867,
launcher53032, guard launcher78860 and actual guard44104 in effective-deadline.
W&B [5xgna8bn](https://wandb.ai/dsc-pjatk-warsaw/my-trackmania-agent/runs/5xgna8bn)
was verified running by API. Actor registered and collecting; this is launch
evidence, not a useful-driving result. No UI or second controller during the run.

## Preserved failure and verification

Resume01 failed before game controller or learner: Windows refused a temporary
checkpoint decompression path exceeding its length limit. Its failure log,
status and normal deadline closure (forced[]) are preserved; it is never
restarted. A separate short-path full-state clone was prepared directly from
the original saved checkpoint and journal. Its actual codec load passed.
The first new validator drafts rejected serialization defaults and an incorrect
import/runtime invocation; these external-helper issues were corrected before
launch. Final40 contract/preparation tests and validate-only passed on exact
frozen cwd/PYTHONPATH. No frozen/main-source edits were made for these failures.
Actual preflight ready:10ms race time,33fields,correctUID,58countdown reads.

Prepared receipts are historical preparation records, not live launch status.
Use actual launch/status/effective-deadline and events. Source freeze includes
the initial cloned checkpoint as a launch input pin; normal retention may later
remove that cloned input after full restore. Its initial SHA remains recorded;
the original checkpoint and immutable source/helper/evidence pins must stay
unchanged. New run checkpoints/journal are legitimate training outputs.

## Gate and next decision

Require complete145408 training, finite checkpoint, matching source fingerprint
and SHA, exact update accounting and drained credit; ten complete correct-map
trials, all timing maxima<=100ms, no controller/telemetry errors, reported skips
and at least eight finishes. FullSD stays BLOCKED until this actual gate.
Training/warmup progress and CPU tests do not establish improved driving.
Comparable earlier training data did not show a demonstrated improvement.
QR29/30median54.3PASS is preserved and never rerun for this repair.

On failure preserve evidence, save/close all owned PID/ctime identities and
release the shared mutex before diagnosing and considering a new bounded test.
Never resume a checkpoint under changed source. On PASS verify manual full
generator, seed17/29/43 YAML, guard and setup; publish an honest manual handoff
without starting full training. Monitor remains ACTIVE for the authorized loops,
silent while healthy; pause only after the completed objective or explicit STOP.
