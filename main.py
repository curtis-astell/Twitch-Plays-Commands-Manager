import sys
import os
import re
import concurrent.futures
import pyautogui
import pydirectinput
import TwitchPlays_Connection
from TwitchPlays_KeyCodes import *
from functools import partial
from threading import Thread
from PyQt5.QtCore import Qt, QPropertyAnimation, pyqtSignal
from PyQt5.QtGui import QIcon, QMovie, QKeySequence, QCloseEvent
from PyQt5.QtWidgets import (QApplication, QMainWindow, QDialog,
                             QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QSplitter, QFrame,
                             QGridLayout, QComboBox, QWidget,
                             QHBoxLayout, QScrollArea, QFileDialog,
                             QTableWidget, QTableWidgetItem, QPlainTextEdit,
                             QShortcut)


# Login Window prompts user for basic stream info and determines the type of stream
class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        # Layout manager for Login Window
        layout = QVBoxLayout()

        # Login window properties
        self.setLayout(layout)
        self.setWindowTitle('Twitch Plays')
        self.setWindowIcon(QIcon('Assets/twitchicon.png'))
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.setFixedSize(325, 210)

        # Login window animated background
        label = QLabel(self)
        background = QMovie("Assets/login_background.gif")
        label.setMovie(background)
        label.setFixedSize(325, 210)
        background.start()

        # Checks settings text file to fill login window with previously used info
        with open("Settings/settings.txt", 'r') as f:
            lines = f.readlines()
            self.twitch_channel = str(lines[7])
            self.twitch_channel.strip()
            self.youtube_id = str(lines[9])
            self.youtube_id.strip()
            self.youtube_url = str(lines[11])
            self.youtube_url.strip()

        # Splitter to organize separate stream connections
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(0)
        layout.addWidget(splitter)

        # Twitch login properties
        twitch_section = QVBoxLayout()  # Adds twitch section to layout manager
        login_introduction = QLabel("Welcome! To begin, enter \n"
                                    "the info for the type of\n"
                                    "livestream you're hosting.\n"
                                    "\n"
                                    "Check the README file for\n"
                                    "additional instructions.")
        login_introduction.setStyleSheet("color: white")
        twitch_section.addWidget(login_introduction)
        twitch_label = QLabel('• Twitch Channel')  # Label for Twitch channel text entry
        twitch_label.setStyleSheet("color: white")
        twitch_section.addWidget(twitch_label)

        # Twitch channel text entry
        # Twitch channel name is necessary to connect program to twitch stream
        self.twitch_channel_edit = QLineEdit(self.twitch_channel)
        self.twitch_channel_edit.setToolTip("Enter Twitch Channel Name")
        twitch_section.addWidget(self.twitch_channel_edit)

        # Sets stream type to Twitch
        self.twitch_login = QPushButton('Connect Twitch Stream')
        twitch_section.addWidget(self.twitch_login)
        self.twitch_login.clicked.connect(self.twitch_login_clicked)  # Connects push button to function

        # Assigns twitch section to left of splitter
        left_frame = QFrame()
        left_frame.setLayout(twitch_section)
        splitter.addWidget(left_frame)

        # YouTube login properties
        youtube_section = QVBoxLayout()  # Add YouTubes section to layout manager
        yt_id_label = QLabel('• Youtube Channel ID')  # Label for YouTube ID text entry
        yt_id_label.setStyleSheet("color: white")
        youtube_section.addWidget(yt_id_label)

        # YouTube ID text entry
        self.youtube_id_edit = QLineEdit(self.youtube_id)
        self.youtube_id_edit.setToolTip("Enter YouTube Channel ID\n"
                                        "Find this by clicking YouTube profile pic -> Settings -> Advanced Settings")

        # YouTube Channel ID is necessary to connect program to YouTube stream
        # Find this by clicking your YouTube profile pic -> Settings -> Advanced Settings
        youtube_section.addWidget(self.youtube_id_edit)
        yt_url_label = QLabel('• Youtube Stream URL')  # Label for YouTube stream URL text entry
        yt_url_label.setStyleSheet("color: white")
        youtube_section.addWidget(yt_url_label)

        # YouTube stream URL text entry
        self.youtube_url_edit = QLineEdit(self.youtube_url)
        self.youtube_url_edit.setToolTip('Enter stream URL to test an unlisted stream\n'
                                         'Can be left as "None" otherwise')

        # User can enter their stream URL to test an unlisted stream
        # Otherwise can be left as "None"
        youtube_section.addWidget(self.youtube_url_edit)

        # Sets stream type to YouTube
        self.youtube_login = QPushButton("Connect YouTube Stream")
        youtube_section.addWidget(self.youtube_login)
        self.youtube_login.clicked.connect(self.youtube_login_clicked)  # Connects push button to function

        # Assigns YouTube section to right of splitter
        right_frame = QFrame()
        right_frame.setLayout(youtube_section)
        splitter.addWidget(right_frame)

        # Initialize streaming_twitch variable
        # Will be used to determine stream type
        self.streaming_twitch = None

    # Sets streaming_twitch variable to True and opens main window
    def twitch_login_clicked(self):
        self.streaming_twitch = True
        # Adds items entered in LoginWindow to settings.txt for later
        with open("Settings/settings.txt", "r+") as f:
            lines = f.readlines()

            lines[7] = "{}\n".format(self.twitch_channel_edit.text().strip().lower())
            lines[9] = "{}\n".format(self.youtube_id_edit.text().strip())
            lines[11] = "{}\n".format(self.youtube_url_edit.text().strip())

            f.seek(0)

            f.writelines(lines)

            f.truncate()

        self.accept()

    # Sets streaming_twitch variable to False and opens main window
    def youtube_login_clicked(self):
        self.streaming_twitch = False
        # Adds items entered in LoginWindow to settings.txt for later
        with open("Settings/settings.txt", "r+") as f:
            lines = f.readlines()

            lines[7] = "{}\n".format(self.twitch_channel_edit.text().strip().lower())
            lines[9] = "{}\n".format(self.youtube_id_edit.text().strip())
            lines[11] = "{}\n".format(self.youtube_url_edit.text().strip())

            f.seek(0)

            f.writelines(lines)

            f.truncate()

        self.accept()

# Options Window lets user edit some basic stream settings
class OptionsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Window Properties
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.setStyleSheet("background-color: #1e1e1e;")
        self.setWindowTitle("Options")
        self.setWindowIcon(QIcon("Assets/twitchicon.png"))
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)

        # Fetches stream settings from settings file
        with open("Settings/settings.txt", 'r') as f:
            lines = f.readlines()
            self.message_rate = float(lines[1])
            self.queue_length = int(lines[3])
            self.max_workers = int(lines[5])

        # Splitter to organize information
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(0)
        main_layout.addWidget(splitter)

        # Labels on left side
        label_section = QVBoxLayout()
        stream_settings_label = QLabel("Stream Settings")
        stream_settings_label.setStyleSheet('text-decoration: underline; color: white')
        label_section.addWidget(stream_settings_label)
        msg_rate_label = QLabel("• Message Rate:")
        msg_rate_label.setStyleSheet("color: white;")
        label_section.addWidget(msg_rate_label)
        queue_length_label = QLabel("• Max Queue Length:")
        queue_length_label.setStyleSheet("color: white;")
        label_section.addWidget(queue_length_label)
        workers_label = QLabel("• Max Workers:")
        workers_label.setStyleSheet("color: white;")
        label_section.addWidget(workers_label)
        invisible_spacer_left = QLabel("")
        label_section.addWidget(invisible_spacer_left)

        # Stores labels to QFrame and places frame to the left of the splitter
        left_frame = QFrame()
        left_frame.setLayout(label_section)
        splitter.addWidget(left_frame)

        # Options text entry on right side
        data_section = QVBoxLayout()
        invisible_spacer_right = QLabel("")
        invisible_spacer_right.setFixedHeight(25) # Adjusted spacer height to fix alignment
        data_section.addWidget(invisible_spacer_right)
        self.message_rate_edit = QLineEdit("{}".format(self.message_rate))
        self.message_rate_edit.setStyleSheet("background-color: white;")
        self.message_rate_edit.setToolTip("This controls how fast the program will process\n"
                                          "incoming Twitch Chat messages.\n"
                                          "Smaller = Faster")
        data_section.addWidget(self.message_rate_edit)
        self.queue_length_edit = QLineEdit("{}".format(self.queue_length))
        self.queue_length_edit.setStyleSheet("background-color: white;")
        self.queue_length_edit.setToolTip('This limits the number of commands that will\n'
                                          'be processed in a given "batch" of messages.')
        data_section.addWidget(self.queue_length_edit)
        self.max_workers_edit = QLineEdit("{}".format(self.max_workers))
        self.max_workers_edit.setStyleSheet("background-color: white;")
        self.max_workers_edit.setToolTip("This is the maximum number of threads that can be processed at a time.")
        data_section.addWidget(self.max_workers_edit)
        save_button = QPushButton("Save and Apply")
        save_button.setStyleSheet("background-color: #333333; color: white;")
        data_section.addWidget(save_button)

        # Stores button and text entry to QFrame and places frame to right of splitter
        right_frame = QFrame()
        right_frame.setLayout(data_section)
        splitter.addWidget(right_frame)

        save_button.clicked.connect(self.save_settings_clicked)

    # Clicking save writes settings to text file and closes Options Window
    def save_settings_clicked(self):
        try:
            with open("Settings/settings.txt", "r+") as f:
                lines = f.readlines()
                lines[1] = "{}\n".format(float(self.message_rate_edit.text()))
                lines[3] = "{}\n".format(int(self.queue_length_edit.text()))
                lines[5] = "{}\n".format(int(self.max_workers_edit.text()))
                f.seek(0)
                f.writelines(lines)
                f.truncate()
                self.accept()
        # Floats and ints only so that the user can't break their stream and then blame me for it
        except ValueError:
            return

# Opens window prompting user for a title before adding game to the grid
class AddGameWindow(QDialog):
    def __init__(self, streaming_twitch, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.setWindowTitle("Add New Game")
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)

        self.parent = parent

        self.streaming_twitch = streaming_twitch

        # Grabs settings from text file for the purposes of refreshing the MainWindow
        with open("Settings/settings.txt", 'r') as f:
            lines = f.readlines()
            self.twitch_channel = str(lines[7])
            self.twitch_channel.strip()
            self.youtube_id = str(lines[9])
            self.youtube_id.strip()
            self.youtube_url = str(lines[11])
            self.youtube_url.strip()

        add_label = QLabel("Enter new game title:")
        add_label.setStyleSheet("color: white;")
        main_layout.addWidget(add_label)
        self.title_entry = QLineEdit()
        self.title_entry.setStyleSheet("background-color: white;")
        main_layout.addWidget(self.title_entry)
        # Error label is empty and set to height 0 unless an error message is needed
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: white;")
        self.error_label.setFixedHeight(0)
        main_layout.addWidget(self.error_label)
        add_button = QPushButton("Add Game")
        add_button.setStyleSheet("background-color: #444444; color: white;")
        main_layout.addWidget(add_button)

        add_button.clicked.connect(self.add_button_clicked)

    # Button adds new game to grid and creates necessary text files
    def add_button_clicked(self, new_title):
        self.new_title = self.title_entry.text()
        try:
            # Game grid title can't have invalid characters because of file i/o
            assert all(char not in self.new_title for char in "\\/:*?\"<>|")
            with open("Grid Info/game_grid", "r+") as f:
                lines = f.readlines()
                # Prevents user from adding duplicates of the same game
                if self.new_title + "\n" in lines:
                    self.error_label.setText("Whoops! That title already exists!")
                    self.error_label.setFixedHeight(15)
                    return
                else:
                    index = len(lines) + 1
                    # Iterates over all items in grid_info.txt and adds the new title to the last unused line
                    try:
                        lines[index].write(self.new_title + "\n")
                    # If no new line is available makes room for one
                    except IndexError:
                        lines.append(self.new_title + "\n")
                    f.seek(0)
                    f.writelines(lines)
                # If the title entered is valid creates the following text files
                with open("Grid Info/Game Commands/{} Commands List.txt".format(self.new_title), "w") as f:
                    f.write("Command1\n*///\n*///\n*///\n*///\n*///\n*///\n*///\n*///\n*///\n*///\n")
                with open("Grid Info/{} Cover Art.txt".format(self.new_title), "w") as f:
                    f.write("url(C:/Dev/TwitchPlays/Cover Art/default_controller.png);")

            # Creates a new instance of the MainWindow class and closes the old one to display new information.
            self.updated_window = MainWindow(self.streaming_twitch, self.twitch_channel,
                                             self.youtube_id, self.youtube_url)
            self.parent.close()
            self.accept()
        except AssertionError:
            # Error message in case of invalid characters
            self.error_label.setText("Invalid title, please try again.")
            self.error_label.setFixedHeight(15)
            pass

# Prompts the user to enter a new title for a selected game
class ChangeTitleWindow(QDialog):
    def __init__(self, game_title):
        super().__init__()
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        self.setWindowTitle("Change Title")
        self.setWindowIcon(QIcon("Assets/twitchicon.png"))
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.setStyleSheet("background-color: #313131;")

        self.old_title = game_title
        title_label = QLabel("Enter new title:")
        title_label.setStyleSheet("color: white;")
        main_layout.addWidget(title_label)
        self.title_entry = QLineEdit(self.old_title)
        self.title_entry.setStyleSheet("background-color: white;")
        main_layout.addWidget(self.title_entry)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: white;")
        self.error_label.setFixedHeight(0)
        main_layout.addWidget(self.error_label)
        apply_button = QPushButton("Save and Apply")
        apply_button.setStyleSheet("background-color: #434343; color: white;")
        main_layout.addWidget(apply_button)

        apply_button.clicked.connect(self.apply_clicked)

    def apply_clicked(self):
        try:
            self.new_title = self.title_entry.text()
            assert self.new_title != "" and all(char not in self.new_title for char in "\\/:*?\"<>|")
            with open("Grid Info/game_grid", "r+") as f:
                lines = f.readlines()
                index = lines.index("{}\n".format(self.old_title))
                f.seek(0)
                for i, line in enumerate(lines):
                    if i != index:
                        f.write(line)
                    else:
                        f.write("{}\n".format(self.new_title))
                f.truncate()
            os.rename("Grid Info/Game Commands/{} Commands List.txt".format(self.old_title),
                      "Grid Info/Game Commands/{} Commands List.txt".format(self.new_title))
            os.rename("Grid Info/{} Cover Art.txt".format(self.old_title),
                      "Grid Info/{} Cover Art.txt".format(self.new_title))
            self.accept()
        except AssertionError:
            self.error_label.setText("Invalid title, please try again")
            self.error_label.setFixedHeight(15)
            pass


# Commands Window lets the user adjust commands for different games
class CommandsWindow(QDialog):
    def __init__(self, game_title):
        super().__init__()
        # Window properties
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)
        self.setWindowTitle("{} Commands Manager".format(game_title))
        self.setWindowIcon(QIcon("Assets/twitchicon.png"))
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)
        self.setStyleSheet("background-color: #313131")
        self.setFixedSize(600, 420)

        # Splitter to separate tables from save button
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(0)
        main_layout.addWidget(splitter)

        # Button section just holds save button and a note
        buttons_section = QHBoxLayout()
        save_button = QPushButton("Save Commands")
        save_button.setFixedSize(100, 30)
        save_button.setStyleSheet("background-color: #434343; color: white;")
        buttons_section.addWidget(save_button)
        invisible_spacer = QLabel("")
        invisible_spacer.setFixedWidth(35)
        buttons_section.addWidget(invisible_spacer)
        save_note = QLabel("•   Be sure to click the Save button before clicking through other commands!")
        save_note.setStyleSheet("color: white;")
        save_note.setFixedSize(500, 30)
        buttons_section.addWidget(save_note)

        # QFrame holds button section above splitter
        top_frame = QFrame()
        top_frame.setLayout(buttons_section)
        splitter.addWidget(top_frame)

        table_style = """
            QHeaderView::section {
                background-color: #434343;
                color: white;
                padding: 1px;
            }
            QTableWidget {
                background-color: #313131;
                alternate-background-color: #white;
                color: white;
                alternate-color: black;
                gridline-color: #666666;
            }
            QTableCornerButton::section {
                background-color: #434343;
            }
        """

        # Commands section holds messages list and associated data in two separate tables
        commands_section = QHBoxLayout()

        # Commands_list holds a list of recognized messages
        self.commands_list = QTableWidget(50, 1)
        self.commands_list.setHorizontalHeaderLabels(["Message"])
        self.commands_list.setFixedSize(125, 330)
        self.commands_list.setStyleSheet(table_style)
        commands_section.addWidget(self.commands_list)

        # Fetches list of commands from text file
        with open("Grid Info/Game Commands/{} Commands List.txt".format(game_title), "r") as f:
            lines = f.readlines()
            last_index = -1  # initialize to -1 to add the first item to index 0
            for line in lines:
                if line.startswith("*"): # Lines that start with * are for data, not recognized messages
                    continue
                last_index += 1  # increment the index for each non-skipped line
                item = line.strip()
                table_item = QTableWidgetItem()
                table_item.setText(item)
                self.commands_list.setItem(last_index, 0, table_item)

        # Commands_table holds previously mentioned data for each recognized message
        self.commands_table = QTableWidget(10, 4)
        self.commands_table.setHorizontalHeaderLabels(["Type", "Keystroke", "Duration", "Direction"])
        self.commands_table.setFixedSize(430, 330)
        self.commands_table.setStyleSheet(table_style)
        commands_section.addWidget(self.commands_table)

        # Sets first column to be a combo box of possible command types
        for row in range(self.commands_table.rowCount()):
            command_type_selection = QComboBox()
            command_type_selection.addItems(["", "Press Key", "Hold Key", "Release Key", "Move Mouse"])
            command_type_selection.setStyleSheet("color: white")
            self.commands_table.setCellWidget(row, 0, command_type_selection)

        # QFrame holds commands tables beneath splitter
        bottom_frame = QFrame()
        bottom_frame.setLayout(commands_section)
        splitter.addWidget(bottom_frame)

        # Every time the user clicks a message type in the commands list, loads associated data
        self.commands_list.itemSelectionChanged.connect(lambda: self.load_table(game_title))
        # Connects save button to save function
        save_button.clicked.connect(lambda: self.save_commands(game_title))

        # Sets selected message to first cell in the list by default every time commands manager is opened
        self.commands_list.setCurrentCell(0, 0)

    # Load function that is called when the user clicks a message in the commands list
    def load_table(self, game_title):
        # Clear the contents first to reset the listed data
        self.commands_table.clearContents()
        # Sets the first column to be combo boxes of command types again
        for row in range(self.commands_table.rowCount()):
            command_type_selection = QComboBox()
            command_type_selection.addItems(["", "Press Key", "Hold Key", "Release Key", "Move Mouse"])
            command_type_selection.setStyleSheet("color: white")
            self.commands_table.setCellWidget(row, 0, command_type_selection)
        selected_item = self.commands_list.currentItem()
        if selected_item is None:
            return
        message = selected_item.text()
        row = 0
        # Goes into text file to fetch associated data for recognized command
        with open("Grid Info/Game Commands/{} Commands List.txt".format(game_title), "r+") as f:
            lines = f.readlines()
            try:
                start_index = lines.index("{}\n".format(message)) # Sets index to position of recognized command
            # If it can't find the selected command in the file, doesn't load any data instead of just crashing
            except ValueError:
                pass
            else:
                end_index = len(lines)
                for i in range(start_index + 1, len(lines)):
                    # Lines with associated data start with "*"
                    # If the program reaches a line without a "*", it means it's now reading a new command
                    # Therefore, it's read all the associated data and the loop can break
                    if not lines[i].startswith("*"):
                        end_index = i
                        break
                # Grabs the lines in the newly established range and fetches necessary data
                for i in range(start_index + 1, end_index):
                    cmd_data = lines[i].strip("*").strip() # Gets rid of "*" and newline character
                    cmd_items = cmd_data.split("/") # Splits up command items in each line by "/"
                    command_type = cmd_items[0] # First line before "/" is for command types
                    row_combobox = self.commands_table.cellWidget(row, 0)
                    row_combobox.setCurrentText(command_type) # Sets that rows combo box to associated command type
                    # For the rest of the row sets up other data from the line into the appropriate cells of the table
                    for column, cell_data in enumerate(cmd_items[1:]):
                        item = QTableWidgetItem(cell_data)
                        self.commands_table.setItem(row, column + 1, item)
                    row += 1

    # Save function to write modified commands to the commands text file for later
    def save_commands(self, game_title):
        # Write each item in the commands_list table to the text file
        with open("Grid Info/Game Commands/{} Commands List.txt".format(game_title), "r+") as f:
            lines = f.readlines()
            # If the amount of lines in the text file is shorter than the list of recognized commands,
            # Adds an additional 11 lines to the text file.
            # Each recognized command will have 1 message name and 10 possible rows of instructions, hence 11
            while len(lines) < self.commands_list.rowCount() * 11:
                lines.append('')
            list_index = 0
            for i in range(self.commands_list.rowCount()):
                item = self.commands_list.item(i, 0)
                if item is not None and item.text() != "":
                    lines[list_index] = "{}\n".format(item.text())
                    if list_index + 1 >= len(lines):
                        lines.append("\n")
                    next_line = lines[list_index + 1]
                    if '*' not in next_line:
                        for j in range(list_index + 1, list_index + 11):
                            if j >= len(lines):
                                lines.append("*///\n")
                            else:
                                lines[j] = "*///\n"
                else:
                    break
                list_index += 11
            f.seek(0)
            f.writelines(lines)

        selected_item = self.commands_list.currentItem()
        try:
            message = selected_item.text()
        except AttributeError:
            return
        with open("Grid Info/Game Commands/{} Commands List.txt".format(game_title), "r+") as f:
            lines = f.readlines()
            try:
                table_index = lines.index("{}\n".format(message)) + 1
            except ValueError:
                return
            for i in range(self.commands_table.rowCount()):
                command_type = self.commands_table.cellWidget(i, 0).currentText()
                if self.commands_table.item(i, 1) is not None:
                    keystroke = self.commands_table.item(i, 1).text()
                else:
                    keystroke = ""
                if self.commands_table.item(i, 2) is not None:
                    duration = self.commands_table.item(i, 2).text()
                else:
                    duration = ""
                if self.commands_table.item(i, 3) is not None:
                    direction = self.commands_table.item(i, 3).text()
                else:
                    direction = ""
                try:
                    lines[table_index] = ("*{}/{}/{}/{}\n".format(command_type, keystroke, duration, direction))
                except AttributeError:
                    break  # exit the loop if an empty cell is encountered
                table_index += 1
            f.seek(0)  # reset file pointer to start of file
            f.writelines(lines)  # write modified lines back to file
            f.truncate()


class LinkStreamWindow(QWidget):
    text_updated = pyqtSignal(str)

    def __init__(self, main_window, streaming_twitch, game_title):
        super().__init__()
        self.main_window = main_window

        self.streaming_twitch = streaming_twitch
        self.game_title = game_title

        self.setStyleSheet("background-color: black")

        self.setWindowTitle("Stream Link")

        self.setWindowIcon(QIcon("Assets/link.png"))
        self.cmd_widget = QPlainTextEdit(self)
        self.cmd_widget.setStyleSheet("background-color: black; color: white; border: 1px black;")
        self.cmd_widget.setWindowFlags(Qt.FramelessWindowHint)
        self.cmd_widget.setReadOnly(True)

        layout = QVBoxLayout()
        layout.addWidget(self.cmd_widget)
        self.setLayout(layout)

        self.stream_connected = True

        with open('Settings/settings.txt', 'r') as f:
            settings = f.readlines()
            self.message_rate = float(settings[1].strip())
            self.queue_length = int(settings[3].strip())
            self.max_workers = int(settings[5].strip())
            self.twitch_channel = str(settings[7].strip())
            self.youtube_id = str(settings[9].strip())
            self.youtube_url = str(settings[11].strip())

        if self.youtube_url == "None":
            self.youtube_url = None

        self.thread = Thread(target=self.run_loop)
        self.thread.start()

        self.text_updated.connect(self.cmd_widget.appendPlainText)

        unlink_stream = QShortcut(QKeySequence(Qt.SHIFT + Qt.Key_Backspace), self)
        unlink_stream.activated.connect(self.close)

    def run_loop(self):
        last_time = time.time()
        message_queue = []
        thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        active_tasks = []
        pyautogui.FAILSAFE = False

        if self.streaming_twitch:
            t = TwitchPlays_Connection.Twitch(self.append_text)
            t.twitch_connect(self.twitch_channel)
        else:
            t = TwitchPlays_Connection.YouTube(self.append_text)
            t.youtube_connect(self.youtube_id, self.youtube_url)

        while self.stream_connected:
            active_tasks = [t for t in active_tasks if not t.done()]

            new_messages = t.twitch_receive_messages()
            if new_messages:
                message_queue += new_messages  # New messages are added to the back of the queue
                message_queue = message_queue[
                                -self.queue_length:]  # Shorten the queue to only the most recent X messages

            messages_to_handle = []
            if not message_queue:
                # No messages in the queue
                last_time = time.time()
            else:
                # Determine how many messages we should handle now
                r = 1 if self.message_rate == 0 else (time.time() - last_time) / self.message_rate
                n = int(r * len(message_queue))
                if n > 0:
                    # Pop the messages we want off the front of the queue
                    messages_to_handle = message_queue[0:n]
                    del message_queue[0:n]
                    last_time = time.time()

            if not messages_to_handle:
                pass
            else:
                for message in messages_to_handle:
                    if len(active_tasks) <= self.max_workers:
                        active_tasks.append(thread_pool.submit(self.handle_message, message, self.game_title))
                    else:
                        self.append_text(
                            f'WARNING: active tasks ({len(active_tasks)}) exceeds number of workers ({self.max_workers}). '
                            f''f'({len(message_queue)} messages in the queue)')

    def append_text(self, text):
        self.text_updated.emit(text)

    def closeEvent(self, event):
        self.stream_connected = False
        self.main_window.show()
        super().closeEvent(event)

    def close(self):
        self.closeEvent(QCloseEvent())

    def handle_message(self, message, game_title):
        try:
            msg = message['message'].lower()
            username = message['username'].lower()

            self.append_text("Got this message from " + username + ": " + msg)

            with open("Grid Info/Game Commands/{} Commands List.txt".format(game_title), "r") as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if line.startswith("*"):
                        continue
                    if msg == line.strip():
                        try:
                            for j in range(i + 1, i + 11):
                                if j >= len(lines):
                                    break
                                parts = lines[j].strip().split("/")
                                if re.search(r'\bPress Key\b', lines[j]):
                                    keystroke_name = parts[1].upper()
                                    if keystroke_name in keycodes:
                                        keystroke = keycodes[keystroke_name]
                                        duration = parts[2]
                                        HoldAndReleaseKey(keystroke, float(duration))
                                    else:
                                        self.append_text(f"Keystroke {keystroke_name} invalid")
                                elif re.search(r'\bHold Key\b', lines[j]):
                                    keystroke_name = parts[1].upper()
                                    if keystroke_name in keycodes:
                                        keystroke = keycodes[keystroke_name]
                                        HoldKey(keystroke)
                                    else:
                                        self.append_text(f"Keystroke {keystroke_name} invalid")
                                elif re.search(r'\bRelease Key\b', lines[j]):
                                    keystroke_name = parts[1].upper()
                                    if keystroke_name in keycodes:
                                        keystroke = keycodes[keystroke_name]
                                        ReleaseKey(keystroke)
                                    else:
                                        self.append_text(f"Keystroke {keystroke_name} invalid")
                                elif re.search(r'\bMove Mouse\b', lines[j]):
                                    duration = int(parts[2])
                                    if parts[3] == "up":
                                        direction_x = 0
                                        direction_y = -duration
                                    elif parts[3] == "left":
                                        direction_x = -duration
                                        direction_y = 0
                                    elif parts[3] == "right":
                                        direction_x = duration
                                        direction_y = 0
                                    elif parts[3] == "down":
                                        direction_x = 0
                                        direction_y = duration
                                    pydirectinput.moveRel(direction_x, direction_y, relative=True)
                                else:
                                    break
                        except StopIteration:
                            self.append_text("Error")


        except Exception as e:
            self.append_text("Encountered exception: " + str(e))


# Main window features a grid of games, with associated information for twitch commands and other variables
class MainWindow(QMainWindow):
    def __init__(self, streaming_twitch, twitch_channel, youtube_id, youtube_url):
        super().__init__()
        # Basic window properties
        self.setWindowTitle('Twitch Plays')
        self.setWindowIcon(QIcon('Assets/twitchicon.png'))
        self.move(0, 0)
        self.setStyleSheet("background-color: #313131;")
        self.setMinimumSize(1920, 1080)
        self.showMaximized()

        # Incorporating established variables from login window
        self.streaming_twitch = streaming_twitch
        self.twitch_channel = twitch_channel
        self.youtube_id = youtube_id
        self.youtube_url = youtube_url

        with open('Settings/settings.txt', 'r') as f:
            settings = f.readlines()
            self.message_rate = float(settings[1].strip())
            self.queue_length = int(settings[3].strip())
            self.max_workers = int(settings[5].strip())

        # Establishing layout settings for the grid of games
        self.game_grid = QGridLayout()
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.game_grid)
        self.setCentralWidget(self.central_widget)

        # Creates a window scroll bar
        scroll_area = QScrollArea()
        scroll_area.setWidget(self.central_widget)
        scroll_area.setWidgetResizable(True)
        self.setCentralWidget(scroll_area)

        # Reserves row 0 of grid for settings button
        top_widget = QWidget()
        self.game_grid.addWidget(top_widget, 0, 0, 1, 5)

        # Settings area in top left of window
        options_section = QFrame(self)
        options_section.setStyleSheet("background-color: #313131")
        options_section.setFixedSize(342, 50)
        self.game_grid.addWidget(options_section, 0, 0)

        options_layout = QHBoxLayout(options_section)
        options_button = QPushButton("Options", self)
        options_button.setFixedSize(100, 30)
        options_button.setStyleSheet("background-color: #444444; color: white")
        options_layout.addWidget(options_button)

        add_game = QPushButton("Add Game", self)
        add_game.setFixedSize(100, 30)
        add_game.setStyleSheet("background-color: #444444; color: white")
        options_layout.addWidget(add_game)

        invisible_spacer = QLabel("")
        invisible_spacer.setFixedSize(100, 50)
        options_layout.addWidget(invisible_spacer)

        # Close window button in top right
        refresh_frame = QFrame(self)
        refresh_frame.setStyleSheet("background-color: #313131")
        refresh_frame.setFixedSize(342, 50)
        self.game_grid.addWidget(refresh_frame, 0, 4)

        invisible_spacer2 = QLabel("")
        invisible_spacer2.setFixedSize(200, 50)

        refresh_layout = QHBoxLayout(refresh_frame)
        refresh_layout.addWidget(invisible_spacer2)

        refresh_button = QPushButton("Refresh Window", self)
        refresh_button.setFixedSize(100, 30)
        refresh_button.setStyleSheet("background-color: #444444; color: white")
        refresh_layout.addWidget(refresh_button)

        options_button.clicked.connect(self.open_options)
        add_game.clicked.connect(self.add_game)
        refresh_button.clicked.connect(self.refresh_clicked)

        self.createGrid()

    def open_options(self):
        settings_dialog = OptionsWindow(self)
        settings_dialog.exec_()

    def add_game(self):
        add_dialog = AddGameWindow(self.streaming_twitch, parent=self)
        add_dialog.exec_()

    def refresh_clicked(self):
        self.updated_window = MainWindow(self.streaming_twitch, self.twitch_channel, self.youtube_id, self.youtube_url)
        self.close()


    # Function to create grid of games
    def createGrid(self):
        # Reads the self.game_grid text file and retrieves list of titles
        with open('Grid Info/game_grid', 'r') as f:
            game_list = f.readlines()
        row = 1  # Row 0 is reserved for settings button
        col = 0
        # Grid info folder will hold text files with a games associated information
        # These text files are used to retrieve game cover art and a list of commands
        grid_folder = "Grid Info"
        os.makedirs(grid_folder, exist_ok=True)

        # For loop to create text files and populate the grid info folder
        for i, line in enumerate(game_list):
            line = line.strip()
            art_file_name = os.path.join(grid_folder, "{} Cover Art.txt".format(line))  # Cover art file
            commands_file_name = os.path.join("Grid Info/Game Commands/{} Commands List.txt".format(line))  # Commands file
            # If the file already exists, don't overwrite it. Otherwise, create the file
            if os.path.exists(art_file_name):
                pass
            else:
                with open(art_file_name, "w") as f:
                    f.write("url(Cover Art/default_controller.png);")  # Default generic image until user changes it
            if os.path.exists(commands_file_name):
                pass
            else:
                with open(commands_file_name, "w") as f:
                    f.write("")  # Game starts out with no usable commands
            # Removes invisible new line character from game title
            game_title = line.strip()
            game = QPushButton()
            # Retrieves artwork file directory from file
            with open(art_file_name, "r") as f:
                game_art = f.readline().strip()

            # Sets game artwork and tool tip
            game.setStyleSheet("background-image: {}".format(game_art))
            game.setToolTip(game_title)
            game.setFixedSize(342, 482)

            # Properties of game settings menu frame
            game.game_settings = QFrame()
            game.game_settings.setFixedHeight(0)
            game.game_settings.setFixedWidth(342)
            game.game_settings.setFrameStyle(QFrame.Panel | QFrame.Sunken)
            game.game_settings.setStyleSheet("background-color: #1e1e1e;")

            # Layout for menu frame
            game_settings_layout = QVBoxLayout(game.game_settings)

            game_settings_animation = QPropertyAnimation(game.game_settings, b"maximumHeight")
            game_settings_animation.setDuration(300)

            # Places game in grid
            self.game_grid.addWidget(game, row, col)
            # Places game settings in grid
            self.game_grid.addWidget(game.game_settings, row + 1, col)

            game_settings_splitter = QSplitter(Qt.Horizontal)
            game_settings_splitter.setHandleWidth(0)
            game_settings_layout.addWidget(game_settings_splitter)

            label_section = QVBoxLayout()
            button_section = QVBoxLayout()

            # Label Section on Left
            title_label = QLabel("{}".format(game_title))
            title_label.setStyleSheet("color: white;")
            label_section.addWidget(title_label)
            art_directory_length = len(game_art)
            settings_cover_label = QLabel("{}".format(game_art[4:art_directory_length - 2]))
            settings_cover_label.setStyleSheet("color: white;")
            label_section.addWidget(settings_cover_label)
            commands_label = QLabel("Chat Commands:")
            commands_label.setStyleSheet("color: white;")
            label_section.addWidget(commands_label)
            link_stream_label = QLabel("Link Game to Stream:")
            link_stream_label.setStyleSheet("color: white;")
            label_section.addWidget(link_stream_label)
            delete_label = QLabel("Delete Game:")
            delete_label.setStyleSheet("color: white;")
            label_section.addWidget(delete_label)

            # Button Section on Right
            change_title = QPushButton("Change Title")
            change_title.setStyleSheet("background-color: #434343; color: white;")
            change_title.setFixedWidth(103)
            button_section.addWidget(change_title)
            change_art = QPushButton("Change Art")
            change_art.setStyleSheet("background-color: #434343; color: white;")
            change_art.setFixedWidth(103)
            button_section.addWidget(change_art)
            commands_button = QPushButton("Modify Commands")
            commands_button.setStyleSheet("background-color: #434343; color: white;")
            commands_button.setFixedWidth(103)
            button_section.addWidget(commands_button)
            link_stream_button = QPushButton()
            link_stream_button.setFixedSize(103, 28)
            if self.streaming_twitch:
                link_stream_button.setStyleSheet("background-image: url(Assets/twitchlogo.png);")
            else:
                link_stream_button.setStyleSheet("background-image: url(Assets/youtubelogo.png);")
            button_section.addWidget(link_stream_button)
            delete_button = QPushButton("Delete")
            delete_button.setStyleSheet("background-color: #434343; color: white;")
            delete_button.setFixedWidth(103)
            button_section.addWidget(delete_button)

            left_frame = QFrame()
            left_frame.setLayout(label_section)
            game_settings_splitter.addWidget(left_frame)

            right_frame = QFrame()
            right_frame.setLayout(button_section)
            game_settings_splitter.addWidget(right_frame)

            game.clicked.connect(partial(self.game_clicked, game_title, game.game_settings, game_settings_animation))
            change_title.clicked.connect(partial(self.change_title_clicked, game_title))
            change_art.clicked.connect(partial(self.change_art_clicked, game_title, game))
            commands_button.clicked.connect(partial(self.commands_clicked, game_title))
            link_stream_button.clicked.connect(partial(self.connect_clicked, game_title))
            delete_button.clicked.connect(partial(self.delete_clicked, game_title))

            # Move one column to the right
            col += 1
            # If on the sixth placement, snap back to the left and descend 2 rows
            if col == 5:
                col = 0
                row += 2

    @staticmethod
    def game_clicked(title, settings, game_settings_animation):
        if settings.maximumHeight() == 0:
            # settings.show()
            game_settings_animation.setStartValue(0)
            game_settings_animation.setEndValue(settings.sizeHint().height())
        else:
            game_settings_animation.setStartValue(settings.sizeHint().height())
            game_settings_animation.setEndValue(0)

        game_settings_animation.start()

    @staticmethod
    def change_title_clicked(game_title):
        title_dialog = ChangeTitleWindow(game_title)
        title_dialog.exec_()

    def change_art_clicked(self, title, game):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Cover Art", "Cover Art", "PNG (*.png)",
                                                   options=options)
        if not file_name:
            return
        with open("Grid Info/{} cover art.txt".format(title), "w") as f:
            f.write("url({});".format(file_name))
        with open("Grid Info/{} cover art.txt".format(title), "r") as f:
            game_art = f.readline().strip()
            game.setStyleSheet("background-image: {}".format(game_art))

    @staticmethod
    def commands_clicked(game_title):
        commands_dialog = CommandsWindow(game_title)
        commands_dialog.exec_()

    def connect_clicked(self, game_title):
        self.cmd = LinkStreamWindow(self, self.streaming_twitch, game_title)
        self.cmd.show()
        self.hide()

    def delete_clicked(self, game_title):
        self.game_title = game_title
        with open("Grid Info/game_grid", "r+") as f:
            lines = f.readlines()
            index = lines.index("{}\n".format(self.game_title))
            f.seek(0)
            for i, line in enumerate(lines):
                if i != index:
                    f.write(line)
            f.truncate()
        if os.path.exists("Grid Info/Game Commands/{} Commands List.txt".format(self.game_title)):
            os.remove("Grid Info/Game Commands/{} Commands List.txt".format(self.game_title))
        if os.path.exists("Grid Info/{} Cover Art.txt".format(self.game_title)):
            os.remove("Grid Info/{} Cover Art.txt".format(self.game_title))
        new_window = MainWindow(self, self.twitch_channel, self.youtube_id, self.youtube_url)
        self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    if login_window.exec_() == QDialog.Accepted:
        TwitchPlays = MainWindow(login_window.streaming_twitch, login_window.twitch_channel,
                                 login_window.youtube_id, login_window.youtube_url)
        TwitchPlays.show()
        sys.exit(app.exec_())
