import threading
from time import sleep

from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow
from app import server_form


class ServerGUI(QMainWindow):
    """Класс окна GUI сервера"""
    def __init__(self, server):
        QMainWindow.__init__(self)
        self.ui = server_form.Ui_Dialog()
        self.ui.setupUi(self)
        self.server = server

        self.ui.connectButton.clicked.connect(self.start)
        self.ui.refreshButton.clicked.connect(self.refresh_online_users)

    def set_clients_table(self):
        """Возвращает список активных пользователей"""
        list_users = self.server.active_clients
        list_ = QStandardItemModel()
        list_.setHorizontalHeaderLabels(['Имя Клиента', 'IP Адрес'])
        for key, value in list_users.items():
            user = QStandardItem(value)
            user.setEditable(False)
            ip = QStandardItem(f'{key[:-5]}:{key[-5:]}')
            ip.setEditable(False)
            list_.appendRow([user, ip])
        return list_

    def refresh_online_users(self):
        """Обновляет значения элементов таблицы подключенных пользователей"""
        self.ui.tableView.setModel(self.set_clients_table())

    def start(self):
        """Запускает поток сервера с установленными параметрами"""
        try:
            self.server.addr = self.ui.lineEdit.text()
            self.server.port = int(self.ui.lineEdit_2.text())
        except:
            self.ui.label_4.setText('Type Error')
        else:
            self.ui.label_4.setText('Connected')
            self.ui.connectButton.setDisabled(True)
            sleep(1)
            threading.Thread(target=self.server.run, daemon=True).start()