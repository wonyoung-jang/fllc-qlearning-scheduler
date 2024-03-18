"""This module contains the ScheduleEvaluator class, which is responsible for evaluating the schedule and generating aggregate statistics."""
import csv
import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta


class ScheduleEvaluator:
    """Class to evaluate the schedule and generate aggregate statistics."""
    
    def __init__(self, file_path):
        """Initialize ScheduleEvaluator object."""
        self.file_path = file_path
        self.detailed_data_summary = self.extract_detailed_information()

    def calculate_round_length_by_start_times(self, data_summary):
        """Calculate the average length of each round type based on the start times."""
        round_start_times = defaultdict(list)
        round_start_times_sorted = defaultdict(set)
        round_end_times = defaultdict(list)
        round_lengths = defaultdict(list)

        for round_type, start_time in zip(data_summary["Round"]["All"], data_summary["Time"]["All"]):
            round_start_times[round_type].append(start_time)

        for round_type in round_start_times:
            round_start_times_sorted[round_type] = sorted(set(round_start_times[round_type]))

        for round_type, times in round_start_times_sorted.items():
            for i in range(len(times) - 1):
                start_time = datetime.strptime(times[i], "%H:%M")
                end_time = datetime.strptime(times[i + 1], "%H:%M")
                duration = (end_time - start_time).total_seconds() / 60
                round_lengths[round_type].append(duration)

        round_average_lengths = {
            round_type: sum(durations) / len(durations) for round_type, durations in round_lengths.items() if durations
        }

        for round_type, start_times in round_start_times.items():
            for start_time in start_times:
                round_end_times[round_type].append(
                    datetime.strptime(start_time, "%H:%M") + timedelta(minutes=round_average_lengths[round_type])
                )

        return round_average_lengths, round_start_times, round_end_times

    def extract_detailed_information(self):
        """Extract detailed information from the schedule file."""
        detailed_tracking = defaultdict(lambda: defaultdict(list))
        with open(self.file_path, "r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            columns = reader.fieldnames
            for row in reader:
                for column in columns:
                    if column == "Team":
                        row[column] = int(row[column]) if row[column].isdigit() else 0
                    detailed_tracking[column]["All"].append(row[column])

        for column, details in detailed_tracking.items():
            details["Unique"] = sorted(set(detail for detail in details["All"] if detail != 0))
            details["Count All"] = len(details["All"])
            details["Count Unique"] = len(details["Unique"])

        (
            detailed_tracking["Round Average Length"],
            detailed_tracking["Round Start Times"],
            detailed_tracking["Round End Times"],
        ) = self.calculate_round_length_by_start_times(detailed_tracking)
        detailed_tracking["Team Info"] = self.process_team_data(detailed_tracking)
        return detailed_tracking

    def process_team_data(self, data_summary):
        """Process team data to calculate various statistics."""
        all_teams = [int(i) for i in data_summary["Team"]["Unique"]]

        for k, v in data_summary["Round End Times"].items():
            data_summary["Round End Times"][k] = [datetime.strftime(t, "%H:%M") for t in v]
            for t in v:
                data_summary["Time"]["End"].append(datetime.strftime(t, "%H:%M"))

        for team in all_teams:
            if team is None:
                continue

            data_summary["Team Info"][team] = self.calculate_team_data(data_summary, team)

        return data_summary["Team Info"]

    def calculate_team_data(self, data_summary, team):
        """Calculate various statistics for a specific team."""
        team_data = defaultdict(list)
        appearances = [i for i, t in enumerate(data_summary["Team"]["All"]) if t == team]
        team_data["Appearances"] = appearances
        team_data["Count Appearances"] = len(appearances)

        trl = [
            (
                data_summary["Time"]["All"][i],
                data_summary["Time"]["End"][i],
                data_summary["Round"]["All"][i],
                data_summary["Location"]["All"][i],
            )
            for i in appearances
        ]
        trl = sorted(trl, key=lambda x: datetime.strptime(x[0], "%H:%M"))
        team_data["Time + Round + Location"] = trl

        # Downtime Calculation
        times = [datetime.strptime(t[0], "%H:%M") for t in trl]  # Extract start times
        end_times = [datetime.strptime(t[1], "%H:%M") for t in trl]  # Extract end times
        if len(times) > 1:
            break_between_start_times = [(times[i + 1] - times[i]).total_seconds() / 60 for i in range(len(times) - 1)]
            break_between_end_times = [
                (end_times[i + 1] - end_times[i]).total_seconds() / 60 for i in range(len(times) - 1)
            ]
            downtimes = [(times[i + 1] - end_times[i]).total_seconds() / 60 for i in range(len(times) - 1)]

            team_data["Break Between Start Times"] = break_between_start_times
            team_data["Average Break Between Start Times"] = sum(break_between_start_times) / len(
                break_between_start_times
            )
            team_data["Break Between End Times"] = break_between_end_times
            team_data["Average Break Between End Times"] = sum(break_between_end_times) / len(break_between_end_times)
            team_data["Downtimes"] = downtimes
            team_data["Average Downtime"] = sum(downtimes) / len(downtimes)
            team_data["Min Downtime"] = min(downtimes)
            team_data["Max Downtime"] = max(downtimes)
            team_data["Total Downtime"] = sum(downtimes)
            team_data["Average Break Time"] = (
                team_data["Average Break Between Start Times"] + team_data["Average Break Between End Times"]
            ) + team_data["Average Downtime"] / 3

        # Unique Locations
        team_data["Unique Locations"] = sorted(set(location for _, _, _, location in trl))
        team_data["Count Unique Locations"] = len(team_data["Unique Locations"])

        # Determine Opponents and Unique Opponents
        opponents = []
        for appearance in team_data["Appearances"]:
            if appearance % 2 == 0:
                opponent_index = appearance + 1
            else:
                opponent_index = appearance - 1

            if (
                0 <= opponent_index < len(data_summary["Team"]["All"])
                and data_summary["Team"]["All"][opponent_index] != 0
            ):  # Check for 'None'
                opponents.append(data_summary["Team"]["All"][opponent_index])

            team_data["Opponents"] = [op for op in opponents if op != 0]
            team_data["Unique Opponents"] = sorted(set(team_data["Opponents"]))
            team_data["Count Opponents"] = len(team_data["Opponents"])
            team_data["Count Unique Opponents"] = len(team_data["Unique Opponents"])

        return team_data

    def generate_aggregate_statistics(self, name):
        """Generate aggregate statistics for the schedule."""
        total_rounds = len([i for i in self.detailed_data_summary["Team"]["All"] if i != 0])

        # Convert team info to DataFrame for further analysis or export
        team_stats = []
        for team, info in self.detailed_data_summary["Team Info"].items():
            team_stats.append(
                {
                    "Team": team,
                    "Appearances": info["Count Appearances"],
                    "Time + Round + Location": info["Time + Round + Location"],
                    "Break Between Start Times": info["Break Between Start Times"],
                    "Average Break Between Start Times": info["Average Break Between Start Times"],
                    "Break Between End Times": info["Break Between End Times"],
                    "Average Break Between End Times": info["Average Break Between End Times"],
                    "Downtimes": info["Downtimes"],
                    "Min Downtime": info["Min Downtime"],
                    "Max Downtime": info["Max Downtime"],
                    "Total Downtime": info["Total Downtime"],
                    "Average Downtime": info["Average Downtime"],
                    "Average Break Time": info["Average Break Time"],
                    "Unique Locations": info["Unique Locations"],
                    "Number of Unique Locations": info["Count Unique Locations"],
                    "Opponents": info["Opponents"],
                    "Number of Opponents": info["Count Opponents"],
                    "Unique Opponents": info["Unique Opponents"],
                    "Number of Unique Opponents": info["Count Unique Opponents"],
                }
            )
        aggregate_df = pd.DataFrame(team_stats)
        aggregate_df = aggregate_df.sort_values(by=["Team"])

        # Example of saving to CSV
        aggregate_df.to_csv(f"./exports/aggregate_stats/aggregate_statistics_{name}.csv", index=False)
        return aggregate_df

    def calculate_schedule_score(self, completion_percentage):
        """Calculate the score of the schedule based on various metrics."""
        if completion_percentage == 1:
            adjusted_score = 1
            return adjusted_score
        # Ensure completion_percentage is within the expected range
        completion_percentage = max(0, min(1, completion_percentage))

        # Calculate base metrics (as previously defined)
        team_stats = self.detailed_data_summary["Team Info"]
        (
            avg_downtime,
            max_downtime,
            avg_appearances,
            min_appearances,
            max_appearances,
            appearance_variance,
            avg_unique_locations,
            avg_unique_opponents,
        ) = self.calculate_base_metrics(team_stats)

        # Calculate normalized metrics
        normalized_downtime = self.normalize(avg_downtime, 0, max_downtime)
        normalized_appearance_variance = self.normalize(appearance_variance, 0, max_appearances - min_appearances)
        normalized_location_diversity = self.normalize(
            avg_unique_locations,
            0,
            len(self.detailed_data_summary["Location"]["Unique"]),
        )
        normalized_opponent_diversity = self.normalize(
            avg_unique_opponents, 0, len(self.detailed_data_summary["Team"]["Unique"])
        )

        # Calculate the weighted score
        base_score = (
            0.25 * (1 - normalized_downtime)
            + 0.25 * (1 - normalized_appearance_variance)
            + 0.25 * normalized_location_diversity
            + 0.25 * normalized_opponent_diversity
        )

        # Adjust score based on the completion percentage
        # The formula here can be adjusted. This example linearly scales the score based on completion.
        adjusted_score = base_score * (0.5 + 0.5 * completion_percentage)  # Scales score up to 50% based on completion

        return adjusted_score

    def calculate_base_metrics(self, team_stats):
        """Calculate the base metrics for the schedule."""
        avg_downtime = sum(
            info["Average Downtime"] for info in team_stats.values() if info["Average Downtime"] != []
        ) / len(team_stats)
        max_downtime = max(info["Max Downtime"] for info in team_stats.values() if info["Max Downtime"] != [])
        avg_appearances = sum(info["Count Appearances"] for info in team_stats.values()) / len(team_stats)
        min_appearances = min(info["Count Appearances"] for info in team_stats.values())
        max_appearances = max(info["Count Appearances"] for info in team_stats.values())
        appearance_variance = sum(
            (info["Count Appearances"] - avg_appearances) ** 2 for info in team_stats.values()
        ) / len(team_stats)
        avg_unique_locations = sum(len(info["Unique Locations"]) for info in team_stats.values()) / len(team_stats)
        avg_unique_opponents = sum(len(info["Unique Opponents"]) for info in team_stats.values()) / len(team_stats)

        return (
            avg_downtime,
            max_downtime,
            avg_appearances,
            min_appearances,
            max_appearances,
            appearance_variance,
            avg_unique_locations,
            avg_unique_opponents,
        )

    def normalize(self, value, min_value, max_value):
        """Normalize a value to the range [0, 1]."""
        if max_value - min_value == 0:
            return 0
        return (value - min_value) / (max_value - min_value)
