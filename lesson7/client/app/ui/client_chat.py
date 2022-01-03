from PyQt5 import QtCore, QtWidgets


class Ui_MainWindow():
    """Класс окна чата"""
    def setupUi(self, MainWindow):
        """Описание элементов окна чата"""
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(547, 323)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.userLbl = QtWidgets.QLabel(self.centralwidget)
        self.userLbl.setGeometry(QtCore.QRect(20, 10, 200, 14))
        self.userLbl.setObjectName("userLbl")


        self.sendBtn = QtWidgets.QPushButton(self.centralwidget)
        self.sendBtn.setGeometry(QtCore.QRect(470, 270, 61, 31))
        self.sendBtn.setObjectName("sendBtn")
        self.msgEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.msgEdit.setGeometry(QtCore.QRect(20, 270, 441, 31))
        self.msgEdit.setObjectName("msgEdit")
        self.chatView = QtWidgets.QListWidget(self.centralwidget)
        self.chatView.setGeometry(QtCore.QRect(20, 30, 511, 231))
        self.chatView.setObjectName("chatView")
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
        self.sendBtn.setText(_translate("MainWindow", "Send"))
