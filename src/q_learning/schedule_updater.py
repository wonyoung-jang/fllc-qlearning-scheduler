from typing import List, Tuple
from config import Config


class ScheduleUpdater:
    def __init__(self) -> None:
        """
        Initialize the schedule updater.
        
        """
    
    def update_schedule(self, current_state, selected_action, schedule, current_length) -> Tuple[List[List], int]:
        """
        Update the schedule for the current state.
        
        """
        for i, schedule_row in enumerate(schedule):
            sched_row = tuple(schedule_row[:5])
            if sched_row == current_state[:5] and schedule_row[5] is None:
                schedule[i][5] = selected_action
                break
        current_length += 1
        return schedule, current_length