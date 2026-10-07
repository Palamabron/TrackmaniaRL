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
