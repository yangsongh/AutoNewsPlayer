
import re
import os
import threading
import winreg as reg

from win32api import MessageBox
from modules.auto_news_player import AutoNewsPlayer

from windows.ui.Ui_Main import Ui_Main
from windows.notification import Notification
from utils.utils_lib import LoggerManager, ConfigManager, Utils


from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QMainWindow
from PyQt5.QtWidgets import QMainWindow


class MainWindow(QMainWindow):
    def __init__(self, logger: LoggerManager, cfg_mgr: ConfigManager, notice_win: Notification):
        super().__init__()
        self.ui = Ui_Main()
        self.ui.setupUi(self)

        if Utils.is_package_mode():
            icon_path = os.path.join(Utils.get_bundle_dir(), 'icon.ico')
            self.setWindowIcon(QIcon(icon_path))

        self.logger = logger
        self.cfg_mgr = cfg_mgr

        self.deft_cfg = cfg_mgr.cfgs['default']
        self.ad_settings = self.deft_cfg['ad_settings']
        self.auto_test_cfg = cfg_mgr.cfgs['auto_test']

        self.test_player = AutoNewsPlayer(
            logger, cfg_mgr, notice_win, run_mode='auto_test', no_weekend_play=False, is_test_mode=True)
        self.test_running = threading.Event()

        self.updateUiElements()
        self.connectSignals()

    def updateUiElements(self):
        """更新UI元素的状态"""
        self.checkAutorunStatus()
        self.ui.no_weekend.setChecked(self.deft_cfg['no_weekend_play'])
        self.ui.hide_progress_bar.setChecked(
            self.deft_cfg['hide_progress_bar'])
        self.ui.show_notice_win.setChecked(self.deft_cfg['show_notice_win'])
        self.ui.xw30f_source.setChecked(
            self.deft_cfg['video_source'] == 'XW30F')
        self.ui.jrsf_source.setChecked(self.deft_cfg['video_source'] == 'JRSF')
        self.ui.everyday_switch.setChecked(
            self.deft_cfg['video_source'] == '[auto_switch]')
        self.ui.duration_slider.setMaximum(self.deft_cfg['total_duration'])
        self.ui.duration_slider.setValue(self.deft_cfg['play_duration'])
        self.ui.duration_txt.setText(
            str(self.ui.duration_slider.value()) + 'min')
        self.ui.volume_slider.setValue(int(self.deft_cfg['volume'] * 100))
        self.ui.volume_txt.setText(
            str(int(self.deft_cfg['volume'] * 100)) + '%')
        self.ui.play_time.setText(str(self.deft_cfg['play_time']))
        self.ui.ad_check_wait.setText(str(self.ad_settings['ad_check_wait']))
        self.ui.max_ad_check.setText(str(self.ad_settings['max_ad_check']))
        self.ui.test_times_edit.setText(str(self.auto_test_cfg['test_times']))
        self.ui.test_duration_edit.setText(
            str(self.auto_test_cfg['play_duration']))
        self.applyColorTheme(self.deft_cfg.get('color_theme', 'dark'))

    def connectSignals(self):
        """连接信号和槽"""
        self.ui.autorun.stateChanged.connect(
            lambda: self.setAutorun(self.ui.autorun.isChecked()))
        self.ui.no_weekend.stateChanged.connect(lambda: self.setSwitch(
            '周末不播放', 'no_weekend_play', self.ui.no_weekend.isChecked()))
        self.ui.hide_progress_bar.stateChanged.connect(lambda: self.setSwitch(
            '隐藏进度条', 'hide_progress_bar', self.ui.hide_progress_bar.isChecked()))
        self.ui.show_notice_win.stateChanged.connect(lambda: self.setSwitch(
            '显示右下角提示窗', 'show_notice_win', self.ui.show_notice_win.isChecked()))
        self.ui.xw30f_source.clicked.connect(
            lambda: self.setSwitch('视频源', 'video_source', 'XW30F'))
        self.ui.jrsf_source.clicked.connect(
            lambda: self.setSwitch('视频源', 'video_source', 'JRSF'))
        self.ui.everyday_switch.clicked.connect(
            lambda: self.setSwitch('视频源', 'video_source', '[auto_switch]'))
        self.ui.duration_slider.valueChanged.connect(
            lambda: self.setPlayDuration(self.ui.duration_slider.value()))
        self.ui.volume_slider.valueChanged.connect(
            lambda: self.setDefaultVolume(self.ui.volume_slider.value()))
        self.ui.play_time.editingFinished.connect(
            lambda: self.setPlayTime(self.ui.play_time.text()))
        self.ui.ad_check_wait.editingFinished.connect(
            lambda: self.setAdCheckWait(self.ui.ad_check_wait.text()))
        self.ui.max_ad_check.editingFinished.connect(
            lambda: self.setMaxAdCheck(self.ui.max_ad_check.text()))
        self.ui.xw30f_test.clicked.connect(
            lambda: self.runPlayingTestThread('XW30F'))
        self.ui.jrsf_test.clicked.connect(
            lambda: self.runPlayingTestThread('JRSF'))
        self.ui.action_light.triggered.connect(
            lambda: self.applyColorTheme('light'))
        self.ui.action_dark.triggered.connect(
            lambda: self.applyColorTheme('dark'))

    def applyColorTheme(self, theme_name):
        """应用颜色主题"""
        if theme_name == 'light':
            qss = '\n                QLineEdit { background-color: rgb(240, 240, 240) } /* 输入框背景色（白色） */\n                QMenuBar { background: rgb(240, 240, 240) } /* 整个菜单栏的背景色（白色） */\n                QMenu::item { background: transparent } /*  菜单栏中单个项目的背景色（貌似无效） */\n                QMenu::item:selected { background-color: rgb(24, 26, 27) } /* 菜单栏项目的action悬停背景色（黑色）*/\n            '
        else:
            if theme_name == 'dark':
                qss = '\n                QMainWindow, QWidget {\n                    background-color: rgb(24, 26, 27); /* 背景色（黑色） */\n                    color: rgb(255, 255, 255); /* 文本色（白色） */\n                }\n                QMenuBar::item { background: transparent } /* 菜单栏中单个项目的背景色（透明）*/\n                QMenu::item:selected {\n                    color: rgb(24, 26, 27); /* 每个action悬停时文字的颜色（黑色） */\n                    background-color: rgb(255, 255, 255);  /* 菜单栏项目的action悬停背景色（白色） */\n                }\n            '
            else:
                qss = ''
        self.setStyleSheet(qss)
        self.setSwitch('颜色主题', 'color_theme', theme_name)

    def runPlayingTest(self, test_times, video_source, play_duration):
        """运行自动化测试"""
        self.test_running.set()
        self.test_player.video_source = video_source
        self.test_player.play_duration = play_duration

        for i in range(test_times):
            self.logger.info(f'开始执行第 {i + 1} 次完整测试')
            ret = self.test_player.playNews()
            if ret == 'cancel':
                self.logger.info('用户主动关闭浏览器，取消测试')
                break
            else:
                self.logger.info(f'第 {i + 1} 次测试完成')
        self.test_running.clear()

    def runPlayingTestThread(self, video_source):
        """运行自动化测试线程"""
        try:
            test_times = int(self.ui.test_times_edit.text())
            play_duration = int(self.ui.test_duration_edit.text())
            if test_times <= 0 or play_duration <= 0:
                MessageBox(0, '测试次数和播放时长必须是正整数。', '提示', 64)
                return
            else:
                if self.test_running.is_set():
                    MessageBox(0, '上一个测试运行中，请先完成上一个测试。', '提示', 64)
                    return
                else:
                    self.logger.info(f'共执行 {test_times} 次自动化测试')
                    test_thread = threading.Thread(target=self.runPlayingTest, args=(
                        test_times, video_source, play_duration), daemon=True)
                    test_thread.start()
        except ValueError:
            MessageBox(0, '请输入有效的整数作为测试次数或播放时长。', '提示', 64)
            return None

    def checkAutorunStatus(self):
        """检测当前自启动状态并更新按钮状态"""
        try:
            if not Utils.is_package_mode():
                self.ui.autorun.setDisabled(True)
                return
            else:
                app_name = os.path.basename(Utils.get_program_dir())
                key_path = 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run'
                with reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_READ) as reg_key:
                    pass
                try:
                    value, _ = reg.QueryValueEx(reg_key, app_name)
                except FileNotFoundError:
                    value = None
                if value:
                    match = re.match('^\"([^\"]+)\"', value)
                    if match:
                        exe_path = match.group(1)
                    else:
                        exe_path = value.split(' ', 1)[0]
                    is_valid = os.path.exists(exe_path.strip('\"'))
                else:
                    is_valid = False
                self.ui.autorun.setChecked(is_valid)
                if value and (not is_valid):
                    with reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE) as write_key:
                        reg.DeleteValue(write_key, app_name)
                    self.logger.warning('自启动项无效，已自动清除。')
        except Exception as e:
            self.logger.error(f'自启动状态检测失败: {str(e)}')
            self.ui.autorun.setChecked(False)

    def setAutorun(self, state):
        """设置开机自启动"""
        try:
            app_name = os.path.basename(Utils.get_program_dir())
            key_path = 'SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run'
            if state:
                with reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE) as reg_key:
                    reg.SetValueEx(reg_key, app_name, 0, reg.REG_SZ,
                                   f'\"{Utils.get_program_path()}\" --autorun')
                    msg = '已启用开机自启动，程序将在系统启动时自动运行'
                    MessageBox(0, msg, '成功', 64)
                    self.logger.info(msg)
            else:
                reply = QMessageBox.information(
                    None, '提示', '温馨提示：关闭自启动后，将不能自动播放新闻。确定关闭自启动？', QMessageBox.Ok | QMessageBox.Cancel)
                if reply != QMessageBox.Ok:
                    self.ui.autorun.setChecked(True)
                else:
                    with reg.OpenKey(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_SET_VALUE) as reg_key:
                        try:
                            reg.DeleteValue(reg_key, app_name)
                            self.logger.info('开机自启动已禁用')
                        except FileNotFoundError:
                            self.logger.warning('尝试删除不存在的自启动项')
        except Exception as e:
            error_msg = f'自启动配置失败: {str(e)}'
            self.logger.error(error_msg)
            MessageBox(0, error_msg, '错误', 16)

    def setSwitch(self, display_name, code_name, state):
        """设置指定开关"""
        try:
            self.deft_cfg[code_name] = state
            self.cfg_mgr.save_config()
            self.logger.info(f'设置{display_name}成功：{state}')
        except Exception as e:
            err_msg = f'设置{display_name}失败: {str(e)}'
            self.logger.error(err_msg)
            MessageBox(0, err_msg, '错误', 16)

    def setPlayDuration(self, duration):
        """设置视频播放时长"""
        try:
            self.ui.duration_txt.setText(str(duration) + 'min')
            self.deft_cfg['play_duration'] = duration
            self.cfg_mgr.save_config()
            self.logger.info(f"设置视频播放时长成功：{str(duration) + 'min'}")
        except Exception as e:
            err_msg = f'设置视频播放时长失败: {str(e)}'
            self.logger.error(err_msg)
            MessageBox(0, err_msg, '错误', 16)

    def setDefaultVolume(self, volume):
        """设置默认音量"""
        try:
            self.ui.volume_txt.setText(str(int(volume)) + '%')
            self.deft_cfg['volume'] = float(volume / 100)
            self.cfg_mgr.save_config()
            self.logger.info(f"设置默认音量成功：{str(int(volume)) + '%'}")
        except Exception as e:
            err_msg = f'设置默认音量失败: {str(e)}'
            self.logger.error(err_msg)
            MessageBox(0, err_msg, '错误', 16)

    def setPlayTime(self, play_time):
        """设置默认播放时间"""
        try:
            parts = play_time.split(':')
            if len(parts) != 3:
                raise ValueError('时间格式应为 HH:MM:SS，例如 18:49:00')

            try:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = int(parts[2])
            except ValueError:
                raise ValueError('时间部分必须为数字')

            if not 0 <= hours <= 23:
                raise ValueError('小时数应在 0-23 之间')

            if not 0 <= minutes <= 59:
                raise ValueError('分钟数应在 0-59 之间')

            if not 0 <= seconds <= 59:
                raise ValueError('秒数应在 0-59 之间')

            formatted_time = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
            self.deft_cfg['play_time'] = formatted_time
            self.cfg_mgr.save_config()
            self.logger.info(f'设置默认播放时间成功：{formatted_time}')

        except Exception as e:
            err_msg = f'设置默认播放时间失败: {str(e)}'
            self.logger.error(err_msg)
            MessageBox(0, err_msg, '错误', 16)

    def setAdCheckWait(self, ad_check_wait):
        """设置广告检查等待时间（支持正小数或整数，如 3 或 2.5）"""
        try:
            if not re.fullmatch('^(\\d+\\.?\\d*|\\.\\d+)$', ad_check_wait):
                raise ValueError('请输入有效的数字（如 5 或 3.14）')
            else:
                wait_time = float(ad_check_wait)
                if wait_time < 0:
                    raise ValueError('等待时间必须大于等于0')
                else:
                    formatted_wait = f'{wait_time:.2f}'.rstrip('0').rstrip('.')
                    self.ad_settings['ad_check_wait'] = float(formatted_wait)
                    self.cfg_mgr.save_config()
                    self.logger.info(f'设置广告检查等待时间成功：{formatted_wait}s')
        except Exception as e:
            err_msg = f'设置广告检查等待时间失败: {str(e)}'
            self.logger.error(err_msg)
            MessageBox(0, err_msg, '错误', 16)

    def setMaxAdCheck(self, max_ad_check):
        """设置最大广告检测次数（整数，如 3）"""
        try:
            max_ad_check = int(float(max_ad_check))
            if max_ad_check < 0:
                MessageBox(0, '最大广告检测次数必须>=0。', '提示', 64)
                return
            else:
                self.ad_settings['max_ad_check'] = max_ad_check
                self.cfg_mgr.save_config()
                self.logger.info(f'设置最大广告检测次数成功：{max_ad_check}次')
        except ValueError:
            MessageBox(0, '请输入有效的数字作为最大广告检测次数。', '提示', 64)
        except Exception as e:
            err_msg = f'设置最大广告检测次数失败: {str(e)}'
            self.logger.error(err_msg)
            MessageBox(0, err_msg, '错误', 16)
