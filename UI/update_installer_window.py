import os
from PyQt5.QtWidgets import  QMainWindow, QVBoxLayout, QWidget, QLabel, QComboBox, QPushButton, QHBoxLayout, QGroupBox, QMessageBox,QSizePolicy,QLayout
from PyQt5.QtGui import QFont
from PyQt5 import QtCore

from Configurations.machines import Machines
from Configurations.read_version import ReadVersion
from Configurations.networkshare import NetworkShare

from Logic.run_installer_execution import RunInstallerExecution

class UpdateInstaller(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        # Window-widgets
        self.setWindowTitle("Automationtool - Update Installer")

        
        #Configurations
        self.machines = Machines()
        self.readVersion = ReadVersion()
        self.networkShare = NetworkShare()

        #Logic
        self.runInstallerExecution = RunInstallerExecution()

        # Labels
        self.runnerLabel = "Runner - InstallHelper ausführen"
        self.runInstallationLabel = "Installation ausführen"
        self.currentVersionLabel = "Aktuelle Version:"
        self.choseVersionLabel = "Ordner:"
        self.subfolderVersionLabel = "Version:"
        self.groupsPerRow = 4  

        self.fileNameAssignmet = "versionZugewiesen"
        self.folderMainPath = os.getenv("NETWORK_PATH_CURRENT_TARGET")

        # Style
        self.font = QFont("Arial", 12)

        # UI
        self.initUI()

    def initUI(self):
        """
        Initializes the user interface for the update installer window.
        This method sets up the central widget and its layout, adds the header layout,
        and adds the machines layout to the central layout.
        The layout consists of:
        - A header section obtained from `getHeaderLayout()`.
        - A machines section obtained from `getMachinesLayout()` which includes the number of machines
          and their names.
        Methods:
        - getHeaderLayout(): Returns the layout for the header section.
        - getMachinesLayout(num_machines, machine_names): Returns the layout for the machines section.
        Attributes:
        - centralWidget (QWidget): The central widget of the window.
        """
        centralLayout = QVBoxLayout()
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(centralLayout)

        header = self.getHeaderLayout()
        centralLayout.addLayout(header)

        machines = self.getMachinesLayout(self.machines.getNumberOfMachines(), self.machines.getMachineNameOfAll())
        centralLayout.addLayout(machines)

    def createHeaderComponent(self):
        """
        Creates the header component for the installer window.
        This method initializes a horizontal box layout (hbox) and a vertical box layout (vboxHeader).
        It sets up the header label with a specified font and alignment, and adds it to the hbox.
        The hbox is then added to the vboxHeader layout.
        Attributes:
            hbox (QHBoxLayout): The horizontal box layout for the header.
            vboxHeader (QVBoxLayout): The vertical box layout containing the hbox.
            fontHeadline (QFont): The font used for the header label.
            headerLabel (QLabel): The label displaying the header text.
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
        Creates a UI component for managing virtual machines.
        This method generates a dynamic layout of group boxes, each representing a virtual machine.
        Each group box contains labels for the current version, a dropdown menu for selecting a version folder,
        and a button to run the installation.
        Args:
            numbersVM (int): The number of virtual machines to create components for.
            hostnameVM (list of str): A list of hostnames for the virtual machines.
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

            # Current version label
            versionLabel = QLabel(self.currentVersionLabel)
            groupboxLayout.addWidget(versionLabel)
            
            # Version label
            machineKey = f"{hostnameVM[i]}"
            if machineKey in self.readVersion.currentVersionListInsideFile:
                currentVersionLabel = QLabel(self.readVersion.currentVersionListInsideFile[machineKey] + "")
                currentVersionLabel.setContentsMargins(0, 0, 0, 30)
                groupboxLayout.addWidget(currentVersionLabel)
            else:
                currentVersionNotFoundLabel = QLabel("version not found")
                currentVersionNotFoundLabel.setContentsMargins(0, 0, 0, 30)
                groupboxLayout.addWidget(currentVersionNotFoundLabel)

            # Choosing a version folder
            choseVersionLabel = QLabel(self.choseVersionLabel)
            groupboxLayout.addWidget(choseVersionLabel)

            # Dropdown menu, with labels
            comboBoxMain = QComboBox()
            comboBoxMain.setFont(QFont("Arial", 11))
            self.fillDropdownMenu(comboBoxMain, self.folderMainPath)
            comboBoxMain.setContentsMargins(0, 30, 0, 30)
            groupboxLayout.addWidget(comboBoxMain)
            
            # Choosing a version
            subfolderLabel = QLabel(self.subfolderVersionLabel)
            groupboxLayout.addWidget(subfolderLabel)

            # Version 
            comboBoxSubFolder = QComboBox()
            comboBoxSubFolder.setFont(QFont("Arial", 11))
            groupboxLayout.addWidget(comboBoxSubFolder)

            comboBoxMain.currentIndexChanged.connect(lambda _, cbMain=comboBoxMain, cbSub=comboBoxSubFolder: self.updateSubFolders(cbMain, cbSub))

            addingEachButtonVM = QPushButton(self.runInstallationLabel)
            addingEachButtonVM.clicked.connect(lambda _, cbMain=comboBoxMain, cbSubfolder=comboBoxSubFolder, vm=hostnameVM[i]: self.installUpdate(cbMain.currentText(), cbSubfolder, vm))
            addingEachButtonVM.setContentsMargins(0, 30, 0, 30)
            hbox.addWidget(groupboxVM)
            hbox.setSpacing(10)
            hbox.setContentsMargins(10, 10, 10, 10)
            groupboxLayout.addWidget(addingEachButtonVM)

            groupboxVM.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            groupboxLayout.setSizeConstraint(QLayout.SetMinimumSize)
            
            groupboxVM.adjustSize()
            groupboxVM.setMinimumSize(groupboxVM.sizeHint())

            groupboxVM.setFont(self.font)
            

    def fillDropdownMenu(self, comboBoxVM, path):
        """
        Populates a dropdown menu with directory names from a specified path.

        Args:
            comboBoxVM (QComboBox): The combo box to populate with directory names.
            path (str): The path to search for directories.

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


    def updateSubFolders(self, comboBoxMain, comboBoxSubFolder):
        """
        Updates the items in the subfolder combo box based on the selected main folder.
        Args:
            comboBoxMain (QComboBox): The combo box containing the main folders.
            comboBoxSubFolder (QComboBox): The combo box to be updated with subfolders.
        Raises:
            Exception: If there is an error accessing the directory, it will add an error message to the subfolder combo box and print the error.
        """
        selectedMainFolder = comboBoxMain.currentText()
        mainFolderPath = os.path.join(self.folderMainPath, selectedMainFolder)

        comboBoxSubFolder.clear()
        if os.path.isdir(mainFolderPath):
            try:
                subdirectories = [name for name in os.listdir(mainFolderPath) if os.path.isdir(os.path.join(mainFolderPath, name))]
                comboBoxSubFolder.addItems(subdirectories)
            except Exception as e:
                comboBoxSubFolder.addItems(["network or path not found"])
                print(f"Fehler beim Zugriff auf den Netzwerkordner: {e}")


    def installUpdate(self, versionFolder, subfolderComboboxContent, vm):
        """
        Installs an update for the specified virtual machine (VM).
        This method writes the assignment file to the specified version folder and 
        executes the update installation process for the given VM. If an error occurs 
        during the installation, it displays a warning message.
        Args:
            versionFolder (str): The path to the folder containing the update version.
            subfolderComboboxContent (QComboBox): The combo box containing the assignment file names.
            vm (str): The name of the virtual machine to update.
        Raises:
            Exception: If an error occurs during the installation process, it is caught and displayed in a message box.
        """
        #Überprüfen ob im Controlling LFREF UND LF_REF, wenn ja soll bei "Updates installieren" das höchste Update vom vorherigen Update installieren
        assignmentFile = subfolderComboboxContent.currentText()
        self.writeInAssignmentTxt(versionFolder,assignmentFile,vm)
        try:
            if vm:
                self.runInstallerExecution.runExecution(vm)
                QMessageBox.information(self, "Installation der Maschine - "+vm, f"Update installieren wurde angestoßen und wird ausgeführt:\n{assignmentFile}")

        except Exception as e:
            QMessageBox.information(self, "Warnung - "+vm, f"{e}")

            print(e)


    def writeInAssignmentTxt(self,versionFolder, fileContent,hostname):
        """
        Ändert vom versionZugewiesen[Maschnummer] die Version was im 'subfolderComoboxContent' selektiert wurde.
        """
        hostNameEnding = hostname[-1]+".txt"

        assignmentHelperPath = os.getenv("INSTALL_HELPER_PATH") + "\\" + self.fileNameAssignmet + hostNameEnding
        print(assignmentHelperPath)
        print(fileContent)
        change = versionFolder + "\\" +fileContent
        print(change)

        # Datei im Lesemodus öffnen, um den Inhalt zu lesen
        with self.networkShare.openFileNetworkUser(assignmentHelperPath, "r") as file:
            print(file)
            lines = file.readlines()
        # Die erste Zeile durch den neuen Inhalt ersetzen oder hinzufügen, wenn die Datei leer ist
        lines = [change + "\n"] if not lines else [change + "\n"] + lines[1:]

        # Datei im Schreibmodus öffnen, um den neuen Inhalt zu schreiben
        with self.networkShare.openFileNetworkUser(assignmentHelperPath, "w") as file:
            print(file)
            file.writelines(lines)
            print(lines)
        
        print("changed")


    def getHeaderLayout(self):
        """
        Creates and returns the header layout for the window.

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


    def getMachinesLayout(self, numberVM, hostnameVM):
        """
        Creates and returns a QVBoxLayout containing the layout for virtual machines.

        Args:
            numberVM (int): The number of virtual machines.
            hostnameVM (str): The hostname of the virtual machines.

        Returns:
            QVBoxLayout: The layout containing the virtual machines components.
        """
        vmLayout = QVBoxLayout()
        self.createMachinesComponent(numberVM, hostnameVM)
        vmLayout.addLayout(self.vboxVM)
        return vmLayout
