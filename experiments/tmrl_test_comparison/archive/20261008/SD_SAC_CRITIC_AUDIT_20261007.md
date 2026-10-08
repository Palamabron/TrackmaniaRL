# SD-SAC terminal reporting repair and saved-critic audit

The reporting defect is fixed in editable source. The saved CP25000 also shows a
real learned-value error: on all 106 recorded terminated failure transitions,
mean selected-action Q is +3.0702 while mean terminal reward is -2.0465. Terminal
MAE/bias is +5.1168. This boundary target is known without a policy assumption or
bootstrap. It does not identify the cause or establish correct unchosen-action
rankings.

The current sd-fit07d training/evaluation remains on frozen commit
281332d99fdb8bc1edb70d590260731699ab40bf. No learner, controller, optimizer, replay
reset, resume, new pilot or full training was created by this audit. The code fix
is for future runtimes; it must never be substituted into the running process or
used to resume its checkpoint under a changed source fingerprint. Full SD-SAC
remains BLOCKED until the actual driving gate and integrity checks pass.

## Reporting defect and regression checks

The learner emits the terminal absolute-error sum and terminal sample count for
each batch. The coordinator previously averaged per-batch terminal MAEs, including
zero values from batches without terminals. Empty batches diluted the reported
error; varying terminal counts also gave inappropriate batch weights.

`_MetricAccumulator` now derives terminal MAE from paired sufficient statistics:
sum of terminal absolute errors / sum of terminal sample counts. It emits
`critic/terminal_samples_total` to distinguish an empty window from measured zero
error. An empty window retains MAE 0 with total count 0; callers must inspect the
count. A MAE without its same-observation sufficient statistics is omitted rather
than presented as a sample-weighted estimate. Existing averaged count/error-sum
fields keep their per-batch units, and ordinary means/maxima are unchanged.

Historical log window updates 24500–27400: mean reported terminal MAE 1.0743,
pooled terminal MAE 4.8721. Terminal samples averaged 0.2497 per batch of 256.
These measurements use updating models and sampled replay; they are distinct
from the fixed-checkpoint, all-terminal calculation below. The repair affects
logging only, not losses, gradients, terminal sampling or learned parameters.

Validation: 50 tests passed across distributed contracts, SD-SAC stability and
the new audit return tests. The regression cases cover unequal terminal counts,
empty batches/windows, accumulator reset, unpaired observations, future-only
entropy, truncation, discontinuous steps, episode boundaries and backward links.
Ruff lint/format and mypy passed for the changed implementation/audit files.
An initial validation invocation used the frozen working directory and could not
find the new helper/tests; it made no edits. Validation was rerun from editable.

## Saved-checkpoint measurements

Checkpoint: update25000, 111985 replay transitions; this is an intermediate
checkpoint, not the final model. Source was copied before loading and source/copy
SHA equality was checked before and after inference:
`a6f7ca1f7de49f8233ecba5a5d6cb000d003a66f471696e573fc8fe2456efe85`.

The CPU audit uses one thread, idle process priority, disabled CUDA and no learner
or environment construction. Inference reads current and target model tensors
from the copied checkpoint and checks both tensor digests and checkpoint SHA
afterward. All 106 recorded terminated transitions and 1024 uniformly sampled
linked nonterminal transitions are evaluated (sampling seed17421). No parameters
are fitted, so no held-out optimization split is claimed.

| Measurement | Result | Meaning |
| --- | ---: | --- |
| Terminal selected-action Q mean | +3.0702 | Wrong sign against known negative terminal rewards |
| Terminal reward mean | -2.0465 | Exact terminal target; no continuation |
| Terminal absolute error mean | 5.1168 | Confirmed learned boundary error |
| Recorded-suffix nonterminal Bellman MAE | 0.0680 (989 states) | Low self-consistency error does not establish correct values |
| Recorded-suffix nonterminal soft-return proxy MAE | 4.0929 (989 states) | Historical behavior differs from the current policy |
| Nonterminal last20steps proxy bias | +5.5066 (26 states) | Small, selected sample; off-policy limitation remains |
| Actor entropy mean, all audited states | 3.3624 | Effective alpha floor0.01, target0.8 raw nats |
| Mean critic top-two action gap | 0.00354 | Near ties make argmax agreement fragile |
| Mean actor greedy Q regret | 0.00619 | Low argmax agreement alone is not a driving diagnosis |

The fixed CP25000 critics have zero greedy argmax agreement on these 1130 states.
The later moving-model log window had about47.9% on different replay batches.
These are different checkpoints/states, not a matched comparison or evidence of
improvement. Both must be read alongside the small Q margins.

Recorded soft returns include future behavior entropy at the checkpoint's fixed
effective alpha, exclude current-action entropy, and follow explicit replay links
within an episode with consecutive steps. Incomplete/truncated/broken suffixes
receive no invented bootstrap. 35 of the sampled nonterminal states lack an
eligible recorded terminal suffix and are excluded from return comparisons.
Replay was already used in training. Its historical stochastic behavior is not
the current policy or greedy evaluation, so return disagreement is a proxy; the
terminal reward comparison is the stronger independent check.

## Integrity and next decision

Frozen source/helper/asset/prior evidence pins and old saved CP25735/CP33852
hashes remain valid. No new/changed STOP was found. Post-audit check at19:46UTC
observed nine exact owned identities and continued ingest (135451 transitions),
with the original21:12UTC SAVE/21:22UTC HARD unchanged. This is a status snapshot,
not a completed driving evaluation.

One historical receipt correction: `launch-confirmation.json` contains prepared
fingerprint241eca1b…; actual initial actor registration, saved CP25000 and a fresh
calculation from the frozen runtime agree on
`1f4d26134a9c90b701d2cc1a3a447c30ac0ef053d447833a4a8a8048b2a81989`.
The old receipt is preserved. `post-audit-integrity.json` supersedes its identity
claim; no fingerprint override or runtime modification occurred.

Finish the already authorized pilot and its ten greedy trials before selecting
another learning change. If it fails, this audit prioritizes terminal value
calibration/sampling diagnosis over further actor argmax tuning. Sparse terminal
data (~one per1056 replay transitions), function approximation and optimization
remain candidate mechanisms, not isolated causes. A prior terminal auxiliary-loss
experiment changed multiple settings and failed; it does not justify blindly
reenabling that loss or increasing its coefficient. No next live test is launched
or authorized by this reporting repair.

Evidence in the repository: `evidence/sd-critic07/` (audit-final, copy receipt,
post-audit integrity and historical metric-window audit). Full copied checkpoint,
initial/final audit logs and original evidence remain in
`H:/Studia/inzynierskie/inzynierkav2/AITrackmania/artifacts/tmrl-test-comparison/sd-critic07`.
