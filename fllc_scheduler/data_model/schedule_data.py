"""Module for managing scheduling data for FLLC events."""

from dataclasses import dataclass, field
from typing import Any, Generator

from ..utils.config import LocationType, RoundType
from .schedule_config import ScheduleConfig


@dataclass(slots=True, unsafe_hash=True)
class Location:
    """Class to represent a location in the FLLC tournament."""

    location_type: LocationType
    location_id: str
    side: int | None = None

    def __eq__(self, other: Any) -> bool:
        """Check equality based on location type, ID, and side."""
        if not isinstance(other, Location):
            return NotImplemented
        return (
            self.location_type == other.location_type
            and self.location_id == other.location_id
            and self.side == other.side
        )


@dataclass(slots=True)
class Booking:
    """Class to represent a single scheduled event in the FLLC tournament."""

    round_type: RoundType
    location: Location
    time_slot: tuple[str, str]
    opponent_id: int | None = None


@dataclass(slots=True)
class Team:
    """Class to represent a team in the FLLC tournament."""

    team_id: int
    bookings: list[Booking] = field(default_factory=list)

    def get_round_count(self, round_type: RoundType) -> int:
        """Get the count of bookings for a specific round type."""
        return sum(1 for booking in self.bookings if booking.round_type == round_type)

    def add_booking(self, booking: Booking) -> None:
        """Adds a new booking to the team's schedule."""
        self.bookings.append(booking)

    def add_opponent(self, time_slot: tuple[str, str], opponent_id: int) -> None:
        """Finds the relevant booking and adds an opponent to it."""
        for booking in self.bookings:
            if booking.time_slot == time_slot:
                booking.opponent_id = opponent_id
                return

    def has_time_conflict(self, new_time_slot: tuple[str, str]) -> bool:
        """Checks if a new time slot conflicts with existing bookings."""
        new_start, new_end = new_time_slot
        for booking in self.bookings:
            existing_start, existing_end = booking.time_slot
            if new_start < existing_end and new_end > existing_start:
                return True
        return False

    def is_fully_scheduled(self, round_type: RoundType, required_rounds: int) -> bool:
        """Check if the team has been scheduled for a specific round type."""
        return self.get_round_count(round_type) >= required_rounds

    def yield_tables(self) -> Generator[Location, None, None]:
        """Yield all tables that this team is scheduled for."""
        for booking in self.bookings:
            yield booking.location

    def yield_opponents(self) -> Generator[tuple[tuple[str, str], int], None, None]:
        """Yield all opponents this team has been scheduled against."""
        for booking in self.bookings:
            if booking.opponent_id is not None:
                yield booking.opponent_id

    def yield_time_slots(self) -> Generator[tuple[str, str], None, None]:
        """Yield all time slots this team is scheduled for."""
        for booking in self.bookings:
            yield booking.time_slot


@dataclass(slots=True)
class ScheduleData:
    """Class to manage scheduling data for FLLC events."""

    config: ScheduleConfig
    teams: dict[int, Team] = field(default_factory=dict)
    booking_lookup: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Initialize the ScheduleData with default values."""
        self.initialize()

    def initialize(self) -> None:
        """Initialize the teams data structure."""
        self.teams.clear()
        for team_id in range(1, self.config.num_teams + 1):
            self.teams[team_id] = Team(team_id=team_id)

    def get_team(self, team_id: int) -> Team:
        """
        Get a team by its ID.

        Args:
            team_id (int): The ID of the team to retrieve.

        Returns:
            Team: The team object corresponding to the given ID.
        """
        return self.teams.get(team_id, None)

    def book_team_for_slot(
        self,
        team_id: int,
        round_type: RoundType,
        time_slot: tuple[str, str],
        location: Location,
    ) -> None:
        """
        High-level method to book a team, handling all state updates.

        Args:
            team_id (int): The ID of the team to book.
            round_type (RoundType): The type of round to book.
            time_slot (tuple[str, str]): The time slot for the booking.
            location (Location): The location for the booking.
        """
        if not (team := self.get_team(team_id)):
            return

        booking = Booking(time_slot=time_slot, location=location, round_type=round_type)
        team.add_booking(booking)

        self.booking_lookup[(time_slot, location)] = team_id

        if location.location_type == LocationType.TABLE:
            side_to_find = 1 if location.side == 2 else 2
            opponent_location = Location(
                location_type=location.location_type,
                location_id=location.location_id,
                side=side_to_find,
            )

            if opponent_id := self.booking_lookup.get((time_slot, opponent_location)):
                opponent_team = self.get_team(opponent_id)
                team.add_opponent(time_slot, opponent_team.team_id)
                opponent_team.add_opponent(time_slot, team.team_id)
