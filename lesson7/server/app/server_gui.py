import threading

from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow
import server_form


class ServerGUI(QMainWindow):
    def __init__(self, server):
        QMainWindow.__init__(self)
        self.ui = server_form.Ui_Dialog()
        self.ui.setupUi(self)
        self.server = server

        self.ui.connectButton.clicked.connect(self.thread)
        self.ui.refreshButton.clicked.connect(self.refresh_online_users)

    def refresh_online_users(self):
        self.ui.tableView.setModel(self.set_clients_table())

    def thread(self):
        self.ui.label_4.setText('Connected')
        self.ui.connectButton.setDisabled(True)
        addr = self.ui.lineEdit.text()
        port = self.ui.lineEdit_2.text()
        threading.Thread(target=self.start, args=(addr, port), daemon=True).start()

    def start(self, addr, port):
        self.server.addr = addr
        self.server.port = port
        self.server.run()

    def set_clients_table(self):
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
