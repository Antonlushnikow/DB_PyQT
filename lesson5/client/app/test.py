import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QListWidgetItem
from PyQt5 import QtCore

import client_connect
import client_chat


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.ui = client_connect.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.connectBtn.clicked.connect(self.connect)
        self.login = None
        self.chat = None

    def connect(self):
        self.login = self.ui.loginEdit.text()
        self.chat = ChatWindow(self.login)
        self.chat.show()


class ChatWindow(QMainWindow):
    def __init__(self, login, parent=None):
        super(ChatWindow, self).__init__(parent)
        self.ui = client_chat.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.sendBtn.clicked.connect(self.send)
        self.login = login
        self.msg = None

    def send(self):
        self.msg = self.ui.msgEdit.toPlainText()
        self.ui.msgEdit.setText('')
        itm = QListWidgetItem()
        itm.setText(f'{self.login}: {self.msg}')
        self.ui.chatView.insertItem(0, itm)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
