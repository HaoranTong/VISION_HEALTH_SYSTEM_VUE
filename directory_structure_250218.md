# 开发文档目录结构250218

# 📂 根目录路径
\\\
E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE
\\\

# 📁 目录结构
├── 📁 backend/
│   ├── 📁 api/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 analysis_api.py
│   │   ├── 📄 calculation_api.py
│   │   ├── 📄 import_api.py
│   │   ├── 📄 query_api.py
│   │   └── 📄 student_api.py
│   ├── 📁 core/
│   │   ├── 📄 __init__.py
│   ├── 📁 infrastructure/
│   │   ├── 📄 __init__.py
│   │   └── 📄 database.py
│   ├── 📁 models/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 models.py
│   │   ├── 📄 student_extension.py
│   │   └── 📄 student.py
│   ├── 📁 services/
│   │   ├── 📄 __init__.py
│   ├── 📁 tests/
│   │   ├── 📄 __init__.py
│   ├── 📄 __init__.py
│   ├── 📄 config.py
│   └── 📄 requirements.txt
├── 📁 config/
│   ├── 📁 app/
│   │   ├── 📄 __init__.py
│   │   └── 📄 config.py
│   ├── 📁 security_rules/
│   │   ├── 📄 __init__.py
│   └── 📄 __init__.py
├── 📁 docker/
│   ├── 📄 __init__.py
├── 📁 frontend/
│   ├── 📁 static/
│   │   ├── 📁 components/
│   │   │   ├── 📁 sidebar/
│   │   │   │   ├── 📄 sidebar.css
│   │   │   │   └── 📄 sidebar.js
│   │   │   └── 📁 topnav/
│   │   │   │   └── 📄 topnav.css
│   │   │   │   └── 📄 topnav.js
│   │   ├── 📁 css/
│   │   │   ├── 📄 main.css
│   │   │   └── 📄 student_detail.css
│   │   ├── 📁 images/
│   │   │   ├── 📄 avatar.png
│   │   ├── 📁 js/
│   │   └── 📄 __init__.py
│   ├── 📁 templates/
│   │   ├── 📁 components/
│   │   │   ├── 📁 sidebar/
│   │   │   │   ├── 📄 sidebar.html
│   │   │   └── 📁 topnav/
│   │   │   │   └── 📄 topnav.html
│   │   ├── 📄 index.html
│   │   └── 📄 student_detail.html
│   ├── 📄 __init__.py
│   ├── 📄 package-lock.json
│   ├── 📄 package.json
│   └── 📄 vite.config.js
├── 📁 instance/
│   ├── 📄 __init__.py
│   └── 📄 app.db
├── 📁 migrations/
│   ├── 📁 versions/
│   │   ├── 📄 013cca489fe0_create_student_extensions_table.py
│   │   ├── 📄 6bd616c6417c_add_extra_fields_to_student_model.py
│   │   └── 📄 ff6682b2db83_initial_migration.py
│   ├── 📄 alembic.ini
│   ├── 📄 env.py
│   ├── 📄 README
│   └── 📄 script.py.mako
├── 📁 scripts/
│   ├── 📄 __init__.py
│   └── 📄 README.md
├── 📁 tests/
│   ├── 📁 e2e/
│   │   ├── 📄 __init__.py
│   ├── 📁 integration/
│   │   ├── 📄 __init__.py
│   ├── 📁 test-data/
│   │   ├── 📄 测试-1.xlsx
│   │   ├── 📄 测试数据-3.xlsx
│   │   ├── 📄 测试数据-4.xlsx
│   │   └── 📄 text-2.xlsx
│   ├── 📁 unit/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 test_import_api.py
│   │   ├── 📄 test_query_api.py
│   │   └── 📄 test_student_api.py
│   ├── 📄 __init__.py
│   └── 📄 conftest.py
├── 📄 .editorconfig
├── 📄 .python-version
├── 📄 导航栏组件设计方案.md
├── 📄 app.py
├── 📄 deepseek_cli.py
├── 📄 Deepseek修正开发目录结构-flask+HTML架构.md
├── 📄 directory_structure_250218.md
├── 📄 fix_directory.py
├── 📄 gds.ps1
├── 📄 package-lock.json
├── 📄 requirements.in
├── 📄 requirements.txt
└── 📄 VISION_HEALTH_SYSTEM.code-workspace


以上是开发环境文档结构目录
我的开发环境是WIndows操作系统，编码工具是vscode+powershell集成终端，编程语言是Python3.10.10，技术栈是HTML/CSS/JavaScript后端采用Flask，有Bootstrap等依赖库，还有数据库。我要开发的是“近视预防干预系统”数据管理软件

请整理上述信息到长期记忆中

