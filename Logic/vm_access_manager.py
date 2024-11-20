from typing import Literal

class VMAccessManager():

    def __init__(self):
        self.machineList = {}

    def getStatus(self, machine):
        """
        Retrieve the status of a specified machine.

        Args:
            machine (str): The identifier of the machine whose status is to be retrieved.

        Returns:
            str: The status of the specified machine, or None if the machine is not found.
        """
        return self.machineList.get(machine)
    

    def setStatus(self, machine: str, status: Literal["Offline", "Online", "Error", "Running"]):
        """
        Sets the status of a specified machine.

        Args:
            machine (str): The name or identifier of the machine.
            status (Literal["Offline", "Online", "Error", "Running"]): The status to set for the machine.

        Returns:
            None
        """
        self.machineList[machine] = status
        print(f"setStatus {machine} - {status}")


    def delMachine(self, machine):
        """
        Deletes a virtual machine from the machine list.

        Args:
            machine (str): The name or identifier of the machine to be deleted.

        Prints:
            str: A message indicating that the machine has been deleted in the StatusWorkerLoop.
        """
        print(machine+" deleted in the StatusWorkerLoop") 
        del self.machineList[machine]