import os

def create_directory_structure(base_path):
    directories = [
        "backend/api", "backend/core", "backend/models", "backend/services", "backend/infrastructure",
        "backend/tests", "frontend/src/assets", "frontend/src/components", "frontend/src/pages",
        "frontend/src/router", "frontend/src/store", "frontend/src/services", "frontend/src/layouts",
        "docs", "scripts", "instance"
    ]
    
    files = {
        "backend/app.py": "# Flask 入口",
        "backend/database.py": "# 数据库初始化",
        "backend/config.py": "# 配置文件",
        "backend/requirements.txt": "# 依赖文件",
        "backend/run.py": "# 启动 Flask 服务器",
        "frontend/src/main.js": "// Vue 入口文件",
        "frontend/src/App.vue": "<!-- Vue 入口组件 -->",
        "frontend/src/router/index.js": "// 路由配置",
        "frontend/src/store/index.js": "// 状态管理",
        "frontend/src/services/api.js": "// API 请求封装",
        "frontend/index.html": "<!-- Vue 入口 HTML -->",
        "frontend/vite.config.js": "// Vite 配置文件",
        "frontend/package.json": "// 依赖管理",
        "README.md": "# 项目说明"
    }
    
    # 创建目录
    for directory in directories:
        path = os.path.join(base_path, directory)
        os.makedirs(path, exist_ok=True)
    
    # 创建文件
    for file_path, content in files.items():
        full_path = os.path.join(base_path, file_path)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    print("✅ 目录结构创建完成！")

if __name__ == "__main__":
    base_directory = os.path.abspath(".")  # 当前目录
    create_directory_structure(base_directory)
