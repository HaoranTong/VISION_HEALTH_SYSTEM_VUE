# 开发文档目录结构250304

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
│   │   ├── 📄 sidebar_api.py
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
│   │   │   ├── 📄 bootstrap-icons.css
│   │   │   ├── 📄 core.css
│   │   │   ├── 📄 index.css
│   │   │   ├── 📄 query.css
│   │   │   └── 📄 student_detail.css
│   │   ├── 📁 images/
│   │   │   ├── 📄 avatar.png
│   │   ├── 📁 js/
│   │   │   ├── 📄 data_import.js
│   │   │   ├── 📄 index.js
│   │   │   └── 📄 query.js
│   │   ├── 📁 uploads/
│   │   ├── 📄 __init__.py
│   │   └── 📄 favicon.ico
│   ├── 📁 templates/
│   │   ├── 📁 components/
│   │   │   ├── 📁 sidebar/
│   │   │   │   ├── 📄 sidebar.html
│   │   │   └── 📁 topnav/
│   │   │   │   └── 📄 topnav.html
│   │   ├── 📁 layouts/
│   │   │   ├── 📄 base.html
│   │   ├── 📄 data_import.html
│   │   ├── 📄 index.html
│   │   ├── 📄 query.html
│   │   └── 📄 student_detail.html
│   ├── 📄 __init__.py
│   ├── 📄 package-lock.json
│   ├── 📄 package.json
│   └── 📄 vite.config.js
├── 📁 instance/
│   ├── 📄 __init__.py
│   └── 📄 test.db
├── 📁 migrations/
│   ├── 📁 versions/
│   │   ├── 📄 013cca489fe0_create_student_extensions_table.py
│   │   ├── 📄 6bd616c6417c_add_extra_fields_to_student_model.py
│   │   └── 📄 ff6682b2db83_initial_migration.py
│   ├── 📄 alembic.ini
│   ├── 📄 env.py
│   ├── 📄 README
│   └── 📄 script.py.mako
├── 📁 miniprogram/
│   ├── 📁 pages/
│   │   ├── 📁 index/
│   │   │   ├── 📄 index.js
│   │   │   ├── 📄 index.json
│   │   │   ├── 📄 index.wxml
│   │   │   └── 📄 index.wxss
│   │   ├── 📁 profile/
│   │   │   ├── 📄 profile.js
│   │   │   ├── 📄 profile.json
│   │   │   ├── 📄 profile.wxml
│   │   │   └── 📄 profile.wxss
│   │   ├── 📁 query/
│   │   │   ├── 📄 query.js
│   │   │   ├── 📄 query.json
│   │   │   ├── 📄 query.wxml
│   │   │   └── 📄 query.wxss
│   │   └── 📁 upload/
│   │   │   └── 📄 upload.js
│   │   │   ├── 📄 upload.json
│   │   │   ├── 📄 upload.wxml
│   │   │   └── 📄 upload.wxss
│   ├── 📁 utils/
│   │   ├── 📄 auth.js
│   ├── 📄 app.js
│   ├── 📄 app.json
│   ├── 📄 app.wxss
│   ├── 📄 project.config.json
│   └── 📄 project.private.config.json
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
├── 📄 创建微信小程序开发环境目录.ps1
├── 📄 代码加载和功能影响.md
├── 📄 导航栏组件设计方案.md
├── 📄 开发过程记录.md
├── 📄 开发技术环境说明.md
├── 📄 数据字段映射表250304.md
├── 📄 提示词总结记录.md
├── 📄 最小功能（MVP）版本开发计划.md
├── 📄 app.db
├── 📄 app.log
├── 📄 app.py
├── 📄 database.db
├── 📄 deepseek_cli.py
├── 📄 directory_structure_250304.md
├── 📄 fix_directory.py
├── 📄 gds.ps1
├── 📄 KIMI总结的技术方案.md
├── 📄 package-lock.json
├── 📄 requirements.in
├── 📄 requirements.txt
├── 📄 reset_db.py
├── 📄 run.ps1
├── 📄 test.py
└── 📄 VISION_HEALTH_SYSTEM.code-workspace
