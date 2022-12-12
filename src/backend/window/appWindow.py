################################################################
# Here is the code responsible for displaying the              #
# content that is mandatory for running the application        #
# This is not a functional app, but only a graphical interface #
# that the app will be implemented with                        #
################################################################


#######################################
# Using icons from https://icons8.com #
#######################################


###########
# Imports #
###########


# Custom modules
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.widgets import SpanSelector

# System Imports
import sys
import os
from copy import copy

# Logic module import
from ..logic.appLogic import appLogic as logic



# Base directory global variable
basedir = os.path.dirname(__file__)



class PlotCanvas(FigureCanvasQTAgg):

   def __init__(self, parent=None, width=8, height=2, dpi=100):

      #################
      # Boolean flags #
      #################

      self.m_MultiplePlots = False
      self.m_StackedHorizontaly = False
      self.m_StackedVerticaly = False


      ###########################################
      # Variables containing the Canvas content #
      ###########################################

      self.m_GridSpace = None
      self.m_Plots = None
      self.m_Figure = Figure(figsize=(width, height), dpi=dpi)

      #########
      # Setup #
      #########

      # Calling the constructor of the base class
      super(PlotCanvas, self).__init__(self.m_Figure)

      # Changing the layout to tight
      self.m_Figure.tight_layout()


   def addSinglePlot(self):
      self.m_Plots = self.m_Figure.subplots()


   def addTwoHorizontalPlots(self):
      self.m_GridSpace = self.m_Figure.add_gridspec(2, hspace=0.2)
      self.m_Plots = self.m_GridSpace.subplots()
      self.m_Plots[0].set_xticklabels([])
      self.m_Plots[0].set_xticks([])
      self.m_MultiplePlots = True
      self.m_StackedVerticaly = True


   def addTwoVerticalPlots(self):
      self.m_GridSpace = self.m_Figure.add_gridspec(1, 2, wspace=0.1)
      self.m_Plots = self.m_GridSpace.subplots(sharex=True)
      self.m_Plots[1].set_yticklabels([])
      self.m_Plots[1].set_yticks([])
      self.m_Plots[0].set_xticks([])
      self.m_MultiplePlots = True
      self.m_StackedHorizontaly = True


   def createFrequencyResponsePlot(self, data):
      self.m_Plots.plot(data[1], data[0])


   def createSpectrogramPlot(self, data):
      if not (self.m_MultiplePlots == True and self.m_StackedVerticaly == True):
         self.m_Plots.pcolormesh(self.backend.getFirstChannelTimeSegments(), self.backend.getFirstChannelFrequencySamples(), self.backend.getFirstChannelSpectrogramData(), cmap="plasma")
      else:
         self.m_Plots[0].pcolormesh(data[0][1], data[0][0], data[0][2], cmap="plasma")
         self.m_Plots[1].pcolormesh(data[1][1], data[1][0], data[1][2], cmap="plasma")


   def createSpectralDistributionPlot(self, data):
      print('')


   def clearCanvas(self):
      # Checking if there are more than one plots on the canvas
      for plot in self.m_Figure.get_axes():
         plot.clear()

      # Clearing the figure of any plots
      self.m_Figure.clear()

      # Changing the multiplots flag
      self.m_MultiplePlots = False
      self.m_StackedHorizontaly = False
      self.m_StackedVerticaly = False


   def clearAxes(self):
      for plot in self.m_Figure.get_axes():
         plot.clear()


   def updateAxes(self):
      self.draw()



# GUI class, implements the functionality from the backend 
class Window(QMainWindow):

   # Thread object for multithreading the backend
   m_BackendThread = QThread()

   def __init__(self, *args, **kwargs):

      # Base class initialisation
      super(Window, self).__init__(*args, **kwargs)

      # App name
      self.m_AppName = "Spectroapp"

      #####################
      # Runtime variables #
      #####################


      self.m_FileName = str()
      self.m_WindowFunctionList = []
      self.m_SpectrogramBandsList = []
      self.m_OverlapPercentage = None

      #self.m_FileData = None
      #self.m_TimeData = None
      #self.m_SpectrogramData = [[], []]

      self.mb_FileOpened = False
      self.mb_FileSaved = False
      self.mb_Mono = False
      self.mb_Stereo = False


      #
      # Backend mt functionality #
      #


      # Defining the backend object
      self.backend = logic()

      self.backend.moveToThread(self.m_BackendThread)

      # Connecting the signals

      self.backend.send_file_name.connect(self.setFileName)
      self.backend.send_window_function_list.connect(self.setWindowFunctionsList)
      self.backend.send_spectrogram_bands_list.connect(self.setSpectrogramBandsList)
      self.backend.send_overlap_percentage.connect(self.setOverlapPercentage)
      self.backend.send_file_status.connect(self.setFileFlag)
      self.backend.send_file_saved_status.connect(self.setFileSavedFlag)
      self.backend.send_mono_status.connect(self.setMonoFlag)
      self.backend.send_stereo_status.connect(self.setStereoFlag)
      self.backend.send_file_data.connect(self.setFileData)
      self.backend.send_time_data.connect(self.setTimeData)
      self.backend.send_channel_data.connect(self.setSpectrogramData)

      self.backend.send_freq_response_data.connect(self.updateFrequencyResponse)
      self.backend.send_spectrogram_data.connect(self.updateSpectrogram)

      # Getting the data
      self.backend.get_window_function_list.emit()
      self.backend.get_spectrogram_bands_list.emit()


      #######################################################
      # Initialising the appWindow with basic functionality #
      #######################################################

      # Adding a toolbar and setting some defaults
      self.toolbar = QToolBar("Audio file actions")
      self.toolbar.setIconSize(QSize(32,32))
      self.toolbar.setMovable(False)
      self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

      # Adding the toolbar to the main window
      self.addToolBar(self.toolbar)

      # Adding the menu bar
      self.menu = QMainWindow.menuBar(self)

      # Adding a status bar
      self.statusbar = QStatusBar()
      self.setStatusBar(self.statusbar)
      self.statusbar.showMessage("Various informations")
      self.statusbar.show()

      # Setting the App title
      self.setWindowTitle(self.m_AppName)
      
      ################################
      # Extending menu functionality #
      ################################

      # File menu
      self.fileMenu = self.menu.addMenu("File")
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
      new_file_action.triggered.connect(self.createNewFile)

      # Open file button
      open_file_action = QAction(QIcon(os.path.join(basedir, "icons/application--pencil.png")),"Open File", self)
      open_file_action.setStatusTip("Allows for searching a file to open")
      open_file_action.triggered.connect(self.openFileFromDirectory)

      # Save file with override
      save_file_action = QAction(QIcon(os.path.join(basedir, "icons/disk--pencil.png")), "Save File", self)
      save_file_action.setStatusTip("Saves the file with override")
      save_file_action.triggered.connect(self.backend.save_file)
      
      # Save file as
      save_file_as_action = QAction(QIcon(os.path.join(basedir, "icons/disk--plus.png")), "Save As", self)
      save_file_as_action.setStatusTip("Saves the file without override")
      save_file_as_action.triggered.connect(self.saveFileWithCurrentName)

      # Save selected timestamp
      export_plot_action = QAction(QIcon(os.path.join(basedir, "icons/icons8-external-link-24.png")), "Export Plot", self)
      export_plot_action.setStatusTip("Saves the selected timestamp")
      export_plot_action.triggered.connect(self.exportPlots)

      ##########################
      # Playback and recording actions #
      ##########################

      # Plays the track
      track_play_action = QAction(QIcon(os.path.join(basedir, "icons/icons8-play-24.png")), "Play", self)
      track_play_action.setStatusTip("Play the current audio track")
      track_play_action.triggered.connect(self.playTrack)

      # Pauses the track
      track_pause_action = QAction(QIcon(os.path.join(basedir, "icons/icons8-pause-24.png")), "Pause", self)
      track_pause_action.setStatusTip("Stops the current audio track")
      track_pause_action.triggered.connect(self.pauseTrack)

      # Stops the playback and resets to the start of the track
      track_stop_action = QAction(QIcon(os.path.join(basedir, "icons/icons8-stop-24.png")), "Stop", self)
      track_stop_action.setStatusTip("Stops and resets the playback")
      track_stop_action.triggered.connect(self.stopTrack)

      # Fast Forwards the track
      track_fast_forward_action = QAction(QIcon(os.path.join(basedir, "icons/icons8-fast-forward-24.png")), "Fast Forward", self)
      track_fast_forward_action.setStatusTip("Fast forwards the track")
      track_fast_forward_action.triggered.connect(self.trackFastForward)

      # Rewind the track
      track_rewind_action = QAction(QIcon(os.path.join(basedir, "icons/icons8-rewind-24.png")), "Rewind", self)
      track_rewind_action.setStatusTip("Rewinds the track")
      track_rewind_action.triggered.connect(self.trackRewind)

      # Start recording audio
      recording_action = QAction(QIcon(os.path.join(basedir, "icons/icons8-micro-24.png")), "Start/Stop recording", self)
      recording_action.setStatusTip("Starts the recording")
      recording_action.setCheckable(True)
      recording_action.triggered.connect(self.startOrStopAudioRecording)

      ##############################
      # Creating Help Actions #
      ##############################

      help_action = QAction("About The Program", self)
      help_action.setStatusTip(".")
      help_action.triggered.connect(self.displayProgramInfo)

      #######################################
      # Connecting actions to the file menu #
      #######################################

      self.fileMenu.addAction(new_file_action)
      self.fileMenu.addSeparator()
      self.fileMenu.addAction(open_file_action)
      self.fileMenu.addSeparator()
      self.fileMenu.addAction(save_file_action)
      self.fileMenu.addAction(save_file_as_action)
      self.fileMenu.addSeparator()
      self.fileMenu.addAction(export_plot_action)

      #######################################
      # Connecting actions to the Tools menu #
      #######################################

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

      #############################################
      # Connecting created actions to the toolbar #
      #############################################

      self.toolbar.addAction(export_plot_action)
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

      self.toolbar_windows_combo = QComboBox()
      self.toolbar_windows_combo.addItems(self.m_WindowFunctionList)
      self.toolbar.addWidget(self.toolbar_windows_combo)
      self.toolbar.addSeparator()
      self.toolbar_windows_combo.activated.connect(self.setWindowFunction)


      self.toolbar_spectrogram_range_combo = QComboBox()
      self.toolbar_spectrogram_range_combo.addItems(self.m_SpectrogramBandsList)
      self.toolbar.addWidget(self.toolbar_spectrogram_range_combo)
      self.toolbar.addSeparator()
      self.toolbar_spectrogram_range_combo.activated.connect(self.setSpectrogramBand)

      self.sld = QSlider(Qt.Horizontal)
      self.sld.setRange(1, 100)
      self.sld.setGeometry(QRect(1, 2, 10, 2))
      self.sld.valueChanged.connect(self.overlapSlider)
      self.sld.setTickPosition(QSlider.TickPosition.TicksLeft)
      self.sld.setTickInterval(1)
      self.sld.setSingleStep(1)
      self.toolbar.addWidget(self.sld)

      self.label = QLabel()
      self.label.setGeometry(QRect(230, 150, 301, 161))
      self.toolbar.addWidget(self.label)
      self.toolbar.addSeparator()

      self.main_widget = QWidget()
      self.setBaseLayout()

      self.main_widget.setLayout(self.baseLayout)
      self.setCentralWidget(self.main_widget)

      self.show()
      self.m_BackendThread.start()


   def closeEvent(self, event):

      super(Window, self).closeEvent(event)

      self.m_BackendThread.quit()



#################################################################################


#####################
# Setters / Getters #
#####################


   def setFileName(self, name):
      self.m_FileName = name


   def setWindowFunctionsList(self, functions):
      self.m_WindowFunctionList = functions


   def setSpectrogramBandsList(self, bands):
      self.m_SpectrogramBandsList = bands


   def setOverlapPercentage(self, percentage):
      self.m_OverlapPercentage = percentage

   def setFileData(self, value):
      self.m_FileData = value

   def setTimeData(self, value):
      self.m_TimeData = value

   def setSpectrogramData(self, value):
      self.m_SpectrogramData = value

   def setFileFlag(self, value):
      self.mb_FileOpened = value

   def setFileSavedFlag(self, value):
      self.mb_FileSaved = value


   def setMonoFlag(self, value):
      self.mb_Mono = value


   def setStereoFlag(self, value):
      self.mb_Stereo = value

   # After opening a new file
   def setBaseLayout(self):
      self.freq_resp_widget = PlotCanvas(self, width=12, height=1.5, dpi=101)
      self.spectrogram_widget = PlotCanvas(self, width=11, height=6, dpi=101)
      self.spectral_distribution_widget = PlotCanvas(self, width=1, height=5, dpi=101)

      self.baseLayout = QGridLayout()
      self.freqLayout = QVBoxLayout()
      self.spectrogramLayout = QHBoxLayout()
      self.spectralDistributionLayout = QHBoxLayout()

      self.baseLayout.addLayout(self.freqLayout, 13, 0, 3, 9, Qt.AlignmentFlag.AlignBottom)
      self.baseLayout.addLayout(self.spectrogramLayout, 0, 0, 13, 8, Qt.AlignmentFlag.AlignTop)
      self.baseLayout.addLayout(self.spectralDistributionLayout, 0, 8, 13, 1, Qt.AlignmentFlag.AlignTop)

      self.freqLayout.addWidget(self.freq_resp_widget)
      self.spectrogramLayout.addWidget(self.spectrogram_widget)
      self.spectralDistributionLayout.addWidget(self.spectral_distribution_widget)

      self.addFrequencyResponse()
      self.addSpectrogram()


#
# File edition and creation #
#


   def createNewFile(self):

      # Updating the file flags
      self.backend.get_file_saved_status.emit()
      self.backend.get_file_status.emit()

      # Checking if anything open is saved
      if not self.mb_FileSaved and self.mb_FileOpened:

         message = QMessageBox
         answer = message.question(self,'', "Recent progress has been unsaved, proceed to saving?", message.Yes | message.No)

         if answer == message.Yes:
            self.backend.save_file.emit()
            self.backend.close_file.emit()

      # Getting the new file name
      text, ok = QInputDialog.getText(self, 'Set Filename', 'Name of the file:')
		
      if ok:
         self.backend.create_file.emit(os.path.join(basedir, text+".wav"))

      self.spectrogram_widget.clearAxes()
      self.freq_resp_widget.clearAxes()

      self.backend.get_file_name.emit()


   def openFileFromDirectory(self):

      # Updating the file flags
      self.backend.get_file_saved_status.emit()
      self.backend.get_file_status.emit()

      # Checking if anything open is saved
      if not self.mb_FileSaved and self.mb_FileOpened:

         message = QMessageBox
         answer = message.question(self,'', "Unsaved progress found, proceed to saving?", message.Yes | message.No)

         if answer == message.Yes:
            self.backend.save_file.emit()
            self.backend.close_file.emit()
      
      if self.mb_FileOpened:
         self.clearPlotWidgets()

      # Getting the filename from the dialog window
      name = QFileDialog.getOpenFileName(self, 'Open file', '', '')

      # Reading the file content
      self.backend.open_file.emit(name[0])
      
      # Adding the spectrogram
      self.spectrogram_widget.clearCanvas()
      self.freq_resp_widget.clearCanvas()

      self.addFrequencyResponse()
      self.addSpectrogram()

      self.backend.prepare_freq_response_data.emit()
      self.backend.prepare_spectrogram_data.emit()


   def saveFileWithCurrentName(self):
      name = QFileDialog.getSaveFileName(self, 'Save File')
      print("Classic save functionality, overrides the file content, keeps the name")

   def saveFileWithAnotherName(self):
      print("Classic save functionality, overrides the file content, keeps the name")


#
# Plot functions
#


   def addFrequencyResponse(self):

      # Adding a single plot
      self.freq_resp_widget.addSinglePlot()

      # Adding the data
      self.freq_resp_widget.m_Figure.tight_layout()
      self.freq_resp_widget.m_Plots.set_yticks([])


   def addSpectrogram(self):

      # Updates the data about the channels
      self.backend.get_mono_status.emit()
      self.backend.get_stereo_status.emit()

      # If the file is mono, creates a mono spectrogram, otherwise does the same for stereo
      if self.mb_Mono:
         self.spectrogram_widget.addSinglePlot()
         self.spectrogram_widget.m_Figure.tight_layout()

      elif self.mb_Stereo:
         self.spectrogram_widget.addTwoHorizontalPlots()
         self.spectrogram_widget.m_Figure.tight_layout()


   def updateSpectrogram(self, value):

      # Clearing the axes values
      self.spectrogram_widget.clearAxes()

      # Setting the correct layout
      self.freq_resp_widget.m_Figure.tight_layout()
      self.freq_resp_widget.m_Plots.set_yticks([])

      # Checking if the mutex can be set
      if self.backend.mutex.tryLock():
         self.m_SpectrogramData = copy(value)
         self.backend.mutex.unlock()

         if self.mb_Mono:
            self.spectrogram_widget.m_Plots.pcolormesh(self.backend.getFirstChannelTimeSegments(), self.backend.getFirstChannelFrequencySamples(), self.backend.getFirstChannelSpectrogramData(), cmap="plasma")
         elif self.mb_Stereo:
            self.spectrogram_widget.m_Plots[0].pcolormesh(self.m_SpectrogramData[0][1], self.m_SpectrogramData[0][0], self.m_SpectrogramData[0][2], cmap="plasma")
            self.spectrogram_widget.m_Plots[1].pcolormesh(self.m_SpectrogramData[1][1], self.m_SpectrogramData[1][0], self.m_SpectrogramData[1][2], cmap="plasma")

      self.spectrogram_widget.updateAxes()


   def updateFrequencyResponse(self, value):

      # Clearing the axes values
      self.freq_resp_widget.clearAxes()
      self.freq_resp_widget.m_Plots.set_yticks([])
      self.freq_resp_widget.m_Figure.tight_layout()

      if self.backend.mutex.tryLock():
         self.m_FileData = copy(value[0])
         self.m_TimeData = copy(value[1])
         self.backend.mutex.unlock()

      self.span = SpanSelector(
         self.freq_resp_widget.m_Plots,
         self.onselect,
         "horizontal",
         useblit=True,
         props=dict(alpha=0.5, facecolor="tab:blue"),
         onmove_callback=self.onselect,
         interactive=True,
         drag_from_anywhere=True
      )

      self.freq_resp_widget.m_Plots.plot(self.m_TimeData, self.m_FileData)

      self.freq_resp_widget.updateAxes()


   def updateSpectralDistribution(self):
      print()


   def overlapSlider(self, value):

      self.backend.get_file_status.emit()

      if self.mb_FileOpened:

         # Sets the percentile value of the overlap
         self.backend.set_window_overlap_percentage.emit(value)

         # Calculating the spectrogram and making the updates visible on the screen
         self.backend.prepare_spectrogram_data.emit()
         

   def clearPlotWidgets(self):
      self.freq_resp_widget.clearCanvas()
      self.spectrogram_widget.clearCanvas()
      self.spectral_distribution_widget.clearCanvas()


   def onselect(self, xmin, xmax):
      #indmin, indmax = np.searchsorted(self.backend.time, (xmin, xmax))
      indmin, indmax = self.backend.getFileTimeData().searchsorted((xmin, xmax))
      indmax = min(len(self.backend.getFileTimeData()) - 1, indmax)

      self.backend.set_file_segment.emit([int(indmin), int(indmax)])

      self.backend.prepare_spectrogram_data.emit()


   ################
   # File methods #
   ################

   def exportPlots(self):

      # Saving the figures with a simple name
      self.freq_resp_widget.m_Figure.savefig("frequency_response")
      self.spectrogram_widget.m_Figure.savefig("spectrogram")
      self.spectral_distribution_widget.m_Figure.savefig("spectral_distribution")

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
      self.backend.play_audio.emit()

   def pauseTrack(self):
      self.backend.pause_audio.emit()

   def stopTrack(self):
      self.backend.stop_audio.emit()

   def trackFastForward(self):
      print("Fast forward the track")

   def trackRewind(self):
      print("Rewinding the track")

   ####################
   # Recorder methods #
   ####################

   def startOrStopAudioRecording(self, s):
      print("Starts or pauses the recording, current checked value is = {a}".format(a=s))


   #######################################
   # Spectral Power Distribution methods #
   #######################################

   def createSpectralPowerDistributionGraph(self):
      print("")

   ################
   # Help methods #
   ################

   def displayProgramInfo(self):
      print("Displays useful information")

   #######################
   # GUI backend methods #
   #######################
   

   def setWindowFunction(self, index):

      # Passing in the index argument
      self.backend.set_window_function.emit(index)

      self.backend.prepare_spectrogram_data.emit()


   def setSpectrogramBand(self, index):

      # Passing in the index argument
      self.backend.set_spectrogram_band.emit(index)

      self.backend.prepare_spectrogram_data.emit()


   def toolbarWindowFnSelector(self, index):
      print(f"Window functions selector")


def main():
   # A quick print environment test
   print("Does anything even work?")

   # Defining the key Qt elements
   app = QApplication(sys.argv)
   window = Window()
   window.resize(1280,720)
   window.show()

   sys.exit(app.exec())



if __name__ == "__main__":
    main()
