# Vision and BC integration review for 1.2.7

## Scope

Reviewed the shared model contracts, RL camera factories, generated configurations,
BC dataset loading and splitting, optimizer/checkpoint lifecycle, evaluation reset
and cleanup, BC-to-RL transfer, documentation links and distribution inclusion.
The full repository test suite and static checks supplement this source review.
This is not a claim of exhaustive formal verification of every library module.

## Findings fixed

- BC internals were typed and implemented around lidar models. A shared abstract
  `BehaviorCloningModel` contract now supports lidar and CNN policies through the
  same learner, metrics, action selection and checkpoint code.
- Existing BC-to-RL documentation described a transfer that the warm-start loader
  could not read. It now accepts selected BC policy checkpoints and extracts only
  encoder and temporal tensors. Tests cover lidar and camera sources and ensure
  the RL head and strategy remain unchanged.
- Warm-start validation could reject required tensors after mutating the target.
  Matching and validation now use cloned tensors before committing the state.
  Regression tests compare every target tensor after an unsuccessful transfer.
- Copied camera episodes could contaminate both sides of a dataset split.
  Loading rejects duplicate image/action sequences regardless of filenames,
  integer action storage dtype or changed timestamps. Splitting precedes reflection.
- Telemetry action-lead and aggregation settings would have been ignored by the
  camera archive path. Camera BC now rejects them and the generated configuration
  explicitly disables aggregation.
- Failed archive writes could leave partial files discoverable as demonstrations.
  The writer creates files exclusively and removes its own incomplete output on
  failure. It preserves pre-existing destinations.

## Follow-up findings fixed

- BC checkpoint restoration could partially replace model, optimizer or RNG state
  before encountering a later error. Restoration now rolls back all captured
  components on failure. Tests inject failures in model keys, optimizer groups
  and RNG state and compare the complete pre-failure state.
- BC restore and named warm starts accepted NaN/Inf tensors. They now reject
  non-finite weights and, for BC restore, non-finite optimizer tensors before use.
- Recovery metadata accepted boolean timing fields and fractional action repeat
  counts through the Python API. Contracts now validate their types explicitly.
- Recovery loading converted fractional labels and student actions into integers
  and arbitrary numeric flags into booleans. It now checks stored dtypes before
  conversion. The writer also rejects fractional labels. Even all-unknown student
  metadata must have exactly one entry per frame.

## Follow-up verification

Integration tests exercise generated camera configurations, image gradients,
training and checkpoint continuation across RL families. BC tests drive the real
CLI with synthetic RGB archives through validation, training, a mid-run resume
and checkpoint evaluation. Resumed model tensors match uninterrupted training
exactly. Tests also cover previous-action conditioning, mirrored action labels,
episode history reset, archive shape/range/timing validation and incompatible data.

Evaluation resets policy and feature history between trials and closes the image
environment. Existing lidar BC, recovery and DAgger regression tests remain part
of the full suite. Distribution checks verify packaged code and documentation.

Camera BC requires aligned RGB/action episodes supplied through its archive API.
The telemetry recorder does not create RGB frames. Existing telemetry DAgger and
recovery datasets are not camera data. BC materializes preprocessed stacks in RAM.
These constraints are documented in the camera BC guide. No live camera racing
performance or hardware capture synchronization is established by synthetic tests.
