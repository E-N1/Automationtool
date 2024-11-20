from PyQt5.QtCore import  pyqtSignal, QObject
from Logic.vm_access_manager import VMAccessManager
import time

class StatusWorker(QObject):
    update_status = pyqtSignal(str, str)

    def __init__(self, component):
        super().__init__()
        self.component = component
        self.vmAccessManager = VMAccessManager()
        self.running = True

    def run(self):
        """
        Continuously monitors the status of virtual machine components and updates their status.

        This method runs in a loop while the `running` attribute is True. It iterates over a copy of 
        the `vmComponentList` to check the status of each virtual machine component. If a component 
        is found to be "Offline", it is removed from the list. The status of each machine is retrieved 
        using the `getMachineStatusWithRetry` method, and the status is emitted using the `update_status` 
        signal.

        Raises:
            Exception: If there is an error retrieving the status of a machine.

        Side Effects:
            - Emits the `update_status` signal with the machine and its status.
            - Removes offline components from the `vmComponentList`.
            - Prints status updates and error messages to the console.
        """
        while self.running:
            for vmComponent in self.component.vmComponentList[:]:  # Iterate over a copy of the list
                if self.running:
                    machine = vmComponent.hostname[vmComponent.number]
                    try:
                        status = self.getMachineStatusWithRetry(machine)
                        self.update_status.emit(machine, status)
                        if status == "Offline":
                            self.component.vmComponentList.remove(vmComponent)
                            print(f"Removed {machine} from the list")
                    except Exception as e:
                        print(f"Failed to get status for {machine}: {e}")
            time.sleep(10)

    def stop(self):
        """ stops the worker """
        self.running = False
        print("worker closed")


    def getMachineStatusWithRetry(self, machine):
        """
        Attempts to retrieve the status of a machine with a specified number of retries.

        This method will try to get the machine status up to `retry_attempts` times, waiting 
        `retry_delay` seconds between each attempt. If the machine status is "black", it is 
        considered not accessible and will be marked as "Offline". If all attempts fail, the 
        machine will also be marked as "Offline".

        Args:
            machine (str): The identifier of the machine whose status is to be retrieved.

        Returns:
            str: The status of the machine. If the machine is not accessible or all attempts 
             fail, "Offline" is returned.
        """
        retry_attempts = 10
        retry_delay = 1  # in seconds

        for attempt in range(retry_attempts):
            try:
                status = self.component.getMachineStatus(machine)
                if status == "black":  # Assuming "black" means the machine is not accessible
                    self.vmAccessManager.setStatus(machine, "Offline")
                    return "Offline"
                return status
            except Exception as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < retry_attempts - 1:
                    time.sleep(retry_delay)
                else:
                    self.vmAccessManager.setStatus(machine, "Offline")
                    return "Offline"