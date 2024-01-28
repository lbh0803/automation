from abc import abstractmethod
from functools import partial
from PyQt5.QtWidgets import (
    QScrollArea,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
)
from PyQt5.QtGui import QFont
from controller.controller import (
    ButtonManager,
    DataManager,
    ExecuteManager,
    NavigatorManager,
)
from model.data import DataModel
from view.ui_widgets import CheckBoxWidget


class BaseInputWindow(QWidget):
    """
    This class is basic interface for other Qwidget classes.
    """

    @abstractmethod
    def __init__(self, *args):
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


class JobSelectWindow(BaseInputWindow):
    """
    You can select which job to be executed.
    """

    def __init__(self, query, infos):
        super().__init__()

        self.button_manager = ButtonManager(self)
        self.buttons = {"Exit": self.close, "Next": self.show_next_window}
        self.data_manager = DataManager(query, infos)
        self.navi_manager = NavigatorManager()
        self.init_ui()

    def init_ui(self):
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_layout.setSpacing(150)

        self.layout = QVBoxLayout(self)
        self.font = QFont("Bookman Old Style", 12, QFont.Bold)
        self.font.setBold(True)
        self.setFont(self.font)
        for idx in range(self.data_manager.widget_number):
            self.container_layout.addWidget(self.data_manager.get_widget(idx))

        self.button_layout = QHBoxLayout()

        for button_name in self.buttons:
            self.button_manager.create_button(button_name, self.buttons[button_name])
            self.button_layout.addWidget(self.button_manager.get_button(button_name))

        self.container_layout.addLayout(self.button_layout)
        self.container.setLayout(self.container_layout)
        self.scroll_area.setWidget(self.container)
        self.layout.addWidget(self.scroll_area)

        self.setLayout(self.layout)
        self.show()

    def show_next_window(self):
        self.current_job = self.data_manager.get_widget(0).get_value()
        self.next_query = self.data_manager.infos.get_data(self.current_job).query
        self.next_func = self.data_manager.infos.get_data(self.current_job).func
        self.data_manager.save_data()
        self.hide()
        self.navi_manager.show_next_window(
            InputWindow, self.next_query, DataModel("INFO"), self, self.next_func
        )
        self.navi_manager.next_window = None


class InputWindow(BaseInputWindow):
    """
    This is main input window
    You can put detailed data that would be used to execute your job.
    """

    def __init__(self, query, infos, pre_window=None, func=None):
        super().__init__()

        self.button_manager = ButtonManager(self)
        self.buttons = {
            "Back": self.show_pre_window,
            "Next": self.show_next_window,
            "Submit": self.execute_function,
        }
        self.data_manager = DataManager(query, infos)
        self.navi_manager = NavigatorManager(pre_window)
        self.execute_manager = ExecuteManager(func, self)
        self.init_ui()

    def init_ui(self):
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_layout.setSpacing(20)

        self.layout = QVBoxLayout(self)
        self.font = QFont("Bookman Old Style", 12, QFont.Bold)
        self.font.setBold(True)
        self.setFont(self.font)

        for idx in range(self.data_manager.widget_number):
            self.add_widget2layout(idx)

        self.button_layout = QHBoxLayout()
        for button_name in self.buttons:
            self.button_manager.create_button(button_name, self.buttons[button_name])
            self.button_layout.addWidget(self.button_manager.get_button(button_name))

        if not self.data_manager.query.is_last():
            self.button_manager.enable_control("Submit", False)
            self.button_manager.enable_control("Next", True)
        else:
            self.button_manager.enable_control("Submit", True)
            if not self.data_manager.query.is_repeat_type():
                self.button_manager.enable_control("Next", False)

        self.container_layout.addLayout(self.button_layout)
        self.container.setLayout(self.container_layout)
        self.scroll_area.setWidget(self.container)
        self.layout.addWidget(self.scroll_area)
        self.setLayout(self.layout)
        self.show()

    def add_widget2layout(self, idx):
        """
        Add widgets to layout,
        partial is needed to fix idx when it called later.
        """
        widget = self.data_manager.get_widget(idx)
        widget.reset()
        if isinstance(widget, CheckBoxWidget):
            self.on_off_line_edit(idx, 0)
            widget.check_box.stateChanged.connect(partial(self.on_off_line_edit, idx))
        self.container_layout.addWidget(widget)

    def on_off_line_edit(self, idx, state):
        """
        This makes line_edits disable or enable
        according to the checkbutton status.
        """
        if state == 2:
            self.data_manager.get_widget(idx + 1).line_edit.setEnabled(True)
            self.data_manager.get_widget(idx + 2).line_edit.setEnabled(True)
        else:
            self.data_manager.get_widget(idx + 1).line_edit.setDisabled(True)
            self.data_manager.get_widget(idx + 2).line_edit.setDisabled(True)

    def show_pre_window(self):
        self.data_manager.save_data()
        self.hide()
        self.navi_manager.show_pre_window()

    def show_next_window(self):
        self.data_manager.save_data()
        self.data_manager.update_info()
        self.data_manager.query.up_cnt()
        self.hide()
        if self.navi_manager.next_window:
            self.navi_manager.next_window.data_manager.restore_data()
            self.navi_manager.next_window.data_manager.set_info(self.data_manager.infos)
            self.navi_manager.next_window.data_manager.copy_pre_info()
        self.data_manager.copy_next_query()
        self.navi_manager.show_next_window(
            InputWindow,
            self.data_manager.next_query,
            self.data_manager.infos,
            self,
            self.execute_manager.func,
        )

    def execute_function(self):
        self.data_manager.update_info()
        self.data_manager.print_all()
        self.execute_manager.execute_function(**self.data_manager.infos.data)
