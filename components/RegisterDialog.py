import re, json

from PyQt5.uic import loadUiType
from PyQt5.QtCore import QJsonDocument, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtWidgets import QDialog, QMessageBox

from components.utils import show_success_msg, show_error_msg

register_form = loadUiType("./GUI/RegisterGui.ui")[0]

class RegisterDialog(QDialog, register_form):
    def __init__(self, SERVER_URL):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon("icon.ico"))
        self.setWindowTitle('Look Out Your Windows')

        self.SERVER_URL = SERVER_URL

        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(self.handle_reply)

        self.btn_register.clicked.connect(self.register)
        self.btn_exit.clicked.connect(self.exit)

 
    def register(self):
        request = QNetworkRequest(QUrl(self.SERVER_URL + "/api/v1/users"))
        request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
        body = {
            "username": self.lineedit_id.text(),
            "password": self.lineedit_password.text(),
            "email":    self.lineedit_email.text(),
        }

        try:
            self.validate_body(body)
        except ValueError as ex:
            show_error_msg(str(ex))
            return

        body = QJsonDocument(body)
        self.nam.post(request, body.toJson())


    def handle_reply(self, reply):
        er = reply.error()

        if er == QNetworkReply.NoError:
            show_success_msg("Your account has been created successfully.")
            self.accept()

        else:
            res_json = json.loads(reply.readAll().data())
            show_error_msg(str(res_json["status"]) + " : " + res_json["message"])


    def exit(self):
        self.close()


    def validate_body(self, body):
        username_regex = r'\b[A-Za-z0-9._%+-]+\b'
        if len(body["username"]) <= 5 :
            self.lineedit_id.setText("")
            raise ValueError("ID must be longer than 5 characters.")

        if not re.fullmatch(username_regex, body["username"]):
            self.lineedit_id.setText("")
            raise ValueError("Invalid ID.")

        email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not re.fullmatch(email_regex, body["email"]):
            self.lineedit_email.setText("")
            raise ValueError("Invalid E-mail.")

        if len(body["password"]) <= 7:
            self.lineedit_password.setText("")
            raise ValueError("Password must be longer than 7 characters.")

        if body["password"] != self.lineedit_confirm.text():
            raise ValueError("The passwords didn't match.")