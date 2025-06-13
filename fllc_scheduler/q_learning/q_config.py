"""Configuration settings for Q-Learning training runs."""

from dataclasses import dataclass, field
from typing import Any, Literal

from ..config import Constraint, QParam
from ..schedule_data import Team
from ..utils.stat_utils import normalize
from ..utils.time_utils import time_to_minutes


@dataclass(slots=True)
class TrainingConfig:
    """Configuration settings for a Q-Learning training run."""

    episodes: int = 5
    max_num_rounds: int = 0
    constraint_weights: dict[Constraint, float] = field(
        default_factory=lambda: {
            Constraint.TABLE_CONSISTENCY: 1.0,
            Constraint.OPP_VARIETY: 1.0,
            Constraint.BTB_PENALTY: 1.0,
            Constraint.BREAK_TIME: 1.0,
        }
    )

    def calc_reward(self, team: Team, time_slot: tuple[str, str], max_num_rounds: int) -> float:
        """
        Calculate the reward for a team based on the scheduled times and constraints.

        Args:
            team (Team): The team for which the reward is being calculated.
            time_slot (tuple[str, str]): The time slot for the current state.
            max_num_rounds (int): The maximum number of rounds in the tournament.
        Returns:
            float: The calculated reward for the team.
        """
        self.max_num_rounds = max_num_rounds
        scheduled_times = list(team.yield_time_slots())
        reward = 0
        reward += self.calc_table_consistency(list(team.yield_tables()))
        reward += self.calc_opponent_variety(list(team.yield_opponents()))
        reward += self.calc_back_to_back_penalty(scheduled_times, time_slot)
        reward += self.calc_break_time(scheduled_times, time_slot)
        return reward

    def calc_table_consistency(self, scheduled_tables: list) -> float | Literal[0]:
        """
        Calculate the table consistency reward based on the scheduled tables.

        Args:
            scheduled_tables (list): A list of scheduled tables for a team.
        Returns:
            float | Literal[0]: The calculated table consistency reward, or 0 if no tables are scheduled.
        """
        len_tables = len(scheduled_tables)
        if len_tables > 1:
            unique_to_tables = len(set(scheduled_tables)) / len_tables
            reward_table = unique_to_tables * self.max_num_rounds
            reward_table = normalize(reward_table, 0, 1)
            return reward_table * self.constraint_weights[Constraint.TABLE_CONSISTENCY]
        return 0

    def calc_opponent_variety(self, scheduled_opponents: list) -> float | Literal[0]:
        """
        Calculate the opponent variety reward based on the scheduled opponents.

        Args:
            scheduled_opponents (list): A list of scheduled opponents for a team.
        Returns:
            float | Literal[0]: The calculated opponent variety reward, or 0 if no opponents are scheduled.
        """
        len_opps = len(scheduled_opponents)
        if len_opps > 1:
            unique_to_opponents = len(set(scheduled_opponents)) / len_opps
            reward_opponent = unique_to_opponents * self.max_num_rounds
            reward_opponent = normalize(reward_opponent, 0, 1)
            return reward_opponent * self.constraint_weights[Constraint.OPP_VARIETY]
        return 0

    def calc_back_to_back_penalty(self, scheduled_times: list, time_slot: tuple[str, str]) -> float | Literal[0]:
        """
        Calculate the back-to-back penalty based on the scheduled times.

        Args:
            scheduled_times (list): A list of scheduled times for a team.
            time_slot (tuple[str, str]): The time slot for the current state.
        Returns:
            float | Literal[0]: The calculated back-to-back penalty, or 0 if no times are scheduled.
        """
        state_start = time_to_minutes(time_slot[0])
        state_end = time_to_minutes(time_slot[1])
        btb_weight = self.constraint_weights[Constraint.BTB_PENALTY]
        reward = 0
        for scheduled_time in scheduled_times:
            action_start = time_to_minutes(scheduled_time[0])
            action_end = time_to_minutes(scheduled_time[1])

            reward_back_to_back = 0

            if (action_start - state_end) <= 0:
                reward_back_to_back -= 1
            elif (action_end - state_start) <= 0:
                reward_back_to_back -= 1
            else:
                reward_back_to_back += 1

            if (state_start - action_end) <= 0:
                reward_back_to_back -= 1
            elif (state_end - action_start) <= 0:
                reward_back_to_back -= 1
            else:
                reward_back_to_back += 1

            reward_back_to_back_normalized = normalize(reward_back_to_back, -1, 1)

            reward += reward_back_to_back_normalized * btb_weight

        return reward

    def calc_break_time(self, scheduled_times: list, time_slot: tuple[str, str]) -> float:
        """
        Calculate the break time reward based on the scheduled times.

        Args:
            scheduled_times (list): A list of scheduled times for a team.
            time_slot (tuple[str, str]): The time slot for the current state.
        Returns:
            float: The calculated break time reward.
        """
        state_start = time_to_minutes(time_slot[0])
        state_end = time_to_minutes(time_slot[1])
        break_time_weight = self.constraint_weights[Constraint.BREAK_TIME]
        reward = 0
        break_time = 30
        for i in range(1, len(scheduled_times)):
            action_start = time_to_minutes(scheduled_times[i][0])
            action_end = time_to_minutes(scheduled_times[i][1])

            reward_break_time = 0

            if (action_start - state_end) >= break_time:
                reward_break_time += 1
            elif (action_end - state_start) >= break_time:
                reward_break_time += 1
            else:
                reward_break_time -= 1

            if (state_start - action_end) >= break_time:
                reward_break_time += 1
            elif (state_end - action_start) >= break_time:
                reward_break_time += 1
            else:
                reward_break_time -= 1

            reward_break_time_normalized = normalize(reward_break_time, -1, 1)

            reward += reward_break_time_normalized * break_time_weight

        return reward

    def update_from_settings(self, settings: dict[str, Any]) -> None:
        """
        Update the training configuration from the provided settings.

        Args:
            settings (dict[str, Any]): A dictionary containing the training configuration settings.
        """
        self.constraint_weights[Constraint.TABLE_CONSISTENCY] = settings.get(Constraint.TABLE_CONSISTENCY)
        self.constraint_weights[Constraint.OPP_VARIETY] = settings.get(Constraint.OPP_VARIETY)
        self.constraint_weights[Constraint.BTB_PENALTY] = settings.get(Constraint.BTB_PENALTY)
        self.constraint_weights[Constraint.BREAK_TIME] = settings.get(Constraint.BREAK_TIME)
        self.episodes = settings.get(QParam.EPISODES)
