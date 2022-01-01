import sys
import threading
from datetime import datetime
from pathlib import Path
from time import sleep

from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidgetItem
from PyQt5 import QtCore

from client.app.ui import client_register, client_connect, client_users, client_chat, client_start


class MyQListWidgetItem(QListWidgetItem):
    def __init__(self, name):
        super().__init__()
        self.name = name


class StartWindow(QMainWindow):
    def __init__(self, client):
        QMainWindow.__init__(self)
        self.ui = client_start.Ui_MainWindow()
        self.ui.setupUi(self)
        self.main_window = None
        self.client = client
        self.ui.connectBtn.clicked.connect(self.connect)

    def connect(self):
        try:
            threading.Thread(target=self.client.launch, daemon=True).start()
        except:
            print('Нет соединения с сервером')
        else:
            self.main_window = MainWindow(self.client)
            self.main_window.show()
            self.hide()


class MainWindow(QMainWindow):
    def __init__(self, client: object) -> object:
        QMainWindow.__init__(self)
        self.ui = client_connect.Ui_MainWindow()
        self.ui.setupUi(self)
        self.client = client
        self.ui.loginBtn.clicked.connect(self.connect)
        self.ui.regBtn.clicked.connect(self.register)

        self.register = None
        self.user_window = None
        self.passwd = None
        self.chat = None

    def connect(self):
        self.client.name = self.ui.loginEdit.text()
        self.client.passwd = self.ui.passwdEdit.text()

        self.client.login()
        # threading.Thread(target=self.client.login, daemon=True).start()

        sleep(1)
        if self.client.presence_response == '200':
            self.user_window = UsersWindow(self.client)

            self.user_window.show()
            sleep(0.5)
            self.user_window.get_online_users()
            self.hide()
        elif self.client.presence_response == '410':
            self.ui.label_err.setText("Login is incorrect")
        elif self.client.presence_response == '420':
            self.ui.label_err.setText("Password is incorrect")
        elif self.client.presence_response == '503':
            self.ui.label_err.setText("Server is not available")
        else:
            self.ui.label_err.setText("Server Error")

    def register(self):
        self.register = RegisterWindow(self.client)
        self.register.show()


class RegisterWindow(QMainWindow):
    def __init__(self, client, parent=None):
        super(RegisterWindow, self).__init__(parent)
        self.ui = client_register.Ui_MainWindow()
        self.ui.setupUi(self)
        self.login = self.ui.loginEdit.text()
        self.client = client
        self.passwd = None
        self.passwd2 = None
        self.ui.regBtn.clicked.connect(self.register)

    def register(self):
        login = self.ui.loginEdit.text()
        passwd = self.ui.passwdEdit.text()
        passwd2 = self.ui.passwd2Edit.text()
        if passwd == passwd2:
            self.client.register(login, passwd)
        else:
            self.ui.label_err.setText("Passwords are not matched")
        sleep(1)
        if self.client.presence_response == '211':
            self.close()
        elif self.client.presence_response == '444':
            self.ui.label_err.setText("Login is busy")


class UsersWindow(QMainWindow):
    def __init__(self, client, parent=None):
        super(UsersWindow, self).__init__(parent)
        self.ui = client_users.Ui_MainWindow()
        self.ui.setupUi(self)
        self.client = client
        self.login = client.name
        self.ui.userLbl.setText(self.login)
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
            print(self.client.online_users)
            for user in self.client.online_users.keys():
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
        dst = self.client.online_users[item.text()]
        contact = item.text()

        if dst in [c.dst for c in self.chats]:
            print('Чат существует')
            for c in self.chats:
                if c.dst == dst:
                    c.activateWindow()
                if not c.dst:
                    self.chats.remove(c)
        else:
            chat = ChatWindow(self.login, contact, dst, self.client)

            chat.ui.chatView.clear()

            for message in self.client.get_last_messages_(contact):
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
    def __init__(self, login, contact, dst, client, parent=None):
        super(ChatWindow, self).__init__(parent)
        self.ui = client_chat.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.sendBtn.clicked.connect(self.send)
        self.login = login
        self.client = client
        self.contact = contact
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
        print(self.client.inbox)
        while self.client.inbox:
            sleep(1)
            for msg in self.client.inbox:
                if msg[0] == self.contact:
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
                self.client.send_gui_message(self.client.client_socket, self.login, self.contact, self.dst, self.msg)
                self.need_send = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
