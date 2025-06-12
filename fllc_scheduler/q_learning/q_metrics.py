"""Module for tracking Q-learning metrics and results."""

from collections import defaultdict
from dataclasses import dataclass, field

from ..schedule_evaluator import ScheduleEvaluator
from ..utils.stat_utils import average
from .q_state import ScheduleState


@dataclass(slots=True)
class QLearningMetrics:
    """Tracks historical metrics and results across all training episodes."""

    episode_rewards: list[float] = field(default_factory=list)
    avg_rewards: list[float] = field(default_factory=list)
    q_value_changes: list[float] = field(default_factory=list)
    avg_reward_changes: list[float] = field(default_factory=list)
    scores: defaultdict[str, list[float]] = field(default_factory=lambda: defaultdict(list))
    completion_percentage: defaultdict[str, list[float]] = field(default_factory=lambda: defaultdict(list))

    def update_metrics(self, episode_reward: float) -> None:
        """Update the metrics with the latest episode rewards and average rewards."""
        self.episode_rewards.append(episode_reward)
        self.avg_rewards.append(average(self.episode_rewards))

        ep_rewards = self.episode_rewards
        q_value_change = abs(ep_rewards[-1] - ep_rewards[-2]) if len(ep_rewards) > 1 else 0
        self.q_value_changes.append(q_value_change)

        avg_change = average(self.q_value_changes) if len(self.q_value_changes) > 1 else 0
        self.avg_reward_changes.append(avg_change)

    def evaluate_schedule(self, schedule: list[ScheduleState], completed_percentage: float, roundtype: str) -> None:
        """
        Update the metrics with the completion percentage and score for the training episode.

        Args:
            schedule (list[ScheduleState]): The schedule to evaluate, where each entry is a ScheduleState.
            completed_percentage (float): The percentage of the schedule that has been completed.
            training (str): The training label (e.g., "Training" or "Validation").
        """
        se = ScheduleEvaluator(schedule)
        schedule_score = se.calculate_schedule_score(completed_percentage)
        se.generate_aggregate_statistics(roundtype)

        self.completion_percentage[roundtype].append(completed_percentage)
        self.scores[roundtype].append(schedule_score)
