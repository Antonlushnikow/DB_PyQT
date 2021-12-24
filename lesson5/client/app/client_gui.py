import sys
import threading
from pathlib import Path
from time import sleep, time

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QListWidgetItem
from PyQt5 import QtCore

import client_connect
import client_chat
import client_users

base_dir = str(Path(__file__).parent.parent.resolve())
print(base_dir)
if base_dir not in sys.path:
    sys.path.append(base_dir)

from common.utils import get_message, send_message
from common.constants import DEFAULT_PORT, DEFAULT_HOST, ACTION, TIME, RESPONSE, TYPE, ACCOUNT_NAME, MESSAGE, \
    SENDER, DESTINATION, USER_LIST, CONTACT_LIST, CONTACT_NAME


class MyQListWidgetItem(QListWidgetItem):
    def __init__(self, name):
        super().__init__()
        self.name = name


class MainWindow(QMainWindow):
    def __init__(self, client):
        QMainWindow.__init__(self)
        self.ui = client_connect.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.connectBtn.clicked.connect(self.connect)
        self.client = client
        self.login = None
        self.chat = None

    def connect(self):
        self.login = self.ui.loginEdit.text()
        self.client.name = self.login
        threading.Thread(target=self.client.launch, daemon=True).start()
        self.users = UsersWindow(self.login, self.client)
        # sender1 = threading.Thread(target=self.users.get_online_users)
        # sender1.daemon = True
        # sender1.start()

        self.users.show()
        self.hide()

        # self.timer = QtCore.QTimer()
        # self.timer.timeout.connect(self.users.get_online_users)
        # self.timer.start(1000)


        # if self.client.connected:
        #
        #     self.client.check_online_users()
        #     print(self.client.online_users)
        #     itm = QListWidgetItem()
        #     itm.setText(f'{self.client.online_users}')
        #     self.ui.chatView.insertItem(0, itm)


class UsersWindow(QMainWindow):
    def __init__(self, login, client, parent=None):
        super(UsersWindow, self).__init__(parent)
        self.ui = client_users.Ui_MainWindow()
        self.ui.setupUi(self)
        self.login = login
        self.ui.userLbl.setText(self.login)
        self.client = client
        self.msg = None
        self.address = None
        self.ui.onlineView.itemDoubleClicked.connect(self.open_chat)
        self.ui.refreshBtn.clicked.connect(self.get_online_users)
        self.ui.addBtn.clicked.connect(self.add_contact)

    def get_online_users(self):
        if self.client.connected:
            self.ui.onlineView.clear()
            self.client.check_online_users()

            for user in self.client.online_users:
                itm = QListWidgetItem()
                itm.setText(user)
                self.ui.onlineView.insertItem(0, itm)

    def open_chat(self, item):
        self.dst = item.text()
        self.chat = ChatWindow(self.login, self.dst, self.client)

        sender = threading.Thread(target=self.chat.run)
        sender.daemon = True
        sender.start()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.chat.get_messages)
        self.timer.start(1000)

        self.chat.show()

    def add_contact(self):
        pass



class ChatWindow(QMainWindow):
    def __init__(self, login, dst, client, parent=None):
        super(ChatWindow, self).__init__(parent)
        self.ui = client_chat.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.sendBtn.clicked.connect(self.send)
        self.login = login
        self.client = client
        self.msg = None
        self.dst = dst
        self.need_send = False
        self.last_item = 0

    def get_messages(self):
        while self.client.inbox:
            sleep(1)
            for msg in self.client.inbox:
                if msg[0] == self.dst:
                    itm = QListWidgetItem()
                    itm.setText(f'{msg[0]}: {msg[1]}')
                    self.ui.chatView.insertItem(self.last_item, itm)
                    self.last_item += 1
                    self.client.inbox.remove(msg)

    def send(self):
        self.msg = self.ui.msgEdit.toPlainText()
        self.ui.msgEdit.setText('')
        itm = MyQListWidgetItem(self.login)
        itm.setText(f'{self.login}: {self.msg}')
        self.ui.chatView.insertItem(self.last_item, itm)
        self.last_item += 1
        self.need_send = True

    def run(self):
        while True:
            sleep(1)
            if self.need_send:
                self.client.send_gui_message(self.client.client_socket, self.login, self.dst, self.msg)
                self.need_send = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
