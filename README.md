# AutoNewsPlayer

> 自动化新闻播放系统 —— 定时播放、无人值守、智能广告跳过，专为学校、企业、公共大屏场景设计

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)](https://www.python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green?logo=qt)](https://www.riverbankcomputing.com/software/pyqt/)
[![Selenium](https://img.shields.io/badge/Selenium-4.0+-43B02A?logo=selenium)](https://www.selenium.dev/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows-blue?logo=windows)](https://www.microsoft.com/windows)

---

## 📖 项目简介

**AutoNewsPlayer（自动新闻播放器）** 是一款基于 Python + PyQt5 开发的自动化新闻播放系统，专为学校、企业、公共场所的大屏展示和自动播放场景设计。项目解决了公共区域定时播放新闻资讯时需人工值守、广告干扰、播放源切换不便等痛点，实现了**全自动定时播放、智能跳过广告、开机自启动、无人值守运行**等核心能力。

AutoNewsPlayer 以中央电视台（CCTV）的《新闻30分》和《今日说法》两个节目为主要播放源，通过 Selenium 自动化框架控制 Chrome 浏览器，实现页面加载、视频定位、播放控制、进度跳转、广告检测与跳过等复杂操作。同时，项目内置了美观的配置管理界面（PyQt5），支持播放时间、播放时长、音量、视频源等参数的灵活配置，并提供了自动化测试功能，方便管理员验证播放流程。

项目基于 **Python 3.8+** 开发，采用 **PyQt5** 构建图形界面，使用 **Selenium** 驱动 Chrome 浏览器，通过 **pycaw** 控制系统音量，支持 Windows 7/10/11 系统，可通过 PyInstaller 打包为独立可执行文件，方便学校信息老师或企业 IT 管理员快速部署。

---

## ✨ 功能特性

| 功能模块            | 描述                                                                |
| ------------------- | ------------------------------------------------------------------- |
| ⏰ **定时自动播放** | 支持设置每日固定播放时间（如 18:50:00），到点自动启动浏览器播放新闻 |
| 📺 **双视频源支持** | 支持《新闻30分》和《今日说法》两个节目源，可手动选择或每天轮播切换  |
| 🎯 **智能进度跳转** | 根据设定的播放时长，自动计算并跳转到视频对应时间点，无需从头播放    |
| 🚫 **自动广告跳过** | 智能检测视频播放中的广告，自动刷新页面并重试，最大可配置检测次数    |
| 🔊 **系统音量控制** | 自动调节系统音量至预设值，播放完毕后恢复原始音量                    |
| 🖥️ **全屏自动播放** | 自动将浏览器切换至全屏模式，适合大屏展示场景                        |
| 📌 **右下角提示窗** | 播放时在屏幕右下角显示提示信息，告知用户当前播放状态                |
| 🧪 **自动化测试**   | 内置自动化测试功能，支持配置测试次数和播放时长，验证播放流程稳定性  |
| ⚙️ **灵活配置管理** | 通过图形界面配置播放时间、时长、音量、视频源、广告检测参数等        |
| 🔄 **开机自启动**   | 支持一键设置开机自启动，程序启动后自动进入定时播放模式              |
| 📦 **一键打包部署** | 内置 `BUILD.BAT` 和 PyInstaller 配置，可快速打包为 `exe` 单文件     |

---

## 🛠️ 技术栈

| 类别              | 技术                              |
| ----------------- | --------------------------------- |
| **编程语言**      | Python 3.8+                       |
| **GUI 框架**      | PyQt5 5.15+                       |
| **浏览器自动化**  | Selenium 4.0+                     |
| **浏览器引擎**    | Chrome for Testing + ChromeDriver |
| **音量控制**      | pycaw + COM 接口                  |
| **进程/窗口管理** | pywin32、psutil                   |
| **定时调度**      | schedule                          |
| **日志系统**      | colorlog（彩色控制台输出）        |
| **注册表操作**    | winreg（Windows 注册表 API）      |
| **打包工具**      | PyInstaller                       |
| **开发环境**      | VS Code（含调试配置）             |
| **平台支持**      | Windows 7/10/11                   |

---

## 🚀 快速开始

### 前置条件

- Python 3.8+（如需源码运行）
- Windows 操作系统
- Chrome 浏览器（自动测试版，包含 `chrome.exe` 和 `chromedriver.exe`）

### 源码运行

```bash
# 1. 克隆项目
git clone https://github.com/yangsongh/AutoNewsPlayer.git
cd AutoNewsPlayer

# 2. 创建虚拟环境（推荐）
python -m venv .venv
.venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 准备 Chrome for Testing
# 从 https://googlechromelabs.github.io/chrome-for-testing/ 下载对应版本
# 将 chrome.exe 和 chromedriver.exe 放置在项目根目录下的 chrome/ 文件夹中

# 5. 运行程序
python src/Main.py          # 正常模式（显示主窗口）
python src/Main.py --autorun # 自启动模式（后台运行）
```

### 基本使用

1. **配置播放参数**：启动程序后，在主界面设置播放时间、播放时长、音量、默认视频源等
2. **启用定时播放**：配置完成后，程序将在设定的时间自动启动浏览器播放新闻
3. **自动化测试**：点击「今日说法」或「新闻30分」测试按钮，可验证播放流程
4. **开机自启动**：勾选「开机自启动」选项，程序将在系统启动时自动运行

---

## 📁 项目结构

```
AutoNewsPlayer/
├── src/                          # 🚀 源代码目录
│   ├── Main.py                   # 程序入口
│   ├── modules/
│   │   └── auto_news_player.py   # 核心播放逻辑
│   ├── utils/
│   │   ├── browser.py            # Chrome 浏览器启动与操作
│   │   └── utils_lib.py          # 通用工具类（日志、配置、系统工具）
│   └── windows/
│       ├── Main.py               # 主窗口逻辑
│       ├── Notification.py       # 右下角提示窗口
│       └── ui/
│           ├── Ui_Main.py        # 主窗口 UI（由 Qt Designer 生成）
│           └── Ui_Notification.py # 提示窗口 UI（由 Qt Designer 生成）
├── assets/                       # 📂 资源文件
│   ├── config.jsonc              # 配置文件（支持 JSON with Comments）
│   ├── config_example.jsonc      # 配置文件示例
│   ├── icon.ico                  # 应用程序图标
│   └── Stop.bat                  # 停止脚本
├── build/                        # 📦 打包输出目录
├── .vscode/                      # 💻 VS Code 调试配置
│   ├── launch.json               # 调试启动配置
│   └── settings.json             # 项目工作区设置
├── requirements.txt              # Python 依赖清单
├── AutoNewsPlayer.spec           # PyInstaller 打包配置
├── BUILD.BAT                     # 一键打包脚本
└── LICENSE                       # MIT 许可证
```

---

## ⚙️ 配置说明

### 配置文件 (`assets/config.jsonc`)

配置文件采用 JSON with Comments 格式，支持注释，便于理解各配置项的含义。

```jsonc
{
  /* 默认配置 */
  "default": {
    "play_time": "18:48:00", // 播放时间 (HH:MM:SS)
    "play_duration": 15, // 播放时长 (分钟)
    "video_source": "[auto_switch]", // 视频源 ("[auto_switch]" 表示自动轮播)
    "volume": 0.8, // 音量 (0-1)
    "no_weekend_play": true, // 周末不播放
    "hide_progress_bar": false, // 是否隐藏进度条
    "show_notice_win": true, // 显示右下角提示窗
    "color_theme": "dark", // 颜色主题 (dark/light)
    "additional_script": "", // 附加脚本 (播放完成后运行)

    /* 广告检测设置 */
    "ad_settings": {
      "max_ad_check": 5, // 最大检测次数
      "ad_check_wait": 1.5, // 检测延迟 (秒)
    },

    /* 内部配置 (一般无需修改) */
    "total_duration": 30, // 视频总时长 (分钟)
    "fail_auto_switch_source": true, // 播放失败后自动切换节目源
    "xw30f_url": "https://tv.cctv.com/lm/xw30f/",
    "jrsf_url": "https://tv.cctv.com/lm/jrsf/index.shtml",
    "browser_title": "Google Chrome for Testing",
    "xw30f_beforehand_close_sec": 10, // 新闻30分提前关闭秒数
    "jrsf_beforehand_close_sec": 20, // 今日说法提前关闭秒数
  },

  /* 自动化测试配置 */
  "auto_test": {
    "test_times": 1, // 测试次数
    "play_duration": 15, // 测试时长 (分钟)
  },
}
```

### 配置项说明

| 配置项              | 类型    | 说明                                                                              |
| ------------------- | ------- | --------------------------------------------------------------------------------- |
| `play_time`         | string  | 每日定时播放时间，格式为 `HH:MM:SS`                                               |
| `play_duration`     | number  | 实际播放时长（分钟），程序将跳转到视频对应位置                                    |
| `video_source`      | string  | 视频源，可选 `XW30F`（新闻30分）、`JRSF`（今日说法）、`[auto_switch]`（每日轮播） |
| `volume`            | number  | 播放音量，取值范围 `0.0` ~ `1.0`                                                  |
| `no_weekend_play`   | boolean | `true` 表示周六日不自动播放                                                       |
| `hide_progress_bar` | boolean | `true` 表示隐藏视频进度条（适合公开场景）                                         |
| `show_notice_win`   | boolean | `true` 表示播放时显示右下角提示窗口                                               |
| `max_ad_check`      | number  | 广告检测最大重试次数                                                              |
| `ad_check_wait`     | number  | 每次广告检测后等待时间（秒）                                                      |

### Chrome 定制版目录配置

程序会按以下顺序自动查找 Chrome 目录：

```
./chrome
../chrome
../../chrome
../../../chrome
../../../../chrome
../../../../../chrome
```

建议将 `chrome.exe` 和 `chromedriver.exe` 放置在项目根目录下的 `chrome/` 文件夹中，或打包后的同级目录下。

---

## 🧪 自动化测试

AutoNewsPlayer 内置了自动化测试功能，可用于验证播放流程的稳定性：

1. 在主界面「自动化测试」区域，输入测试次数和播放时长
2. 点击「今日说法」或「新闻30分」按钮开始测试
3. 程序将自动执行多次播放测试，并记录日志

测试过程中，程序会执行完整的播放流程，包括：

- 启动浏览器并访问对应节目页面
- 查找并点击最新一期视频
- 跳转到指定播放位置
- 检测并跳过广告
- 进入全屏模式
- 监测播放进度并提前关闭

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 代码规范

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 代码风格
- 类名使用大驼峰命名（如 `AutoNewsPlayer`）
- 方法名使用蛇形命名（如 `checkAndSkipVideoAd`）
- 添加必要的注释说明关键逻辑
- 提交前确保程序在 Windows 下正常运行

### 提交 Pull Request

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- **无痕芳华** —— 项目开发者与维护者
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) —— 强大的 Python GUI 框架
- [Selenium](https://www.selenium.dev/) —— 浏览器自动化框架
- [PyInstaller](https://www.pyinstaller.org/) —— 应用打包工具
- [pycaw](https://github.com/AndreMiras/pycaw) —— Windows 音量控制库

---

## 📮 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 [GitHub Issue](https://github.com/yangsongh/AutoNewsPlayer/issues)
- 邮件联系：18675864731@163.com

---

> **提示**：如需修改播放源 URL、广告检测参数或内部配置，请直接编辑 `assets/config.jsonc` 文件。如需深度定制，欢迎提交 Issue 讨论。
