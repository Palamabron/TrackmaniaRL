> **RETIRED / EXPERIMENTAL — 2026-10-08.** Human decision supersedes the active
> repair loop below. Scheduler PAUSED; no pending automatic experiment. This
> document preserves the diagnosis/proposal, not launch authorization. See
> [the Fable 5.1 report](SD_SAC_FABLE_5_1_REPORT.md) and
> [the current campaign](MULTI_COMPUTER_TRAINING.md), which excludes SD-SAC.

# SD-SAC repair decisions

Updated 2026-10-08 07:22 UTC. Human instruction: make the complete repair search more efficient. This ledger is the entry point; READINESS/HANDOFF retain full evidence history. Latest actual files/process identities override historical snapshots.

## Working rule

Every new experiment must name the hypothesis, the decision it can change, the existing evidence it adds to, a fixed compute/step budget, matched controls and a stop/rejection condition before launch. Reuse existing results and whole-episode partitions. Batch complementary measurements in one checkpoint load. No broad grids, repeated failed endpoints, isolated gradient audits without a pending decision, or promotion from fitting metrics. Run at most one owned offline computation at a time. Finish closure and verification before any next run. Scheduler wakeups continue the decision, not generate new audits just because time passed.

## Decisions already closed

| Hypothesis | Evidence | Decision |
| --- | --- | --- |
| Faster actor tracking fixes driving | Real fast-actor pilot0/10 vs predecessor2/10; different runs | Reject repeating faster-actor pilot; no causal precision claim |
| Actor cannot represent start actions | Start-only copies fit held starts; mixed objectives fail general/start guards | Capacity not established; stop actor-loss/temperature/margin grids |
| Terminal reward outside critic output range | Head geometry bounds contain terminal rewards | No output-range/architecture fix supported |
| Exact current-observation terminal alias in saved replay | All current observations hashed in both snapshots, no cross-label exact aliases | No exact-alias evidence; nearest distances are descriptive only |
| Timeout should bootstrap | Intentional penalized race deadline; focused tests pass | Do not relabel terminal/truncation or change task |
| Initial terminal/nonterminal gradient conflict | Globally positive raw/tangent alignment | Does not explain finite drift; no new gradient variations |
| Initial Adam momentum reverses improvement | All15 analytic directions improve held MSE/MAE locally | No reset justified; close initial-direction audits |
| Existing terminal weights are runtime fixes | All nonzero tested weights fail held nonterminal guard | Reject their promotion; no blind weight search |

## Completed decision: finite calibration drift

One trajectory diagnostic, not a new candidate: existing weight0 and0.01, saved Adam, projected copied critics, same frozen targets/actor/alpha/sampling/episode split. Seeds17/29 x48steps =192 total, fixed300s computation cap. Trace0/1/4/8/16/32/48. A single evaluation collects fit/held MAE, squared error, actual clipped Bellman loss and held terminal reason errors. Endpoints must reproduce projected-calibration.json within1e-6; otherwise investigate instrumentation and do not interpret candidate gains. CPU idle1thread, original checkpoint/model/target/all optimizers/source/replay immutable. Output BASE/sd-projlr08-audit/calibration-trajectory.json; actual captured identities in calibration-trajectory-processes.json. Do not restart, extend or select an early checkpoint for promotion.

Decision after completion:
1. If fitting loss improves while held errors worsen, report generalization/interference rather than an optimizer bug. Close generic optimizer tweaking unless a specific counterfactual is justified.
2. If MAE worsens while held squared/clipped losses improve, document the metric tradeoff; keep the MAE guard, do not waive it.
3. If both held objectives worsen after initially improving, only a demonstrated mechanism (for example clipping versus un-clipped behavior) warrants one fixed matched counterfactual; no automatic learning-rate/weight/step grid.
4. If there is no supported optimization repair, produce a concrete observation/termination-history proposal using the known clock-shift information loss and absent explicit progress counters. Specify which causal pre-action values are needed and compatibility/scope consequences. Endpoint logs are post-action and cannot become current inputs. Missing explicit signals alone do not prove driving causality. Shared feature/model/reward/GNN/replay changes remain outside current authorization; present the finished proposal before asking to widen that scope.

## Runtime decision

A CPU result must justify one fresh bounded pilot and pass existing scope/held guards; it is not driving evidence. No used queue restart/resume or identical failed runtime pilot. Real evaluation gate remains >=8/10 finishes plus completeness/identity/timing/closure checks. Full SD remains BLOCKED; no automatic full launch. STOP always wins.

## Operating efficiency

Maintain this ledger and compact machine-readable repair-state.json as the current state. Preserve evidence files, do not overwrite them. Update the seven historical documents with concise links/outcomes at decision boundaries, not one repeated narrative for every small check. Keep the existing heartbeat every5min and shorten its instructions to current decision plus durable constraints; retrieve detailed history only when a specific decision requires it. Notify only meaningful result/completion/failure/intervention.

## Outcome and current decision

Trajectory COMPLETE212.36s/192 copied steps, both exact processes closed, original CP/model/target/all optimizers unchanged, pins/STOP valid. All four final MAE endpoints reproduce prior results exactly (maximum error0). Baselines never cross the held MAE guard at traced steps. Both weight0.01 seeds first cross at sampled step8: held MAE0.109539/0.100690 versus initial0.071385 and limit0.085662. At48 it is0.113856/0.115229. Held MSE0.095405/0.090436 versus initial0.033756; fit MSE0.080726/0.059229 versus initial0.027232; held clipped loss also worsens. Terminal MAE improves to4.550828/4.597501 from5.016299.

This is a finite tradeoff affecting fitting and held nonterminal states, not just a held-MAE-versus-squared-loss discrepancy or ordinary train-only overfitting. Initial analytic gradients/Adam directions were locally benign, but their signs did not predict finite dynamics. No specific clipping bug/reset fix is established; do not infer one from this trace. Close the current terminal-weighting/initial-optimizer branch. No new grid, early checkpoint selection, pilot or architecture edit.

Prepared next proposal: SD_SAC_OBSERVABILITY_PROPOSAL.md, a causal remaining-clock input in an SD-SAC-only adapter versus identical constant-clock adapter control. Current no-observation/model/architecture-change constraint requires human scope authorization before implementation. While pending, do not substitute another unrelated audit, model update or runtime experiment. Scheduler remains ACTIVE5min, quiet when nothing actionable changes; no automatic PAUSED status without user instruction.
