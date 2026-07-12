@echo off

:: 解除文件占用
taskkill /im AutoNewsPlayer.exe /f >nul 2>&1

:: 清空文件夹
if exist "build\AutoNewsPlayer" (
    rd /s /q "build\AutoNewsPlayer" >nul
)

:: 开始打包
pyinstaller --distpath build --workpath %PYINSTALLER_CACHE_DIR% --noconfirm AutoNewsPlayer.spec

copy assets\config.jsonc build\AutoNewsPlayer\config.jsonc
copy assets\icon.ico build\AutoNewsPlayer\_internal\icon.ico
copy assets\Stop.bat build\AutoNewsPlayer\Stop.bat
