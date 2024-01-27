from abc import abstractmethod
from collections import namedtuple
import copy
from functools import partial
import logging
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QScrollArea,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QThread, pyqtSignal
from config import JOB_A, JOB_B, JOB_C, construct_query

from data import DataDict
from pyqt_ui import CheckBoxWidget
from user_function import make_atp, make_cfg, make_tb


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

    def create_button(self, text, callback):
        button = QPushButton(text, self)
        button.clicked.connect(callback)
        self.button_dict.set_data(text, button)
        self.button_layout.addWidget(self.button_dict.get_data(text))

    def save_data(self):
        """
        Save all widget data before moving to next/pre window.
        """
        for widget in self.input_widgets:
            widget.save()

    def restore_data(self):
        """
        Restore all widget status after getting back from next/pre window.
        """
        for widget in self.input_widgets:
            widget.restore()

    def print_restored_data(self):
        print("restored data")
        for widget in self.input_widgets:
            print(f"widget : {widget.get_value()}")

    def print_saved_data(self):
        print("saved data")
        for widget in self.input_widgets:
            print(f"widget : {widget.log}")

    def show_msgbox(self, text):
        msg = QMessageBox(self)
        font = QFont("Bookman Old Style", 15, QFont.Bold)
        msg.setFont(font)
        msg.setText(text)
        msg.show()

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

    def __init__(self, query, job_data):
        super().__init__()

        self.query = query
        self.job_data = job_data
        self.input_widgets = list(query.get_query().values())
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
        for idx in range(len(self.input_widgets)):
            self.container_layout.addWidget(self.input_widgets[idx])

        self.button_layout = QHBoxLayout()

        self.next_button = QPushButton("Next", self)
        self.next_button.clicked.connect(self.show_next_window)
        self.button_layout.addWidget(self.next_button)

        self.container_layout.addLayout(self.button_layout)
        self.container.setLayout(self.container_layout)
        self.scroll_area.setWidget(self.container)
        self.layout.addWidget(self.scroll_area)

        self.setLayout(self.layout)
        self.show()

    def show_next_window(self):
        self.current_job = self.input_widgets[0].get_value()
        self.next_query = self.job_data.get_data(self.current_job).query
        self.next_func = self.job_data.get_data(self.current_job).func
        self.save_data()
        self.hide()
        self.next_window = InputWindow(
            self.next_query, DataDict("INFO"), self, self.next_func
        )


class InputWindow(BaseInputWindow):
    """
    This is main input window
    You can put detailed data that would be used to execute your job.
    """

    def __init__(self, query, infos, pre_window=None, func=None):
        super().__init__()

        self.query = query
        self.infos = infos
        self.pre_infos = copy.deepcopy(infos)
        self.pre_window = pre_window
        self.next_window = None
        self.func = func
        self.input_varname = list(query.get_query().keys())
        self.input_widgets = list(query.get_query().values())
        self.button_dict = DataDict("BUTTON")
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

        for idx in range(len(self.input_widgets)):
            self.add_widget2layout(idx)

        self.button_layout = QHBoxLayout()

        self.create_button("Back", self.show_pre_window)
        self.create_button("Next", self.show_next_window)
        self.create_button("Submit", self.execute_function)

        if not self.query.is_last():
            self.button_dict.get_data("Submit").setDisabled(True)
            self.button_dict.get_data("Next").setEnabled(True)
        else:
            self.button_dict.get_data("Submit").setEnabled(True)
            if not self.query.is_repeat_type():
                self.button_dict.get_data("Next").setDisabled(True)
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
        self.input_widgets[idx].reset()
        if isinstance(self.input_widgets[idx], CheckBoxWidget):
            self.on_off_line_edit(idx, 0)
            self.input_widgets[idx].check_box.stateChanged.connect(
                partial(self.on_off_line_edit, idx)
            )
        self.container_layout.addWidget(self.input_widgets[idx])

    def on_off_line_edit(self, idx, state):
        """
        This makes line_edits disable or enable
        according to the checkbutton status.
        """
        if state == 2:
            self.input_widgets[idx + 1].line_edit.setEnabled(True)
            self.input_widgets[idx + 2].line_edit.setEnabled(True)
        else:
            self.input_widgets[idx + 1].line_edit.setDisabled(True)
            self.input_widgets[idx + 2].line_edit.setDisabled(True)

    def copy_pre_info(self):
        """
        deepcopy is needed to make it different object
        from original infos
        """
        self.pre_infos = copy.deepcopy(self.infos)

    def set_info(self, value):
        self.infos = value

    def update_info(self):
        """
        This function saves all input data to self.infos
        """
        if self.query.is_last() and self.query.is_repeat_type():
            new_key = self.input_widgets[0].get_value()
            for idx in range(1, len(self.input_varname)):
                self.infos.set_data(
                    new_key + "." + self.input_varname[idx],
                    self.input_widgets[idx].get_value(),
                )
        else:
            for idx in range(len(self.input_varname)):
                self.infos.set_data(
                    self.input_varname[idx], self.input_widgets[idx].get_value()
                )

    def restore_info(self):
        self.infos = copy.deepcopy(self.pre_infos)

    def show_pre_window(self):
        self.save_data()
        self.hide()
        self.pre_window.query.down_cnt()
        self.pre_window.restore_data()
        try:
            self.pre_window.restore_info()
        except Exception:
            print("Previous window is job select window")
            pass
        self.pre_window.show()

    def show_next_window(self):
        self.save_data()
        self.update_info()
        self.hide()
        self.query.up_cnt()
        if not self.next_window:
            self.next_query = copy.deepcopy(self.query)
            self.next_window = InputWindow(self.next_query, self.infos, self, self.func)
        else:
            self.next_window.restore_data()
            self.next_window.set_info(self.infos)
            self.next_window.copy_pre_info()
            self.next_window.show()

    def execute_function(self):
        self.update_info()
        print("execute!!!")
        self.infos.show_all()
        self.worker_thread = WorkerThread(self.func, **self.infos.data)
        self.worker_thread.finished.connect(self.handle_result)
        self.worker_thread.start()

    def handle_result(self, result):
        if result:
            self.show_msgbox("Complete!")
        else:
            self.show_msgbox("Fail!")


class WorkerThread(QThread):
    """
    This is for controlling async functions
    """

    finished = pyqtSignal(object)

    def __init__(self, func, **kwargs):
        super().__init__()
        self.func = func
        self.kwargs = kwargs

    def run(self):
        try:
            self.func(**self.kwargs)
            result = True
        except Exception("execute funcion failed"):
            result = False
        self.finished.emit(result)


if __name__ == "__main__":
    app = QApplication([])
    query = construct_query()
    logging.basicConfig(
        level=logging.INFO, format="%(levelname)s [%(asctime)s] - %(message)s"
    )
    job = DataDict("JOB")
    job_info = namedtuple("info", "query, func")
    info_A = job_info(query.jobA, make_tb)
    info_B = job_info(query.jobB, make_cfg)
    info_C = job_info(query.jobC, make_atp)
    job.set_data(JOB_A, info_A)
    job.set_data(JOB_B, info_B)
    job.set_data(JOB_C, info_C)

    window = JobSelectWindow(query.common, job)
    window.show()
    sys.exit(app.exec_())
