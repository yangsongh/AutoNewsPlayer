@echo off

:: 解除文件占用
taskkill /im AutoNewsPlayer.exe /f >nul 2>&1

:: 清空文件夹
if exist "build\AutoNewsPlayer" (
    rd /s /q "build\AutoNewsPlayer" >nul
)

:: 开始打包
pyinstaller --distpath build --workpath %PYINSTALLER_CACHE_DIR% --noconfirm AutoNewsPlayer.spec

:: 复制文件
xcopy %PYTHON_VENV_DIR%\AutoNewsPlayer\Lib\site-packages\selenium\webdriver\common build\AutoNewsPlayer\_internal\selenium\webdriver\common /E /H /C /I /Y
xcopy %PYTHON_VENV_DIR%\AutoNewsPlayer\Lib\site-packages\selenium\webdriver\chrome build\AutoNewsPlayer\_internal\selenium\webdriver\chrome /E /H /C /I /A /Y
xcopy %PYTHON_VENV_DIR%\AutoNewsPlayer\Lib\site-packages\selenium\webdriver\chromium build\AutoNewsPlayer\_internal\selenium\webdriver\chromium /E /H /C /I /A /Y

copy assets\config.jsonc build\AutoNewsPlayer\config.jsonc
copy assets\icon.ico build\AutoNewsPlayer\_internal\icon.ico
copy assets\Stop.bat build\AutoNewsPlayer\Stop.bat
