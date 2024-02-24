import logging
from abc import abstractmethod

import pandas as pd
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class BaseInputWidget(QWidget):
    """
    This is basic input widget for other input windows.
    All types of pyqt widget can inherit this class.
    """

    def __init__(self, label_text):
        super().__init__()
        self.set_font()
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

    def set_font(self):
        self.font = QFont("Courier New", 12)
        # self.font.setBold(True)
        self.setFont(self.font)


class BaseInputWindow(QWidget):
    """
    This class is basic interface for other Qwidget classes.
    """

    @abstractmethod
    def __init__(self, logo):
        super().__init__()
        self.logo = logo
        self.close_by_navigator = False
        self.center()
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.add_statusbar()
        self.add_logo_img()
        self.add_scroll_area()
        self.add_button_area()
        self.fill_scroll_area()
        self.fill_button_area()
        self.button_control()
        self.setLayout(self.layout)
        self.show()

    def add_statusbar(self):
        self.statusbar_layout = QHBoxLayout()
        self.statusbar_layout.addStretch(1)
        self.statusbar_widget = QWidget()
        self.home_icon = QPushButton()
        self.home_icon.setIcon(QIcon("home_logo.png"))
        self.home_icon.clicked.connect(self.go_home)
        self.statusbar_layout.addWidget(self.home_icon)
        self.statusbar_widget.setLayout(self.statusbar_layout)
        self.statusbar_widget.setFixedHeight(40)
        self.layout.addWidget(self.statusbar_widget)

    def add_logo_img(self):
        self.img_label = QLabel()
        self.pixmap = QPixmap(self.logo)
        self.pixmap = self.pixmap.scaled(
            self.width(), self.height(), Qt.KeepAspectRatio
        )
        self.img_label.setPixmap(self.pixmap)
        self.layout.addWidget(self.img_label)

    def add_scroll_area(self):
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_layout.setSpacing(20)
        self.container.setLayout(self.container_layout)
        self.scroll_area.setWidget(self.container)
        self.layout.addWidget(self.scroll_area)

    def add_button_area(self):
        self.button_layout = QHBoxLayout()

    @abstractmethod
    def fill_scroll_area(self):
        pass

    @abstractmethod
    def fill_button_area(self):
        pass

    @abstractmethod
    def button_control(self):
        pass

    @abstractmethod
    def show_next_window(self):
        pass

    @abstractmethod
    def go_home(self):
        pass

    def center(self):
        qr = self.frameGeometry()
        cp = QCoreApplication.instance().primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        """
        This is called automatically, when exit button is clicked.
        """
        if self.close_by_navigator:
            event.accept()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("Message")
            msg.setText("Are you sure you want to quit?")

            font = QFont("Bookman Old Style", 12, QFont.Bold)
            msg.setFont(font)

            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)

            reply = msg.exec_()

            if reply == QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()
