import logging
import time
import traceback

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication

from model.data import DataModel


def exception_hook(exc_type, exc_value, exc_traceback):
    print("Python error:", exc_type, ":", exc_value)
    traceback.print_tb(exc_traceback)


class SafeApplication(QApplication):
    def notify(self, receiver, event):
        try:
            return QApplication.notify(self, receiver, event)
        except Exception as e:
            logging.error("Exception caught from QApplication:", e)
            traceback.print_exc()
            return False


class WorkerThread(QThread):
    """
    This is for controlling async functions
    """

    finished = pyqtSignal(object)
    updated = pyqtSignal(int)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        logging.info(f"Start worker thread, function : {self.func}")
        try:
            self.kwargs["callback"] = self._make_update
            self.func(*self.args, **self.kwargs)
            result = True
        except Exception as e:
            logging.error(f"Function execution failed: {e}")
            result = False
        self.finished.emit(result)

    def _make_update(self, value):
        self.updated.emit(value)


def monitor_thread(thread, callback, val):
    thread.join()
    callback(val)
    logging.info(f"thread : {thread.name} is finished")


def q_monitor_thread(q, callback, full_cnt):
    while True:
        current_cnt = q.qsize()
        callback(10000 * current_cnt / full_cnt)
        if current_cnt == full_cnt:
            break


def func_log(func):
    """
    This is decorator for logging function informations.
    It can show func_name, args, kwargs, return, error.
    """

    def execute_func(*args, **kwargs):
        start = time.time()
        try:
            result = func(*args, **kwargs)
            end = time.time()
            logging.info(
                f"function {func.__name__} is called, \n args : {args} \n kwargs : {kwargs} \n return : {result} \n running time : {end-start}"
            )
        except Exception as e:
            end = time.time()
            logging.error(
                f"function {func.__name__} failed, \n args : {args} \n kwargs : {kwargs} \n error: {str(e)} \n running time : {end-start}"
            )
            raise
        return result

    return execute_func


def print_dict(dictionary):
    """
    Show all dict key, value recursively.
    """
    for key, value in dictionary.items():
        logging.info(f"key : {key}, value: {value}")
        if isinstance(value, DataModel):
            print_dict(value.data)
        elif isinstance(value, dict):
            print_dict(value)
