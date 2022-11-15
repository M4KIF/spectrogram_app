import sys
import random
# Including Qt core functionality
from PySide6 import QtCore, QtWidgets, QtGui
# Responsible for audio file editing
from wavfile import base
# Responsible for generating a graph
from matplotlib import pyplot
# For storing particular data in the array
import numpy as np
# For needed window functions
from scipy import signal



class File(base.Wavfile):
   def __init__(self):
      #Placeholder
      print("Random stuff")



class WindowFunctions():
   def __init__(self):
      #Another placeholder
      print("Even more random stuff")



class Graph():
   def __init__(self):
      #
      print(" ")



class Spectrogram(Graph):
   def __init__(self):
      #
      print("")



class appBackEnd():
   def __init__(self):
      #
      print(" ")



class appGUI(QtWidgets.QWidget):
   def __init__(self):
      super().__init__()

      self.hello = ["Jeden", "Dwa", "Trzy"]

      self.button = QtWidgets.QPushButton("Click Me!")
      self.text = QtWidgets.QLabel(
            "Hello!", alignment=QtCore.Qt.AlignCenter)

      self.layout = QtWidgets.QVBoxLayout(self)
      self.layout.addWidget(self.text)
      self.layout.addWidget(self.button)

      self.button.clicked.connect(self.magic)

   @QtCore.Slot()
   def magic(self):
      self.text.setText(random.choice(self.hello))



def main():

   # Printing some basic information about the setup
   print("Checking environment setup")
   print(QtCore.__version__)

   # Preparing the app window
   app = QtWidgets.QApplication([])

   widget = appGUI()
   widget.resize(1280, 720)
   widget.show()

   # Exiting the app
   sys.exit(app.exec())

if __name__ == "__main__":
    main()
