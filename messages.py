from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox

ERROR_MSG = 0
INFO_MSG = 1
YES_NO_BOX = 4

def display_message(message: str, title: str, message_type: int):
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(message)

    if message_type == ERROR_MSG:
        msg.setIcon(QMessageBox.Icon.Critical)
    elif message_type == INFO_MSG:
        msg.setIcon(QMessageBox.Icon.Information)

    msg.exec()

def display_option_message(message: str, title: str, type_of_dialog=None) -> bool:
    msg = QMessageBox()
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

    result = msg.exec()
    return result == QMessageBox.StandardButton.Yes
