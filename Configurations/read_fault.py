import os
import re
import time

from Configurations.networkshare import NetworkShare
from Configurations.machines import Machines

class ReadFault:
    def __init__(self):
        # Configurations
        self.networkShare = NetworkShare()
        self.machines = Machines()
        self.module = os.getenv("MODULE")
        
        # Fault-list
        self.errorList = os.getenv("ERROR_LIST")
        self.dictMachineErrors = {}
        self.lastModifiedTimes = {}
            

    def getCurrentVersionMachine(self, masch, modulOption=None, versionOption=None, versionDateOption=None):
        """
        Retrieves the current version, module, or version date of a machine from the system log.
        Args:
            masch (str): The machine identifier.
            modulOption (bool, optional): If True, return the module name. Defaults to None.
            versionOption (bool, optional): If True, return the version. Defaults to None.
            versionDateOption (bool, optional): If True, return the version date. Defaults to None.
        Returns:
            str: The requested information (module, version, or version date) based on the provided options.
            None: If the information could not be retrieved or an error occurred.
        Raises:
            ValueError: If neither version nor module string is found in the specified format.
            FileNotFoundError: If the system log file is not found.
            IOError: If an I/O error occurs while reading the file.
            Exception: For any other exceptions that occur during execution.
        """

        try:
            readLine = 8
            systemLogPath = os.getenv("MACHINE_SYSTEMLOG_PATH")
            retry_attempts = 5
            retry_delay = 1  # in seconds

            # Create a regex pattern to match any of the module names
            module_pattern = '|'.join(self.module)
            regex_pattern = rf'ergebnis\\({module_pattern})\\(\d{{2}}-\d{{4}})\\'

            for attempt in range(retry_attempts):
                try:
                    with self.networkShare.openFileVMUser(systemLogPath, masch, 'r') as file:
                        for lineNum, line in enumerate(file, start=1):
                            if lineNum == readLine:
                                matchLF = re.search(r'\\(LF[^\\]*)\\', line)
                                matchLT = re.search(r'\\(LT[^\\]*)\\', line)
                                matchLFREF = re.search(r'\\(LFREF[^\\]*)\\', line)

                                # Find the version based on priority: LF > LT > LFREF > None
                                if matchLF:
                                    version = matchLF.group(1)
                                elif matchLT:
                                    version = matchLT.group(1)
                                elif matchLFREF:
                                    version = matchLFREF.group(1)
                                else:
                                    version = None

                                matchModul = re.search(regex_pattern, line)
                                modul = matchModul.group(1).strip() if matchModul else None
                                version_date = matchModul.group(2) if matchModul else None

                                # Return the desired value based on option flags
                                if version and modul and version_date:
                                    if modulOption is not None:
                                        return modul
                                    elif versionOption is not None:
                                        return version
                                    elif versionDateOption is not None:
                                        return version_date
                                else:
                                    raise ValueError("Neither version nor modul string found in the specified format.")
                except FileNotFoundError as fnf_error:
                    if attempt == retry_attempts - 1:
                        print(f"Attempt {attempt + 1} failed: FileNotFoundError: {fnf_error}")
                except IOError as io_error:
                    if attempt == retry_attempts - 1:
                        print(f"Attempt {attempt + 1} failed: IOError: {io_error}")
                except Exception as e:
                    if attempt == retry_attempts - 1:
                        print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay)
                    return None
        except Exception as e:
            print(e)
            return None


    def readOverview(self, masch):
        """
        Reads the overview of machine errors from a specified machine and updates the dictionary of machine errors.
        Args:
            masch (str): The machine identifier.
        Returns:
            None
        This method performs the following steps:
        1. Retrieves the current module version, software version, and version date of the specified machine.
        2. Checks if the retrieved versions and date are valid.
        3. Constructs the base path to the machine's error overview files.
        4. Checks if the base path exists.
        5. Iterates through the categories in the base path and processes the "uebersicht.txt" file in each category.
        6. Reads the "uebersicht.txt" file and extracts error patterns for each test case.
        7. Updates the dictionary of machine errors with the extracted error patterns.
        Raises:
            Exception: If an error occurs while reading the overview, an exception is caught and an error message is printed.
        """
        try:
            modulVersion = self.getCurrentVersionMachine(masch, modulOption=True)
            softwareVersion = self.getCurrentVersionMachine(masch, versionOption=True)
            versionDate = self.getCurrentVersionMachine(masch, versionDateOption=True)
            
            if not modulVersion or not softwareVersion or not versionDate:
                return

            self.dictMachineErrors[masch] = {}
            base_path = os.getenv("BASEPATH")
            if not os.path.exists(base_path):
                return


            for category in os.listdir(base_path):
                category_path = os.path.join(base_path, category)
                if os.path.isdir(category_path):
                    self.dictMachineErrors[masch][category] = {pattern: [] for pattern in self.errorList}
                    uebersicht_path = os.path.join(category_path, "uebersicht.txt")

                    if os.path.exists(uebersicht_path):
                        with self.networkShare.openFileVMUser(uebersicht_path,masch, 'r') as file:
                            currentTestCase = None
                            temp_errors = {pattern: [] for pattern in self.errorList}
                            
                            for line in file:
                                cleanLine = line.strip() + "<br>"  # for html, break line
                                if line.startswith("Start TF"):
                                    currentTestCase = line.strip() + "<br>"
                                elif line.startswith("Ende  TF"):
                                    if currentTestCase:
                                        for errorPattern in self.errorList:
                                            if temp_errors[errorPattern]:
                                                self.dictMachineErrors[masch][category][errorPattern].append(currentTestCase + ''.join(temp_errors[errorPattern]))
                                    currentTestCase = None
                                    temp_errors = {pattern: [] for pattern in self.errorList}
                                elif currentTestCase:
                                    for errorPattern in self.errorList:
                                        if errorPattern in line:
                                            temp_errors[errorPattern].append(cleanLine + "<br>")
                    else:
                        print(f"{uebersicht_path} does not exist")
        except Exception as e:
            print(f"{e}")


    def getVersionPath(self, masch):
        """
        Constructs and returns the file path for the specified machine's version information.
        Args:
            masch (str): The machine identifier.
        Returns:
            str: The constructed file path in the format:
        Notes:
            - `modulVersion`, `softwareVersion`, and `versionDate` are obtained by calling 
              `getCurrentVersionMachine` with different options.
        """
        modulVersion = self.getCurrentVersionMachine(masch, modulOption=True)
        softwareVersion = self.getCurrentVersionMachine(masch, versionOption=True)
        versionDate = self.getCurrentVersionMachine(masch, versionDateOption=True)

        if not modulVersion or not softwareVersion or not versionDate:
            return None

        basepath_template = os.getenv("BASEPATH_TEMPLATE")

        version_path = basepath_template.format(masch=masch, modulVersion=modulVersion, versionDate=versionDate, softwareVersion=softwareVersion)
        return version_path


    def getAllCategories(self, masch):
        """
        Retrieves all categories for a given machine.

        This method constructs the version path for the specified machine and checks if the path exists.
        If the path does not exist, it prints an error message and returns an empty list.
        If the path exists, it lists all folders in the path that start with "Kategorie" and returns them as a list.

        Args:
            masch (str): The identifier for the machine.

        Returns:
            list: A list of category folder names that start with "Kategorie". If the path does not exist, returns an empty list.
        """
        path = self.getVersionPath(masch)
        if not os.path.exists(path):
            print(f"Es konnte für {masch} kein Ergebnis auslesen werden. Bitte Überprüfe einmal deine Konfigurationen.")
            return []
        categories = [folder for folder in os.listdir(path) if folder.startswith("Kategorie")]
        return categories
        

    def getErrorsForPattern(self, masch, category, pattern):
        """
        Retrieve errors for a specific machine, category, and pattern.

        Args:
            masch (str): The machine identifier.
            category (str): The category of the error.
            pattern (str): The pattern of the error.

        Returns:
            list: A list of errors matching the specified machine, category, and pattern.
                  Returns an empty list if no matching errors are found.
        """
        if masch in self.dictMachineErrors and category in self.dictMachineErrors[masch] and pattern in self.dictMachineErrors[masch][category]:
            return self.dictMachineErrors[masch][category][pattern]
        else:
            return []
