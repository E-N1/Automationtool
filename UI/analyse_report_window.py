from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, QMessageBox,QGroupBox,QSizePolicy,QLayout
from PyQt5.QtGui import QFont

from PyQt5 import QtCore

from Configurations.machines import Machines
from Logic.access_db_reader import AccessDBReader
from Logic.html_data import HTMLData

class AnalyseReportWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        # Window-widgets
        self.setWindowTitle("Automationtool - Analyse-Report")
        self.setFixedSize(900, 500)
        
        self.dictMachines = {}

        # Configurations
        self.machines = Machines()

        # Logic
        self.htmlData = HTMLData()
        self.accessDBReader = AccessDBReader()

        # Labels & other
        self.groupsPerRow = 4  
        self.runnerLabel = "Analyse-Report - HTML File"
        self.informationLabel = "Wenn Sie auf 'Analyse starten' klicken, beginnt der Prozess zur Überprüfung der 'uebersicht.txt' in je Maschine.\nWird das Analyse-Fenster geschlossen, wird die Überprüfung gestoppt."
        self.databaseUpdateButtonLabel = "Datenbank Inhalte aktualisieren"
        self.subfolderVersionLabel = "Version:"
        self.startAnalyseButton = "Analyse starten"

        # Style
        self.font = QFont("Arial", 12)

        # UI
        self.initUI()


    def initUI(self):
        """
        Initializes the user interface for the report analysis window.

        This method sets up the central widget and its layout, adds the header layout,
        and adds the layout for each virtual machine.

        The layout includes:
        - A header layout obtained from `getHeaderLayout()`.
        - A layout for each virtual machine obtained from `getMachinesLayout()`.

        Attributes:
            centralWidget (QWidget): The central widget of the window.
        """
        centralLayout = QVBoxLayout()
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(centralLayout)

        header = self.getHeaderLayout()
        centralLayout.addLayout(header)

        eachVM = self.getMachinesLayout(self.machines.getNumberOfMachines(), self.machines.getMachineNameOfAll())
        centralLayout.addLayout(eachVM)


    def createHeaderComponent(self):
        """
        Creates the header component for the analysis report window.

        This method sets up the header layout with three main rows:
        1. A headline row with a centered, underlined label.
        2. An information row with a centered label.
        3. A button row with a button to update the database.

        The header component is structured using QVBoxLayout and QHBoxLayout
        to organize the widgets vertically and horizontally.

        Attributes:
            runnerLabel (str): The text for the headline label.
            informationLabel (str): The text for the information label.
            databaseUpdateButtonLabel (str): The text for the database update button.
            font (QFont): The font used for the information label and the button.
            machines (Machines): An instance providing machine-related data.
            accessDBReader (DBReader): An instance for accessing and updating the database.

        Widgets:
            headerLabel (QLabel): Displays the headline text.
            informationLabel (QLabel): Displays the information text.
            updateDatabaseButton (QPushButton): Button to trigger database update.
        """
        # Headline row0, informations
        hbox = QHBoxLayout()
        self.vboxHeader = QVBoxLayout()
        self.vboxHeader.addLayout(hbox)
        fontHeadline = QFont("Arial", 15)
        fontHeadline.setUnderline(True)

        headerLabel = QLabel(self.runnerLabel)
        headerLabel.setFont(fontHeadline)
        headerLabel.setAlignment(QtCore.Qt.AlignCenter)
        headerLabel.setContentsMargins(50, 50, 50, 50)
        hbox.addWidget(headerLabel)

        # Headline row1, informations
        hbox1 = QVBoxLayout()
        informationLabel = QLabel(self.informationLabel)
        informationLabel.setFont(self.font)
        informationLabel.setAlignment(QtCore.Qt.AlignCenter)
        informationLabel.setContentsMargins(50, 50, 50, 50)
        hbox1.addWidget(informationLabel)
        self.vboxHeader.addLayout(hbox1)

        # Headline row2, Button to update database
        firstMachineName = self.machines.getFirstMachineName()
        hbox2 = QVBoxLayout()
        updateDatabaseButton = QPushButton(self.databaseUpdateButtonLabel)
        updateDatabaseButton.clicked.connect(lambda _: self.accessDBReader.setDBDataInJson(firstMachineName))
        updateDatabaseButton.setContentsMargins(50, 30, 50, 30)
        updateDatabaseButton.setFont(self.font)
        hbox2.addWidget(updateDatabaseButton)
        self.vboxHeader.addLayout(hbox2)


    def createMachinesComponent(self, listedCountedVMs, listedVMHostnames):
        """
        Creates a UI component to display a list of virtual machines.

        This method generates a vertical box layout (QVBoxLayout) containing horizontal box layouts (QHBoxLayout) 
        for each row of virtual machine group boxes (QGroupBox). Each group box contains a button that triggers 
        the analysis of the corresponding virtual machine.

        Args:
            listedCountedVMs (int): The number of virtual machines to display.
            listedVMHostnames (list of str): A list of hostnames for the virtual machines.
        """
        self.vboxVM = QVBoxLayout()

        if listedCountedVMs == 0:
            return

        hbox = QHBoxLayout()  
        self.vboxVM.addLayout(hbox)

        for i in range(0, listedCountedVMs):
            if i % self.groupsPerRow == 0 and i != 0:
                hbox = QHBoxLayout()
                self.vboxVM.addLayout(hbox)

            groupboxVM = QGroupBox(listedVMHostnames[i])
            groupboxLayout = QVBoxLayout(groupboxVM)


            addingEachButtonVM = QPushButton(self.startAnalyseButton)
            addingEachButtonVM.clicked.connect(lambda _, vm= listedVMHostnames[i]: self.htmlData.openHTMLDataWithWatchdog(vm))
            addingEachButtonVM.setContentsMargins(0, 30, 0, 30)
            groupboxLayout.addWidget(addingEachButtonVM)

            hbox.addWidget(groupboxVM)
            groupboxVM.setMinimumWidth(200)
            groupboxVM.setFont(self.font)


    def getHeaderLayout(self):
        """
        Creates and returns the header layout for the UI.

        This method initializes a QVBoxLayout, calls the createHeaderComponent 
        method to set up the header components, and adds the header components 
        to the layout.

        Returns:
            QVBoxLayout: The layout containing the header components.
        """
        headerLayout = QVBoxLayout()
        self.createHeaderComponent()
        headerLayout.addLayout(self.vboxHeader)
        return headerLayout


    def getMachinesLayout(self,countedVMSInList,VMHostName):
        """
        Creates and returns a QVBoxLayout containing the layout for the machines.

        Args:
            countedVMSInList (list): A list of counted virtual machines.
            VMHostName (str): The name of the virtual machine host.

        Returns:
            QVBoxLayout: The layout containing the machines.
        """
        machinesLayout = QVBoxLayout()
        self.createMachinesComponent(countedVMSInList,VMHostName)
        machinesLayout.addLayout(self.vboxVM)
        return machinesLayout


    def closeEvent(self, event):
        """
        Handles the close event for the window.

        This method is called when the user attempts to close the window. It prompts the user with a message box
        asking for confirmation to close the window. If the user confirms, the window is closed and the logs stop
        updating. If the user cancels, the close event is ignored and the window remains open.

        Args:
            event (QCloseEvent): The close event triggered by the user action.

        """
        reply = QMessageBox.question(self, 'Message',
            "Wenn du das Fenster schließt, aktualisieren sich die Logs nicht.\nMöchtest du sicher schließen? ", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.htmlData.close()
            event.accept()
        else:
            event.ignore()
