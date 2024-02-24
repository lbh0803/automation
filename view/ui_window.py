import logging

from controller.controller import (
    ButtonManager,
    DataManager,
    ExecuteManager,
    NavigatorManager,
)
from model.data import DataModel
from view.ui_interface import BaseInputWindow


class JobSelectWindow(BaseInputWindow):
    """
    You can select which job to be executed.
    """

    def __init__(self, query, info, logo, query_init, info_init, func=None):
        self.logo = logo
        self.query_init = query_init
        self.info_init = info_init
        self.button_manager = ButtonManager(self)
        self.buttons = {
            "Back": self.go_home,
            "Next": self.show_next_window,
            "Submit": self.execute_function,
        }
        self.data_manager = DataManager(query, info)
        self.navi_manager = NavigatorManager()
        self.execute_manager = ExecuteManager(func, self)
        super().__init__(self.logo)

    def fill_scroll_area(self):
        for idx in range(self.data_manager.widget_number):
            self.add_widget2layout(idx)

    def fill_button_area(self):
        for button_name in self.buttons:
            self.button_manager.create_button(button_name, self.buttons[button_name])
            self.button_layout.addWidget(self.button_manager.get_button(button_name))
        self.container_layout.addLayout(self.button_layout)

    def button_control(self):
        if self.logo == "main_logo.png":
            self.button_manager.enable_control("Submit", False)
            self.button_manager.enable_control("Back", False)
        else:
            self.button_manager.enable_control("Next", False)

    def add_widget2layout(self, idx):
        widget = self.data_manager.get_widget(idx)
        widget.reset()
        self.container_layout.addWidget(widget)

    def show_next_window(self):
        self.data_manager.update_info()
        self.data_manager.show_all()
        self.current_job = self.data_manager.info.get_data("job")
        self.next_info = self.data_manager.info.get_data(self.current_job)
        self.next_query = self.next_info.get_data("base_query")
        self.next_func = self.next_info.get_data("base_function")
        self.next_logo = self.next_info.get_data("logo")
        logging.info(f"Selected job is {self.current_job}")
        self.navi_manager.show_next_window(
            JobSelectWindow,
            query=self.next_query,
            info=self.next_info,
            logo=self.next_logo,
            query_init=self.query_init,
            info_init=self.info_init,
            func=self.next_func,
        )
        self.navi_manager.next_window = None
        self.hide()

    def execute_function(self):
        self.data_manager.update_info()
        self.data_manager.show_all()
        self.current_job = self.data_manager.info.get_data("job")
        self.base_info = DataModel("BASE")
        self.execute_manager.execute_function(
            base_info=self.base_info,
            user_input=self.data_manager.info,
            callback=self.show_input_window,
        )

    def show_input_window(self):
        self.next_query = self.data_manager.info.get_data(
            f"{self.current_job}.query_func"
        )(self.base_info)
        self.next_func = self.data_manager.info.get_data(
            f"{self.current_job}.execute_func"
        )
        self.data_manager.save_data()
        logging.info(f"Selected job is {self.current_job}")
        self.navi_manager.show_next_window(
            InputWindow,
            query=self.next_query,
            info=DataModel("INFO"),
            base_info=self.base_info,
            logo=self.logo,
            query_init=self.query_init,
            info_init=self.info_init,
            pre_window=self,
            func=self.next_func,
        )
        self.navi_manager.next_window = None
        self.hide()

    def go_home(self):
        self.first_query = self.query_init()
        self.first_info = self.info_init()
        self.navi_manager.go_home_window(
            JobSelectWindow,
            query=self.first_query,
            info=self.first_info,
            logo="main_logo.png",
            query_init=self.query_init,
            info_init=self.info_init,
        )
        self.close_by_navigator = True
        self.close()


class InputWindow(BaseInputWindow):
    """
    This is main input window
    You can put detailed data that would be used to execute your job.
    """

    def __init__(
        self,
        query,
        info,
        base_info,
        logo,
        query_init,
        info_init,
        pre_window=None,
        func=None,
    ):
        self.logo = logo
        self.query_init = query_init
        self.info_init = info_init
        self.button_manager = ButtonManager(self)
        self.buttons = {
            "Back": self.show_pre_window,
            "Next": self.show_next_window,
            "Submit": self.execute_function,
        }
        self.data_manager = DataManager(query, info, base_info)
        self.navi_manager = NavigatorManager(pre_window)
        self.execute_manager = ExecuteManager(func, self)
        super().__init__(self.logo)

    def fill_scroll_area(self):
        for idx in range(self.data_manager.widget_number):
            self.add_widget2layout(idx)

    def fill_button_area(self):
        for button_name in self.buttons:
            self.button_manager.create_button(button_name, self.buttons[button_name])
            self.button_layout.addWidget(self.button_manager.get_button(button_name))
        self.container_layout.addLayout(self.button_layout)

    def button_control(self):
        if not self.data_manager.query.is_last():
            self.button_manager.enable_control("Submit", False)
            self.button_manager.enable_control("Next", True)
        else:
            self.button_manager.enable_control("Submit", True)
            if not self.data_manager.query.is_repeat_type():
                self.button_manager.enable_control("Next", False)

    def add_widget2layout(self, idx):
        widget = self.data_manager.get_widget(idx)
        widget.reset()
        self.container_layout.addWidget(widget)

    def show_pre_window(self):
        self.data_manager.save_data()
        self.hide()
        self.navi_manager.show_pre_window()

    def show_next_window(self):
        self.data_manager.save_data()
        repeat_break = self.data_manager.update_info()
        self.data_manager.query.up_cnt()
        self.hide()
        if self.navi_manager.next_window and not repeat_break:
            self.navi_manager.next_window.data_manager.restore_data()
            self.navi_manager.next_window.data_manager.set_info(self.data_manager.info)
            self.navi_manager.next_window.data_manager.copy_pre_info()
        else:
            self.navi_manager.next_window = None
        self.data_manager.copy_next_query()
        self.navi_manager.show_next_window(
            InputWindow,
            query=self.data_manager.next_query,
            info=self.data_manager.info,
            base_info=self.data_manager.base_info,
            logo=self.logo,
            query_init=self.query_init,
            info_init=self.info_init,
            pre_window=self,
            func=self.execute_manager.func,
        )

    def execute_function(self):
        self.data_manager.update_info()
        self.data_manager.show_all()
        self.execute_manager.execute_function(
            base_info=self.data_manager.base_info, user_input=self.data_manager.info
        )

    def go_home(self):
        self.first_query = self.query_init()
        self.first_info = self.info_init()
        self.navi_manager.go_home_window(
            JobSelectWindow,
            query=self.first_query,
            info=self.first_info,
            logo="main_logo.png",
            query_init=self.query_init,
            info_init=self.info_init,
        )
        self.close_by_navigator = True
        self.close()
