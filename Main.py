import sys

from PyQt5.QtCore import QCoreApplication, QThread, QTimer, pyqtSignal, pyqtSlot
from PyQt5.QtGui import *
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QAction, QApplication, QDialog, QFileDialog, \
                            QMainWindow, QMenu, QSystemTrayIcon, QErrorMessage

from components.MainWindow import MainWindow
from components.LoginDialog import LoginDialog
from components.SystemTrayIcon import SystemTrayIcon

SERVER_URL = "http://localhost:8080"

if __name__ == '__main__':
    app = QApplication(sys.argv)

    session = None
    login_dialog = LoginDialog(SERVER_URL)
    if login_dialog.exec_():
        session = login_dialog.session

    if session == None:
        sys.exit()

    main_window = MainWindow(SERVER_URL, session)
    main_window.show()

    # Set Tray System
    app.setQuitOnLastWindowClosed(False)
    tray_icon = SystemTrayIcon(main_window)

    # Creating the options
    menu = QMenu()

    # To open the window
    _open = QAction("Open")
    _open.triggered.connect(main_window.show)
    menu.addAction(_open)

    # To quit the app
    _quit = QAction("Quit")
    _quit.triggered.connect(QCoreApplication.instance().quit)
    menu.addAction(_quit)
    
    # Adding options to system tray
    tray_icon.setContextMenu(menu)

    sys.exit(app.exec())