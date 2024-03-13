import gc
import logging
import sys
import tracemalloc
from memory_profiler import profile

from controller.utility import SafeApplication, exception_hook
from model.config import construct_app_query, construct_base_query
from view.ui_window import JobSelectWindow


class MainApplication:
    def __init__(self, window, logo):
        self.app = SafeApplication([])
        self.logo = logo
        self.window = window
        self.setup()

    def setup(self):
        logging.basicConfig(
            level=logging.INFO, format="%(levelname)s [%(asctime)s] - %(message)s"
        )
        self.query = construct_base_query()
        self.info = construct_app_query()

    @profile
    def run(self):
        self.start = self.window(
            self.query, self.info, self.logo, construct_base_query, construct_app_query
        )
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    # gc.set_debug(gc.DEBUG_LEAK)
    gc.collect()
    sys.excepthook = exception_hook
    app = MainApplication(JobSelectWindow, "main_logo.png")
    # tracemalloc.start()
    app.run()
