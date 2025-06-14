"""FLLC Q-Learning Tournament Scheduler Data Module."""

from dataclasses import dataclass, field

from ..q_learning.q_learning import QLearning
from .schedule_config import ScheduleConfig
from .schedule_data import ScheduleData
from .time_data import TimeData, TimeDataDurationsAvailable, TimeDataSettings, TimeDataStartTimeCollections


@dataclass(slots=True)
class FLLCSchedulerData:
    """Data class to hold the schedule data for the FLLC Q-Learning Tournament Scheduler."""

    config: ScheduleConfig = field(default_factory=ScheduleConfig)
    schedule: ScheduleData = None
    time: TimeData = None
    q_learning: QLearning = None

    def __post_init__(self) -> None:
        """Initialize the FLLCSchedulerData with default values."""
        self.schedule = ScheduleData(
            config=self.config,
        )
        self.time = TimeData(
            config=self.config,
            setting=TimeDataSettings(),
            start_times=TimeDataStartTimeCollections(),
            duration_available=TimeDataDurationsAvailable(),
        )
        self.q_learning = QLearning(self.config, self.schedule, self.time)
