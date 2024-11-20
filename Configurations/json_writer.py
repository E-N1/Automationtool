import json
import os

class JsonWriter:

    def __init__(self):
        self.data = "durchlaufen.json"
        self.hostname = "hostname"
        self.timestamp = "timestamp"
        self.dd = "dd"
        self.mm = "mm"
        self.yyyy = "yyyy"
        self.modulEntry = "modul-entry"
        if not os.path.exists(self.data):
            with open(self.data, 'w') as json_file:
                json.dump([], json_file)

    def loadData(self):
        """
        Loads data from a JSON file specified by `self.data`.
        This method checks if the file exists. If it does not, it creates an empty file.
        It then attempts to read and parse the JSON data from the file. If the file is
        corrupted or contains invalid JSON, it prints a warning message and returns an
        empty list. If any other exceptions occur during file access, it prints an error
        message and returns the error message as a string.
        Returns:
            list or str: The parsed JSON data as a list if successful, an empty list if
            the JSON is corrupted, or an error message string if an exception occurs.
        """

        try:
            # Check if file exists
            if not os.path.exists(self.data):
                # Create the file if it doesn't exist
                with open(self.data, "w") as file:
                    pass

            # Open the file and load data
            with open(self.data, "r") as file:
                try:
                    data = json.load(file)
                    return data
                except json.decoder.JSONDecodeError:
                    # Handle corrupt file scenario (optional: log error, clear the file)
                    print("Warning: Corrupted JSON file found. Consider clearing the file.")
                    return []  # Return an empty list

        except Exception as e:
            # Handle other file-related errors
            errorMessage = f"Error accessing JSON file: Reason - {e}"
            print(errorMessage)
            return errorMessage


    def getNumbersOfEntries(self):
        """
        Reads a JSON file and returns the number of entries.
        This method loads data from a JSON file specified by `self.data`,
        counts the number of entries in the JSON object, and returns the count.
        Returns:
            int: The number of entries in the JSON file.
        """
        self.loadData()

        with open(self.data, 'r') as f:
            data = json.load(f)

        # Count the number of entries
        countedNumber = len(data)

        return countedNumber


    def writeEntry(self, machineName, data):
        """
        Writes an entry to a JSON file. If the file does not exist, it creates and initializes it.
        Args:
            machineName (str): The name of the machine to be used as a key in the JSON entry.
            data (dict): The data to be written as the value associated with the machineName key.
        Raises:
            Exception: If there is an error writing to the JSON file.
        Example:
            writeEntry("Machine1", {"key": "value"})
        """
        try:
            if not os.path.exists(self.data):
                with open(self.data, 'w') as json_file:
                    json.dump([], json_file)

            with open(self.data, 'r+') as json_file:
                try:
                    currentData = json.load(json_file)
                except json.JSONDecodeError:
                    currentData = []

                currentData.append({machineName: data})

                # Overwrite file from the beginning
                json_file.seek(0)
                json.dump(currentData, json_file, indent=4)


                print(f"Successfully wrote entry to {self.data}")
        except Exception as e:
            print(f"Error writing to JSON file: {e}")

