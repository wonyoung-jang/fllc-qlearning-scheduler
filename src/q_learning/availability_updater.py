from config import Config

JUDGING = Config.JUDGING
PRACTICE = Config.PRACTICE
TABLE = Config.TABLE
TABLE_SIDE_1 = Config.TABLE_SIDE_1
TABLE_SIDE_2 = Config.TABLE_SIDE_2


class AvailabilityUpdater:
    def __init__(self, schedule_data, practice_teams_available, table_teams_available) -> None:
        self.schedule_data = schedule_data
        self.practice_teams_available = practice_teams_available
        self.table_teams_available = table_teams_available
        
    def update_team_availability(self, team_id, round_type, time_slot, location_id, side) -> None:
        """
        Update the team availability for the current state.
        
        """
        if team_id in self.schedule_data.teams:
            team_info = self.schedule_data.teams[team_id]

            team_info.scheduled_round_types[round_type] += 1
            team_info.scheduled_times.append(time_slot)
            team_info.scheduled_tables.append((location_id, int(side)))
            team_info.scheduled_time_table_pairs.append((time_slot, (location_id, int(side))))

            if round_type == PRACTICE:
                self.practice_teams_available.remove(team_id)
            elif round_type == TABLE:
                self.table_teams_available.remove(team_id)

            # Table side and opponent logic
            table_id = location_id[0]

            if side == TABLE_SIDE_2:  # Assuming side 2 indicates both are scheduled
                other_side = TABLE_SIDE_1
                
                # Find the team assigned to the other side, if any
                for other_team_id, other_team_info in self.schedule_data.teams.items():
                    if (
                        other_team_id != team_id
                        and (time_slot, (table_id, other_side)) in other_team_info.scheduled_time_table_pairs
                    ):
                        # Update opponents for both teams
                        other_team_info["scheduled_opponents"].append(team_id)
                        team_info["scheduled_opponents"].append(other_team_id)

                        break  # Found the other team, no need to continue the loop
        else:
            print(f"Team {team_id} does not exist.")

    def update_table_availability(self, location_id, team_id, time_slot) -> None:
        """
        Update the table availability for the current state.
        
        """
        table_id = location_id[0]  # Extract table ID (e.g., 'A1' from 'A11')
        side = int(location_id[-1])  # Extract side (e.g., 1 from 'A11')

        if (table_id, side) in self.schedule_data.tables:
            self.schedule_data.tables[(table_id, side)].scheduled_teams.append(team_id)
            self.schedule_data.tables[(table_id, side)].scheduled_times.append(time_slot)
        else:
            print(f"Table {table_id} side {side} does not exist.")
