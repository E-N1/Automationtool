import os
import re

from Configurations.networkshare import NetworkShare

class ReadCategories():

    def __init__(self):
        self.categories = {}
        

        self.networkShare = NetworkShare()

    def getCategories(self, masch, modul):
        """
        Retrieves and processes categories from a specified module on a network share.
        Args:
            masch (str): The machine name or network path.
            modul (str): The module name to search for.
        Returns:
            None
        This method searches for a directory matching the given module name within a base path on the specified machine.
        If a matching directory is found, it attempts to open a  file within that directory.
        It then reads through the file to find and process category information, storing the results in the `self.categories` dictionary.
        If the module is not found or an error occurs while opening the file, appropriate messages are printed.
        Raises:
            Exception: If there is an error opening the file on the network share.
        """
        basepath = os.getenv("MACHINE_SOURCE_PATH")
        pattern = modul.lower()

        matched_dir = None
        for entry in os.listdir(basepath):
            if pattern in entry.lower():
                matched_dir = entry
                break
        
        if not matched_dir:
            print(f"Modul {modul} nicht gefunden.")
            return

        fullPath = os.path.join(basepath, matched_dir, "Test", )
        try:
            with self.networkShare.openFileVMUser(fullPath,masch, "r") as file:
                for line in file:
                    if "'public Kategorie:    Kategorie" in line:
                        continue

                    elif "public Kategorie:    Kategorie" in line:
                        category_match = re.search(r'Kategorie\s*=\s*"(.*?)"', line)
                        if category_match:
                            categories = category_match.group(1).split(',')
                            formatted_categories = []
                            for cat in categories:
                                cat = cat.strip()
                                if cat.startswith("Kategorie_"):
                                    formatted_categories.append(cat)
                                else:
                                    formatted_categories.append(f"Kategorie_{cat}")
                            
                            if masch not in self.categories:
                                self.categories[masch] = {}
                            self.categories[masch][modul] = formatted_categories

                        return
        except Exception as e:
            print(f"Fehler beim Öffnen der Kategorie: {e}")
            return