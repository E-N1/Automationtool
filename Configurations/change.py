from Configurations.networkshare import NetworkShare
import re
import os

class Change():

    def __init__(self):
        self.share = NetworkShare()

        self.praefixStatus = None
        self.buildStatus = None
        self.ddStatus = None
        self.mmStatus = None
        self.yyyyStatus = None
        self.categoryStatus = None

        # Controlling Data
        self.dayControllingStatus = None
        self.monthControllingStatus = None
        self.yearControllingStatus = None
        self.buildControllingStatus = None
        self.updateControllingStatus = None
        self.praefixControllingStatus = None


    
    def changePraefix(self, data, masch, praefix):
        """
        Changes the prefix in the configuration file for a given machine.

        Args:
            data (str): The data path or identifier.
            masch (str): The machine identifier.
            praefix (str): The new prefix to be set in the configuration file.

        Returns:
            bool: True if the prefix was successfully changed, False if the file was not found.

        Raises:
            FileNotFoundError: If the configuration file does not exist.

        """
        changeline = []
        try:
            # Check whether Config exists, if not, one should be created.
            with self.share.openFileVMUser(data,masch,"r") as file:
                for line in file:
                    find = re.search(r'praefix\s*=\s*"(.*?)"', line)
                    if find:
                        newline = re.sub(r'praefix\s*=\s*"(.*?)"', f'praefix      = "{praefix}"', line)
                        changeline.append(newline)
                    else:
                        changeline.append(line)
            with self.share.openFileVMUser(data,masch, "w") as file:
                file.writelines(changeline)
            self.praefixStatus = True
            return self.praefixStatus
        except FileNotFoundError as e:
            print(e)
            self.praefixStatus = False
            return self.praefixStatus



    def changeBuild(self, data, masch, build):
        """
        Updates the build version in the configuration file for a given machine.

        This method reads the configuration file for the specified machine, searches for the 
        build version line, updates it with the new build version provided, and writes the 
        updated lines back to the file. If the configuration file does not exist, it will 
        handle the FileNotFoundError.

        Args:
            data (str): The data required to locate the configuration file.
            masch (str): The machine identifier for which the configuration file is to be updated.
            build (str): The new build version to be set in the configuration file.

        Returns:
            bool: True if the build version was successfully updated, False if the file was not found.
        """
        changeline = []
        try:
            # Check whether Config exists, if not, one should be created.
            with self.share.openFileVMUser(data,masch,"r") as file:
                for line in file:
                    find = re.search(r'build\s*=\s*"(.*?)"', line)
                    if find:
                        newline = re.sub(r'build\s*=\s*"(.*?)"', f'build        = "{build}"', line) 
                        changeline.append(newline)
                    else:
                        changeline.append(line)
            with self.share.openFileVMUser(data,masch, "w") as file:
                file.writelines(changeline)
            self.buildStatus = True
            return self.buildStatus
        except FileNotFoundError as e:
            print(e)
            self.buildStatus = False
            return self.buildStatus


    def changeDay(self,data,masch,day):
        """
        Modifies the day in a date string within a file.
        This method reads a file, searches for a specific date pattern, 
        and changes the day part of the date while keeping the rest of the date unchanged. The modified lines are then written back to the file.
        Args:
            data (str): The data parameter used to open the file.
            masch (str): The machine parameter used to open the file.
            day (str): The new day value to replace in the date string.
        Returns:
            bool: True if the operation was successful, False if the file was not found.
        Raises:
            FileNotFoundError: If the file specified by `data` and `masch` does not exist.
        Notes:
            - The method looks for lines containing 'vbdatum      = ' followed by a date in the format DD.MM.YYYY.
            - If the date is found, only the day part (DD) is replaced with the provided `day` value.
            - All lines, whether modified or not, are written back to the file.
        """
        changeline = []
        try:
            with self.share.openFileVMUser(data,masch,"r") as file:
                for line in file:
                    # Searches the date, but changes and the day, the rest remains
                    # Remaining lines should be saved and added to the list so that they are not deleted and can be called up again
                    if 'vbdatum      = ' in line :
                        searchVB = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', line)
                        if searchVB:
                            newDate = f"{day}.{searchVB.group(2)}.{searchVB.group(3)}"
                            newline = re.sub(searchVB.group(0),newDate,line)
                        else:
                            newline = line
                    else:
                        newline = line
                    changeline.append(newline)
            with self.share.openFileVMUser(data,masch, "w") as file:
                file.writelines(changeline)
            self.ddStatus = True
            return self.ddStatus
        except FileNotFoundError as e:
            print(e)
            self.ddStatus = False
            return self.ddStatus


    def changeMonth(self, data, masch, month):
        """
        Modifies specific lines in a file to change the month value.
        This method reads a file, searches for specific patterns in the lines, and updates the month value
        in those lines. The updated lines are then written back to the file.
        Args:
            data (str): The data required to open the file.
            masch (str): The machine identifier required to open the file.
            month (str): The new month value to replace in the file.
        Returns:
            bool: True if the month was successfully changed, False otherwise.
        Raises:
            Exception: If an error occurs during file operations, it prints an error message and returns False.
        """
        changeline = []
        try:
            with self.share.openFileVMUser(data,masch, "r") as file:
                for line in file:
                    if "testsammlung = " in line or 'TestDB       = ' in line:
                        searchTestAndDB = re.search(r'\\(\d{2})', line)
                        if searchTestAndDB:
                            newline = re.sub(searchTestAndDB.group(1), month, line)
                        else:
                            newline = line
                    elif 'vbdatum      = ' in line:
                        searchVB = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', line)
                        if searchVB:
                            newDate = f"{searchVB.group(1)}.{month}.{searchVB.group(3)}"
                            newline = re.sub(searchVB.group(0), newDate, line)
                        else:
                            newline = line
                    else:
                        newline = line
                    changeline.append(newline)

            with self.share.openFileVMUser(data,masch, "w") as file:
                file.writelines(changeline)
            self.mmStatus = True
            return self.mmStatus
        
        except Exception as e:
            print(e)
            self.mmStatus = False
            return self.mmStatus


    def changeYear(self, data, masch, year):
        """
        Modifies the year in specific lines of a file.
        This method reads a file, searches for specific patterns in the lines, and replaces the year with the provided year.
        The modified lines are then written back to the file.
        Args:
            data (str): The data parameter used to locate the file.
            masch (str): The masch parameter used to locate the file.
            year (str): The year to replace in the file.
        Returns:
            bool: True if the operation was successful, False if the file was not found.
        Raises:
            FileNotFoundError: If the file specified by data and masch is not found.
        Patterns:
            - "testsammlung = ": Searches for a pattern '\\d{2}-\\d{4}' and replaces the year part.
            - 'TestDB       = ': Searches for a pattern '\\d{2}-\\d{4}' and replaces the year part.
                Also handles patterns like 'YYYYMM.mdb' or 'YYMM.mdb'.
            - 'vbdatum      = ': Searches for a date pattern 'dd.mm.yyyy' and replaces the year part.
        """
        changeline = []
        try:
            with self.share.openFileVMUser(data,masch, "r") as file:
                for line in file:
                    if "testsammlung = " in line:
                        searchTest = re.search(r'\\(\d{2})-(\d{4})', line)
                        if searchTest:
                            newline = re.sub(searchTest.group(2), year, line)
                        else:
                            newline = line

                    elif 'TestDB       = ' in line:
                        searchTestDB = re.search(r'\\(\d{2})-(\d{4})', line)
                        match = re.search(r'["]?(\d{4}|\d{2})(\d{2})["]?\.mdb', line)

                        if searchTestDB:
                            yearPart = match.group(1)
                            newline = re.sub(searchTestDB.group(2), year, line)

                            if len(yearPart) == 2:
                                # Take the last two numbers of year, in the case of YYMM
                                newline = re.sub(match.group(1), year[2:], newline)

                            elif len(yearPart) == 4:
                                # YYYYMM.mdb
                                newline = re.sub(match.group(1), year, newline)

                    elif 'vbdatum      = ' in line:
                        searchVB = re.search(r'(\d{2})\.(\d{2})\.(\d{4})', line)
                        if searchVB:
                            newDate = f"{searchVB.group(1)}.{searchVB.group(2)}.{year}"
                            newline = re.sub(searchVB.group(0), newDate, line)

                    else:
                        newline = line

                    changeline.append(newline)

            with self.share.openFileVMUser(data,masch, "w") as file:
                file.writelines(changeline)
            self.yyyyStatus = True
            return self.yyyyStatus
        
        except FileNotFoundError as e:
            print(e)
            self.yyyyStatus = False
            return self.yyyyStatus
        

    def changeCategory(self, data, masch, category):
        """
        Changes the category in the specified file.
        This method reads a file, searches for a line containing "Kategorie:", and replaces the existing category value with the new category provided. If the category line is not found, it adds a new line with the category. The modified content is then written back to the file.
        Args:
            data (str): The path to the file where the category needs to be changed.
            masch (str): A parameter used by the `openFileVMUser` method to access the file.
            category (str): The new category value to be set in the file.
        Returns:
            bool: True if the category was successfully changed, False otherwise.
        Raises:
            Exception: If there is an error while reading or writing the file, an exception is caught and an error message is printed.
        """
        changeline = []
        try:
            dataunconverted = data.replace("\\", r"\\")
            with self.share.openFileVMUser(dataunconverted,masch, "r") as file:
                for line in file:
                    if "Kategorie:" in line:
                        # Extract the category value from the line, allowing any characters
                        category_match = re.search(r'Kategorie\s*=\s*"(.*?)"', line)
                        if category_match:
                            # Replace the matched category value with the new category
                            new_line = line.replace(category_match.group(1), category)
                            changeline.append(new_line)
                        else:
                            # If the category pattern is not found, add the category line
                            new_line = f'Kategorie:    = "{category}"\n'
                            changeline.append(new_line)
                    else:
                        changeline.append(line)

            with open(dataunconverted, "w") as file:
                file.writelines(changeline)
            self.categoryStatus = True
            return self.categoryStatus
        
        except Exception as e:
            print(e)
            self.categoryStatus = False
            return self.categoryStatus
        


    def changeLinesControlling(self, lineNr,masch, day=None, dayEntry=None, month=None, monthEntry=None, year=None, yearEntry=None, build=None, buildEntry=None, update=None, updateEntry=None, praefix=None, praefixEntry=None):
        changeline = []
        try:    
            with self.share.openFileRegisterSession(os.getenv("CONTROLLING_PATH"), masch, "r") as file:
                lines = file.readlines()  
                for i, line in enumerate(lines):
                    if i == lineNr - 1:  # Line index starts at 0
                        if lineNr == 1 and (day or month or year):
                            if day:
                                findDay = re.search(r"(\d{2})\.\d{2}\.\d{4}", line)
                                if findDay:
                                    line = line.replace(findDay.group(1), dayEntry)
                                    self.dayControllingStatus = True
                            if month:
                                findMonth = re.search(r"\d{2}\.(\d{2})\.\d{4}", line)
                                if findMonth:
                                    line = line.replace(findMonth.group(1), monthEntry)
                                    self.monthControllingStatus = True
                            if year:
                                findYear = re.search(r"\d{2}\.\d{2}\.(\d{4})", line)
                                if findYear:
                                    line = line.replace(findYear.group(1), yearEntry)
                                    self.yearControllingStatus = True
                        elif lineNr == 2 and buildEntry and build:
                            line = buildEntry + '\n'
                            self.buildControllingStatus = True
                        elif lineNr == 3 and updateEntry and update:
                            line = updateEntry + '\n'
                            self.updateControllingStatus = True
                        elif lineNr == 4 and praefixEntry and praefix:
                            line = praefixEntry + '\n'
                            self.praefixControllingStatus = True

                    changeline.append(line)  # Add each line, both modified and unmodified

            # Open file for writing and write Configurations.paths import Paths
            with self.share.openFileRegisterSession(os.getenv("CONTROLLING_PATH"), "w") as file:
                file.writelines(changeline)

        except Exception as e:
            print(f"An error occurred: {e}")


    # Controlling
    def getDayControllingStatus(self):
        if self.dayControllingStatus:
            return "Tag im Controlling(Zeile 1) geaendert"
        else:
            return "Tag im Controlling(Zeile 1) konnte nicht geaendert werden"
        
    def getMonthControllingStatus(self):
        if self.monthControllingStatus:
            return "Monat im Controlling(Zeile 1) geaendert"
        else:
            return "Monat im Controlling(Zeile 1) konnte nicht geaendert werden"
        
    def getYearControllingStatus(self):
        if self.yearControllingStatus:
            return "Jahr im Controlling(Zeile 1) geaendert"
        else:
            return "Jahr im Controlling(Zeile 1) konnte nicht geaendert werden"

    def getBuildControllingStatus(self):
        if self.buildControllingStatus:
            return "Build im Controlling(Zeile 2) geaendert"
        else:
            return "Build im Controlling(Zeile 2) konnte nicht geaendert werden"

    def getUpdateControllingStatus(self):
        if self.updateControllingStatus:
            return "Update im Controlling(Zeile 3) geaendert"
        else:
            return "Update im Controlling(Zeile 3) konnte nicht geaendert werden"

    def getPraefixControllingStatus(self):
        if self.praefixControllingStatus:
            return "Praefix im Controlling(Zeile 4) geaendert"
        else:
            return "Praefix im Controlling(Zeile 4) konnte nicht geaendert werden"

    def getPraefixStatus(self):
        if self.praefixStatus:
            return "Praefix geaendert"
        else:
            return "Praefix konnte nicht geaendert werden"

    def getBuildStatus(self):
        if self.buildStatus:
            return "Build geaendert"
        else:
            return "Build konnte nicht geandert werden"

    def getddStatus(self):
        if self.ddStatus:
            return "Tag geaendert"
        else:
            return "Tag konnte nicht geandert werden"

    def getmmStatus(self):
        if self.mmStatus:
            return "Monat geaendert"
        else:
            return "Monat konnte nicht geandert werden"

    def getyyyyStatus(self):
        if self.yyyyStatus:
            return "Jahr geaendert"
        else: 
            return "Jahr konnte nicht geandert werden"

