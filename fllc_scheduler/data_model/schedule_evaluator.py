"""Optimized module for evaluating and analyzing schedules in FLLC events."""

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import pandas as pd

from ..utils.config import BASE_ADJUST, WEIGHTED
from ..q_learning.q_state import ScheduleState
from ..utils.export_utils import _format_location
from ..utils.stat_utils import average, normalize


@dataclass(slots=True)
class TimeStats:
    """Encapsulates time statistics."""

    break_between_start_times: list[float] = field(default_factory=list)
    break_between_end_times: list[float] = field(default_factory=list)
    downtimes: list[float] = field(default_factory=list)

    @property
    def avg_break_between_start_times(self) -> float:
        """Calculate the average break time between start times."""
        return average(self.break_between_start_times) if self.break_between_start_times else 0.0

    @property
    def avg_break_between_end_times(self) -> float:
        """Calculate the average break time between end times."""
        return average(self.break_between_end_times) if self.break_between_end_times else 0.0

    @property
    def avg_downtime(self) -> float:
        """Calculate the average downtime between events."""
        return average(self.downtimes) if self.downtimes else 0.0

    @property
    def min_downtime(self) -> float:
        """Calculate the minimum downtime."""
        return min(self.downtimes) if self.downtimes else 0.0

    @property
    def max_downtime(self) -> float:
        """Calculate the maximum downtime."""
        return max(self.downtimes) if self.downtimes else 0.0

    @property
    def total_downtime(self) -> float:
        """Calculate the total downtime across all events."""
        return sum(self.downtimes)

    @property
    def avg_break_time(self) -> float:
        """Calculate the average break time across all metrics."""
        return (self.avg_break_between_start_times + self.avg_break_between_end_times + self.avg_downtime) / 3


@dataclass(slots=True)
class TeamStats:
    """Encapsulates team statistics."""

    team_id: int
    appearances: list[int] = field(default_factory=list)
    time_round_location: list[tuple[str, str, str, str]] = field(default_factory=list)
    unique_locations: list[str] = field(default_factory=list)
    opponents: list[int] = field(default_factory=list)
    unique_opponents: list[int] = field(default_factory=list)
    time: TimeStats = field(default_factory=TimeStats)

    @property
    def count_appearances(self) -> int:
        """Count the number of appearances for this team."""
        return len(self.appearances)

    @property
    def count_unique_locations(self) -> int:
        """Count the number of unique locations this team has appeared in."""
        return len(self.unique_locations)

    @property
    def count_opponents(self) -> int:
        """Count the number of opponents this team has faced."""
        return len(self.opponents)

    @property
    def count_unique_opponents(self) -> int:
        """Count the number of unique opponents this team has faced."""
        return len(self.unique_opponents)


@dataclass(slots=True)
class TimeMetrics:
    """Encapsulates schedule-wide metrics."""

    times: list[str] = field(default_factory=list)
    end_times: list[str] = field(default_factory=list)
    round_start_times: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))
    round_avg_lengths: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class ScheduleMetrics:
    """Encapsulates schedule-wide metrics."""

    time: TimeMetrics = field(default_factory=TimeMetrics)
    rounds: list[str] = field(default_factory=list)
    locations: list[str] = field(default_factory=list)
    teams: list[int] = field(default_factory=list)
    unique_locations: list[str] = field(default_factory=list)
    unique_teams: list[int] = field(default_factory=list)


@dataclass(slots=True)
class BaseMetrics:
    """Encapsulate base metrics."""

    avg_downtime: float = 0.0
    max_downtime: float = 0.0
    min_appearances: int = 0
    max_appearances: int = 0
    appearance_variance: float = 0.0
    avg_unique_locations: float = 0.0
    avg_unique_opponents: float = 0.0


@dataclass(slots=True)
class ScheduleEvaluator:
    """Class to evaluate and analyze schedules for FLLC events."""

    schedule: list[ScheduleState]
    _metrics: ScheduleMetrics | None = field(default=None, init=False)
    _team_stats: dict[int, TeamStats] | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Initialize the ScheduleEvaluator."""
        self._process_schedule()

    def _process_schedule(self) -> None:
        """Process the schedule and extract all metrics in a single pass."""
        self._metrics = ScheduleMetrics()

        for state in self.schedule:
            time = state.time_slot[0]
            round_type = state.round_type.capitalize()
            location = _format_location(state.location)
            team_id = state.team_id if state.team_id is not None else 0

            self._metrics.time.times.append(time)
            self._metrics.rounds.append(round_type)
            self._metrics.locations.append(location)
            self._metrics.teams.append(team_id)
            self._metrics.time.round_start_times[round_type].append(time)

        self._metrics.unique_locations = sorted(set(self._metrics.locations))
        self._metrics.unique_teams = sorted(set(t for t in self._metrics.teams if t != 0))

        self._calculate_round_metrics()
        self._process_team_data()

    def _calculate_round_metrics(self) -> None:
        """Calculate round lengths and end times."""
        round_start_times_sorted = {
            round_type: sorted(set(times)) for round_type, times in self._metrics.time.round_start_times.items()
        }

        for round_type, times in round_start_times_sorted.items():
            if len(times) > 1:
                durations = []
                for i in range(len(times) - 1):
                    start_time = datetime.strptime(times[i], "%H:%M")
                    end_time = datetime.strptime(times[i + 1], "%H:%M")
                    durations.append((end_time - start_time).total_seconds() / 60)
                self._metrics.time.round_avg_lengths[round_type] = average(durations)
            else:
                self._metrics.time.round_avg_lengths[round_type] = 0.0

        for i, (round_type, start_time) in enumerate(zip(self._metrics.rounds, self._metrics.time.times)):
            avg_length = self._metrics.time.round_avg_lengths.get(round_type, 0.0)
            start_datetime = datetime.strptime(start_time, "%H:%M")
            end_datetime = start_datetime + timedelta(minutes=avg_length)
            self._metrics.time.end_times.append(end_datetime.strftime("%H:%M"))

    def _process_team_data(self) -> None:
        """Process team data."""
        self._team_stats = {}

        team_indices = defaultdict(list)
        for i, team_id in enumerate(self._metrics.teams):
            if team_id != 0:
                team_indices[team_id].append(i)

        for team_id, indices in team_indices.items():
            self._team_stats[team_id] = self._calculate_team_stats(team_id, indices)

    def _calculate_team_stats(self, team_id: int, indices: list[int]) -> TeamStats:
        """Calculate statistics for a specific team."""
        stats = TeamStats(team_id=team_id, appearances=indices)

        trl_data = []
        for i in indices:
            trl_data.append(
                (
                    self._metrics.time.times[i],
                    self._metrics.time.end_times[i],
                    self._metrics.rounds[i],
                    self._metrics.locations[i],
                )
            )

        trl_data.sort(key=lambda x: datetime.strptime(x[0], "%H:%M"))
        stats.time_round_location = trl_data

        if len(trl_data) > 1:
            self._calculate_timing_metrics(stats, trl_data)

        self._calculate_location_opponent_metrics(stats, indices)

        return stats

    def _calculate_timing_metrics(self, stats: TeamStats, trl_data: list[tuple[str, str, str, str]]) -> None:
        """Calculate timing-related metrics for a team."""
        start_times = [datetime.strptime(t[0], "%H:%M") for t in trl_data]
        end_times = [datetime.strptime(t[1], "%H:%M") for t in trl_data]

        for i in range(len(start_times) - 1):
            break_start = (start_times[i + 1] - start_times[i]).total_seconds() / 60
            stats.time.break_between_start_times.append(break_start)

            break_end = (end_times[i + 1] - end_times[i]).total_seconds() / 60
            stats.time.break_between_end_times.append(break_end)

            downtime = (start_times[i + 1] - end_times[i]).total_seconds() / 60
            stats.time.downtimes.append(downtime)

    def _calculate_location_opponent_metrics(self, stats: TeamStats, indices: list[int]) -> None:
        """Calculate location and opponent metrics for a team."""
        locations = [self._metrics.locations[i] for i in indices]
        stats.unique_locations = sorted(set(locations))

        opponents = []
        for idx in indices:
            opponent_idx = idx + 1 if idx % 2 == 0 else idx - 1
            if 0 <= opponent_idx < len(self._metrics.teams) and self._metrics.teams[opponent_idx] != 0:
                opponents.append(self._metrics.teams[opponent_idx])

        stats.opponents = [op for op in opponents if op != 0]
        stats.unique_opponents = sorted(set(stats.opponents))

    def generate_aggregate_statistics(self, name: str) -> None:
        """Generate aggregate statistics and save to CSV."""
        if not self._team_stats:
            return

        team_data = []
        for team_id, stats in self._team_stats.items():
            team_data.append(
                {
                    "Team": team_id,
                    "Appearances": stats.count_appearances,
                    "Time + Round + Location": stats.time_round_location,
                    "Break Between Start Times": stats.time.break_between_start_times,
                    "Average Break Between Start Times": stats.time.avg_break_between_start_times,
                    "Break Between End Times": stats.time.break_between_end_times,
                    "Average Break Between End Times": stats.time.avg_break_between_end_times,
                    "Downtimes": stats.time.downtimes,
                    "Min Downtime": stats.time.min_downtime,
                    "Max Downtime": stats.time.max_downtime,
                    "Total Downtime": stats.time.total_downtime,
                    "Average Downtime": stats.time.avg_downtime,
                    "Average Break Time": stats.time.avg_break_time,
                    "Unique Locations": stats.unique_locations,
                    "Number of Unique Locations": stats.count_unique_locations,
                    "Opponents": stats.opponents,
                    "Number of Opponents": stats.count_opponents,
                    "Unique Opponents": stats.unique_opponents,
                    "Number of Unique Opponents": stats.count_unique_opponents,
                }
            )

        aggregate_df = pd.DataFrame(team_data).sort_values(by=["Team"])
        aggregate_df.to_csv(f"./exports/aggregate_stats/aggregate_statistics_{name}.csv", index=False)

    def calculate_schedule_score(self, completion_percentage: float) -> float:
        """Calculate the score of a schedule based on completion percentage and various metrics."""
        bm = self._calculate_base_metrics()
        if not bm:
            return 0.0

        unique_locations = len(self._metrics.unique_locations)
        unique_teams = len(self._metrics.unique_teams)
        diff_appearances = bm.max_appearances - bm.min_appearances

        downtime = normalize(bm.avg_downtime, 0, bm.max_downtime) if bm.max_downtime > 0 else 0
        appearance = normalize(bm.appearance_variance, 0, diff_appearances) if diff_appearances > 0 else 0
        location = normalize(bm.avg_unique_locations, 0, unique_locations) if unique_locations > 0 else 0
        opponent = normalize(bm.avg_unique_opponents, 0, unique_teams) if unique_teams > 0 else 0

        base_score = self._calculate_base_score(downtime, appearance, location, opponent)
        adjusted_completion_percentage = self._calculate_adjusted_completion_percentage(completion_percentage)

        return base_score * adjusted_completion_percentage

    def _calculate_base_metrics(self) -> BaseMetrics | None:
        """Calculate base metrics for the schedule score."""
        if not self._team_stats:
            return None

        valid_downtimes = [stats.time.avg_downtime for stats in self._team_stats.values() if stats.time.downtimes]
        max_downtimes = [stats.time.max_downtime for stats in self._team_stats.values() if stats.time.downtimes]
        appearances = [stats.count_appearances for stats in self._team_stats.values()]
        unique_locations_counts = [stats.count_unique_locations for stats in self._team_stats.values()]
        unique_opponents_counts = [stats.count_unique_opponents for stats in self._team_stats.values()]

        if not appearances:
            return None

        avg_downtime = average(valid_downtimes) if valid_downtimes else 0.0
        max_downtime = max(max_downtimes) if max_downtimes else 0.0
        min_appearances = min(appearances)
        max_appearances = max(appearances)
        avg_appearances = average(appearances)

        appearance_variance = sum((count - avg_appearances) ** 2 for count in appearances) / len(appearances)
        avg_unique_locations = average(unique_locations_counts)
        avg_unique_opponents = average(unique_opponents_counts)
        return BaseMetrics(
            avg_downtime=avg_downtime,
            max_downtime=max_downtime,
            min_appearances=min_appearances,
            max_appearances=max_appearances,
            appearance_variance=appearance_variance,
            avg_unique_locations=avg_unique_locations,
            avg_unique_opponents=avg_unique_opponents,
        )

    def _calculate_base_score(self, downtime: float, appearance: float, location: float, opponent: float) -> float:
        """Calculate the base score of a schedule based on various metrics."""
        return sum([WEIGHTED * (1 - downtime), WEIGHTED * (1 - appearance), WEIGHTED * location, WEIGHTED * opponent])

    def _calculate_adjusted_completion_percentage(self, completion_percentage: float) -> float:
        """Calculate the adjusted completion percentage."""
        c_percent = max(0.0, min(1.0, completion_percentage))
        return BASE_ADJUST + (BASE_ADJUST * c_percent)
