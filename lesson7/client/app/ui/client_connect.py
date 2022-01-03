from PyQt5 import QtCore, QtWidgets


class Ui_MainWindow():
    """Класс окна подключения"""
    def setupUi(self, MainWindow):
        """Описание элементов окна подключения"""
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(247, 148)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(30, 20, 47, 14))
        self.label.setObjectName("label")
        self.loginEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.loginEdit.setGeometry(QtCore.QRect(92, 20, 121, 20))
        self.loginEdit.setObjectName("loginEdit")
        self.loginBtn = QtWidgets.QPushButton(self.centralwidget)
        self.loginBtn.setGeometry(QtCore.QRect(30, 80, 75, 23))
        self.loginBtn.setObjectName("loginBtn")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(30, 50, 47, 14))
        self.label_2.setObjectName("label_2")

        self.label_err = QtWidgets.QLabel(self.centralwidget)
        self.label_err.setGeometry(QtCore.QRect(30, 110, 97, 14))
        self.label_err.setStyleSheet("color: red;")
        self.label_err.setObjectName("label_err")

        self.passwdEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.passwdEdit.setGeometry(QtCore.QRect(92, 50, 121, 20))
        self.passwdEdit.setObjectName("passwdEdit")
        self.regBtn = QtWidgets.QPushButton(self.centralwidget)
        self.regBtn.setGeometry(QtCore.QRect(130, 80, 75, 23))
        self.regBtn.setObjectName("regBtn")
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
        self.label.setText(_translate("MainWindow", "Login"))
        self.loginBtn.setText(_translate("MainWindow", "Login"))
        self.label_2.setText(_translate("MainWindow", "Password"))
        self.loginEdit.setText("tonych")
        self.passwdEdit.setText("123")
        self.label_err.setText(_translate("MainWindow", ""))
        self.regBtn.setText(_translate("MainWindow", "Register"))
