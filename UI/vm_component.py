from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QLineEdit, QDialog, QDialogButtonBox, QPushButton, QMessageBox
from PyQt5.QtGui import QFont

from UI.vm_manager import VMManager
from Configurations.machines import Machines

class VMComponent:
    def __init__(self, number, button=None, boolean=None, hostname=None, i=None, vmGroupBox=None, machines=None):
        self.number = number
        self.boolActiv = boolean
        self.addingEachButtonVM = button
        self.vmGroupBox = vmGroupBox
        self.hostname = hostname
        self.iLoop = i
        self.entrysFromGUIDiaglog = []
        self.boolFromGUIDialog = []

        # Boolean
        self.boolEntriesList = []
        self.boolActiv = False
        self.resetVM = False
        self.resetControlling = False

        # Entries
        self.entriesList = []
        self.machines = machines  

        # Dict
        self.moduleEntries = {}
        self.attributesDict = {}

        # Style
        self.font = QFont("Arial", 11)
        
        # Imports
        self.machines = Machines()
        self.vmManager = VMManager()


    def createModuleWidget(self, module):
        """
        Creates a widget for a given module consisting of a label, a checkbox, and a line edit.
        Args:
            module (str): The name of the module to create the widget for.
        Returns:
            QWidget: A widget containing the module label, checkbox, and line edit.
        """
        hbox = QHBoxLayout()
        moduleLabel = QLabel(module)
        moduleCheckbox = QCheckBox()
        moduleEntry = QLineEdit()
        hbox.addWidget(moduleLabel)
        hbox.addWidget(moduleCheckbox)
        hbox.addWidget(moduleEntry)
        moduleWidget = QWidget()
        moduleWidget.setLayout(hbox)

        # Set initial checkbox state
        moduleCheckbox.setChecked(False)
        
        # Save module entry reference
        self.moduleEntries[module] = (moduleCheckbox, moduleEntry)
        
        return moduleWidget
    

    def openDialogVM(self):
        """
        Opens a dialog to configure VM modules and their attributes.

        This method initializes a dialog window where the user can configure
        various modules of a virtual machine. The dialog includes checkboxes
        and text entries for each module, and buttons to save or discard the
        changes.

        The method performs the following steps:
        1. Initializes the dialog window and layout.
        2. Retrieves the modules for the current machine.
        3. Creates widgets for each module and adds them to the layout.
        4. Adds buttons for saving, canceling, and discarding changes.
        5. Connects button actions to their respective slots.
        6. Processes the dialog result to update the VM attributes.

        If the user accepts the dialog, the method validates the entries and
        updates the VM attributes dictionary. If any entries are invalid, a
        warning is shown. The method also updates the UI elements to reflect
        the changes.

        Attributes:
            moduleEntries (dict): Stores the state of each module's checkbox and text entry.
            resetVM (bool): Flag to reset the VM state.
            resetControlling (bool): Flag to reset the controlling state.
            dialog (QDialog): The dialog window instance.
            attributesDict (dict): Dictionary to store the attributes of the VM modules.
            boolActiv (bool): Flag to indicate if the VM is active.
        """
        self.moduleEntries = {}
        self.resetVM = False
        self.resetControlling = False

        self.dialog = QDialog()
        self.dialog.setWindowTitle("VM: " + str(self.hostname[self.iLoop]))

        vbox = QVBoxLayout()
        labelControlling = QLabel(f"{self.hostname[self.iLoop]}")
        labelControlling.setFont(QFont("Arial", 12))
        vbox.addWidget(labelControlling)

        # Creating widgets for each module of the machine
        modules = self.machines.getModuleFromMachine(self.hostname[self.iLoop])
        for module in modules:
            moduleWidget = self.createModuleWidget(module)
            self.entriesList.append(module)
            vbox.addWidget(moduleWidget)

        # Creating button box for dialog actions
        buttonBox = QDialogButtonBox()
        acceptButton = buttonBox.addButton("Eintragung speichern", QDialogButtonBox.AcceptRole)
        cancelButton = buttonBox.addButton("Abbrechen", QDialogButtonBox.RejectRole)

        # Adding discard button
        discardBox = QPushButton("Eintragung verwerfen")
        vbox.addWidget(discardBox)

        # Adding buttons to the layout
        vbox.addWidget(buttonBox)

        self.dialog.setLayout(vbox)

        acceptButton.clicked.connect(self.dialog.accept)
        cancelButton.clicked.connect(self.dialog.reject)
        discardBox.clicked.connect(lambda _, reset=True: self.discardVM(reset))

        if self.dialog.exec_() == QDialog.Accepted:
            self.discardVM(reset=False)
            validEntries = True  # Flag to check if all entries are valid

            for module in modules:
                isChecked = self.moduleEntries[module][0].isChecked()
                entryText = self.moduleEntries[module][1].text()

                # Check if the module is checked and entry is not empty
                if isChecked and entryText:
                    # Create the moduleDict for each module
                    self.attributesDict["Activ"] = {
                        'bool': "True"
                    }
                    self.attributesDict[module] = {
                        entryText: "True"
                    }
                elif isChecked and not entryText:
                    # If checked but entry is empty, show a warning
                    validEntries = False
                    self.attributesDict["Activ"] = {
                        'bool': "False"
                    }
                    self.attributesDict[module] = {
                        "": "True"
                    }

                elif not isChecked and entryText:
                    # If entry is not empty but checkbox is not checked, show a warning
                    validEntries = False
                    self.attributesDict["Activ"] = {
                        'bool': "False"
                    }
                    self.attributesDict[module] = {
                        entryText: "False"
                    }
                else:
                    # Create the moduleDict with unchecked state
                    self.attributesDict[module] = {
                        "": "False"
                    }

            if not validEntries:
                self.informationWindow()
                return
            else:
                self.vmGroupBox.adjustSize()
                # Update entrysFromGUIDiaglog with valid entries
                for module in modules:
                    entryText = next(iter(self.attributesDict[module].keys()))
                    isChecked = self.attributesDict[module][entryText] == "True"

                    for hboxInside in self.entrysFromGUIDiaglog:
                        if not type(hboxInside) == dict:
                            label = hboxInside.itemAt(0).widget().text()
                            if label == module:
                                hboxInside.itemAt(1).widget().setText(entryText if isChecked else "''")

                # Background from Adding Button
                self.boolActiv = True
                self.addingEachButtonVM.setStyleSheet("background-color: green;")
                self.addingEachButtonVM.setFont(self.font)

            if self.resetVM:
                self.addingEachButtonVM.setStyleSheet("")
                self.addingEachButtonVM.setFont(self.font)
                self.boolActiv = False

            if self.resetControlling:
                self.addingEachButtonVM.setStyleSheet("")
                self.addingEachButtonVM.setFont(self.font)
                self.boolActiv = False

            # Set the VMManager object in the class to the created attributes dictionary
            print(self.attributesDict)
            self.vmManager.vmDict[str(self.hostname[self.iLoop])] = self.attributesDict


    def discardVM(self, reset):
        """
        Discards the current VM configuration and optionally resets the VM.

        Parameters:
        reset (bool): If True, the VM will be marked as reset and the dialog will be accepted.
        """
        # Clear the attributes dictionary
        self.attributesDict.clear()

        # Accept the dialog to close it
        if reset == True:
            # Mark the VM as reset
            self.resetVM = True
            self.dialog.accept()
            print("Config discarded for VM")


    def informationWindow(self):
        """
        Displays an information message box with a warning message.

        This method shows a QMessageBox with a warning message indicating that at least one checkbox must be activated 
        and an entry must be made in the field to write to the configuration.

        Returns:
            QMessageBox.StandardButton: The button that was clicked to dismiss the message box.
        """
        return QMessageBox.information(None, "Warnung", "Um in die Konfiguration zu schreiben, müssen mindestens eine Checkbox aktiviert und ein Eintrag in das Feld gemacht sein.")
