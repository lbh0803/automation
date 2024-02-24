import logging

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QScrollArea,
                             QVBoxLayout, QWidget)

from controller.controller import (ButtonManager, DataManager, ExecuteManager,
                                   NavigatorManager)
from model.data import DataModel
from view.ui_interface import BaseInputWindow


class JobSelectWindow(BaseInputWindow):
    """
    You can select which job to be executed.
    """

    def __init__(self, query, info, func=None):
        super().__init__()

        self.button_manager = ButtonManager(self)
        self.buttons = {"Exit": self.close, 
                        "Next": self.show_next_window, 
                        "Submit": self.execute_function}
        self.data_manager = DataManager(query, info)
        self.navi_manager = NavigatorManager()
        self.execute_manager = ExecuteManager(func, self)
        self.init_ui()

    def init_ui(self):
        self.img_label = QLabel()
        self.pixmap = QPixmap("logo.png")
        self.pixmap = self.pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        self.img_label.setPixmap(self.pixmap)
        
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.container = QWidget()
        self.container_layout = QVBoxLayout()

        self.layout = QVBoxLayout(self)
        for idx in range(self.data_manager.widget_number):
            self.container_layout.addWidget(self.data_manager.get_widget(idx))

        self.button_layout = QHBoxLayout()

        for button_name in self.buttons:
            self.button_manager.create_button(button_name, self.buttons[button_name])
            self.button_layout.addWidget(self.button_manager.get_button(button_name))

        self.container_layout.addLayout(self.button_layout)
        self.container.setLayout(self.container_layout)
        self.scroll_area.setWidget(self.container)
        self.layout.addWidget(self.img_label)
        self.layout.addWidget(self.scroll_area)

        self.setLayout(self.layout)
        self.show()

    def show_next_window(self):
        self.data_manager.update_info()
        self.data_manager.show_all()
        self.current_job = self.data_manager.info.get_data("job")
        self.next_info = self.data_manager.info.get_data(self.current_job)
        self.next_query = self.next_info.get_data("base_query")
        self.next_func = self.next_info.get_data("base_function")
        logging.info(f"Selected job is {self.current_job}")
        self.navi_manager.show_next_window(
            JobSelectWindow,
            query=self.next_query,
            info=self.next_info,
            func=self.next_func,
        )
        self.navi_manager.next_window = None
        self.hide()

    def execute_function(self):
        self.data_manager.update_info()
        self.data_manager.show_all()
        self.current_job = self.data_manager.info.get_data("job")
        self.base_info = DataModel("BASE")
        self.execute_manager.execute_function(base_info=self.base_info,
                                              user_input=self.data_manager.info, 
                                              callback=self.show_input_window)

    def show_input_window(self):
        self.next_query = self.data_manager.info.get_data(f"{self.current_job}.query_func")(
            self.base_info)
        self.next_func = self.data_manager.info.get_data(f"{self.current_job}.execute_func")
        self.data_manager.save_data()
        logging.info(f"Selected job is {self.current_job}")
        self.navi_manager.show_next_window(
            InputWindow,
            query=self.next_query,
            info=DataModel("INFO"),
            base_info=self.base_info,
            pre_window=self,
            func=self.next_func,
        )
        self.navi_manager.next_window = None
        self.hide()


class InputWindow(BaseInputWindow):
    """
    This is main input window
    You can put detailed data that would be used to execute your job.
    """

    def __init__(self, query, info, base_info, pre_window=None, func=None):
        super().__init__()

        self.button_manager = ButtonManager(self)
        self.buttons = {
            "Back": self.show_pre_window,
            "Next": self.show_next_window,
            "Submit": self.execute_function,
        }
        self.data_manager = DataManager(query, info, base_info)
        self.navi_manager = NavigatorManager(pre_window)
        self.execute_manager = ExecuteManager(func, self)
        self.init_ui()

    def init_ui(self):
        self.img_label = QLabel()
        self.pixmap = QPixmap("logo.png")
        self.pixmap = self.pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio)
        self.img_label.setPixmap(self.pixmap)
        
        self.statusbar_layout = QHBoxLayout()
        self.statusbar_layout.addStretch(1)
        self.statusbar_widget = QWidget()
        self.home_icon = QPushButton()
        self.home_icon.setIcon(QIcon('home_logo.png'))
        self.home_icon.clicked.connect(self.go_home)
        self.statusbar_layout.addWidget(self.home_icon)
        self.statusbar_widget.setLayout(self.statusbar_layout)
        self.statusbar_widget.setFixedHeight(40)
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        self.container = QWidget()
        self.container_layout = QVBoxLayout()
        self.container_layout.setSpacing(20)

        self.layout = QVBoxLayout(self)

        for idx in range(self.data_manager.widget_number):
            self.add_widget2layout(idx)

        self.button_layout = QHBoxLayout()
        for button_name in self.buttons:
            self.button_manager.create_button(button_name, self.buttons[button_name])
            self.button_layout.addWidget(self.button_manager.get_button(button_name))

        if not self.data_manager.query.is_last():
            self.button_manager.enable_control("Submit", False)
            self.button_manager.enable_control("Next", True)
        else:
            self.button_manager.enable_control("Submit", True)
            if not self.data_manager.query.is_repeat_type():
                self.button_manager.enable_control("Next", False)

        self.container_layout.addLayout(self.button_layout)
        self.container.setLayout(self.container_layout)
        self.scroll_area.setWidget(self.container)
        self.layout.addWidget(self.statusbar_widget)
        self.layout.addWidget(self.img_label)
        self.layout.addWidget(self.scroll_area)
        self.setLayout(self.layout)
        self.show()

    def add_widget2layout(self, idx):
        """
        Add widgets to layout,
        partial is needed to fix idx when it is called later.
        """
        widget = self.data_manager.get_widget(idx)
        widget.reset()
        # if isinstance(widget, CheckBoxWidget):
        #     self.on_off_line_edit(idx, 0)
        #     widget.check_box.stateChanged.connect(partial(self.on_off_line_edit, idx))
        self.container_layout.addWidget(widget)

    def on_off_line_edit(self, idx, state):
        """
        This makes line_edits disable or enable
        according to the checkbutton status.
        """
        if state == 2:
            self.data_manager.get_widget(idx + 1).line_edit.setEnabled(True)
            self.data_manager.get_widget(idx + 2).line_edit.setEnabled(True)
        else:
            self.data_manager.get_widget(idx + 1).line_edit.setDisabled(True)
            self.data_manager.get_widget(idx + 2).line_edit.setDisabled(True)

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
            pre_window=self,
            func=self.execute_manager.func,
        )

    def execute_function(self):
        self.data_manager.update_info()
        self.data_manager.show_all()
        self.execute_manager.execute_function(base_info=self.data_manager.base_info, 
                                              user_input=self.data_manager.info)

    def go_home(self):
        pass