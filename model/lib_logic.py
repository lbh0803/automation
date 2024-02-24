import logging
import os
import subprocess
import threading
import time
from collections import defaultdict
from multiprocessing import Process

import pandas as pd

from controller.utility import func_log, monitor_thread
from model.data import DataModel


@func_log
def make_base_info(*args, **kwargs):
    callback = kwargs.get("callback", None)
    for _ in range(100):
        callback(100)
        time.sleep(0.05)

        
@func_log
def make_lib_status_info(*args, **kwargs):
    callback = kwargs.get("callback", None)
    for _ in range(100):
        callback(100)
        time.sleep(0.05)