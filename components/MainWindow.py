import base64, ctypes, json, os

from datetime import datetime
from requests_toolbelt.multipart import decoder

from PyQt5.QtCore import QCoreApplication, QTimer, QUrl, QFile, QSaveFile, QDir, QIODevice
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.uic import loadUiType
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QtWidgets import QMainWindow

from components.SaveDialog import SaveDialog
from components.AddDialog import AddDialog
from components.utils import show_success_msg, show_error_msg

main_form = loadUiType("./GUI/MainGui.ui")[0]

class MainWindow(QMainWindow, main_form):
    def __init__(self, SERVER_URL, session):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("Look Out Your Windows")
        self.setWindowIcon(QIcon("icon.ico"))
        
        self.SERVER_URL = SERVER_URL
        self.session = session
        self.btn_stop.hide()

        self.nam = QNetworkAccessManager() 
        
        self.btn_add.clicked.connect(self.add_image)
        self.btn_exit.clicked.connect(QCoreApplication.instance().quit)
        self.btn_start.clicked.connect(self.start)
        self.btn_stop.clicked.connect(self.stop)
        self.btn_refresh.clicked.connect(self.refresh)      
        self.lw_images.itemDoubleClicked.connect(self.get_thumbnail)
        self.timer = QTimer(self, interval=90000, timeout=self.set_wallpaper)

        self.get_image_list()  
   
    # Start setting wallpaper
    def add_image(self):
        add_dialog = AddDialog(self.SERVER_URL, self.session)
        if add_dialog.exec_():
            self.refresh()

    def start(self):
        file_names = ["morning", "afternoon", "evening", "night"]

        save_dialog = SaveDialog()
        if save_dialog.exec_():
            self.save_path = save_dialog.save_path
            dest_path = QDir.fromNativeSeparators(self.save_path)
            dest_files = [QDir(dest_path).filePath(file_name + ".jpg") for file_name in file_names]        

        else:
            return

        for dest_file in dest_files:
            if QFile.exists(dest_file):
                QFile.remove(dest_file)
            
        self.files = [QSaveFile(dest_file) for dest_file in dest_files]

        self.get_output_images()
     
    # Stop setting wallpaper
    def stop(self):
        self.btn_start.show()
        self.btn_stop.hide()
        self.timer.stop()

    # Set desktop wallpaper according to time
    def set_wallpaper(self):
        now = datetime.now()
        SPI_SETDESKWALLPAPER = 20
        if 7 <= now.hour < 13:
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, os.path.join(self.save_path, "morning.jpg"), 0)
        elif 13 <= now.hour < 18:
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, os.path.join(self.save_path, "afternoon.jpg"), 0)
        elif 18 <= now.hour < 21:
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, os.path.join(self.save_path, "evening.jpg"), 0)
        else:
            ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, os.path.join(self.save_path, "night.jpg"), 0)


    def refresh(self):
        self.lw_images.clear()
        self.get_image_list()
        return


    def get_image_list(self):
        request = QNetworkRequest(QUrl(self.SERVER_URL + "/api/v1/images"))
        request.setRawHeader("Cookie".encode("UTF-8"), self.session.encode("UTF-8"))

        self.reply_image_list = self.nam.get(request)
        self.reply_image_list.finished.connect(self.handle_image_list)


    def handle_image_list(self):
        er = self.reply_image_list.error()

        if er == QNetworkReply.NoError:
            res_json = json.loads(self.reply_image_list.readAll().data())
            image_list = res_json["fileNames"]
            for image_name in image_list:
                self.lw_images.addItem(image_name)

        else:
            show_error_msg("Cannot load a list of images.")

        if self.reply_image_list:
            self.reply_image_list.deleteLater()


    def get_thumbnail(self):
        base64_image_name = str(base64.b64encode(self.lw_images.currentItem().text().encode("UTF-8")), "UTF-8")
        request = QNetworkRequest(QUrl(self.SERVER_URL + "/api/v1/images/" + base64_image_name + "/thumbnail"))
        request.setRawHeader("Cookie".encode("UTF-8"), self.session.encode("UTF-8"))

        self.reply_thumbnail = self.nam.get(request)
        self.reply_thumbnail.finished.connect(self.handle_thumbnail)


    def handle_thumbnail(self):
        er = self.reply_thumbnail.error()

        if er == QNetworkReply.NoError:
            pixmap = QPixmap()
            pixmap.loadFromData(self.reply_thumbnail.readAll())
            pixmap = pixmap.scaled(self.lbl_image.size())
            self.lbl_image.setPixmap(pixmap)
                        
        else:
            show_error_msg("Cannot load the image.")

        if self.reply_thumbnail:
            self.reply_thumbnail.deleteLater()


    def get_output_images(self):
        base64_image_name = str(base64.b64encode(self.lw_images.currentItem().text().encode("UTF-8")), "UTF-8")
        request = QNetworkRequest(QUrl(self.SERVER_URL + "/api/v1/images/" + base64_image_name + "/outputs"))
        request.setRawHeader("Cookie".encode("UTF-8"), self.session.encode("UTF-8"))

        self.reply_output_images = self.nam.get(request)
        self.reply_output_images.finished.connect(self.handle_output_images)
        

    def handle_output_images(self):
        er = self.reply_output_images.error()
        
        if er == QNetworkReply.NoError:
            content_type = self.reply_output_images.header(QNetworkRequest.ContentTypeHeader)
            multipart_data = self.reply_output_images.readAll().data()
            for part, file in zip(decoder.MultipartDecoder(multipart_data, content_type).parts, self.files):
                if file.open(QIODevice.WriteOnly):
                    file.write(part.content)
                    file.commit()

            if self.reply_output_images:
                self.reply_output_images.deleteLater()
        
            self.btn_start.hide()
            self.btn_stop.show()
            self.set_wallpaper()
            self.timer.start()

        else:
            # import pdb; pdb.set_trace()
            show_error_msg("Cannot load the output images.")
    

        