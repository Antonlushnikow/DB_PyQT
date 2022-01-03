from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QLineEdit


class Ui_MainWindow(object):
    """Класс окна регистрации"""
    def setupUi(self, MainWindow):
        """Описание элементов окна регистрации"""
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(237, 209)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.regBtn = QtWidgets.QPushButton(self.centralwidget)
        self.regBtn.setGeometry(QtCore.QRect(80, 140, 75, 23))
        self.regBtn.setObjectName("regBtn")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(20, 20, 47, 14))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(20, 60, 47, 14))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(20, 100, 51, 31))
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")

        self.label_err = QtWidgets.QLabel(self.centralwidget)
        self.label_err.setGeometry(QtCore.QRect(20, 160, 151, 31))
        self.label_err.setObjectName("label_err")

        self.loginEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.loginEdit.setGeometry(QtCore.QRect(80, 20, 141, 20))
        self.loginEdit.setObjectName("loginEdit")
        self.passwdEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.passwdEdit.setGeometry(QtCore.QRect(80, 60, 141, 20))
        self.passwdEdit.setObjectName("passwdEdit")
        self.passwd2Edit = QtWidgets.QLineEdit(self.centralwidget)
        self.passwd2Edit.setGeometry(QtCore.QRect(80, 100, 141, 20))
        self.passwd2Edit.setObjectName("passwd2Edit")
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
        self.regBtn.setText(_translate("MainWindow", "Register"))
        self.label.setText(_translate("MainWindow", "Login"))
        self.loginEdit.setText("tonych")
        self.label_2.setText(_translate("MainWindow", "Password"))
        self.passwdEdit.setEchoMode(QLineEdit.Password)
        self.passwd2Edit.setEchoMode(QLineEdit.Password)
        self.label_3.setText(_translate("MainWindow", "Re-Enter Password"))
        self.label_err.setText(_translate("MainWindow", ""))
