# SD-SAC foreground recovery and preserved resume — 2026-10-07

Latest state: the newly authorized exact-source resume is now ACTIVE on a shorter
artifact path after a bounded Windows path-length failure. See
[actual continuation, evidence and loop limits](SD_SAC_RESUME_LOOPS_20261007.md).
The preparation-only statements below describe the earlier preparation snapshot.

The comprehensive pilot stopped at 2026-10-06 19:19:55 UTC (21:19 Warsaw)
because Windows denied foreground activation before the next episode reset.
The actor exited, the learner saved checkpoint 3272, and the queue closed
normally with no forced owned processes. Evaluation never launched. This is an
interrupted training run, with no result for the ten-trial driving gate.

## Repair and actual game checks

The editable keyboard reset now retries foreground acquisition for at most five
seconds, checking cancellation between attempts and waits. A final check verifies
the same game window immediately before each key-down. The editor sequence checks
Delete and Enter separately. Its two focus waits can total ten seconds, plus the
0.7 seconds of key/transition waits, unless the caller's guard expires earlier.
Direct keyboard reset also releases Delete if its hold is interrupted.

This handles transient activation denial or the operator returning to the game.
Persistent Windows foreground denial still produces a bounded error before reset
input. Windows does not guarantee that a background process can activate a game
while another application is being used; no foreground-lock setting, fake input,
security setting, or input-thread attachment is changed. The operating-system
restriction is documented in
[SetForegroundWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow).

Computer Use selected and activated the running Trackmania process 80684. With
no learner or evaluator active and the shared controller mutex held, two reset
checks on the repaired editable code passed. Both returned race time 10 ms,
33 telemetry fields, protocol 2, and map UID `oqIJ5rQDRrNwLPTh9H2p_W4tLof`.
The controller closed after each check. No policy was loaded and no learning
updates were performed. Evidence is under
`artifacts/tmrl-test-comparison/sd-sac-focus-repair-20261007/readiness-summary.json`.

Validation: 84 keyboard/focus, preflight, gamepad lifecycle, and comparison
launcher tests passed. An initial broader invocation used an excessively long
Windows temporary path and failed to create checkpoint temporary files; the
same tests passed using a fresh short external base directory. No implementation
change was made for that test-path problem. Ruff lint/format, strict mypy on the
changed source with followed imports, and diff checks passed.

## Saved training and resume boundary

Original checkpoint: `distributed-update-00003272.pt`.
SHA-256: `bc68ab6231f3e2ff21235961f1337144690031bb7034acc143e261f8f8b5401d`.
It contains 23,582 transitions, 3,272 updates, credit 123.5, and
earned = accounted = 3,395.5. Its learner tensors are finite. Replay and sampler
state are preserved. Training is incomplete and update credit is not drained.

The saved and recomputed fingerprints match:
`bb4a1819292e59a76cba405198cfd92ba05baee99a25bceabb6d339848cce652`.
The SQLite journal is intact and its identity matches the checkpoint; the
applied/pruned frontier is 646, with no pending chunks. The remaining target is
121,826 transitions; the configured total must remain 145,408.

A resume must use exactly frozen comprehensive source `ab736f53`, the original
training/environment/metadata configuration, full replay and optimizer restore,
and no fingerprint override. The repaired keyboard source has a different
fingerprint and cannot be silently substituted under this checkpoint. Existing
frozen runtimes, the original checkpoint and journal remain unchanged.

Offline resume preparation creates a separate run with a cloned checkpoint and
matching journal, preserving the old run and its retention-sensitive checkpoint.
It does not launch a learner or controller, update the active pointer, start a
new budget, or extend the old queue. A later launch needs its own bounded queue
and explicit human start instruction. On the original frozen code, Trackmania
must remain foreground for keyboard episode resets. Applying the new focus
repair to learning requires a fresh pilot from zero.

## Driving evidence and current readiness

The earlier comparison of comprehensive training progress 33.4% with previous
greedy evaluation progress 0% did not establish improvement. At a comparable
23,582-transition prefix, comprehensive/terminal/stability training mean progress
was 10.08%/13.09%/15.65%, and each had zero finishes. After warmup the means were
12.44%/13.21%/12.34%. Different episode counts and single runs do not establish
either improvement or regression. The comprehensive pilot already reached 32.66%
during warmup, before an update.

Full SD-SAC remains BLOCKED. QR's 29/30 finishes and 54.3 s median remain valid.
The completed failed queue remains closed; automation stays PAUSED. No new
training or ten-trial evaluation is launched by this repair/preparation work.
