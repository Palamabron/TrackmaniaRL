# SD-SAC implementation audit and repairs — 2026-10-06

The human request “Dobra to teraz na serio już napraw wszystkie problemy z SD SAC”
authorized a comprehensive code repair. The changes below are in the editable
training-fixes checkout. They do not modify or resume any frozen experiment.
Useful Trackmania driving remains unqualified; passing CPU tests is not a driving
result. No subsequent game pilot or evaluation was launched.

## Confirmed defects corrected

| Defect | Resulting behavior |
| --- | --- |
| `q_clip_epsilon=0` was accepted even though the clipped branch becomes constant and can suppress the TD gradient. | Require a finite positive clipping width; zero is not interpreted as disabling clipping. |
| A positive Python temperature could underflow to zero or overflow in float32, including learned log/exp round trips. | Validate the actual temperature representation and optional bounds before optimization. |
| Centered finite float32 Q values divided by a small valid alpha could overflow and poison KL/entropy diagnostics. | Compute the small all-action soft-Q log tensor in float64, without clipping advantages or changing the ordinary softmax distribution. |
| Shared actor/Q parameters could be updated by multiple independent Adam optimizers. | Reject overlapping optimizer ownership. First-party Trackmania models already use separate encoders. |
| Fractional actions were silently converted to integer actions; malformed vectors could broadcast; invalid importance weights could distort loss. | Validate action dtype/range, transition-aligned scalar fields, boolean episode flags, action dimensions, and finite non-negative weights with positive total. |
| The shared weight-denominator floor changed the loss when all positive weights were very small. | Normalize SD-SAC weights by their validated total; scaling weights does not change updates. |
| The terminal-only denominator floor suppressed valid subnormal terminal weights, and diagnostic averaging could overflow by adding finite critics. | Normalize terminal weights in float64 before applying errors, preserve zero terminal mass as zero loss/gradient, and average critics without an overflowing intermediate sum. |
| `0 * NaN` from an undefined true-terminal continuation contaminated the known reward target. | Ignore continuation only for true terminals with zero discount; reject non-finite nonterminal continuation. Truncations retain bootstrap. |
| A malformed current actor could be discovered after critic parameters had already changed. | Validate/cache its graph before optimization while preserving next/current forward order and using updated critics for the actor loss. |
| Missing Q margins appeared as measured zero, and categorical SD-SAC displayed an unused epsilon schedule. | Preserve unknown measurements as null with counts, report unused epsilon explicitly, and carry these semantics through transport, logs and evaluation artifacts. |
| Action-histogram entropy could be confused with conditional policy entropy. | Record conditional entropy in nats separately from normalized histogram entropy; retain the old histogram key as a compatibility alias. |

Numerical and contract regressions exercise the failures before their fixes.
The functional regression trains both actor objectives on a delayed-goal MDP and
compares both critics with an independently solved soft-Bellman oracle. It also
checks that a truncated transition continues to bootstrap. This is a synthetic
learning test without game input, not evidence that either objective drives well.

## Reset and preflight audit

The reset path ignored `SetForegroundWindow`'s return value and reported focus
success whenever a window was found. Windows can deny foreground activation, so
the old code could send Delete/Enter to a different foreground window. The repair
checks the actual foreground HWND before sending keys; fake Win32 tests require
zero key events on failure. [Microsoft's API contract](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow)
documents the failure result and foreground restrictions.

The used terminal queue helper slept one second and inspected only one telemetry
frame for a clock in `[0,2500]`. It did not poll through countdown/transient frames
or reject a finished frame, and it omitted the rejected clock and focus evidence.
The historical helper and its hash remain preserved. The future launcher uses a
bounded, cancellable race-start check with explicit failure observations and
cleanup. It requires the expected map/player before any reset input, sends no
unconditional finish-confirmation input, and does not weaken the race-start gate.
EOF during telemetry drain cannot validate an earlier complete start packet.
Reset cancellation checks before each new keydown; an already pressed key is
released during cleanup even when STOP or the deadline cancels the operation.
Callers retain the enclosing queue/launcher mutex and idle checks; the preflight
child does not acquire another process's controller lease.
These are verified implementation weaknesses; today's specific reset failure
cause is not established by the old log.

## What the independent audits did not establish

The ordinary double-average critic target, canonical actor/temperature signs,
action ordering, gas/brake binding, and truncated-vs-terminal bootstrap path were
consistent with their intended contracts. The paper/code comparison used the
[SD-SAC paper](https://arxiv.org/html/2209.10081) and
[authors' implementation](https://github.com/coldsummerday/SD-SAC/blob/main/src/libs/discrete_sac.py).
The implementation follows the paper's per-transition conservative clipped loss;
the published code reduces before its maximum. Its entropy-penalty coefficient
convention matches the code; the paper writes a factor of one half. Neither
convention difference proves a Trackmania failure cause.

The optional terminal regression is an experimental objective with substantial
reweighting: at coefficient 1, one terminal in a uniform batch of 256 receives
about 256 times its ordinary additional per-row gradient. It is not merely an
unclipping repair. The earlier preserved CPU probe improved terminal MAE from
13.921 to 3.009 while worsening the fixed old nonterminal-target MAE from 0.138 to
1.995. That tradeoff remains visible; no new arbitrary parameter setting was
selected in this repair.

The current V5 observation omits absolute race time, the no-progress counter, and
the rolling progress window used by environment termination. Identical physical
features can therefore have different termination targets depending on hidden
history. This is a shared partial-observability limitation, not an established
cause of SD-SAC's failed driving. Shared features, reward, model/GNN, replay and
historical baselines were not changed by this audit. A controlled observation
ablation would need separate authorization and a fresh experiment.

## Preserved terminal pilot outcome

`queue-sd-sac-terminal-20261006` trained normally from zero in frozen commit
`7704b7f9cfb6c7cdc5f32ad672136b9f8e01437d`, ending at
2026-10-06 18:17:35 UTC (20:17 Warsaw). It collected 145481/145408 transitions,
consumed 33870 updates and drained credit to 0.25; earned and accounted updates
both equal 33870.25. The complete finite checkpoint is:

`distributed-update-00033870.pt`

SHA256: `09507b686ffb7077b4ad1483ac9154c1e6907fd1a45272d7e5144924a3850505`.

The evaluation preflight failed at 18:17:50 UTC with
`Preflight reset did not return to the race start`. **No driving evaluation was
launched; this is not a 0/10 driving result.** Closure at 18:17:50.898527 UTC was
normal with no forced processes. The final audit checked 37 exact PID/creation
identities closed, a free comparison mutex, unchanged checkpoint/source/helper/
previous receipts and STOP pins, and W&B `mygl7lrw` finished. Evidence is in
`BASE/queue-sd-sac-terminal-20261006/final-closure-audit.json`.

A read-only CPU audit in exact frozen 7704 verified the checkpoint SHA and run
fingerprint. All 182 recorded starts choose action 71: full gas, brake tap and
steering +0.8333; mean entropy 1.81392, maximum probability 0.50849, alpha 0.01.
All 181 recorded terminals have twin selected-Q/reward MAE 0.71417. On 256 evenly
spaced replay states, the actor chooses only 71 or 75, both with gas, and actor/
average-Q agreement is 10.94%; at starts it is 0%. Twin-Q greedy agreement is
also 0% at starts. Thus the saved actor no longer repeats the previous no-gas
choice, but steering, brake use and critic disagreement remain driving concerns.
The previous MAE 14.414 used 137 different terminal states; this is not a paired
causal comparison. No learner was instantiated or updated and no model was saved
by this audit. See `terminal-checkpoint-audit.json` in the repair evidence folder.

The automation is PAUSED. Full SD-SAC remains BLOCKED pending actual >=8/10
finishes and complete/finite/fingerprint/SHA/drained/accounted training, ten valid
UID trials, timing maxima <=100 ms, no errors, and reported skipped frames. QR's
29/30, median 54.3 s PASS is preserved. Any further pilot, controller or evaluation
requires another direct human instruction; neither this queue nor a checkpoint
may be resumed on changed source.

## Validation and evidence

The final integrated selection passed **329 tests**, with one unrelated
port-creating backlog-stop test deliberately deselected. Ruff, format checks,
targeted mypy over all 13 edited source modules, and whitespace checks passed.
Generated full YAML for seeds 17/29/43 matched the generator; each first-party
model passed a synthetic CPU update and checkpoint round trip with environment
creation explicitly forbidden. These were validation runs, not full training.

Final integrated check totals and source hashes are recorded in
`BASE/sd-sac-comprehensive-repair-20261006/repair-verification.json`.
Tests use CPU-only execution and fake session/telemetry/Win32 backends; no test
issues real game input. Initial test invocation/environment failures are retained
in that record separately from the passing checks. Repairs were published
atomically to both authorized branches from the editable checkout.

Real GPU throughput, memory use and <=100 ms game timing have not been measured
for this edited version. They remain part of the next authorized bounded pilot,
along with useful driving; the preserved pilot used its earlier frozen source.
