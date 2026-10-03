"""Recoverable observation interruptions, distinct from transport failures."""


class EnvironmentPausedError(RuntimeError):
    """Collection must wait for external readiness and reset before continuing."""
