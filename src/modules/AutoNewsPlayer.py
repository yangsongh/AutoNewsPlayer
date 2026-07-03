import os
import time
import datetime
import schedule
import win32gui
import win32con
import threading
import subprocess

from ctypes import windll
from win32api import MessageBox

from utils.UtilsLibs import LoggerManager, ConfigManager, Utils
from modules.AutomaticBrowser import startChrome, clickElement

from pathlib import Path
from PyQt5.QtCore import QTimer
from windows.Notification import Notification

from pythoncom import CoInitialize, CoUninitialize
from pycaw.pycaw import AudioUtilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import TimeoutException, ElementNotInteractableException


class AutoNewsPlayer:
    def __init__(self, logger: LoggerManager, cfg_mgr: ConfigManager, notice_win: Notification, run_mode='normal', play_time=None, play_duration=None, video_source=None, volume=None, total_duration=None, additional_script=None, fail_auto_switch_source=None, no_weekend_play=None, max_ad_check=None, ad_check_wait=None, hide_progress_bar=None, show_notice_win=None, is_test_mode=False):
        self.logger = logger
        self.driver = None
        self.unadjusted_volume = None
        self.timer = None
        self.is_test_mode = is_test_mode
        self.notice_win = notice_win
        self.run_mode = run_mode
        self.cfg_mgr = cfg_mgr
        self.deft_cfg = cfg_mgr.cfgs['default']
        self.ad_settings = self.deft_cfg['ad_settings']
        self.play_time = self.deft_cfg['play_time'] if play_time is None else play_time
        self.play_duration = self.deft_cfg['play_duration'] if play_duration is None else play_duration
        self.volume = self.deft_cfg['volume'] if volume is None else volume
        self.total_duration = self.deft_cfg['total_duration'] if total_duration is None else total_duration
        self.additional_script = self.deft_cfg['additional_script'] if additional_script is None else additional_script
        self.no_weekend_play = self.deft_cfg['no_weekend_play'] if no_weekend_play is None else no_weekend_play
        self.hide_progress_bar = self.deft_cfg['hide_progress_bar'] if hide_progress_bar is None else hide_progress_bar
        self.show_notice_win = self.deft_cfg['show_notice_win'] if show_notice_win is None else show_notice_win
        self.fail_auto_switch_source = self.deft_cfg[
            'fail_auto_switch_source'] if fail_auto_switch_source is None else fail_auto_switch_source
        self.max_ad_check = self.ad_settings['max_ad_check'] if max_ad_check is None else max_ad_check
        self.ad_check_wait = self.ad_settings['ad_check_wait'] if ad_check_wait is None else ad_check_wait
        if video_source is None:
            if self.deft_cfg['video_source'] == '[auto_switch]':
                self.video_source = 'JRSF' if self.deft_cfg.get(
                    'last_source', 'XW30F') == 'XW30F' else 'XW30F'
            else:
                self.video_source = self.deft_cfg['video_source']
        else:
            self.video_source = video_source
        self.xw30f_url = self.deft_cfg['xw30f_url']
        self.jrsf_url = self.deft_cfg['jrsf_url']
        self.progress_bar_css = self.deft_cfg['progress_bar_css']
        self.fs_btn_css = self.deft_cfg['fs_btn_css']
        self.big_play_btn_css = self.deft_cfg['big_play_btn_css']
        self.browser_title = self.deft_cfg['browser_title']
        self.xw30f_beforehand_close_sec = self.deft_cfg['xw30f_beforehand_close_sec']
        self.jrsf_beforehand_close_sec = self.deft_cfg['jrsf_beforehand_close_sec']

    def showTimedPopups(self, title: str, content: str, duration: int, timeout=10):
        """显示定时弹窗"""
        def _closeAfter(hwnd: int, delay: float):
            time.sleep(delay)
            try:
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            except:
                return None
        threading.Thread(target=MessageBox, args=(
            0, content, title, 48), daemon=True).start()
        start = time.time()
        while time.time() - start < timeout:
            hwnd = win32gui.FindWindow('#32770', title)
            if hwnd:
                win32gui.SetWindowPos(
                    hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                threading.Thread(target=_closeAfter, args=(
                    hwnd, duration), daemon=True).start()
                return True
            time.sleep(0.1)
        self.logger.warning(f'弹窗句柄获取超时（{timeout}秒）')
        return False

    def clickVideoPlayButton(self):
        """定位并点击视频播放按钮"""
        play_button = (self.findElements(
            self.big_play_btn_css) or [None])[(-1)]
        if not play_button:
            return False
        try:
            play_button.click()
            self.logger.info('成功点击视频播放大按钮')
            return True
        except ElementNotInteractableException:
            return True
        except Exception as e:
            self.logger.error(f'点击播放按钮时发生未知错误: {str(e)}')
            return False

    def checkAndSkipVideoAd(self):
        """视频播放页广告检测与处理"""
        if not self.driver:
            raise Exception('浏览器驱动未初始化')
        else:
            attempt = 0
            while attempt < self.max_ad_check:
                self.waitForVideo2Load()
                time.sleep(1)
                self.clickVideoPlayButton()
                progress_bar = (self.findElements(
                    self.progress_bar_css, False) or [None])[(-1)]
                if progress_bar and (not self.hover2Element(progress_bar, False)):
                    retries = f'{attempt + 1}/{self.max_ad_check}'
                    msg = f'检测到广告，尝试刷新页面（第 {retries} 次）...'
                    self.logger.info(msg)
                    self.showTimedPopups(f'新闻播放器 - 检测到广告 ({retries})', msg, 5)
                    self.driver.refresh()
                    time.sleep(self.ad_check_wait)
                    attempt += 1
                else:
                    self.logger.info('未检测到广告，继续流程')
                    return True
            self.logger.error('广告跳过失败，达到最大检测次数')
            return False

    def openNewsPage(self):
        """初始化浏览器并打开新闻页面"""
        try:
            url = self.xw30f_url if self.video_source == 'XW30F' else self.jrsf_url
            self.logger.info(f'打开浏览器并访问新闻页面：{url}')
            self.driver = startChrome(self.logger)
            if not self.driver:
                raise Exception('无法启动Chrome浏览器')
            else:
                self.driver.get(url)
                return True
        except Exception as e:
            raise Exception(
                f"初始化浏览器并打开新闻页面失败。\n{str(e).split('Stacktrace:')[0]}")

    def bringBrowser2Foreground(self):
        """将浏览器窗口置于最前"""
        def _findWindowContains(title_part: str = self.browser_title):
            """最简单的模糊匹配窗口标题，返回第一个匹配的句柄"""
            def _callback(hwnd, extra: list):
                if title_part.lower() in win32gui.GetWindowText(hwnd).lower():
                    extra.append(hwnd)
                    return True
                else:
                    return True
            result = []
            win32gui.EnumWindows(_callback, result)
            return result[0] if result else None
        try:
            hwnd = _findWindowContains()
            if not hwnd:
                raise
            else:
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                win32gui.SendMessage(
                    hwnd, win32con.WM_ACTIVATE, win32con.WA_ACTIVE, 0)
                windll.user32.SwitchToThisWindow(hwnd, True)
                self.logger.info('浏览器窗口已置于最前')
                return True
        except:
            self.logger.info('无法将浏览器窗口置于最前')
            return False

    def findAndClickVideoLink(self):
        """查找并点击视频链接"""
        if not self.driver:
            raise Exception('浏览器驱动未初始化')
        else:
            try:
                self.logger.info('查找并点击视频链接，打开新标签页')
                today_date = datetime.datetime.now().strftime('%Y%m%d')
                if self.video_source == 'XW30F':
                    xpath = '//a[contains(text(), \"《新闻30分》\")]'
                else:
                    if self.video_source == 'JRSF':
                        xpath = f'//a[contains(@title, \"{today_date}\") or contains(text(), \"{today_date}\")]'
                    else:
                        xpath = ''
                link = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, xpath)))
                clickElement(self.logger, link)
                WebDriverWait(self.driver, 10).until(
                    EC.number_of_windows_to_be(2))
                self.driver.switch_to.window(self.driver.window_handles[(-1)])
            except TimeoutException:
                if self.video_source == 'XW30F' or not self.fail_auto_switch_source:
                    raise
                else:
                    msg = '没有找到今日说法视频链接。今天可能未播出今日说法。\n即将切换到新闻30分...'
                    self.logger.warning(msg)
                    self.showTimedPopups('警告', msg, 5)
                    self.driver.quit()
                    self.video_source = 'XW30F'
                    self.openNewsPage()
                    self.findAndClickVideoLink()
                    return True
            except Exception as e:
                raise Exception(
                    f"无法找到或点击播放链接按钮。\n{str(e).split('Stacktrace:')[0]}")
            return True

    def waitForVideo2Load(self):
        if not self.driver:
            raise Exception('浏览器驱动未初始化')
        else:
            try:
                self.logger.info('等待视频播放器加载...')
                WebDriverWait(self.driver, 30).until(EC.presence_of_element_located(
                    (By.XPATH, '//*[@id=\"_video_player_html5_api\"]')))
            except Exception as e:
                raise Exception(f'视频播放器加载失败: {str(e)}')
            self.logger.info('视频播放器加载完成。')

    def _findAndClickCuePoint(self, target_percent: float):
        """尝试查找并点击目标视频时间点"""
        if not self.driver:
            raise Exception('浏览器驱动未初始化')

        try:
            cue_points_left = self.driver.execute_script(
                '\n                const cuePoints = document.querySelectorAll(\'.vjs-cue-point\');\n                const parent = document.querySelector(\'.vjs-progress-control\');\n                if (!parent) return [];\n                const parentWidth = parent.offsetWidth;\n                return Array.from(cuePoints).map(cuePoint => ({\n                    element: cuePoint,\n                    leftPercent: (cuePoint.offsetLeft / parentWidth) * 100\n                }));\n            ')
            self.logger.debug(f'找到 {len(cue_points_left)} 个视频时间点')
            if cue_points_left:
                closest = min(cue_points_left, key=lambda x: abs(
                    x['leftPercent'] - target_percent))['element']
                self.logger.info(f'尝试点击最接近{target_percent:.1f}%的时间点')
                ret = clickElement(self.logger, closest, max_retries=100,
                                   wait_time=0.5, fail_callback=self.hover2Element)
                return ret
        except TimeoutException:
            return None
        except Exception as e:
            self.logger.warning(f'处理并点击视频时间点时出现异常: {str(e)}')
            return False

    def _clickProgressBarTargetPos(self, progress_bar: WebElement, target_percent: float):
        """点击进度条目标位置"""
        self.logger.info('没有找到视频时间点或处理失败，开始处理进度条点击')
        if not self.driver:
            raise Exception('浏览器驱动未初始化')
        else:
            try:
                bar_width = self.driver.execute_script(
                    'return arguments[0].getBoundingClientRect()', progress_bar)['width']
                if bar_width <= 0:
                    self.logger.warning('进度条宽度为0，无法点击')
                    return False
                else:
                    click_x = bar_width * (target_percent / 100)
                    self.logger.debug(f'进度条宽度: {bar_width}px')
                    self.logger.info(
                        f'目标点击进度条坐标: {click_x:.1f}px (目标百分比 {target_percent}%)')
                    click_result = self.driver.execute_script(
                        '\n                const progressBar = arguments[0];\n                const clickX = arguments[1];\n                const rect = progressBar.getBoundingClientRect();\n                const event = new MouseEvent(\'click\', {\n                    bubbles: true,\n                    cancelable: true,\n                    view: window,\n                    clientX: rect.left + clickX,\n                    clientY: rect.top + rect.height/2\n                });\n                progressBar.dispatchEvent(new MouseEvent(\'mousedown\', event));\n                progressBar.dispatchEvent(new MouseEvent(\'mouseup\', event));\n                return progressBar.dispatchEvent(event);\n            ', progress_bar, click_x)
                    self.logger.debug(f'JavaScript点击进度条返回值: {click_result}')
                    if click_result:
                        self.logger.info(f'已点击进度条{target_percent:.1f}%位置')
                        current_time = self.driver.execute_script(
                            'return document.querySelector(\'.vjs-current-time-display\').textContent')
                        self.logger.debug(f'进度条点击后的播放时间: {current_time}')
                        return True
                    else:
                        self.logger.warning('视频进度条点击失败。')
                        return False
            except Exception as e:
                self.logger.warning(
                    f"处理或点击进度条时发生异常: {str(e).split('Stacktrace:')[0]}")
                return False

    def findAndClickTargetProgress(self):
        """根据播放时长计算、查找并点击目标视频时间点或进度条"""
        target_minutes = self.total_duration - self.play_duration
        target_percent = target_minutes / self.total_duration * 100
        target_percent = max(0, min(target_percent, 100))
        self.logger.info(
            f'目标视频位置：从{target_minutes}分钟开始播放（进度{target_percent:.1f}%）')
        progress_bar = (self.findElements(
            self.progress_bar_css) or [None])[(-1)]
        if not self.hover2Element(progress_bar):
            self.logger.warning('找不到进度条/鼠标悬停失败/视频存在广告，后续点击时间点或进度条操作可能失败')
        if self._findAndClickCuePoint(target_percent):
            return True
        else:
            return self._clickProgressBarTargetPos(progress_bar, target_percent)

    def setVolume(self, target_volume: int | None = None):
        """设置系统音量并保存原始音量值"""
        try:
            volume_value = target_volume if target_volume is not None else self.volume
            self.logger.info(f'设置系统音量为{volume_value * 100:.0f}%')

            CoInitialize()
            device = AudioUtilities.GetSpeakers()
            if device is None:
                raise Exception('未获取到默认音频设备')
            interface = device.EndpointVolume

            if self.unadjusted_volume is None:
                self.unadjusted_volume = interface.GetMasterVolumeLevelScalar()
            interface.SetMasterVolumeLevelScalar(volume_value, None)

            CoUninitialize()
        except Exception as e:
            raise Exception(f'设置音量失败。\n{str(e)}')

    def findElements(self, css_value: str, show_log=True):
        """查找元素"""
        if not self.driver:
            return []

        try:
            element = self.driver.find_elements(By.CSS_SELECTOR, css_value)
            self.logger.info(f'成功定位元素 {css_value}') if show_log else False
            return element
        except TimeoutException:
            self.logger.warning(f'未找到元素 {css_value}') if show_log else None
            return []

    def hover2Element(self, element: None | WebElement = None, show_log=True):
        """悬停鼠标到元素上"""
        if not self.driver:
            return False

        element = element if element else (
            self.findElements(self.fs_btn_css) or [None])[(-1)]
        if not element:
            return False

        try:
            ActionChains(self.driver).move_to_element(
                element).perform()
            if show_log:
                self.logger.info('鼠标已悬停在元素上')
            return True
        except Exception as e:
            if show_log:
                self.logger.warning(
                    f"悬停操作失败: {str(e).split('Stacktrace:')[0]}")
            return False

    def hideProgressBar(self):
        """隐藏页面中的进度条元素"""
        if not self.driver:
            raise Exception('浏览器驱动未初始化')
        else:
            if not self.hide_progress_bar:
                return True
            else:
                try:
                    progress_bar = (self.findElements(
                        self.progress_bar_css) or [None])[(-1)]
                    if not progress_bar:
                        self.logger.warning('找不到进度条，无法隐藏')
                        return False
                    else:
                        self.driver.execute_script(
                            'arguments[0].style.display = \"none\";', progress_bar)
                        self.logger.info('视频进度条已隐藏')
                        return True
                except Exception as e:
                    self.logger.info(f'隐藏进度条失败: {str(e)}')
                    return None

    def toggleFullscreen(self):
        """查找并切换全屏模式"""
        self.logger.info('查找按钮并切换全屏模式')

        try:
            fullscreen_buttons = self.findElements(self.fs_btn_css)
            if not fullscreen_buttons:
                return False

            btns_num = len(fullscreen_buttons)
            if btns_num >= 2:
                clickElement(
                    self.logger, fullscreen_buttons[(-1)], wait_time=0.5, fail_callback=self.hover2Element)
                return True
            else:
                raise Exception(f'未找到足够的全屏按钮（应为>=2个，实际为{btns_num}个）')
        except Exception as e:
            self.logger.warning(
                f"全屏模式切换失败: {str(e).split('Stacktrace:')[0]}")
            return False

    def monitorPlaybackProgress(self):
        """循环监测视频播放进度，支持提前关闭"""
        def _time2Seconds(time_str):
            """将时间字符串(MM:SS或HH:MM:SS)转换为秒数"""
            if not time_str.strip():
                return 0
            else:
                parts = list(map(int, time_str.split(':')))
                if len(parts) == 2:
                    return parts[0] * 60 + parts[1]
                else:
                    return 0

        self.logger.info(
            f"开始监测视频播放进度，提前关闭秒数：{(self.xw30f_beforehand_close_sec if self.video_source == 'XW30F' else self.jrsf_beforehand_close_sec)}")

        if not self.driver:
            raise Exception('浏览器驱动未初始化')

        # 进入全屏模式
        fs_btns = self.findElements(self.fs_btn_css, False)
        if fs_btns:
            self.hover2Element(fs_btns[-1], False)

        # 循环监测播放进度
        while True:
            try:
                # 获取当前时间和总时长
                current_time_str = self.driver.find_element(
                    By.CSS_SELECTOR, '.vjs-current-time-display').text.strip()
                duration_str = self.driver.find_element(
                    By.CSS_SELECTOR, '.vjs-duration-display').text.strip()

                # 转换为秒数
                current_sec = _time2Seconds(current_time_str)
                total_sec = _time2Seconds(duration_str)

                # 如果时间获取失败，继续循环
                if not current_sec or not total_sec:
                    time.sleep(0.3)
                    continue

                # 每30秒记录一次进度
                if current_sec % 30 == 0:
                    self.logger.debug(
                        f'当前进度: {current_time_str}({current_sec}秒), 总时长: {duration_str}({total_sec}秒)')

                # 计算剩余时间
                remaining_sec = total_sec - current_sec
                beforehand_close_sec = (self.xw30f_beforehand_close_sec
                                        if self.video_source == 'XW30F'
                                        else self.jrsf_beforehand_close_sec)

                # 判断是否需要提前关闭
                if 0 < remaining_sec <= beforehand_close_sec:
                    self.logger.info(f'视频即将结束(剩余{remaining_sec}秒)，提前关闭浏览器')
                    self.driver.quit()
                    return True

                # 判断是否播放完毕
                if current_sec >= total_sec:
                    self.logger.info('视频播放完毕，关闭浏览器')
                    self.driver.quit()
                    return True

                # 短暂休眠后继续监测
                time.sleep(0.3)

            except Exception as e:
                error_msg = str(e).split('Stacktrace:')[0]

                # 处理可恢复的错误
                if any(err in error_msg for err in ['stale element', 'no such element', 'NoneType']):
                    time.sleep(0.3)
                    continue
                else:
                    # 不可恢复的错误，重新抛出异常
                    raise Exception(f'播放进度监测失败: {error_msg}')

    def savePlayFailScreenshot(self, base_dir: str):
        """保存播放失败的浏览器截图"""
        now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        screenshot_path = os.path.join(
            base_dir, f"{now}_{self.video_source}_{self.play_time.replace(':', '-')}_{self.play_duration}_{self.total_duration}.png")
        os.makedirs(base_dir, exist_ok=True)
        if self.driver:
            try:
                self.driver.save_screenshot(screenshot_path)
                self.logger.info(f'播放失败截图已保存到: {screenshot_path}')
            except Exception as screenshot_e:
                screenshot_e = str(screenshot_e).split('Stacktrace:')[0]
                self.logger.error(f'播放失败截图保存失败: {str(screenshot_e)}')
                return None

    def moveMouse2TopLeft(self):
        """移动鼠标到屏幕左上角"""
        windll.user32.SetCursorPos(0, 0)
        self.logger.info('鼠标已移动到屏幕左上角')

    def saveVideoSource(self):
        """保存视频播放源"""
        if not self.is_test_mode:
            self.deft_cfg['last_source'] = self.video_source
            self.cfg_mgr.save_config()
            self.logger.info(f'已保存视频源：{self.video_source}')

    def playNews(self):
        """播放新闻：整合各步骤的主流程"""
        ret = 'fail'

        try:
            # 执行主流程
            self.openNewsPage()
            self.findAndClickVideoLink()

            # 显示通知窗口
            if self.show_notice_win:
                self.notice_win.showWinSignal.emit()

            self.bringBrowser2Foreground()
            self.checkAndSkipVideoAd()
            self.findAndClickTargetProgress()
            self.toggleFullscreen()
            self.hideProgressBar()
            self.saveVideoSource()
            self.moveMouse2TopLeft()
            self.setVolume()

            # 监测播放进度
            self.monitorPlaybackProgress()

            # 播放完成
            ret = 'success'

        except Exception as e:
            error_msg = str(e).split('Stacktrace:')[
                0] if 'Stacktrace:' in str(e) else str(e)

            # 处理特定异常类型
            if any(err in error_msg for err in ['no such window', 'invalid session id', 'disconnected',
                                                'Connection aborted', 'ConnectionResetError',
                                                'NewConnectionError', 'MaxRetryError']):
                self.logger.info('目标窗口已关闭')
                ret = 'cancel'
            else:
                msg = f'自动播放新闻失败: {error_msg}'
                self.logger.error(msg)
                MessageBox(0, msg, '错误', 48)

                # 保存失败截图
                if self.driver:
                    self.savePlayFailScreenshot(f'{self.run_mode}_fail')

                ret = 'fail'

        finally:
            # 隐藏通知窗口
            self.notice_win.hideWinSignal.emit()

            # 恢复音量
            try:
                if self.unadjusted_volume:
                    self.setVolume(self.unadjusted_volume)
            except Exception as e:
                self.logger.warning(f'恢复音量失败: {str(e)}')
                if ret == 'success':
                    ret = 'err_volume_rec'

        return ret

    def playWithScript(self):
        """播放新闻，带脚本"""
        self.playNews()
        if self.additional_script:
            self.logger.info('启动附加脚本...')
            bat_path = Path(Utils.get_bundle_dir() / self.additional_script)
            try:
                subprocess.run([bat_path], check=True)
            except subprocess.CalledProcessError as e:
                self.logger.error(f'运行附加脚本失败: {str(e)}')
                return None
            except FileNotFoundError:
                self.logger.error(f'未找到附加脚本: {bat_path}')

    def playWithThread(self):
        """线程：播放新闻，防止堵塞"""
        now = datetime.datetime.now()
        if not (self.no_weekend_play and now.weekday() >= 6):
            play_thread = threading.Thread(target=self.playWithScript)
            play_thread.start()
        else:
            self.logger.info('周末不自动播放新闻')

    def setSchedule(self):
        """设置计划播放任务"""
        schedule.every().day.at(self.play_time).do(self.playWithThread)
        self.timer = QTimer()
        self.timer.timeout.connect(schedule.run_pending)
        self.timer.start(100)
        self.logger.info('已设置计划播放任务')
