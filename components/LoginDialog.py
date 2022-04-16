import base64

from PyQt5.uic import loadUiType
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QUrl
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtWidgets import QDialog

from components.RegisterDialog import RegisterDialog
from components.utils import show_error_msg, show_success_msg

login_form = loadUiType("./GUI/LoginGui.ui")[0]

class LoginDialog(QDialog, login_form):
    def __init__(self, SERVER_URL):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QIcon("icon.ico"))
        self.setWindowTitle('Look Out Your Windows')

        self.SERVER_URL = SERVER_URL

        self.nam = QNetworkAccessManager()
        self.nam.finished.connect(self.handle_reply)
        self.btn_login.clicked.connect(self.login)
        self.btn_register.clicked.connect(self.register)


    def login(self):
        request = QNetworkRequest(QUrl(self.SERVER_URL + "/api/v1/login"))
        
        auth_string = (self.lineedit_id.text() + ":" + self.lineedit_password.text()).encode("UTF-8")
        request.setRawHeader("Authorization".encode("UTF-8"), 
                             "Basic ".encode("UTF-8") + base64.b64encode(auth_string))

        self.nam.post(request, None)


    def handle_reply(self, reply):
        er = reply.error()
        if er == QNetworkReply.NoError:
            self.session = str(reply.rawHeader(b"Set-Cookie"), "UTF-8")
            self.accept()

        else:
            show_error_msg("Invalid\nID or Password.")
        
    def register(self):
        register_dialog = RegisterDialog(self.SERVER_URL)
        register_dialog.exec_()
