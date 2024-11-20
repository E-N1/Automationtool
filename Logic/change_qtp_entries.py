from PyQt5.QtWidgets import QMessageBox

from Configurations.networkshare import NetworkShare
from Configurations.change import Change
from Configurations.machines import Machines
from Configurations.json_writer import JsonWriter

from UI.vm_manager import VMManager

from datetime import datetime


class ChangeQTPEntries:

    def __init__(self):
        # Configurations
        self.machines = Machines()
        self.change = Change()
        self.networkShare = NetworkShare()
        self.jsonWriter = JsonWriter()

        # UI
        self.vmManager = VMManager()

        self.maschlist = self.machines.getNumberOfMachines()
        self.folderSearched = False

    def searchFolder(self,masch):
        """
        Searches through the folder and applies changes based on the provided machine and header entries.

        Args:
            masch (str): The machine identifier to apply changes to.

        Returns:
            None

        Raises:
            Exception: If there is an error while listing files.

        This method performs the following steps:
        1. Initializes the folder search status and an info message list.
        2. Retrieves header entries from the VM manager.
        3. Checks if any header entry is set.
        4. Checks if any machine is active.
        5. If no machine is active but headers are set, applies header changes and returns.
        6. If headers and machines need changes, or only machines are active, iterates through the machines:
            - Checks if the machine is active.
            - If active, retrieves modules and applies changes to each module entry.
            - Updates the info message list with the change status.
            - Changes QTP folders based on the header entries.
        7. If the folder search is completed, writes the changes to a JSON writer and displays an information window.
        8. If the folder search is not completed, prints an error message.
        """
        self.folderSearched = False
        infoMessage = []
        headerEntrys = {
            "dd": self.vmManager.getHeaderEntry('dd'),
            "mm": self.vmManager.getHeaderEntry('mm'),
            "yyyy": self.vmManager.getHeaderEntry('yyyy'),
            "praefix": self.vmManager.getHeaderEntry('praefix'),
            "update": self.vmManager.getHeaderEntry('update'),
            "build": self.vmManager.getHeaderEntry('build')
        }

        # Check if any header entry is set
        headerSet = any(value for value in headerEntrys.values())

        # Check if any machine is active
        anyMachineActive = False
        for i in range(1, self.maschlist + 1):
            machineName = self.machines.getMachinesName(i)
            if machineName in self.vmManager.vmDict:
                vmDict = self.vmManager.vmDict[machineName]
                isActiv = vmDict.get("Activ", {}).get("bool") == "True"
                if isActiv:
                    anyMachineActive = True
                    break

        # Check if no machine is active but headers are set
        if not anyMachineActive and headerSet:
            self.applyHeaderChanges(headerEntrys,masch)
            infoMessage.append(f"\n{headerEntrys}\n:")
            return

        # If headers and machines need changes, or only machines are active
        try:
            for i in range(1, self.maschlist + 1):
                machineName = self.machines.getMachinesName(i)

                if machineName not in self.vmManager.vmDict:
                    print(f"VM index {machineName} not found in vmDict")
                    continue
                vmDict = self.vmManager.vmDict[machineName]

                isActiv = vmDict.get("Activ", {}).get("bool") == "True"


                if isActiv:
                    print(f"boolActiv is True for VM {machineName}")
                    hostname = machineName
                    modules = self.machines.getModuleFromMachine(hostname)
                    for module in modules:
                        if module not in vmDict:
                            continue
                        moduleDict = vmDict[module]
                        if isinstance(moduleDict, dict):
                            for entryKey, entryValue in moduleDict.items():
                                if entryValue == "True":
                                    machineFilePath = self.machines.changeMachinePathBasedOnModule(i, module)
                                    self.change.changeCategory(machineFilePath,masch, entryKey)
                                    if self.change.categoryStatus == True:
                                        infoMessage.append(f"\n{machineName}\nModul: {module}\nEintrag: {entryKey}\n\n")
                                        print(f"In {machineName}: Category was changed in {module}, {entryKey}")
                                    else:
                                        infoMessage.append(f"\n{machineName}\nModul: {module} failed ")
                                        break
                                    self.changingQTPFolders(
                                        machineFilePath,
                                        **{k: v for k, v in headerEntrys.items() if v}
                                    )

                self.folderSearched = True

        except Exception as e:
            print(f"Error listing files: {e}")

        if self.folderSearched:
            print("All machines gone through.")
            numbersOfEntries = self.jsonWriter.getNumbersOfEntries()

            for machineName in set(msg.split('\n')[0] for msg in infoMessage if "Modul:" in msg):
                machineData = {
                    self.jsonWriter.hostname: hostname,
                    self.jsonWriter.timestamp: self.getCurrentTimestamp(),
                    self.jsonWriter.dd: headerEntrys['dd'],
                    self.jsonWriter.mm: headerEntrys['mm'],
                    self.jsonWriter.yyyy: headerEntrys['yyyy'],
                    self.jsonWriter.modulEntry: self.extractModuleEntries(infoMessage, machineName)
                }
                self.jsonWriter.writeEntry(numbersOfEntries + 1, machineData)

            self.informationWindow("".join(infoMessage))
        else:
            print("Execution was canceled! Something went wrong.")


    def applyHeaderChanges(self, headerEntrys,masch):
        """
        Applies changes to header entries for a given machine.

        Args:
            headerEntrys (dict): A dictionary containing header entry values with keys 'dd', 'mm', 'yyyy', 'build', 'update', and 'praefix'.
            masch (str): The machine identifier.

        Raises:
            Exception: If an error occurs while updating header entries.

        Example:
            headerEntrys = {
                'dd': '01',
                'mm': '12',
                'yyyy': '2023',
                'build': '1234',
                'update': '5678',
                'praefix': 'AB'
            }
            masch = 'machine_1'
            applyHeaderChanges(headerEntrys, masch)
        """
        try:
            self.change.changeLinesControlling(
                1,masch,
                day=bool(headerEntrys['dd']),
                dayEntry=headerEntrys['dd'],
                month=bool(headerEntrys['mm']),
                monthEntry=headerEntrys['mm'],
                year=bool(headerEntrys['yyyy']),
                yearEntry=headerEntrys['yyyy'],
            )
            self.change.changeLinesControlling(2,masch, build=bool(headerEntrys['build']), buildEntry=headerEntrys['build'])
            self.change.changeLinesControlling(3,masch, update =bool(headerEntrys['update']),updateEntry =headerEntrys['update'])
            self.change.changeLinesControlling(4,masch, praefix=bool(headerEntrys['praefix']), praefixEntry=headerEntrys['praefix'])
            print("Header entries updated.")
        except Exception as e:
            print(f"Error updating header entries: {e}")



    def changingQTPFolders(self, filePath, dd=None, mm=None, yyyy=None, praefix=None, build=None):
        """
        Changes QTP folder entries based on the provided parameters.

        This method updates the QTP folder entries by calling the corresponding 
        methods for day, month, year, prefix, and build if their values are provided.

        Args:
            filePath (str): The path to the file where the changes will be applied.
            dd (int, optional): The day value to change. Defaults to None.
            mm (int, optional): The month value to change. Defaults to None.
            yyyy (int, optional): The year value to change. Defaults to None.
            praefix (str, optional): The prefix value to change. Defaults to None.
            build (str, optional): The build value to change. Defaults to None.

        """
        # Mapping of parameters to corresponding methods
        changes = {
            "changeDay": dd,
            "changeMonth": mm,
            "changeYear": yyyy,
            "changePraefix": praefix,
            "changeBuild": build
        }
        # Iterate through the changes and call the corresponding method if the value is not None
        for method, value in changes.items():
            if value is not None:
                getattr(self.change, method)(filePath, value)


    def getCurrentTimestamp(self):
            """
            Get the current timestamp.

            Returns:
                str: The current date and time formatted as 'dd.mm.YYYY - HH:MM'.
            """
            now = datetime.now()
            return now.strftime('%d.%m.%Y - %H:%M')


    def extractModuleEntries(self, infoMessage, machineName):
        """
        Extracts module entries from the provided info messages for a specific machine.
        Args:
            infoMessage (list of str): List of information messages to be parsed.
            machineName (str): The name of the machine to filter messages.
        Returns:
            list of str: A list of module entries in the format "ModuleName: 'EntryName'".
        """
        moduleEntries = []
        for message in infoMessage:
            if machineName in message and "Modul:" in message and "Eintrag:" in message:
                moduleName = message.split("Modul: ")[1].split("\n")[0]
                entry_name = message.split("Eintrag: ")[1].split("\n")[0]
                moduleEntry = f"{moduleName}: '{entry_name}'"
                moduleEntries.append(moduleEntry)
        return moduleEntries


    def informationWindow(self, message):
        """
        Displays an information window with a given message.

        Args:
            message (str): The message to be displayed in the information window.

        Returns:
            QMessageBox.StandardButton: The button that was clicked to close the message box.
        """
        return QMessageBox.information(None, "Information", "Maschine/n durchgelaufen, folgende Informationen:\n" + message)
