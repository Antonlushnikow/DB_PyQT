from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    """Класс окна списка пользователей"""
    def setupUi(self, MainWindow):
        """Описание элементов окна списка пользователей"""
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(414, 446)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.userLbl = QtWidgets.QLabel(self.centralwidget)
        self.userLbl.setGeometry(QtCore.QRect(20, 10, 47, 14))
        self.userLbl.setObjectName("userLbl")
        self.onlineView = QtWidgets.QListWidget(self.centralwidget)
        self.onlineView.setGeometry(QtCore.QRect(20, 70, 181, 301))
        self.onlineView.setObjectName("onlineView")
        self.refreshBtn = QtWidgets.QPushButton(self.centralwidget)
        self.refreshBtn.setGeometry(QtCore.QRect(60, 400, 75, 23))
        self.refreshBtn.setObjectName("refreshBtn")
        self.addBtn = QtWidgets.QPushButton(self.centralwidget)
        self.addBtn.setGeometry(QtCore.QRect(170, 400, 75, 23))
        self.addBtn.setObjectName("addBtn")
        self.rmvBtn = QtWidgets.QPushButton(self.centralwidget)
        self.rmvBtn.setGeometry(QtCore.QRect(270, 400, 91, 23))
        self.rmvBtn.setObjectName("rmvBtn")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 50, 91, 16))
        self.label.setObjectName("label")
        self.contactsView = QtWidgets.QListWidget(self.centralwidget)
        self.contactsView.setGeometry(QtCore.QRect(210, 70, 181, 301))
        self.contactsView.setObjectName("contactsView")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(210, 50, 47, 14))
        self.label_2.setObjectName("label_2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        """Установка стартовых значений элементам окна"""
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.userLbl.setText(_translate("MainWindow", "TextLabel"))
        self.refreshBtn.setText(_translate("MainWindow", "Refresh"))
        self.addBtn.setText(_translate("MainWindow", "Add Contact"))
        self.rmvBtn.setText(_translate("MainWindow", "Remove Contact"))
        self.label.setText(_translate("MainWindow", "Online Users"))
        self.label_2.setText(_translate("MainWindow", "Contacts"))
