"""Loss-scale comparisons cannot replace the categorical gradient or optimum."""

import torch

from experiments.tmrl_test_comparison.probe_sd_sac_actor_plasticity import policy_loss
from trackmaniarl.algorithms.sd_sac_objectives import soft_q_log_probabilities


def test_temperature_cannot_reverse_the_fixed_q_greedy_preference() -> None:
    q = torch.tensor([[10.22286, 10.25556, 10.1]])
    for alpha in (0.1, 0.01, 0.001):
        logs = soft_q_log_probabilities(q, torch.tensor(alpha))
        assert logs.argmax(1).item() == 1
    logs = soft_q_log_probabilities(q, torch.tensor(0.01))
    assert 26 < float((logs[0, 1] - logs[0, 0]).exp()) < 27


def test_state_baseline_preserves_sac_actor_gradient() -> None:
    logits = torch.tensor([[0.3, -0.2, 0.7]], requires_grad=True)
    logs = logits.log_softmax(1)
    q = torch.tensor([[10.22, 10.26, 10.1]])
    centered = policy_loss(logs, q, 0.01, "sac")
    expected = (logs.exp() * (0.01 * logs - q)).sum(1).mean()
    first = torch.autograd.grad(centered, logits, retain_graph=True)[0]
    second = torch.autograd.grad(expected, logits)[0]
    assert torch.allclose(first, second, atol=1e-6)


def test_forward_loss_still_moves_probability_toward_missed_best_action() -> None:
    logits = torch.tensor([[2.0, 0.0, 1.0]], requires_grad=True)
    q = torch.tensor([[0.0, 0.1, -0.1]])
    loss = policy_loss(logits.log_softmax(1), q, 0.01, "forward")
    gradient = torch.autograd.grad(loss, logits)[0]
    assert gradient[0, 1] < 0
