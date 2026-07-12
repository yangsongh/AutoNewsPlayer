import os
import time

from typing import Callable, Optional
from utils.utils_lib import LoggerManager, Utils

from selenium.webdriver.chrome import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement

def getChromeDir():
    """查找 chrome 目录，按层级顺序尝试可能的路径"""
    base_dir = Utils.get_bundle_dir()
    rel_paths = [
        './chrome',
        '../chrome',
        '../../chrome',
        '../../../chrome',
        '../../../../chrome',
        '../../../../../chrome'
    ]
    for rel_path in rel_paths:
        chromedriver_dir = os.path.join(base_dir, rel_path)
        if os.path.exists(chromedriver_dir):
            return chromedriver_dir
    return os.path.join(base_dir, rel_paths[(-1)])


def getChromedriverPath():
    chromedriver_path = os.path.join(getChromeDir(), 'chromedriver.exe')
    return chromedriver_path


def getChromeBinaryPath():
    chrome_path = os.path.join(getChromeDir(), 'chrome.exe')
    return chrome_path


def clickElement(logger, element: WebElement, max_retries=20, wait_time=0.0, fail_callback: Optional[Callable] = None):
    retries = 0
    while retries < max_retries:
        try:
            element.click()
            logger.info('成功点击元素')
        except Exception as e:
            if fail_callback:
                logger.warning('元素点击失败，执行回调函数')
                fail_callback()
            error_msg = str(e).split('Stacktrace:')[0]
            logger.warning(
                f'元素点击失败，正在重试（第 {retries + 1}/{max_retries} 次）| 错误: {error_msg}')
            retries += 1
            time.sleep(wait_time)
        else:
            return True
    logger.error(f'超过最大重试次数（{max_retries} 次），点击失败')
    return False


def startChrome(logger: LoggerManager):
    """启动 Chrome 浏览器"""
    chromedriver_path = getChromedriverPath()
    chrome_binary_path = getChromeBinaryPath()
    logger.info(f'使用的 ChromeDriver 路径: {chromedriver_path}')
    logger.info(f'使用的 Chrome 二进制路径: {chrome_binary_path}')
    try:
        options = Options()
        options.binary_location = chrome_binary_path
        options.add_argument('log-level=3')
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option(
            'excludeSwitches', ['enable-automation'])
        options.add_argument('--start-maximized')
        service = Service(chromedriver_path)
        driver = webdriver.WebDriver(
            service=service, options=options)  # type: ignore
        logger.debug('浏览器已启动')
        return driver
    except Exception as e:
        logger.error(
            f"启动浏览器失败: {str(e).split('Stacktrace:')[0]}", exc_info=True)
