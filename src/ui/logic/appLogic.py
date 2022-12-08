
#
#
#

import scipy.io.wavfile as wavfile
import numpy as np
import math
from scipy import signal


class appLogic():
   def __init__(self):

      ##########################################################################
      # Initialising the needed variables for executing the main functionality #
      ##########################################################################

      self.listOfWindows = ["tukey", "triang", "flattop", "exponential"]
      self.spectrogramBand = ["Narrow", "Wide"]

      self.openedFilename = str()
      self.rawfile = np.array([])

      # Default window is set as "tukey"
      self.choosenWindow = "tukey"

      # Flagi

      self.mono = False
      self.stereo = False
      self.fileRead = False
      self.rangeSelected = False

      self.length = None
      self.start = None
      self.end = None

      self.freq_channel_1 = None
      self.freq_channel_2 = None
      self.segments_channel_1 = None
      self.segments_channel_2 = None
      self.spectro_channel_1 = None
      self.spectro_channel_2 = None

      # The default range is set to narrow.
      self.selectedRange = 0
      self.narrowBandWindow = None
      self.wideBandWindow = None 

      self.window_length = 500
      self.window_overlap = None

   def openAudioFile(self):
      #self.audiofile = wavfile.open(self.openedFilename, "r")
      self.fs, self.file = wavfile.read(self.openedFilename)
      self.fileOpened = True

      self.end = self.length = len(self.file)
      self.start = 0
      
      if np.ndim(self.file) > 1:
         self.stereo = True
         self.mono = False

         self.channel_1 = self.file[:,0]
         self.channel_2 = self.file[:,1]
      else:
         self.mono = True
         self.stereo = False

         self.channel_1 = self.file
      
      # Calculating the matching window lengths for the wide/narrow spectrogram
      self.calculateWindowLengths()

      # Setting the overlap to 10%
      self.window_overlap = int(math.ceil(self.window_length/10))

      # Setting the narrow spectrogram as default
      self.window_length = self.narrowBandWindow

      # Calculating the timespace array
      self.time = np.linspace(0, len(self.channel_1)/self.fs, num=len(self.channel_1))

   def editRange(self, start=None, end=None):
      if end != 0:
         self.start = start
         self.end = end
      else:
         self.start = 0
         self.end = self.length

   def calculateWindowLengths(self):
      # Calculating the narrowband window length > 2 * n-samples/sampling frequency
      self.narrowBandWindow = int(0.035 * self.fs)
      # Calculating the wideband window length < n-samples/sampling frequency
      self.wideBandWindow = int(0.004 * self.fs)

   def chooseSpectrum(self, index):
      # For further use
      self.selectedRange = index

      # Selecting the right window
      if index == 0:
         # Calculating the narrowband window length > 2 * n-samples/sampling frequency
         self.window_length = self.narrowBandWindow 
      elif index == 1:
         # Calculating the wideband window length < n-samples/sampling frequency
         self.window_length = self.wideBandWindow

      # Everytime the window is calculated, so i have to change the nperseg
      self.window_overlap = int(math.ceil(self.window_length/10))

   def calculateSpectrogram(self, min_index=None, max_index=None):
      print(f"Here comes the error {self.window_length}, and narr {self.narrowBandWindow} or wide {self.wideBandWindow}")
      print(f"{self.end-self.start}")
      if self.window_length == self.window_overlap:
         self.window_length+=1

      if self.mono:
         self.freq_channel_1, self.segments_channel_1, self.spectro_channel_1 = signal.spectrogram(self.channel_1[self.start:self.end], self.fs, window=signal.get_window(self.choosenWindow, self.window_length), noverlap=self.window_overlap)
         self.spectro_channel_1 = np.log(self.spectro_channel_1)
      elif self.stereo:
         self.freq_channel_1, self.segments_channel_1, self.spectro_channel_1 = signal.spectrogram(self.channel_1[self.start:self.end], self.fs, window=signal.get_window(self.choosenWindow, self.window_length), noverlap=self.window_overlap)
         self.freq_channel_2, self.segments_channel_2, self.spectro_channel_2 = signal.spectrogram(self.channel_2[self.start:self.end], self.fs, window=signal.get_window(self.choosenWindow, self.window_length), noverlap=self.window_overlap)
         self.spectro_channel_1 = np.log(self.spectro_channel_1)
         self.spectro_channel_2 = np.log(self.spectro_channel_2)
      

