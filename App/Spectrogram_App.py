



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
