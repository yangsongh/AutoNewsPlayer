from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_notification(object):
    def setupUi(self, notification):
        notification.setObjectName('notification')
        notification.resize(210, 52)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap('designer\\../assets/icon.ico'),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        notification.setWindowIcon(icon)
        notification.setStyleSheet(
            '/* 浅色模式 */\n\n/* 深色模式 */\n/*background-color: rgb(24, 26, 27);\ncolor: rgb(255, 255, 255);*/\n')
        self.gridLayout = QtWidgets.QGridLayout(notification)
        self.gridLayout.setObjectName('gridLayout')
        self.notice = QtWidgets.QLabel(notification)
        font = QtGui.QFont()
        font.setFamily('黑体')
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.notice.setFont(font)
        self.notice.setAlignment(QtCore.Qt.AlignCenter)
        self.notice.setObjectName('notice')
        self.gridLayout.addWidget(self.notice, 0, 0, 1, 1)
        self.retranslateUi(notification)
        QtCore.QMetaObject.connectSlotsByName(notification)

    def retranslateUi(self, notification):
        _translate = QtCore.QCoreApplication.translate
        notification.setWindowTitle(_translate('notification', '提示'))
        self.notice.setText(_translate(
            'notification', '新闻播放完成后将自动关闭\n如需手动关闭请关闭本窗口'))


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    notification = QtWidgets.QWidget()
    ui = Ui_notification()
    ui.setupUi(notification)
    notification.show()
    sys.exit(app.exec_())
