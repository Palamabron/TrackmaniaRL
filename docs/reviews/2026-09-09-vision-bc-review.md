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

### Sensor composability review

- Actors unpacked mapping and tuple observations while critics and composite
  models passed them as one argument. The same lidar encoder consequently worked
  in a critic but raised TypeError in both actor types. All now use the one-argument
  observation contract, including PPO. Tests use the real lidar encoder.
- Gaussian action bounds accepted NaN/Inf and float32 overflow. Construction now
  rejects unusable bounds before creating action scale and bias buffers.
- PPO initialization assumed all custom linear encoders had bias tensors. Biasless
  layers now initialize correctly and have a regression test.
- Gymnasium dictionary collation required insertion order to match the space.
  It now validates key sets and emits fields in the declared space order.
- A configurable actor-critic factory and a lidar/image fusion encoder now support
  all nine RL families. Generated lidar and paired configurations have integration
  coverage for updates, nonzero sensor gradients, training and checkpoint resume.
  The paired pipeline forwards evaluation-map changes to lidar geometry and resets
  camera history. Encoders are independently constructed for actor and critics.
- Paired BC archives now carry aligned 33-field telemetry alongside RGB and actions.
  The shared BC model trains both sensor branches, restores exact continuation and
  evaluates with paired observations. Tests verify modality matching, timestamps,
  control masking and consistent reflection of both sensors.

### Release verification

Independent GitHub CI on Windows and Ubuntu verifies the source test suite,
formatting, strict type checks and distribution build. Machine-specific diagnostic
scripts and reports are not part of the release.

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
