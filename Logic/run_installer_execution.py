import os
import paramiko
from paramiko import client as c
from Configurations.networkshare import NetworkShare
from scp import SCPClient
class RunInstallerExecution():

    def __init__(self):
        self.networkShare = NetworkShare()
        self.exePath = "./Resources/run_exe_in_network.exe"
        self.vmPathDirectory = os.getenv("MACHINE_PATH")
        self.filePath = fr"run_exe_in_network.exe"


    def uploadExecution(self,client):
        """
        Uploads an executable file to a remote virtual machine if it does not already exist.

        Args:
            client (paramiko.SSHClient): The SSH client connected to the remote virtual machine.

        Raises:
            SCPException: If there is an error during the SCP file transfer.
        """
        command = f'if (Test-Path "{self.vmPathDirectory}\\{self.filePath}")' + r' {{"True"}} else {{"False"}}'
        stdin, stdout, stderr = client.exec_command(f'powershell -Command {command}')
        result = stdout.read().decode().strip()
        if result == "False":
            with SCPClient(client.get_transport()) as scp:
                scp.put(self.exePath, self.vmPathDirectory)



    def runExecution(self, vm):
        """
        Executes a remote command on a virtual machine (VM) to create and run a scheduled task.
        This method connects to a VM via SSH, uploads an executable file, creates a scheduled task to run the executable,
        and then immediately runs the scheduled task.
        Args:
            vm (str): The IP address or hostname of the virtual machine.
        Raises:
            Exception: If there is an error during the execution of the commands on the remote host.
        """
        client = c.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(vm, port = 22 , username = self.networkShare.usernameVM, password=self.networkShare.passwordVM,look_for_keys=False)
        self.uploadExecution(client)
        try:

            # Befehl zum Erstellen einer geplanten Aufgabe, die die exe-Datei ausführt
            taskName = "runExecutionInNetwork"
            pathToFile = os.getenv("EXE_IN_NETWORK")
            command = f'schtasks /create /tn {taskName} /tr "{pathToFile}" /sc once /st 00:00 /rl HIGHEST /f'
            print(command)
            print(f"Creating scheduled task with command: {command}")

            # Befehl zum Erstellen der geplanten Aufgabe auf dem Remote-Host ausführen
            stdin, stdout, stderr = client.exec_command(command)
            stdout.channel.recv_exit_status()  # Warten, bis der Befehl abgeschlossen ist


            # Befehl zum sofortigen Ausführen der geplanten Aufgabe
            runCommand = f'schtasks /run /tn {taskName}'
            print(f"Running scheduled task with command: {runCommand}")
            stdin, stdout, stderr = client.exec_command(runCommand)
            stdout.channel.recv_exit_status()  # Warten, bis der Befehl abgeschlossen ist

            
        except Exception as e:
            print(e)
        client.close()