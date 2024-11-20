import os

from Configurations.machines import Machines


class DriveChecker:
    def __init__(self):
        self.machines = Machines()
        self.drive = self.machines.getMachineDrive()

    def checkAllDrives(self):
        """
        Checks the connection status of all drives.
        Iterates through the list of drives and checks if each drive is connected.
        Returns two lists: one containing the connected drives and the other containing the not connected drives.
        Returns:
            tuple: A tuple containing two lists:
            - connected (list): A list of drives that are connected.
            - notConnected (list): A list of drives that are not connected.
        """
        notConnected = []
        connected = []

        for drive in self.drive:
            if self.isDriveConnected(drive):
                connected.append(drive)
            else:
                notConnected.append(drive)

        return connected, notConnected

    @staticmethod
    def isDriveConnected(drive):
        """
        Check if a drive is connected.

        Args:
            drive (str): The path to the drive to check.

        Returns:
            bool: True if the drive is connected (i.e., the path is a directory), False otherwise.
        """
        return os.path.isdir(drive)