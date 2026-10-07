# Actor-fit pilot: completed, driving gate FAIL

The authorized single pilot sd-fit07d completed normally at20:04:20UTC on
2026-10-07. The final model finished **0/10** greedy trials. Mean progress was
5.770238%, median0.599639%, maximum51.659876%. Nine trials ended for slow progress
at0.55–1.20%; one reached51.66% before the150s time limit. This candidate is not
qualified for full training. Monitoring is PAUSED; no subsequent pilot or full
run was launched. Another live test requires a new direct human instruction.

## Completed budget and evaluation integrity

- Final CP33866:145464 transitions (target145408, permitted batch overshoot56),
  33866 updates, credit0, finite/accounted/drained. Original saved checkpoint and
  audit copy SHA verified:
  `a243b4f50d210d882860b74e4626ff42b369c3f1c2fd78a25fe81068d05906d7`.
- Ten complete trials, correct map UID throughout. All4477 expected race-timing
  measurements valid; max/p9950ms, no controller or telemetry errors. Skipped
  frames1248, max5, explicitly reported. Issued controls are not proof of game
  acceptance; the evaluation's measured progress is the driving evidence.
- Normal closure, forced processes[]. Post-closure verifier confirmed all
  51 observed exact PID/creation-time identities closed, mutex free,1260 immutable
  source/helper/asset/prior evidence pins unchanged. The stopped original
  CP25735 and prior completed CP33852 hashes remain unchanged.
- Every integrity/timing gate passed; the>=8/10 finishes requirement failed.
  QR PASS29/30 median54.3s is preserved. Full SD-SAC remains BLOCKED.

Frozen runtime remained281332d99fdb8bc1edb70d590260731699ab40bf. Actual initial
actor registration and both audited saved checkpoints agree on fingerprint
`1f4d26134a9c90b701d2cc1a3a447c30ac0ef053d447833a4a8a8048b2a81989`.
The different historical launch-confirmation snapshot is preserved and superseded
by actual identity evidence; no override occurred. The terminal reporting repair
published as207046eb remained editable only and was never injected into this run.

## Offline diagnosis of the final checkpoint

CPU-only inference used a SHA-verified copy, one thread and idle process priority.
No learner, optimizer, environment or controller was created; model tensor digests
and copied checkpoint SHA remained unchanged.

All137 recorded terminal transitions show mean selected-action Q+1.2866 against
mean terminal reward-2.0315, MAE/bias+3.3182. The terminal target is known without
bootstrap, so this confirms residual value miscalibration. It is lower than the
intermediate CP25000 all-terminal error5.1168, but the terminal population changed;
this is not a matched comparison or evidence that driving improved.

On1001 sampled nonterminal states with recorded terminated suffixes, Bellman MAE
is0.1053 while historical behavior soft-return proxy MAE is5.1727. Low Bellman
residual does not establish correct values because its continuation is supplied
by the learned target critic. Recorded behavior differs from current/greedy policy,
so the longer-return comparison is off-policy evidence, not ground truth.

The two critics' greedy rankings agree on89.58% of1161 sampled states, yet the
model fails the real evaluation. Agreement between critics is not a driving gate.
Mean actor entropy3.1439 remains above the raw target0.8 with alpha at the0.01
floor. Saved replay's138 episode-first states all select greedy action21:
gas1, brake0, steering-0.5. Mean top probability is only13.39%, and its advantage
over the second action is0.128 percentage points. Thus broad stochastic exploration
can coexist with one repeated deterministic starting choice. This saved-state
probe is not a trace of actual evaluation controls and does not prove a controller
fault or representation collapse. Actor-vs-critic argmax agreement is0% on these
starts with Q regret0.0327; action-value correctness remains unproven.

The forward-KL candidate did not solve driving. The earlier completed slow-SAC
variant scored3/10 with51.37% mean progress, while the immediate alpha-floor
predecessor was human-stopped before evaluation. The completed-candidate comparison
therefore does not isolate the effect of forward KL alone, nor establish a reliable
effect across seeds. No three-seed training is qualified by these results.

The next investigation, if separately authorized, should prioritize terminal value
calibration and the stochastic-training/greedy-evaluation gap before another actor
objective change. Sparse terminal sampling, function approximation and optimization
remain hypotheses. This audit does not justify blindly increasing terminal-loss
weight, removing the alpha floor or resuming a saved model on changed code.

## Preserved evidence

Repository evidence: `evidence/sd-fit07-final/` contains the closure, completion,
evaluation artifact, final critic audit, saved-start policy probe and concise
summary. Full originals and copied checkpoint remain under
`H:/Studia/inzynierskie/inzynierkav2/AITrackmania/artifacts/tmrl-test-comparison` in
sd-fit07d, tmrl-sd-sac-actorfit-s17 and sd-fit07-final-audit. Historical logs,
STOP files, checkpoints and journals were preserved; no used queue was restarted
or extended.
