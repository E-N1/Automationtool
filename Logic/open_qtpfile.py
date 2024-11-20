import smbclient
import subprocess
import tempfile
import os

from Configurations.networkshare import NetworkShare

class OpenQTPFile():
    def __init__(self):
        self.notepadPath = r"C:\Windows\System32\notepad.exe"

        self.networkShare = NetworkShare()

    def openWithNotepad(self, filePath):
        """
        Opens a file from a network share with Notepad.

        This method reads the content of a file from a network share using SMB protocol,
        writes it to a temporary file, opens the temporary file with Notepad, and then
        deletes the temporary file after Notepad is closed.

        Args:
            filePath (str): The path to the file on the network share.

        Raises:
            Exception: If an error occurs during file operations or subprocess execution.

        Notes:
            - The method checks if the provided filePath is a valid string.
            - It uses the smbclient library to read the file from the network share.
            - A temporary file is created to hold the content of the remote file.
            - The temporary file is opened with Notepad.
            - The temporary file is deleted after Notepad is closed.
        """
        if not isinstance(filePath, str) or not filePath: 
            print(f"Invalid file path: {filePath}")
            return

        try:
            smbclient.ClientConfig(username=self.networkShare.usernameVM, password=self.networkShare.passwordVM)
            with smbclient.open_file(filePath, mode='r') as remote_file:
                content = remote_file.read()  

            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode='w', encoding='utf-8') as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name

            # Output the path of the temporary file
            print(f"Temporäre Datei erstellt: {temp_file_path}")

            # Open the temporary file with Notepad
            subprocess.run([self.notepadPath, temp_file_path], check=True)

            # Delete the temporary file after closing Notepad
            os.remove(temp_file_path)
            print(f"Temporäre Datei gelöscht: {temp_file_path}")
        except Exception as e:
            print(f"Ein Fehler ist aufgetreten: {e}")
