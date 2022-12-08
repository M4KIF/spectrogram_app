
# Here is the main app code,
# that connects gui to the backend



# Imports
import sys

# Local modules and packages
from backend import *
from ui import appWindow as gui



def main():
   # A quick print environment test
   print("Does anything even work?")

   app = gui.QApplication(sys.argv)

   window = gui.Window()
   window.setFixedSize(1280,720)

   window.show()

   # Running the Qt loop inside the exit method,
   # that ceases the application when We exit the loop
   sys.exit(app.exec())

if __name__ == "__main__":
    main()
