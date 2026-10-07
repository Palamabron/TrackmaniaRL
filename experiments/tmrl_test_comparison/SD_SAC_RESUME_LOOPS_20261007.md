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
