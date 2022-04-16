import os

from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import QDialog, QFileDialog

save_form = loadUiType("./GUI/SaveGui.ui")[0]

class SaveDialog(QDialog, save_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle('Look Out Your Windows')
        
        self.save_path = None
        if os.path.exists("./LookOutYourWindows_SavePath.txt"):
            with open("./LookOutYourWindows_SavePath.txt", "r") as f:
                self.save_path = f.readline()

        if self.save_path: 
            self.lineedit_savepath.setText(self.save_path)
            self.chkbox_save.toggle() # Set check box on

        self.btn_browse.clicked.connect(self.browse_dir)
        self.btn_ok.clicked.connect(self.ok)
        self.btn_cancel.clicked.connect(self.cancel)

    # Browse save directory
    def browse_dir(self):
        save_path = QFileDialog.getExistingDirectory(self, 'Open a Folder', './')   # Must be not self.save path
        self.lineedit_savepath.setText(save_path)                                   # to press 'cancel' returns None

    # Click OK btn
    def ok(self):
        self.save_path = self.lineedit_savepath.text()

        if self.chkbox_save.isChecked():
            if self.save_path:
                with open("./LookOutYourWindows_SavePath.txt", "w") as f:
                    f.write(self.save_path)
        else:
            if os.path.exists("./LookOutYourWindows_SavePath.txt"):
                os.remove("./LookOutYourWindows_SavePath.txt")

        self.accept()

    def cancel(self):
        self.close()