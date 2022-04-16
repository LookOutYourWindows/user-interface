from PyQt5.QtWidgets import QMessageBox

def show_error_msg(msg):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setText("Error")
    msg_box.setInformativeText(msg)
    msg_box.setWindowTitle("Error")
    msg_box.exec_()

def show_success_msg(msg):
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setText("Success")
    msg_box.setInformativeText(msg)
    msg_box.setWindowTitle("Success")
    msg_box.exec_()

def get_file_name(file_path):
    index = file_path.rfind("/")
    if index == -1:
        return ""
    return file_path[index + 1:]

def extract_ext(file_name):
    index = file_name.rfind(".")
    if index == -1:
        return ""
    return file_name[index + 1:]