from collections import namedtuple
import logging
import sys
from PyQt5.QtWidgets import QApplication
from controller.user_function import make_atp, make_cfg, make_tb

from model.config import JOB_A, JOB_B, JOB_C, construct_query
from model.data import DataModel
from view.ui_window import JobSelectWindow


class MainApplication:
    def __init__(self):
        self.app = QApplication([])
        self.setup()

    def setup(self):
        self.query = construct_query()
        logging.basicConfig(level=logging.INFO, format="%(levelname)s [%(asctime)s] - %(message)s")
        self.job = DataModel("JOB")
        job_info = namedtuple("info", "query, func")
        info_A = job_info(self.query.jobA, make_tb)
        info_B = job_info(self.query.jobB, make_cfg)
        info_C = job_info(self.query.jobC, make_atp)
        self.job.set_data(JOB_A, info_A)
        self.job.set_data(JOB_B, info_B)
        self.job.set_data(JOB_C, info_C)

    def run(self):
        self.window = JobSelectWindow(self.query.common, self.job)
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    app = MainApplication()
    app.run()
