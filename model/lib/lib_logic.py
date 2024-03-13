import gc
import logging
import os
import subprocess
import threading
import time
from collections import defaultdict
from multiprocessing import Process
from memory_profiler import profile
import pandas as pd
import objgraph
from controller.utility import func_log, monitor_thread
from model.data import DataModel


# @func_log
@profile
def make_base_info(*args, **kwargs):
    callback = kwargs.get("callback", None)
    for i in range(1, 101):
        callback(100 * i)
        time.sleep(0.05)


# @func_log
@profile
def make_lib_status_info(*args, **kwargs):
    callback = kwargs.get("callback", None)
    for i in range(1, 101):
        callback(100 * i)
        time.sleep(0.05)