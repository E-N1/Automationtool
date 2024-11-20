import os

from PyQt5.QtWidgets import QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QGroupBox, QWidget, QLineEdit,QSizePolicy,QLayout
from PyQt5.QtCore import  pyqtSlot,pyqtSignal,QTimer
from PyQt5.QtGui import QFont
from PyQt5 import QtCore


from Configurations.machines import Machines
from Configurations.read_controlling import ReadControlling
from Configurations.read_version import ReadVersion
from Configurations.networkshare import NetworkShare
from Configurations.read_fault import ReadFault

from Logic.open_qtpfile import OpenQTPFile
from Logic.change_qtp_entries import ChangeQTPEntries
from Logic.run_test_execution import RunTestExecution
from Logic.vm_access_manager import VMAccessManager

from UI.vm_manager import VMManager
from UI.vm_component import VMComponent
from UI.archive_window import ArchiveWindow
from UI.update_installer_window import UpdateInstaller
from UI.start_tests_window import StartTestsWindow
from UI.analyse_report_window import AnalyseReportWindow
from UI.status_window import StatusWindow
from UI.traffic_light_widget import TrafficLightWidget


class WindowComponents(QWidget):
    trafficLightUpdated = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent

        # Configurations
        self.machines = Machines()
        self.readControlling = ReadControlling()
        self.readVersion = ReadVersion()
        self.networkShare = NetworkShare()
        self.readFault = ReadFault()

        #Logic
        self.startAutomaticProcess = ChangeQTPEntries()
        self.openQTPFile = OpenQTPFile()
        self.runTestExecution = RunTestExecution()
        self.vmAccessManager = VMAccessManager()

        #UI
        self.vmManager = VMManager()
        self.archiveWindow = ArchiveWindow()
        self.updateInstallerWindow = UpdateInstaller()
        self.startTestWindow = StartTestsWindow()
        self.analyseReportWindows = AnalyseReportWindow()
        self.statusWindow = StatusWindow()


        # GUI - Header
        self.headerText = "Automationtool"
        self.headerControlling = "Controlling:"
        self.headerLabels = ["Tag", "Monat", "Jahr", "Build", "Update", "Praefix"]

        # GUI - Adding Button
        self.addButtonLabel = "Hinzufügen"

        # Category Label each VM, also
        self.categoryLabel = "Module:"
        self.currentVersion = ""


        
        # Button-Label
        self.startButton = "Dateiänderung starten"
        self.archiveButton = "Archiv öffnen"
        self.updateInstallerButton = "Update installieren"
        self.starttestButtonLabel = "Maschinen-Test öffnen"
        self.analyseReportButtonLabel = "Analyse-Report öffnen"
        self.statusButtonLabel = "Status öffnen"
        self.closeButton = "Beenden"
        self.groupsPerRow = 4 
        
        #Style
        self.font = QFont("Arial", 12)

        self.vmComponentList = []
        


   # Header
    def createHeaderComponent(self):
        """Creates the header component of the main window."""
        hbox = QHBoxLayout()
        self.vboxHeader = QVBoxLayout()
        self.vboxHeader.addLayout(hbox)
        fontHeadline = QFont("Arial", 15)
        fontHeadline.setUnderline(True)

        # Headline row 0, Maschtestkonfigurator
        self.headerLabel = QLabel(self.headerText)
        self.headerLabel.setFont(fontHeadline)
        self.headerLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.headerLabel.setContentsMargins(20,20,20,20)
        hbox.addWidget(self.headerLabel)

        # Headline row1, Tag, Monat, Jahr, Praefix, Build
        hbox1 = QHBoxLayout()
        for labelText in self.headerLabels:
            label = QLabel(labelText)
            label.setAlignment(QtCore.Qt.AlignCenter)  
            hbox1.addWidget(label, alignment=QtCore.Qt.AlignCenter)  
            label.setFont(self.font)
        self.vboxHeader.addLayout(hbox1)

        
        # Headline row2, Tag , Monat, Jahr, Praefix und  Build from Controlling
        self.hbox2 = QHBoxLayout()
        for labelText in self.readControlling.controllingEntries:
            label = QLabel(labelText)
            label.setAlignment(QtCore.Qt.AlignCenter)  
            self.hbox2.addWidget(label, alignment=QtCore.Qt.AlignCenter)  
            label.setFont(self.font)
        self.vboxHeader.addLayout(self.hbox2)


        # Headline row3, Entrys of all of row1
        # datum(zeile 1),lauf(zeile 2),update(zeile 3),präfix(zeile 4)
        hbox3 = QHBoxLayout()
        self.dayEntry = QLineEdit() 
        self.monthEntry = QLineEdit()
        self.yearEntry = QLineEdit()
        self.updateEntry = QLineEdit()
        self.praefixEntry = QLineEdit()
        self.buildEntry = QLineEdit()
        for entry in [self.dayEntry, self.monthEntry, self.yearEntry,self.buildEntry, self.updateEntry, self.praefixEntry]:
            entry.setFixedWidth(100)
            entry.setContentsMargins(10,0,10,15)
            hbox3.addWidget(entry)
        self.vboxHeader.addLayout(hbox3)

    def createMainComponent(self, numbersVM, hostnameVM, mainWindow):
        """
        Creates the main component of the main window.
        :param numbersVM: represents the number of VMs
        :param hostnameVM: represents the hostname of the VMs
        :param mainWindow: marks the main window
        """
        self.vboxVM = QVBoxLayout()

        if numbersVM == 0:
            print("Please note a machine in your machines.json!")
            return

        hbox = QHBoxLayout()
        self.vboxVM.addLayout(hbox)

        for i in range(0, numbersVM):
            if i % self.groupsPerRow == 0 and i != 0:
                hbox = QHBoxLayout()
                self.vboxVM.addLayout(hbox)

            modules = self.machines.getModuleFromMachine(hostnameVM[i])

            # Groupbox name
            groupboxVM = QGroupBox(hostnameVM[i])
            groupboxLayout = QVBoxLayout(groupboxVM)

            trafficLightWidget = TrafficLightWidget()
            groupboxLayout.addWidget(trafficLightWidget)


            self.addingEachButtonVM = QPushButton(self.addButtonLabel)
            vmComponent = VMComponent(number=i, button=self.addingEachButtonVM, hostname=hostnameVM, i=i, vmGroupBox=groupboxVM)
            self.addingEachButtonVM.clicked.connect(vmComponent.openDialogVM)
            self.vmComponentList.append(vmComponent)

            vmComponent.trafficLightWidget = trafficLightWidget  # Save the TrafficLightWidget in the component
            self.vmComponentList.append(vmComponent)
            machineKey = f"{hostnameVM[i]}"

            if machineKey in self.readVersion.currentVersionListInsideFile:
                currentVersionLabel = QLabel(self.readVersion.currentVersionListInsideFile[machineKey])
                groupboxLayout.addWidget(currentVersionLabel)
            else:
                currentVersionNotFoundLabel = QLabel("version not found")
                groupboxLayout.addWidget(currentVersionNotFoundLabel)

            catlabel = QLabel(self.categoryLabel)
            groupboxLayout.addWidget(catlabel)

            for module in modules:
                machineFilePath = self.machines.changeMachinePathBasedOnModule(i+1, module)
                hboxInside = QHBoxLayout()
                button = QPushButton(module)
                button.clicked.connect(lambda _, mp=machineFilePath: self.openQTPFile.openWithNotepad(mp))
                emptyLabel = QLabel("''")
                hboxInside.addWidget(button)
                hboxInside.addWidget(emptyLabel)
                vmComponent.entrysFromGUIDiaglog.append(hboxInside)
                groupboxLayout.addLayout(hboxInside)

            self.addingEachButtonVM.adjustSize()
            groupboxLayout.addWidget(self.addingEachButtonVM)

            groupboxVM.setLayout(groupboxLayout)
            hbox.addWidget(groupboxVM)
            hbox.setSpacing(10)
            hbox.setContentsMargins(10, 10, 10, 10)

            groupboxVM.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            groupboxLayout.setSizeConstraint(QLayout.SetMinimumSize)
            
            groupboxVM.adjustSize()
            groupboxVM.setMinimumSize(groupboxVM.sizeHint())

            button.setFont(self.font)
            catlabel.setFont(self.font)
            groupboxVM.setFont(self.font)

        startAndCloseWidget = QWidget()
        startAndCloseWidget.setLayout(self.getButtonsLayout(mainWindow,hostnameVM))
        hbox.addWidget(startAndCloseWidget)


    #Start & Close
    def createButtonsComponent(self, mainWindow, hostnameVM):
        """
        Creates the buttons component of the main window.

        This method initializes and configures the buttons used in the main window.
        It sets up the layout and connects the buttons to their respective event handlers.

        :param mainWindow: The main window instance.
        :param hostnameVM: The hostname of the virtual machines.
        """
        self.vboxButtons = QVBoxLayout()

        # Start button
        self.startPushButton = QPushButton(self.startButton)
        self.startPushButton.setFont(self.font)
        self.startPushButton.setStyleSheet("text-align: center;")
        self.startPushButton.adjustSize()
        self.startPushButton.clicked.connect(lambda vm=hostnameVM: self.startProcess(vm)) 
        self.vboxButtons.addWidget(self.startPushButton)

        # Archive button
        self.archivePushButton = QPushButton(self.archiveButton)
        self.archivePushButton.setFont(self.font)
        self.archivePushButton.setStyleSheet("text-align: center;")
        self.archivePushButton.adjustSize()
        self.archivePushButton.clicked.connect(self.openArchivWindow)
        self.vboxButtons.addWidget(self.archivePushButton)

        # Update-Installer button
        self.updateInstallerPushButton = QPushButton(self.updateInstallerButton)
        self.updateInstallerPushButton.setFont(self.font)
        self.updateInstallerPushButton.setStyleSheet("text-align: center;")
        self.updateInstallerPushButton.adjustSize()
        self.updateInstallerPushButton.clicked.connect(self.openUpdateInstallerWindow)
        self.vboxButtons.addWidget(self.updateInstallerPushButton)

        # Tests-starten button
        self.startTestPushButton = QPushButton(self.starttestButtonLabel)
        self.startTestPushButton.setFont(self.font)
        self.startTestPushButton.setStyleSheet("text-align: center;")
        self.startTestPushButton.adjustSize()
        self.startTestPushButton.clicked.connect(self.openStartTestWindow)
        self.vboxButtons.addWidget(self.startTestPushButton)

        # Analysereport button
        self.analyseReportButton = QPushButton(self.analyseReportButtonLabel)
        self.analyseReportButton.setFont(self.font)
        self.analyseReportButton.setStyleSheet("text-align: center;")
        self.analyseReportButton.adjustSize()
        self.analyseReportButton.clicked.connect(self.openAnalyseReportWindow)
        self.vboxButtons.addWidget(self.analyseReportButton)

        # Status button
        self.statusButton = QPushButton(self.statusButtonLabel)
        self.statusButton.setFont(self.font)
        self.statusButton.setStyleSheet("text-align: center;")
        self.statusButton.adjustSize()
        self.statusButton.clicked.connect(self.openStatusWindow)
        self.vboxButtons.addWidget(self.statusButton)

        # Close button
        self.closePushButton = QPushButton(self.closeButton)
        self.closePushButton.setFont(self.font)
        self.closePushButton.setStyleSheet("text-align: center;")
        self.closePushButton.adjustSize()
        self.closePushButton.clicked.connect(mainWindow.closeEvent)
        self.vboxButtons.addWidget(self.closePushButton)


    def createFooter(self):
        """ Creates the footer component of the main window. """
        self.hboxFooter = QHBoxLayout()

        # Green: Test running
        greenTrafficLight = TrafficLightWidget()
        greenTrafficLight.setStatus("green")
        greenLabel = QLabel("Tests running")

        greenLayout = QHBoxLayout()
        greenLayout.addWidget(greenTrafficLight)
        greenLayout.addWidget(greenLabel)

        # Orange: Machine is not running
        orangeTrafficLight = TrafficLightWidget()
        orangeTrafficLight.setStatus("orange")
        orangeLabel = QLabel("Machine is not running")

        orangeLayout = QHBoxLayout()
        orangeLayout.addWidget(orangeTrafficLight)
        orangeLayout.addWidget(orangeLabel)

        # Red: Machine has one or more errors
        redTrafficLight = TrafficLightWidget()
        redTrafficLight.setStatus("red")
        redLabel = QLabel("Machine has one or more errors")

        redLayout = QHBoxLayout()
        redLayout.addWidget(redTrafficLight)
        redLayout.addWidget(redLabel)

        # Black: Machine not avaible
        blackTrafficLight = TrafficLightWidget()
        blackTrafficLight.setStatus("black")
        blackLabel = QLabel("Machine cannot be reached")

        blackLayout = QHBoxLayout()
        blackLayout.addWidget(blackTrafficLight)
        blackLayout.addWidget(blackLabel)

        # Add the individual layouts to the footer layout
        self.hboxFooter.addLayout(greenLayout)
        self.hboxFooter.addLayout(orangeLayout)
        self.hboxFooter.addLayout(redLayout)
        self.hboxFooter.addLayout(blackLayout)


    #Getter - Layout
    def getHeaderLayout(self):
        """ Returns the header layout. """
        headerLayout = QVBoxLayout()
        self.createHeaderComponent()
        headerLayout.addLayout(self.vboxHeader)  
        return headerLayout


    def getMainLayout(self, numberVM, hostnameVM, mainWindow):
        """
        Returns the main layout of the window.

        This method creates the main component of the window, which includes the virtual machines (VMs) layout.

        Parameters:
        numberVM (int): The number of virtual machines.
        hostnameVM (list): A list of hostnames for the virtual machines.
        mainWindow (QWidget): The main window instance.

        Returns:
        QVBoxLayout: The layout containing the main components of the window.
        """
        vmLayout = QVBoxLayout()
        self.createMainComponent(numberVM,hostnameVM,mainWindow)
        vmLayout.addLayout(self.vboxVM)  
        return vmLayout


    def getButtonsLayout(self,mainWindow,hostnameVM):
        buttonsLayout = QVBoxLayout()
        self.createButtonsComponent(mainWindow,hostnameVM)
        buttonsLayout.addLayout(self.vboxButtons)  
        return buttonsLayout
    
    # Getter - sending Data
    def getHeaderData(self):
        headerData = {
            'dd': self.dayEntry.text(),
            'mm': self.monthEntry.text(),
            'yyyy': self.yearEntry.text(),
            'build': self.buildEntry.text(),
            'update': self.updateEntry.text(),
            'praefix': self.praefixEntry.text()
        }
        return headerData
    
    def getFooterLayout(self):
        vboxFooter = QVBoxLayout()
        self.createFooter()
        vboxFooter.addLayout(self.hboxFooter)  
        return vboxFooter
    

    def openUpdateInstallerWindow(self):
        self.updateInstallerWindow.show()

    def openArchivWindow(self):
        self.archiveWindow.show()

    def openStartTestWindow(self):
        self.startTestWindow.show()

    def openAnalyseReportWindow(self):
        self.analyseReportWindows.show()

    def openStatusWindow(self):
        self.statusWindow.show()
                
    def getMachineStatus(self, machine):
        # First check if the machine is accessible:
        if not self.isMachineAccessible(machine):
            self.vmAccessManager.setStatus(machine, "Offline")
            return "black"

        # Mock function to determine machine status
        error_count = self.getErrorCountForMachine(machine)
        if self.isMachineRunningWithError(machine, error_count):
            return "red"
        elif self.isMachineRunning(machine):
            return "green"
        else:
            return "orange"

    def getErrorCountForMachine(self, machine):
        error_count = 0
        self.readFault.readOverview(machine)

        if machine not in self.readFault.dictMachineErrors:
            return error_count

        for category in self.readFault.dictMachineErrors[machine]:

            for pattern in self.readFault.errorList:
                if self.vmAccessManager.getStatus(machine) == "Offline":
                    break
                if pattern != ".H.":
                    count = self.readFault.getErrorsForPattern(machine, category, pattern)
                    error_count += len(count)
        return error_count

    def isMachineRunningWithError(self, machine, error_count):
        # red traffic light
        if os.path.exists(os.getenv("MACHINE_ACTIV_CHECKDATA")) and error_count > 0:
            return True
        return False

    def isMachineRunning(self, machine):
        # green traffic light
        if os.path.exists(os.getenv("MACHINE_ACTIV_CHECKDATA")):
            return True
        return False

    def isMachineAccessible(self, machine):
        # black traffic light when machine is not accessible
        try:
            self.readFault.readOverview(machine)
            return True
        except Exception as e:
            print(f"Machine {machine} is not accessible: {e}")
            return False
        
    # Start-Button, begin processing
    def startProcess(self,vm):

        # set the header-entries and save them
        self.vmManager.setHeaderEntries('dd', self.dayEntry.text())
        self.vmManager.setHeaderEntries('mm', self.monthEntry.text())
        self.vmManager.setHeaderEntries('yyyy', self.yearEntry.text())
        self.vmManager.setHeaderEntries('build', self.buildEntry.text())
        self.vmManager.setHeaderEntries('update', self.updateEntry.text())
        self.vmManager.setHeaderEntries('praefix', self.praefixEntry.text())

        # start the automatic search-change-run-process
        self.startAutomaticProcess.searchFolder(vm)
