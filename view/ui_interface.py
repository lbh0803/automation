from abc import abstractmethod

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QMessageBox, QWidget


class BaseInputWidget(QWidget):
    """
    This is basic input widget for other input windows.
    All types of pyqt widget can inherit this class.
    """

    def __init__(self, label_text):
        super().__init__()

        self.label = QLabel(label_text, self)

    @abstractmethod
    def get_value(self):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def save(self):
        pass

    @abstractmethod
    def restore(self):
        pass

    @abstractmethod
    def __deepcopy__(self, memo):
        pass


class BaseInputWindow(QWidget):
    """
    This class is basic interface for other Qwidget classes.
    """

    @abstractmethod
    def __init__(self):
        super().__init__()
        pass

    @abstractmethod
    def init_ui(self):
        pass

    @abstractmethod
    def add_widget2layout(self, idx):
        pass

    @abstractmethod
    def show_next_window(self):
        pass

    def closeEvent(self, event):
        """
        This is called automatically, when exit button is clicked.
        """
        msg = QMessageBox()
        msg.setWindowTitle("Message")
        msg.setText("Are you sure you want to quit?")

        font = QFont("Bookman Old Style", 15, QFont.Bold)
        msg.setFont(font)

        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)

        reply = msg.exec_()

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
