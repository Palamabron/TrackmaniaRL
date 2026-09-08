"""Unified discrete value learning."""

from trackmaniarl.algorithms.value_based.learner import DiscreteValueLearner
from trackmaniarl.algorithms.value_based.objectives import (
    DemonstrationCrossEntropyObjective,
    DemonstrationMarginObjective,
    DemonstrationProgressWindowCrossEntropyObjective,
    PolicyAnchorObjective,
)

__all__ = [
    "DemonstrationCrossEntropyObjective",
    "DemonstrationMarginObjective",
    "DemonstrationProgressWindowCrossEntropyObjective",
    "DiscreteValueLearner",
    "PolicyAnchorObjective",
]
