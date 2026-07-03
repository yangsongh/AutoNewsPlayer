import os

from windows.ui.Ui_Notification import Ui_notification
from utils.UtilsLibs import Utils, LoggerManager

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QPoint, pyqtSignal
from PyQt5.QtWidgets import QWidget, QDesktopWidget


class Notification(QWidget):
    showWinSignal = pyqtSignal()
    hideWinSignal = pyqtSignal()

    def __init__(self, logger: LoggerManager):
        super().__init__()
        self.ui = Ui_notification()
        self.ui.setupUi(self)

        if Utils.is_package_mode():
            icon_path = os.path.join(Utils.get_bundle_dir(), 'icon.ico')
            self.setWindowIcon(QIcon(icon_path))

        self.logger = logger

        self.showWinSignal.connect(self.showWin)
        self.hideWinSignal.connect(self.hideWin)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint)

    def showWin(self):
        self.show()
        self.logger.info('显示新闻播放提示窗口')

    def hideWin(self):
        self.hide()
        self.logger.info('隐藏新闻播放提示窗口')

    def _adjustPosition(self):
        """直接使用屏幕总尺寸定位到右下角（覆盖任务栏）"""
        desktop = QDesktopWidget()
        screen_num = desktop.screenNumber(self)
        screen_geom = desktop.screenGeometry(screen_num)
        window_width = self.frameGeometry().width()
        window_height = self.frameGeometry().height()
        target_x = screen_geom.x() + screen_geom.width() - window_width
        target_y = screen_geom.y() + screen_geom.height() - window_height
        self.move(QPoint(target_x, target_y))

    def showEvent(self, event):  # type: ignore
        """显示时确保使用最新屏幕信息"""
        super().showEvent(event)
        self._adjustPosition()
