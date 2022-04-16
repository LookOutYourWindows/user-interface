from PyQt5.QtWidgets import QSystemTrayIcon
from PyQt5.QtGui import QIcon

class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        # Set Tray Icon
        self.setIcon(QIcon("icon.ico"))
        self.setVisible(True)
        self.activated.connect(self.onTrayIconActivated)
    
    # Show main window when user double-clicks the tray icon
    def onTrayIconActivated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.parent.show()