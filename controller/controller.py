import copy
from controller.utility import WorkerThread
from model.data import DataModel
from PyQt5.QtWidgets import (
    QPushButton,
    QMessageBox,
)
from PyQt5.QtGui import QFont


class ButtonManager:
    def __init__(self, parent):
        self.button_data = DataModel("BUTTON")
        self._parent = parent

    def create_button(self, name, callback, *args, **kwargs):
        button = QPushButton(name, self._parent)
        button.clicked.connect(lambda: callback(*args, **kwargs))
        self.button_data.set_data(name, button)

    def get_button(self, key):
        try:
            return self.button_data.get_data(key)
        except KeyError:
            print(f"Key {key} is not in Button manager")
            raise

    def enable_control(self, key, enable):
        self.get_button(key).setEnabled(enable)


class DataManager:
    def __init__(self, query, infos):
        self.query = query
        self.infos = infos
        self.pre_infos = copy.deepcopy(self.infos)
        self._input_varname = list(query.get_query().keys())
        self._input_widgets = list(query.get_query().values())
        self.widget_number = len(self._input_widgets)

    def set_info(self, value):
        self.infos = value

    def save_data(self):
        """
        Save all widget data before moving to next/pre window.
        """
        for widget in self._input_widgets:
            widget.save()

    def restore_data(self):
        """
        Restore all widget status after getting back from next/pre window.
        """
        for widget in self._input_widgets:
            widget.restore()

    def print_restored_data(self):
        print("restored data")
        for widget in self._input_widgets:
            print(f"widget : {widget.get_value()}")

    def print_saved_data(self):
        print("saved data")
        for widget in self._input_widgets:
            print(f"widget : {widget.log}")

    def copy_next_query(self):
        """
        deepcopy is needed to make it different object
        from original query
        """
        self.next_query = copy.deepcopy(self.query)

    def copy_pre_info(self):
        """
        deepcopy is needed to make it different object
        from original infos
        """
        self.pre_infos = copy.deepcopy(self.infos)

    def update_info(self):
        """
        This function saves all input data to self.infos
        """
        if self.query.is_last() and self.query.is_repeat_type():
            new_key = self._input_widgets[0].get_value()
            for idx in range(1, self.widget_number):
                self.infos.set_data(
                    new_key + "." + self._input_varname[idx],
                    self._input_widgets[idx].get_value(),
                )
        else:
            for idx in range(self.widget_number):
                self.infos.set_data(
                    self._input_varname[idx], self._input_widgets[idx].get_value()
                )

    def restore_info(self):
        self.infos = copy.deepcopy(self.pre_infos)

    def print_all(self):
        self.infos.show_all()

    def get_widget(self, idx):
        return self._input_widgets[idx]


class NavigatorManager:
    def __init__(self, pre_window=None):
        self.pre_window = pre_window
        self.next_window = None

    def show_pre_window(self):
        self.pre_window.data_manager.query.down_cnt()
        self.pre_window.data_manager.restore_data()
        try:
            self.pre_window.data_manager.restore_info()
        except Exception:
            print("Previous window is job select window")
            pass
        self.pre_window.show()

    def show_next_window(self, BaseInputWindow, *args):
        if not self.next_window:
            self.next_window = BaseInputWindow(*args)
        else:
            self.next_window.show()

    def show_input_window(self, *args):
        self.next_window = BaseInputWindow(*args)


class ExecuteManager:
    def __init__(self, func, parent):
        self.func = func
        self._parent = parent

    def execute_function(self, *args, **kwargs):
        print("execute!!!")
        self.worker_thread = WorkerThread(self.func, *args, **kwargs)
        self.worker_thread.finished.connect(self.handle_result)
        self.worker_thread.start()

    def handle_result(self, result):
        if result:
            self.show_msgbox("Complete!")
        else:
            self.show_msgbox("Fail!")

    def show_msgbox(self, text):
        self.msg = QMessageBox(self._parent)
        font = QFont("Bookman Old Style", 15, QFont.Bold)
        self.msg.setFont(font)
        self.msg.setText(text)
        self.msg.show()
