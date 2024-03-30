"""Export Q-Learning data to CSV and Excel files."""
import csv
import os
import pandas as pd
from config import Config

OPTIMAL_SCHEDULE_GRID_EXCEL = Config.OPTIMAL_SCHEDULE_GRID_EXCEL_PATH
EXPORTS_DIRECTORY = Config.EXPORTS_DIRECTORY

COL_TIME        = Config.COL_TIME 
COL_ROUND       = Config.COL_ROUND
COL_LOCATION    = Config.COL_LOCATION
COL_TEAM        = Config.COL_TEAM
COL_QVALUE      = Config.COL_QVALUE


class QLearningExporter:
    """
    Class to export Q-Learning data to CSV and Excel files.
    
    """

    def __init__(self):
        """
        Initialize QLearningExporter object.
        
        """
        self.clear_exports_directory()
        self.dataframe = None
        self.excel_file_path = OPTIMAL_SCHEDULE_GRID_EXCEL

    def clear_exports_directory(self):
        """
        Clear the exports directory.
        
        """
        exports_directory = EXPORTS_DIRECTORY
        for root, _, files in os.walk(exports_directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                except OSError as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")    

    def transform_dataframe_to_grid(self, dataframe, sheet_name, writer):
        """
        Transform the DataFrame into grid format and write to Excel.
        
        """
        pivot_dataframe = dataframe.pivot_table(
            index=COL_TIME, 
            columns=[COL_LOCATION], 
            values=COL_TEAM
        ).reset_index()
        
        pivot_dataframe.columns = [i for i in pivot_dataframe.columns]
        pivot_dataframe.sort_index(axis=1, inplace=True)
        pivot_dataframe.to_excel(writer, sheet_name=sheet_name, index=False)

    def convert_q_table_to_rows(self, q_table):
        """
        Convert the Q-Table to a list of rows for CSV export.
        
        """
        q_table_rows = []
        
        for ((time_start, _, round_type, location_type, location_id, _), action), value in q_table.items():
            q_table_rows.append([
                time_start,
                f"{round_type.capitalize()} Round",
                f"{location_type.capitalize()} {location_id}",
                action,
                value,
            ])
            
        return q_table_rows

    def export_q_table_to_csv(self, file_path, q_table):
        """
        Export the Q-Table to a CSV file.
        
        """
        q_table_rows = self.convert_q_table_to_rows(q_table)
        
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([COL_TIME, COL_ROUND, COL_LOCATION, COL_TEAM, COL_QVALUE])
            writer.writerows(q_table_rows)
            
        return file_path

    def convert_schedule_to_rows(self, schedule):
        """
        Convert the schedule to a list of rows for CSV export.
        
        """
        schedule_rows = []
        
        for time_start, _, round_type, location_type, location_id, team_id in schedule:
            schedule_rows.append([
                time_start,
                f"{round_type.capitalize()} Round",
                f"{location_type.capitalize()} {location_id}",
                team_id,
            ])
            
        return schedule_rows

    def export_schedule_to_csv(self, file_path, schedule):
        """
        Export the schedule to a CSV file.
        
        """        
        schedule_rows = self.convert_schedule_to_rows(schedule)
        
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([COL_TIME, COL_ROUND, COL_LOCATION, COL_TEAM])
            writer.writerows(schedule_rows)
            
        return file_path
    
    def export_optimal_schedule_to_excel(self, file_path, schedule):
        """
        Export the optimal schedule to an Excel file.
        
        """
        optimal_schedule_rows = self.convert_schedule_to_rows(schedule)
        
        with open(file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([COL_TIME, COL_ROUND, COL_LOCATION, COL_TEAM])
            writer.writerows(optimal_schedule_rows)
            
        self.dataframe = pd.read_csv(file_path)
        
        with pd.ExcelWriter(self.excel_file_path, engine="xlsxwriter") as writer:
            for round_type in self.dataframe[COL_ROUND].unique():
                filtered_dataframe = self.dataframe[self.dataframe[COL_ROUND] == round_type]
                self.transform_dataframe_to_grid(filtered_dataframe, round_type, writer)
                workbook = writer.book
                worksheet = writer.sheets[round_type]
                dataframe_for_sheet = self.dataframe[self.dataframe[COL_ROUND] == round_type].dropna()
                last_row = len(dataframe_for_sheet)
                worksheet.conditional_format(1, 1, last_row, len(dataframe_for_sheet.columns), {
                    "type": "no_blanks",
                    "format": workbook.add_format({"bg_color": "#FFFFFF"})
                })
        return file_path
