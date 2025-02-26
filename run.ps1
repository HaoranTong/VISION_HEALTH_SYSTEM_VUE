# 文件名称：run.ps1
# 完整路径：E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\run.ps1
# 功能说明：无警告启动脚本，使用生产服务器运行

$env:VIRTUAL_ENV = "E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\.venv"
& "$env:VIRTUAL_ENV\Scripts\Activate.ps1"

# 清理环境变量
$env:FLASK_APP = $null
$env:FLASK_DEBUG = $null
$env:PYTHONWARNINGS = "ignore"

# 启动生产服务器
waitress-serve --host=0.0.0.0 --port=5000 --call app:create_app