import os
import re
import psutil
import subprocess

from Configurations.networkshare import NetworkShare


class ReadControlling():

    def __init__(self):
        self.dayStatusControlling = None
        self.monthStatusControlling = None
        self.yearStatusControlling = None
        self.runStatusControlling = None
        self.updateStatusControlling = None
        self.praefixStatusControlling = None
        self.timeManagerKilled = False
        self.processname= "timeManager2.exe"

        self.controllingEntries = []

        self.networkShare = NetworkShare()

        # Checking Timemanager and kill process, for reading controlling.txt
        self.checkIfTimemanagerIsActiv()

        # Read the controlling
        self.getControllingData()

        self.startTimeManager()

    def checkIfTimemanagerIsActiv(self):
        """Checks whether the "timeManager2.exe" process is running."""


        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == self.processname.lower():
                    print(f"End process {proc.info['name']} with process ID {proc.pid}")
                    proc.terminate()
                    self.timeManagerKilled = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        if self.timeManagerKilled:
            print(f"The process '{self.processname}' has been terminated.")
        else:
            print(f"The process '{self.processname}' is not active.")

    def killTimemanager(self):
        """Terminates the process 'timeManager2.exe'."""

        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == self.processname.lower():
                    print(f"End process {proc.info['name']} with process ID {proc.pid}")
                    proc.terminate()
                    self.timeManagerKilled = True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        if self.timeManagerKilled:
            print(f"The process '{self.processname}' has been terminated.")
        else:
            print(f"The process '{self.processname}' is not active.")
        
    def startTimeManager(self):
        # Startet den Prozess
        try:
            # Falls keine Argumente erforderlich sind, entferne die 'args' Schlüsselwort
            subprocess.Popen([os.getenv("TIME_MANAGER_PATH")], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("Timemanager started")

        except Exception as e:
            print(f"Error when starting the process, timeManager: {e}")


    def getControllingData(self):
        self.readDay()
        self.readMonth()
        self.readYear()
        self.readBuild()
        self.readUpdate()
        self.readPraefix()

    def readDay(self):
        """ reads the tag from the Controlling.txt from the first line. """
        day = ""
        try:
            file = self.networkShare.openFileRegisterSession(os.getenv("CONTROLLING_PATH"), "r")
            if not file:
                raise TypeError("Returned file object is None")

            with file as f:
                firstLine = f.readline().strip()
                findDay = re.search(r"(\d{2})\.\d{2}\.\d{4}", firstLine)
                if findDay:
                    day = findDay.group(1)
                    self.controllingEntries.append(day)
                    self.dayStatusControlling = True
                return findDay
        except FileNotFoundError as e:
            print(f"File not found error: {e}")
            self.dayStatusControlling = False
            return self.dayStatusControlling
        except TypeError as e:
            print(f"Type error: {e}")
            self.dayStatusControlling = False
            return self.dayStatusControlling
        except Exception as e:
            print(f"An error occurred: {e}")
            self.dayStatusControlling = False
            return self.dayStatusControlling


    def readMonth(self):
        """ reads the month from the first line of Controlling.txt. """
        month = ""
        try:
            with self.networkShare.openFileRegisterSession(os.getenv("CONTROLLING_PATH"), "r") as file:
                firstLine = file.readline().strip()
                findMonth = re.search(r"\d{2}\.(\d{2})\.\d{4}", firstLine)
                if findMonth:
                    month = findMonth.group(1)
                    self.controllingEntries.append(month)
                    self.monthStatusControlling = True
                return findMonth
        except FileNotFoundError as e:
            print(e)
            self.monthStatusControlling = False
            return self.monthStatusControlling

    def readYear(self):
        """ reads the year from the first line of Controlling.txt. """
        year = ""
        try:
            with self.networkShare.openFileRegisterSession(os.getenv("CONTROLLING_PATH"), "r") as file:
                firstLine = file.readline().strip()
                findYear = re.search(r"\d{2}\.\d{2}\.(\d{4})", firstLine)
                if findYear:
                    year = findYear.group(1)
                    self.controllingEntries.append(year)
                    self.yearStatusControlling = True
                return findYear
        except FileNotFoundError as e:
            print(e)
            self.yearStatusControlling = False
            return self.yearStatusControlling


    def readBuild(self):
        """
        Read the second line, run from Controlling.txt.
        """ 
        run = ""
        try:
            with self.networkShare.openFileRegisterSession(os.getenv("CONTROLLING_PATH"), "r") as file:
                lines = file.readlines()
                if len(lines) >= 2:
                    self.runStatusControlling = True
                    run = lines[1].strip()
                    self.controllingEntries.append(run)
                    return run
        except FileNotFoundError as e:
            print(e)
            self.runStatusControlling = False
            return self.runStatusControlling
        

    def readUpdate(self):
        """
        Reads the third line, update from Controlling.txt.
        """ 
        update = ""
        try:
            with self.networkShare.openFileRegisterSession(os.getenv("CONTROLLING_PATH"), "r") as file:
                lines = file.readlines()
                if len(lines) >= 3:
                    update += lines[2].strip()
                    self.controllingEntries.append(update)
                    self.updateStatusControlling = True
                    return update
        except FileNotFoundError as e:
            print(e)
            self.updateStatusControlling = False
            return self.updateStatusControlling


    def readPraefix(self):
        """
        Reads the third line, update from Controlling.txt.
        """ 
        praefix = ""
        try:
            with self.networkShare.openFileRegisterSession(os.getenv("CONTROLLING_PATH"), "r") as file:
                lines = file.readlines()
                if len(lines) >= 4:
                    self.praefixStatusControlling = True
                    praefix += lines[3].strip()
                    self.controllingEntries.append(praefix)
                    return praefix
        except FileNotFoundError as e:
            print(e)
            self.praefixStatusControlling = False
            return self.praefixStatusControlling