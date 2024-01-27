import logging
import time

from data import DataDict


def func_log(func):
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
                f"function {func.__name__} failed, \n error: {str(e)} \n running time : {end-start}"
            )
            raise
        return result

    return execute_func


def print_dict(dictionary):
    for key, value in dictionary.items():
        print(f"key : {key}, value: {value}")
        if isinstance(value, DataDict):
            print_dict(value.data)
        elif isinstance(value, dict):
            print_dict(value)
