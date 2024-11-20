from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import QLabel, QWidget,QHBoxLayout
class TrafficLightWidget(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
  
        self.initUI()

    def initUI(self):
        """
        Initializes the user interface for the traffic light widget.

        This method sets up the layout and creates QLabel widgets to represent 
        the traffic lights (green, orange, red, and black). Each light is given 
        a fixed size and styled to appear round and colored. Initially, all lights 
        are set to be invisible. The lights are then added to the horizontal layout.

        Attributes:
            layout (QHBoxLayout): The horizontal layout for the traffic lights.
            greenLight (QLabel): The label representing the green light.
            orangeLight (QLabel): The label representing the orange light.
            redLight (QLabel): The label representing the red light.
            blackLight (QLabel): The label representing the black light.
        """
        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Create labels for the traffic lights
        self.greenLight = QLabel()
        self.orangeLight = QLabel()
        self.redLight = QLabel()
        self.blackLight = QLabel()

        # Set fixed size for each light to make them small and round
        size = 15
        self.greenLight.setFixedSize(size, size)
        self.orangeLight.setFixedSize(size, size)
        self.redLight.setFixedSize(size, size)
        self.blackLight.setFixedSize(size, size)

        # Apply styles to make them round and colored
        self.greenLight.setStyleSheet("background-color: green; border-radius: 7px;")
        self.orangeLight.setStyleSheet("background-color: orange; border-radius: 7px;")
        self.redLight.setStyleSheet("background-color: red; border-radius: 7px;")
        self.blackLight.setStyleSheet("background-color: black; border-radius: 7px;")

        # Not showing when implementing the widget 
        self.greenLight.setVisible(False)
        self.orangeLight.setVisible(False)
        self.redLight.setVisible(False)
        self.blackLight.setVisible(False)

        # Add the lights to the layout
        self.layout.addWidget(self.greenLight)
        self.layout.addWidget(self.orangeLight)
        self.layout.addWidget(self.redLight)
        self.layout.addWidget(self.blackLight)


    def setStatus(self, status):
        """
        Set the status of the traffic light widget and update the visibility of the lights accordingly.

        Parameters:
        status (str): The status of the traffic light. It can be one of the following values:
                  - "green": Turns on the green light and turns off the orange and red lights.
                  - "orange": Turns on the orange light and turns off the green and red lights.
                  - "red": Turns on the red light and turns off the green and orange lights.
                  - "black": Turns off all lights and turns on the black light.
        """
        self.status = status
        if self.status == "green":
            self.greenLight.setVisible(True)
            self.orangeLight.setVisible(False)
            self.redLight.setVisible(False)

        elif self.status == "orange":
            self.greenLight.setVisible(False)
            self.orangeLight.setVisible(True)
            self.redLight.setVisible(False)

        elif self.status == "red":
            self.greenLight.setVisible(False)
            self.orangeLight.setVisible(False)
            self.redLight.setVisible(True)

        elif self.status == "black":
            self.greenLight.setVisible(False)
            self.orangeLight.setVisible(False)
            self.redLight.setVisible(False)
            self.blackLight.setVisible(True)
