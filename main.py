# Author: Enver E.
# Date: 05/24
# Python 3.11.9

import sys
from PyQt5.QtWidgets import QApplication
from dotenv import load_dotenv


# load environment variables from .env file
load_dotenv()


class Execute:
    def __init__(self):

        self.startGUI()


    def startGUI(self):
        """Starts the GUI."""
        from UI.main_window import MainWindow
        app = QApplication(sys.argv)
        window = MainWindow()
        window.showMaximized()
        sys.exit(app.exec_())


if __name__ == "__main__":
    execute = Execute()