
#############################################################################
# The backend of the spectrogram app, containing all of the needed maths    #
# and modules that are neccessary to give the signal analysis functionality #
#############################################################################


###########
# Imports #
###########


# For plot data creation and storage
import scipy.io.wavfile as wavfile
from scipy import signal
import numpy as np

# Audio playback and recording
import pyaudio as pa
import wave 

# Threading support
from PyQt5.QtCore import pyqtSignal, QObject, QMutex

# Miscelanous
import math


# Mutex object for securing the critical data
mutex = QMutex()


################################################################
# Main logic object class, created as a singleton just in case #
################################################################


class appLogic(QObject):

   # Those are signals to be emitted from the main section. Here they will be captured
   set_filename = pyqtSignal(str)
   set_window_function = pyqtSignal(int)
   set_spectrogram_band = pyqtSignal(int)
   set_file_segment = pyqtSignal([int, int])
   set_window_overlap_percentage = pyqtSignal(int)

   # Those are signals to be emitted from the main section. Here they will be captured
   get_window_function_list = pyqtSignal()
   get_spectrogram_bands_list = pyqtSignal()
   get_window_function = pyqtSignal()
   get_spectrogram_band = pyqtSignal()
   get_file_segment = pyqtSignal()
   get_overlap_percentage = pyqtSignal()
   get_file_data = pyqtSignal()
   get_time_data = pyqtSignal()
   get_channel_data = pyqtSignal()
   get_file_status = pyqtSignal()
   get_mono_status = pyqtSignal()
   get_stereo_status = pyqtSignal()

   send_window_function_list = pyqtSignal(list)
   send_spectrogram_bands_list = pyqtSignal(list)
   send_window_function = pyqtSignal(str)
   send_spectrogram_band = pyqtSignal(str)
   send_file_segment = pyqtSignal(list)
   send_overlap_percentage = pyqtSignal(int)
   send_file_data = pyqtSignal(np.ndarray)
   send_time_data = pyqtSignal(np.ndarray)
   send_channel_data = pyqtSignal(list)
   send_file_status = pyqtSignal(bool)
   send_mono_status = pyqtSignal(bool)
   send_stereo_status = pyqtSignal(bool)

   play_audio = pyqtSignal()
   pause_audio = pyqtSignal()
   stop_audio = pyqtSignal()
   playback_status = pyqtSignal()

   # 
   open_file = pyqtSignal(str)

   # Emitted from the main section of the program and captured here
   prepare_freq_response_data = pyqtSignal()
   prepare_spectrogram_data = pyqtSignal()
   prepare_spectral_dist_data = pyqtSignal()

   # 
   freq_response_data_ready = pyqtSignal(list)
   spectrogram_data_ready = pyqtSignal(list)
   spectral_distribution_data_ready = pyqtSignal(list)

   # Creates a new instance of the class
   def __new__(object):
      if not hasattr(object, 'instance'):
         object.instance = super(appLogic, object).__new__(object)
      return object.instance

   # Initialises the default values
   def __init__(self):
      super().__init__()
      
      ##########################
      # Connecting the signals #
      ##########################

      self.set_filename.connect(self.setFileName)
      self.set_window_function.connect(self.setWindowFunction)
      self.set_spectrogram_band.connect(self.setSpectrogramBand)
      self.set_file_segment.connect(self.setFileSegment)
      self.set_window_overlap_percentage.connect(self.setWindowOverlapPercentage)
      
      self.get_window_function_list.connect(self.getWindowFunctionsList)
      self.get_spectrogram_bands_list.connect(self.getSpectrogramBandsList)
      self.get_window_function.connect(self.getWindowFunction)
      self.get_spectrogram_band.connect(self.getSpectrogramBand)
      self.get_file_segment.connect(self.getFileSegment)
      self.get_overlap_percentage.connect(self.getOverlapPercentage)
      self.get_file_data.connect(self.getFileData)
      self.get_time_data.connect(self.getFileTimeData)
      self.get_channel_data.connect(self.getChannelData)
      self.get_file_data.connect(self.getFileStatus)
      self.get_mono_status.connect(self.getMonoStatus)
      self.get_stereo_status.connect(self.getStereoStatus)

      self.open_file.connect(self.openFile)

      self.prepare_freq_response_data.connect(self.calculateFrequencyResponse)
      self.prepare_spectrogram_data.connect(self.calculateSpectrogram)
      self.prepare_spectral_dist_data.connect(self.calculateSpectralDistribution)

      ######################################
      # Defining needed runtime variables  #
      ######################################

      # Lists of selectable options
      self.m_ListOfWindowFunctions = ["tukey", "triang", "flattop", "exponential"]
      self.m_ListOfFilters = []
      self.m_SpectrogramBand = ["Narrow", "Wide"]

      ##################
      # File variables #
      ##################

      # Passed filename
      self.m_ObtainedFileName = str()

      # File data
      self.m_Data = None

      # Sampling frequency of the file
      self.m_SamplingFrequency = None

      # Time segments array
      self.m_TimeSegments = None

      # Divided into first channel
      self.m_Channel_1_Data = None

      # And the second channel if exists
      self.m_Channel_2_Data = None

      # Contains the length of the file in samples
      self.m_FileSampleCount = None

      # Contains the first sample of the segment, default = 0
      self.m_FirstSelectedSample = None

      # Contains the last sapmple of the segment, default = m_FileSampleCount
      self.m_LastSelectedSample = None

      ############################
      # FFT properties variables #
      ############################

      # How wide is the window used by window function (in samples)
      self.m_WindowLength = None

      # The value of the narrowband spectrogram window length
      self.m_NarrowWindow = None

      # The value of the wideband spectrogram window length
      self.m_WideWindow = None

      # How much samples do the windows overlap 
      self.m_WindowOverlap = None

      # Default value equal to 10%
      self.m_DefaultWindowOverlapPercentage = 10
      self.m_CurrentWindowOverlapPercentage = None

      #########################
      # Spectrogram variables #
      #########################

      # Default window is set as the first item from the list
      self.m_CurrentWindowFunction = self.m_ListOfWindowFunctions[0]

      # Default spectrogram band
      self.m_CurrentSpectrogramBand = self.m_SpectrogramBand[0]

      # Numpy arrays containing sample frequency values
      self.m_Freq_1 = None
      self.m_Freq_2 = None

      # Numpy arrays containing time segments for the spectrogram
      self.m_Time_1 = None
      self.m_Time_2 = None

      # Numpy arrays containing spectrogram values
      self.m_Spectrogram_1 = None
      self.m_Spectrogram_2 = None

      #####################
      # For file creation #
      #####################

      # I dont know what it means
      self.m_Chunk = None

      # The pyaudio module backend stuff
      self.m_SampleFormat = None

      # The amount of channels to record, either mono, or stereo
      self.m_ChannelsToRecord = None

      # Contains the sampling rate
      self.m_RecordSamplingFrequency = None

      # Also dont know what it means
      self.m_SecondsStored = None

      # Contains the audio interface that will be used for recording
      self.m_AudioInterface = None

      #################
      # Boolean flags #
      #################

      # State of the file flags
      self.mb_FileOpened = False
      self.mb_SegmentSelected = False

      # Opened file channel count flags
      self.mb_MonoChannelHandled = False
      self.mb_StereoChannelsHandled  = False

      # FFT(Fast Fourier Transform) parameters flags
      self.mb_WindowFunctionSelected = False
      self.mb_OverlapSelected = False
      self.mb_OverlapCalculated = False
      self.mb_WindowLengthsCalculated = False
      self.mb_SpectrogramBandSelected = False


######################################################################################


   #####################
   # Setters / Getters #
   #####################


   def setFileName(self, filename=str()):
      self.m_ObtainedFileName = filename


   # Changes the currently set window function
   def setWindowFunction(self, index=0):

      # Check if the passed argument is correct
      if type(index) != int:
         raise TypeError("Incorrect type of the argument argument")
      elif index > len(self.m_ListOfWindowFunctions):
         raise ValueError("The index is out of range of the window functions list")
      else:
         mutex.lock()

         self.m_CurrentWindowFunction = self.m_ListOfWindowFunctions[index]

         # Activating the flag
         self.mb_WindowFunctionSelected = True

         mutex.unlock()


   # Changes the currently set sepctrogram band mode
   def setSpectrogramBand(self, index=int(0)):

      if type(index) != int:
         raise TypeError("Incorrect type of the argument argument")
      elif index != 0 and index !=1:
         raise ValueError("Index out of list range")
      else:
         mutex.lock()

         self.m_CurrentSpectrogramBand = self.m_SpectrogramBand[index]

         # Activating the flag
         self.mb_SpectrogramBandSelected = True

         mutex.unlock()


   # Resets the segment indexes to default values according to the file data
   def setDefaultFileSegment(self):

      if self.mb_FileOpened:

         # Activating the flag
         self.mb_SegmentSelected = True

         # If the file has been opened - sets the range to the whole file
         self.m_FirstSelectedSample = 0
         self.m_LastSelectedSample = self.m_FileSampleCount


   # Sets the file segment after checking the safety statements
   def setFileSegment(self, start=None, end=None):

      if type(start)!=int and type(end)!=int:
         raise TypeError("Incorrect parameters")
      elif start > end or (start == 0 and end == 0):
         mutex.lock()

         # Resets to default values
         if self.mb_FileOpened:
            self.setDefaultFileSegment()
         else:
            raise RuntimeError("File hasn't been opened yet")

         mutex.unlock()
      else:
         mutex.lock()
         
         # Activating the flag
         self.mb_SegmentSelected = True

         # Settting the values 
         self.m_FirstSelectedSample = start
         self.m_LastSelectedSample = end

         # If the segment happens to be shorter than the window
         if self.mb_WindowLengthsCalculated:
            if (end - start) < self.m_WindowLength:
               self.setDefaultFileSegment()
         
         mutex.unlock()


   # Sets the default overlap value
   def setDefaulWindowOverlapPercentage(self):
      mutex.lock()
      self.m_CurrentWindowOverlapPercentage = self.m_DefaultWindowOverlapPercentage
      self.mb_OverlapSelected = True
      mutex.unlock()


   # Sets the overlap of the windows for the FFT calculations
   def setWindowOverlapPercentage(self, percent=None):

      # If the value is in fact a percentile value
      if percent==None:
         raise SyntaxError("No parameters passed")
      elif type(percent)!=int:
         raise TypeError("Incorrect type")
      elif percent > 0 and percent <= 100:
         mutex.lock()
         self.m_CurrentWindowOverlapPercentage = percent
         self.mb_OverlapSelected = True
         mutex.unlock()
      else:
         self.setDefaulWindowOverlapPercentage()


   # Returns the list of windows used in here
   def getWindowFunctionsList(self):
      
      # Emititng the signal with data
      self.send_window_function_list.emit(self.m_ListOfWindowFunctions)

      return self.m_ListOfWindowFunctions


   # Returns the list of band of the spectrogram
   def getSpectrogramBandsList(self):

      # Emititng the signal with data
      self.send_spectrogram_bands_list.emit(self.m_SpectrogramBand)

      return self.m_SpectrogramBand


   # Return currently used window function
   def getWindowFunction(self):

      # Emititng the signal with data
      self.send_window_function.emit(self.m_CurrentWindowFunction)

      return self.m_CurrentWindowFunction

   
   # Return currently used spectrogram type
   def getSpectrogramBand(self):

      # Emititng the signal with data
      self.send_spectrogram_band.emit(self.m_CurrentSpectrogramBand)

      return self.m_CurrentSpectrogramBand


   # Returns a tuple of default range
   def getDefaultFileSegment(self):
      return [0, self.m_FileSampleCount]


   # Return a tuple of currently selected range
   def getFileSegment(self):

      # Emititng the signal with data
      self.send_file_segment.emit([self.m_FirstSelectedSample, self.m_LastSelectedSample])

      return [self.m_FirstSelectedSample, self.m_LastSelectedSample]


   # Returns the default overlap value
   def getDefaultOverlapValue(self):
      return self.m_DefaultWindowOverlapPercentage

   
   def getOverlapPercentage(self):

      # Emititng the signal with data
      self.send_overlap_percentage.emit(self.m_DefaultWindowOverlapPercentage)
      
      return self.m_CurrentWindowOverlapPercentage


   def getFileData(self):

      # Emititng the signal with data
      self.send_file_data.emit(self.m_Data)

      return self.m_Data


   def getFileTimeData(self):

      # Emititng the signal with data
      self.send_time_data.emit(self.m_TimeSegments)

      return self.m_TimeSegments

   def getChannelData(self):

      # Emititng the signal with data
      self.send_channel_data.emit([[self.m_Freq_1, self.m_Time_1, self.m_Spectrogram_1], [self.m_Freq_2, self.m_Time_2, self.m_Spectrogram_2]])

      return [[self.m_Freq_1, self.m_Time_1, self.m_Spectrogram_1], [self.m_Freq_2, self.m_Time_2, self.m_Spectrogram_2]]


   def getFirstChannelData(self):
      return self.m_Channel_1_Data

   
   def getFirstChannelTimeSegments(self):
      return self.m_Time_1

   
   def getFirstChannelFrequencySamples(self):
      return self.m_Freq_1


   def getFirstChannelSpectrogramData(self):
      return self.m_Spectrogram_1


   def getSecondChannelTimeSegments(self):
      return self.m_Time_2

   
   def getSecondChannelFrequencySamples(self):
      return self.m_Freq_2


   def getSecondChannelSpectrogramData(self):
      return self.m_Spectrogram_2


   def getSecondChannelData(self):
      return self.m_Channel_2_Data


   def getFileStatus(self):

      # Emititng the signal with data
      self.send_file_status.emit(self.mb_FileOpened)

      return self.mb_FileOpened


   def getMonoStatus(self):

      # Emititng the signal with data
      self.send_mono_status.emit(self.mb_MonoChannelHandled)

      return self.mb_MonoChannelHandled


   def getStereoStatus(self):
      # Emititng the signal with data
      self.send_stereo_status.emit(self.mb_StereoChannelsHandled)

      return self.mb_StereoChannelsHandled

   
##################################################################


   # Set the values needed for audio recording
   def createFile(self, chunksize=1024, sampleformat=pa.paInt16, channels=2, fs=44100, seconds=3):
      self.m_Chunk = chunksize
      self.m_SampleFormat = sampleformat
      self.m_ChannelsToRecord = channels
      self.m_RecordSamplingFrequency = fs
      self.m_SecondsStored = seconds

      self.m_AudioInterface = pa.PyAudio()


   # Opens and reads the file
   def openFile(self, filename=None):

      # Checking if the filename is correct
      if filename == None:
         raise SyntaxError("Incorrect parameters")
      elif type(filename)!=str:
         raise TypeError("Incorrect parameters")
      else:
         mutex.lock()
         # Setting the name of the currently active file
         self.m_ObtainedFileName = filename
         mutex.unlock()
         
      try:
         mutex.lock()
         self.m_SamplingFrequency, self.m_Data = wavfile.read(self.m_ObtainedFileName)
         mutex.unlock()
      except:
         raise RuntimeError("Could't open the file")
      else:
         mutex.lock()

         # Getting the length of the file
         self.m_FileSampleCount = len(self.m_Data)

         # Setting the default file segment
         self.setDefaultFileSegment()

         # Checking if the number of dimmensions of the array corresponds to stereo or mono audio data
         if np.ndim(self.m_Data) > 1:
            # Setting flags accordingly
            self.mb_StereoChannelsHandled  = True
            self.mb_MonoChannelHandled = False

            # Dividing the data into channels
            self.m_Channel_1_Data = self.m_Data[:,0]
            self.m_Channel_2_Data = self.m_Data[:,1]
         else:
            # Setting flags accordingly
            self.mb_MonoChannelHandled = True
            self.mb_StereoChannelsHandled  = False

            # Division of the data not needed
            self.m_Channel_1_Data = self.m_Data

         self.m_TimeSegments = np.linspace(0, len(self.m_Channel_1_Data)/self.m_SamplingFrequency, num=len(self.m_Channel_1_Data))

         mutex.unlock()

         # Activating the flag that informs about the opened file
         self.mb_FileOpened = True

         ###########################
         # Calling setup functions #
         ###########################

         self.setSpectrogramBand()
         self.setWindowFunction()
         self.setDefaulWindowOverlapPercentage()

         #####################################
         # Calling the calculating functions #
         #####################################

         self.calculateSpectrogramParameters()


   # Writes to the current name if no name is present in the logic, raises an exception
   def saveFile(self):
      if self.m_ObtainedFileName == None:
         raise RuntimeError("No filename selected")
      elif self.mb_FileOpened == False:
         raise RuntimeError("File not opened")


   # Gives the opportunity to change the name of the file before saving
   def saveFileAs(self, filename=str()):
      self.setFileName(filename)
      return


   # Imitates the closage of the file by deactivating the flags
   def closeFile(self):
      mutex.lock()
      self.mb_FileOpened = False
      self.mb_MonoChannelHandled = False
      self.mb_StereoChannelsHandled = False
      self.mb_SegmentSelected = False
      self.mb_SpectrogramBandSelected = False
      self.mb_WindowFunctionSelected = False
      self.mb_OverlapSelected = False
      mutex.unlock()


   # Calculates the window length 
   def calculateWindowLength(self):

      # If the window lengths haven't been calculated before
      if self.mb_WindowLengthsCalculated == False:
         mutex.lock()
         # Calculating the narrowband window length > 2 * n-samples/sampling frequency
         self.m_NarrowWindow = int(0.035 * self.m_SamplingFrequency)
         # Calculating the wideband window length < n-samples/sampling frequency
         self.m_WideWindow = int(0.004 * self.m_SamplingFrequency)

         # Activating the flag
         self.mb_WindowLengthsCalculated = True
         mutex.unlock()

      # Checks if the spectrogram band type has been selected
      if self.mb_SpectrogramBandSelected:
         mutex.lock()
         if self.m_CurrentSpectrogramBand == self.m_SpectrogramBand[0]:
            # Calculating the narrowband window length > 2 * n-samples/sampling frequency
            self.m_WindowLength = self.m_NarrowWindow 
            
         elif self.m_CurrentSpectrogramBand == self.m_SpectrogramBand[1]:
            # Calculating the wideband window length < n-samples/sampling frequency
            self.m_WindowLength = self.m_WideWindow
         mutex.unlock()


   # Calculates window overlap
   def calculateWindowOverlap(self):

      if self.mb_WindowLengthsCalculated and self.mb_SpectrogramBandSelected:
         # Calculates the overlap with a safety rounding to prevent the overlap from reaching 0
         #temp = int(math.ceil(self.m_WindowLength * self.m_CurrentWindowOverlapPercentage / 100))
         mutex.lock()
         self.m_WindowOverlap = int((self.m_WindowLength * self.m_CurrentWindowOverlapPercentage / 100))
         
         if self.m_WindowLength <= self.m_WindowOverlap:
            self.m_WindowOverlap = self.m_WindowLength - 1
         mutex.unlock()

         print(f"Overlap = {self.m_WindowOverlap}")
         print(f"Length = {self.m_WindowLength}")
      else:
         raise RuntimeError("Cannot set overlap")


   def calculateFrequencyResponse(self):
      
      self.freq_response_data_ready.emit([self.m_Data, self.m_TimeSegments])

   
   # Calculates a spectrogram using all the data that is stored in this object
   def calculateSpectrogram(self):

      # Calculating needed data
      self.calculateSpectrogramParameters()

      # Checking if the conditions are met
      if not self.mb_FileOpened:
         raise RuntimeError("File not read")
      elif not self.mb_SpectrogramBandSelected:
         raise RuntimeError("Spectrogram band not selected")
      elif not self.mb_WindowFunctionSelected:
         raise RuntimeError("Window function not selected")
      elif not self.mb_WindowLengthsCalculated:
         raise RuntimeError("Window lenghts not calculated")

      # Calculating the spectrogram
      mutex.lock()
      if self.mb_MonoChannelHandled:
         self.m_Freq_1, self.m_Time_1, self.m_Spectrogram_1 = signal.spectrogram(self.m_Channel_1_Data[self.m_FirstSelectedSample:self.m_LastSelectedSample], self.m_SamplingFrequency, window=signal.get_window(self.m_CurrentWindowFunction, self.m_WindowLength), nperseg=self.m_WindowLength, noverlap=self.m_WindowOverlap)
         self.m_Spectrogram_1 = np.log(self.m_Spectrogram_1)

      elif self.mb_StereoChannelsHandled :
         self.m_Freq_1, self.m_Time_1, self.m_Spectrogram_1 = signal.spectrogram(self.m_Channel_1_Data[self.m_FirstSelectedSample:self.m_LastSelectedSample], self.m_SamplingFrequency, window=signal.get_window(self.m_CurrentWindowFunction, self.m_WindowLength), nperseg=self.m_WindowLength, noverlap=self.m_WindowOverlap)
         self.m_Freq_2, self.m_Time_2, self.m_Spectrogram_2 = signal.spectrogram(self.m_Channel_2_Data[self.m_FirstSelectedSample:self.m_LastSelectedSample], self.m_SamplingFrequency, window=signal.get_window(self.m_CurrentWindowFunction, self.m_WindowLength), nperseg=self.m_WindowLength, noverlap=self.m_WindowOverlap)
         self.m_Spectrogram_1 = np.log(self.m_Spectrogram_1)
         self.m_Spectrogram_2 = np.log(self.m_Spectrogram_2)
      mutex.unlock()

      self.spectrogram_data_ready.emit([[self.m_Freq_1, self.m_Time_1, self.m_Spectrogram_1], [self.m_Freq_2, self.m_Time_2, self.m_Spectrogram_2]])


   def calculateSpectralDistribution(self):
      
      self.spectral_distribution_data_ready.emit([])


   def calculateSpectrogramParameters(self):
      #
      self.calculateWindowLength()
      self.calculateWindowOverlap()


####################################################################################


   # Opening an audio file with the given name

   def editRnge(self, start=None, end=None):
      if end != 0:
         self.m_FirstSelectedSample = start
         self.m_LastSelectedSample = end
      else:
         self.m_FirstSelectedSample = 0
         self.m_LastSelectedSample = self.m_FileSampleCount


   # The default window overlap is set to 10%
   def setOvelap(self, value=10):
      # If the value is in fact a percentile value
      if value > 0 and value <= 100:
         # Calculates the overlap with a safety rounding to prevent the overlap from reaching 0
         self.m_WindowOverlap = int(math.ceil(self.m_WindowLength * value / 100))

      else:
         # If it isn't setting to default 10%
         self.m_WindowOverlap = int(math.ceil(self.m_WindowLength/10))

      print(self.m_WindowOverlap)


   def calculateWidowLengths(self):
      # Calculating the narrowband window length > 2 * n-samples/sampling frequency
      self.m_NarrowWindow = int(0.035 * self.m_SamplingFrequency)
      # Calculating the wideband window length < n-samples/sampling frequency
      self.m_WideWindow = int(0.004 * self.m_SamplingFrequency)

   def chooseRnge(self, index=0):
      # Selecting the right window
      if index == 0:
         # Calculating the narrowband window length > 2 * n-samples/sampling frequency
         self.m_WindowLength = self.m_NarrowWindow 
      elif index == 1:
         # Calculating the wideband window length < n-samples/sampling frequency
         self.m_WindowLength = self.m_WideWindow


   def calculateSpectogram(self, min_index=None, max_index=None):

      print(f"Here comes the error {self.m_WindowLength}, and narr {self.m_NarrowWindow} or wide {self.m_WideWindow}")
      print(f"{self.m_LastSelectedSample-self.m_FirstSelectedSample}")
      if self.m_WindowLength == self.m_WindowOverlap:
         self.m_WindowLength+=1

      if self.mono:
         self.m_Freq_1, self.m_Time_1, self.m_Spectrogram_1 = signal.spectrogram(self.channel_1[self.m_FirstSelectedSample:self.m_LastSelectedSample], self.m_SamplingFrequency, window=signal.get_window(self.m_CurrentWindowFunction, self.m_WindowLength), nperseg=self.m_WindowLength, noverlap=self.m_WindowOverlap)
         self.m_Spectrogram_1 = np.log(self.m_Spectrogram_1)
      elif self.mb_StereoChannelsHandled :
         self.m_Freq_1, self.m_Time_1, self.m_Spectrogram_1 = signal.spectrogram(self.channel_1[self.m_FirstSelectedSample:self.m_LastSelectedSample], self.m_SamplingFrequency, window=signal.get_window(self.m_CurrentWindowFunction, self.m_WindowLength), nperseg=self.m_WindowLength, noverlap=self.m_WindowOverlap)
         self.m_Freq_2, self.m_Time_2, self.m_Spectrogram_2 = signal.spectrogram(self.channel_2[self.m_FirstSelectedSample:self.m_LastSelectedSample], self.m_SamplingFrequency, window=signal.get_window(self.m_CurrentWindowFunction, self.m_WindowLength), nperseg=self.m_WindowLength, noverlap=self.m_WindowOverlap)
         self.m_Spectrogram_1 = np.log(self.m_Spectrogram_1)
         self.m_Spectrogram_2 = np.log(self.m_Spectrogram_2)
      
