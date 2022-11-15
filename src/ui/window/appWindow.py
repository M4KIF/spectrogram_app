# Here is the code responsible for displaying the
# content that is mandatory for running the application
# This is not a functional app, but only a graphical interface
# that the app will be implemented with



# Imports
import sys
import random

# Including Qt core functionality
from PySide6 import QtCore, QtWidgets, QtGui



class appWindow(QtWidgets.QWidget):
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
