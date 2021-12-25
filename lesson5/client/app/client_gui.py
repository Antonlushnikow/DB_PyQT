import sys
import threading
from datetime import datetime
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

        self.users.show()
        sleep(0.5)
        self.users.get_online_users()
        self.hide()


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
        self.ui.contactsView.itemDoubleClicked.connect(self.open_chat)
        self.ui.refreshBtn.clicked.connect(self.get_online_users)
        self.ui.addBtn.clicked.connect(self.add_contact)
        self.ui.rmvBtn.clicked.connect(self.del_contact)
        self.chats = []

    def get_online_users(self):
        if self.client.connected:
            self.ui.onlineView.clear()
            self.client.check_online_users()
            sleep(0.5)
            for user in self.client.online_users:
                itm = QListWidgetItem()
                itm.setText(user)
                self.ui.onlineView.insertItem(0, itm)

            self.ui.contactsView.clear()
            self.client.get_contacts_(self.client.name)

            for contact in self.client.contacts:
                itm = QListWidgetItem()
                itm.setText(contact)
                self.ui.contactsView.insertItem(0, itm)

    def open_chat(self, item):
        dst = item.text()

        if dst in [c.dst for c in self.chats]:
            print('Чат существует')
            for c in self.chats:
                if c.dst == dst:
                    c.activateWindow()
                if not c.dst:
                    self.chats.remove(c)
        else:
            chat = ChatWindow(self.login, dst, self.client)

            chat.ui.chatView.clear()

            for message in self.client.get_last_messages_(dst):
                itm = QListWidgetItem()
                itm.setText(f'{message[0]} {message[1]}: {message[2]}')
                chat.ui.chatView.insertItem(0, itm)
                chat.last_item += 1

            sender = threading.Thread(target=chat.run)
            sender.daemon = True
            sender.start()
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(chat.get_messages)
            self.timer.start(1000)

            self.chats.append(chat)

            chat.show()

    def add_contact(self):
        try:
            self.dst = self.ui.onlineView.currentItem().text()
            self.client.add_contact_(self.login, self.dst)
            self.get_online_users()
        except:
            pass

    def del_contact(self):
        try:
            self.dst = self.ui.contactsView.currentItem().text()
            self.client.del_contact_(self.dst)
            self.get_online_users()
        except:
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
        self.ui.userLbl.setText(f'{login} -> {dst}')

    def closeEvent(self, event):
        print('Чат закрыт')
        self.dst = ''
        event.accept()

    def get_messages(self):
        while self.client.inbox:
            sleep(1)
            for msg in self.client.inbox:
                if msg[0] == self.dst:
                    itm = QListWidgetItem()
                    itm.setText(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} {msg[0]}: {msg[1]}')
                    self.ui.chatView.insertItem(self.last_item, itm)
                    self.last_item += 1
                    self.client.inbox.remove(msg)

    def send(self):
        self.msg = self.ui.msgEdit.toPlainText()
        self.ui.msgEdit.setText('')
        itm = MyQListWidgetItem(self.login)
        itm.setText(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} {self.login}: {self.msg}')
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
