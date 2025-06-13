"""Module for managing scheduling data for FLLC events."""

from dataclasses import dataclass, field
from typing import Any

from .config import RoundType, Configuration


@dataclass(slots=True)
class ScheduleConfig:
    """Configuration for the tournament schedule."""

    num_teams: int = 42
    num_rooms: int = 7
    num_tables: int = 4
    round_types_per_team: dict[RoundType, int] = field(
        default_factory=lambda: {
            RoundType.JUDGING: 1,
            RoundType.PRACTICE: 2,
            RoundType.TABLE: 3,
        }
    )

    def get_required_schedule_slots(self) -> int:
        """
        Calculate the total number of required schedule slots based on the number of teams and round types.

        Returns:
            int: The total number of required schedule slots.
        """
        n_teams = self.num_teams
        n_rounds = sum(self.round_types_per_team.values())
        return n_teams * n_rounds

    def update_from_settings(self, settings: dict[str, Any]) -> None:
        """
        Update the scheduling data from the provided settings.

        Args:
            settings (dict[str, Any]): The settings to update the scheduling data.
        """
        self.num_teams = settings.get(Configuration.NUM_TEAMS)
        self.num_rooms = settings.get(Configuration.NUM_ROUNDS)
        self.num_tables = settings.get(Configuration.NUM_TABLES)
        self.round_types_per_team.update(settings.get(Configuration.ROUND_TYPES))
