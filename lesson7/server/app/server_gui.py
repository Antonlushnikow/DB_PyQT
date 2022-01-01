import threading
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow
from server.app import server_form


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
        list_.setHorizontalHeaderLabels(['Имя Клиента', 'IP Адрес', 'Время подключения'])
        for key, value in list_users.items():
            user = QStandardItem(key)
            user.setEditable(False)
            ip = QStandardItem(value[0])
            ip.setEditable(False)
            time = QStandardItem(str(value[1].replace(microsecond=0)))
            time.setEditable(False)
            list_.appendRow([user, ip, time])
        return list_

    def refresh_online_users(self):
        """Обновляет значения элементов таблицы подключенных пользователей"""
        self.ui.tableView.setModel(self.set_clients_table())

    def start(self):
        """Запускает поток сервера с установленными параметрами"""
        self.server.addr = self.ui.lineEdit.text()
        self.server.port = self.ui.lineEdit_2.text()

        self.ui.label_4.setText('Connected')
        self.ui.connectButton.setDisabled(True)

        threading.Thread(target=self.server.run, daemon=True).start()
