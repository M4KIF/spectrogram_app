
#############################################################################
# The backend of the spectrogram app, containing all of the needed maths    #
# and modules that are neccessary to give the signal analysis functionality #
#############################################################################


###########
# Imports #
###########


import scipy.io.wavfile as wavfile
import numpy as np
import math
from scipy import signal


################################################################
# Main logic object class, created as a singleton just in case #
################################################################


class appLogic():

   # Creates a new instance of the class
   def __new__(object):
      if not hasattr(object, 'instance'):
         object.instance = super(appLogic, object).__new__(object)
      return object.instance

   # Initialises the default values
   def __init__(self):

      ######################################
      # Defining needed runtime variables  #
      ######################################

      # Lists of selectable options
      self.m_ListOfWindowFunctions = ["tukey", "triang", "flattop", "exponential"]
      self.m_SpectrogramBand = ["Narrow", "Wide"]

      # Passed filename
      self.m_ObtainedFileName = str()

      # Default window is set as the first item from the list
      self.m_CurrentWindowFunction = self.m_ListOfWindowFunctions[0]

      # Contains the length of the file in samples
      self.m_FileSampleCount = None

      # Contains the first sample of the segment, default = 0
      self.m_FirstSelectedSample = None

      # Contains the last sapmple of the segment, default = m_FileSampleCount
      self.m_LastSelectedSample = None

      # The value of the narrowband spectrogram window length
      self.m_NarrowWindow = None

      # The value of the wideband spectrogram window length
      self.m_WideWindow = None

      #############################
      # File properties variables #
      #############################

      # How wide is the window used by window function (in samples)
      self.m_WindowLength = None

      # How much samples do the windows overlap 
      self.m_WindowOverlap = None

      # Default value equal to 10%
      self.m_DefaultWindowOverlapPercent = 10

      ######################
      # Spectrogram values #
      ######################

      # Numpy arrays containing sample frequency values
      self.m_Freq_1 = None
      self.m_Freq_2 = None

      # Numpy arrays containing time segments for the spectrogram
      self.m_Time_1 = None
      self.m_Time_2 = None

      # Numpy arrays containing spectrogram values
      self.m_Spectrogram_1 = None
      self.m_Spectrogram_2 = None

      #################
      # Boolean flags #
      #################

      # State of the file flags
      self.m_FileOpened = False
      self.m_SegmentSelected = False

      # Opened file channel count flags
      self.m_MonoChannelHandled = False
      self.m_StereoChannelsHandled  = False

      # FFT(Fast Fourier Transform) parameters flags
      self.m_WindowFunctionSelected = False
      self.m_OverlapSelected = False
      self.m_WindowLengthsCalculated = False
      self.m_SpectrogramBandSelected = False


######################################################################################


   #####################
   # Setters / Getters #
   #####################


   # Changes the currently set window function
   def setWindowFunction(self, index=0):

      # Check if the passed argument is correct
      if type(index) != int:
         raise TypeError("Incorrect type of the argument argument")
      elif index > len(self.m_ListOfWindowFunctions):
         raise ValueError("The index is out of range of the window functions list")
      else:
         self.m_CurrentWindowFunction = self.m_ListOfWindowFunctions[index]


   # Changes the currently set sepctrogram band mode
   def setSpectrogramBand(self, index=0):

      if type(index) != int:
         raise TypeError("Incorrect type of the argument argument")
      elif index != 0 or index !=1:
         raise ValueError("Index out of list range")
      else:
         # Checks if the window length has been calculated earlier
         if self.m_WindowLengthsCalculated:
            if index == 0:
               # Calculating the narrowband window length > 2 * n-samples/sampling frequency
               self.m_WindowLength = self.m_NarrowWindow 
            elif index == 1:
               # Calculating the wideband window length < n-samples/sampling frequency
               self.m_WindowLength = self.m_WideWindow
         else:
            raise RuntimeError("Window length cannot be selected without first calculating it")


   # Resets the segment indexes to default values according to the file data
   def setDefaultFileSegment(self):

      if self.m_FileOpened:
         # If the file has been opened - sets the range to the whole file
         self.m_FirstSelectedSample = 0
         self.m_LastSelectedSample = self.m_FileSampleCount


   # Sets the file segment after checking the safety statements
   def setFileSegment(self, start=None, end=None):

      if start == None or end == None:
         raise SyntaxError("Incorrect parameters")
      elif type(start)!=int or type(end)!=int:
         raise TypeError("Incorrect parameters")
      elif start > end or (start == 0 and end == 0):

         # Resets to default values
         if self.m_FileOpened:
            self.setDefaultFileSegment()
         else:
            raise RuntimeError("File hasn't been opened yet")
      else:
         self.m_FirstSelectedSample = start
         self.m_LastSelectedSample = end


   # Sets the default overlap value
   def setDefaulWindowOverlap(self):
      
      if self.m_WindowLengthsCalculated and self.m_SpectrogramBandSelected:
         # Calculates the overlap with a safety rounding to prevent the overlap from reaching 0
         self.m_WindowOverlap = int(math.ceil(self.m_WindowLength * self.m_DefaultWindowOverlapPercent / 100))
      else:
         raise RuntimeError("Cannot set overlap")


   # Return currently used window function
   def getWindowFunction(self):
      return self.m_CurrentWindowFunction

   
   # Return currently used spectrogram type
   def getSpectrogramBand(self):
      return self.m_SpectrogramBand


   # Returns a tuple of currently selected range
   def getDefaultFileSegment(self):
      return (0, self.m_FileSampleCount)


   


   # Sets the overlap of the windows for the FFT calculations
   def setWindowOverlap(self, percent=None):

      # If the value is in fact a percentile value
      if percent==None:
         raise SyntaxError("No parameters passed")
      elif type(percent)!=int:
         raise TypeError("Incorrect type")
      elif percent > 0 and percent <= 100:

         if self.m_WindowLengthsCalculated:
            # Calculates the overlap with a safety rounding to prevent the overlap from reaching 0
            self.m_WindowOverlap = int(math.ceil(self.m_WindowLength * percent / 100))
         else:
            raise RuntimeError("Window Length hasn't been calculated")
      else:
         self.setDefaulWindowOverlap()


   # Opening an audio file with the given name
   def openAudioFile(self, filename=None):

      # Setting the name of the currently active file
      self.m_ObtainedFileName = filename

      # Checking if any name has been passed
      if self.m_ObtainedFileName == None:
         

      self.fs, self.file = wavfile.read(self.m_ObtainedFileName)
      self.fileOpened = True

      self.m_LastSelectedSample = self.m_FileSampleCount = len(self.file)
      self.m_FirstSelectedSample = 0
      
      if np.ndim(self.file) > 1:
         self.m_StereoChannelsHandled  = True
         self.m_MonoChannelHandled = False

         self.channel_1 = self.file[:,0]
         self.channel_2 = self.file[:,1]
      else:
         self.m_MonoChannelHandled = True
         self.m_StereoChannelsHandled  = False

         self.channel_1 = self.file

      # Calculating the matching window lengths for the wide/narrow spectrogram
      self.calculateWindowLengths()

      self.chooseRange()

      self.setOverlap()

      # Setting the narrow spectrogram as default
      self.m_WindowLength = self.m_NarrowWindow

      # Calculating the timespace array
      self.time = np.linspace(0, len(self.channel_1)/self.fs, num=len(self.channel_1))

   def editRange(self, start=None, end=None):
      if end != 0:
         self.m_FirstSelectedSample = start
         self.m_LastSelectedSample = end
      else:
         self.m_FirstSelectedSample = 0
         self.m_LastSelectedSample = self.m_FileSampleCount


   # The default window overlap is set to 10%
   def setOverlap(self, value=10):
      # If the value is in fact a percentile value
      if value > 0 and value <= 100:
         # Calculates the overlap with a safety rounding to prevent the overlap from reaching 0
         self.m_WindowOverlap = int(math.ceil(self.m_WindowLength * value / 100))

      else:
         # If it isn't setting to default 10%
         self.m_WindowOverlap = int(math.ceil(self.m_WindowLength/10))

      print(self.m_WindowOverlap)


   def calculateWindowLengths(self):
      # Calculating the narrowband window length > 2 * n-samples/sampling frequency
      self.m_NarrowWindow = int(0.035 * self.fs)
      # Calculating the wideband window length < n-samples/sampling frequency
      self.m_WideWindow = int(0.004 * self.fs)

   def chooseRange(self, index=0):
      # Selecting the right window
      if index == 0:
         # Calculating the narrowband window length > 2 * n-samples/sampling frequency
         self.m_WindowLength = self.m_NarrowWindow 
      elif index == 1:
         # Calculating the wideband window length < n-samples/sampling frequency
         self.m_WindowLength = self.m_WideWindow


   def calculateSpectrogram(self, min_index=None, max_index=None):

      print(f"Here comes the error {self.m_WindowLength}, and narr {self.m_NarrowWindow} or wide {self.m_WideWindow}")
      print(f"{self.m_LastSelectedSample-self.m_FirstSelectedSample}")
      if self.m_WindowLength == self.m_WindowOverlap:
         self.m_WindowLength+=1

      if self.mono:
         self.m_Freq_1, self.m_Time_1, self.m_Spectrogram_1 = signal.spectrogram(self.channel_1[self.m_FirstSelectedSample:self.m_LastSelectedSample], self.fs, window=signal.get_window(self.m_CurrentWindowFunction, self.m_WindowLength), nperseg=self.m_WindowLength, noverlap=self.m_WindowOverlap)
         self.m_Spectrogram_1 = np.log(self.m_Spectrogram_1)
      elif self.m_StereoChannelsHandled :
         self.m_Freq_1, self.m_Time_1, self.m_Spectrogram_1 = signal.spectrogram(self.channel_1[self.m_FirstSelectedSample:self.m_LastSelectedSample], self.fs, window=signal.get_window(self.m_CurrentWindowFunction, self.m_WindowLength), nperseg=self.m_WindowLength, noverlap=self.m_WindowOverlap)
         self.m_Freq_2, self.m_Time_2, self.m_Spectrogram_2 = signal.spectrogram(self.channel_2[self.m_FirstSelectedSample:self.m_LastSelectedSample], self.fs, window=signal.get_window(self.m_CurrentWindowFunction, self.m_WindowLength), nperseg=self.m_WindowLength, noverlap=self.m_WindowOverlap)
         self.m_Spectrogram_1 = np.log(self.m_Spectrogram_1)
         self.m_Spectrogram_2 = np.log(self.m_Spectrogram_2)
      

