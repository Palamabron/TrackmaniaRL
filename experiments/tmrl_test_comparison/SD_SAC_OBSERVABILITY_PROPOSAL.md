# Scoped SD-SAC observability proposal

Prepared 2026-10-08 from clock-semantics and terminal-history evidence. Proposal only; no shared observation/model/reward/GNN/replay code changed. This is a candidate next hypothesis if the calibration trajectory closes generic optimizer tuning, not an established cause of failed driving.

## Problem and smallest discriminating change

The configured150s race deadline is an intentional penalized terminal, while frozen V5 transforms synthetic identical-motion histories at different race-clock offsets into identical tensors. Reward no-progress age and rolling-progress state are also absent explicitly. Existing replay does not retain causal pre-action counters, so historical endpoint logs cannot safely reconstruct current inputs. Exact terminal/nonterminal aliases were not observed in existing replay.

First proposed intervention would expose only normalized remaining race time to an SD-SAC-specific observation/model adapter, keeping reward/termination rules, actions, base GNN and all optimization settings fixed. This tests the one information-loss mechanism already demonstrated by a controlled pipeline input. Do not combine it initially with no-progress counters or a recurrent architecture; those would confound the result. Scope needs explicit human authorization because current instructions forbid observation/model architecture changes.

Causality contract: clock is taken from the telemetry underlying s_t, before a_t. Store the same scalar with current observation and the new scalar with next observation; never compute s_t features from endpoint termination or future data. Reset state at each actual reset; include validity for missing telemetry rather than substituting future clock. Freeze normalization against configured deadline, with finite/bounds checks. No clock perturbation may alter reward or termination. Missing-time policy and tensor dimensions must be specified in the new fingerprint; old checkpoints/replay remain immutable and incompatible shapes fail explicitly, never override fingerprints.

For a later separate progress-history hypothesis, source values must be a read-only snapshot of the reward state already accumulated before the action: _step-_last_progress_step, _window_progress_m, and window fill/age. Source reward_step.py updates these during scoring. Export at the observation boundary after processing the previous transition and before choosing the next action. A rolling aggregate does not fully specify future queue expiration; do not claim a fully Markov state from these summaries. A public snapshot API and exact reset/timing tests would be needed; no direct mutation of reward internals.

## Implementation and validation contract, after authorization

Use a new SD-SAC-only component/config in the editable worktree and a new pinned runtime. Preserve the shared feature pipeline/GNN and all prior artifacts. Actor and both online/target critics must receive the same causal clock field; merely adding replay info without model input does not test observability. Document the adapter parameter initialization and control capacity; compare an identical adapter supplied a constant clock against the real clock to separate information from extra parameters. This introduces a model-specific component and therefore cannot be done under the present no-architecture-edit constraint.

Before any game run: deterministic causal clock boundary/reset/terminal-vs-truncation controls; source/fingerprint/scope validation; synthetic equal-motion clock-shift inputs must now differ only in the clock branch. Check no endpoint/future leakage. Do not use the existing replay for a feature-conditioned fit unless causal current/next clocks can be independently verified from preserved source data. Absence means new collection is required, not guessed labels or replay rewriting.

Only then propose fresh bounded runtime controls with the existing safety caps, closure and real driving gate. Baseline optimization is held fixed; do not restore the failed faster actor or add terminal weighting at the same time. Report time-limit and progress-related outcomes separately; a better offline target fit is not qualification. No automatic full launch.

## Decision requested only if optimization branch closes

Authorize the SD-SAC-specific causal clock observation/model-adapter experiment, including a separate new pinned runtime/config/fingerprint; keep reward, termination and shared GNN unchanged. Otherwise retain current scope and explicitly report that this hypothesis cannot be tested within it. Do not run another generic optimizer grid as a substitute for the missing authorization.
