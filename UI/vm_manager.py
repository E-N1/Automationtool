class VMManager:
    # Dictionary für die VM-Daten
    headerEntriesDict = {'dd': '', 'mm': '', 'yyyy': '', 'praefix': '', 'build': ''}
    vmDict = {}
    controllingDict = {}

    def setHeaderEntries(self, key, value):
        """
        Updates the value of a specified key in the headerEntriesDict.

        Args:
            key (str): The key to update in the dictionary.
            value (Any): The new value to set for the specified key.

        Returns:
            dict: The updated headerEntriesDict.
        """
        if key in self.headerEntriesDict:
            self.headerEntriesDict[key] = value
        return self.headerEntriesDict

    def setVMDataSettings(self, iLoopVMNumber, boolActiv, *args, **kwargs):
        """
        Methode zum Setzen der VM-Daten.

        Args:
            iLoopVMNumber (int): Die Nummer der VM.
            boolActiv (bool): Aktivitätsstatus der VM.
            args (list): Eine Liste mit den Einträgen der VM.
            kwargs (dict): Ein Dictionary mit den Boolean-Werten der VM.
        """
        entryDict = args[:len(args)//2]
        boolDict = args[len(args)//2:]

        # Überprüfen, ob die VM-Nummer bereits im Dictionary vorhanden ist
        if iLoopVMNumber in self.vmDict:
            # Update der Einträge und Boolean-Werte für die VM
            self.vmDict[iLoopVMNumber].update({
                'Activ': {'bool': boolActiv},
                **entryDict,
                **boolDict,
                **kwargs
            })
        else:
            # Hinzufügen der Einträge und Boolean-Werte für eine neue VM
            self.vmDict[iLoopVMNumber] = {
                'Activ': {'bool': boolActiv},
                **entryDict,
                **boolDict,
                **kwargs
            }

    def getHeaderEntry(self, key):
        """ Returns the value of a specified key in the headerEntriesDict. """
        return self.headerEntriesDict.get(key)
