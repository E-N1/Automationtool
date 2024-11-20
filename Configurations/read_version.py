import os
import re

from Configurations.networkshare import NetworkShare
from Configurations.machines import Machines

class ReadVersion():

    def __init__(self):
        self.currentVersionListInsideFile = {}
        self.files = []
        
        self.machines = Machines()
        self.networkShare = NetworkShare()

        self.listFolder()
        self.comparativeAlgorithm()

    def listFolder(self):
        """
        Lists files in the specified network folder that match a specific pattern.
        This method checks if the path specified in `os.getenv("INSTALL_HELPER_PATH")` exists.
        If the path exists, it lists all files in the directory that match the pattern
        "versionAktuell" followed by a digit (1-9) or a letter (A-Z) and ending with ".txt".
        The matching files are appended to `self.files`.
        Raises:
            Exception: If there is an error accessing the network folder.
        Prints:
            A message indicating if the specified path does not exist.
            A message indicating an error accessing the network folder.
        """
        try:
            # Überprüfen, ob der Pfad korrekt ist
            if not os.path.exists(os.getenv("INSTALL_HELPER_PATH")):
                print(f"Path does not exist: {os.getenv("INSTALL_HELPER_PATH")}")

            # Liste der Dateien im Netzwerkordner
            directories = [name for name in os.listdir(os.getenv("INSTALL_HELPER_PATH")) if os.path.isfile(os.path.join(os.getenv("INSTALL_HELPER_PATH"), name))]

            pattern = re.compile(r"^versionAktuell([1-9]|[A-Za-z])\.txt$")
            for directory in directories:
                # Überprüfen, ob der Dateiname mit "versionAktuell" beginnt und entweder mit einer Ziffer (1-5) oder einem Buchstaben (A-Z) endet
                if pattern.match(directory):
                    self.files.append(directory)

        except Exception as e:
            print(f"Error accessing the network folder:{e}")

    def comparativeAlgorithm(self):
        """
        Check each versionAktuell[NUMBER] with the added current maschines in machines.json
        When versionAktuell([Number]) == masch[Number]:
        Start process reading file inside and return for main-window
        """

        # Extract the endings from the filenames
        fileEndings = [re.search(r"versionAktuell([_a-zA-Z0-9]+)\.txt$", file).group(1) for file in self.files]
        machineEndings = [re.search(r"masch([_a-zA-Z0-9]+)", machine).group(1) for machine in self.machines.getMachineNameOfAll()]

        for fileEnding in fileEndings:
            for machineEnding in machineEndings:
                if re.match(fr"^{machineEnding}", fileEnding):

                    file = fr"versionAktuell{fileEnding}.txt"
                    masch = f"masch{machineEnding}"
                    # Speichern der Inhalte der Dateien in einem Dictionary
                    self.currentVersionListInsideFile[masch] = self.readContent(file)
                    break


    def readContent(self, file):
        """
        Reads the first line of a file from a network share.
        Args:
            file (str): The name of the file to read.
        Returns:
            str: The first line of the file, stripped of leading and trailing whitespace.
            None: If the file is not found.
        Raises:
            FileNotFoundError: If the file does not exist.
        """
        path = os.path.join(os.getenv("INSTALL_HELPER_PATH"), file)
        try:
            with self.networkShare.openFileRegisterSession(path, "r") as file:
                firstLine = file.readline().strip()
                return firstLine
        except FileNotFoundError as e:
            print(e)
            return None