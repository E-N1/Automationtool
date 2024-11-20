import os
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, QGroupBox, QCheckBox, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5 import QtCore

from Configurations.machines import Machines
from Configurations.read_version import ReadVersion

from Logic.run_test_execution import RunTestExecution

class StartTestsWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        # Window-widgets
        self.setWindowTitle("Automationtool - Starting Tests")

        
        #Configurations
        self.machines = Machines()
        self.readVersion = ReadVersion()

        #Logic
        self.runTestExecution = RunTestExecution()

        # Labels
        self.runnerLabel = "Start Maschinen Tests"
        self.runInstallationLabel = "Tests starten"
        self.subfolderVersionLabel = "Version:"
        self.groupsPerRow = 4  

        # Dict
        self.modulqtp_allg = {}

        # Style
        self.font = QFont("Arial", 12)

        # UI
        self.initUI()


    def initUI(self):
        """
        Initializes the user interface for the start tests window.

        This method sets up the central widget and layout for the window, 
        adds a header layout, and dynamically creates and adds a layout 
        for the machines based on the number of machines and their names.

        Methods:
            getHeaderLayout(): Returns the header layout.
            getMachinesLayout(num_machines, machine_names): Returns the layout for the machines.

        Attributes:
            centralWidget (QWidget): The central widget of the window.
            machines (Machines): An instance containing machine information.
        """
        centralLayout = QVBoxLayout()
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(centralLayout)

        header = self.getHeaderLayout()
        centralLayout.addLayout(header)

        machines = self.getMachinesLayout(self.machines.getNumberOfMachines(), self.machines.getMachineNameOfAll())
        centralLayout.addLayout(machines)


    def createModuleWidget(self, machine, module):
        """
        Creates a QWidget containing a QLabel and a QCheckBox for a given module.
        Args:
            machine (str): The name or identifier of the machine.
            module (str): The name of the module.
        Returns:
            QWidget: A widget containing the module label and checkbox.
        """
        hbox = QHBoxLayout()
        moduleLabel = QLabel(module)
        moduleCheckbox = QCheckBox()

        hbox.addWidget(moduleLabel)
        hbox.addWidget(moduleCheckbox)

        moduleWidget = QWidget()
        moduleWidget.setLayout(hbox)

        # Set initial checkbox state
        moduleCheckbox.setChecked(False)
        
        # Save module entry reference for the specific machine
        if machine not in self.modulqtp_allg:
            self.modulqtp_allg[machine] = {}
        self.modulqtp_allg[machine][module] = moduleCheckbox
        
        return moduleWidget


    def createHeaderComponent(self):
        """
        Creates the header component for the UI.

        This method initializes a horizontal box layout (hbox) and a vertical box layout (vboxHeader).
        It sets up the header label with a specified font and alignment, and adds it to the hbox.
        The hbox is then added to the vboxHeader layout.

        Attributes:
            vboxHeader (QVBoxLayout): The vertical box layout for the header.
            headerLabel (QLabel): The label used as the header, styled with a specific font and alignment.
        """
        hbox = QHBoxLayout()
        self.vboxHeader = QVBoxLayout()
        self.vboxHeader.addLayout(hbox)
        fontHeadline = QFont("Arial", 15)
        fontHeadline.setUnderline(True)

        self.headerLabel = QLabel(self.runnerLabel)
        self.headerLabel.setFont(fontHeadline)
        self.headerLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.headerLabel.setContentsMargins(50, 50, 50, 50)
        hbox.addWidget(self.headerLabel)


    def createMachinesComponent(self, numbersVM, hostnameVM):
        """
        Creates a component for managing virtual machines (VMs) in the UI.
        This method dynamically generates a layout of group boxes, each representing a VM. 
        Each group box contains:
        - A label for the subfolder version.
        - A label displaying the current version of the VM, or a "version not found" message if the version is unavailable.
        - A list of modules that can be selected for testing.
        - A button to start the test execution for the selected modules.
        Args:
            numbersVM (int): The number of virtual machines to create components for.
            hostnameVM (list): A list of hostnames for the virtual machines.
        """
        self.vboxVM = QVBoxLayout()

        if numbersVM == 0:
            return

        hbox = QHBoxLayout()  
        self.vboxVM.addLayout(hbox)

        for i in range(0, numbersVM):
            if i % self.groupsPerRow == 0 and i != 0:
                hbox = QHBoxLayout()
                self.vboxVM.addLayout(hbox)



            groupboxVM = QGroupBox(hostnameVM[i])
            groupboxLayout = QVBoxLayout(groupboxVM)

            
            # Chosing a version
            subfolderLabel = QLabel(self.subfolderVersionLabel)
            groupboxLayout.addWidget(subfolderLabel)
            
            # Version label
            machineKey = f"{hostnameVM[i]}"
            if machineKey in self.readVersion.currentVersionListInsideFile:
                currentVersionLabel = QLabel(self.readVersion.currentVersionListInsideFile[machineKey]+"")
                currentVersionLabel.setContentsMargins(0,0,0,30)
                groupboxLayout.addWidget(currentVersionLabel)
            else:
                currentVersionNotFoundLabel = QLabel("version not found")
                currentVersionNotFoundLabel.setContentsMargins(0,0,0,30)
                groupboxLayout.addWidget(currentVersionNotFoundLabel)

            # Able to chose one or more Modul, what will be test
            modules = self.machines.getModuleFromMachine(hostnameVM[i])
            for modul in modules:
                moduleWidget = self.createModuleWidget(hostnameVM[i],modul)
                groupboxLayout.addWidget(moduleWidget)

            # Button erstellen und die angehakten Module übergeben
            addingEachButtonVM = QPushButton(self.runInstallationLabel)
            
            def on_button_click(vm=machineKey, modules=modules):
                checkedModules = [mod for mod in modules if self.modulqtp_allg[vm][mod].isChecked()]

                if not checkedModules:
                    self.informationWindow("Bitte mindestens ein Modul auswählen.")
                else:
                    self.runTestExecution.startTest(vm, checkedModules)
            
            addingEachButtonVM.clicked.connect(lambda _, vm=machineKey: on_button_click(vm))
            addingEachButtonVM.setContentsMargins(0, 30, 0, 30)
            groupboxLayout.addWidget(addingEachButtonVM)

            hbox.addWidget(groupboxVM)
            groupboxVM.setMinimumWidth(200)
            groupboxVM.setFont(self.font)


    def fillDropdownMenu(self, comboBoxVM, path):
        """
        Populates a dropdown menu with directory names from a specified path.

        Args:
            comboBoxVM (QComboBox): The combo box widget to populate.
            path (str): The file system path to search for directories.

        Raises:
            Exception: If there is an error accessing the specified path, 
                   a default item indicating the error is added to the combo box 
                   and the error is printed to the console.
        """
        try:
            directories = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
            comboBoxVM.addItems(directories)
        except Exception as e:
            comboBoxVM.addItems(["network or path not found"])
            print(f"Fehler beim Zugriff auf den Netzwerkordner: {e}")

        
    def getHeaderLayout(self):
        """
        Creates and returns the header layout for the UI.

        This method initializes a QVBoxLayout, calls the createHeaderComponent 
        method to set up the header components, and then adds the header 
        components to the layout.

        Returns:
            QVBoxLayout: The layout containing the header components.
        """
        headerLayout = QVBoxLayout()
        self.createHeaderComponent()
        headerLayout.addLayout(self.vboxHeader)
        return headerLayout


    def getMachinesLayout(self, numberVM, hostnameVM):
        """
        Creates and returns a QVBoxLayout containing the layout for virtual machines.

        Args:
            numberVM (int): The number of virtual machines.
            hostnameVM (str): The hostname of the virtual machines.

        Returns:
            QVBoxLayout: The layout containing the virtual machines.
        """
        vmLayout = QVBoxLayout()
        self.createMachinesComponent(numberVM, hostnameVM)
        vmLayout.addLayout(self.vboxVM)
        return vmLayout


    def informationWindow(self,message):
        """
        Displays an information message box with the given message.

        Parameters:
        message (str): The message to be displayed in the information box.

        Returns:
        QMessageBox.StandardButton: The button that was clicked to dismiss the message box.
        """
        return QMessageBox.information(None, "Warnung", message)

