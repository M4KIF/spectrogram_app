# Here is the code responsible for displaying the
# content that is mandatory for running the application
# This is not a functional app, but only a graphical interface
# that the app will be implemented with



# Modules imports
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
import numpy as np

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

      #################################################
      # Base informations and data needed for runtime #
      #################################################

      self.freq_resp = PlotCanvas(self, width=14, height=1, dpi=100)
      self.mono_spectrogram = PlotCanvas(self, width=14, height=5, dpi=100)
      self.left_channel_spectrogram = PlotCanvas(self, width=7, height=5, dpi=100)
      self.right_channel_spectrogram = PlotCanvas(self, width=7, height=5, dpi=100)

      # Contains the names of the filters
      self.list_of_windows = ["tukey", "boxcar", "flattop"]

      # Contains the names of window functions
      self.list_of_filters = []

      # Flags initialisation
      self.m_FilterChanged = True
      self.m_WindowFunctionChanged = True

      self.displayingMonoSpectrogram = False
      self.displayingStereoSpectrogram = False

      #######################################################
      # Initialising the appWindow with basic functionality #
      #######################################################

      # Base class initialisation
      super(Window, self).__init__(*args, **kwargs)

      # Adding a toolbar and setting some defaults
      self.toolbar = QToolBar("Actions")
      self.toolbar.setIconSize(QSize(32,32))
      self.toolbar.setMovable(False)
      self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

      
      self.addToolBar(self.toolbar)



      #self.layout = QGridLayout(self)
      #self.layout.addWidget(self.freq_resp, 56, 0, 3, 48, Qt.AlignmentFlag.AlignBottom)

      # Initialising the appLogic class with all of the needed functionality
      self.backend = logic()

      # Setting the App title
      self.setWindowTitle("Spectrogram")

      # Adding the menu bar
      self.menu = QMainWindow.menuBar(self)

      # Adding a status bar
      self.statusbar = QStatusBar()
      self.setStatusBar(self.statusbar)
      self.statusbar.showMessage("Here I will print bitrate and all of this stuff")
      self.statusbar.show()
      
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
      new_file_action.triggered.connect(self.createNewFile)

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
      save_plot_action = QAction(QIcon(os.path.join(basedir, "icons/disk-rename.png")), "Export Plot", self)
      save_plot_action.setStatusTip("Saves the selected timestamp")
      save_plot_action.triggered.connect(self.exportPlots)

      # Save with separate channels
      save_separate_channels_action = QAction(QIcon(os.path.join(basedir, "icons/disks.png")), "Save Separate Audio Channels", self)
      save_separate_channels_action.setStatusTip("Saves the right and left channel in separate files")
      save_separate_channels_action.triggered.connect(self.saveAudioChannelsSeparately)

      #########################
      # Creating Edit Actions #
      #########################

      plot_action = QAction(QIcon(os.path.join(basedir, "icon/selection.png")), "Create Spectrogram", self)
      plot_action.setStatusTip("Creates a spectrogram")
      plot_action.triggered.connect(self.createSpectrogramGraph)

      # Select Section
      select_section_action = QAction(QIcon(os.path.join(basedir, "icons/selection.png")), "Select", self)
      select_section_action.setStatusTip("Allows selection of timestamp of the file\nfor creating the graphs")
      select_section_action.triggered.connect(self.selectTimestamp)

      # Select Whole File
      select_all_action = QAction(QIcon(os.path.join(basedir, "icons/selection-select.png")), "Select All", self)
      select_all_action.setStatusTip("Allows selection of timestamp of the file\nfor creating the graphs")
      select_all_action.triggered.connect(self.selectWholeFile)


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
      track_play_action.triggered.connect(self.clearPlotWidgets)

      # Pauses the track
      track_pause_action = QAction(QIcon(os.path.join(basedir, "icons/control-pause.png")), "Pause", self)
      track_pause_action.setStatusTip("Stops the current audio track")
      track_pause_action.triggered.connect(self.updateFigure)

      # Stops the playback and resets to the start of the track
      track_stop_action = QAction(QIcon(os.path.join(basedir, "icons/control-stop-square.png")), "Stop", self)
      track_stop_action.setStatusTip("Stops and resets the playback")
      track_stop_action.triggered.connect(self.addFrequencyResponse)

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
      recording_action = QAction(QIcon(os.path.join(basedir, "icons/control-pause-record.png")), "Start/Stop recording", self)
      recording_action.setStatusTip("Starts the recording")
      recording_action.setCheckable(True)
      recording_action.triggered.connect(self.startOrStopAudioRecording)

      ## Spectrogram

      # Percentile coverage
      percentile_coverage = QAction()

      ## Window functions
      rectangular_window_function_action = QAction("Rectangular", self)
      rectangular_window_function_action.setStatusTip("Selects a rectangular window")
      rectangular_window_function_action.triggered.connect(self.setRectangularWindowFunction)    

      ## Spectral Power Distribution



      ##############################
      # Creating Help Actions #
      ##############################

      help_action = QAction("About The Program", self)
      help_action.setStatusTip("dunno")
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
      self.fileMenu.addAction(save_plot_action)
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

      #############################################
      # Connecting created actions to the toolbar #
      #############################################

      self.toolbar.addAction(save_plot_action)
      self.toolbar.addAction(plot_action)
      self.toolbar.addSeparator()
      #self.toolbar.addAction(select_section_action)
      #self.toolbar.addAction(select_all_action)
      #self.toolbar.addSeparator()
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

      # Window functions
      self.window_function_label = QLabel()
      self.window_function_label.setText(" Window Function: ")
      self.toolbar.addWidget(self.window_function_label)

      self.toolbar_windows_combo = QComboBox()
      self.toolbar_windows_combo.addItems(self.backend.listOfWindows)
      self.toolbar.addWidget(self.toolbar_windows_combo)
      self.toolbar.addSeparator()
      self.toolbar_windows_combo.activated.connect(self.toolbarWindowSelector)

      # Narrow/Wideband
      self.range_label = QLabel()
      self.range_label.setText(" Range: ")
      self.toolbar.addWidget(self.range_label)

      self.toolbar_spectrogram_range_combo = QComboBox()
      self.toolbar_spectrogram_range_combo.addItems(self.backend.spectrogramBand)
      self.toolbar.addWidget(self.toolbar_spectrogram_range_combo)
      self.toolbar.addSeparator()
      self.toolbar_spectrogram_range_combo.activated.connect(self.toolbarSpectrogramRangeSelector)

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

      # Window functions
      #self.toolbar_windowfn_combo = QComboBox()
      #self.toolbar_windowfn_combo.addItems(self.list_of_windows)
      #self.toolbar.addWidget(self.toolbar_windowfn_combo)
      #self.toolbar.addSeparator()
      #self.toolbar_windowfn_combo.activated.connect(self.toolbarWindowFnSelector)

      np.random.seed(19680801)

      #self.mainLayout = QGridLayout()
      self.freqRespLayout = QVBoxLayout(self)
      #self.mainLayout.addLayout(self.freqRespLayout, 1, 1, Qt.AlignmentFlag.AlignBottom)

      self.fileOpenedFlag = False

      spacer = QSpacerItem(60, 32, QSizePolicy.Minimum, QSizePolicy.Expanding)
      #self.layout.addWidget(self.toolbar, 0, 0, 2, 32, Qt.AlignmentFlag.AlignTop)
      #self.layout.addItem(spacer, 0, 0, Qt.AlignmentFlag.AlignTop)

      #self.layout.addWidget(OverloadedPlotToolbar(self.sc, self))
      #self.main_widget.setLayout(self.layout)
      #self.setLayout(self.mainLayout)

      #self.sc.axes.set_xticklabels([])
      #self.sc.axes.set_yticklabels([])

      self.indmax = 0
      self.indmin = 0

      
      self.main_widget = QWidget()
      self.createBaseLayout()
      self.main_widget.setLayout(self.baseLayout)
      self.setCentralWidget(self.main_widget)

#ax1.set_ylim(-2, 2)
#ax1.set_title('Press left mouse button and drag '
#              'to select a region in the top graph')

      self.show()
# Set useblit=True on most backends for enhanced performance.

      


#################################################################################

   def overlapSlider(self, value):
      if self.backend.fileRead:
         self.backend.setOverlap(value)
         self.currentSliderValue = value
         self.slider_label.setText(f" {self.currentSliderValue}  ")
         self.backend.calculateSpectrogram()
         self.spectrogram_widget.clearCanvas()
         self.addSpectrogram()
         self.spectrogram_widget.updateAxes()

   # After opening a new file
   def createBaseLayout(self):
      self.freq_resp_widget = PlotCanvas(self, width=12, height=1, dpi=100)
      self.spectrogram_widget = PlotCanvas(self, width=11, height=6, dpi=100)
      self.spectrogram_widget.addTwoHorizontalPlots()
      self.freq_resp_widget.addSinglePlot()
      self.spectral_distribution_widget = PlotCanvas(self, width=1, height=5, dpi=100)
      self.spectral_distribution_widget.addTwoVerticalPlots()

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

   def clearPlotWidgets(self):
      self.freq_resp_widget.clearCanvas()
      self.spectrogram_widget.clearCanvas()
      self.spectral_distribution_widget.clearCanvas()

   def addFrequencyResponse(self):
      # I have to check how many channels does the file have
      if self.backend.mono:
         # Adding a single plot
         self.freq_resp_widget.addSinglePlot()

         # Adding the data
         self.freq_resp_widget.m_Plots.set_yticks([])
         self.freq_resp_widget.m_Plots.set_xticks([])
         self.freq_resp_widget.m_Plots.plot(self.backend.time, self.backend.channel_1)

         self.span = SpanSelector(
            self.freq_resp_widget.m_Plots,
            self.onselect,
            "horizontal",
            useblit=True,
            props=dict(alpha=0.5, facecolor="tab:blue"),
            interactive=True,
            drag_from_anywhere=True
         )
      elif self.backend.stereo:
         self.freq_resp_widget.addTwoHorizontalPlots()

         self.freq_resp_widget.m_Plots[0].set_yticks([])
         self.freq_resp_widget.m_Plots[0].set_yticklabels([])
         self.freq_resp_widget.m_Plots[0].set_xticks([])
         self.freq_resp_widget.m_Plots[1].set_yticks([])
         self.freq_resp_widget.m_Plots[1].set_yticklabels([])
         self.freq_resp_widget.m_Plots[1].set_xticks([])

         self.freq_resp_widget.m_Plots[0].plot(self.backend.time, self.backend.channel_1)
         self.freq_resp_widget.m_Plots[1].plot(self.backend.time, self.backend.channel_2)

         self.span_left = SpanSelector(
            self.freq_resp_widget.m_Plots[0].axes,
            self.onselect,
            "horizontal",
            useblit=True,
            props=dict(alpha=0.5, facecolor="tab:blue"),
            interactive=True,
            drag_from_anywhere=True
         )
         self.span_right = SpanSelector(
            self.freq_resp_widget.m_Plots[1].axes,
            self.onselect,
            "horizontal",
            useblit=True,
            props=dict(alpha=0.5, facecolor="tab:blue"),
            interactive=True,
            drag_from_anywhere=True
         )
      else:
         print('I have to display an error window here')

   def addSpectrogram(self):
      # Calling the backend fucntion for creating a spectrogram
      self.backend.calculateSpectrogram()

      if self.backend.mono:
         self.spectrogram_widget.addSinglePlot()

         self.spectrogram_widget.m_Plots.set_yticks([])
         self.spectrogram_widget.m_Plots.set_xticks([])

         self.spectrogram_widget.m_Plots.pcolormesh(self.backend.segments_channel_1, self.backend.freq_channel_1, self.backend.spectro_channel_1, cmap="plasma")
      elif self.backend.stereo:
         self.spectrogram_widget.addTwoHorizontalPlots()

         self.spectrogram_widget.m_Plots[0].pcolormesh(self.backend.segments_channel_1, self.backend.freq_channel_1, self.backend.spectro_channel_1, cmap="plasma")
         self.spectrogram_widget.m_Plots[1].pcolormesh(self.backend.segments_channel_2, self.backend.freq_channel_2, self.backend.spectro_channel_2, cmap="plasma")
      else:
         print('I have to display an error window here')

   def updateFigure(self):
      self.freq_resp_widget.draw()
      self.spectrogram_widget.draw()
      self.spectral_distribution_widget.draw()
      

   def onselect(self, xmin, xmax):
      #indmin, indmax = np.searchsorted(self.backend.time, (xmin, xmax))
      indmin, indmax = self.backend.time.searchsorted((xmin, xmax))
      indmax = min(len(self.backend.time) - 1, indmax)

      #region_x = self.x[indmin:indmax]
      #region_y = self.y[indmin:indmax]
      self.backend.editRange(indmin, indmax)

      self.spectrogram_widget.clearCanvas()
      self.backend.calculateSpectrogram()
      self.addSpectrogram()
      self.spectrogram_widget.updateAxes()

   ################
   # File methods #
   ################

   def createNewFile(self):
      self.checkIfFileIsSaved()
      #self.freq_resp.clear()
      #self.mono_spectrogram.clear()
      #self.right_channel_spectrogram.clear()
      #self.left_channel_spectrogram.clear()

   def checkIfFileIsSaved(self):
      print("Checking if the files have been saved after creation(graphs, recordings)")

   def openFileFromDirectory(self):
      # Checking if any wile was read before
      if self.backend.fileRead:
         self.clearPlotWidgets()

      # Getting the filename from the dialog window
      filename=QFileDialog.getOpenFileName(self, 'Open file', '', '')
      self.backend.openedFilename = filename[0]

      # Reading the file content
      self.backend.openAudioFile()
      
      # Adding the spectrogram
      self.spectrogram_widget.clearCanvas()
      self.freq_resp_widget.clearCanvas()
      self.backend.calculateSpectrogram()
      self.addFrequencyResponse()
      self.addSpectrogram()
      self.spectrogram_widget.updateAxes()
      self.freq_resp_widget.updateAxes()


   def saveFileWithCurrentName(self):
      print("Classic save functionality, overrides the file content, keeps the name")

   def saveFileWithAnotherName(self):
      print("Classic save functionality, overrides the file content, keeps the name")

   def exportPlots(self):
      name = QFileDialog.getSaveFileName(self, 'Save File')
      self.sc.fig.savefig(str(name[0]))

   def saveFileWithSelectedTimestamp(self):
      print("Saves the selected timestamp")
   
   def saveAudioChannelsSeparately(self):
      print("Saves audio channels into separate files")

   ###################
   # Editing methods #
   ###################

   def selectTimestamp(self):
      print("Allows selecting of the timestamp")

   def selectWholeFile(self):
      print("Selects whole file")

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

   def saveRecordedAudio(self):
      print("")

   def startOrStopAudioRecording(self, s):
      print("Starts or pauses the recording, current checked value is = {a}".format(a=s))

   #######################
   # Spectrogram methods #
   #######################

   # 
   def createSpectrogramGraph(self):
      # If there are more than one channels in the file, i will create two spectrograms instead

      self.backend.calculateSpectrogram()

      if self.displayingMonoSpectrogram is True:
         self.mono_spectrogram.axes.clearCanvas()
         self.displayingMonoSpectrogram = False
      elif self.displayingStereoSpectrogram is True:
         self.left_channel_spectrogram.axes.clearCanvas()
         self.right_channel_spectrogram.axes.clearCanvas()
         self.displayingStereoSpectrogram = False
         



      if self.backend.monoChannelFile is True:
         #self.mono_spectrogram.axes.specgram(self.backend.channel_1, Fs=self.backend.fs, )
         self.mono_spectrogram.axes.pcolormesh(self.backend.segm, self.backend.freq, self.backend.sxx)
         #self.mono_spectrogram.axes.set_xticklabels([])
         #self.mono_spectrogram.axes.set_yticklabels([])
         #self.mono_spectrogram.axes.set_xticks([])
         #self.mono_spectrogram.axes.set_yticks([])
         #self.mono_spectrogram.fig.tight_layout()
         self.layout.addWidget(self.mono_spectrogram, 0, 0, 48, 32, Qt.AlignmentFlag.AlignTop)
         self.displayingMonoSpectrogram = True
         
      if self.backend.stereoChannelFile is True:
         self.left_channel_spectrogram.axes.specgram(self.backend.channel_1, Fs=self.backend.fs, )
         self.left_channel_spectrogram.axes.set_xticklabels([])
         self.left_channel_spectrogram.axes.set_yticklabels([])
         self.left_channel_spectrogram.axes.set_xticks([])
         self.left_channel_spectrogram.axes.set_yticks([])
         self.left_channel_spectrogram.fig.tight_layout()
         self.layout.addWidget(self.left_channel_spectrogram, 0, 0, 48, 16, Qt.AlignmentFlag.AlignTop)

         self.right_channel_spectrogram.axes.specgram(self.backend.channel_2, Fs=self.backend.fs, )
         self.right_channel_spectrogram.axes.set_xticklabels([])
         self.right_channel_spectrogram.axes.set_yticklabels([])
         self.right_channel_spectrogram.axes.set_xticks([])
         self.right_channel_spectrogram.axes.set_yticks([])
         self.right_channel_spectrogram.fig.tight_layout()
         self.layout.addWidget(self.right_channel_spectrogram, 0, 16, 48, 16, Qt.AlignmentFlag.AlignTop)
         self.displayingStereoSpectrogram = True


   ## Window functions
   def setRectangularWindowFunction(self):
      print("Sets triangular window function")

   #######################################
   # Spectral Power Distribution methods #
   #######################################

   def createSpectralPowerDistributionGraph(self):
      print("")

   ################
   # Help methods #
   ################

   def displayProgramInfo(self):
      print("Displays usefull information")

   #######################
   # GUI backend methods #
   #######################
   
   def toolbarWindowSelector(self, index):
      print(f"Something was clicked on the combobo, {self.backend.listOfWindows[index]}")
      self.backend.choosenWindow = self.backend.listOfWindows[index]

      self.spectrogram_widget.clearCanvas()
      self.backend.calculateSpectrogram()
      self.addSpectrogram()
      self.spectrogram_widget.updateAxes()

   def toolbarSpectrogramRangeSelector(self, index):
      self.backend.chooseSpectrumWidth(index)

      self.spectrogram_widget.clearCanvas()
      self.backend.calculateSpectrogram()
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
