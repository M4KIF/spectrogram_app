
# Here is the main app code,
# that connects gui to the backend



# Imports
import sys



# Local modules and packages
from backend import *
from ui import appWindow as ui



def main():
   # A quick print environment test
   print("Does anything even work?")

   x = player.player()

   app = ui.QtWidgets.QApplication([])

   y = ui.appWindow()
   y.resize(1280, 720)
   y.show()

   # Exiting the app
   sys.exit(app.exec())

if __name__ == "__main__":
    main()
