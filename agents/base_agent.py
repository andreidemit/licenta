"""Interfața comună pentru strategiile de navigare."""


class BaseAgent:
    name = "BaseAgent"
    requires_training = False

    def reset(self):
        """Resetează starea internă între episoade."""

    def select_action(self, observation):
        raise NotImplementedError

    def learn(self, transition):
        """Agenții non-learning pot ignora tranzițiile."""

    def explain(self) -> str:
        return "Interfață comună pentru agenții rulați de simulator."
