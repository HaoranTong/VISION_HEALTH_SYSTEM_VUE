# 定义项目根目录路径
$projectRoot = "E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM"

# 创建项目根目录及主要子目录
New-Item -ItemType Directory -Force -Path $projectRoot
New-Item -ItemType Directory -Force -Path "$projectRoot\config\app"
New-Item -ItemType Directory -Force -Path "$projectRoot\config\security_rules"
New-Item -ItemType Directory -Force -Path "$projectRoot\docker"
New-Item -ItemType Directory -Force -Path "$projectRoot\docs"
New-Item -ItemType Directory -Force -Path "$projectRoot\frontend\vscode-extension\src\commands"
New-Item -ItemType Directory -Force -Path "$projectRoot\frontend\vscode-extension\src\core"
New-Item -ItemType Directory -Force -Path "$projectRoot\frontend\vscode-extension\src\webviews\components"
New-Item -ItemType Directory -Force -Path "$projectRoot\scripts"
New-Item -ItemType Directory -Force -Path "$projectRoot\src\context_system\api\endpoints"
New-Item -ItemType Directory -Force -Path "$projectRoot\src\context_system\core\managers"
New-Item -ItemType Directory -Force -Path "$projectRoot\src\context_system\core\models"
New-Item -ItemType Directory -Force -Path "$projectRoot\src\context_system\core\services"
New-Item -ItemType Directory -Force -Path "$projectRoot\src\context_system\core\tasks"
New-Item -ItemType Directory -Force -Path "$projectRoot\src\context_system\infrastructure\cache"
New-Item -ItemType Directory -Force -Path "$projectRoot\src\context_system\infrastructure\config"
New-Item -ItemType Directory -Force -Path "$projectRoot\src\context_system\infrastructure\database"
New-Item -ItemType Directory -Force -Path "$projectRoot\src\context_system\utils"
New-Item -ItemType Directory -Force -Path "$projectRoot\tests\unit"
New-Item -ItemType Directory -Force -Path "$projectRoot\tests\integration"
New-Item -ItemType Directory -Force -Path "$projectRoot\tests\e2e"

# 创建基础文件
New-Item -ItemType File -Force -Path "$projectRoot\README.md" -Value "# VISION_HEALTH_SYSTEM"
New-Item -ItemType File -Force -Path "$projectRoot\.gitignore" -Value "venv/`n*.pyc`n__pycache__/`nnode_modules/"

Write-Host "项目目录结构已创建完成：$projectRoot"
