# 开发文档目录结构及开发环境的说明

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
│   │   ├── 📁 layouts/
│   │   │   ├── 📄 base.html
│   │   ├── 📄 data_import.html
│   │   ├── 📄 index.html
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
├── 📄 directory_structure_250219.md
├── 📄 fix_directory.py
├── 📄 gds.ps1
├── 📄 package-lock.json
├── 📄 requirements.in
├── 📄 requirements.txt
├── 📄 run.ps1
├── 📄 test.py
└── 📄 VISION_HEALTH_SYSTEM.code-workspace

#### 开发环境

* 操作系统：WIndows 11
* 编码环境：vscode+powershell
* 代码管理：git+github
* 编程语言：Pythong 3.10.10
* 前端框架：HTML+css+JavaScript
* 后端框架：Flask
* 数据库：SQLite

#### 已经安装的依赖库

alembic             1.14.1
aniso8601           10.0.0
anyio               4.5.0
autopep8            2.3.2
certifi             2024.8.30
charset-normalizer  3.3.2
click               8.1.7
colorama            0.4.6
devchat             0.3.0
distlib             0.3.9
distro              1.9.0
dnspython           2.6.1
email_validator     2.2.0
et_xmlfile          2.0.0
exceptiongroup      1.2.2
fastapi             0.111.1
fastapi-cli         0.0.5
filelock            3.16.1
Flask               2.2.5
Flask-Migrate       4.0.4
Flask-RESTful       0.3.10
Flask-SQLAlchemy    3.0.3
gitdb               4.0.11
GitPython           3.1.43
greenlet            3.1.1
gunicorn            22.0.0
h11                 0.14.0
httpcore            1.0.5
httptools           0.6.1
httpx               0.27.2
idna                3.10
importlib-metadata  6.11.0
importlib_resources 6.4.5
itsdangerous        2.2.0
Jinja2              3.1.4
loguru              0.7.2
Mako                1.3.9
markdown-it-py      3.0.0
MarkupSafe          2.1.5
mdurl               0.1.2
mypy-extensions     1.0.0
networkx            3.1
numpy               1.24.0
openai              1.35.15
openpyxl            3.1.5
oyaml               1.0
packaging           24.1
pandas              2.0.3
pathspec            0.12.1
pip                 25.0.1
platformdirs        4.3.6
pycodestyle         2.12.1
pydantic            1.10.16
Pygments            2.18.0
pyreadline3         3.5.4
python-dateutil     2.9.0.post0
python-dotenv       1.0.1
python-multipart    0.0.10
pytz                2025.1
PyYAML              6.0.2
requests            2.32.3
rich                13.8.1
rich-click          1.8.3
setuptools          75.8.0
shellingham         1.5.4
six                 1.17.0
smmap               5.0.1
sniffio             1.3.1
SQLAlchemy          2.0.23
starlette           0.37.2
tenacity            8.5.0
tiktoken            0.7.0
tinydb              4.8.0
tomli               2.2.1
tqdm                4.66.5
typer               0.12.5
typing_extensions   4.12.2
tzdata              2025.1
urllib3             1.26.20
uvicorn             0.30.6
uvloop              0.20.0
virtualenv          20.27.1
waitress            3.0.2
watchfiles          0.24.0
websockets          13.1
Werkzeug            3.1.3
wheel               0.45.1
win32-setctime      1.1.0
XlsxWriter          3.2.2
zipp                3.20.2
(.venv) PS E:\DEV_CONTEXT\1_Projects\VISION_HEALTH_SYSTEM_VUE> 

