# Automationtool
Das Tool zur Unterstützung automatisierten Tests beihilft. Es umfasst die automatisierte Änderung von Konfigurationsdateien virtueller Maschinen sowie die automatisierte Installation und Testausführung. Zusätzlich wird eine lokale HTML-Anwendung zur Früherkennung von Fehlern im Testlauf, sichtbar als Tortendiagramm, erstellt. Und vieles mehr.

## Setup
- requirements.txt 
- install_openssh.bat - auf jeder Maschine einfügen und ausführen. Danach eine SSH-Verbindung (Host-VM) zu den Maschinen aufbauen.



## SSH-Verbindung:
### 1. SSH-Schlüssel auf dem Rechner erzeugen:

* ssh-keygen
    * Folgen Sie den Anweisungen und drücken Sie die Eingabetaste, um die Standardwerte zu akzeptieren.

2. Öffentlichen Schlüssel auf den Zielcomputer kopieren:
* ssh-copy-id john@192.168.1.100
    * Geben Sie das Passwort des Benutzers john ein.

3. SSH-Verbindung mit Schlüssel herstellen:

* ssh john@192.168.1.100
    * Nach diesen Schritten können Sie sich ohne erneute Passwortabfrage auf dem Zielcomputer anmelden, solange der öffentliche Schlüssel im ~/.ssh/authorized_keys-Datei des Benutzers auf dem Zielcomputer vorhanden ist.


machines.json, die beim ersten Start erstellt wird:
```
{
    "Maschine100": {
        "modul": ["Modul_1", "Modul_2", "Modul_3","Modul_4"],
        "path": "\\HOSTNAME\\FREIGABE\\MODUL-ORDNER\\PFAD\\ZUR\\DATEI\\DATEI.ini"
    },
    ...
    .
}
    
```