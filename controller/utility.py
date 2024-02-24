import logging
import time

from PyQt5.QtCore import QObject, QRunnable, QThread, pyqtSignal, pyqtSlot

from model.data import DataModel


class WorkerSignals(QObject):
    finished = pyqtSignal(object)
    updated = pyqtSignal(float)


class Worker(QRunnable):
    def __init__(self, func, signal, *args, **kwargs):
        super(Worker, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = signal
        self.finished = False

    @pyqtSlot()
    def run(self):
        try:
            self.kwargs["callback"] = self._make_update
            self.func(*self.args, **self.kwargs)
            result = True
        except Exception as e:
            result = False
        finally:
            self.finished = True
            self.signals.finished.emit(result)

    def _make_update(self, value):
        self.signals.updated.emit(value)

    def is_finished(self):
        self.finished = True


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
