import os
import re
import json
import time
from Configurations.networkshare import NetworkShare
from Configurations.read_fault import ReadFault

class TestCaseAnalyzer:

    def __init__(self):
        self.networkShare = NetworkShare()
        self.readFault = ReadFault()

    def get_each_starting_tests(self, masch, category,countedTCNumbergetByJson):
        """
        Retrieves the number of starting tests and total tests from a specified overview file.
        Args:
            masch (str): The machine identifier.
            category (str): The category of the tests.
            countedTCNumbergetByJson (int): The total number of test cases as obtained from JSON.
        Returns:
            tuple: A tuple containing the number of starting tests and total tests.
                   Returns (None, None) if the file is not found or an error occurs.
        Raises:
            FileNotFoundError: If the overview file is not found after all retry attempts.
            IOError: If an I/O error occurs after all retry attempts.
            Exception: If any other exception occurs after all retry attempts.
        """
        try:
            overview_path = os.path.join(self.readFault.getVersionPath(masch), category, "uebersicht.txt")
            retry_attempts = 5
            retry_delay = 10  # in seconds

            for attempt in range(retry_attempts):
                try:
                    with self.networkShare.openFileVMUser(overview_path, masch,'r') as file:
                        for line in file:
                            match = re.search(rf"Start TF:.*?\((\d+) von ({countedTCNumbergetByJson})\)", line)
                            if match:
                                starting_tests = int(match.group(1))
                                total_tests = int(match.group(2))
                                print(f"Starting Tests: {starting_tests}, Total Tests: {total_tests}")
                                return starting_tests, total_tests
                except FileNotFoundError as fnf_error:
                    if attempt == (retry_attempts - 1):
                        print(f"Attempt {attempt + 1} failed: FileNotFoundError: {fnf_error}")
                except IOError as io_error:
                    if attempt == (retry_attempts - 1):
                        print(f"Attempt {attempt + 1} failed: IOError: {io_error}")
                except Exception as e:
                    if attempt == (retry_attempts - 1):
                        print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay)
        except Exception as e:
            print(e)
        return None, None


    def extractDataFromJson(self, json_path):
        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
        

    def getJsonFile(self, pattern):
        """
        Sucht im angegebenen Verzeichnis nach einer JSON-Datei, deren Name dem gegebenen Muster 'ähnlich' ist.

        :param dir_path: Der Pfad des Verzeichnisses, in dem gesucht werden soll.
        :param pattern: Das Suchmuster als String.
        :return: Der Pfad zur gefundenen Datei oder None, wenn keine ähnliche Datei gefunden wurde.
        """
        try:
            # Kompilieren des regulären Ausdrucks aus dem Muster, um eine flexible Suche zu ermöglichen
            regex = re.compile(pattern, re.IGNORECASE)

            path = "./Resources/Eintraege_Datenbank"

            # Durchsuchen der Dateien im Verzeichnis
            for file_name in os.listdir(path):
                # Überprüfen, ob die Datei eine JSON-Datei ist
                if file_name.endswith(".json"):
                    # Überprüfen, ob der Dateiname auf das Muster passt
                    if regex.search(file_name):
                        # Rückgabe des kompletten Pfades zur gefundenen Datei
                        return os.path.join(path, file_name)
            return None
        except Exception as e:
            print(e)
            return None


    def getTestCaseNumberCategory(self,jsonPattern, category):
        """
        Extrahiert die Anzahl der Testfälle für die angegebenen Kategorien aus einer JSON-Datei.

        :param json_path: Pfad zur JSON-Datei.
        :param categories: Liste der Kategorienamen, für die die Testfalldaten extrahiert werden sollen.
        :return: Ein Dictionary mit den Kategorienamen als Schlüssel und der Anzahl der Testfälle als Werte.
        """
        try:
            with open(self.getJsonFile(jsonPattern), 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            test_cases = data.get("TestfaelleJeKategorien", [])
            

            for entry in test_cases:
                if category in entry:
                    return entry[category]
            
            return 0

        except Exception as e:
            print(f"Fehler beim Lesen der JSON-Datei: {e}")
            return 0
