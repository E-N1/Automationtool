import re
import os
import time
from Configurations.networkshare import NetworkShare
from Configurations.read_fault import ReadFault

class ReadCountedTestcase:
    def __init__(self):
        # Configurations
        self.networkShare = NetworkShare()
        self.readFault = ReadFault()
        
        
        # Fault-list
    def getCountTests(self, masch):
        """
        Retrieves the count of tests from the system log file on a specified machine.
        Args:
            masch (str): The machine name or IP address where the system log file is located.
        Returns:
            str: The count of tests as a string if found, otherwise None.
        Raises:
            FileNotFoundError: If the system log file is not found after all retry attempts.
            IOError: If there is an I/O error accessing the system log file after all retry attempts.
            Exception: For any other exceptions encountered during the process.
        Notes:
            - The method attempts to read the system log file up to 5 times with a delay of 10 seconds between attempts.
            - The system log file is expected to contain a line with the format "Testanzahl:'<count>'".
        """
        try:
            systemLogPath = os.getenv("MACHINE_SYSTEMLOG_PATH")

            retry_attempts = 5
            retry_delay = 10  # in seconds

            for attempt in range(retry_attempts):
                try:
                    with self.networkShare.openFileVMUser(systemLogPath,masch, 'r') as file:
                        for line in file:
                            match = re.search(r"Testanzahl:'([^']*)'",line)
                            if match:
                                testanzahl = match.group(1)
                                return testanzahl
                except FileNotFoundError as fnf_error:
                    if attempt == 4+1:
                        print(f"Attempt {attempt + 1} failed: FileNotFoundError: {fnf_error}")
                except IOError as io_error:
                    if attempt == 4+1:
                        print(f"Attempt {attempt + 1} failed: IOError: {io_error}")
                except Exception as e:
                    if attempt == 4+1:
                        print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay)

        except Exception as e:
            print(e)

    def getEachStartingTests(self, masch, category):
        """
        Counts the number of occurrences of "Start TF:" in the "uebersicht.txt" file located in the specified category 
        for a given machine.
        Args:
            masch (str): The machine identifier.
            category (str): The category directory containing the "uebersicht.txt" file.
        Returns:
            int: The count of "Start TF:" occurrences in the file.
        Raises:
            FileNotFoundError: If the file is not found after the specified retry attempts.
            IOError: If an I/O error occurs after the specified retry attempts.
            Exception: For any other exceptions that occur after the specified retry attempts.
        """
        try:

            # Each uebersicht.txt from parameter category
            overviewPath = os.path.join(self.readFault.getVersionPath(masch), category, "uebersicht.txt")
            # for reading each Start TF in Kategorie/uebersicht.txt
            counter = 0

            retry_attempts = 5
            retry_delay = 10  # in seconds

            for attempt in range(retry_attempts):
                try:
                    with self.networkShare.openFileVMUser(overviewPath,masch, 'r') as file:
                        for line in file:
                            match = re.search(r"Start TF:",line)
                            match
                            if match:
                                counter += 1
                        return counter
                except FileNotFoundError as fnf_error:
                    if attempt == 4+1:
                        print(f"Attempt {attempt + 1} failed: FileNotFoundError: {fnf_error}")
                except IOError as io_error:
                    if attempt == 4+1:
                        print(f"Attempt {attempt + 1} failed: IOError: {io_error}")
                except Exception as e:
                    if attempt == 4+1:
                        print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay)
        except Exception as e:
            print(e)

    def extractLastTestcaseNumber(self, file_path,masch, maxNumberFromJson):
        """
        Extracts the last testcase number from a file based on a specific pattern.
        Args:
            file_path (str): The path to the file from which to extract the testcase number.
            masch (str): The machine identifier used for accessing the network share.
            maxNumberFromJson (int): The maximum number from JSON to be used in the pattern.
        Returns:
            int: The last testcase number found in the file. Returns 0 if the file does not exist,
                 if no matching testcase is found, or if there is an error reading the file.
        Raises:
            FileNotFoundError: If the file is not found.
            IOError: If there is an error reading the file.
        Notes:
            The function looks for lines matching the pattern 'Start TF: .+ (X von Y)' where Y is
            the maxNumberFromJson. It extracts the first number (X) in the parentheses and returns
            the highest number found.
        """
        # Pattern that only considers 'Start TF' and '(X of Y)'.
        pattern = re.compile(r'Start TF: .+ \((\d+) von {}\)'.format(maxNumberFromJson))
        last_number = None
        if not os.path.exists(file_path):
            # Return 0 here if no suitable test case was found
            return 0
        try:
            with self.networkShare.openFileVMUser(file_path,masch, 'r') as file:
                for line in file:
                    match = pattern.search(line)
                    if match:
                        # Extract the first number in the parentheses
                        first_number = int(match.group(1))
                        if last_number is None or first_number > last_number:
                            last_number = first_number

            if last_number is not None:
                return last_number
            else:
                print("No matching test cases found.")
                return 0  # Return 0 here if no suitable test case was found

        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return 0
        except IOError as e:
            print(f"Error reading the file: {e}")
            return 0

    def allTestCasesCompleted(self, masch, overview_path, tcNumberReadOut):
        """
        Check if all test cases are completed for the given category by comparing the last number.
        """
        last_testcase_number = self.extractLastTestcaseNumber(overview_path, masch, tcNumberReadOut)

        if last_testcase_number == tcNumberReadOut:
            return True
        else:
            print(
                f"Not all test cases completed: last test case ({last_testcase_number}) is not equal to {tcNumberReadOut}.")
            return False
