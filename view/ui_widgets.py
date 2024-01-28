from abc import abstractmethod
from PyQt5.QtWidgets import (
    QLineEdit,
    QPlainTextEdit,
    QComboBox,
    QCheckBox,
    QVBoxLayout,
)
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
        return self.line_edit.text()

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
        return self.combo_box.currentText()

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


class PlainTextEditWidget(BaseInputWidget):
    def __init__(self, label_text):
        super().__init__(label_text)

        self.line_edit = QPlainTextEdit(self)

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.line_edit)
        self.setLayout(self.layout)

    def get_value(self):
        return self.line_edit.toPlainText().split("\n")

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
