import os
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont

from Configurations.machines import Machines

from Configurations.read_fault import ReadFault


class StatusWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        # Window-widgets
        self.setWindowTitle("Automationtool - Status")
        self.setGeometry(1500,400,300,600)

        #Configurations
        self.machines = Machines()

        # Logic
        self.readFault = ReadFault()
        
        # Style
        self.font = QFont("Arial", 12)

        # UI
        self.initUI()

        self.timer = QTimer(self, interval=1000, timeout=self.handleTimeout)
        self.timer.start()
        self.handleTimeout()


    def initUI(self):
        """
        Initializes the user interface for the status window.

        This method sets up the central widget and layout, and adds a read-only
        QTextEdit widget to display the statuses of machines. It also initializes
        a dictionary to store the names of all machines with empty status strings.

        Attributes:
            dictOfMachines (dict): A dictionary to store machine names with their statuses.
            centralWidget (QWidget): The central widget of the status window.
            statusTextBox (QTextEdit): A text edit widget to display machine statuses.
        """
        self.dictOfMachines = {}
        for i in range(len(self.machines.getMachineNameOfAll())):
            self.dictOfMachines[self.machines.getMachineNameOfAll()[int(i)]] = ""

        centralLayout = QVBoxLayout()
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(centralLayout)

        # Add a QTextEdit to display machine statuses
        self.statusTextBox = QTextEdit()
        self.statusTextBox.setReadOnly(True)
        self.statusTextBox.setFont(self.font)
        centralLayout.addWidget(self.statusTextBox)


    def handleTimeout(self):
        """
        Handles the timeout event to update the status text box with the current statuses of machines.

        This method reads the status of each machine from a corresponding file, determines the display color based on the status,
        and updates the status text box with the formatted status information.

        Status color coding:
        - "n": blue
        - Contains "error" (case insensitive): red
        - Any other status: black

        Raises:
            IOError: If there is an issue reading the status file for a machine.
        """
        # Update the status text box with machine statuses
        status_text = ""
        for machine_id in self.dictOfMachines.keys():
            try:
                path = os.getenv("INSTALL_HELPER_PATH")
                with open(path,"r") as f:
                    status = f.read()
            except:
                status = "ERROR: COULD NOT FETCH STATUS"
            if status == "n":
                color = "blue"
            elif "error" in status.lower():
                color = "red"
            else:
                color = "black"
            status_text += f'<span style="color:{color}">{machine_id}: {status}</span><br><br>'
        self.statusTextBox.setHtml(status_text)
        self.update()


