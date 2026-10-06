## 2026-10-06 — no-movement diagnosis and offline corrective variant

After “no to ogarnij to”, audited the preserved CP33866 in exact frozen e50b0b02,
CPU only, no controller or learner updates. Across128 recorded starts actor argmax
was always action24=[gas0,brake0,steer-1/3], maxprob0.03947, entropy4.16891;
critic preferred56, agreement0%. This explains why this greedy policy can remain
stationary; the old evaluation did not persist issued commands, so actual backend
execution cannot be reconstructed. It was still a valid driving FAIL0/10.

All137 replay terminal states had mean Q12.368 vs reward-2.046, MAE14.414;
terminal fraction0.09418%, clipped loss blocked9.489% of terminal gradients.
Added explicit optional terminal_value_loss_coefficient (default0 preserves SD-SAC)
to anchor selected true-terminal actions directly to known rewards, normalized
within terminal samples, without bootstrap or clipping. Truncations excluded;
importance weights honored; checkpoint options prohibit changing this objective
on resume. It is an experimental critic objective, NOT a proven driving fix.
Added terminal TD error sum/count diagnostics and issued-control histogram,
measurement completeness and gas mean in future evaluation artifacts. Missing
commands are unknown, not zero gas; commands do not prove game acknowledgement.

Offline independent critic copies,200 CPU regression steps, fixed old bootstrap:
coefficient0 terminalMAE13.921/nonterminalTDMAE0.138;
coefficient1 terminalMAE3.009/nonterminalTDMAE1.995. This tradeoff must remain visible.
Head-only300step probe improved terminalMAE14.105 to13.992 only. Training-data
calibration and frozen targets cannot establish ranking, policy quality or driving.
113 CPU tests, Ruff and mypy passed. No saved model, reward, replay or frozen source
was edited; no game test, evaluation or new pilot launched. Evidence in
BASE/sd-sac-stability-no-movement-audit-20261006. FullSD BLOCKED; automation stays
PAUSED. Fresh training/test requires a new direct human instruction.


The checkpoint remains SHA1428c80edfc05f5b341040aa39e6d051893b8c32d3b2648a667c048f5a94cb73.
Recent31 complete training episodes separately show terminal Q18.015 vs reward-2.049;
these recent-state figures differ from the137-state all-terminal aggregate above.
Full-episode historical soft returns are behavior-policy proxies, not on-policy truth.
Terminal immediate rewards require no behavior-policy assumption.

Artifacts: inspect_saved_policy.py/recorded-return-calibration.json,
inspect_terminal_gradient.py/terminal-gradient-audit.json,
probe_terminal_heads.py/terminal-head-probe.json,
probe_terminal_critics.py/terminal-critic-probe.json. No probe saves model weights.
The current failed checkpoint will not be resumed under this changed objective.
The optional coefficient1 is a diagnostic candidate, not an automatically enabled
configuration or a qualified monthly/three-seed run. Do not mask failures by forcing
gas, changing greedy evaluation to stochastic, removing no-gas actions or modifying
the shared reward. The observed actor/Q mismatch and nonterminal tradeoff remain
unresolved until a separately authorized fresh bounded pilot and actual driving gate.
