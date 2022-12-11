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

   def __init__(self, *args, **kwargs):

      # Base class initialisation
      super(Window, self).__init__(*args, **kwargs)

      # App name
      self.m_AppName = "Spectroapp"

      #####################
      # Runtime variables #
      #####################


      self.m_FileName = str
      self.m_WindowFunctionList = []
      self.m_SpectrogramBandsList = []
      self.m_OverlapPercentage = None

      self.m_FileData = np.ndarray()
      self.m_TimeData = np.ndarray()
      self.m_SpectrogramData = [[], []]

      self.mb_FileOpened = False
      self.mb_Mono = False
      self.mb_Stereo = False


      #
      # Backend mt functionality #
      #


      # Defining the backend object
      self.backend = logic()

      # Connecting the signals

      self.backend.send_file_name.connect(self.setFileName)
      self.backend.send_window_function_list.connect(self.setWindowFunctions)
      self.backend.send_spectrogram_bands_list.connect(self.setSpectrogramBands)
      self.backend.send_overlap_percentage.connect(self.setOverlapPercentage)
      self.backend.send_file_status.connect(self.setFileFlag)
      self.backend.send_mono_status.connect(self.setMonoFlag)
      self.backend.send_stereo_status.connect(self.setStereoFlag)
      self.backend.send_file_data.connect(self.setFileData)
      self.backend.send_time_data.connect(self.setTimeData)
      self.backend.send_channel_data.connect(self.setSpectrogramData)

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
      track_play_action.triggered.connect(self.clearPlotWidgets)

      # Pauses the track
      track_pause_action = QAction(QIcon(os.path.join(basedir, "icons/icons8-pause-24.png")), "Pause", self)
      track_pause_action.setStatusTip("Stops the current audio track")
      track_pause_action.triggered.connect(self.updateFigure)

      # Stops the playback and resets to the start of the track
      track_stop_action = QAction(QIcon(os.path.join(basedir, "icons/icons8-stop-24.png")), "Stop", self)
      track_stop_action.setStatusTip("Stops and resets the playback")
      track_stop_action.triggered.connect(self.addFrequencyResponse)

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

      # overlap slider
      self.slider_label = QLabel()
      self.slider_label.setText(" Window Overlap: ")
      self.toolbar.addWidget(self.slider_label)

      self.currentSliderValue = 0

      self.slider_value = QLabel()
      self.slider_value.setText(f" {self.currentSliderValue}  ")
      self.toolbar.addWidget(self.slider_value)
      self.sld = QSlider(Qt.Horizontal)
      self.sld.setRange(1, 100)
      self.sld.setGeometry(30, 40, 200, 30)
      self.sld.valueChanged.connect(self.overlapSlider)
      self.toolbar.addWidget(self.sld)

      self.main_widget = QWidget()
      self.setBaseLayout()
      self.main_widget.setLayout(self.baseLayout)
      self.setCentralWidget(self.main_widget)

      self.show()

      


#################################################################################


#####################
# Setters / Getters #
#####################


   def setFileName(self, name):
      self.m_FileName = name


   def setWindowFunctions(self, functions):
      self.m_WindowFunctionList = functions


   def setSpectrogramBands(self, bands):
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


#
# File edition and creation #
#


   def createNewFile(self):
      self.checkIfFileIsSaved()

      text, ok = QInputDialog.getText(self, 'Text Input Dialog', 'Enter your name:')
		
      if ok:
         self.backend.create_file.emit(os.path.join(basedir, text))

      self.backend.get_file_name.emit()
      #self.freq_resp.clear()
      #self.mono_spectrogram.clear()
      #self.right_channel_spectrogram.clear()
      #self.left_channel_spectrogram.clear()

   def checkIfFileIsSaved(self):
      print("Checking if the files have been saved after creation(graphs, recordings)")

   def openFileFromDirectory(self):
      # Checking if any wile was read before
      if self.backend.getFileStatus():
         self.clearPlotWidgets()

      # Getting the filename from the dialog window
      name=QFileDialog.getOpenFileName(self, 'Open file', '', '')

      # Reading the file content
      self.backend.openFile(filename=name[0])
      
      # Adding the spectrogram
      self.spectrogram_widget.clearCanvas()
      self.freq_resp_widget.clearCanvas()
      self.addFrequencyResponse()
      self.addSpectrogram()
      self.spectrogram_widget.updateAxes()
      self.freq_resp_widget.updateAxes()


   def saveFileWithCurrentName(self):
      name = QFileDialog.getSaveFileName(self, 'Save File')
      print("Classic save functionality, overrides the file content, keeps the name")

   def saveFileWithAnotherName(self):
      print("Classic save functionality, overrides the file content, keeps the name")



   def overlapSlider(self, value):

      if self.backend.getFileStatus():
         # Sets the percentile value of the overlap
         self.backend.setWindowOverlapPercentage(value)

         self.currentSliderValue = value
         self.slider_value.setText(f" {self.currentSliderValue}  ")

         # Calculating the spectrogram and making the updates visible on the screen
         self.spectrogram_widget.clearCanvas()
         self.addSpectrogram()
         self.spectrogram_widget.updateAxes()

   def clearPlotWidgets(self):
      self.freq_resp_widget.clearCanvas()
      self.spectrogram_widget.clearCanvas()
      self.spectral_distribution_widget.clearCanvas()

   def addFrequencyResponse(self):


      # Adding a single plot
      self.freq_resp_widget.addSinglePlot()

      # Adding the data
      self.freq_resp_widget.m_Figure.tight_layout()
      self.freq_resp_widget.m_Plots.set_yticks([])
      #self.freq_resp_widget.m_Plots.set_xticks([])
      self.freq_resp_widget.m_Plots.plot(self.backend.getFileTimeData(), self.backend.getFileData())

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


   def addSpectrogram(self):
      # Calling the backend fucntion for creating a spectrogram
      self.backend.calculateSpectrogram()

      if self.backend.getMonoStatus():
         self.spectrogram_widget.addSinglePlot()

         #self.spectrogram_widget.m_Figure.set_size_inches(11, 5)
         self.spectrogram_widget.m_Figure.tight_layout()
         #self.spectrogram_widget.m_Plots.set_yticks([])
         #self.spectrogram_widget.m_Plots.set_xticks([])

         self.spectrogram_widget.m_Plots.pcolormesh(self.backend.getFirstChannelTimeSegments(), self.backend.getFirstChannelFrequencySamples(), self.backend.getFirstChannelSpectrogramData(), cmap="plasma")
      elif self.backend.getStereoStatus():
         self.spectrogram_widget.addTwoHorizontalPlots()
         self.spectrogram_widget.m_Figure.tight_layout()

         self.spectrogram_widget.m_Plots[0].pcolormesh(self.backend.getFirstChannelTimeSegments(), self.backend.getFirstChannelFrequencySamples(), self.backend.getFirstChannelSpectrogramData(), cmap="plasma")
         self.spectrogram_widget.m_Plots[1].pcolormesh(self.backend.getSecondChannelTimeSegments(), self.backend.getSecondChannelFrequencySamples(), self.backend.getSecondChannelSpectrogramData(), cmap="plasma")
      else:
         print('I have to display an error window here')

   def updateFigure(self):
      self.freq_resp_widget.draw()
      self.spectrogram_widget.draw()
      self.spectral_distribution_widget.draw()
      

   def onselect(self, xmin, xmax):
      #indmin, indmax = np.searchsorted(self.backend.time, (xmin, xmax))
      indmin, indmax = self.backend.getFileTimeData().searchsorted((xmin, xmax))
      indmax = min(len(self.backend.getFileTimeData()) - 1, indmax)

      ##region_x = self.x[indmin:indmax]
      ##region_y = self.y[indmin:indmax]
      self.backend.setFileSegment([int(indmin), int(indmax)])

      print(indmax)

      self.spectrogram_widget.clearCanvas()
      self.addSpectrogram()
      self.spectrogram_widget.updateAxes()

   ################
   # File methods #
   ################

   def exportPlots(self):
      #name = QFileDialog.getSaveFileName(self, 'Save File')
      #self.sc.fig.savefig(str(name[0]))

      self.freq_resp_widget.m_Figure.savefig("ajla")
      self.spectrogram_widget.m_Figure.savefig("bajla")
      self.spectral_distribution_widget.savefig("morela")

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
   
   def setWindowFunction(self, ind):

      # Passing in the index argument
      self.backend.setWindowFunction(index=ind)

      self.spectrogram_widget.clearCanvas()
      self.addSpectrogram()
      self.spectrogram_widget.updateAxes()

   def setSpectrogramBand(self, index):

      # Passing in the index argument
      self.backend.setSpectrogramBand(index)

      self.spectrogram_widget.clearCanvas()
      self.addSpectrogram()
      self.spectrogram_widget.updateAxes()

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
