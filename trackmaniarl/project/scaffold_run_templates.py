from __future__ import annotations

import yaml

_STARTER_CONFIG = """api_version: "2.0"
run_id: starter
seed: 0
artifacts_dir: artifacts
components:
  learner: {{class_path: {package}.components:StarterMlpLearner}}
  environment: {{class_path: {package}.components:StarterEnvironmentFactory}}
  replay_store:
    class_path: trackmaniarl.core.replay:InMemoryReplayStore
    kwargs: {{capacity: 10000}}
  sampler: {{class_path: trackmaniarl.core.replay:UniformSampler, kwargs: {{seed: 0}}}}
  feature_pipeline: {{class_path: {package}.components:StarterFeaturePipeline}}
  logger: {{class_path: trackmaniarl.core.builtins:JsonlRunLogger}}
  checkpoint_codec: {{class_path: trackmaniarl.core.builtins:TorchCheckpointCodec}}
training:
  total_transitions: 64
  max_episode_steps: 16
  batch_size: 8
  n_step: 1
  gamma: 0.99
  warmup_transitions: 8
  updates_per_transition: 1.0
  checkpoint_interval_updates: 16
"""


def _config(package: str) -> str:
    return _STARTER_CONFIG.format(package=package)


_TRACKMANIA_CONFIG = """api_version: "2.0"
run_id: trackmania-iqn-lidar-v1
seed: 0
artifacts_dir: artifacts
components:
  learner:
    class_path: trackmaniarl.algorithms.value_based:DiscreteValueLearner
    kwargs:
      learning_rate: 3.0e-5
      gradient_clip_norm: 1.0
      target_update_interval: 5000
      exploration_epsilon: 1.0
      action_selector:
        class_path: trackmaniarl.trackmania.actions:TrackmaniaActionSelector
      execution:
        device: auto
        precision: auto
  environment:
    class_path: trackmaniarl.trackmania.environment:OpenPlanetEnvironmentFactory
    kwargs:
      config:
        geometry_path: assets/my-map.geometry.npz
        expected_map_uid: REPLACE_WITH_YOUR_MAP_UID
        control_backend: gamepad
        confirm_finish_before_reset: false
        action_repeat_frames: 1
        decision_interval_ms: 50.0
        demonstration_control_aggregation: true
        slow_progress_window_steps: 300
        no_progress_steps: 600
        minimum_progress_per_window_m: 0.5
  model_factory:
    class_path: trackmaniarl.models.factory:CompositeValueModelFactory
    kwargs:
      encoder:
        class_path: trackmaniarl.trackmania.encoders:LidarSensorEncoder
        kwargs:
          config:
            output_dim: 256
      temporal:
        class_path: trackmaniarl.models.temporal:IdentityTemporalCore
        kwargs:
          input_dim: 256
      head:
        class_path: trackmaniarl.models.heads:ImplicitQuantileHead
        kwargs:
          config:
            feature_dim: 256
            action_count: 78
            cosine_count: 64
            dueling: true
      strategy:
        class_path: trackmaniarl.models.strategies:RandomQuantileStrategy
        kwargs:
          train_quantile_count: 32
          target_quantile_count: 32
          evaluation_quantile_count: 32
  replay_store:
    class_path: trackmaniarl.core.replay:InMemoryReplayStore
  sampler:
    class_path: trackmaniarl.core.replay:PrioritizedSampler
  feature_pipeline:
    class_path: trackmaniarl.trackmania.features:LidarFeaturePipeline
    kwargs:
      config:
        geometry_path: assets/my-map.geometry.npz
        expected_map_uid: REPLACE_WITH_YOUR_MAP_UID
  evaluator:
    class_path: trackmaniarl.trackmania.evaluation:TrackmaniaEvaluator
evaluation:
  name: my-map
  version: "1"
  maps:
    - id: my-map
      map_path: maps/my-map.Map.Gbx
      geometry_path: assets/my-map.geometry.npz
      expected_map_uid: REPLACE_WITH_YOUR_MAP_UID
  trials_per_map: 20
  min_finish_rate: 1.0
distributed:
  epsilon_profiles: [1.0]
  epsilon_start: 0.5
  epsilon_final: 0.05
  epsilon_decay_transitions: 1500000
training:
  total_transitions: 2000000
  batch_size: 512
  n_step: 3
  gamma: 0.995
  beta: 0.4
  per_beta_final: 1.0
  per_beta_anneal_transitions: 2000000
  warmup_transitions: 20000
  updates_per_transition: 0.25
  checkpoint_interval_updates: 5000
  metrics_interval_updates: 50
"""


def _trackmania_config() -> str:
    return _TRACKMANIA_CONFIG


def _trackmania_ppo_config(*, vision: bool = False) -> str:
    config = yaml.safe_load(_TRACKMANIA_CONFIG)
    config["run_id"] = "trackmania-ppo-vision" if vision else "trackmania-ppo-telemetry"
    config.pop("distributed")
    components = config["components"]
    components["learner"] = {
        "class_path": "trackmaniarl.algorithms:ProximalPolicyOptimization",
        "kwargs": {
            "learning_rate": 3e-4,
            "update_epochs": 10,
            "minibatch_size": 64,
            "normalize_observations": not vision,
            "execution": {"device": "auto", "precision": "float32"},
        },
    }
    components["model_factory"] = {
        "class_path": "trackmaniarl.trackmania.vision_models:VisionPpoModelFactory"
        if vision
        else "trackmaniarl.trackmania.baseline:TelemetryPpoModelFactory"
    }
    components["feature_pipeline"] = {
        "class_path": "trackmaniarl.trackmania.vision:VisionFeaturePipeline"
        if vision
        else "trackmaniarl.trackmania.features:TelemetryFeaturePipeline"
    }
    components["sampler"] = {"class_path": "trackmaniarl.core.replay:OnPolicySequenceSampler"}
    components["replay_store"]["kwargs"] = {"capacity": 2048}
    if vision:
        components["environment"]["class_path"] = (
            "trackmaniarl.trackmania.vision_environment:VisionEnvironmentFactory"
        )
        components["environment"]["kwargs"]["capture"] = {
            "left": 0,
            "top": 0,
            "width": 1280,
            "height": 720,
        }
    config["training"] = {
        "total_transitions": 2048000,
        "sequence_length": 2048,
        "batch_size": 1,
        "n_step": 1,
        "gamma": 0.995,
        "max_episode_steps": 4000,
        "checkpoint_interval_updates": 10,
    }
    return yaml.safe_dump(config, sort_keys=False)


def _trackmania_actor_critic_config(algorithm: str) -> str:
    choices = {
        "sac": ("SoftActorCritic", "actor_critic:TelemetrySacModelFactory"),
        "redq": ("RandomizedEnsembleSAC", "actor_critic:TelemetryRedqModelFactory"),
        "tqc": ("TruncatedQuantileCritic", "baseline:TelemetryTqcModelFactory"),
        "discrete-sac": (
            "StableDiscreteSoftActorCritic",
            "actor_critic:TelemetryDiscreteSacModelFactory",
        ),
    }
    if algorithm not in choices:
        raise ValueError(f"unknown actor-critic algorithm: {algorithm}")
    learner, model = choices[algorithm]
    config = yaml.safe_load(_TRACKMANIA_CONFIG)
    config["run_id"] = f"trackmania-{algorithm}-telemetry"
    config.pop("distributed")
    components = config["components"]
    components["learner"] = {
        "class_path": f"trackmaniarl.algorithms:{learner}",
        "kwargs": {"execution": {"device": "auto", "precision": "float32"}},
    }
    components["model_factory"] = {"class_path": f"trackmaniarl.trackmania.{model}"}
    components["feature_pipeline"] = {
        "class_path": "trackmaniarl.trackmania.features:TelemetryFeaturePipeline"
    }
    config["training"]["batch_size"] = 256
    config["training"]["sequence_length"] = 1
    return yaml.safe_dump(config, sort_keys=False)
