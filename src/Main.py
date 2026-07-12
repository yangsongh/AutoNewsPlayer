import sys

from modules.auto_news_player import AutoNewsPlayer
from utils.utils_lib import Utils, LoggerManager, ConfigManager
from PyQt5.QtWidgets import QApplication

from windows.notification import Notification
from windows.main import MainWindow

if __name__ == '__main__':
    Utils.sync_work_dir()

    logger = LoggerManager()

    Utils.setup_except_hook(logger)
    Utils.qt_setup_high_dpi(logger)
    Utils.timing_debug_memory_usage(logger)

    app = QApplication(sys.argv)

    cfg_mgr = ConfigManager(logger)
    cfg_mgr.load_configs()

    notice_window = Notification(logger)
    main_window = MainWindow(logger, cfg_mgr, notice_window, )
    is_autorun = '--autorun' in sys.argv[1:]

    if not is_autorun:
        if not Utils.is_already_running('AutoNewsPlayer'):
            main_window.show()
        else:
            logger.info('程序已在运行中，退出当前程序。')
            sys.exit()

    player = AutoNewsPlayer(logger, cfg_mgr, notice_window)
    player.setSchedule()

    app.exec_()
