import json
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QMainWindow, QWidget, QTableWidget, QTableWidgetItem,QPushButton
from PyQt5.QtGui import QFont
from PyQt5 import QtCore

from Configurations.json_writer import JsonWriter

class ArchiveWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Automationtool - Archiv")
        self.width = 900
        self.height = 500
        self.setFixedSize(self.width, self.height)

        self.jsonWriter = JsonWriter()

        self.dateLabel = "Datum eingeben\nYYYY-MM-DD"
        self.archiveLabel = "Archiv - Einträge aus der durchlaufen.json"
        self.archiveKeys = ["Rechner", "Zeitpunkt","dd", "mm", "yyyy", "Modul-Eintrag"]
        
        self.font = QFont("Arial", 11)
        self.initUI()

    def initUI(self):
        """
        Initializes the user interface for the archive window.

        This method sets up the central widget and layout, adds the header and archive sections,
        and includes an update button for refreshing entries.

        Layout Structure:
        - Central Layout (QVBoxLayout)
            - Header Layout (from getHeaderLayout)
            - Archive Layout (from getArchiveLayout)
            - Update Button ("Einträge aktualisieren")

        The update button is connected to the updateEntries method.

        """
        centralLayout = QVBoxLayout()
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.setLayout(centralLayout)

        # Header
        headerLayout = self.getHeaderLayout()
        centralLayout.addLayout(headerLayout)

        # Archive
        archiveLayout = self.getArchiveLayout()
        centralLayout.addLayout(archiveLayout)

        # Update Button
        self.updateButton = QPushButton("Einträge aktualisieren")
        self.updateButton.clicked.connect(self.updateEntries)
        centralLayout.addWidget(self.updateButton)


    def createHeaderComponent(self):
        """
        Creates the header component for the UI.

        This method sets up the header layout using QHBoxLayout and QVBoxLayout.
        It creates a headline label with a specific font and alignment, and adds it to the layout.

        Attributes:
            vboxHeader (QVBoxLayout): The vertical box layout for the header.
            headerLabel (QLabel): The label used as the headline in the header.

        Layout:
            - A QHBoxLayout is created and added to vboxHeader.
            - A QLabel is created with the text from self.archiveLabel, styled with a specific font, and added to the QHBoxLayout.
        """
        hbox = QHBoxLayout()
        self.vboxHeader = QVBoxLayout()
        self.vboxHeader.addLayout(hbox)
        fontHeadline = QFont("Arial", 15)
        fontHeadline.setUnderline(True)

        # Headline row 0, archiveLabel
        self.headerLabel = QLabel(self.archiveLabel)
        self.headerLabel.setFont(fontHeadline)
        self.headerLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.headerLabel.setContentsMargins(20, 20, 20, 20)
        hbox.addWidget(self.headerLabel)


    def createArchive(self):
        """
        Creates the archive layout for the UI.

        This method sets up the layout for the archive section of the UI. It initializes
        a horizontal box layout (hbox) and a vertical box layout (vboxArchive). It also
        sets up a QTableWidget with the number of columns based on the length of 
        `self.archiveKeys` and sets the horizontal header labels to `self.archiveKeys`.
        Finally, it calls `self.updateEntries()` to populate the table with data.
        """
        hbox = QHBoxLayout()
        self.vboxArchive = QVBoxLayout()
        self.vboxArchive.addLayout(hbox)
        fontHeadline = QFont("Arial", 15)
        fontHeadline.setUnderline(True)

        self.tableWidget = QTableWidget()

        # Anzahl der Spalten basierend auf den Daten
        self.tableWidget.setColumnCount(len(self.archiveKeys))
        self.tableWidget.setHorizontalHeaderLabels(self.archiveKeys)
        hbox.addWidget(self.tableWidget)
        self.updateEntries()


    def updateEntries(self):
        """
        Updates the entries in the table widget by reading data from a JSON file.
        This method clears the existing rows in the table widget and populates it with new rows
        based on the data read from the JSON file specified in `self.jsonWriter.data`. Each entry
        in the JSON file is expected to be a dictionary containing nested dictionaries. The method
        extracts specific fields from these nested dictionaries and inserts them into the table widget.
        The following fields are extracted from each nested dictionary:
        - hostname: The hostname of the entry.
        - timestamp: The timestamp of the entry.
        - dd: The day of the entry.
        - mm: The month of the entry.
        - yyyy: The year of the entry.
        - modulEntry: A list of module entries, each item is displayed on a new line in the table.
        The text in the `modulEntry` column is aligned to the top for better readability.
        Raises:
            FileNotFoundError: If the JSON file specified in `self.jsonWriter.data` does not exist.
            json.JSONDecodeError: If the JSON file contains invalid JSON.
        """
        with open(self.jsonWriter.data) as f:
            data = json.load(f)

        self.tableWidget.setRowCount(0)  # Clear existing rows
        
        row = 0
        for entry in data:
            # Check if entry is a dictionary
            if isinstance(entry, dict):
                # Access data within the nested dictionary using the key
                nestedData = entry[list(entry.keys())[0]]  # Get first key

                hostname = nestedData.get(self.jsonWriter.hostname, "")
                timestamp = nestedData.get(self.jsonWriter.timestamp, "")
                dd = nestedData.get(self.jsonWriter.dd, "")
                mm = nestedData.get(self.jsonWriter.mm, "")
                yyyy = nestedData.get(self.jsonWriter.yyyy, "")

                # Format modulEntry with each item on a new line
                modulEntries = nestedData.get(self.jsonWriter.modulEntry, [])
                modulEntryStr = "\n".join(modulEntries)

                self.tableWidget.insertRow(row)
                self.tableWidget.setItem(row, 0, QTableWidgetItem(hostname))
                self.tableWidget.setItem(row, 1, QTableWidgetItem(timestamp))
                self.tableWidget.setItem(row, 2, QTableWidgetItem(dd))
                self.tableWidget.setItem(row, 3, QTableWidgetItem(mm))
                self.tableWidget.setItem(row, 4, QTableWidgetItem(yyyy))
                modulItem = QTableWidgetItem(modulEntryStr)
                modulItem.setTextAlignment(QtCore.Qt.AlignTop)  # Align text to top for better readability
                self.tableWidget.setItem(row, 5, modulItem)
                row += 1


    def getHeaderLayout(self):
        """
        Creates and returns the header layout for the UI.

        This method initializes a QVBoxLayout, calls the method to create the header component,
        adds the header component layout to the QVBoxLayout, and returns the resulting layout.

        Returns:
            QVBoxLayout: The layout containing the header component.
        """
        headerLayout = QVBoxLayout()
        self.createHeaderComponent()
        headerLayout.addLayout(self.vboxHeader)
        return headerLayout


    def getArchiveLayout(self):
        """
        Creates and returns the layout for the archive window.

        This method initializes a QVBoxLayout, calls the createArchive method to 
        set up the archive, and adds the created archive layout to the QVBoxLayout.

        Returns:
            QVBoxLayout: The layout containing the archive.
        """
        archiveLayout = QVBoxLayout()
        self.createArchive()
        archiveLayout.addLayout(self.vboxArchive)
        return archiveLayout
