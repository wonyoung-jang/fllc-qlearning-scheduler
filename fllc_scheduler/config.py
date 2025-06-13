"""Enums for the FLLC Scheduler."""

from enum import StrEnum
from pathlib import Path

EXPORT_DIR = Path("./exports")
EXPORT_Q_TABLE = EXPORT_DIR / "q_table.csv"
EXPORT_OPTIMAL = EXPORT_DIR / "optimal_schedule.csv"
EXPORT_OPTIMAL_GRID = EXPORT_DIR / "optimal_schedule_grid.xlsx"
EXPORT_SCHED_DIR = EXPORT_DIR / "training_schedules_output"
EXPORT_SCHED_BENCHMARK = EXPORT_SCHED_DIR / "schedule_episode_benchmark.csv"
EXPORT_EVAL_DIR = EXPORT_DIR / "schedule_evaluation"
EXPORT_RESULTS = EXPORT_EVAL_DIR / "evaluation_results.csv"
WEIGHTED = 0.25
BASE_ADJUST = 0.5


class Time(StrEnum):
    """Enumeration for time-related settings in the FLLC Scheduler."""

    JUDGING_START = "start_time_judging_rounds"
    PRACTICE_START = "start_time_practice_rounds"
    PRACTICE_STOP = "stop_time_practice_rounds"
    TABLE_START = "start_time_table_rounds"
    TABLE_STOP = "stop_time_table_rounds"


class Configuration(StrEnum):
    """Enumeration for configuration options in the FLLC Scheduler."""

    NUM_TEAMS = "num_teams"
    NUM_ROUNDS = "num_rounds"
    NUM_TABLES = "num_tables"
    ROUND_TYPES = "round_types_per_team"


class QParam(StrEnum):
    """Enumeration for Q-learning parameters in the FLLC Scheduler."""

    ALPHA = "alpha"
    GAMMA = "gamma"
    EPSILON_START = "epsilon_start"
    EPSILON_END = "epsilon_end"
    EPSILON_DECAY = "epsilon_decay"
    EPISODES = "episodes"


class LocationType(StrEnum):
    """Enumeration for different types of locations in the FLLC tournament."""

    ROOM = "Room"
    TABLE = "Table"


class RoundType(StrEnum):
    """Enum for different types of rounds in the FLLC Scheduler."""

    JUDGING = "judging"
    PRACTICE = "practice"
    TABLE = "table"


class Constraint(StrEnum):
    """Enum for different types of constraints in the FLLC Scheduler."""

    TABLE_CONSISTENCY = "Table Consistency"
    OPP_VARIETY = "Opponent Variety"
    BTB_PENALTY = "Back to Back Penalty"
    BREAK_TIME = "Break Time"


class Training(StrEnum):
    """Enum for different training types in the FLLC Scheduler."""

    BENCHMARK = "benchmark"
    TRAINING = "training"
    OPTIMAL = "optimal"
