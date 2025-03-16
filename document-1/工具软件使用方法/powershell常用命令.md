以下是针对 PowerShell 终端的常用命令行操作，你可以用来进行项目的管理、开发和调试。

### 1. **安装依赖**

在 PowerShell 中，进入项目根目录后，执行以下命令来安装项目的依赖：

```powershell
# 安装 requirements.txt 中列出的 Python 依赖
pip install -r requirements.txt
```

### 2. **运行 Flask 应用**

通过 PowerShell 启动 Flask 应用：

```powershell
# 运行 Flask 应用
python -m flask run
```

### 3. **使用 Flask-Migrate 初始化数据库**

如果你使用 Flask-Migrate 进行数据库迁移，首先要确保 `flask db` 命令有效，可以按如下命令初始化数据库：

```powershell
# 初始化数据库迁移
flask db init
```

之后，使用以下命令创建迁移脚本：

```powershell
# 创建数据库迁移脚本
flask db migrate -m "initial migration"
```

然后应用数据库迁移：

```powershell
# 应用数据库迁移
flask db upgrade
```

### 4. **安装 Vue.js 项目的依赖**

在 Vue 项目目录下运行以下命令来安装前端依赖：

```powershell
# 进入 frontend 目录
cd frontend

# 安装 Vue 项目的依赖
npm install
```

### 5. **运行 Vue.js 项目**

启动 Vue.js 开发服务器来运行前端项目：

```powershell
# 进入 frontend 目录
cd frontend

# 运行 Vue 开发服务器
npm run dev
```

### 6. **检查当前 Python 环境**

查看当前虚拟环境或系统 Python 的版本：

```powershell
# 检查 Python 版本
python --version
```

### 7. **清理 Python 缓存**

有时在使用 Python 时，可能需要清理缓存，可以运行以下命令：

```powershell
# 删除 Python 的缓存
python -m compileall -f .
```

### 8. **激活/退出虚拟环境**

你可以通过以下命令激活和退出虚拟环境。

```powershell
# 激活虚拟环境
.venv\Scripts\Activate

# 退出虚拟环境
deactivate
```

### 9. **运行单元测试**

在 PowerShell 中，你可以运行单元测试。以下命令运行所有测试：

```powershell
# 运行所有单元测试
pytest
```

如果你需要运行特定的测试文件或测试方法：

```powershell
# 运行特定测试文件
pytest path\to\test_file.py

# 运行特定测试方法
pytest path\to\test_file.py::test_method
```

### 10. **清理临时目录或文件**

如果你想清理临时文件或缓存，可以使用以下命令删除 `.pyc` 文件等：

```powershell
# 删除所有 Python 的 .pyc 文件
Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item
```

### 11. **检查文件路径和文件夹**

你可以用 PowerShell 来查看目录结构和文件内容：

```powershell
# 查看当前目录内容
Get-ChildItem

# 查看某个文件夹内容
Get-ChildItem -Path "path\to\folder"

# 查看当前目录的文件结构
tree
```

### 12. **查看端口占用情况**

如果你发现 Flask 应用启动失败，可能是端口被占用，可以使用以下命令查看端口占用情况：

```powershell
# 查看端口是否被占用
netstat -ano | findstr :5000
```

如果端口被占用，可以结束相关进程：

```powershell
# 停止占用端口的进程
taskkill /PID <PID> /F
```

------

这些命令可以帮助你在 PowerShell 中管理你的 Flask 项目，运行测试，启动开发服务器，以及进行常见的调试工作。如果你有其他的命令需求或开发问题，请随时告诉我！