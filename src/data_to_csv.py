import json
import csv
from xlsxwriter import Workbook
import pandas as pd
import os
import shutil

class QLearningExporter:
    def __init__(self):
        self.clear_exports_folder()
    
    def clear_exports_folder(self):
        folder = './exports'
        for root, dirs, files in os.walk(folder):  # Use os.walk for recursive traversal
            for filename in files:
                file_path = os.path.join(root, filename)
                try:
                    if os.path.isfile(file_path):  # Only delete files
                        os.unlink(file_path)
                except Exception as e:
                    print(f"Failed to delete {file_path}. Reason: {e}")                
                    
    def transform_and_write(self, df, sheet_name, writer):
        # Pivot table to create the desired grid format
        pivot_df = df.pivot_table(index='Time', columns=['Location'], values='Team').reset_index()
        # Sorting if necessary, can be customized based on requirements
        pivot_df.columns = [i for i in pivot_df.columns]
        pivot_df.sort_index(axis=1, inplace=True)
        # Write to the specified sheet in the Excel writer context
        pivot_df.to_excel(writer, sheet_name=sheet_name, index=False)

    def convert_q_table_to_rows(self, q_table):
        q_rows = []
        for ((time_start, time_end, round_type, location_type, location_id, team_id), action), value in q_table.items():
            q_rows.append([time_start, f'{round_type.capitalize()} Round', f'{location_type.capitalize()} {location_id}', action, value])
        return q_rows
    
    def export_q_table_to_csv(self, filename, q_table):
        q_table_rows = self.convert_q_table_to_rows(q_table)
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Time", "Round", "Location", "Team", "Q-Value"])
            writer.writerows(q_table_rows)
        
    def convert_schedule_to_rows(self, schedule):
        s_rows = []
        for (time_start, time_end, round_type, location_type, location_id, team_id) in schedule:
            s_rows.append([time_start, f'{round_type.capitalize()} Round', f'{location_type.capitalize()} {location_id}', team_id])
        return s_rows
    
    def export_schedule_for_eval_to_csv(self, filename, schedule):
        schedule_rows = self.convert_schedule_to_rows(schedule)
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Time", "Round", "Location", "Team"])
            writer.writerows(schedule_rows)
        
    def export_optimal_schedule_to_csv(self, filename, schedule):
        optimal_schedule_rows = self.convert_schedule_to_rows(schedule)
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Time", "Round", "Location", "Team"])
            writer.writerows(optimal_schedule_rows)
            
        self.df = pd.read_csv(filename)
        self.excel_file = './exports/grid_optimal_schedule.xlsx'
        
        with pd.ExcelWriter(self.excel_file, engine='xlsxwriter') as writer:
            # Step 2 & 3: Filter, transform, and write for each round_type
            for round_type in self.df['Round'].unique():
                filtered_df = self.df[self.df['Round'] == round_type]

                # Write the data to Excel
                self.transform_and_write(filtered_df, round_type, writer)  

                # Formatting (Apply after writing the data)
                workbook = writer.book
                worksheet = writer.sheets[round_type]  # Assuming the sheet name matches round_type 

                # Find last row with data 
                df_for_sheet = self.df[self.df['Round'] == round_type].dropna()

        return filename
