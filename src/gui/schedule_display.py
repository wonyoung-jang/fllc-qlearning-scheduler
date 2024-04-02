from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem, QSplitter, QGroupBox, QVBoxLayout
import colorsys
from config import Config


class ScheduleDisplay:
    def __init__(self, schedule_data, time_data, q_learning): 
        """Creates the schedule display for the Q-learning scheduler."""
        self.schedule_data = schedule_data
        self.time_data = time_data
        
        # Judging Rounds Table
        self.judging_table = QTableWidget()
        self.judging_table.setColumnCount(self.schedule_data.NUM_ROOMS + 1)  # Time + Room columns
        self.judging_table.setHorizontalHeaderLabels(['Time'] + [f'Room {i+1}' for i in range(self.schedule_data.NUM_ROOMS)])

        # Practice Rounds Table
        self.practice_table = QTableWidget()
        self.practice_table.setColumnCount(self.schedule_data.NUM_TABLES * 2 + 1)  # Time + Table columns
        practice_headers = ['Time'] + [f'Table {chr(65 + i // 2)}{i % 2 + 1}' for i in range(self.schedule_data.NUM_TABLES * 2)]
        self.practice_table.setHorizontalHeaderLabels(practice_headers)

        # Table Rounds Table
        self.table_round_table = QTableWidget()
        self.table_round_table.setColumnCount(self.schedule_data.NUM_TABLES * 2 + 1)  # Time + Table columns
        table_round_headers = ['Time'] + [f'Table {chr(65 + i // 2)}{i % 2 + 1}' for i in range(self.schedule_data.NUM_TABLES * 2)]
        self.table_round_table.setHorizontalHeaderLabels(table_round_headers)
        
        self.initialize_schedule_display(q_learning)
        self.setup_schedule_display()
    
    def initialize_schedule_display(self, q_learning):
        """Initializes the schedule display for the Q-learning scheduler."""
        schedule = q_learning.schedule
        
        # Ensure tables are clear and set up before populating
        self.clear_and_setup_tables()

        # Initialize a dictionary to track the last row used for each time in each table
        last_row = {'judging': {}, 'practice': {}, 'table': {}}

        # Create a color map to store unique colors for each team
        color_map = {}

        # Iterate over each entry in the sorted schedule
        for entry in sorted(schedule, key=lambda x: (x[0], x[2], x[4])):
            time_start, _, round_type, _, location_id, team_id = entry

            table_widget = self.get_table_widget(round_type)

            # If this time_start has not been used in this table, add a new row for it
            if time_start not in last_row[round_type]:
                newRow = table_widget.rowCount()
                table_widget.insertRow(newRow)
                table_widget.setItem(newRow, 0, QTableWidgetItem(time_start))  # Set the time in the first column
                last_row[round_type][time_start] = newRow

            row = last_row[round_type][time_start]

            # Calculate the column for this entry. Adjust get_col_index to fit your logic
            col = self.get_col_index(round_type, location_id)

            item = QTableWidgetItem(str(team_id))
            table_widget.setItem(row, col, item)

            # Generate a unique color for each team if not already in the color map
            if team_id not in color_map:
                hue = (len(color_map) * 0.618033988749895) % 1.0  # Golden ratio
                saturation = 0.5
                value = 0.85
                r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
                color = QColor.fromRgb(int(r * 255), int(g * 255), int(b * 255))
                color_map[team_id] = color
                                
            # Set the cell background color using QBrush
            item.setBackground(QBrush(color_map[team_id]))
        

    def setup_schedule_display(self): 
        """Sets up the schedule display for the Q-learning scheduler."""
        # Create a vertical splitter for arranging the schedule display
        schedule_splitter = QSplitter(Qt.Vertical)

        # Create the group box for the schedule display
        self.schedule_display_groupbox = QGroupBox("Schedule Display")
        self.schedule_layout = QVBoxLayout(self.schedule_display_groupbox)

        # Create the group box for the judging rounds display
        self.judging_display_groupbox = QGroupBox("Judging Rounds")
        self.judging_layout = QVBoxLayout(self.judging_display_groupbox)

        # Create the group box for the practice rounds display
        self.practice_display_groupbox = QGroupBox("Practice Rounds")
        self.practice_layout = QVBoxLayout(self.practice_display_groupbox)

        # Create the group box for the table rounds display
        self.table_display_groupbox = QGroupBox("Table Rounds")
        self.table_layout = QVBoxLayout(self.table_display_groupbox)

        # Add the judging table widget to the judging layout
        self.judging_layout.addWidget(self.judging_table)

        # Add the practice table widget to the practice layout
        self.practice_layout.addWidget(self.practice_table)

        # Add the table round table widget to the table layout
        self.table_layout.addWidget(self.table_round_table)

        # Add the judging display group box to the splitter
        schedule_splitter.addWidget(self.judging_display_groupbox)

        # Add the practice display group box to the splitter
        schedule_splitter.addWidget(self.practice_display_groupbox)

        # Add the table display group box to the splitter
        schedule_splitter.addWidget(self.table_display_groupbox)

        # Add the splitter to the schedule layout
        self.schedule_layout.addWidget(schedule_splitter)
    
    def clear_and_setup_tables(self):
        """Clears and sets up the judging, practice, and table round tables."""

        for table in [self.judging_table, self.practice_table, self.table_round_table]:
            table.clearContents()  # Clear the contents of the table
            table.setColumnCount(0)  # Clear the columns
            table.setRowCount(0)  # Clear the rows
            table.setAlternatingRowColors(True)  # Enable alternating row colors
            table.setEditTriggers(QTableWidget.NoEditTriggers)  # Disable editing

            if table is self.judging_table:
                # Set column count and header labels for judging table
                table.setColumnCount(self.schedule_data.NUM_ROOMS + 1)
                table.setHorizontalHeaderLabels(['Time'] + [f'Room {i+1}' for i in range(self.schedule_data.NUM_ROOMS)])
            else:
                # Set column count and header labels for practice and table round tables
                table.setColumnCount((self.schedule_data.NUM_TABLES * 2) + 1)
                table.setHorizontalHeaderLabels(['Time'] + [f'Table {chr(65 + i // 2)}{i % 2 + 1}' for i in range(self.schedule_data.NUM_TABLES * 2)])

    def get_table_widget(self, round_type):
        """Returns the table widget based on the round type."""
        if round_type == 'judging':
            return self.judging_table
        elif round_type == 'practice':
            return self.practice_table
        else:  # 'table'
            return self.table_round_table

    def get_col_index(self, round_type, location_id):
        """Returns the column index based on the round type and location ID."""
        if round_type == 'judging':
            return int(location_id)
        else:
            col_base = ord(location_id[0]) - ord('A') + 1
            col_offset = int(location_id[1])
            return (col_base - 1) * 2 + col_offset
