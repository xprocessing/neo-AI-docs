在Python中，将脚本打包为Windows可执行文件（`.exe`）最常用的工具是**PyInstaller**，它简单易用、兼容性好，支持单文件/目录打包、GUI程序无控制台、自定义图标等功能。以下是详细的打包命令及使用技巧：

### 一、安装PyInstaller
首先通过`pip`安装PyInstaller：
```bash
pip install pyinstaller
```
如果需要升级到最新版本：
```bash
pip install --upgrade pyinstaller
```

### 二、核心打包命令
基本语法：
```bash
pyinstaller [可选参数] 你的脚本名.py
```

#### 1. 基础打包（默认目录模式）
直接执行命令，会生成**dist**（存放exe）和**build**（临时文件）两个文件夹，exe依赖的库文件会和exe放在同一目录下：
```bash
pyinstaller your_script.py
```
- 特点：启动速度快，适合依赖较多的程序；缺点是文件分散，需整个文件夹分发。

#### 2. 单文件打包（-F/--onefile）
将所有依赖和脚本打包为**单个exe文件**，方便分发：
```bash
pyinstaller -F your_script.py
# 或
pyinstaller --onefile your_script.py
```
- 特点：仅一个exe文件，分发方便；缺点是启动时会解压临时文件，速度较慢。

#### 3. 无控制台窗口（-w/--windowed）
适用于**GUI程序**（如Tkinter、PyQt、wxPython），打包后运行exe不会弹出黑色控制台窗口：
```bash
# 单文件+无控制台
pyinstaller -F -w your_script.py
# 或
pyinstaller --onefile --windowed your_script.py
```
⚠️ 注意：控制台程序（如命令行工具）不要加`-w`，否则会无法运行。

#### 4. 自定义图标（-i/--icon）
为exe文件设置自定义图标（仅支持`.ico`格式，不支持`.png/.jpg`）：
```bash
# 单文件+无控制台+自定义图标
pyinstaller -F -w -i your_icon.ico your_script.py
```

#### 5. 自定义exe名称（-n/--name）
默认exe名称为脚本名，可通过`-n`指定新名称：
```bash
pyinstaller -F -n my_app your_script.py
```

#### 6. 清理临时文件（--clean）
打包时清理之前的临时构建文件，避免缓存问题：
```bash
pyinstaller -F --clean your_script.py
```

#### 7. 指定输出目录（--distpath）
默认exe生成在`dist`目录，可通过`--distpath`指定自定义路径：
```bash
pyinstaller -F --distpath ./output your_script.py
```

### 三、处理资源文件（如图片、配置文件）
如果脚本依赖外部资源文件（如`.txt`、`.png`、配置文件），需要通过`--add-data`（Windows）/`--add-binary`指定文件路径映射：
- **Windows**：路径分隔符用`;`（英文分号）
- **Mac/Linux**：路径分隔符用`:`

示例（Windows）：将`data`文件夹打包到exe同目录的`data`文件夹：
```bash
pyinstaller -F --add-data "data;data" your_script.py
```
示例：将单个`config.ini`文件打包到exe同目录：
```bash
pyinstaller -F --add-data "config.ini;." your_script.py
```

### 四、常见问题解决
1. **打包后exe运行提示“缺少模块”**
   - 原因：PyInstaller未自动识别某些第三方库（如`PyQt`、`pandas`的子模块）。
   - 解决：通过`--hidden-import`手动添加缺失模块，例如：
     ```bash
     pyinstaller -F --hidden-import=sklearn.utils._cython_blas your_script.py
     ```

2. **单文件exe启动慢**
   - 原因：单文件运行时会先解压所有依赖到临时目录。
   - 解决：改用目录模式（去掉`-F`），或优化代码减少依赖。

3. **杀毒软件误报病毒**
   - 原因：PyInstaller打包的exe会被部分杀毒软件误判（无实际病毒）。
   - 解决：将exe加入杀毒软件白名单，或使用专业签名工具签名exe。

4. **Python版本/位数不匹配**
   - 若在64位Python环境打包，生成的exe仅能在64位Windows运行；32位Python需安装32位依赖库，打包的exe可兼容32/64位系统。

### 五、其他打包工具
除了PyInstaller，还有以下工具可用于Python打包exe（但易用性不如PyInstaller）：
1. **cx_Freeze**：跨平台，支持Python 3.x，需手动配置`setup.py`。
2. **py2exe**：仅支持Python 2.x和早期Python 3.x，现已基本淘汰。
3. **Nuitka**：将Python代码编译为C++代码后再打包，运行速度更快，但配置复杂。

综上，**PyInstaller**是Python打包exe的首选工具，掌握上述命令即可满足绝大多数场景的需求。