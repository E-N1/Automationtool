import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QVBoxLayout, QWidget, QScrollArea, QSizePolicy,QMessageBox
from PyQt5.QtCore import QThread, Qt

from Configurations.machines import Machines
from Configurations.read_controlling import ReadControlling
from Configurations.read_fault import ReadFault
from Logic.drive_checker import DriveChecker

from Logic.status_worker import StatusWorker

from UI.window_components import WindowComponents
from UI.traffic_light_widget import TrafficLightWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Configurations
        self.machines = Machines()
        self.readFault = ReadFault()
        self.readControlling = ReadControlling()

        # UI
        self.component = WindowComponents()

        # Logic
        self.driveChecker = DriveChecker()

        self.setWindowTitle("Automationtool")
        self.widgets = []

        self.initUI()
        self.setupWorker()

        # Überprüfe die Laufwerksverbindungen und zeige den Status an
        self.showDriveStatus()

    def initUI(self):
        """
        Initializes the main user interface components.
        This method sets up the central widget, a scroll area with vertical scrolling
        always enabled and horizontal scrolling disabled, and a vertical box layout
        for the central widget. It also adds header, main components, and footer 
        sections to the layout. Additionally, it configures the margins for the 
        central layout and ensures that the central widget matches the width of the 
        scroll area.
        Components initialized:
        - centralWidget: The main widget for the central area.
        - scrollArea: A scrollable area containing the central widget.
        - centralLayout: A vertical box layout for the central widget.
        Methods called:
        - addHeader(): Adds the header section to the layout.
        - addMainComponents(): Adds the main components to the layout.
        - addFooter(): Adds the footer section to the layout.
        """
        self.centralWidget = QWidget()

        # ScrollArea
        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(self.centralWidget)
        self.setCentralWidget(self.scrollArea)

        self.centralLayout = QVBoxLayout(self.centralWidget)

        self.addHeader()
        self.addMainComponents()
        self.addFooter()

        # Margin for the main layout container
        self.centralLayout.setContentsMargins(20, 10, 20, 50)

        # Ensure the central widget matches the width of the scroll area
        self.centralWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)



    def resizeEvent(self, event):
        """
        Handles the resize event for the main window.

        This method is called whenever the main window is resized. It ensures that
        the central widget's minimum width is set to the width of the scroll area's viewport.

        Args:
            event (QResizeEvent): The resize event object containing information about the resize.
        """
        super().resizeEvent(event)
        self.centralWidget.setMinimumWidth(self.scrollArea.viewport().width())


    def setupWorker(self):
        """
        Sets up a worker thread for updating the status of a component.
        This method initializes a QThread and a StatusWorker, moves the worker to the thread,
        connects the worker's update_status signal to the updateTrafficLightStatus slot, 
        and starts the thread.
        Attributes:
            self.thread (QThread): The thread in which the worker will run.
            self.worker (StatusWorker): The worker that will perform the status update tasks.
        """
        self.thread = QThread()
        self.worker = StatusWorker(self.component)
        self.worker.moveToThread(self.thread)

        self.worker.update_status.connect(self.updateTrafficLightStatus)

        self.thread.started.connect(self.worker.run)
        self.thread.start()


    def updateTrafficLightStatus(self, machine, status):
        """
        Updates the traffic light status of a virtual machine component.

        Args:
            machine (str): The hostname of the virtual machine.
            status (str): The new status to set for the traffic light widget. 
                  Possible values include "Online", "Offline", etc.

        This method iterates over the list of virtual machine components, finds the 
        corresponding traffic light widget for the given machine, and updates its status.
        If the status is "Offline", the virtual machine component is removed from the list.

        Raises:
            ValueError: If the traffic light widget is not found for the given machine.
        """
        for vmComponent in self.component.vmComponentList[:]:  # Iterate over a copy of the list
            if vmComponent.hostname[vmComponent.number] == machine:
                trafficLightWidget = vmComponent.vmGroupBox.findChild(TrafficLightWidget)
                if trafficLightWidget:
                    trafficLightWidget.setStatus(status)
                if status == "Offline":
                    self.component.vmComponentList.remove(vmComponent)
                    print(f"Removed {machine} from the list")


    def closeEvent(self, event):
        """
        Handles the close event for the main window.
        This method is called when the main window is about to be closed. It performs
        necessary cleanup operations such as stopping the worker, quitting the thread,
        killing the time manager, and terminating the thread if it is still running.
        Args:
            event (QCloseEvent): The close event that triggered this method.
        """
        self.worker.stop()
        self.thread.quit()
        self.readControlling.killTimemanager()
        if self.thread.isRunning():
            self.thread.terminate()

        self.close()


    def addHeader(self):
        """
        Adds the header layout to the central layout of the main window.

        This method retrieves the header layout from the component and adds it to the central layout.
        """
        headerLayout = self.component.getHeaderLayout()
        self.centralLayout.addLayout(headerLayout)


    def addMainComponents(self):
        """
        Adds the main components to the central layout.

        This method retrieves the main layout for the virtual machines using the number of machines
        and their names, and then adds this layout to the central layout of the main window.
        """
        vmsLayout = self.component.getMainLayout(self.machines.getNumberOfMachines(), self.machines.getMachineNameOfAll(), self)
        self.centralLayout.addLayout(vmsLayout)


    def addFooter(self):
        """
        Adds the footer layout to the central layout of the main window.

        This method retrieves the footer layout from the component and adds it to the central layout.
        """
        footerLayout = self.component.getFooterLayout()
        self.centralLayout.addLayout(footerLayout)


    def showDriveStatus(self):
        """
        Displays the status of network drives in a message box.
        This method checks the connection status of all network drives using the
        `driveChecker` object. It then creates an informational message indicating
        which drives are connected and which are not, and displays this message
        in a message box.
        The connected drives are displayed in green, while the not connected drives
        are displayed in red.
        """
        connected, notConnected = self.driveChecker.checkAllDrives()

        # Erstelle Labels für die Netzwerklaufwerke
        infoMessage = "<b>Netzwerklaufwerkstatus:</b><br>"

        for drive in connected:
            infoMessage += f"<span style='color: green;'>{drive} - Verbunden</span><br>"

        for drive in notConnected:
            infoMessage += f"<span style='color: red;'>{drive} - Nicht verbunden</span><br>"

        # Zeige eine MessageBox als extra Information
        QMessageBox.information(self, "Laufwerkstatus", infoMessage)

    def startGUI(self):
        """
        Initializes and starts the GUI application.

        This method creates an instance of QApplication, initializes the main window,
        displays it maximized, and starts the application's event loop.
        """
        app = QApplication(sys.argv)
        window = MainWindow()
        window.showMaximized()
        sys.exit(app.exec_())