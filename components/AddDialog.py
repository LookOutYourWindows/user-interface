from audioop import mul
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply, QHttpMultiPart, QHttpPart
from PyQt5.QtCore import QUrl, QVariant, QFile, QIODevice
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.uic import loadUiType
from PyQt5.QtWidgets import  QFileDialog, QDialog

from components.utils import show_error_msg, show_success_msg, extract_ext, get_file_name

add_form = loadUiType("./GUI/AddGui.ui")[0] # Main Window GUI

# Main Window
class AddDialog(QDialog, add_form):
    def __init__(self, SERVER_URL, session):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Look Out Your Windows")
        self.setWindowIcon(QIcon("icon.ico"))

        self.SERVER_URL = SERVER_URL
        self.session = session
        self.nam = QNetworkAccessManager()

        self.btn_browse.clicked.connect(self.browse_files)
        self.btn_send.clicked.connect(self.send)
        self.btn_exit.clicked.connect(self.exit)

    # Open file explorer to browse image and set file path
    def browse_files(self):
        self.image_path = QFileDialog.getOpenFileName(self, "Open File", './', "Images (*.png *.jpg *.jpeg)")[0]
        if not self.image_path:
            self.image_name = None
            return

        self.image_name = get_file_name(self.image_path)
        self.lineedit_filepath.setText(self.image_path)
        self.load_image_from_file(self.image_path)


    # Load select image and show it
    def load_image_from_file(self, filepath):
        pixmap = QPixmap()
        pixmap.load(filepath) 
        pixmap = pixmap.scaled(self.lbl_image.size())
        self.lbl_image.setPixmap(pixmap)


    def send(self):
        multipart = QHttpMultiPart(QHttpMultiPart.FormDataType)
        
        image_part = QHttpPart()
        image_part.setHeader(QNetworkRequest.ContentTypeHeader, 
                             QVariant("image/" + extract_ext(self.image_path)))
        image_part.setHeader(QNetworkRequest.ContentDispositionHeader, 
                             QVariant(f'form-data; name="MultipartFile"; filename="{self.image_name}"'))

        image_file = QFile(self.image_path)
        image_file.open(QIODevice.ReadOnly)
        if image_file.size() > 5000000: # If the image is arger than 5MB
            show_error_msg("An image must be smaller than 5MB.")
            return
            
        image_part.setBodyDevice(image_file)
        image_file.setParent(multipart)
        multipart.append(image_part)
    
        request = QNetworkRequest(QUrl(self.SERVER_URL + "/api/v1/images"))
        request.setRawHeader("Cookie".encode("UTF-8"), self.session.encode("UTF-8"))

        self.reply_send = self.nam.post(request, multipart)
        self.reply_send.finished.connect(self.handle_reply_send)
        multipart.setParent(self.reply_send)


    def handle_reply_send(self):
        er = self.reply_send.error()

        if er == QNetworkReply.NoError:
            show_success_msg("The image has been sent successfully.")
            self.accept()
        else:
            show_error_msg("Failed to send the image. Try again.")

    def exit(self):
        self.close()