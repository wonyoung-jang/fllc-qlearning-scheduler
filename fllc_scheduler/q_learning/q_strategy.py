"""Q-Learning strategy and parameters for reinforcement learning."""

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class QLearningParameters:
    """Dataclass for Q-Learning parameters."""

    alpha: float = 0.20  # Learning rate
    gamma: float = 0.80  # Discount factor
    epsilon_start: float = 1.00
    epsilon_end: float = 0.01
    epsilon_decay: float = 0.995
    epsilon: float = 1.00

    def update_epsilon(self) -> None:
        """
        Get the current epsilon value for exploration-exploitation trade-off.
        """
        self.epsilon = max(self.epsilon_end, self.epsilon_decay * self.epsilon)

    def get_new_q(self, reward: float, current_q: float, max_future_q: float) -> float:
        """
        Calculate the new Q-value using the Q-learning formula.

        Args:
            reward (float): The reward received for the action taken.
            current_q (float): The current Q-value for the state-action pair.
            max_future_q (float): The maximum Q-value for the next state.
        Returns:
            float: The updated Q-value for the state-action pair.
        """
        return (1 - self.alpha) * current_q + self.alpha * (reward + self.gamma * max_future_q)

    def update_from_settings(self, settings: dict[str, Any]) -> None:
        """Update the Q-Learning parameters from a settings dictionary."""
        self.alpha = settings.get("alpha")
        self.gamma = settings.get("gamma")
        self.epsilon_start = settings.get("epsilon_start")
        self.epsilon_end = settings.get("epsilon_end")
        self.epsilon_decay = settings.get("epsilon_decay")


@dataclass(slots=True)
class QLearningStrategy:
    """Dataclass for Q-Learning strategy parameters."""

    exploitation_count: int = 0
    exploitation_counts: list = field(default_factory=list)
    exploration_count: int = 0
    exploration_counts: list = field(default_factory=list)

    def reset(self) -> None:
        """Reset the exploration and exploitation counts to zero."""
        self.exploitation_count = 0
        self.exploration_count = 0

    def update(self) -> None:
        """Update the exploration and exploitation counts."""
        self.exploration_counts.append(self.exploration_count)
        self.exploitation_counts.append(self.exploitation_count)
