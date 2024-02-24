import logging
import sys

from PyQt5.QtWidgets import QApplication

from model.config import construct_app_query, construct_base_query
from view.ui_window import JobSelectWindow


class MainApplication:
    def __init__(self, window, logo):
        self.app = QApplication([])
        self.logo = logo
        self.window = window
        self.setup()

    def setup(self):
        logging.basicConfig(
            level=logging.INFO, format="%(levelname)s [%(asctime)s] - %(message)s"
        )
        self.query = construct_base_query()
        self.info = construct_app_query()

    def run(self):
        self.start = self.window(
            self.query, self.info, self.logo, construct_base_query, construct_app_query
        )
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    app = MainApplication(JobSelectWindow, "main_logo.png")
    app.run()
