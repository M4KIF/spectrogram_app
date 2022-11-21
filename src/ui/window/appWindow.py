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



class appWindow(QMainWindow):
   def __init__(self, *args, **kwargs):

      #######################################################
      # Initialising the appWindow with basic functionality #
      #######################################################

      super(appWindow, self).__init__(*args, **kwargs)

      # Setting the App title
      self.setWindowTitle("Spectrogram")

      # Adding the menu bar
      menu = self.menuBar()

      # Adding a toolbar
      toolbar = QToolBar("Actions")

      ###############################
      # Extending the functionality #
      ###############################

      # File menu
      fileMenu = menu.addMenu("File")
      # View menu
      viewMenu = menu.addMenu("View")
      # Tools menu
      toolsMenu = menu.addMenu("Tools")
      # Help menu
      helpMenu = menu.addMenu("Help")

      ##############################
      # Creating File Actions #
      ##############################
      
      # New file button
      new_file = QAction("New File", self)
      new_file.setStatusTip("Creates a new empty file")
      new_file.triggered.connect(self.checkIfFileIsSaved)

      # Open file button
      open_file = QAction("Open File", self)
      open_file.setStatusTip("Allows for searching a file to open")
      open_file.triggered.connect(self.openFileFromDirectory)

      # Save file with override
      save_file = QAction("Save File", self)
      save_file.setStatusTip("Saves the file with override")
      save_file.triggered.connect(self.saveFileWithCurrentName)
      
      # Save file as
      save_file_as = QAction("Save As", self)
      save_file_as.setStatusTip("Saves the file without override")
      save_file_as.triggered.connect(self.saveFileWithAnotherName)

      # Save selected timestamp
      save_selected_timestamp = QAction("Save Timestamp", self)
      save_selected_timestamp.setStatusTip("Saves the selected timestamp")
      save_selected_timestamp.triggered.connect(self.saveFileWithSelectedTimestamp)

      # Save with separate channels
      save_separate_channels = QAction("Save Separate Audio Channels", self)
      save_separate_channels.setStatusTip("Saves the right and left channel in separate files")
      save_separate_channels.triggered.connect(self.saveAudioChannelsSeparately)

      #########################
      # Creating View Actions #
      #########################

      show_frequency_response_graph = QAction("Frequency Response")
      show_frequency_response_graph.setCheckable(True)
      show_frequency_response_graph.checked.connect()

      #########################
      # Creating Tools Actions #
      #########################

      # Timestamp selection
      select_timestamp = QAction("Select Timestamp", self)
      select_timestamp.setStatusTip("Allows selection of timestamp of the file\nfor creating the graphs")
      select_timestamp.triggered.connect(self.selectTimestamp)

      # Filter activation
      activate_filter = QAction("Activate Filters", self)
      activate_filter.setStatusTip("Activates a filter, by default a highpass is selected")
      activate_filter.triggered.connect(self.activateFilter)

      # Filter deactivation
      deactivate_filter = QAction("Deactivate Filter", self)
      deactivate_filter.setStatusTip("Deactivates the filter, and returns to default(no filter)")
      deactivate_filter.triggered.connect(self.deactivateFilter)

      # filters menu
      default_filter = QAction("(default)", self)
      default_filter.setStatusTip("Default filter")
      default_filter.triggered.connect(self.setDefaultFilter)

      # Percentile coverage
      percentile_coverage = QAction()

      ## Window functions
      rectangular_window_function = QAction("Rectangular", self)
      rectangular_window_function.setStatusTip("Selects a rectangular window")
      rectangular_window_function.triggered.connect(self.setRectangularWindowFunction)      

      ##############################
      # Creating Help Actions #
      ##############################



      ###########################################
      # Connecting created actions to the menus #
      ###########################################

      ### Adding actions to the file menu
      fileMenu.addAction(new_file)
      fileMenu.addSeparator()
      fileMenu.addAction(open_file)
      fileMenu.addSeparator()
      fileMenu.addAction(save_file)
      fileMenu.addAction(save_file_as)
      fileMenu.addAction(save_selected_timestamp)
      fileMenu.addAction(save_separate_channels)

      ### Adding actions to view menu

      ### Adding action to the Tools menu
      timestamp_submenu = toolsMenu.addMenu("Timestamp")
      filters_submenu = toolsMenu.addMenu("Filters")
      player_submenu = toolsMenu.addMenu("Player")
      recorder_submenu = toolsMenu.addMenu("Recorder")
      spectrogram_submenu = toolsMenu.addMenu("Spectrogram")
      spectral_power_distribution_submenu = toolsMenu.addMenu("Spectral Power Distribution")
      frequency_response_graph = toolsMenu.addMenu("Frequency Response")



   ### GUI methods definitions

   ## File menu methods
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

   ## View menu functionality

   ## Tools menu functionality
   def selectTimestamp(self):
      print("Allows selecting of the timestamp")

   def activateFilter(self):
      print("Activating a fiter, if not selected, highpass is default")

   def deactivateFilter(self):
      print("Deactivating the filter, returning to clear signal")

   ## Filters
   def setDefaultFilter(self):
      print("Sets the default filter")

   ## Window functions
   def setRectangularWindowFunction(self):
      print("Sets triangular window function")


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
