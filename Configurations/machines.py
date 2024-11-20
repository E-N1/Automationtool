import os
import json
class Machine():
    def __init__(self, name, modules, path):
        self.name = name
        self.modules = modules
        self.path = path
        
    def to_dict(self):
        """
        Converts the machine configuration to a dictionary.

        Returns:
            dict: A dictionary containing the machine configuration with keys 'modul' and 'path'.
        """
        return {
            "modul": self.modules,
            "path": self.path
        }

class Machines:
    def __init__(self):
        self.filename = "machines.json"
        self.machines = []
        self.loadFromJson()


    def addMachine(self, name, modules, path):
        """
        Adds a new machine to the list of machines.

        Args:
            name (str): The name of the machine.
            modules (list): A list of modules associated with the machine.
            path (str): The file path where the machine configuration is stored.

        Returns:
            None
        """
        machine = Machine(name, modules, path)
        self.machines.append(machine)


    def saveToJson(self):
        """
        Saves the current state of machines to a JSON file.
        This method iterates over the list of machines, converts each machine
        to a dictionary using its `to_dict` method, and then writes the resulting
        dictionary to a JSON file specified by `self.filename`.
        Raises:
            IOError: If the file cannot be opened or written to.
        """
        data = {}
        for machine in self.machines:
            data[machine.name] = machine.to_dict()

        with open(self.filename, 'w') as file:
            json.dump(data, file, indent=4)


    def loadFromJson(self):
        """
        Loads machine configurations from a JSON file.
        If the specified JSON file does not exist, it creates the file by calling `saveToJson`.
        Reads the JSON file and adds machines using the `addMachine` method.
        Raises:
            JSONDecodeError: If the file contains invalid JSON.
        """
        if not os.path.isfile(self.filename):
            self.saveToJson()

        with open(self.filename, 'r') as file:
            data = json.load(file)
            for name, attributes in data.items():
                self.addMachine(name, attributes["modul"], attributes["path"])


    def getNumberOfMachines(self):
        """
        Returns the number of machines.

        This method calculates and returns the total number of machines
        currently stored in the `machines` attribute.

        Returns:
            int: The number of machines.
        """
        return len(self.machines)


    def getMachineNameOfAll(self):
        """
        Retrieves the names of all machines.

        Returns:
            list: A list containing the names of all machines.
        """
        return [machine.name for machine in self.machines]


    def getPathOfAll(self):
        """
        Retrieve the paths of all machines.

        Returns:
            list: A list containing the paths of all machines.
        """
        return [machine.path for machine in self.machines]


    def getModuleFromMachine(self, machineName):
        """
        Retrieve the modules associated with a given machine.

        Args:
            machineName (str): The name of the machine to search for.

        Returns:
            list: A list of modules associated with the specified machine. 
                  Returns an empty list if the machine is not found.
        """
        for machine in self.machines:
            if machine.name == machineName:
                return machine.modules
        return []


    def getMachinesName(self, numberMachine):
        """
        Retrieve the name of a machine based on its index.
        Args:
            numberMachine (int): The 1-based index of the machine.

        Returns:
            str: The name of the machine at the specified index.

        Raises:
            IndexError: If the index is out of range.
        """
        return self.machines[numberMachine - 1].name


    def getMachinePath(self, numberMachine):
        """
        Retrieves the path of a specified machine and converts backslashes.

        Args:
            numberMachine (int): The index of the machine (1-based).

        Returns:
            str: The converted path of the specified machine.
        """
        unconverted = self.machines[numberMachine - 1].path
        converted = unconverted.replace("\\", "\\")
        return converted


    def getMachineModul(self, numberMachine):
        """
        Retrieve the modules of a specific machine.

        Args:
            numberMachine (int): The index of the machine (1-based index).

        Returns:
            list: The modules of the specified machine.
        """
        return self.machines[numberMachine-1].modules
    

    def getLenMachineModules(self,numberMachine):
        """
        Get the number of modules for a specified machine.

        Args:
            numberMachine (int): The index of the machine (1-based index).

        Returns:
            int: The number of modules in the specified machine.
        """
        return len(self.machines[numberMachine - 1].modules)


    def changeMachinePathBasedOnModule(self, numberMachine, newModule):
        """
        Changes the path of a machine based on the specified module.
        This method updates the path of the machine at the given index by replacing the first module
        that starts with "qtp_" after the "Source" directory with the new module name provided.
        Args:
            numberMachine (int): The index of the machine (1-based index).
            newModule (str): The new module name to replace the existing one.
        Returns:
            str: The updated path of the machine, or None if the "Source" directory is not found in the path.
        Raises:
            IndexError: If the numberMachine is out of range of the machines list.
        """
        machine = self.machines[numberMachine - 1]
        parts = machine.path.split("\\")
        
        # Find the index of ‘Source’ (case insensitive)
        source_index = next((i for i, part in enumerate(parts) if part.lower() == "source"), None)
        
        if source_index is None:
            print(f"Error: 'Source' not found in the path: {machine.path}")
            return None

        # Change the first matching module
        for i in range(source_index + 1, len(parts)):
            if parts[i].startswith("qtp_"):
                parts[i] = newModule
                break

        temporaryPath = "\\".join(parts)

        self.machines[numberMachine - 1].path = temporaryPath
        return temporaryPath


    def getFirstMachineName(self):
        """
        Retrieve the name of the first machine in the list.

        Returns:
            str: The name of the first machine.
        """
        return self.machines[0].name


    def getMachineDrive(self):
        """
        Generates a list of network paths to the C drives of all machines.

        Returns:
            list: A list of strings, each representing the network path to the C drive of a machine.
        """
        path_template = os.getenv("MACHINE_PATH_TEMPLATE")
        if path_template is None:
            raise EnvironmentError("Environment variable MACHINE_PATH_TEMPLATE is not set")

        return [path_template.format(machine_name=machine.name) for machine in self.machines]


