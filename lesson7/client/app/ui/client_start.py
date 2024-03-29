from PyQt5 import QtCore, QtWidgets


class Ui_MainWindow(object):
    """Класс стартового окна"""
    def setupUi(self, MainWindow):
        """Описание элементов стартового окна"""
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(247, 148)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(30, 20, 47, 14))
        self.label.setObjectName("label")

        self.addrEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.addrEdit.setGeometry(QtCore.QRect(92, 20, 121, 20))
        self.addrEdit.setObjectName("addrEdit")

        self.portEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.portEdit.setGeometry(QtCore.QRect(92, 50, 121, 20))
        self.portEdit.setObjectName("portEdit")

        self.connectBtn = QtWidgets.QPushButton(self.centralwidget)
        self.connectBtn.setGeometry(QtCore.QRect(30, 80, 75, 23))
        self.connectBtn.setObjectName("connectBtn")

        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(30, 50, 47, 14))
        self.label_2.setObjectName("label_2")

        self.label_err = QtWidgets.QLabel(self.centralwidget)
        self.label_err.setGeometry(QtCore.QRect(30, 110, 97, 14))
        self.label_err.setStyleSheet("color: red;")
        self.label_err.setObjectName("label_err")

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
        self.label.setText(_translate("MainWindow", "Address/IP"))
        self.connectBtn.setText(_translate("MainWindow", "Connect"))
        self.label_2.setText(_translate("MainWindow", "Port"))
        self.addrEdit.setText("")
        self.portEdit.setText("7777")
        self.label_err.setText(_translate("MainWindow", ""))
