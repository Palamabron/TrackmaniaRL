Actor-fit actual start 2026-10-07 17:22:36.869341UTC (19:22 Warsaw): NEW sd-fit07d is RUNNING, fresh tmrl-sd-sac-actorfit-s17/W&B6d20j27j, frozen281332d99fdb8bc1edb70d590260731699ab40bf. Actualpreflight ready10ms/33fields/58reads/correctUID, learner83588 and actor71412 registered/collecting, initialupdates0 and freshingest confirmed. Objective-only experimentalforwardKL; noresume, unchangedreward/model/GNN/replay/UTD. Train145408/max11400s then10greedy/max2100s, whole14400s, SAVE21:12UTC/HARD21:22UTC (23:12/23:22Warsaw). ExactPIDctime inlive-ownedreceipt. AutomationACTIVE15min, newSTOPwins, noautonexttest/full. Warmup is not driving evidence; fullBLOCKED until>=8/10 plus all integrity/timing checks. Earlier sd-fit07 failedforeground/normalclosed; sd-fit07b/c preparationonly preserved. See sd-fit07d/launch-confirmation.json and actualstatus, not older snapshots.

# SD-SAC actor-fit candidate — prepared, not launched

The stopped alpha-floor checkpoint chooses gas0/steer-1 at saved episode-first observations, while its average critic chooses action57 (gas1/steer+0.5). This is an actor/critic fit problem on those observations, not proof that critic action rankings are correct.

## Prepared change

`configs/diagnostic/sd-sac-actorfit-s17.yaml` changes only the learner's `actor_objective` from `sac` to the existing explicit experimental `soft_q_forward_kl` mode compared with sd-af07. ActorLR0.0001, critic/entropyLR0.0003, alpha minimum0.01/init0.2, target entropy0.8, beta0.0005 behavior anchor, terminal auxiliary coefficient0 and qclip0.5 remain unchanged. Reward/model/GNN/replay capacity/sampling/UTD remain unchanged. Output paths/run identity/metadata and the explicit ten-trial evaluation gate are updated separately. Defaults of canonical SD-SAC and full YAML17/29/43 are NOT changed. No forced-throttle override or action mask is introduced.

New diagnostics expose greedy probability margin, probability assigned to the critic-greedy action, soft-Q cross entropy and critic top-two value margin. This prevents high categorical entropy alone from looking like a repaired greedy policy. Checkpoint compatibility already rejects objective switching; never resume an old SAC checkpoint into this candidate.

## Offline evidence and limits

Evidence: `artifacts/tmrl-test-comparison/sd-af07-actor-fit-20261007/comparison.json` under the main artifact base. Two independent copies of the actual stopped actor and its optimizer state were optimized at LR0.0001 against identical detached frozen critic values, alpha0.01 and unchanged beta0.0005. There were768 training and256 heldout states from disjoint replay episodes,128 saved episode-first observations,300 updates per copy. Probe-only gradient norm clipping10 applied equally to both copies; the production learner's optimizer behavior is unchanged. No saved model, original optimizer, replay, checkpoint, game controller or environment was changed/created.

| Heldout result after300 actor-copy steps | Existing SAC | Forward KL candidate |
|---|---:|---:|
| Agreement with frozen Q argmax |13.28%|91.80%|
| Forward KL |0.3310|0.08168|
| Episode-first greedy action |22 on128/128|57 on128/128|

Initially both copies selected action0 on128/128 first observations. Forward KL selected57 already after100 steps. This justifies an objective-only fresh bounded experiment. It does NOT establish critic correctness, causal driving improvement, canonical SD-SAC qualification or a real finish rate. Earlier forward-KL pilots changed several other mechanisms together and failed; this candidate remains experimental and unqualified.

## Preparation and later start

Run `python -m experiments.tmrl_test_comparison.prepare_sd_sac_actorfit --baseline <sd-af07/sd-sac.yaml> --candidate experiments/tmrl_test_comparison/configs/diagnostic/sd-sac-actorfit-s17.yaml --receipt <new-receipt.json>` from this editable checkout with the main virtual-environment interpreter. This validates the exact scope against the stopped baseline, RunSpec, asset SHA, candidate fingerprint and unused run identity. Receipt creation is exclusive. It NEVER starts training, manipulates STOP files or grants STOP exceptions.

A later explicit human start must create a NEW immutable runtime at the published commit and a NEW bounded queue using this template, with actual launch time/deadlines, full helper/source/config pins and exact PID/creation-time capture. Do not run the old queue or the generic `run_assigned.ps1 -Pilot` expecting this candidate: that launcher selects an older config. Materialize candidate output paths under the shared artifact base before freezing the new queue.

Train fresh from zero to145408 transitions, maximum11400s; then10 greedy trials maximum2100s, whole queue14400s, SAVE600s before HARD, same controller mutex, preflight/STOP/stage watchdog/guard and closure checks as previous pilots. All old STOP/checkpoints/journals stay preserved. Today's explicit STOP remains effective; preparation is not a new launch authorization and automation remainsPAUSED. No full training or evaluation has been started.

Driving gate remains>=8/10 finishes plus complete/finite/fingerprint/SHA/drained/accounted training,10complete correct UID trials/all timing maxima<=100ms/noerrors/skips report. Verify every owned PID/ctime closed, mutex free, immutable inputs and final checkpoint before another controller. Full training remainsBLOCKED until actual qualification.


## Human-authorized launch attempt, 7 October 2026 17:02 UTC

The user authorized one fresh actor-fit test. New queue `sd-fit07` used immutable runtime281332d99fdb8bc1edb70d590260731699ab40bf, fresh145408 target, train11400s/eval10x2100s/whole14400s. Its actual preflight blocked before learner/evaluation: Windows refused Trackmania foreground activation (SetForegroundWindow=0). `sd-fit07/post-closure-verification.json` confirms normal closure/forced[], all6 captured exact PID+creation identities closed, mutex free, immutable inputs valid, no training run directory. This is NOT a failed driving result. No learner or game evaluation ran. Earlier five legacy actor-LR-plan tests were inapplicable to this new objective-only launcher;19 applicable guard tests plus8 objective-scope tests passed. Standalone validation initially lacked PYTHONPATH; the corrected frozen-runtime environment passed before launch.

`sd-fit07b` and `sd-fit07c` are preserved preparation-only snapshots, never launched. Their authorization prose had a text-encoding defect; the new source helper uses Unicode escapes for the exact human instruction. None supersedes a new STOP or resets a deadline. Next queue `sd-fit07d` is not yet prepared/launched. Await the human placing Trackmania in foreground; native UI automation is unavailable in this session. A new bounded attempt must recheck closure/pins/mutex/STOP and retain every prior attempt. Current test is blocked before training, full readiness remains BLOCKED, automation stays PAUSED pending actual start.
