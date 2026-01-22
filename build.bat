@echo off
chcp 65001 >nul
echo 正在打包日记应用为可执行文件...
echo.

REM 检查是否安装了 PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo 正在安装 PyInstaller...
    pip install pyinstaller
)

REM 获取桌面路径
set DESKTOP=%USERPROFILE%\Desktop

REM 打包应用
pyinstaller --onefile --windowed --name=日记 --distpath=%DESKTOP% --clean --noconfirm diary_gui.py

if exist "%DESKTOP%\日记.exe" (
    echo.
    echo ✓ 打包成功！
    echo 可执行文件位置: %DESKTOP%\日记.exe
    echo.
    pause
) else (
    echo.
    echo ✗ 打包失败，请检查错误信息
    echo.
    pause
)

