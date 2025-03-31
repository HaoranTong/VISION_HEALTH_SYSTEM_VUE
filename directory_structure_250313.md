# 开发文档目录结构250313

# 📂 根目录路径
\\\
E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE\
\\\

# 📁 目录结构
├── 📁 backend/
│   ├── 📁 api/
│   │   ├── 📄 __init__.py
│   │   ├── 📄 测试git
│   │   ├── 📄 analysis_api-1.py
│   │   ├── 📄 analysis_api.py
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
│   │   └── 📄 vision_calculation.py
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
│   │   │   ├── 📄 chart.css
│   │   │   ├── 📄 comboQuery.css
│   │   │   ├── 📄 core.css
│   │   │   ├── 📄 index.css
│   │   │   ├── 📄 query.css
│   │   │   ├── 📄 report.css
│   │   │   └── 📄 student_detail.css
│   │   ├── 📁 images/
│   │   │   ├── 📄 avatar.png
│   │   ├── 📁 js/
│   │   │   ├── 📄 chart.js
│   │   │   ├── 📄 comboQuery_report.js
│   │   │   ├── 📄 comboQuery.js
│   │   │   ├── 📄 data_import.js
│   │   │   ├── 📄 index.js
│   │   │   ├── 📄 query.js
│   │   │   ├── 📄 report-1.js
│   │   │   └── 📄 report.js
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
│   │   ├── 📄 chart.html
│   │   ├── 📄 comboQuery.html
│   │   ├── 📄 data_import.html
│   │   ├── 📄 index.html
│   │   ├── 📄 query.html
│   │   ├── 📄 report-1.html
│   │   ├── 📄 report.html
│   │   └── 📄 student_detail.html
│   ├── 📄 __init__.py
│   ├── 📄 package-lock.json
│   ├── 📄 package.json
│   └── 📄 vite.config.js
├── 📁 instance/
│   ├── 📄 __init__.py
│   ├── 📄 app.db
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
│   ├── 📄 export_mapping_table.py
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
├── 📄 app.log
├── 📄 app.py
├── 📄 directory_structure_250313.md
├── 📄 requirements.in
├── 📄 requirements.txt
├── 📄 run.ps1
└── 📄 VISION_HEALTH_SYSTEM.code-workspace
