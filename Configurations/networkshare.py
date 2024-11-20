import os
import subprocess
import time
import smbclient
from smbprotocol.exceptions import SMBAuthenticationError, SMBException

from Logic.vm_access_manager import VMAccessManager

class NetworkShare():
    def __init__(self):
        self.vmAccessManager = VMAccessManager()
        # Drive letter for the network share
        self.usernameNetwork = os.getenv("NETWORK_USERNAME")
        self.passwordNetwork = os.getenv("Network_PASSWORD")

        # VM-Data
        self.usernameVM = os.getenv("VIRTUAL_MACHINE_NAME") 
        self.passwordVM = os.getenv("VIRTUAL_MACHINE_PASSWORD")
        self.maschLogin = {}
        self.netDrive = os.getenv("NET_DRIVE")
        self.retry_attemptsListOfVMs = {}

    def openFileVMUser(self, filepath, machine, mode):
        """
        Attempts to open a file on a virtual machine using SMB protocol with retry logic.
        Parameters:
        filepath (str): The path to the file to be opened.
        machine (str): The identifier of the virtual machine.
        mode (str): The mode in which to open the file (e.g., 'r' for read, 'w' for write).
        Returns:
        file: The file object if the file is successfully opened, None otherwise.
        Exceptions:
        SMBAuthenticationError: Raised if there is an authentication error.
        SMBException: Raised for other SMB-related errors.
        Exception: Raised for any other exceptions.
        Notes:
        - The function will retry opening the file up to `max_retry` times with exponential backoff.
        - If the virtual machine is offline, the function will print a message and return None.
        - If the file is being used by another process, the function will retry opening the file.
        - The retry attempts are recorded in `self.retry_attemptsListOfVMs`.
        """
        max_retry = 10
        wait_time = 1  # in seconds
        
        if self.vmAccessManager.getStatus(machine) == "Offline":
            print(f"VM {machine} is offline.")
            return None

        for attempt in range(max_retry):
            try:
                smbclient.ClientConfig(username=self.usernameVM, password=self.passwordVM)
                file = smbclient.open_file(filepath, mode=mode)
                self.retry_attemptsListOfVMs[filepath] = attempt
                return file
            
            except SMBAuthenticationError:
                print(f"Failed to open file - SMBAuthenticationError {filepath}: Authentication error.")
                print(f"{filepath} not accessible. Password or username may be incorrect.")
                break  

            except SMBException as e:
                print(f"Failed to open file - SMBException {filepath}: {e}")
                if "used by another process" in str(e):
                    print(f"{filepath} being used by another process. Retrying...")
                else:
                    break

            except Exception as e:
                print(f"Failed to open file - Exception {filepath}: {e}")
                if "used by another process" in str(e):
                    print(f"{filepath} being used by another process. Retrying...")
                else:
                    break

            # Wait: exponential backoff
            time.sleep(wait_time)
            wait_time *= 2  # double the wait time for each retry

    def openFileNetworkUser(self, filepath, mode):
        """
        Opens a file on a network share using the provided network user credentials.

        Args:
            filepath (str): The path to the file on the network share.
            mode (str): The mode in which to open the file (e.g., 'r' for read, 'w' for write).

        Returns:
            file object: A file object corresponding to the opened file.

        Raises:
            Exception: If there is an error opening the file, an exception is raised with an error message.
        """
        try:
            smbclient.ClientConfig(username=self.usernameNetwork, password=self.passwordNetwork)
            return smbclient.open_file(filepath, mode=mode)
        except Exception as e:
            print(f"Failed to open file {filepath}: {e}")
        

    def openFileRegisterSession(self, filepath, mode):
        """
        Opens a file on a network share using SMB protocol and returns the file object.
        This method configures the SMB client with the provided network credentials and 
        opens the specified file in the given mode.
        Args:
            filepath (str): The path to the file on the network share.
            mode (str): The mode in which to open the file (e.g., 'r' for read, 'w' for write).
        Returns:
            file object: The file object corresponding to the opened file.
        Raises:
            SMBException: If there is an error opening the file.
        """
        smbclient.ClientConfig(username=self.usernameNetwork, password=self.passwordNetwork)
        return smbclient.open_file(filepath, mode=mode)


    def checkExistingConnection(self):
        """
        Checks whether a connection to a net_drive already exists.
        """
        try:
            result = subprocess.run(["net", "use"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                existingConnections = result.stdout.decode()
                return self.netDrive.lower() in existingConnections.lower()
            return False
        except Exception as e:
            print(f"Error when checking the existing connections: {e}")
            return False
        

    def connectToNetworkDrive(self,remotePath, retries=3):
        """
        Versucht eine Verbindung zu einem Netzwerkpfad (net_drive) herzustellen, mit mehreren Versuchen.
        """
        if self.checkExistingConnection():
            print(f"Connection to {self.netDrive} already exists.")
            return True


        for attempt in range(retries):
            try:
                result = subprocess.run(["net", "use", self.netDrive, remotePath, "/USER:" + self.usernameNetwork, self.passwordNetwork],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if result.returncode == 0:
                    return True
                else:
                    print(f"Verbindungsversuch {attempt + 1} fehlgeschlagen: {result.stderr.decode()}")
            except Exception as e:
                print(f"Fehler beim Verbinden: {e}")
            time.sleep(1)
        return False
    

    def disconnectNetworkDrive(self):
        """
        Disconnects the network drive specified by `self.netDrive`.

        This method attempts to disconnect the network drive using the `net use` command.
        If an error occurs during the disconnection process, it catches the exception and
        prints an error message.

        Raises:
            Exception: If there is an error during the disconnection process.
        """
        try:
            subprocess.run(["net", "use", self.netDrive, "/delete"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            print(f"Error when disconnecting the network drive connection: {e}")

