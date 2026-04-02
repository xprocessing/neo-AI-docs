# MacOS 中 Python 的 Pip 问题及解决方案

从你的终端输出可以看到，你的 Mac 系统里能正常运行 Python 3.14.2，但找不到 `pip` 命令，这是 macOS 上使用 Python 很常见的问题。我来帮你解决这个问题。

### 问题原因

macOS 系统中，Python 3 的 pip 命令通常需要用 `pip3` 来调用（而不是 `pip`），或者你的 Python 环境没有正确配置环境变量。

### 解决方案

#### 方案 1：直接使用 pip3（最推荐）

这是最简单直接的方式，直接在终端执行：

```Bash

# 检查 pip3 是否可用
pip3 --version

# 使用 pip3 安装包（示例：安装 requests）
pip3 install requests

# 如果需要升级 pip3 本身
pip3 install --upgrade pip
```

#### 方案 2：创建 pip 别名（让 pip 指向 pip3）

如果你习惯用 `pip` 而不是 `pip3`，可以给 `pip3` 创建别名：

```Bash

# 临时生效（仅当前终端会话）
alias pip=pip3

# 永久生效（推荐）
echo "alias pip=pip3" >> ~/.zshrc
source ~/.zshrc
```

执行完后，你再输入 `pip --version` 就能正常显示了。

#### 方案 3：通过 Python 本身调用 pip

如果以上方法都不行，可以直接通过 Python 来调用 pip：

```Bash

# 安装包
python -m pip install requests

# 升级 pip
python -m pip install --upgrade pip
```

### 验证是否解决

执行以下命令，能正常输出版本信息就说明没问题了：

```Bash

pip --version  # 或 pip3 --version
```

### 总结

1. macOS 下 Python 3 的 pip 命令默认是 `pip3`，而非 `pip`；

2. 最便捷的解决方式是直接使用 `pip3` 或给 `pip3` 创建 `pip` 别名；

3. 兜底方案是通过 `python -m pip` 方式调用 pip，兼容性最好。

如果执行过程中遇到权限错误（比如 `Permission denied`），可以在命令后加 `--user` 参数（如 `pip3 install --user requests`），避免使用 `sudo`（可能会破坏系统 Python 环境）。
> （注：文档部分内容可能由 AI 生成）