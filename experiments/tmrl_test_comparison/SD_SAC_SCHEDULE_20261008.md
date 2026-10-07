# SD-SAC scheduled pilots — 8 October 2026

Status at preparation: **scheduled, PREPARED_NOT_LAUNCHED**. No live preflight,
controller, learner, evaluation or new training run has started. Driving remains
unqualified and full training remains **BLOCKED**.

The direct human instruction authorizes further justified SD-SAC pilots from
**8 October 01:30 Europe/Warsaw** (7 October 23:30 UTC), initially monitored every
5–10 minutes and hourly once healthy. This supersedes the prior offline-only /
PAUSED / one-pilot scope for this scheduled work. Any later human STOP wins.

## First prepared pilot

- Queue: `H:/Studia/inzynierskie/inzynierkav2/AITrackmania/artifacts/tmrl-test-comparison/sd-proj08`.
- Fresh run: `tmrl-sd-sac-projected-s17`; no old checkpoint restore.
- Frozen runtime: `C:/Users/szulc/.codex/worktrees/tmrl-sd-sac-projection-runtime/AITrackmania`.
- Frozen commit: `9821c23eabfacc989869a71e7b97e99ce006deca`; never edit/pull.
- Materialized fingerprint: `ece6974ec331584446a84366ecd647ebc50911d2f7d665e7bfe7caaad51b3cc1`.
- Preparation: `preparation.json`, `plan.json`, `RESUME-AUTHORIZATION.json`,
  `source-freeze.json` (1865 immutable pins). `pending-sd-projection.json` is a
  preparation pointer, not a launch receipt.

The learning change is hyperspherical weight projection after actor/critic Adam
and before Polyak. Reward, model/GNN, replay/UTD, losses and learning settings
match the completed actorfit pilot. The runtime also carries the previously
tested scalar-tensor replay read fix and sample-weighted terminal metric
aggregation; these are separately documented, not additional loss tuning.
Offline fixed-Q gains support testing the optimizer repair; they do not prove
correct Q values or driving.

The launcher accepts its first start only between **01:30 and 01:45 Warsaw**.
It refuses early/stale starts, reused queue/run identities, changed frozen files,
new/changed STOPs, active predecessor identities and occupied controller mutexes.
The upper bound prevents a missed overnight schedule from starting unexpectedly
the next day; it does not permit extending a launched pilot.

Each launch has a fresh four-hour cap from its actual start: total target145408
transitions / training max11400 seconds, then ten greedy trials / max2100 seconds.
SAVE is actual START+13800 seconds; HARD is actual START+14400 seconds. A launch
at01:30 therefore has SAVE05:20 and HARD05:30 Warsaw. Actual receipts take
precedence over these planned times. Independent guard and stage watchdog apply.

## Scheduled launch and monitoring

Existing chat heartbeat `trackmania-nocne-piloty-i-gotowo-trening-w` is ACTIVE for
01:30 local time; no duplicate task was created. At that first wake it must
change itself to five-minute cadence and validate/launch the prepared queue.
The machine, Codex app and game must remain available; the live preflight checks
foreground, telemetry and the exact map UID rather than assuming game readiness.
Do not bypass locked-desktop, signature or security settings.

Use main `.venv/Scripts/python.exe`, with cwd and `PYTHONPATH` set to the frozen
runtime and `PYTHONNOUSERSITE=1`. Run the queue's pinned `pilot.py --validate-only`
before `pilot.py --launch`. Launch the actual process with `Start-Process
-WindowStyle Hidden`, redirecting output to new launcher logs. Preserve exact
PID+creation time. Do not propagate offline `CUDA_VISIBLE_DEVICES=-1` to this
unchanged CUDA learner configuration. Never print main `.env`.

Read actual launch/status/effective-deadline/log/errors/events/checkpoint and
evaluation receipts; `active-queue.json` is only a pointer. Persist monitor
snapshots and cadence evidence in the active queue's `monitor-state.json`.
Three consecutive healthy checks spanning at least15 minutes may reduce cadence
to60 minutes. Healthy means verified runner/guard identities, registered actor,
new ingest and increasing counters, fresh expected outputs, valid immutable
pins and no new STOP/errors; it does not mean qualified driving.

Return to five-minute checks for stage changes, stalled progress or errors.
Hourly checks are allowed only while SAVE is more than70 minutes away. Near
SAVE keep the turn active, checking at intervals no greater than60 seconds until
closure/HARD. No owned controller/learner may survive HARD. Never create a second
controller (`Global\TrackmaniaRL.ComparisonController`) or use UI during a live
learner/evaluation.

## Results and further pilots

After closure verify all observed exact PID/creation times, free mutex, immutable
source/helper/assets/prior checkpoints, final SHA/fingerprint/finite/accounting/
draining, and STOP. The existing external `sd-verify08/verify_closed.py` can write
a new proof for a normally completed queue carrying `original_checkpoint`.
Preserve old proofs, checkpoint/journal files and historical STOPs.

The first predecessor is closed `sd-fit07d`: CP33866 SHA
`a243b4f50d210d882860b74e4626ff42b369c3f1c2fd78a25fe81068d05906d7`,
145464 transitions /33866 updates /credit0, real **0/10 finishes**. Its original
and verified copy remain immutable. Previous best completed slow-SAC checkpoint
has **3/10 finishes**, also unqualified. QR29/30 is preserved and is not rerun.

A real FAIL permits offline diagnosis and a new justified bounded pilot after
full closure. It does not permit restarting this queue, extending its cap,
resuming an old checkpoint under changed code/settings, resetting old replay,
changing shared reward/model/GNN, ignoring a new STOP, or blind identical retries.
Each next attempt needs fresh run/queue identity, reviewed scope and current pins.

Gate: >=8/10 finishes, full145408, finite/fingerprint/SHA/accounted/drained,
ten complete correct-UID trials, all timing max<=100ms, no controller/telemetry
errors, and reported skips. After PASS match manual generator, fullYAML17/29/43,
guard/setup and handoff to the qualified variant; report and pause. Full training
is not scheduled by this request. Explicit STOP also closes/saves/reports/pauses.

## Preparation checks

17 schedule/scope/projection tests and19 applicable guard tests passed;
five historical actorLR-plan cases are inapplicable to this projection plan.
Ruff passed; mypy passed with missing-import/stub checking disabled for the
external queue modules and psutil boundary. Real frozen-runtime validate-only
passed. The first guard-test invocation hit an inaccessible default pytest temp
folder; an explicit owned basetemp resolved it without changing permissions.
No live preflight has been run. Automation status, saved cadence, target chat,
Warsaw timezone and absent launch/run directory were checked after scheduling.
