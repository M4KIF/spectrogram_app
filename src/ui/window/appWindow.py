# Here is the code responsible for displaying the
# content that is mandatory for running the application
# This is not a functional app, but only a graphical interface
# that the app will be implemented with



# Modules imports
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

# System Imports
import sys
import os


# Base directory global variable
basedir = os.path.dirname(__file__)



class appWindow(QMainWindow):
   def __init__(self, *args, **kwargs):

      #################################################
      # Base informations and data needed for runtime #
      #################################################

      # Contains the names of the filters
      self.list_of_filters = ["(default)", "cubic"]

      # Contains the names of window functions
      self.list_of_windows = []

      #######################################################
      # Initialising the appWindow with basic functionality #
      #######################################################

      super(appWindow, self).__init__(*args, **kwargs)

      # Setting the App title
      self.setWindowTitle("Spectrogram")

      # Adding the menu bar
      self.menu = self.menuBar()

      # Adding a toolbar and setting some defaults
      self.toolbar = QToolBar("Actions")
      self.toolbar.setIconSize(QSize(32,32))
      self.toolbar.setMovable(False)
      self.addToolBar(self.toolbar)
      self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

      # Adding a status bar
      self.statusbar = QStatusBar()
      self.setStatusBar(self.statusbar)
      self.statusbar.showMessage("show")

      ################################
      # Extending menu functionality #
      ################################

      # File menu
      self.fileMenu = self.menu.addMenu("File")
      # Edit menu
      self.editMenu = self.menu.addMenu("Edit")
      # View menu
      self.viewMenu = self.menu.addMenu("View")
      # Tools menu
      self.toolsMenu = self.menu.addMenu("Tools")
      # Help menu
      self.helpMenu = self.menu.addMenu("Help")

      ##############################
      # Creating File Actions #
      ##############################
      
      # New file button
      new_file_action = QAction(QIcon(os.path.join(basedir, "icons/application--plus.png")), "New File", self)
      new_file_action.setStatusTip("Creates a new empty file")
      new_file_action.triggered.connect(self.checkIfFileIsSaved)

      # Open file button
      open_file_action = QAction(QIcon(os.path.join(basedir, "icons/application--pencil.png")),"Open File", self)
      open_file_action.setStatusTip("Allows for searching a file to open")
      open_file_action.triggered.connect(self.openFileFromDirectory)

      # Save file with override
      save_file_action = QAction(QIcon(os.path.join(basedir, "icons/disk--pencil.png")), "Save File", self)
      save_file_action.setStatusTip("Saves the file with override")
      save_file_action.triggered.connect(self.saveFileWithCurrentName)
      
      # Save file as
      save_file_as_action = QAction(QIcon(os.path.join(basedir, "icons/disk--plus.png")), "Save As", self)
      save_file_as_action.setStatusTip("Saves the file without override")
      save_file_as_action.triggered.connect(self.saveFileWithAnotherName)

      # Save selected timestamp
      save_selected_section_action = QAction(QIcon(os.path.join(basedir, "icons/disk-rename.png")), "Save Selected Section", self)
      save_selected_section_action.setStatusTip("Saves the selected timestamp")
      save_selected_section_action.triggered.connect(self.saveFileWithSelectedTimestamp)

      # Save with separate channels
      save_separate_channels_action = QAction(QIcon(os.path.join(basedir, "icons/disks.png")), "Save Separate Audio Channels", self)
      save_separate_channels_action.setStatusTip("Saves the right and left channel in separate files")
      save_separate_channels_action.triggered.connect(self.saveAudioChannelsSeparately)

      #########################
      # Creating Edit Actions #
      #########################

      # Select Section
      select_section_action = QAction(QIcon(os.path.join(basedir, "icons/selection.png")), "Select Section", self)
      select_section_action.setStatusTip("Allows selection of timestamp of the file\nfor creating the graphs")
      select_section_action.triggered.connect(self.selectTimestamp)

      # Select Whole File
      select_all_action = QAction(QIcon(os.path.join(basedir, "icons/selection-select.png")), "Select All", self)
      select_all_action.setStatusTip("Allows selection of timestamp of the file\nfor creating the graphs")
      select_all_action.triggered.connect(self.selectTimestamp)


      #########################
      # Creating View Actions #
      #########################

      # Gives the choice of currently displayed channels
      show_left_channel_data_action = QAction("Left Channel", self)
      show_left_channel_data_action.setCheckable(True)
      show_left_channel_data_action.toggled.connect(self.showLeftChannelData)

      show_right_channel_data_action = QAction("Right Channel", self)
      show_right_channel_data_action.setCheckable(True)
      show_right_channel_data_action.toggled.connect(self.showRightChannelData)

      show_both_channels_data_action = QAction("All Channels", self)
      show_both_channels_data_action.setCheckable(True)
      show_both_channels_data_action.toggled.connect(self.showBothChannelData)

      # Shows the frequency response graph on the screen
      show_frequency_response_action = QAction("Frequency Response", self)
      show_frequency_response_action.setCheckable(True)
      show_frequency_response_action.toggled.connect(self.showFrequencyResponseGraph)

      # Shows the spectral power distribution graph
      show_spectral_power_distribution_action = QAction("Spectral Power Distribution", self)
      show_spectral_power_distribution_action.setCheckable(True)
      show_spectral_power_distribution_action.toggled.connect(self.showSpectralPowerDistribution)

      # Shows the spectrogram
      show_spectrogram_action = QAction("Spectrogram", self)
      show_spectrogram_action.setCheckable(True)
      show_spectrogram_action.toggled.connect(self.showSpectrogram)

      ##########################
      # Creating Tools Actions #
      ##########################

      ## Filters

      # default filter()
      set_default_filter_action = QAction("(default)", self)
      set_default_filter_action.setStatusTip("Default filter")
      set_default_filter_action.triggered.connect(self.setDefaultFilter)

      ## Player

      # Plays the track
      track_play_action = QAction(QIcon(os.path.join(basedir, "icons/control.png")), "Play", self)
      track_play_action.setStatusTip("Play the current audio track")
      track_play_action.triggered.connect(self.playTrack)

      # Pauses the track
      track_pause_action = QAction(QIcon(os.path.join(basedir, "icons/control-pause.png")), "Pause", self)
      track_pause_action.setStatusTip("Stops the current audio track")
      track_pause_action.triggered.connect(self.pauseTrack)

      # Stops the playback and resets to the start of the track
      track_stop_action = QAction(QIcon(os.path.join(basedir, "icons/control-stop-square.png")), "Stop", self)
      track_stop_action.setStatusTip("Stops and resets the playback")
      track_stop_action.triggered.connect(self.stopTrack)

      # Fast Forwards the track
      track_fast_forward_action = QAction(QIcon(os.path.join(basedir, "icons/control-double.png")), "Fast Forward", self)
      track_fast_forward_action.setStatusTip("Fast forwards the track")
      track_fast_forward_action.triggered.connect(self.trackFastForward)

      # Rewind the track
      track_rewind_action = QAction(QIcon(os.path.join(basedir, "icons/control-double-180.png")), "Rewind", self)
      track_rewind_action.setStatusTip("Rewinds the track")
      track_rewind_action.triggered.connect(self.trackRewind)

      ## Recorder

      # Start recording audio
      recording_action = QAction(QIcon(os.path.join(basedir, "icons/control-pause-record.png")), "Start recording", self)
      recording_action.setStatusTip("Starts the recording")
      recording_action.setCheckable(True)
      recording_action.triggered.connect(self.startOrStopAudioRecording)


      # Percentile coverage
      percentile_coverage = QAction()

      ## Window functions
      rectangular_window_function_action = QAction("Rectangular", self)
      rectangular_window_function_action.setStatusTip("Selects a rectangular window")
      rectangular_window_function_action.triggered.connect(self.setRectangularWindowFunction)      

      ##############################
      # Creating Help Actions #
      ##############################



      #######################################
      # Connecting actions to the file menu #
      #######################################

      self.fileMenu.addAction(new_file_action)
      self.fileMenu.addSeparator()
      self.fileMenu.addAction(open_file_action)
      self.fileMenu.addSeparator()
      self.fileMenu.addAction(save_file_action)
      self.fileMenu.addAction(save_file_as_action)
      self.fileMenu.addAction(save_selected_section_action)
      self.fileMenu.addAction(save_separate_channels_action)

      #######################################
      # Connecting actions to the edit menu #
      #######################################

      self.editMenu.addAction(select_section_action)
      self.editMenu.addSeparator()
      self.editMenu.addAction(select_all_action)

      #######################################
      # Connecting actions to the view menu #
      #######################################
      
      # Displayed channels submenu
      displayed_channels_submenu = self.viewMenu.addMenu("Channels")
      displayed_channels_submenu.addAction(show_left_channel_data_action)
      displayed_channels_submenu.addAction(show_right_channel_data_action)
      displayed_channels_submenu.addAction(show_both_channels_data_action)
      self.viewMenu.addSeparator()
      
      # Display freq resp graph on the screen
      self.viewMenu.addAction(show_frequency_response_action)
      self.viewMenu.addSeparator()

      # Display spectral power distribution graph on the screen
      self.viewMenu.addAction(show_spectral_power_distribution_action)
      self.viewMenu.addSeparator()

      # Displays spectrogram graph on the screen
      self.viewMenu.addAction(show_spectrogram_action)

      #######################################
      # Connecting actions to the Tools menu #
      #######################################

      # Filters submenu with added actions
      filters_submenu = self.toolsMenu.addMenu("Filters")
      filters_submenu.addAction(set_default_filter_action)

      # Player submenu with added actions
      player_submenu = self.toolsMenu.addMenu("Player")
      player_submenu.addAction(track_play_action)
      player_submenu.addAction(track_pause_action)

      # Recorder submenu with added actions
      recorder_submenu = self.toolsMenu.addMenu("Recorder")
      recorder_submenu.addAction(recording_action)

      # Spectrogram submenu with added actions
      spectrogram_submenu = self.toolsMenu.addMenu("Spectrogram")

      # Spectral Power Distribution submenu with added actions
      spectral_power_distribution_submenu = self.toolsMenu.addMenu("Spectral Power Distribution")

      # Freq Resp submenu with added actions
      frequency_response_graph = self.toolsMenu.addMenu("Frequency Response")

      #############################################
      # Connecting created actions to the toolbar #
      #############################################

      self.toolbar.addAction(new_file_action)
      self.toolbar.addAction(open_file_action)
      self.toolbar.addAction(save_file_action)
      self.toolbar.addAction(save_file_as_action)
      self.toolbar.addSeparator()
      self.toolbar.addAction(select_section_action)
      self.toolbar.addAction(select_all_action)
      self.toolbar.addSeparator()
      self.toolbar.addAction(track_play_action)
      self.toolbar.addAction(track_pause_action)
      self.toolbar.addAction(track_stop_action)
      self.toolbar.addAction(track_fast_forward_action)
      self.toolbar.addAction(track_rewind_action)
      self.toolbar.addSeparator()
      self.toolbar.addAction(recording_action)
      self.toolbar.addSeparator()

      ####################################
      # Adding a ComboBoxes to the toolbar #
      ####################################

      # Filters
      self.toolbar_filters_combo = QComboBox()
      self.toolbar_filters_combo.addItems(self.list_of_filters)
      self.toolbar.addWidget(self.toolbar_filters_combo)
      self.toolbar.addSeparator()
      self.toolbar_filters_combo.activated.connect(self.toolbarFilterSelector)

      # Window functions
      self.toolbar_windowfn_combo = QComboBox()
      self.toolbar_windowfn_combo.addItems(self.list_of_windows)
      self.toolbar.addWidget(self.toolbar_windowfn_combo)
      self.toolbar.addSeparator()
      self.toolbar_windowfn_combo.activated.connect(self.toolbarWindowFnSelector)


#################################################################################


   ################
   # File methods #
   ################


   def checkIfFileIsSaved(self):
      print("Checking if the files have been saved after creation(graphs, recordings)")

   def openFileFromDirectory(self):
      print("I will open a window for searching files through the directories")

   def saveFileWithCurrentName(self):
      print("Classic save functionality, overrides the file content, keeps the name")

   def saveFileWithAnotherName(self):
      print("Classic save functionality, overrides the file content, keeps the name")

   def saveFileWithSelectedTimestamp(self):
      print("Saves the selected timestamp")
   
   def saveAudioChannelsSeparately(self):
      print("Saves audio channels into separate files")

   ###################
   # Editing methods #
   ###################

   def selectTimestamp(self):
      print("Allows selecting of the timestamp")

   ################
   # View methods #
   ################


   def showLeftChannelData(self):
      print("Allows displaying of the left channel data")

   def showRightChannelData(self):
      print("Allows displaying of the right channel data")

   def showBothChannelData(self):
      print("Allows displaying both channels data")

   def showFrequencyResponseGraph(self):
      print("Displays on the screen the Freq Response graph")

   def showSpectralPowerDistribution(self):
      print("Displays the spectral power distribtuion")

   def showSpectrogram(self):
      print("Shows the spectrogram")


   ###################
   # Filters methods #
   ###################

   ## Filters
   def setDefaultFilter(self):
      print("Sets the default filter")

   ##################
   # Player methods #
   ##################


   def playTrack(self):
      print("Playing the audio track")

   def pauseTrack(self):
      print("Pausing the audio track")

   def stopTrack(self):
      print("Stopping the audio track")

   def trackFastForward(self):
      print("Fast forward the track")

   def trackRewind(self):
      print("Rewinding the track")


   ####################
   # Recorder methods #
   ####################

   def startOrStopAudioRecording(self, s):
      print("Starts or pauses the recording, current checked value is = {a}".format(a=s))

   #######################
   # Spectrogram methods #
   #######################

   ## Window functions
   def setRectangularWindowFunction(self):
      print("Sets triangular window function")

   #######################################
   # Spectral Power Distribution methods #
   #######################################



   ##############################
   # Frequency Response methods #
   ##############################



   #######################
   # GUI backend methods #
   #######################
   
   def toolbarFilterSelector(self, index):
      print(f"Something was clicked on the combobo, {index}")

   def toolbarWindowFnSelector(self, index):
      print(f"Window functions selector")


def main():
   # A quick print environment test
   print("Does anything even work?")

   # Defining the key Qt elements
   app = QApplication(sys.argv)
   window = appWindow()
   window.resize(1280,720)
   window.show()

   sys.exit(app.exec())



if __name__ == "__main__":
    main()
