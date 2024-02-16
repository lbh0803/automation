import copy
import logging

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMessageBox, QPushButton
import pandas as pd

from controller.utility import WorkerThread, func_log
from model.data import DataModel
from view.ui_widget import ProgressBar


class ButtonManager:

    def __init__(self, parent):
        self.button_data = DataModel("BUTTON")
        self._parent = parent

    def create_button(self, name, callback, *args, **kwargs):
        self.button = QPushButton(name, self._parent)
        self.button.clicked.connect(lambda: callback(*args, **kwargs))
        self.font = QFont("Bookman Old Style", 12)
        self.font.setBold(True)
        self.button.setFont(self.font)
        self.button_data.set_data(name, self.button)

    def get_button(self, key):
        try:
            return self.button_data.get_data(key)
        except KeyError:
            logging.error(f"Key {key} is not in Button manager")
            raise

    def enable_control(self, key, enable):
        self.get_button(key).setEnabled(enable)


class DataManager:

    def __init__(self, query, info, base_info=None):
        self.query = query
        self.info = info
        self.base_info = base_info
        self.pre_info = copy.deepcopy(self.info)
        self._input_varname = list(query.get_query().keys())
        self._input_widgets = list(query.get_query().values())
        self.widget_number = len(self._input_widgets)

    def set_info(self, value):
        self.info = value

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
        logging.info("restored data")
        for widget in self._input_widgets:
            logging.info(f"widget : {widget.get_value()}")

    def print_saved_data(self):
        logging.info("saved data")
        for widget in self._input_widgets:
            logging.info(f"widget : {widget.log}")

    def copy_next_query(self):
        """
        deepcopy is needed to make it different object
        from original query
        """
        self.next_query = copy.deepcopy(self.query)

    def copy_pre_info(self):
        """
        deepcopy is needed to make it different object
        from original info
        """
        self.pre_info = copy.deepcopy(self.info)

    def update_info(self):
        """
        This function saves all input data to self.info
        """
        if self.query.is_repeat_type():
            # key : loop_data.mode_name.step ex) loop_data.TEST_MODE_ADC.VCD2WGL
            new_key = "loop_data." + self._input_widgets[0].get_value(
            ) + "." + self._input_widgets[1].get_value()
            for idx in range(2, self.widget_number):
                self.info.set_data(
                    new_key + "." + self._input_varname[idx],
                    self._input_widgets[idx].get_value(),
                )
            breakable = self._input_widgets[-1].get_value()
            self.check_repeat_break(breakable)
            return breakable
        else:
            for idx in range(self.widget_number):
                self.info.set_data(self._input_varname[idx], self._input_widgets[idx].get_value())

    def restore_info(self):
        self.info = copy.deepcopy(self.pre_info)

    def check_repeat_break(self, value):
        self.query.set_repeat_break(value)

    def show_all(self):
        self.info.show_all()

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
            logging.info("Previous window is job select window")
            pass
        self.pre_window.show()

    def show_next_window(self, BaseInputWindow, *args, **kwargs):
        if not self.next_window:
            self.next_window = BaseInputWindow(*args, **kwargs)
        else:
            self.next_window.show()


class ExecuteManager:

    def __init__(self, func, parent):
        self.func = func
        self._parent = parent

    def execute_function(self, *args, **kwargs):
        user_input = kwargs.get("user_input", None)
        self.dataframe_extractor = DataframeExtractor(user_input)
        self.dataframe_extractor.extract_dataframe()
        kwargs["dataframe_list"] = self.dataframe_extractor.dataframe_list
        self.kwargs = kwargs
        self.worker_thread = WorkerThread(self.func, *args, **kwargs)
        self.worker_thread.finished.connect(self._handle_result)
        self.worker_thread.updated.connect(self._udpate_progress)
        self.worker_thread.start()
        self.progressbar = ProgressBar()
        self.progressbar.show()

    def _udpate_progress(self, value):
        self.progressbar.update_progress(value)

    def _handle_result(self, result):
        if result:
            self._show_msgbox("Complete!")
        else:
            self._show_msgbox("Fail!")
        self._run_callback()
    
    def _run_callback(self):
        if "callback" in self.kwargs:
            self.kwargs["callback"]()

    def _show_msgbox(self, text):
        self.msg = QMessageBox(self._parent)
        font = QFont("Bookman Old Style", 15, QFont.Bold)
        self.msg.setFont(font)
        self.msg.setText(text)
        self.msg.buttonClicked.connect(self.progressbar.close)
        self.msg.show()


class DataframeExtractor:
    def __init__(self, user_input):
        self.user_input = user_input
        self.dataframe_list = list()
    
    def extract_dataframe(self):
        """
        To avoid unexpected Gui close, extract dataframe in mainthread
        """
        self.user_input.show_all()
        for variable in self.user_input.data:
            if "_xlsx" in variable:
                self._convert_to_dataframe(self.user_input.get_data(variable))
        logging.info("Extracting dataframe finished")

    def _convert_to_dataframe(self, excel):
        """
        To avoid unexpected Gui close, extract dataframe in mainthread
        """
        try:
            df = pd.read_excel(excel, sheet_name=None, header=None)
            for dataframe in df.values():
                dataframe.fillna("N/A", inplace=True)
                r_idx = (dataframe != "N/A").any(axis=1).idxmax()
                c_idx = (dataframe != "N/A").any(axis=0).idxmax()
                dataframe = dataframe.iloc[r_idx:, c_idx:]
                self.dataframe_list.append(dataframe)
        except Exception as e:
            logging.error(f"Error while converting excel data to dataframe : {e}")
