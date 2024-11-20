import os
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QMessageBox
import paramiko
from scp import SCPClient
from paramiko import client as c
from Configurations.networkshare import NetworkShare
class RunTestExecution(QObject):
    def __init__(self):
        super().__init__()
        self.networkShare = NetworkShare()
        self.activCheckDataPath = "./Resources/ActivCheckData.txt"
        self.vmPathDirectory = os.getenv("MACHINE_PATH")
        self.activCheckData = "ActivCheckData.txt"


    def uploadActivCheckData(self, client):
        command = f'if (Test-Path "{self.vmPathDirectory}\\{self.activCheckData}")' + r' {{"True"}} else {{"False"}}'
        stdin, stdout, stderr = client.exec_command(f'powershell -Command {command}')
        result = stdout.read().decode().strip()
        if result == "False":
            with SCPClient(client.get_transport()) as scp:
                scp.put(self.activCheckDataPath, self.vmPathDirectory)


    def unCommentModul(self, masch, modules):
        """
        This method modifies a VBScript file on a remote machine by commenting out all `RunTest` lines 
        and uncommenting specific module lines provided in the `modules` list.
        Args:
            masch (str): The name or IP address of the remote machine.
            modules (list): A list of module names to be uncommented in the VBScript file.
        Raises:
            FileNotFoundError: If the specified VBScript file is not found on the remote machine.
            Exception: For any other exceptions that occur during file processing.
        Steps:
            1. Reads the content of the VBScript file from the remote machine.
            2. Comments out all lines containing `RunTest`.
            3. Uncomments lines corresponding to the modules specified in the `modules` list.
            4. Writes the modified content back to the VBScript file on the remote machine.
        """
        path = os.getenv("MACHINE_VBS_SCRIPT_PATH")

        try:
            with self.networkShare.openFileVMUser(path,masch, 'r') as file:
                lines = file.readlines()

            # Schritt 1: Alle `RunTest`-Zeilen auskommentieren
            processed_lines = self.comment_all_runtest_lines(lines)

            # Schritt 2: Die Module aus der Liste einkommentieren
            for module in modules:
                processed_lines = self.uncomment_module_lines(masch,processed_lines, module)

            # Optional: Speichern der bearbeiteten Zeilen in der Datei
            with self.networkShare.openFileVMUser(path,masch, 'w') as output_file:
                output_file.writelines(processed_lines)

        except FileNotFoundError:
            print(f"The file {path} was not found.")
        except Exception as e:
            print(f"An error has occurred: {e}")


    def comment_all_runtest_lines(self, lines):
        """
        Comments out all lines containing 'RunTest "C:\\' in the provided list of lines.

        This function iterates through the given list of lines and comments out any line
        that contains the substring 'RunTest "C:\\' and does not already start with a comment.
        The comment is added by prefixing the line with a single quote.

        Args:
            lines (list of str): The list of lines to process.

        Returns:
            list of str: A new list of lines with the specified lines commented out.
        """
        # Alle `RunTest`-Zeilen auskommentieren
        return [f"'{line}" if 'RunTest "C:\\' in line and not line.strip().startswith("'") else line for line in lines]


    def uncomment_module_lines(self, masch, lines, module):
        """
        Uncomments lines in the provided list that contain a specific module path.
        This method searches for lines that contain the specified module path and removes
        the comment character (') if the line is commented out. If the line is not commented,
        it remains unchanged.
        Args:
            masch: An object representing the machine or context in which this method is called.
            lines (list of str): A list of lines (strings) to be processed.
            module (str): The name of the module to search for in the lines.
        Returns:
            list of str: A list of processed lines with the specified module path uncommented.
        Raises:
            Exception: If an error occurs during processing, it logs the error and raises an exception.
        """
        # Zeilen suchen, die das spezifische Modul enthalten, und auskommentieren
        target_line_pattern = f'RunTest {os.getenv("MACHINE_RUNTEST_PATH")}'

        # Neue Liste, um die bearbeiteten Zeilen zu halten
        processed_lines = []
        try:

            for line in lines:
                if target_line_pattern in line:
                    # Falls die Zeile auskommentiert ist, entfernen Sie das Kommentarzeichen
                    if line.strip().startswith("'"):
                        processed_lines.append(line.replace("'", "", 1))
                    else:
                        processed_lines.append(line)
                else:
                    processed_lines.append(line)

            return processed_lines
        except Exception as e:
            self.warningWindow(masch,e)
            print(f"Ein Fehler ist aufgetreten: {e}")


    def startTest(self, masch, module):
        """
        Initiates the test execution process on a remote machine.
        This method performs the following steps:
        1. Uncomments the specified module in the configuration.
        2. Establishes an SSH connection to the remote machine.
        3. Uploads necessary data for the activation check.
        4. Creates and runs a scheduled task to start the Java test execution.
        5. Displays an information window upon successful initiation.
        6. Handles any exceptions by displaying a warning window and printing the error.
        Args:
            masch (str): The hostname or IP address of the remote machine.
            module (str): The module to be uncommented in the configuration.
        Raises:
            Exception: If there is an error during the SSH connection or command execution.
        """
        # Alle Module in qtp_allg auskommentieren und dann alle gesetzten Module auskommentieren.
        self.unCommentModul(masch,module)


        client = c.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(masch, port=22, username=self.networkShare.usernameVM, password=self.networkShare.passwordVM, look_for_keys=False)
            self.uploadActivCheckData(client)

            taskName = "startJavaTestsExecution"
            pathToFile = os.getenv("MACHINE_STARTTEST_PATH")
            command = f'schtasks /create /tn {taskName} /tr "{pathToFile}" /sc once /st 00:00 /rl HIGHEST /f'
            stdin, stdout, stderr = client.exec_command(command)
            stdout.channel.recv_exit_status()
            runCommand = f'schtasks /run /tn {taskName}'
            stdin, stdout, stderr = client.exec_command(runCommand)
            stdout.channel.recv_exit_status()
            self.informationWindow(masch)
            print(f"Tests für {masch} wurden angestoßen!")

        except Exception as e:
            self.warningWindow(masch, str(e))
            print(e)

        client.close()


    def warningWindow(self, vm, message):
        """ shows a warning window with a message """
        return QMessageBox.information(None, "Warnung", "Ein Fehler ist bei " + vm + " aufgetreten: " + message)
    

    def informationWindow(self, vm):
        """ shows an information window with a message """
        return QMessageBox.information(None, "Information", vm + "-Test's wurden angestoßen!\nTestergebnisse sind bald sichtbar.")