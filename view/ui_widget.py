from abc import abstractmethod

from PyQt5.QtWidgets import (QCheckBox, QComboBox, QLineEdit, QPlainTextEdit, QVBoxLayout)

from view.ui_interface import BaseInputWidget


class LineEditWidget(BaseInputWidget):

    def __init__(self, label_text):
        super().__init__(label_text)

        self.line_edit = QLineEdit(self)
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.line_edit)
        self.setLayout(self.layout)

    def get_value(self):
        return self.line_edit.text().strip()

    def reset(self):
        self.line_edit.setText("")

    def save(self):
        self.log = self.get_value()

    def restore(self):
        self.line_edit.setText(self.log)

    def __deepcopy__(self, memo):
        new_widget = LineEditWidget(self.label.text())
        new_widget.line_edit.setText(self.line_edit.text())
        memo[id(self)] = new_widget
        return new_widget


class ComboBoxWidget(BaseInputWidget):

    def __init__(self, label_text, *items):
        self.items = items
        super().__init__(label_text)

        self.combo_box = QComboBox(self)
        self.combo_box.addItems(self.items)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.combo_box)
        self.setLayout(self.layout)

    def get_value(self):
        return self.combo_box.currentText().strip()

    def reset(self):
        self.combo_box.setCurrentIndex(0)

    def save(self):
        self.log = self.combo_box.currentIndex()

    def restore(self):
        self.combo_box.setCurrentIndex(self.log)

    def __deepcopy__(self, memo):
        new_widget = ComboBoxWidget(self.label.text(), *self.items)
        new_widget.combo_box.setCurrentIndex(self.combo_box.currentIndex())
        memo[id(self)] = new_widget
        return new_widget


class CheckBoxWidget(BaseInputWidget):

    def __init__(self, label_text, item):
        super().__init__(label_text)

        self.item = item
        self.check_box = QCheckBox(self)
        self.check_box.setText(self.item)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.check_box)
        self.setLayout(self.layout)

    def get_value(self):
        return self.check_box.isChecked()

    def reset(self):
        self.check_box.setChecked(False)

    def save(self):
        self.log = self.get_value()

    def restore(self):
        self.check_box.setChecked(self.log)

    def __deepcopy__(self, memo):
        new_widget = CheckBoxWidget(self.label.text(), self.item)
        new_widget.check_box.setChecked(self.check_box.isChecked())
        memo[id(self)] = new_widget
        return new_widget


class MultiCheckBoxWidget(BaseInputWidget):

    def __init__(self, label_text, *items):
        super().__init__(label_text)

        self.items = items
        self.check_box_list = list()
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label)

        for item in self.items:
            self.check_box = QCheckBox(self)
            self.check_box.setText(item)
            self.check_box_list.append(self.check_box)
            self.layout.addWidget(self.check_box)

        self.setLayout(self.layout)

    def get_value(self):
        return_list = list()
        for check_box in self.check_box_list:
            if check_box.isChecked():
                return_list.append(check_box.text().strip())
        return return_list

    def reset(self):
        for check_box in self.check_box_list:
            check_box.setChecked(False)

    def save(self):
        self.log = [False] * len(self.items)
        for idx in range(len(self.items)):
            if self.check_box_list[idx].isChecked():
                self.log[idx] = True

    def restore(self):
        for idx in range(len(self.items)):
            self.check_box_list[idx].setChecked(self.log[idx])

    def __deepcopy__(self, memo):
        new_widget = MultiCheckBoxWidget(self.label.text(), *self.items)
        for idx in range(len(self.items)):
            new_widget.check_box_list[idx].setChecked(self.check_box_list[idx].isChecked())
        memo[id(self)] = new_widget
        return new_widget


class PlainTextEditWidget(BaseInputWidget):

    def __init__(self, label_text):
        super().__init__(label_text)

        self.line_edit = QPlainTextEdit(self)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.line_edit)
        self.setLayout(self.layout)

    def get_value(self):
        return self.line_edit.toPlainText().strip().split("\n")

    def reset(self):
        self.line_edit.setPlainText("")

    def save(self):
        self.log = self.line_edit.toPlainText()

    def restore(self):
        self.line_edit.setPlainText(self.log)

    def __deepcopy__(self, memo):
        new_widget = PlainTextEditWidget(self.label.text())
        new_widget.line_edit.setPlainText(self.line_edit.toPlainText())
        memo[id(self)] = new_widget
        return new_widget
