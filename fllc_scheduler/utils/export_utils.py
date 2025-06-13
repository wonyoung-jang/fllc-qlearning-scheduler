"""Utility functions for exporting data to CSV and Excel formats."""

import csv
from pathlib import Path

import pandas as pd

from ..q_learning.q_state import ScheduleState
from ..data_model.schedule_data import Location


def clear_exports_dir(export_dir: Path) -> None:
    """Clear the exports folder by deleting all files."""
    for root, _, files in Path.walk(export_dir):
        for file in files:
            path = root / file
            try:
                if path.is_file():
                    path.unlink()
            except Exception as e:
                print(f"Failed to delete {path}. Reason: {e}")
                raise e


def _format_location(location: Location) -> str:
    """Format location string."""
    location_str = f"{location.location_type.capitalize()} {location.location_id}"
    if location.side is not None:
        location_str += f"{location.side}"
    return location_str


def save_qtable_to_csv(file: Path, q_table: dict[tuple[ScheduleState, int], float]) -> None:
    """
    Export the Q-table to a CSV file.

    Args:
        file (Path): The path to the file where the Q-table will be saved.
        q_table (dict): The Q-table data to export.
    """
    header = ("Time", "Round", "Location", "Team", "Q-Value")
    with file.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for (state, action), value in q_table.items():
            time = state.time_slot[0]
            round_type = state.round_type.capitalize()
            location = _format_location(state.location)
            w.writerow((time, round_type, location, action, value))


def save_schedule_to_csv(file: Path, schedule: list[ScheduleState]) -> None:
    """
    Export the schedule for evaluation to a CSV file.

    Args:
        file (Path): The path to the file to save the schedule.
        schedule (list[ScheduleState]): The schedule data to export.
    """
    header = ("Time", "Round", "Location", "Team")
    with file.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for state in schedule:
            time = state.time_slot[0]
            round_type = state.round_type.capitalize()
            location = _format_location(state.location)
            team_id = state.team_id
            w.writerow((time, round_type, location, team_id))


def save_optimal_schedule_to_excel(file: Path, excel_file: Path) -> None:
    """
    Export the optimal schedule to an Excel file.

    Args:
        file (Path): The path to the file to save the optimal schedule.
        excel_file (Path): The path to the Excel file to save the schedule.
    """
    df = pd.read_csv(file)
    with pd.ExcelWriter(excel_file, engine="xlsxwriter") as w:
        for round_type in df["Round"].unique():
            filtered_df = df[df["Round"] == round_type]
            pivot = filtered_df.pivot_table(
                index="Time", columns=["Location"], values="Team", aggfunc="first"
            ).reset_index()
            pivot.sort_index(axis=1, inplace=True)
            pivot.to_excel(w, sheet_name=round_type, index=False)
            df[df["Round"] == round_type].dropna()
