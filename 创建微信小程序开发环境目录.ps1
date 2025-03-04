# 进入项目根目录（假设当前目录已经是项目根目录）
cd E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE

# 创建 miniprogram 目录
mkdir miniprogram

# 进入 miniprogram 目录
cd miniprogram

# 创建小程序页面目录
mkdir pages
mkdir pages/index
mkdir pages/query
mkdir pages/upload
mkdir pages/profile

# 创建小程序全局文件
New-Item -Path app.js -ItemType File
New-Item -Path app.json -ItemType File
New-Item -Path app.wxss -ItemType File
New-Item -Path project.config.json -ItemType File

# 创建页面文件
New-Item -Path pages/index/index.wxml -ItemType File
New-Item -Path pages/index/index.wxss -ItemType File
New-Item -Path pages/index/index.js -ItemType File
New-Item -Path pages/index/index.json -ItemType File

New-Item -Path pages/query/query.wxml -ItemType File
New-Item -Path pages/query/query.wxss -ItemType File
New-Item -Path pages/query/query.js -ItemType File
New-Item -Path pages/query/query.json -ItemType File

New-Item -Path pages/upload/upload.wxml -ItemType File
New-Item -Path pages/upload/upload.wxss -ItemType File
New-Item -Path pages/upload/upload.js -ItemType File
New-Item -Path pages/upload/upload.json -ItemType File

New-Item -Path pages/profile/profile.wxml -ItemType File
New-Item -Path pages/profile/profile.wxss -ItemType File
New-Item -Path pages/profile/profile.js -ItemType File
New-Item -Path pages/profile/profile.json -ItemType File

# 输出完成信息
Write-Host "miniprogram 目录及相关文件已创建完成！"