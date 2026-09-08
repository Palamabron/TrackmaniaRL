"""Static release-content manifest used by the archive validator."""

from __future__ import annotations

DIAGRAM_STEMS = (
    "checkpoint-resume",
    "demonstration-timing",
    "distributed-security",
    "imitation-learning",
    "model-composition",
    "replay-sequence",
    "reward-decomposition",
    "runtime-architecture",
    "trackmania-integration",
)
DIAGRAM_SUFFIXES = (
    ".spec.json",
    ".excalidraw",
    "-preview.png",
    "-preview.svg",
    "-preview.html",
)
SDIST_REQUIRED_PATHS = frozenset(
    {
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "docs/assets/v108-neighbors-best.gif",
        "docs/reward-function.md",
        "docs/recording.md",
        "examples/own-map.yaml",
        "experiments/sub37/runner.py",
        "docs/assets/trackmaniarl-logo.png",
        "docs/diagrams/render.py",
        "LICENSE",
        "NOTICE",
        "README.md",
        "SECURITY.md",
        "pyproject.toml",
        "readme/development.md",
        "readme/trackmania.md",
        "scripts/distribution_manifest.py",
        "scripts/fetch_analysis.py",
        "scripts/iteration_report.py",
        "scripts/verify_soak.py",
        "tests/unit/test_release_distribution.py",
        "tests/unit/test_verify_soak.py",
        "tests/unit/core/test_run_spec_serialization.py",
        "trackmaniarl/py.typed",
        "trackmaniarl/project/scaffold.py",
        "trackmaniarl/project/scaffold_run_templates.py",
        "trackmaniarl/project/scaffold_templates.py",
    }
)
