from PyQt5 import QtCore, QtWidgets


class Ui_Dialog(object):
    """Класс, описывающий интерфейс окна сервера"""
    def setupUi(self, Dialog):
        """Описание элементов окна сервера"""
        Dialog.setObjectName("Dialog")
        Dialog.resize(748, 201)

        self.connectButton = QtWidgets.QPushButton(Dialog)
        self.connectButton.setGeometry(QtCore.QRect(60, 120, 75, 23))
        self.connectButton.setObjectName("pushButton")

        self.refreshButton = QtWidgets.QPushButton(Dialog)
        self.refreshButton.setGeometry(QtCore.QRect(140, 120, 75, 23))
        self.refreshButton.setObjectName("refreshButton")

        self.lineEdit = QtWidgets.QLineEdit(Dialog)
        self.lineEdit.setGeometry(QtCore.QRect(70, 40, 113, 20))
        self.lineEdit.setObjectName("lineEdit")

        self.lineEdit_2 = QtWidgets.QLineEdit(Dialog)
        self.lineEdit_2.setGeometry(QtCore.QRect(70, 70, 113, 20))
        self.lineEdit_2.setObjectName("lineEdit_2")

        self.label = QtWidgets.QLabel(Dialog)
        self.label.setGeometry(QtCore.QRect(10, 40, 47, 14))
        self.label.setObjectName("label")

        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setGeometry(QtCore.QRect(10, 70, 47, 14))
        self.label_2.setObjectName("label_2")

        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(240, 10, 141, 16))
        self.label_3.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_3.setObjectName("label_3")

        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(240, 20, 87, 14))
        self.label_4.setObjectName("label_4")

        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(240, 40, 87, 14))
        self.label_5.setObjectName("label_5")

        self.tableView = QtWidgets.QTableView(Dialog)
        self.tableView.setGeometry(QtCore.QRect(240, 40, 491, 131))
        self.tableView.setObjectName("tableView")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        """Установка стартовых значений элементам окна"""
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.connectButton.setText(_translate("Dialog", "Connect"))
        self.refreshButton.setText(_translate("Dialog", "Refresh"))
        self.lineEdit_2.setText(_translate("Dialog", "7777"))
        self.label.setText(_translate("Dialog", "Address"))
        self.label_2.setText(_translate("Dialog", "Port"))
        self.label_3.setText(_translate("Dialog", "Подключены:"))
        self.label_4.setText(_translate("Dialog", "Disconnected"))
