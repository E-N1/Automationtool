#This data was converted to an .exe(see in Resources/run_exe_in_network.exe), it should not delete.
import os
import subprocess
class RunExecution():


    def startInstallerExe(self):
        """
        Executes the installer executable located on the network path.

        This method runs the installer executable found at the specified
        network location using the subprocess module.

        Returns:
            None
        """
        subprocess.run([os.getenv("INSTALL_HELPER_PATH")])
        return

if __name__ == "__main__":
    run = RunExecution()
    run.startInstallerExe()