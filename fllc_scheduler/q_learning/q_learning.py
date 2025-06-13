"""Module for Q-Learning based scheduling in FLLC Scheduler."""

import random
from dataclasses import InitVar, dataclass, field
from typing import Any

from ..data_model.schedule_data import ScheduleConfig, ScheduleData
from ..data_model.time_data import TimeData
from ..utils.config import (
    EXPORT_OPTIMAL,
    EXPORT_OPTIMAL_GRID,
    EXPORT_Q_TABLE,
    EXPORT_SCHED_BENCHMARK,
    EXPORT_SCHED_DIR,
)
from ..utils.export_utils import (
    save_optimal_schedule_to_excel,
    save_qtable_to_csv,
    save_schedule_to_csv,
)
from .q_config import TrainingConfig
from .q_data import QLearningSchedulerData
from .q_metrics import QLearningMetrics
from .q_state import QLearningStates, ScheduleState
from .q_strategy import QLearningParameters, QLearningStrategy


@dataclass(slots=True)
class QLearning:
    """Class for implementing Q-Learning based scheduling in FLLC Scheduler."""

    sched_config: InitVar[ScheduleConfig]
    schedule_data: InitVar[ScheduleData]
    time_data: InitVar[TimeData]

    config: TrainingConfig = field(default_factory=TrainingConfig)
    data: QLearningSchedulerData = None
    metrics: QLearningMetrics = field(default_factory=QLearningMetrics)
    param: QLearningParameters = field(default_factory=QLearningParameters)
    state: QLearningStates = field(default_factory=QLearningStates)
    strategy: QLearningStrategy = field(default_factory=QLearningStrategy)
    q_table_size_limit: int = None

    def __post_init__(self, sched_config: ScheduleConfig, schedule_data: ScheduleData, time_data: TimeData) -> None:
        """
        Initialize the Q-Learning scheduler with schedule and time data.
        """
        self.data = QLearningSchedulerData(
            config=sched_config,
            schedule=schedule_data,
            time=time_data,
        )
        self._reset()

    def _reset(self) -> None:
        """Initialize the schedule and states for the Q-learning model."""
        self.state.initialize_schedule_and_states(self.data)
        self.strategy.reset()
        self.q_table_size_limit = len(self.state.states) * len(self.data.schedule.teams)

    def _get_completed_percentage(self) -> float:
        """Calculate the percentage of the schedule that has been completed."""
        return self.state.current_schedule_length / self.data.config.get_required_schedule_slots()

    def _post_benchmark_training(self) -> None:
        """Post-training updates after completing benchmark episodes."""
        save_schedule_to_csv(EXPORT_SCHED_BENCHMARK, self.state.schedule)
        completed_percentage = self._get_completed_percentage()
        self.metrics.evaluate_schedule(self.state.schedule, completed_percentage, "Benchmark")

    def _post_training_episode(self, episode: int, reward: float) -> None:
        """
        Post-training updates after completing an episode.

        Args:
            episode (int): The episode number.
            reward (float): The reward received for the last action taken.
        """
        self.param.update_epsilon()
        self.metrics.update_metrics(reward)
        self.strategy.update()

        export_file = EXPORT_SCHED_DIR / f"schedule_episode_{episode}.csv"
        save_schedule_to_csv(export_file, self.state.schedule)
        completed_percentage = self._get_completed_percentage()
        self.metrics.evaluate_schedule(self.state.schedule, completed_percentage, "Training")

    def _post_optimal_schedule(self) -> None:
        """Post-processing after generating the optimal schedule."""
        save_qtable_to_csv(EXPORT_Q_TABLE, self.state.q_table)
        save_schedule_to_csv(EXPORT_OPTIMAL, self.state.schedule)
        save_optimal_schedule_to_excel(EXPORT_OPTIMAL, EXPORT_OPTIMAL_GRID)
        completed_percentage = self._get_completed_percentage()
        self.metrics.evaluate_schedule(self.state.schedule, completed_percentage, "Optimal")

    def train_benchmark_episodes(self) -> None:
        """Train benchmark episodes to establish a baseline schedule."""
        self._reset()
        self.state.current_schedule_length = 0
        data = self.data
        book = data.schedule.book_team_for_slot
        while self.state.states and not self.state.is_terminal():
            i = random.choice(range(len(self.state.states)))
            s = self.state.states.pop(i)
            if not (actions := self.state.update_available_actions(s, data)):
                continue
            curr_action = random.choice(actions)
            book(curr_action, s.round_type, s.time_slot, s.location)
            self.state.update_schedule(s, curr_action)
        self._post_benchmark_training()

    def train_one_episode(self, episode: int) -> None:
        """
        Train the Q-learning model for one episode.

        Args:
            episode (int): The current episode number.
        """
        self._reset()
        self.state.current_schedule_length = 0
        episode_reward = 0
        data = self.data
        book = data.schedule.book_team_for_slot
        while self.state.states and not self.state.is_terminal():
            s = self.state.states.pop(0)
            if not (actions := self.state.update_available_actions(s, data)):
                continue
            curr_action = self.select_action(s, actions)
            book(curr_action, s.round_type, s.time_slot, s.location)
            self.state.update_schedule(s, curr_action)

            state_reward = self.get_reward(s, curr_action)
            episode_reward += state_reward

            if self.state.states:
                next_state = self.state.states[0]
                self.update_q_value((s, curr_action), state_reward, next_state, actions)
            else:
                self.add_q_value((s, curr_action), state_reward)
        self._post_training_episode(episode, episode_reward)

    def generate_optimal_schedule(self) -> None:
        """Generate the optimal schedule using the trained Q-table."""
        self._reset()
        self.state.current_schedule_length = 0
        data = self.data
        book = data.schedule.book_team_for_slot
        while self.state.states:
            s = self.state.states.pop(0)
            if not (actions := self.state.update_available_actions(s, data)):
                continue
            curr_action = self.state.get_best_action(actions, s)
            book(curr_action, s.round_type, s.time_slot, s.location)
            self.state.update_schedule(s, curr_action)
        self._post_optimal_schedule()

    def update_q_value(self, state_action_pair: tuple, reward: float, next_state: tuple, actions: list) -> None:
        """
        Update the Q-value for a given state-action pair using the Q-learning formula.
        Initializes Q-value if the state-action pair is not in the q_table-table

        Args:
            state_action_pair (tuple): The current state-action pair represented as a tuple.
            reward (float): The reward received for taking the action.
            next_state (tuple): The next state after taking the action.
            actions (list): A list of available actions for the next state.
        """
        curr_q = self.state.q_table.get(state_action_pair, 10)
        potential_qs = (self.state.q_table.get((next_state, a), 10) for a in actions)
        max_future_q = max(potential_qs, default=10)
        self.state.q_table[state_action_pair] = self.param.get_new_q(reward, curr_q, max_future_q)

    def add_q_value(self, state_action_pair: tuple, state_reward: float) -> None:
        """
        Add a new Q-value for a given state-action pair.

        Args:
            state_action_pair (tuple): The current state-action pair represented as a tuple.
            state_reward (float): The reward received for taking the action.
        """
        a = self.param.alpha
        curr_q = self.state.q_table.get(state_action_pair, 0)
        self.state.q_table[state_action_pair] = (1 - a) * curr_q + a * state_reward

    def select_action(self, state: ScheduleState, actions: list) -> Any:
        """
        Select an action based on the epsilon-greedy policy.

        Args:
            state (ScheduleState): The current state represented as a ScheduleState object.
            actions (list): A list of available actions for the current state.
        Returns:
            Any: The selected action, or None if no actions are available.
        """
        random_val = random.uniform(0, 1)

        # Exploration
        if random_val < self.param.epsilon:
            self.strategy.exploration_count += 1
            return random.choice(actions)

        # Exploitation
        self.strategy.exploitation_count += 1
        q_values = [self.state.q_table.get((state, a), 0) for a in actions]
        max_q_value = max(q_values)
        best_actions = [actions[i] for i, q in enumerate(q_values) if q == max_q_value]
        return random.choice(best_actions)

    def get_reward(self, state: ScheduleState, action: int) -> float:
        """
        Get the reward for a given state-action pair based on soft constraints.

        Args:
            state (ScheduleState): The current state represented as a ScheduleState object.
            action (int): The action taken in the current state.
        Returns:
            float: The calculated reward for the state-action pair.
        """
        team = self.data.schedule.get_team(action)
        max_num_rounds = sum(self.data.config.round_types_per_team.values())
        reward = self.config.calc_reward(team, state.time_slot, max_num_rounds)
        required_not_judging = self.data.config.get_required_schedule_slots() - self.data.config.num_teams
        completion_reward = self.state.current_schedule_length / required_not_judging if required_not_judging > 0 else 0
        return reward + (reward * completion_reward)

    def update_from_settings(self, settings: dict[str, Any]) -> None:
        """
        Update the Q-learning settings based on the provided settings dictionary.

        Args:
            settings (dict[str, Any]): A dictionary containing the Q-learning settings.
        """
        self._reset()
        self.param.update_from_settings(settings)
        self.config.update_from_settings(settings)
