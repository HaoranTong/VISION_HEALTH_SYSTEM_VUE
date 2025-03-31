# 文件名称：run.ps1
# 完整存储路径：E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\run.ps1
# 功能说明：无警告启动脚本，使用生产服务器运行
# 说明：
#   1. 激活指定的虚拟环境；
#   2. 设置必要的环境变量（如 PYTHONWARNINGS）以避免警告输出；
#   3. 清理不必要的调试环境变量，确保生产环境不启用调试；
#   4. 启动 waitress 生产服务器，监听 0.0.0.0:5000，调用 app:create_app 作为应用工厂函数。

# （可选）如果需要开启调试模式，请取消下面这一行的注释；生产环境建议关闭调试
$env:FLASK_DEBUG="1"

# 设置虚拟环境路径并激活虚拟环境
$env:VIRTUAL_ENV = "E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\.venv"
& "$env:VIRTUAL_ENV\Scripts\Activate.ps1"

# 设置忽略 Python 警告，避免多余输出
$env:PYTHONWARNINGS = "ignore"

# 清理不需要传递到应用中的环境变量（确保生产环境不启用调试）
$env:FLASK_APP = $null
$env:FLASK_DEBUG = $null

# 启动生产服务器
waitress-serve --host=0.0.0.0 --port=5000 --call app:create_app
