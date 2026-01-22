"""
使用 PyInstaller 打包日记应用为可执行文件
"""
import PyInstaller.__main__
import os
import sys

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

PyInstaller.__main__.run([
    'diary_gui.py',
    '--onefile',  # 打包成单个文件
    '--windowed',  # 不显示控制台窗口
    '--name=日记',  # 可执行文件名称
    f'--distpath={desktop_path}',  # 输出到桌面
    '--clean',  # 清理临时文件
    '--noconfirm',  # 不询问确认
    '--add-data=requirements.txt;.',  # 包含requirements.txt（如果需要）
])

print(f"\n可执行文件已生成到桌面: {desktop_path}\\日记.exe")

