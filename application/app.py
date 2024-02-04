import logging
import sys
from collections import namedtuple

from PyQt5.QtWidgets import QApplication

from controller.user_function import make_atp, make_cfg, make_tb
from model.config import (JOB_A, JOB_B, JOB_C, construct_a_query,
                          construct_b_query, construct_base_query,
                          construct_c_query)
from model.data import DataModel
from view.ui_window import JobSelectWindow


class MainApplication:

    def __init__(self, job, window):
        self.app = QApplication([])
        self.job = job
        self.window = window
        self.setup()

    def setup(self):
        self.query = construct_base_query()
        logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(asctime)s] - %(message)s")
        job_info = namedtuple("info", "query_func, execute_func")
        info_A = job_info(construct_a_query, make_tb)
        info_B = job_info(construct_b_query, make_cfg)
        info_C = job_info(construct_c_query, make_atp)
        self.job.set_data(JOB_A, info_A)
        self.job.set_data(JOB_B, info_B)
        self.job.set_data(JOB_C, info_C)

    def run(self):
        window = self.window(self.query, self.job)
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    job = DataModel("JOB")
    app = MainApplication(job, JobSelectWindow)
    app.run()
