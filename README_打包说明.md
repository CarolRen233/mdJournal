# 打包日记应用为可执行文件

## 方法一：使用批处理文件（推荐）

1. 双击运行 `build.bat` 文件
2. 等待打包完成
3. 可执行文件会生成在桌面，名为 `日记.exe`

## 方法二：手动打包

1. 安装 PyInstaller（如果还没安装）：
   ```bash
   pip install pyinstaller
   ```

2. 运行打包命令：
   ```bash
   pyinstaller --onefile --windowed --name=日记 --distpath=%USERPROFILE%\Desktop --clean --noconfirm diary_gui.py
   ```

3. 打包完成后，在桌面找到 `日记.exe` 文件

## 注意事项

- 首次打包可能需要几分钟时间
- 打包后的 exe 文件可能比较大（因为包含了 Python 解释器和所有依赖）
- 如果遇到问题，可以尝试：
  - 更新 PyInstaller: `pip install --upgrade pyinstaller`
  - 检查是否有杀毒软件拦截
  - 查看打包过程中的错误信息

