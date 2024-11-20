import re
import os
import pyodbc
import glob
import json

from PyQt5.QtWidgets import QMessageBox

from Configurations.machines import Machines
from Configurations.networkshare import NetworkShare
from Configurations.read_fault import ReadFault


class AccessDBReader:

    def __init__(self):
        # Configurations
        self.networkShare = NetworkShare()
        self.readFault = ReadFault()
        self.module = os.getenv("MODULE")
        self.machines = Machines()


    def extract_number_from_folder_name(self,category):
        """
        Use regular expression to extract the first number found from the folder name.
        """
        numbers = [int(s) for s in re.findall(r'\d+', category)]
        if numbers:
            return numbers[0]  # Returns only the first number found
        else:
            raise ValueError("No number found in category name")


    def extractSecondDigitfromNumber(self,number):
        """
        Pulls from the database, table, the Sp
        """
        if isinstance(number, str) and number.startswith("Kategorie_"):
            match = re.search(r'\d+', number)
            if match:
                number_str = match.group()
                return number_str
            else:
                raise ValueError("No digit found in the input.")
            

    def getMDBDataFromFolder(self,dbPath):
        """
        Retrieves the path of a single .mdb file from the specified folder.
        Args:
            dbPath (str): The path to the directory where .mdb files are located.
        Returns:
            str: The path to the .mdb file if exactly one .mdb file is found.
        Raises:
            FileNotFoundError: If no .mdb files are found in the directory.
            FileExistsError: If more than one .mdb file is found in the directory.
        """

        # glob to search for all .mdb files in the directory
        mdb_dateien = glob.glob(os.path.join(dbPath, '*.mdb'))

        if len(mdb_dateien) == 1:
            # There is exactly one .mdb file
            return mdb_dateien[0]
        elif len(mdb_dateien) == 0:
            raise FileNotFoundError("No .mdb file found in the directory")
        else:
            raise FileExistsError("More than one .mdb file exists in the directory")



    def fetchAllCategoriesFromDB(self,path,modul):

        # Removed for security reasons
       
        return 
        
    def ensure_directory_exists(self,file_path):
        """
        Ensures that the directory for the specified file exists.

        :param file_path: The full path to the file.
        """
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)


    def setDBDataInJson(self, masch):
        """
        Reads the test cases per category from the database and writes them to a JSON file.
        """
        versionDate = self.readFault.getCurrentVersionMachine(masch, versionDateOption=True)
        all_successful = True  # Variable to track if all modules were processed successfully

        for modul in self.module:
            dbTemplatePath = os.getenv("DB_PATH") + rf"\{modul}\{versionDate}\Testdaten"
            print(dbTemplatePath)
            # Searches for the .mdb/accesDB in the test data folder
            dbPath = self.getMDBDataFromFolder(dbTemplatePath)

            try:
                results, total_count = self.fetchAllCategoriesFromDB(dbPath, modul)

                # Daten in JSON-Datei schreiben
                json_data = {
                    "TestfaelleJeKategorien": results,
                    "GesamtTF": total_count
                }

                json_file_name = os.path.join("./Resources/Eintraege_Datenbank", f"{modul}.json")

                with open(json_file_name, 'w', encoding='utf-8') as json_file:
                    json.dump(json_data, json_file, ensure_ascii=False, indent=4)
                print(f"JSON file successfully created: {json_file_name}")
            except (ValueError, FileNotFoundError, FileExistsError, pyodbc.Error) as e:
                print(f"Error when processing the module {modul}: {e}")
                all_successful = False  # Mark as unsuccessful if any exception occurs

        if all_successful:
            self.informationWindow()
        else:
            QMessageBox.warning(None, "Warnung", "Einige Module konnten nicht erfolgreich verarbeitet werden.")


    def informationWindow(self):
        """
        Displays an information message box indicating that the database contents have been updated.

        Returns:
            QMessageBox.StandardButton: The button that was clicked to dismiss the message box.
        """
        return QMessageBox.information(None, "Information", "Datenbank Inhalte wurden aktualisiert.")
    