# Continued SD-SAC repair — 5 October 2026

The human explicitly instructed: “No to poprawiaj SD SAC tak długo aż będzie sensowny”. This authorizes further bounded fresh SD-SAC diagnostics, with unchanged shared reward. PPO and the already queued QR-DQN run keep their frozen sources, stages and deadlines. A new SD-SAC controller may start only after their normal closure, with no new STOP and a free shared controller mutex. No full monthly training is started automatically. Completion of PPO or QR alone no longer ends the SD-SAC repair objective.

## Evidence from the failed behavior-entropy pilot

The `266e2629` seed17 pilot stopped at its 8100-second limit: 135406/145408 transitions, 30775 updates, 576.5 remaining credit. Earned and accounted credit match, but the complete-budget and drained-credit gates fail. Its ten greedy trials produced **0/10 finishes**, mean progress **3.5517%**, valid timing 1961/1961 measurements, maximum/p99 50 ms, no controller or telemetry errors, 2440 skipped telemetry frames, maximum 5. Full SD-SAC remains blocked.

The matching finite checkpoint SHA is `6fdab80112a7e27a5bfd65cd98e01eb20297f647b4b7258045ea726e82154175`. An offline CPU audit in its exact frozen runtime verified the fingerprint and inspected 1024 replay states plus all 118 episode starts. It created no controller, resumed no live training, and performed no learner updates.

At the sampled checkpoint, alpha was `1.9704e-5`; mean current entropy was 4.2507 nats and stored behavior entropy 4.2883. Mean maximum action probability was only 0.0329. The Q preference gradient norm was 0.0074725; the beta0.5 behavior anchor gradient norm was 0.0080897. Their cosine was **−0.9295**, and the anchor cancelled **1.0059** of the value gradient along its direction. This is a measured conflict on this batch, not proof that beta0.5 is universally incorrect. Q clipping blocked gradients in only 1/1024 and 0/1024 sampled critic entries.

At all recorded starts the actor selected action75 (full throttle, steer+1), while the double-average critic preferred action63 (full throttle, steer−2/3). Q differences were small; better agreement with these critics alone cannot establish useful driving.

## Next isolated hypothesis

`configs/diagnostic/sd-sac-anchor005-s17.yaml` changes the **policy hyperparameter beta0.5 → beta0.005** only. Target entropy stays 0.8 nats, initial alpha0.2, learning rate3e-4, seed17, categorical78 actions, model, uniform replay, gamma0.995, sampling, update ratio0.25 and the shared reward remain unchanged. Full configurations17/29/43 and the full-run block are unchanged pending live evidence.

An independent actor-head probe on frozen encoders and critics used the same 1024 states and original alpha. After 1000 Adam steps, beta0.5 kept mean entropy4.2439 and mean maximum probability0.0298; beta0.005 gave entropy3.5263 and maximum probability0.1331. This supports testing a weaker anchor. These are counterfactual CPU copies, **not a new trained driving policy**, and they were never saved or passed to evaluation.

The candidate starts from random initialization on a separate frozen checkout. Its short budget remains145408 interactions. The collection/drain stage allows10800 seconds to avoid repeating the previous premature time limit; ten greedy trials allow2100 seconds. The entire candidate has a14400-second cap from its actual start, SAVE600 seconds before HARD. Its passive waiter has a separate finite deadline and creates no learner or controller. Existing PPO/QR limits are not extended.

## Source changes and checks

Actor improvement now evaluates detached critic values under `no_grad`, avoiding a critic graph that was immediately discarded. The scalar actor objective and actor gradients are preserved. New diagnostics report maximum action probability, Q action spread, actor/Q greedy agreement, weighted anchor loss, reference entropy and its gap from current entropy. These describe learning; they do not substitute for the driving gate.

The new scalar-reference regression verifies actor gradients independently and confirms that actor improvement builds no critic graph. A78-action small-value objective test checks that the weaker anchor still allows the known preferred action to gain probability despite stale uniform replay entropy. The complete learning test directory passed106 tests. Standard CLI validation of the actual GNN/categorical78 composition completed a CPU synthetic update and zstd checkpoint roundtrip with no controller or W&B initialization. Ruff and mypy checks must pass before freezing the candidate.

## Success and continuation

Useful single-seed diagnostic behavior requires the complete budget and drained/reconciled credit, finite matching fingerprint/SHA, ten complete map-valid greedy trials, **at least8/10 finishes**, every timing measurement valid, maximum step100ms, no runtime errors and a skip report. If it fails, preserve the result and continue diagnosis under the human instruction; never relabel a failure as success or restart a used run directory. Each further hypothesis needs fresh sources/config identity, a bounded pilot and actual driving evidence. No single result establishes globally optimal HP,37-second pace, three-seed qualification or monthly readiness.

Local evidence is under `artifacts/tmrl-test-comparison/sd-sac-iterative-repair-20261005/` (`checkpoint-audit.json`, `actor-anchor-probe.json`); direct authorization is `SD-SAC-ITERATIVE-REPAIR-AUTHORIZATION.json` in the comparison artifact root.
